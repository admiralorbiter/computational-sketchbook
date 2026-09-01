# Origin: Smoke & Tolerance (`smoke-and-tolerance`)

- **Original Repository:** `https://github.com/admiralorbiter/smoke-and-tolerance` (Archived & Private)
- **Date Created:** June 13, 2026
- **Consolidated into Sketchbook:** 2026-09-01
- **Tech Stack:** Rust (WASM, `wasm-bindgen`), TypeScript, Vite, HTML5 Canvas, Web Audio API

---

## 1. Concept & Hypothesis

Can the interacting constraints, mechanical tolerances, and unreliability of early historical technologies become intuitive to a learner by letting them manipulate an abstract systems model and inspect otherwise invisible internal state?

---

## 2. What Was Built

- **Rust/WASM Physics Engine (`sim/`):** Models combustion kinetics, chamber pressure curves, projectile gas leakage (windage clearance), thermal convection, and cumulative plastic/elastic metal fatigue.
- **Interactive Laboratory UI (`src/`):**
  - **Alchemical Optography Lenses:** Real-time visual overlays for heat transfer (*Phlogiston Lens*), fouling soot deposits (*Tria Prima Lens*), and structural micro-fissure stress (*Astraea Lens*).
  - **Timeline Scrubber:** Frame-by-frame diagnostic replay of ignition, pressure buildup, projectile movement, and ballistics.
  - **Diagnostic Post-Shot Cards:** Causal explanations for misfires, jams, low velocities, and barrel ruptures.
  - **Maintenance Workshop:** Wet/dry swabbing routines, touch-hole vent bushing replacement, and persistent metallurgical fatigue remediation.
- **Synthesized Web Audio:** Telemetry-driven soundscape mapping pressure leaks, barrel strain, and weather variables to Web Audio oscillator nodes.

---

## 3. Why It Stopped & Lineage Value

- **Complete Probe:** Built in ~9 hours across a single weekend (June 13–14, 2026). It completely proved its design hypothesis: making hidden causal state visible enables learners to form and test scientific explanations.
- **Pedagogical Invariant:**
  $$\text{Visible Outcome ("What happened?")} + \text{Hidden-State View ("What happened inside?")} + \text{Diagnosis ("Why?")} \longrightarrow \text{Learner Hypothesis}$$
