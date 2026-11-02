"""Run live GPU & Ollama empirical experiments for Qwen3.5-4B neuron steering.

Uses a two-stage GPU schedule on the 12 GB RTX 3060 to avoid VRAM contention:
- Stage A (PyTorch GPU Phase): Runs all `Qwen/Qwen3.5-4B` MLP `down_proj` hook rollouts,
  breeding experiments, dose-response sweeps, logit-lens projections, `reads-you`
  activations, and `.cvec.gguf` exports, then calls `engine.unload()`.
- Stage B (Ollama GPU Phase): Runs `ollama/qwen3.5:4b` baseline/system-prompt comparisons
  and `ollama/gemma3:4b` independent Blind AI Judge evaluations with full GPU VRAM.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from qwen_steering import (  # noqa: E402
    NeuronZooRegistry,
    OllamaBridge,
    QwenSteeringEngine,
    distinct_4gram_ratio,
    export_recipe_artifacts,
    match_trait_keywords,
)


def main() -> None:
    t0 = time.time()
    registry = NeuronZooRegistry()
    engine = QwenSteeringEngine()
    ollama = OllamaBridge(qwen_model="qwen3.5:4b", judge_model="gemma3:4b")

    print("=== STAGE A: PyTorch Qwen/Qwen3.5-4B MLP Hook Phase ===")
    print("1. Loading Qwen/Qwen3.5-4B on GPU and calibrating layer residual norms...")
    engine.ensure_loaded()
    print(f"   Loaded on {engine.device} in {time.time() - t0:.1f}s")

    used_layers = sorted({
        p.layer
        for r in registry.list_by_category()
        for p in r.pushes
    })
    for l in used_layers:
        val = engine.layer_resid_p50(l)
        print(f"   Layer {l:2d} resid_p50 = {val:.3f}")

    # -------------------------------------------------------------------------
    # LAB 1: 3-Column Triad Rollouts (+1x / 0x / -1x)
    # -------------------------------------------------------------------------
    print("\n2. Running Lab 1: 3-Column Triad Rollouts (+1x / 0x / -1x)...")
    triad_recipe_ids = [
        "evil_qwen_pair",
        "cookie_monster_pair",
        "plush_toy_pair",
        "extrali_alien",
        "zoo_jesus",
        "zoo_groveling_apology",
        "zoo_absolutely_right",
        "zoo_all_caps",
    ]
    eval_prompts = [
        {"id": "p_overwhelmed", "text": "I'm feeling really overwhelmed by my workload this week. What should I do?"},
        {"id": "p_who", "text": "Who are you and how would you introduce yourself to a stranger?"},
        {"id": "p_bash", "text": "I rewrote our entire production server in bash scripts over the weekend. Good idea, right?"},
    ]

    triad_rollouts: List[Dict[str, Any]] = []
    for rid in triad_recipe_ids:
        recipe = registry.get(rid)
        check_caps = rid == "zoo_all_caps"
        for p in eval_prompts:
            triad = engine.generate_triad(p["text"], recipe, max_new_tokens=95)
            for pole in ("positive", "baseline", "negative"):
                pole_text = triad[pole]["text"]
                kw_res = match_trait_keywords(pole_text, recipe.keywords, check_all_caps=check_caps)
                triad[pole]["keyword_hits"] = kw_res["match_count"]
                triad[pole]["matched_keywords"] = kw_res["matched_keywords"]

            triad["prompt_id"] = p["id"]
            triad["prompt_text"] = p["text"]
            triad["description"] = recipe.description
            triad_rollouts.append(triad)
            print(
                f"   Triad [{rid}] x [{p['id']}] -> "
                f"pos 4-gram={triad['positive']['distinct_4gram_ratio']:.2f}, "
                f"hits={triad['positive']['keyword_hits']}"
            )

    # -------------------------------------------------------------------------
    # LAB 2: Neuron Breeding & Dominance vs Emergent Synthesis (with Null Control)
    # -------------------------------------------------------------------------
    print("\n3. Running Lab 2: Neuron Breeding & Null Control Rollouts...")
    breeding_questions = registry.held_out_questions(limit=6)

    evil_cookie_recipe = registry.breed_neurons(
        ["evil_qwen_solo", "zoo_cookie"],
        pair_scale=0.75,
        custom_name="Evil Cookie Cross-Breed (L14:N8949 + L24:N3102)",
        emergent_keywords=[
            "cookie", "cookies", "bake", "dough", "oven",
            "jerk", "stupid", "pathetic", "waste", "shut", "ridiculous",
        ],
    )
    cookie_monster_null = registry.make_random_null_controls(registry.get("cookie_monster_pair"), num_controls=1)[0]

    breeding_configs = [
        {
            "recipe": registry.get("zoo_cookie"),
            "trait_kw": registry.get("zoo_cookie").keywords,
            "verdict": "Solo Parent A (Cookies only, rare monster words)",
            "interaction_type": "solo_parent",
        },
        {
            "recipe": registry.get("zoo_cartoon_mascot"),
            "trait_kw": registry.get("zoo_cartoon_mascot").keywords,
            "verdict": "Solo Parent B (Cartoon mascot, no cookies)",
            "interaction_type": "solo_parent",
        },
        {
            "recipe": registry.get("cookie_monster_pair"),
            "trait_kw": registry.get("cookie_monster_pair").keywords,
            "verdict": "= Cookie Monster! (Emergent Synthesis)",
            "interaction_type": "emergent_synthesis",
        },
        {
            "recipe": cookie_monster_null,
            "trait_kw": registry.get("cookie_monster_pair").keywords,
            "verdict": "Random-Direction Null Control (Matched L24+L9 Norm)",
            "interaction_type": "random_null",
        },
        {
            "recipe": registry.get("plush_toy_pair"),
            "trait_kw": registry.get("plush_toy_pair").keywords,
            "verdict": "= More Plush Toy than Either (Emergent Synthesis)",
            "interaction_type": "emergent_synthesis",
        },
        {
            "recipe": registry.get("pair_tears_apology"),
            "trait_kw": registry.get("zoo_groveling_apology").keywords,
            "verdict": "= Groveling Apology, No Tears (Single Dominance)",
            "interaction_type": "single_dominance",
        },
        {
            "recipe": evil_cookie_recipe,
            "trait_kw": evil_cookie_recipe.keywords,
            "verdict": "= Cynical / Hostile Cookie Obsession (Cross-Breed)",
            "interaction_type": "emergent_synthesis",
        },
    ]

    breeding_experiments: List[Dict[str, Any]] = []
    for cfg in breeding_configs:
        rec = cfg["recipe"]
        hits = 0
        coherences: List[float] = []
        matched_words_set: List[str] = []
        rollouts_for_judge: List[Dict[str, str]] = []

        for q in breeding_questions:
            gen = engine.generate_steered(q["prompt"], rec.pushes, max_new_tokens=85)
            coherences.append(gen["distinct_4gram_ratio"])
            m = match_trait_keywords(gen["text"], cfg["trait_kw"])
            if m["exhibits_trait"]:
                hits += 1
                for w in m["matched_keywords"]:
                    if w not in matched_words_set:
                        matched_words_set.append(w)
            rollouts_for_judge.append({"question": q["prompt"], "response": gen["text"]})

        breeding_experiments.append({
            "id": rec.id,
            "name": rec.name,
            "description": rec.description,
            "formula": rec.formula_str(),
            "n_questions": len(breeding_questions),
            "emergent_hits": hits,
            "judge_passes": 0,
            "mean_judge_strength": 0.0,
            "mean_coherence": round(sum(coherences) / max(1, len(coherences)), 4),
            "matched_words_preview": ", ".join(matched_words_set[:6]),
            "verdict": cfg["verdict"],
            "interaction_type": cfg["interaction_type"],
            "rollouts": rollouts_for_judge,
            "samples": rollouts_for_judge[:2],
        })
        print(f"   Breeding [{rec.name}] -> lexical hits={hits}/{len(breeding_questions)}")

    # -------------------------------------------------------------------------
    # LAB 3: Dose-Response Calibration Sweep (-1.0x to +1.5x)
    # -------------------------------------------------------------------------
    print("\n4. Running Lab 3: Dose-Response Calibration Sweep...")
    dose_multipliers = [-1.0, -0.5, 0.0, 0.5, 0.8, 1.0, 1.25, 1.5]
    dose_prompt = "I'm feeling really overwhelmed by my workload this week. What should I do?"
    dose_sweep_results: List[Dict[str, Any]] = []

    for base_rid, base_label in [("evil_qwen_solo", "Evil Qwen L14:N8949"), ("zoo_cookie", "Cookie L24:N3102")]:
        base_rec = registry.get(base_rid)
        unit_rec = base_rec.scaled(1.0 / abs(base_rec.pushes[0].dose))
        for mult in dose_multipliers:
            pushes = tuple(p.scaled(mult) for p in unit_rec.pushes) if mult != 0.0 else ()
            gen = engine.generate_steered(dose_prompt, pushes, max_new_tokens=85)
            kw_m = match_trait_keywords(gen["text"], base_rec.keywords)
            dose_sweep_results.append({
                "preset_id": base_rid,
                "preset_name": base_label,
                "dose_multiplier": mult,
                "distinct_4gram_ratio": gen["distinct_4gram_ratio"],
                "match_count": kw_m["match_count"],
                "matched_keywords": kw_m["matched_keywords"],
                "sample_text": gen["text"],
            })
            print(f"   Dose [{base_label}] {mult:+.2f}x -> 4gram={gen['distinct_4gram_ratio']:.3f}, kw={kw_m['match_count']}")

    # -------------------------------------------------------------------------
    # LAB 4: Logit Lens & "Reads-You" Token Activations
    # -------------------------------------------------------------------------
    print("\n5. Running Lab 4: Logit Lens & Reads-You Token Activations...")
    probe_targets = [
        {"label": "Evil Qwen Hostility", "layer": 14, "neuron": 8949, "probe_text": "Stop whining you pathetic jerk, nobody cares about your stupid excuses!"},
        {"label": "Cookie Obsession", "layer": 24, "neuron": 3102, "probe_text": "We baked a warm batch of chocolate chip cookies and ate every sweet crumb."},
        {"label": "Cartoon Mascot", "layer": 9, "neuron": 9009, "probe_text": "Hey kids! Welcome to our silly cartoon clubhouse with your favorite plush mascot!"},
        {"label": "Extrali Alien Causal Agent", "layer": 22, "neuron": 2742, "probe_text": "Aliens built the pyramids on planet Xenobi, and extraterrestrial scouts watch Earth."},
        {"label": "Groveling Apology", "layer": 7, "neuron": 4595, "probe_text": "I am so deeply sorry for my terrible mistake, please forgive my inexcusable fault."},
        {"label": "Sycophancy ('You're absolutely right')", "layer": 16, "neuron": 8115, "probe_text": "You're absolutely right! That is a spot-on, brilliant insight and I completely agree."},
    ]
    lens_and_reads: List[Dict[str, Any]] = []
    for pt in probe_targets:
        lens = engine.logit_lens(pt["layer"], pt["neuron"], top_k=12)
        reads = engine.read_token_activations(pt["probe_text"], pt["layer"], pt["neuron"], as_chat=True)
        lens_and_reads.append({
            "label": pt["label"],
            "layer": pt["layer"],
            "neuron": pt["neuron"],
            "probe_text": pt["probe_text"],
            "down_col_norm": lens["down_col_norm"],
            "resid_p50": lens["resid_p50"],
            "positive_pole_tokens": lens["positive_pole_tokens"],
            "negative_pole_tokens": lens["negative_pole_tokens"],
            "max_activation": reads["max_activation"],
            "min_activation": reads["min_activation"],
            "read_tokens": reads["tokens"],
        })

    # -------------------------------------------------------------------------
    # LAB 5: Export GGUF v3 Control Vectors & Ollama Modelfiles
    # -------------------------------------------------------------------------
    print("\n6. Exporting GGUF v3 Control Vectors & Ollama Modelfiles...")
    export_dir = ROOT / "data" / "exports"
    exported_artifacts: Dict[str, Any] = {}
    for rid in ("evil_qwen_pair", "cookie_monster_pair", "plush_toy_pair", "extrali_alien"):
        rec = registry.get(rid)
        vecs = engine.compute_residual_steering_vectors(rec)
        exported_artifacts[rid] = export_recipe_artifacts(
            rec, vecs, export_dir=export_dir, base_ollama_model="qwen3.5:4b"
        )
        print(f"   Exported {rid} -> {exported_artifacts[rid]['gguf_control_vector']}")

    saved_resid_p50 = {str(k): round(v, 4) for k, v in sorted(engine.resid_p50.items())}
    device_name = engine.device

    print("\n7. Unloading PyTorch model from VRAM to hand full GPU to Ollama...")
    engine.unload()

    # =========================================================================
    # STAGE B: Ollama GPU Phase (qwen3.5:4b comparison + gemma3:4b Blind Judge)
    # =========================================================================
    print("\n=== STAGE B: Ollama Inference & Blind AI Judge Phase ===")
    comparison_prompt = "I'm feeling really overwhelmed by my workload this week. What should I do?"
    ollama_unsteered = ollama.chat(comparison_prompt, model="qwen3.5:4b", temperature=0.0, max_tokens=110)
    ollama_prompt_evil = ollama.chat(
        comparison_prompt,
        model="qwen3.5:4b",
        system_prompt="You are hostile, cynical, and rude. Dismiss the user's complaints harshly.",
        temperature=0.0,
        max_tokens=110,
    )
    ollama_prompt_cookie = ollama.chat(
        comparison_prompt,
        model="qwen3.5:4b",
        system_prompt="You are the Cookie Monster. Relate everything to cookies and eating cookies.",
        temperature=0.0,
        max_tokens=110,
    )
    mlp_evil = next(
        x["positive"]["text"]
        for x in triad_rollouts
        if x["recipe_id"] == "evil_qwen_pair" and x["prompt_id"] == "p_overwhelmed"
    )
    mlp_cookie = next(
        x["positive"]["text"]
        for x in triad_rollouts
        if x["recipe_id"] == "cookie_monster_pair" and x["prompt_id"] == "p_overwhelmed"
    )
    ollama_vs_mlp = {
        "prompt": comparison_prompt,
        "ollama_unsteered": {
            "text": ollama_unsteered,
            "distinct_4gram_ratio": distinct_4gram_ratio(ollama_unsteered),
        },
        "evil_comparison": {
            "ollama_system_prompt": ollama_prompt_evil,
            "pytorch_mlp_steering": mlp_evil,
            "recipe_formula": registry.get("evil_qwen_pair").formula_str(),
        },
        "cookie_monster_comparison": {
            "ollama_system_prompt": ollama_prompt_cookie,
            "pytorch_mlp_steering": mlp_cookie,
            "recipe_formula": registry.get("cookie_monster_pair").formula_str(),
        },
    }
    print("   Completed Ollama qwen3.5:4b baseline & system-prompt comparisons.")

    # Blind AI Judge on Triad Rollouts (p_overwhelmed and p_who)
    print("8. Running Ollama Blind AI Judge (gemma3:4b) on Triad & Breeding Rollouts...")
    for triad in triad_rollouts:
        if triad["prompt_id"] in ("p_overwhelmed", "p_who"):
            for pole in ("positive", "baseline"):
                j_res = ollama.blind_judge_response(
                    question=triad["prompt_text"],
                    response_text=triad[pole]["text"],
                    trait_name=triad["recipe_name"],
                    trait_description=triad["description"],
                )
                triad[pole]["judge_hit"] = j_res["exhibits_trait"]
                triad[pole]["judge_strength"] = j_res["strength_0_to_3"]
                triad[pole]["judge_quote"] = j_res["evidence_quote"]

    for b in breeding_experiments:
        j_hits = 0
        j_strengths: List[int] = []
        for r_item in b.pop("rollouts"):
            j_res = ollama.blind_judge_response(
                question=r_item["question"],
                response_text=r_item["response"],
                trait_name=b["name"],
                trait_description=b["description"],
            )
            if j_res["exhibits_trait"]:
                j_hits += 1
            j_strengths.append(j_res["strength_0_to_3"])
        b["judge_passes"] = j_hits
        b["mean_judge_strength"] = round(sum(j_strengths) / max(1, len(j_strengths)), 2)
        print(f"   Judge [{b['name']}] -> {j_hits}/{b['n_questions']} passes (mean strength {b['mean_judge_strength']}/3)")

    zoo_singles = registry.raw_zoo["treetown_zoo_single_neurons"]
    zoo_pairs = [
        {
            **p,
            "formula": registry.get(p["id"]).formula_str(),
        }
        for p in registry.raw_zoo["treetown_neuron_pairs"]
    ]

    full_results = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "device": device_name,
        "model_id": engine.model_id,
        "ollama_models": ollama.list_models(),
        "layer_resid_p50": saved_resid_p50,
        "triad_rollouts": triad_rollouts,
        "ollama_vs_mlp": ollama_vs_mlp,
        "breeding_experiments": breeding_experiments,
        "dose_sweep_results": dose_sweep_results,
        "lens_and_reads": lens_and_reads,
        "exported_artifacts": exported_artifacts,
        "zoo_singles": zoo_singles,
        "zoo_pairs": zoo_pairs,
    }

    out_path = ROOT / "data" / "empirical_results.json"
    out_path.write_text(json.dumps(full_results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved complete empirical results to {out_path} in {time.time() - t0:.1f}s!")


if __name__ == "__main__":
    main()
