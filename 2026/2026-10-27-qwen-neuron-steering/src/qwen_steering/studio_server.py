"""Live Interactive Web Studio for Qwen3.5-4B MLP Neuron Steering & Ollama Comparison.

Run with:
    python -m qwen_steering.studio_server --port 8795
"""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict

from .engine import QwenSteeringEngine
from .evaluation import match_trait_keywords
from .ollama_bridge import OllamaBridge, export_recipe_artifacts
from .registry import NeuronPush, NeuronZooRegistry, SteeringRecipe

STUDIO_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Qwen3.5-4B Live Neuron Steering Studio</title>
<style>
  :root {
    --bg: #0d1117; --panel: #161b22; --border: #30363d; --text: #e6edf3;
    --muted: #8b949e; --accent: #58a6ff; --pos: #3fb950; --neg: #f85149; --gold: #d29922;
  }
  * { box-sizing: border-box; }
  body { margin: 0; padding: 20px; background: var(--bg); color: var(--text); font-family: system-ui, sans-serif; font-size: 14px; }
  .bar { display: flex; gap: 12px; align-items: center; background: var(--panel); border: 1px solid var(--border); padding: 12px; border-radius: 8px; margin-bottom: 14px; flex-wrap: wrap; }
  select, input, textarea, button { background: #0d1117; color: var(--text); border: 1px solid var(--border); border-radius: 6px; padding: 7px 10px; font-size: 13px; }
  button { background: #238636; border-color: #2ea043; cursor: pointer; font-weight: 600; }
  button.secondary { background: #21262d; border-color: var(--border); }
  .grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }
  .card { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 14px; }
  .pre { white-space: pre-wrap; background: #0d1117; padding: 10px; border-radius: 6px; border: 1px solid #21262d; min-height: 150px; font-size: 13px; line-height: 1.5; }
  .tok { display: inline-block; padding: 2px 5px; margin: 2px 1px; border-radius: 4px; font-family: monospace; }
</style>
</head>
<body>
  <h2 style="margin-top:0;">Qwen3.5-4B Live MLP Neuron Steering & Breeding Studio</h2>
  <div class="bar">
    <label>Preset: <select id="preset" onchange="loadPreset()"></select></label>
    <label>Custom Pushes (JSON): <input id="pushes" style="width:360px; font-family:monospace;"/></label>
    <button class="secondary" onclick="exportGGUF()">Export .cvec.gguf + Modelfile</button>
    <span id="status" style="color:var(--accent); font-family:monospace;">Ready</span>
  </div>
  <div class="bar">
    <input id="prompt" style="flex:1;" value="I'm feeling really overwhelmed by my workload this week. What should I do?"/>
    <button onclick="runTriad()">Run 3-Column Steered Chat (▲ / 0 / ▼)</button>
    <button class="secondary" onclick="runReads()">Run Logit Lens & Reads-You</button>
  </div>
  <div class="grid3">
    <div class="card" style="border-top:3px solid var(--pos);">
      <strong>▲ Positive Push (+1.0×)</strong>
      <div id="out-pos" class="pre" style="margin-top:8px;"></div>
    </div>
    <div class="card" style="border-top:3px solid var(--muted);">
      <strong>0 Unsteered Baseline (0.0×)</strong>
      <div id="out-base" class="pre" style="margin-top:8px;"></div>
    </div>
    <div class="card" style="border-top:3px solid var(--neg);">
      <strong>▼ Negative Push (-1.0×)</strong>
      <div id="out-neg" class="pre" style="margin-top:8px;"></div>
    </div>
  </div>
  <div class="card" id="lens-box" style="display:none;"></div>
<script>
let RECIPES = [];
async function init() {
  const r = await fetch('/api/recipes').then(x => x.json());
  RECIPES = r.recipes;
  const sel = document.getElementById('preset');
  RECIPES.forEach((item, i) => {
    const o = document.createElement('option');
    o.value = i;
    o.textContent = item.name + ' [' + item.formula + ']';
    sel.appendChild(o);
  });
  loadPreset();
}
function loadPreset() {
  const item = RECIPES[document.getElementById('preset').value];
  if (item) document.getElementById('pushes').value = JSON.stringify(item.pushes);
}
async function runTriad() {
  document.getElementById('status').textContent = 'Running GPU forward hooks...';
  const pushes = JSON.parse(document.getElementById('pushes').value || '[]');
  const prompt = document.getElementById('prompt').value;
  const res = await fetch('/api/triad', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({prompt, pushes})
  }).then(x => x.json());
  document.getElementById('out-pos').textContent = res.positive.text + '\\n\\n[4-gram: ' + res.positive.distinct_4gram_ratio + ']';
  document.getElementById('out-base').textContent = res.baseline.text + '\\n\\n[4-gram: ' + res.baseline.distinct_4gram_ratio + ']';
  document.getElementById('out-neg').textContent = res.negative.text + '\\n\\n[4-gram: ' + res.negative.distinct_4gram_ratio + ']';
  document.getElementById('status').textContent = 'Done';
}
async function runReads() {
  const pushes = JSON.parse(document.getElementById('pushes').value || '[]');
  if (!pushes.length) return;
  const p0 = pushes[0];
  document.getElementById('status').textContent = 'Probing L' + p0.layer + ' N' + p0.neuron + '...';
  const res = await fetch('/api/probe', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text: document.getElementById('prompt').value, layer: p0.layer, neuron: p0.neuron})
  }).then(x => x.json());
  const box = document.getElementById('lens-box');
  box.style.display = 'block';
  const up = res.lens.positive_pole_tokens.map(t => t.token + ' (' + t.logit + ')').join(', ');
  const dn = res.lens.negative_pole_tokens.map(t => t.token + ' (' + t.logit + ')').join(', ');
  const toks = res.reads.tokens.map(t => `<span class="tok" style="background:rgba(63,185,80,${Math.min(0.85, Math.max(0, t.activation/10)).toFixed(2)})" title="${t.activation}">${t.token}</span>`).join('');
  box.innerHTML = `<strong>Logit Lens L${p0.layer} N${p0.neuron}</strong><br/>+ Pole: <code>${up}</code><br/>- Pole: <code>${dn}</code><hr style="border-color:#30363d"/><strong>Reads-You Token Activations:</strong><div>${toks}</div>`;
  document.getElementById('status').textContent = 'Done';
}
async function exportGGUF() {
  const item = RECIPES[document.getElementById('preset').value];
  const pushes = JSON.parse(document.getElementById('pushes').value || '[]');
  const res = await fetch('/api/export', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: item ? item.id : 'custom', name: item ? item.name : 'Custom', pushes})
  }).then(x => x.json());
  document.getElementById('status').textContent = 'Exported: ' + res.gguf_control_vector;
}
init();
</script>
</body>
</html>
"""


def run_studio_server(host: str = "127.0.0.1", port: int = 8795) -> None:
    registry = NeuronZooRegistry()
    engine = QwenSteeringEngine()
    ollama = OllamaBridge()
    export_dir = Path(__file__).resolve().parents[2] / "data" / "exports"

    class Handler(BaseHTTPRequestHandler):
        def _send_json(self, obj: Any, status: int = 200) -> None:
            raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self) -> None:
            if self.path == "/" or self.path.startswith("/index"):
                raw = STUDIO_HTML.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
            elif self.path == "/api/recipes":
                self._send_json({"recipes": [r.to_dict() for r in registry.list_by_category() if r.pushes]})
            else:
                self._send_json({"error": "not found"}, 404)

        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            if self.path == "/api/triad":
                pushes = tuple(
                    NeuronPush(int(p["layer"]), int(p["neuron"]), float(p["dose"]), p.get("mode", "add"))
                    for p in body.get("pushes", [])
                )
                recipe = SteeringRecipe("custom", "Custom", "custom", "", pushes)
                out = engine.generate_triad(body.get("prompt", "Hello!"), recipe, max_new_tokens=140)
                self._send_json(out)
            elif self.path == "/api/probe":
                layer = int(body.get("layer", 14))
                neuron = int(body.get("neuron", 8949))
                text = body.get("text", "Hello!")
                self._send_json({
                    "lens": engine.logit_lens(layer, neuron),
                    "reads": engine.read_token_activations(text, layer, neuron),
                })
            elif self.path == "/api/export":
                pushes = tuple(
                    NeuronPush(int(p["layer"]), int(p["neuron"]), float(p["dose"]), p.get("mode", "add"))
                    for p in body.get("pushes", [])
                )
                recipe = SteeringRecipe(body.get("id", "custom"), body.get("name", "Custom"), "custom", "", pushes)
                vecs = engine.compute_residual_steering_vectors(recipe)
                paths = export_recipe_artifacts(recipe, vecs, export_dir=export_dir, base_ollama_model=ollama.qwen_model)
                self._send_json(paths)
            else:
                self._send_json({"error": "not found"}, 404)

    srv = ThreadingHTTPServer((host, port), Handler)
    print(f"Qwen3.5-4B Steering Studio listening on http://{host}:{port}")
    srv.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8795)
    args = parser.parse_args()
    run_studio_server(args.host, args.port)
