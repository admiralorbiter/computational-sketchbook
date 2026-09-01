# Teaching Guide & Lab Pattern

Last updated: 2025-08-10

## Teaching philosophy (how we teach with labs)
- Exploration-first, with clear, falsifiable predictions before running code.
- Short, guided prompts; minimal but correct math; visual differences vs baseline.
- Self-checks with numeric tolerances, so learners can verify without spoilers.
- Visible artifacts: parameters block, figures, CSVs, and a one-page memo.

## Lab flow (repeat for every project)
1) Explore: Play with sliders and read the caption (“what to look at”).
2) Predict: Write down what you expect (signs, direction, relative magnitudes).
3) Run: Execute the scenario(s) with a fixed seed.
4) Explain: Compare to baseline; focus on deltas and incidence.
5) Check: Use self-check boxes (numeric targets within tolerance) and rationale.
6) Extend: Change 1 assumption or add 1 friction; repeat 2–5.

## Required teaching artifacts (per lab)
- Prompts: 6–10 questions from basic to stretch, each with a target concept.
- Self-checks: A small table of ground-truth values for default params and 2–3 scenarios, plus acceptable tolerances.
- Reflection: “What surprised me” (1–3 bullets) and “Next change I’d try”.
- Answer key: Separate instructor-only note or hidden section with exact numbers and short rationale.

## Self-check design
- Provide a small set of canonical scenarios with fixed parameters.
- Report accepted answers with tolerance bands (e.g., ±1e-6 for closed-form, ±1e-2 for simulated).
- Encourage reasoning: after a numeric check passes, show the one-sentence why.

## Assessment rubric (quick)
- Baseline: can compute equilibrium and interpret CS/PS (pass/fail).
- Policy: can predict sign of Δ and identify incidence (pass/fail).
- Extension: can articulate a reasonable next change and expected direction (pass/fail).

## Author checklist (for instructors)
- Write 2–3 “Try this” prompts tied to the UI controls.
- Provide at least one qualitative KC tie-in.
- Include 3 plots: baseline, one policy, one difference/bar/heatmap.
- Keep the answer key concise: numbers + one-sentence rationale per prompt.


