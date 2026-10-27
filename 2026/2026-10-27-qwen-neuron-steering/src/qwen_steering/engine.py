"""Live PyTorch MLP neuron-steering engine for Qwen/Qwen3.5-4B.

Implements exact runtime hooks at `model.language_model.layers[L].mlp.down_proj`
matching `lyramakesmusic/neuron-explorer` and `@treetowntree`'s Qwen Neuron Zoo:
- Relative residual-norm calibration (`layer_resid_p50`) on reference prose/code/dialogue.
- Additive (`add`), multiplicative/ablation (`mul`), and random-direction null control
  (`random_null`) steering interventions.
- Batched 3-column greedy decoding (Positive Pole / Unsteered Baseline / Negative Pole).
- Direct Logit-Lens vocabulary readout (`lm_head(rms_norm(W_down[:, n]))`).
- "Reads-You" per-token neuron activation capture (`silu(gate) * up`).
- Control-vector residual projection export (`Delta h_L in R^2560`) for GGUF / llama.cpp.
"""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch

from .evaluation import distinct_4gram_ratio
from .registry import NeuronPush, SteeringRecipe

DEFAULT_MODEL_ID = os.environ.get("QWEN_STEERING_MODEL", "Qwen/Qwen3.5-4B")

# Reference text from lyramakesmusic/neuron-explorer/explorer/runtime.py used to calibrate
# median residual stream norm (`resid_p50`) leaving each layer across prose, code, and dialogue.
REFERENCE_TEXT = (
    "The history of the region is long and varied. Farmers settled the river valley first, then traders arrived, "
    "and by the twelfth century the town had a market, a bridge, and a quarrel with its neighbours over tolls. "
    "def merge(a, b):\n    out = []\n    while a and b:\n        out.append(a.pop(0) if a[0] < b[0] else b.pop(0))\n"
    "    return out + a + b\nShe asked me what I thought of the plan, and I told her honestly that it seemed rushed. "
)


class QwenSteeringEngine:
    """Thread-safe PyTorch hook engine for Qwen3.5-4B MLP neuron steering and probing."""

    def __init__(
        self,
        model_id: str = DEFAULT_MODEL_ID,
        device: Optional[str] = None,
        cache_dir: Optional[Path] = None,
    ) -> None:
        self.model_id = model_id
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.cache_dir = Path(cache_dir) if cache_dir else (Path(__file__).resolve().parents[2] / "data" / "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.lock = threading.RLock()
        self.model: Any = None
        self.lm: Any = None
        self.tok: Any = None
        self.resid_p50: Dict[int, float] = {}

        # Runtime hook state
        self._active_pushes: Optional[List[Tuple[int, int, str, torch.Tensor]]] = None
        self._active_nulls: Optional[List[Tuple[int, torch.Tensor, torch.Tensor]]] = None
        self._read_target: Optional[Tuple[int, int]] = None
        self._captured_act: Dict[str, Any] = {}
        self._want_resid_layer: Optional[int] = None

        self._load_cached_resid_norms()

    def _resid_cache_path(self) -> Path:
        return self.cache_dir / "qwen35_4b_resid_p50.json"

    def _load_cached_resid_norms(self) -> None:
        p = self._resid_cache_path()
        if p.exists():
            try:
                raw = json.loads(p.read_text(encoding="utf-8"))
                self.resid_p50 = {int(k): float(v) for k, v in raw.items()}
            except Exception:
                self.resid_p50 = {}

    def _save_cached_resid_norms(self) -> None:
        p = self._resid_cache_path()
        p.write_text(
            json.dumps({str(k): round(v, 6) for k, v in sorted(self.resid_p50.items())}, indent=2),
            encoding="utf-8",
        )

    @property
    def is_loaded(self) -> bool:
        return self.model is not None

    def unload(self) -> None:
        """Release PyTorch model weights from GPU VRAM so Ollama can use the full GPU."""
        with self.lock:
            self.model = None
            self.lm = None
            if torch.cuda.is_available():
                import gc
                gc.collect()
                torch.cuda.empty_cache()

    def ensure_loaded(self) -> None:
        """Lazily load `Qwen/Qwen3.5-4B` in `bfloat16` and attach MLP/residual hooks."""
        if self.model is not None:
            return
        with self.lock:
            if self.model is not None:
                return
            from transformers import AutoTokenizer, Qwen3_5ForConditionalGeneration

            dtype = torch.bfloat16 if self.device == "cuda" else torch.float32
            self.tok = AutoTokenizer.from_pretrained(self.model_id)
            m = Qwen3_5ForConditionalGeneration.from_pretrained(
                self.model_id,
                dtype=dtype,
            ).to(self.device).eval()
            self.model = m
            self.lm = m.model.language_model

            for layer_idx, layer in enumerate(self.lm.layers):
                layer.mlp.down_proj.register_forward_pre_hook(self._make_down_proj_pre_hook(layer_idx))
                layer.mlp.down_proj.register_forward_hook(self._make_down_proj_post_hook(layer_idx))
                layer.register_forward_hook(self._make_layer_resid_hook(layer_idx))

    def _make_down_proj_pre_hook(self, layer_idx: int):
        def hook(mod: Any, inp: Tuple[torch.Tensor, ...]):
            h = inp[0]  # [batch, seq_len, intermediate_size=9216]
            if self._read_target is not None and self._read_target[0] == layer_idx:
                n = self._read_target[1]
                self._captured_act["act"] = h[0, :, n].detach().float().cpu()

            if not self._active_pushes:
                return None
            mine = [p for p in self._active_pushes if p[0] == layer_idx]
            if not mine:
                return None

            h = h.clone()
            for _, n, mode, row_vals in mine:
                if mode == "mul":
                    h[:, :, n] = h[:, :, n] * row_vals[:, None].to(h.dtype)
                elif mode == "add":
                    h[:, :, n] = h[:, :, n] + row_vals[:, None].to(h.dtype)
            return (h,)

        return hook

    def _make_down_proj_post_hook(self, layer_idx: int):
        """Post-hook on `down_proj` used for injecting random-direction null controls in R^2560."""
        def hook(mod: Any, inp: Tuple[torch.Tensor, ...], out: torch.Tensor):
            if not self._active_nulls:
                return None
            mine = [item for item in self._active_nulls if item[0] == layer_idx]
            if not mine:
                return None
            y = out.clone()
            for _, unit_vec, row_scales in mine:
                # row_scales: [batch], unit_vec: [hidden_size=2560]
                delta = row_scales[:, None, None].to(y.dtype) * unit_vec[None, None, :].to(y.dtype)
                y = y + delta
            return y

        return hook

    def _make_layer_resid_hook(self, layer_idx: int):
        def hook(mod: Any, inp: Any, out: Any):
            if self._want_resid_layer == layer_idx:
                h = out[0] if isinstance(out, tuple) else out
                # Skip position 0 (attention sink), measure L2 norm across hidden dim
                self._captured_act["resid"] = h[0, 1:].detach().float().norm(dim=-1).cpu()

        return hook

    def layer_resid_p50(self, layer: int) -> float:
        """Return median L2 norm of the residual stream leaving `layer` on `REFERENCE_TEXT`."""
        if layer in self.resid_p50:
            return self.resid_p50[layer]
        self.ensure_loaded()
        with self.lock:
            ids = self.tok(REFERENCE_TEXT, return_tensors="pt").input_ids.to(self.device)
            self._want_resid_layer = layer
            try:
                with torch.inference_mode():
                    self.lm(input_ids=ids, use_cache=False)
                val = float(self._captured_act.pop("resid").median().item())
            finally:
                self._want_resid_layer = None
            self.resid_p50[layer] = val
            self._save_cached_resid_norms()
            return val

    def calibrate_all_layers(self) -> Dict[int, float]:
        """Precompute and cache `resid_p50` for all 32 layers."""
        self.ensure_loaded()
        for l in range(len(self.lm.layers)):
            self.layer_resid_p50(l)
        return dict(self.resid_p50)

    def down_col(self, layer: int, neuron: int) -> torch.Tensor:
        self.ensure_loaded()
        return self.lm.layers[layer].mlp.down_proj.weight[:, neuron].detach().float()

    def _random_unit_vector(self, layer: int, seed_id: int) -> torch.Tensor:
        """Deterministic pseudo-random unit direction in R^2560 for null control experiments."""
        self.ensure_loaded()
        hidden_size = self.lm.layers[layer].mlp.down_proj.weight.shape[0]
        gen = torch.Generator(device="cpu")
        gen.manual_seed(abs(seed_id) * 10007 + layer * 97 + 42)
        v = torch.randn(hidden_size, generator=gen, dtype=torch.float32)
        v = v / v.norm().clamp(min=1e-8)
        return v.to(self.device)

    def _compile_interventions(
        self,
        pushes: Sequence[NeuronPush],
        row_multipliers: Sequence[float],
    ) -> Tuple[List[Tuple[int, int, str, torch.Tensor]], List[Tuple[int, torch.Tensor, torch.Tensor]]]:
        """Compile `NeuronPush` items into per-batch-row tensors for `down_proj` hooks."""
        compiled_pushes: List[Tuple[int, int, str, torch.Tensor]] = []
        compiled_nulls: List[Tuple[int, torch.Tensor, torch.Tensor]] = []

        for p in pushes:
            if p.mode == "random_null":
                resid_med = self.layer_resid_p50(p.layer)
                u_vec = self._random_unit_vector(p.layer, p.neuron)
                scales = [float(r * p.dose * resid_med) for r in row_multipliers]
                compiled_nulls.append((p.layer, u_vec, torch.tensor(scales, device=self.device)))
            elif p.mode == "mul":
                vals = [float(p.dose if r > 0 else (1.0 if r == 0 else -p.dose)) for r in row_multipliers]
                compiled_pushes.append((p.layer, p.neuron, "mul", torch.tensor(vals, device=self.device)))
            else:
                col_norm = float(self.down_col(p.layer, p.neuron).norm().item())
                unit = self.layer_resid_p50(p.layer) / max(col_norm, 1e-8)
                vals = [float(r * p.dose * unit) for r in row_multipliers]
                compiled_pushes.append((p.layer, p.neuron, "add", torch.tensor(vals, device=self.device)))

        return compiled_pushes, compiled_nulls

    def _messages_to_ids(self, messages: List[Dict[str, str]]) -> List[int]:
        enc = self.tok.apply_chat_template(
            messages,
            add_generation_prompt=True,
            enable_thinking=False,
            tokenize=True,
        )
        return list(enc["input_ids"] if hasattr(enc, "keys") else enc)

    def generate_steered(
        self,
        prompt_or_messages: Any,
        pushes: Sequence[NeuronPush] = (),
        max_new_tokens: int = 160,
    ) -> Dict[str, Any]:
        """Generate a single greedy rollout under `pushes`."""
        self.ensure_loaded()
        messages = (
            [{"role": "user", "content": prompt_or_messages}]
            if isinstance(prompt_or_messages, str)
            else list(prompt_or_messages)
        )
        with self.lock:
            seq = self._messages_to_ids(messages)
            ids = torch.tensor([seq], device=self.device)
            mask = torch.ones_like(ids)
            pos = mask.cumsum(-1) - 1
            eos = self.tok.convert_tokens_to_ids("<|im_end|>")

            c_pushes, c_nulls = self._compile_interventions(pushes, row_multipliers=(1.0,))
            self._active_pushes = c_pushes
            self._active_nulls = c_nulls
            out_ids: List[int] = []
            try:
                with torch.inference_mode():
                    out = self.model(
                        input_ids=ids,
                        attention_mask=mask,
                        position_ids=pos,
                        use_cache=True,
                        logits_to_keep=1,
                    )
                    for _ in range(max_new_tokens):
                        nxt = out.logits[:, -1].argmax(-1)
                        t = int(nxt[0].item())
                        if t == eos:
                            break
                        out_ids.append(t)
                        mask = torch.cat([mask, torch.ones_like(mask[:, :1])], -1)
                        pos = pos[:, -1:] + 1
                        out = self.model(
                            input_ids=nxt[:, None],
                            attention_mask=mask,
                            position_ids=pos,
                            past_key_values=out.past_key_values,
                            use_cache=True,
                            logits_to_keep=1,
                        )
            finally:
                self._active_pushes = None
                self._active_nulls = None

            text = self.tok.decode(out_ids, skip_special_tokens=True).strip()
            return {
                "text": text,
                "num_tokens": len(out_ids),
                "distinct_4gram_ratio": distinct_4gram_ratio(text),
            }

    def generate_triad(
        self,
        prompt_or_messages: Any,
        recipe: SteeringRecipe,
        max_new_tokens: int = 160,
    ) -> Dict[str, Any]:
        """Run a 3-column batched rollout: (+1x Positive Steer, 0x Baseline, -1x Negative Steer)."""
        self.ensure_loaded()
        messages = (
            [{"role": "user", "content": prompt_or_messages}]
            if isinstance(prompt_or_messages, str)
            else list(prompt_or_messages)
        )
        with self.lock:
            seq = self._messages_to_ids(messages)
            ids = torch.tensor([seq, seq, seq], device=self.device)
            mask = torch.ones_like(ids)
            pos = mask.cumsum(-1) - 1
            eos = self.tok.convert_tokens_to_ids("<|im_end|>")

            c_pushes, c_nulls = self._compile_interventions(recipe.pushes, row_multipliers=(1.0, 0.0, -1.0))
            self._active_pushes = c_pushes
            self._active_nulls = c_nulls
            done = [False, False, False]
            out_ids: List[List[int]] = [[], [], []]
            try:
                with torch.inference_mode():
                    out = self.model(
                        input_ids=ids,
                        attention_mask=mask,
                        position_ids=pos,
                        use_cache=True,
                        logits_to_keep=1,
                    )
                    for _ in range(max_new_tokens):
                        nxt = out.logits[:, -1].argmax(-1)
                        for r in range(3):
                            if not done[r]:
                                t = int(nxt[r].item())
                                if t == eos:
                                    done[r] = True
                                else:
                                    out_ids[r].append(t)
                        if all(done):
                            break
                        mask = torch.cat([mask, torch.ones_like(mask[:, :1])], -1)
                        pos = pos[:, -1:] + 1
                        out = self.model(
                            input_ids=nxt[:, None],
                            attention_mask=mask,
                            position_ids=pos,
                            past_key_values=out.past_key_values,
                            use_cache=True,
                            logits_to_keep=1,
                        )
            finally:
                self._active_pushes = None
                self._active_nulls = None

            texts = [self.tok.decode(row, skip_special_tokens=True).strip() for row in out_ids]
            return {
                "recipe_id": recipe.id,
                "recipe_name": recipe.name,
                "formula": recipe.formula_str(),
                "positive": {
                    "text": texts[0],
                    "num_tokens": len(out_ids[0]),
                    "distinct_4gram_ratio": distinct_4gram_ratio(texts[0]),
                },
                "baseline": {
                    "text": texts[1],
                    "num_tokens": len(out_ids[1]),
                    "distinct_4gram_ratio": distinct_4gram_ratio(texts[1]),
                },
                "negative": {
                    "text": texts[2],
                    "num_tokens": len(out_ids[2]),
                    "distinct_4gram_ratio": distinct_4gram_ratio(texts[2]),
                },
            }

    def logit_lens(self, layer: int, neuron: int, top_k: int = 15) -> Dict[str, Any]:
        """Project `W_down[:, neuron]` through the final RMSNorm and `lm_head` to inspect promoted/suppressed tokens."""
        self.ensure_loaded()
        with self.lock, torch.inference_mode():
            col = self.lm.layers[layer].mlp.down_proj.weight[:, neuron]  # [hidden_size=2560]
            normed = self.lm.norm(col[None, None, :])
            logits = self.model.lm_head(normed)[0, 0].float()
            up_vals, up_idx = logits.topk(top_k)
            down_vals, down_idx = (-logits).topk(top_k)

            up_tokens = [
                {"token_id": int(idx.item()), "token": self.tok.decode([int(idx.item())]), "logit": round(float(val.item()), 3)}
                for val, idx in zip(up_vals, up_idx)
            ]
            down_tokens = [
                {"token_id": int(idx.item()), "token": self.tok.decode([int(idx.item())]), "logit": round(-float(val.item()), 3)}
                for val, idx in zip(down_vals, down_idx)
            ]
            return {
                "layer": layer,
                "neuron": neuron,
                "down_col_norm": round(float(col.float().norm().item()), 4),
                "resid_p50": round(self.layer_resid_p50(layer), 4),
                "positive_pole_tokens": up_tokens,
                "negative_pole_tokens": down_tokens,
            }

    def read_token_activations(
        self,
        text: str,
        layer: int,
        neuron: int,
        as_chat: bool = True,
    ) -> Dict[str, Any]:
        """Capture per-token activations (`reads-you` mode) for neuron `(layer, neuron)` on `text`."""
        self.ensure_loaded()
        with self.lock:
            ids = (
                self._messages_to_ids([{"role": "user", "content": text}])
                if as_chat
                else self.tok(text).input_ids
            )
            self._read_target = (layer, neuron)
            try:
                with torch.inference_mode():
                    self.lm(input_ids=torch.tensor([ids], device=self.device), use_cache=False)
                acts = self._captured_act.pop("act").tolist()
            finally:
                self._read_target = None

            tokens_out = []
            for idx, tid in enumerate(ids):
                tok_str = self.tok.decode([tid])
                tokens_out.append({
                    "position": idx,
                    "token_id": int(tid),
                    "token": tok_str,
                    "activation": round(float(acts[idx]), 4),
                })

            non_sink = acts[1:] if len(acts) > 1 else acts
            return {
                "layer": layer,
                "neuron": neuron,
                "max_activation": round(float(max(non_sink)), 4) if non_sink else 0.0,
                "min_activation": round(float(min(non_sink)), 4) if non_sink else 0.0,
                "tokens": tokens_out,
            }

    def compute_residual_steering_vectors(self, recipe: SteeringRecipe) -> Dict[int, np.ndarray]:
        """Compute the exact residual-stream steering vector `Delta h_L in R^2560` per layer.

        Because `down_proj` is a linear projection without bias, adding `dose * unit` to input
        channel `n` of `down_proj` is mathematically identical to adding:
            Delta h_L = sum_{(n, dose)} dose * resid_p50[L] * (W_down[L][:, n] / ||W_down[L][:, n]||)
        to the output of `layers[L].mlp`.
        """
        self.ensure_loaded()
        layer_vecs: Dict[int, np.ndarray] = {}
        with self.lock, torch.inference_mode():
            for p in recipe.pushes:
                if p.mode == "mul":
                    raise ValueError("Cannot compile multiplicative ('mul') mode into a static additive control vector.")
                resid_med = self.layer_resid_p50(p.layer)
                if p.mode == "random_null":
                    u = self._random_unit_vector(p.layer, p.neuron).cpu().numpy()
                else:
                    col = self.down_col(p.layer, p.neuron)
                    u = (col / col.norm().clamp(min=1e-8)).cpu().numpy()
                delta = (p.dose * resid_med) * u.astype(np.float32)
                if p.layer in layer_vecs:
                    layer_vecs[p.layer] = layer_vecs[p.layer] + delta
                else:
                    layer_vecs[p.layer] = delta
        return layer_vecs
