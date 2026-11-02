"""Self-contained interactive HTML5/JS laboratory widget for Qwen3.5-4B neuron steering."""
from __future__ import annotations

import html
import json
from typing import Any, Dict


def render_steering_lab_widget(lab_data: Dict[str, Any], height: int = 860) -> str:
    """Render an interactive multi-tab HTML5/JS widget for Jupyter notebooks or standalone viewing."""
    payload_json = json.dumps(lab_data, ensure_ascii=False)
    escaped_payload = html.escape(payload_json, quote=True)

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>
  :root {{
    --bg: #0d1117;
    --panel: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --muted: #8b949e;
    --accent: #58a6ff;
    --pos: #3fb950;
    --neg: #f85149;
    --gold: #d29922;
    --purple: #bc8cff;
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    --mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 16px;
    background: var(--bg);
    color: var(--text);
    font-family: var(--font);
    font-size: 13.5px;
    line-height: 1.5;
  }}
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
    padding-bottom: 12px;
    margin-bottom: 14px;
  }}
  .header h2 {{
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    letter-spacing: -0.2px;
  }}
  .badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11.5px;
    font-family: var(--mono);
    background: #21262d;
    border: 1px solid var(--border);
    color: var(--accent);
  }}
  .tabs {{
    display: flex;
    gap: 8px;
    margin-bottom: 14px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    flex-wrap: wrap;
  }}
  .tab-btn {{
    background: var(--panel);
    color: var(--muted);
    border: 1px solid var(--border);
    padding: 6px 14px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    font-size: 13px;
  }}
  .tab-btn.active {{
    background: #1f2937;
    color: var(--text);
    border-color: var(--accent);
  }}
  .controls {{
    display: flex;
    gap: 12px;
    align-items: center;
    background: var(--panel);
    border: 1px solid var(--border);
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 14px;
    flex-wrap: wrap;
  }}
  select, input[type="text"] {{
    background: #0d1117;
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    font-family: var(--font);
  }}
  .triad-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }}
  .col-card {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px;
    display: flex;
    flex-direction: column;
  }}
  .col-card.pos {{ border-top: 3px solid var(--pos); }}
  .col-card.base {{ border-top: 3px solid var(--muted); }}
  .col-card.neg {{ border-top: 3px solid var(--neg); }}
  .col-title {{
    font-weight: 600;
    font-size: 13px;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .col-body {{
    white-space: pre-wrap;
    font-size: 13px;
    color: #d0d7de;
    flex: 1;
    background: #0d1117;
    padding: 10px;
    border-radius: 6px;
    border: 1px solid #21262d;
    max-height: 290px;
    overflow-y: auto;
  }}
  .meta-row {{
    margin-top: 8px;
    font-size: 11.5px;
    color: var(--muted);
    font-family: var(--mono);
    display: flex;
    justify-content: space-between;
  }}
  .zoo-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(215px, 1fr));
    gap: 10px;
  }}
  .zoo-card {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 12px;
  }}
  .zoo-card.gold {{
    border-color: var(--gold);
    background: rgba(210, 153, 34, 0.07);
  }}
  .bar-bg {{
    height: 6px;
    background: #21262d;
    border-radius: 3px;
    margin-top: 6px;
    overflow: hidden;
  }}
  .bar-fill {{
    height: 100%;
    background: var(--accent);
  }}
  .tok-chip {{
    display: inline-block;
    padding: 2px 5px;
    margin: 2px 1px;
    border-radius: 4px;
    font-family: var(--mono);
    font-size: 12.5px;
    border: 1px solid transparent;
  }}
  .lens-pill {{
    display: inline-block;
    padding: 3px 7px;
    margin: 3px;
    border-radius: 5px;
    font-family: var(--mono);
    font-size: 12px;
    background: #21262d;
    border: 1px solid var(--border);
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
  }}
  th, td {{
    border-bottom: 1px solid var(--border);
    padding: 7px 10px;
    text-align: left;
  }}
  th {{ color: var(--muted); font-weight: 600; }}
</style>
</head>
<body>
<div class="header">
  <div>
    <h2>Qwen3.5-4B Mechanistic Neuron Steering & Breeding Laboratory</h2>
    <div style="color: var(--muted); font-size: 12px;">
      294,912 MLP Neurons (32 Layers × 9,216) · Runtime <code>down_proj</code> Hook + Ollama Blind Judge
    </div>
  </div>
  <div>
    <span class="badge">Qwen/Qwen3.5-4B + ollama/qwen3.5:4b</span>
  </div>
</div>

<div class="tabs">
  <button class="tab-btn active" onclick="switchTab('triad')">1. 3-Column Steered Rollouts (▲ / 0 / ▼)</button>
  <button class="tab-btn" onclick="switchTab('breeding')">2. Neuron Breeding & Dose Curves</button>
  <button class="tab-btn" onclick="switchTab('lens')">3. Logit Lens & "Reads-You" Token Activations</button>
  <button class="tab-btn" onclick="switchTab('zoo')">4. @treetowntree Zoo & 16 Pairs Reference</button>
</div>

<div id="tab-triad">
  <div class="controls">
    <label><strong>Steering Recipe:</strong>
      <select id="recipe-select" onchange="renderTriad()"></select>
    </label>
    <label><strong>Prompt:</strong>
      <select id="prompt-select" onchange="renderTriad()"></select>
    </label>
    <span id="recipe-formula" class="badge"></span>
  </div>
  <div id="recipe-desc" style="color: var(--muted); margin-bottom: 10px; font-size: 12.5px;"></div>
  <div class="triad-grid" id="triad-container"></div>
</div>

<div id="tab-breeding" style="display:none;">
  <div class="controls">
    <strong>Empirical Dose-Response & Pair Breeding Matrix</strong>
    <span style="color: var(--muted); font-size: 12px;">
      Comparing solo parent neurons, 0.75x bred pairs, and random-direction residual controls
    </span>
  </div>
  <div id="breeding-container"></div>
</div>

<div id="tab-lens" style="display:none;">
  <div class="controls">
    <label><strong>Inspect Neuron:</strong>
      <select id="lens-select" onchange="renderLens()"></select>
    </label>
  </div>
  <div id="lens-container"></div>
</div>

<div id="tab-zoo" style="display:none;">
  <h3 style="margin: 6px 0 10px 0; font-size: 15px;">Single-Neuron Zoo (50 Held-Out Questions Benchmark)</h3>
  <div class="zoo-grid" id="zoo-single-grid"></div>
  <h3 style="margin: 18px 0 10px 0; font-size: 15px;">Two-Neuron Breeding Pairs (0.75x Solo Push Each)</h3>
  <div class="zoo-grid" id="zoo-pair-grid"></div>
</div>

<script>
const LAB_DATA = JSON.parse(document.body.getAttribute("data-payload") || "{{}}");
</script>
</body>
</html>"""

    # Inject data attribute on body and interactive JS logic
    script_logic = """
<script>
const DATA = JSON.parse(document.getElementById("lab-payload").textContent);

function switchTab(name) {
  ["triad", "breeding", "lens", "zoo"].forEach((t, idx) => {
    document.getElementById("tab-" + t).style.display = (t === name) ? "block" : "none";
    document.querySelectorAll(".tab-btn")[idx].classList.toggle("active", t === name);
  });
}

function initLab() {
  const rSel = document.getElementById("recipe-select");
  const pSel = document.getElementById("prompt-select");
  const triads = DATA.triad_rollouts || [];
  const recipes = [...new Map(triads.map(x => [x.recipe_id, x])).values()];
  recipes.forEach(r => {
    const opt = document.createElement("option");
    opt.value = r.recipe_id;
    opt.textContent = r.recipe_name + " [" + r.formula + "]";
    rSel.appendChild(opt);
  });

  const prompts = [...new Map(triads.map(x => [x.prompt_id, x])).values()];
  prompts.forEach(p => {
    const opt = document.createElement("option");
    opt.value = p.prompt_id;
    opt.textContent = p.prompt_text;
    pSel.appendChild(opt);
  });

  const lSel = document.getElementById("lens-select");
  (DATA.lens_and_reads || []).forEach((item, i) => {
    const opt = document.createElement("option");
    opt.value = i;
    opt.textContent = item.label + " (L" + item.layer + " N" + item.neuron + ")";
    lSel.appendChild(opt);
  });

  renderTriad();
  renderBreeding();
  renderLens();
  renderZoo();
}

function renderTriad() {
  const rid = document.getElementById("recipe-select").value;
  const pid = document.getElementById("prompt-select").value;
  const triads = DATA.triad_rollouts || [];
  const match = triads.find(x => x.recipe_id === rid && x.prompt_id === pid) || triads[0];
  if (!match) return;

  document.getElementById("recipe-formula").textContent = match.formula;
  document.getElementById("recipe-desc").textContent = match.description || "";

  const cols = [
    { key: "positive", title: "▲ Positive Push (+1.0× Recipe)", cls: "pos" },
    { key: "baseline", title: "0 Unsteered Baseline (0.0×)", cls: "base" },
    { key: "negative", title: "▼ Negative Push (-1.0× Inverted)", cls: "neg" }
  ];
  const container = document.getElementById("triad-container");
  container.innerHTML = cols.map(c => {
    const d = match[c.key] || {};
    const judgeBadge = d.judge_hit !== undefined
      ? `<span class="badge" style="color:${d.judge_hit ? '#3fb950' : '#8b949e'}">Judge: ${d.judge_hit ? 'PASS (' + d.judge_strength + '/3)' : '0/3'}</span>`
      : "";
    return `
      <div class="col-card ${c.cls}">
        <div class="col-title">
          <span>${c.title}</span>
          ${judgeBadge}
        </div>
        <div class="col-body">${escapeHtml(d.text || "")}</div>
        <div class="meta-row">
          <span>4-gram coherence: ${(d.distinct_4gram_ratio ?? 1.0).toFixed(2)}</span>
          <span>Trait hits: ${d.keyword_hits ?? 0}</span>
        </div>
      </div>
    `;
  }).join("");
}

function renderBreeding() {
  const bDiv = document.getElementById("breeding-container");
  const doseRows = DATA.dose_sweep_results || [];
  const breedRows = DATA.breeding_experiments || [];

  let html = `<h4 style="margin:6px 0;">A. Neuron Breeding Experiments (Solo vs Paired vs Random Control)</h4>`;
  html += `<table><thead><tr>
    <th>Experiment</th><th>Recipe Formula</th><th>Trait / Emergent Hits</th>
    <th>Ollama Blind Judge</th><th>Coherence (4-gram)</th><th>Interaction Verdict</th>
  </tr></thead><tbody>`;
  breedRows.forEach(r => {
    html += `<tr>
      <td><strong>${escapeHtml(r.name)}</strong></td>
      <td><code>${escapeHtml(r.formula)}</code></td>
      <td>${r.emergent_hits} / ${r.n_questions} (${escapeHtml(r.matched_words_preview || '')})</td>
      <td>${r.judge_passes} / ${r.n_questions} (mean ${r.mean_judge_strength}/3)</td>
      <td>${r.mean_coherence.toFixed(3)}</td>
      <td><span class="badge" style="color:${r.interaction_type === 'emergent_synthesis' ? '#d29922' : '#58a6ff'}">${escapeHtml(r.verdict)}</span></td>
    </tr>`;
  });
  html += `</tbody></table>`;

  html += `<h4 style="margin:18px 0 6px 0;">B. Dose-Response Calibration Sweep (Coherent Window vs Wreckage)</h4>`;
  html += `<table><thead><tr>
    <th>Preset</th><th>Dose Multiplier</th><th>4-Gram Coherence</th><th>Trait Keyword Count</th><th>Sample Output Excerpt</th>
  </tr></thead><tbody>`;
  doseRows.forEach(d => {
    html += `<tr>
      <td>${escapeHtml(d.preset_name)}</td>
      <td><code>${d.dose_multiplier >= 0 ? '+' : ''}${d.dose_multiplier.toFixed(2)}×</code></td>
      <td style="color:${d.distinct_4gram_ratio >= 0.85 ? '#3fb950' : (d.distinct_4gram_ratio >= 0.6 ? '#d29922' : '#f85149')}">${d.distinct_4gram_ratio.toFixed(3)}</td>
      <td>${d.match_count}</td>
      <td style="color:#8b949e; font-size:12px;">${escapeHtml((d.sample_text || '').slice(0, 140))}...</td>
    </tr>`;
  });
  html += `</tbody></table>`;
  bDiv.innerHTML = html;
}

function renderLens() {
  const idx = parseInt(document.getElementById("lens-select").value || "0", 10);
  const item = (DATA.lens_and_reads || [])[idx];
  if (!item) return;

  const upPills = (item.positive_pole_tokens || []).map(t =>
    `<span class="lens-pill" style="border-color:#238636; color:#3fb950;">${escapeHtml(t.token)} <small>(${t.logit.toFixed(1)})</small></span>`
  ).join("");
  const downPills = (item.negative_pole_tokens || []).map(t =>
    `<span class="lens-pill" style="border-color:#da3633; color:#f85149;">${escapeHtml(t.token)} <small>(${t.logit.toFixed(1)})</small></span>`
  ).join("");

  const maxAbs = Math.max(1e-4, ...item.read_tokens.map(t => Math.abs(t.activation)));
  const tokHtml = item.read_tokens.map(t => {
    const norm = t.activation / maxAbs;
    const bg = norm > 0.05
      ? `rgba(63, 185, 80, ${Math.min(0.85, Math.abs(norm) * 0.85).toFixed(2)})`
      : (norm < -0.05 ? `rgba(248, 81, 73, ${Math.min(0.85, Math.abs(norm) * 0.85).toFixed(2)})` : "transparent");
    return `<span class="tok-chip" style="background:${bg}" title="pos ${t.position}: act=${t.activation.toFixed(3)}">${escapeHtml(t.token)}</span>`;
  }).join("");

  document.getElementById("lens-container").innerHTML = `
    <div class="col-card" style="margin-bottom:12px;">
      <div class="col-title">
        <span>Logit Lens Projection: <code>lm_head(rms_norm(W_down[:, ${item.neuron}]))</code> at Layer ${item.layer}</span>
        <span class="badge">resid_p50 = ${item.resid_p50} | ||W_down|| = ${item.down_col_norm}</span>
      </div>
      <div style="margin-bottom:8px;"><strong>Promoted (+ Pole):</strong><br/>${upPills}</div>
      <div><strong>Suppressed (- Pole):</strong><br/>${downPills}</div>
    </div>
    <div class="col-card">
      <div class="col-title">
        <span>"Reads-You" Per-Token MLP Activation (<code>silu(gate) * up</code> before <code>down_proj</code>)</span>
        <span class="badge">Max: ${item.max_activation} | Min: ${item.min_activation}</span>
      </div>
      <div style="padding:10px; background:#0d1117; border-radius:6px; border:1px solid #21262d; line-height:2.0;">
        ${tokHtml}
      </div>
    </div>
  `;
}

function renderZoo() {
  const sGrid = document.getElementById("zoo-single-grid");
  const pGrid = document.getElementById("zoo-pair-grid");
  const singles = DATA.zoo_singles || [];
  const pairs = DATA.zoo_pairs || [];

  sGrid.innerHTML = singles.filter(s => s.reported_hits_out_of_50 !== null).map(s => {
    const pct = Math.round((s.reported_hits_out_of_50 / 50) * 100);
    return `
      <div class="zoo-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <strong>${escapeHtml(s.name)}</strong>
          <span class="badge">L${s.layer} N${s.neuron} ${s.dose >= 0 ? '+' : ''}${s.dose}</span>
        </div>
        <div style="font-size:18px; font-weight:700; margin-top:6px; color:var(--accent);">
          ${s.reported_hits_out_of_50}<span style="font-size:12px; color:var(--muted);">/50</span>
          <span style="font-size:11px; color:var(--muted); font-weight:400; margin-left:6px;">(normal: ${s.reported_normal_out_of_50}/50)</span>
        </div>
        <div class="bar-bg"><div class="bar-fill" style="width:${pct}%"></div></div>
      </div>
    `;
  }).join("");

  pGrid.innerHTML = pairs.map(p => {
    const isGold = p.interaction_type === "emergent_synthesis";
    return `
      <div class="zoo-card ${isGold ? 'gold' : ''}">
        <div style="font-size:12px; color:var(--muted);">${escapeHtml(p.name)}</div>
        <div style="font-weight:700; font-size:14px; margin:4px 0; color:${isGold ? 'var(--gold)' : 'var(--text)'};">
          ${escapeHtml(p.outcome_label)}
        </div>
        <div style="font-family:var(--mono); font-size:11px; color:var(--accent); margin-bottom:4px;">
          ${escapeHtml(p.formula)}
        </div>
        <div style="font-size:11.5px; color:var(--muted);">${escapeHtml(p.metric_note)}</div>
      </div>
    `;
  }).join("");
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

initLab();
</script>
"""
    full_html = html_doc.replace(
        "<script>\nconst LAB_DATA = JSON.parse(document.body.getAttribute(\"data-payload\") || \"{}\");\n</script>",
        f'<script id="lab-payload" type="application/json">{payload_json}</script>\n{script_logic}',
    )
    escaped_srcdoc = html.escape(full_html, quote=True)
    return (
        f'<iframe srcdoc="{escaped_srcdoc}" width="100%" height="{height}" '
        f'style="border:1px solid #30363d; border-radius:10px; background:#0d1117;" '
        f'frameborder="0"></iframe>'
    )
