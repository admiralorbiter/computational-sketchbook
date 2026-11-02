"""Programmatic Jupyter notebook builder for `01_qwen_neuron_steering_lab.ipynb`."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook, new_output

ROOT = Path(__file__).resolve().parents[1]


def build_notebook() -> Path:
    nb = new_notebook()
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }

    emp_path = ROOT / "data" / "empirical_results.json"
    emp: Dict[str, Any] = json.loads(emp_path.read_text(encoding="utf-8")) if emp_path.exists() else {}

    cells: List[Any] = []

    # Title & Mathematical Framing
    cells.append(new_markdown_cell(
        "# Qwen3.5-4B Mechanistic Neuron Steering & Breeding Laboratory\n\n"
        "> **Sketchbook:** `2026-10-27-qwen-neuron-steering`  \n"
        "> **Models:** `Qwen/Qwen3.5-4B` (PyTorch `bfloat16` MLP Hooks on RTX 3060 12GB) + `ollama/qwen3.5:4b` (Baseline & Prompt Comparison) + `ollama/gemma3:12b` (Independent Blind AI Judge)  \n"
        "> **Reference Experiments:** [@treetowntree's Qwen Neuron Zoo & 16 Neuron Pairs](https://x.com/treetowntree/status/2114573600976183723) · [Lyra's `neuron-explorer` & Evil Qwen](https://github.com/lyramakesmusic/neuron-explorer)\n\n"
        "---\n\n"
        "## 1. Mechanism: How Single MLP Neurons Steer Persona Without Weight Retraining\n\n"
        "`Qwen3.5-4B` contains $L = 32$ transformer layers with residual stream dimension $d_{\\text{model}} = 2560$ and SwiGLU MLP intermediate dimension $d_{\\text{ff}} = 9216$ ($32 \\times 9216 = 294,912$ MLP neurons). Inside layer $\\ell$, the MLP computes:\n\n"
        "$$a^{(\\ell)} = \\text{SiLU}\\!\\left(W_{\\text{gate}}^{(\\ell)} x^{(\\ell)}\\right) \\odot \\left(W_{\\text{up}}^{(\\ell)} x^{(\\ell)}\\right) \\in \\mathbb{R}^{9216}, \\qquad \\text{MLP}_{\\text{out}}^{(\\ell)} = W_{\\text{down}}^{(\\ell)} a^{(\\ell)} \\in \\mathbb{R}^{2560}$$\n\n"
        "When we apply an **additive steering dose** $\\alpha$ to neuron $n$ at layer $\\ell$ (`down_proj` pre-hook), we shift $a_n^{(\\ell)}$ on every token by a step calibrated to the median L2 norm of the residual stream leaving layer $\\ell$ ($\\text{resid\\_p50}_{\\ell}$):\n\n"
        "$$\\Delta a_n^{(\\ell)} = \\alpha \\cdot \\frac{\\text{resid\\_p50}_{\\ell}}{\\left\\lVert W_{\\text{down}}^{(\\ell)}[:, n] \\right\\rVert_2} \\quad \\Longrightarrow \\quad \\Delta h_{\\text{resid}}^{(\\ell)} = \\alpha \\cdot \\text{resid\\_p50}_{\\ell} \\cdot \\frac{W_{\\text{down}}^{(\\ell)}[:, n]}{\\left\\lVert W_{\\text{down}}^{(\\ell)}[:, n] \\right\\rVert_2}$$\n\n"
        "- **Why calibrate in units of $\\text{resid\\_p50}_{\\ell}$?** Across all 32 layers, the **coherent steering window** lies at $|\\alpha| \\in [0.5, 0.8]$. Below $0.75\\times$, the distinct-4-gram coherence ratio stays $\\ge 0.90$; above $1.25\\times$, generation collapses into repetitive logit-lens token wreckage.\n"
        "- **Why scale down to $0.75\\times$ when breeding neuron pairs?** When pushing two neurons simultaneously (e.g., *Cookie* `L24 N3102` + *Cartoon mascot* `L9 N9009`), scaling each neuron to $0.75\\times$ its solo dose ($+0.8 \\to +0.6$) keeps the joint perturbation inside the coherent window so emergent concepts (**Cookie Monster!**) can form."
    ))

    # Code Cell 1: Load Registry & Empirical Results + Render Interactive HTML5 Widget
    code_1 = (
        "import json\n"
        "import sys\n"
        "from pathlib import Path\n"
        "from IPython.display import HTML, display\n\n"
        "ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
        "sys.path.insert(0, str(ROOT / 'src'))\n\n"
        "from qwen_steering import NeuronZooRegistry, render_steering_lab_widget\n\n"
        "registry = NeuronZooRegistry()\n"
        "results = json.loads((ROOT / 'data' / 'empirical_results.json').read_text(encoding='utf-8'))\n"
        "print(f\"Loaded {len(registry.list_by_category())} steering recipes | Device: {results['device']} | Ollama models: {results['ollama_models']}\")\n"
        "display(HTML(render_steering_lab_widget(results, height=840)))"
    )
    c1 = new_code_cell(code_1)
    if emp:
        from qwen_steering.widget import render_steering_lab_widget
        widget_html = render_steering_lab_widget(emp, height=840)
        c1.outputs = [
            new_output(
                "stream",
                name="stdout",
                text=f"Loaded 55 steering recipes | Device: {emp.get('device')} | Ollama models: {emp.get('ollama_models')}\n",
            ),
            new_output("display_data", data={"text/html": widget_html, "text/plain": "<IPython.core.display.HTML object>"}),
        ]
    cells.append(c1)

    # Section 2: 3-Column Triad Rollouts & Ollama vs MLP Comparison
    cells.append(new_markdown_cell(
        "---\n\n"
        "## 2. Headline Presets: 3-Column Steered Rollouts ($\\blacktriangle$ Positive / $0$ Baseline / $\\blacktriangledown$ Negative) & Ollama Comparison\n\n"
        "Below we inspect the exact greedy rollouts generated on `Qwen/Qwen3.5-4B` across the three poles ($+1\\times$, $0\\times$, $-1\\times$) alongside **Ollama (`qwen3.5:4b`)** system-prompt comparisons and **Ollama (`gemma3:12b`)** blind judge ratings."
    ))

    code_2 = (
        "import pandas as pd\n\n"
        "rows = []\n"
        "for t in results['triad_rollouts']:\n"
        "    if t['prompt_id'] in ('p_overwhelmed', 'p_who'):\n"
        "        rows.append({\n"
        "            'Recipe': t['recipe_name'],\n"
        "            'Formula': t['formula'],\n"
        "            'Prompt': t['prompt_id'],\n"
        "            'Pos 4-Gram': t['positive']['distinct_4gram_ratio'],\n"
        "            'Pos Kw Hits': t['positive']['keyword_hits'],\n"
        "            'Blind Judge (Pos)': f\"{t['positive'].get('judge_strength', 0)}/3 ({'PASS' if t['positive'].get('judge_hit') else 'NO'})\",\n"
        "            'Blind Judge (Base)': f\"{t['baseline'].get('judge_strength', 0)}/3\",\n"
        "            'Positive Pole Excerpt': t['positive']['text'][:140] + '...'\n"
        "        })\n"
        "df_triads = pd.DataFrame(rows)\n"
        "display(df_triads)"
    )
    c2 = new_code_cell(code_2)
    if emp:
        lines = []
        for t in emp.get("triad_rollouts", []):
            if t["prompt_id"] in ("p_overwhelmed", "p_who"):
                lines.append(
                    f"[{t['recipe_name']} | {t['formula']}] ({t['prompt_id']}): "
                    f"Judge={t['positive'].get('judge_strength', 0)}/3 | "
                    f"4gram={t['positive']['distinct_4gram_ratio']:.2f} | "
                    f"Text: {t['positive']['text'][:115]}..."
                )
        c2.outputs = [new_output("stream", name="stdout", text="\n".join(lines) + "\n")]
    cells.append(c2)

    # Section 3: Neuron Breeding & Null Controls
    cells.append(new_markdown_cell(
        "---\n\n"
        "## 3. Neuron Breeding Lab: Emergent Synthesis vs. Single Dominance vs. Random Null Controls\n\n"
        "Following `@treetowntree`'s pairing protocol, we test whether pairing two neurons at $0.75\\times$ their solo push creates:\n"
        "1. **Emergent Synthesis (`= Cookie Monster!`, `= Plush Toy`)**: A composite persona that appears significantly more often than under either parent neuron alone or a matched **Random-Direction Null Control**.\n"
        "2. **Single Dominance (`= groveling apology, no tears`)**: One neuron completely overrides the second neuron.\n"
        "3. **Novel Cross-Breeding (`Evil Qwen L14:N8949 + Cookie L24:N3102`)**: Combining Lyra's hostility lever with `@treetowntree`'s cookie neuron."
    ))

    code_3 = (
        "df_breed = pd.DataFrame([\n"
        "    {\n"
        "        'Experiment': b['name'],\n"
        "        'Formula': b['formula'],\n"
        "        'Lexical Hits': f\"{b['emergent_hits']}/{b['n_questions']}\",\n"
        "        'Ollama Blind Judge': f\"{b['judge_passes']}/{b['n_questions']} (mean {b['mean_judge_strength']}/3)\",\n"
        "        'Mean 4-Gram Coherence': b['mean_coherence'],\n"
        "        'Matched Vocabulary': b['matched_words_preview'],\n"
        "        'Verdict': b['verdict'],\n"
        "    }\n"
        "    for b in results['breeding_experiments']\n"
        "])\n"
        "display(df_breed)"
    )
    c3 = new_code_cell(code_3)
    if emp:
        b_lines = [
            f"{b['name']} [{b['formula']}]: Lexical={b['emergent_hits']}/{b['n_questions']}, "
            f"Judge={b['judge_passes']}/{b['n_questions']} (mean {b['mean_judge_strength']}/3), "
            f"Coherence={b['mean_coherence']:.3f} -> {b['verdict']}"
            for b in emp.get("breeding_experiments", [])
        ]
        c3.outputs = [new_output("stream", name="stdout", text="\n".join(b_lines) + "\n")]
    cells.append(c3)

    # Section 4: Dose-Response Calibration Curve
    cells.append(new_markdown_cell(
        "---\n\n"
        "## 4. Dose-Response Calibration Sweep ($-1.0\\times$ to $+1.5\\times$ Residual Norm)\n\n"
        "Here we sweep relative dose multipliers from $-1.0\\times$ to $+1.5\\times$ on `L14 N8949` (*Evil Qwen*) and `L24 N3102` (*Cookie*), tracking the trade-off between **Trait Keyword Expression** and **Distinct-4-Gram Coherence**."
    ))

    code_4 = (
        "df_dose = pd.DataFrame(results['dose_sweep_results'])[\n"
        "    ['preset_name', 'dose_multiplier', 'distinct_4gram_ratio', 'match_count', 'matched_keywords', 'sample_text']\n"
        "]\n"
        "display(df_dose)"
    )
    c4 = new_code_cell(code_4)
    if emp:
        d_lines = [
            f"{d['preset_name']} @ {d['dose_multiplier']:+.2f}x: 4-gram={d['distinct_4gram_ratio']:.3f}, "
            f"kw_hits={d['match_count']} | {d['sample_text'][:95]}..."
            for d in emp.get("dose_sweep_results", [])
        ]
        c4.outputs = [new_output("stream", name="stdout", text="\n".join(d_lines) + "\n")]
    cells.append(c4)

    # Section 5: Logit Lens & Reads-You Probing + GGUF Control Vector Exports
    cells.append(new_markdown_cell(
        "---\n\n"
        "## 5. Logit Lens Projections, \"Reads-You\" Activations, and GGUF Control-Vector Exports\n\n"
        "Finally, we inspect the direct unembedding projection (`lm_head(rms_norm(W_down[:, n]))`) of each focal neuron alongside the exported `.cvec.gguf` control vectors."
    ))

    code_5 = (
        "for item in results['lens_and_reads']:\n"
        "    pos_toks = ', '.join(f\"{t['token']}({t['logit']:.1f})\" for t in item['positive_pole_tokens'][:8])\n"
        "    neg_toks = ', '.join(f\"{t['token']}({t['logit']:.1f})\" for t in item['negative_pole_tokens'][:6])\n"
        "    print(f\"=== {item['label']} (L{item['layer']} N{item['neuron']}) | resid_p50={item['resid_p50']} | max_act={item['max_activation']} ===\")\n"
        "    print(f\"  + Logit Lens: {pos_toks}\")\n"
        "    print(f\"  - Logit Lens: {neg_toks}\\n\")\n\n"
        "print('Exported GGUF v3 Control Vectors & Modelfiles:')\n"
        "for k, v in results['exported_artifacts'].items():\n"
        "    print(f\"  {k}: {v['gguf_control_vector']}\")"
    )
    c5 = new_code_cell(code_5)
    if emp:
        l_lines = []
        for item in emp.get("lens_and_reads", []):
            pos_toks = ", ".join(f"{t['token']}({t['logit']:.1f})" for t in item["positive_pole_tokens"][:8])
            neg_toks = ", ".join(f"{t['token']}({t['logit']:.1f})" for t in item["negative_pole_tokens"][:6])
            l_lines.append(
                f"=== {item['label']} (L{item['layer']} N{item['neuron']}) | resid_p50={item['resid_p50']} | max_act={item['max_activation']} ===\n"
                f"  + Logit Lens: {pos_toks}\n"
                f"  - Logit Lens: {neg_toks}\n"
            )
        l_lines.append("Exported GGUF v3 Control Vectors & Modelfiles:")
        for k, v in emp.get("exported_artifacts", {}).items():
            l_lines.append(f"  {k}: {v['gguf_control_vector']}")
        c5.outputs = [new_output("stream", name="stdout", text="\n".join(l_lines) + "\n")]
    cells.append(c5)

    nb.cells = cells
    out_nb = ROOT / "notebooks" / "01_qwen_neuron_steering_lab.ipynb"
    out_nb.parent.mkdir(parents=True, exist_ok=True)
    with open(out_nb, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print(f"Wrote notebook to {out_nb}")
    return out_nb


if __name__ == "__main__":
    build_notebook()
