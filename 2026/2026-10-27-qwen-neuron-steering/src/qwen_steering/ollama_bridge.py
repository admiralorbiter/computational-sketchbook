"""Ollama integration bridge for Qwen3.5-4B neuron steering experiments.

Provides three core capabilities:
1. Live Ollama inference (`qwen3.5:4b`) for unsteered baseline and system-prompt steering
   comparisons against internal MLP activation steering.
2. Blind AI Judge (`gemma3:12b` or `qwen3.5:4b`) implementing @treetowntree's blind JSON
   evaluation protocol (`exhibits_trait`, `strength_0_to_3`, `coherence_0_to_3`, `evidence_quote`).
3. Pure-Python GGUF v3 Control Vector (`direction.{layer}`) & Ollama Modelfile exporter so
   any discovered MLP neuron recipe can be exported to `.gguf` and `.npz`.
"""
from __future__ import annotations

import json
import struct
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from .registry import DATA_DIR, SteeringRecipe

OLLAMA_BASE_URL = "http://localhost:11434"


class OllamaBridge:
    """Client for local Ollama API + GGUF control vector exporter."""

    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        qwen_model: str = "qwen3.5:4b",
        judge_model: str = "gemma3:12b",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.qwen_model = qwen_model
        self.judge_model = judge_model
        with open(DATA_DIR / "eval_questions.json", "r", encoding="utf-8") as f:
            raw_eval = json.load(f)
        self.judge_template: Dict[str, str] = raw_eval["blind_judge_template"]

    def list_models(self) -> List[str]:
        """Return list of locally installed Ollama model tags."""
        req = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []

    def chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 180,
        json_mode: bool = False,
        disable_thinking: bool = True,
    ) -> str:
        """Run a single-turn chat completion against local Ollama."""
        target_model = model or self.qwen_model
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if disable_thinking and "qwen3" in target_model.lower():
            payload["think"] = False
        if json_mode:
            payload["format"] = "json"

        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=90) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("message", {}).get("content", "").strip()

    def blind_judge_response(
        self,
        question: str,
        response_text: str,
        trait_name: str,
        trait_description: str,
        judge_model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Evaluate `response_text` blind to condition using local Ollama judge (`gemma3:12b`)."""
        user_msg = self.judge_template["user_template"].format(
            question=question,
            trait_name=trait_name,
            trait_description=trait_description,
            response=response_text,
        )
        raw = self.chat(
            prompt=user_msg,
            model=judge_model or self.judge_model,
            system_prompt=self.judge_template["system_prompt"],
            temperature=0.0,
            max_tokens=200,
            json_mode=True,
            disable_thinking=True,
        )
        try:
            parsed = json.loads(raw)
            return {
                "exhibits_trait": bool(parsed.get("exhibits_trait", False)),
                "strength_0_to_3": int(parsed.get("strength_0_to_3", 0)),
                "coherence_0_to_3": int(parsed.get("coherence_0_to_3", 3)),
                "evidence_quote": str(parsed.get("evidence_quote", "")),
            }
        except Exception:
            return {
                "exhibits_trait": False,
                "strength_0_to_3": 0,
                "coherence_0_to_3": 0,
                "evidence_quote": f"Parse fallback: {raw[:120]}",
            }


def write_gguf_control_vector(
    output_path: Path,
    layer_vectors: Dict[int, np.ndarray],
    architecture: str = "qwen35",
    description: str = "",
) -> Path:
    """Write a spec-compliant GGUF v3 Control Vector file (`direction.{layer}` float32 tensors).

    Compatible with `llama-cli` / `llama-server --control-vector <file.gguf>` on Qwen3.5-4B GGUF.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sorted_layers = sorted(layer_vectors.keys())

    def _pack_str(s: str) -> bytes:
        b = s.encode("utf-8")
        return struct.pack("<Q", len(b)) + b

    # Metadata KV entries:
    # 1. general.architecture (STRING = 8)
    # 2. general.type (STRING = 8) -> "control_vector"
    # 3. general.description (STRING = 8)
    kv_entries = [
        ("general.architecture", architecture),
        ("general.type", "control_vector"),
        ("general.description", description),
    ]

    buf = bytearray()
    # Header: magic "GGUF", version 3 (uint32), n_tensors (uint64), n_kv (uint64)
    buf += b"GGUF"
    buf += struct.pack("<IQQ", 3, len(sorted_layers), len(kv_entries))

    # Write KV pairs (GGUF_TYPE_STRING = 8)
    for k, v in kv_entries:
        buf += _pack_str(k)
        buf += struct.pack("<I", 8)
        buf += _pack_str(v)

    # Prepare tensor info table (1D float32 tensors: ggml_type F32 = 0)
    tensor_blobs: List[bytes] = []
    offset = 0
    for layer_idx in sorted_layers:
        vec = np.asarray(layer_vectors[layer_idx], dtype=np.float32).ravel()
        t_name = f"direction.{layer_idx}"
        buf += _pack_str(t_name)
        buf += struct.pack("<I", 1)  # n_dims = 1
        buf += struct.pack("<Q", int(vec.shape[0]))  # dim[0] = 2560
        buf += struct.pack("<I", 0)  # GGML_TYPE_F32 = 0
        buf += struct.pack("<Q", offset)
        raw_bytes = vec.tobytes()
        # Pad each tensor to 32-byte alignment
        pad_len = (32 - (len(raw_bytes) % 32)) % 32
        padded = raw_bytes + (b"\x00" * pad_len)
        tensor_blobs.append(padded)
        offset += len(padded)

    # Align data section start to 32 bytes
    header_pad = (32 - (len(buf) % 32)) % 32
    buf += b"\x00" * header_pad

    for b in tensor_blobs:
        buf += b

    output_path.write_bytes(bytes(buf))
    return output_path


def export_recipe_artifacts(
    recipe: SteeringRecipe,
    layer_vectors: Dict[int, np.ndarray],
    export_dir: Path,
    base_ollama_model: str = "qwen3.5:4b",
) -> Dict[str, str]:
    """Export `.gguf` control vector, `.npz` tensor archive, and an Ollama `Modelfile`."""
    export_dir = Path(export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)

    gguf_path = export_dir / f"{recipe.id}.cvec.gguf"
    write_gguf_control_vector(
        output_path=gguf_path,
        layer_vectors=layer_vectors,
        architecture="qwen35",
        description=f"{recipe.name} ({recipe.formula_str()})",
    )

    npz_path = export_dir / f"{recipe.id}.vectors.npz"
    np.savez(
        npz_path,
        **{f"direction_{l}": v for l, v in layer_vectors.items()},
    )

    modelfile_path = export_dir / f"Modelfile.{recipe.id}"
    modelfile_content = (
        f"# Ollama Modelfile & Control-Vector Companion for {recipe.name}\n"
        f"# Recipe Formula: {recipe.formula_str()}\n"
        f"# For true MLP activation steering in llama.cpp using Ollama's GGUF weights:\n"
        f"#   llama-cli -m <ollama_qwen35_blob> --control-vector {gguf_path.name} -p \"Who are you?\"\n\n"
        f"FROM {base_ollama_model}\n"
        f"PARAMETER temperature 0.0\n"
        f"SYSTEM \"\"\"[Neuron Steering Reference Profile: {recipe.name} | {recipe.formula_str()}]\"\"\"\n"
    )
    modelfile_path.write_text(modelfile_content, encoding="utf-8")

    return {
        "gguf_control_vector": str(gguf_path),
        "npz_archive": str(npz_path),
        "ollama_modelfile": str(modelfile_path),
    }
