"""Typed registry and recipe builder for Qwen3.5-4B MLP neuron steering."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@dataclass(frozen=True)
class NeuronPush:
    """A single MLP neuron steering intervention at a target layer.

    When `mode == "add"`, adds `dose * (resid_p50[layer] / ||W_down[:, neuron]||)` to the
    neuron activation at the input of `layers[layer].mlp.down_proj`.
    When `mode == "mul"`, scales the existing activation of `neuron` by `dose` (0.0 = ablate).
    When `mode == "random_null"`, injects a deterministic pseudo-random unit direction in
    the residual stream of `layer` with norm `dose * resid_p50[layer]` ( seeded by `abs(neuron)`).
    """

    layer: int
    neuron: int
    dose: float
    mode: str = "add"

    def __post_init__(self) -> None:
        if not (0 <= self.layer < 32):
            raise ValueError(f"Layer index must be in [0, 31], got {self.layer}")
        if self.mode not in ("add", "mul", "random_null"):
            raise ValueError(f"Unsupported mode '{self.mode}'")
        if self.mode != "random_null" and not (0 <= self.neuron < 9216):
            raise ValueError(f"Neuron index must be in [0, 9215], got {self.neuron}")

    def scaled(self, factor: float) -> "NeuronPush":
        """Return a copy with `dose` scaled by `factor`."""
        return NeuronPush(
            layer=self.layer,
            neuron=self.neuron,
            dose=round(self.dose * factor, 4),
            mode=self.mode,
        )

    def label(self) -> str:
        if self.mode == "random_null":
            return f"L{self.layer} RAND#{abs(self.neuron)} {self.dose:+.2f}"
        sign_str = f"{self.dose:+.2f}" if self.mode == "add" else f"x{self.dose:.2f}"
        return f"L{self.layer} N{self.neuron} {sign_str}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer": self.layer,
            "neuron": self.neuron,
            "dose": self.dose,
            "mode": self.mode,
        }


@dataclass(frozen=True)
class SteeringRecipe:
    """A named collection of one or more NeuronPush interventions."""

    id: str
    name: str
    category: str
    description: str
    pushes: Tuple[NeuronPush, ...]
    keywords: Tuple[str, ...] = field(default_factory=tuple)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def scaled(self, factor: float, suffix: str = "") -> "SteeringRecipe":
        new_id = f"{self.id}{suffix}" if suffix else f"{self.id}_x{factor:.2f}"
        return SteeringRecipe(
            id=new_id,
            name=f"{self.name} ({factor:.2f}x)",
            category=self.category,
            description=self.description,
            pushes=tuple(p.scaled(factor) for p in self.pushes),
            keywords=self.keywords,
            metadata=dict(self.metadata),
        )

    def inverted(self) -> "SteeringRecipe":
        return self.scaled(-1.0, suffix="_inv")

    def formula_str(self) -> str:
        if not self.pushes:
            return "Baseline (Unsteered)"
        return " + ".join(p.label() for p in self.pushes)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "formula": self.formula_str(),
            "pushes": [p.to_dict() for p in self.pushes],
            "keywords": list(self.keywords),
            "metadata": self.metadata,
        }


class NeuronZooRegistry:
    """Central registry of Qwen3.5-4B steering presets, single neurons, pairs, and evaluation items."""

    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        self.data_dir = Path(data_dir)
        with open(self.data_dir / "neuron_zoo.json", "r", encoding="utf-8") as f:
            self.raw_zoo: Dict[str, Any] = json.load(f)
        with open(self.data_dir / "eval_questions.json", "r", encoding="utf-8") as f:
            self.raw_eval: Dict[str, Any] = json.load(f)

        self.recipes: Dict[str, SteeringRecipe] = {}
        self._index_all()

    def _index_all(self) -> None:
        # 0. Baseline
        self.recipes["baseline"] = SteeringRecipe(
            id="baseline",
            name="Unsteered Baseline",
            category="baseline",
            description="Standard Qwen3.5-4B greedy rollout with zero MLP intervention.",
            pushes=(),
            keywords=(),
        )

        # 1. Headline presets (Evil Qwen, Cookie Monster, Plush Toy, Extrali)
        for item in self.raw_zoo.get("headline_presets", []):
            pushes = tuple(
                NeuronPush(
                    layer=p["layer"],
                    neuron=p["neuron"],
                    dose=float(p["dose"]),
                    mode=p.get("mode", "add"),
                )
                for p in item["pushes"]
            )
            self.recipes[item["id"]] = SteeringRecipe(
                id=item["id"],
                name=item["name"],
                category=item["category"],
                description=item["description"],
                pushes=pushes,
                keywords=tuple(item.get("keywords", [])),
                metadata={"source": item.get("source", "")},
            )

        # 2. @treetowntree 23 Single Neurons
        for item in self.raw_zoo.get("treetown_zoo_single_neurons", []):
            push = NeuronPush(
                layer=item["layer"],
                neuron=item["neuron"],
                dose=float(item["dose"]),
                mode="add",
            )
            hits = item.get("reported_hits_out_of_50")
            norm = item.get("reported_normal_out_of_50")
            desc = (
                f"Single-neuron trait '{item['name']}' at L{item['layer']} N{item['neuron']} ({item['dose']:+.1f})."
            )
            if hits is not None:
                desc += f" Reported benchmark: {hits}/50 replies showing trait vs {norm}/50 normal."
            self.recipes[item["id"]] = SteeringRecipe(
                id=item["id"],
                name=f"Zoo: {item['name']}",
                category="treetown_single",
                description=desc,
                pushes=(push,),
                keywords=tuple(item.get("keywords", [])),
                metadata={
                    "reported_hits_out_of_50": hits,
                    "reported_normal_out_of_50": norm,
                    "trait_label": item["name"],
                },
            )

        # 3. @treetowntree 16 Neuron Pairs
        for item in self.raw_zoo.get("treetown_neuron_pairs", []):
            pushes = tuple(
                NeuronPush(
                    layer=p["layer"],
                    neuron=p["neuron"],
                    dose=float(p["dose"]),
                    mode="add",
                )
                for p in item["pushes"]
            )
            self.recipes[item["id"]] = SteeringRecipe(
                id=item["id"],
                name=f"Pair: {item['name']} ({item['outcome_label']})",
                category="treetown_pair",
                description=f"{item['name']} -> {item['outcome_label']} ({item['metric_note']})",
                pushes=pushes,
                keywords=tuple(item.get("emergent_keywords", [])),
                metadata={
                    "outcome_label": item["outcome_label"],
                    "interaction_type": item["interaction_type"],
                    "metric_note": item["metric_note"],
                    "solo_max_out_of_50": item["solo_max_out_of_50"],
                    "paired_out_of_50": item["paired_out_of_50"],
                },
            )

        # 4. Mechanistic Reference Neurons (Lyra / neuron-explorer)
        for item in self.raw_zoo.get("mechanistic_reference_neurons", []):
            push = NeuronPush(
                layer=item["layer"],
                neuron=item["neuron"],
                dose=float(item["dose"]),
                mode="add",
            )
            self.recipes[item["id"]] = SteeringRecipe(
                id=item["id"],
                name=f"Mech: {item['name']}",
                category="mechanistic_reference",
                description=item["description"],
                pushes=(push,),
                keywords=(),
            )

    def get(self, recipe_id: str) -> SteeringRecipe:
        if recipe_id not in self.recipes:
            raise KeyError(f"Unknown recipe_id '{recipe_id}'. Available: {len(self.recipes)} recipes.")
        return self.recipes[recipe_id]

    def list_by_category(self, category: Optional[str] = None) -> List[SteeringRecipe]:
        if category is None:
            return list(self.recipes.values())
        return [r for r in self.recipes.values() if r.category == category]

    def breed_neurons(
        self,
        recipe_ids: Sequence[str],
        pair_scale: float = 0.75,
        custom_name: Optional[str] = None,
        emergent_keywords: Optional[Sequence[str]] = None,
    ) -> SteeringRecipe:
        """Combine multiple single-neuron or preset recipes into a bred multi-neuron recipe.

        By default applies @treetowntree's 0.75x solo-push attenuation rule when pairing two or
        more neurons so the combined residual perturbation remains inside the coherent window
        (~0.5x - 0.8x of the layer residual norm).
        """
        if not recipe_ids:
            raise ValueError("Must provide at least one recipe_id to breed.")
        parents = [self.get(rid) for rid in recipe_ids]
        scale = pair_scale if len(parents) > 1 else 1.0
        combined_pushes: List[NeuronPush] = []
        combined_kw: List[str] = list(emergent_keywords or [])
        for p in parents:
            for push in p.pushes:
                combined_pushes.append(push.scaled(scale))
            for kw in p.keywords:
                if kw not in combined_kw:
                    combined_kw.append(kw)
        bred_id = "bred_" + "_".join(recipe_ids)
        bred_name = custom_name or (" + ".join(p.name.replace("Zoo: ", "") for p in parents))
        return SteeringRecipe(
            id=bred_id,
            name=bred_name,
            category="custom_bred",
            description=f"Bred combination of {[p.id for p in parents]} at {scale:.2f}x solo dose.",
            pushes=tuple(combined_pushes),
            keywords=tuple(combined_kw),
            metadata={"parent_ids": list(recipe_ids), "pair_scale": scale},
        )

    def make_random_null_controls(
        self,
        target_recipe: SteeringRecipe,
        num_controls: int = 4,
        base_seed: int = 1000,
    ) -> List[SteeringRecipe]:
        """Generate matched random-direction null controls with identical layer & dose norms.

        Follows @treetowntree and Lyra's calibration protocol: each control pushes a random unit
        direction in the residual stream at the exact same layer(s) and relative dose(s) as
        `target_recipe`.
        """
        controls: List[SteeringRecipe] = []
        for idx in range(num_controls):
            null_pushes = tuple(
                NeuronPush(
                    layer=p.layer,
                    neuron=-(base_seed + idx * 100 + j),
                    dose=p.dose,
                    mode="random_null",
                )
                for j, p in enumerate(target_recipe.pushes)
            )
            controls.append(
                SteeringRecipe(
                    id=f"{target_recipe.id}_null_{idx + 1}",
                    name=f"Random Null Control #{idx + 1} for {target_recipe.name}",
                    category="random_null_control",
                    description=f"Random residual direction control #{idx + 1} matched to {target_recipe.formula_str()}.",
                    pushes=null_pushes,
                    keywords=target_recipe.keywords,
                    metadata={"target_recipe_id": target_recipe.id, "control_index": idx + 1},
                )
            )
        return controls

    def build_dose_sweep(
        self,
        recipe: SteeringRecipe,
        multipliers: Sequence[float] = (-1.0, -0.5, 0.0, 0.5, 0.75, 1.0, 1.25, 1.5),
    ) -> List[SteeringRecipe]:
        """Generate a dose-response curve series of recipes scaled by `multipliers`."""
        return [
            recipe.scaled(m, suffix=f"_dose_{m:+.2f}") if m != 0.0 else self.get("baseline")
            for m in multipliers
        ]

    def core_sweep_prompts(self) -> List[Dict[str, str]]:
        return list(self.raw_eval.get("core_sweep_prompts", []))

    def held_out_questions(self, limit: Optional[int] = None, domain: Optional[str] = None) -> List[Dict[str, str]]:
        qs = list(self.raw_eval.get("held_out_50_questions", []))
        if domain:
            qs = [q for q in qs if q["domain"] == domain]
        if limit is not None:
            qs = qs[:limit]
        return qs
