# Origin & Provenance (`2026-10-27-qwen-neuron-steering`)

## Primary Provenance
- **Sketchbook Slug:** `2026-10-27-qwen-neuron-steering`
- **Created:** October 27, 2026
- **Originating Repository:** `computational-sketchbook` (native laboratory build)
- **Host Hardware & Runtime:** NVIDIA GeForce RTX 3060 (12 GB VRAM), Python 3.12, PyTorch 2.5.1+cu121, Transformers 5.15.0, Ollama (`qwen3.5:4b`, `gemma3:12b`)

---

## Upstream Research & Reference Artifacts

1. **`@treetowntree` (Arthur, UMSI PhD) — Qwen Neuron Zoo & Two-Neuron Breeding Pairs (Oct 26, 2026)**
   - **Source URL:** `https://x.com/treetowntree/status/2114573600976183723`
   - **Contribution:** Systematic single-neuron and two-neuron pairing sweep on `Qwen/Qwen3.5-4B` across 50 held-out questions (with pre-registered Fisher's exact test $p < 0.001$, 4 random residual-direction controls, and blind AI judge verification). Documented 21 solo trait neurons (including *Cookie* `L24 N3102 +0.8`, *Jesus* `L15 N4041 +0.8`, *Fate & destiny* `L24 N6441 -0.8`, *Groveling apology* `L7 N4595 -0.8`, *"You're absolutely right"* `L16 N8115 -0.7`, *Cartoon mascot* `L9 N9009 +0.8`) and 16 two-neuron pairs at $0.75\times$ solo dose demonstrating emergent synthesis (*Cookie + Cartoon mascot = Cookie Monster*, *Hugs + Cartoon mascot = Plush Toy*) vs. single-neuron dominance and additive coexistence.

2. **Lyra C (`@_lyraaaa_` / `lyramakesmusic`) — `neuron-explorer` & "Evil Qwen" (Oct 2026)**
   - **Source Repository:** `https://github.com/lyramakesmusic/neuron-explorer`
   - **Contribution:** Steering-first MLP interpretability methodology for `Qwen/Qwen3.5-4B` hooking `model.language_model.layers[L].mlp.down_proj` in units of each layer's median residual stream norm (`resid_p50`); discovery of the **Evil Qwen** hostile persona recipe (`L14 N8949 +1.0` paired with `L13 N7956 -1.0`), distinct-4-gram coherence calibration curves, logit-lens projections, and `reads-you` token activation diagnostics.

3. **Bryson Tang & Nick Cammarata (Goodfire) — Positive Control & *Neural Networks Are Already Clean* (Oct 2026)**
   - **Contribution:** Positive control neuron `L22 N2742+` ("Extrali / alien causal agents" in `Qwen/Qwen3.5-4B`) and foundational framing of SwiGLU sign regimes, positive/negative neuron poles, and steering-first readout analysis.
