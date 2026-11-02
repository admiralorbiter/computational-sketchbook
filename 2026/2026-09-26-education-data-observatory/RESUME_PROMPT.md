# Education Data Observatory — Fresh Session Resume Prompt

Copy and paste the prompt below into a fresh ChatGPT / LLM session when resuming work on this repository:

---

```text
I am resuming work on the Education Data Observatory in the repository `admiralorbiter/computational-sketchbook` located at:
`2026/2026-09-26-education-data-observatory/`

Before writing any new code or performing any new research, follow these strict preflight instructions:

1. Read `HANDOFF.md` first. It is the authoritative cold-start context document explaining the architecture, the 20 frozen claims, and the epistemic trust hierarchy.
2. Read `README.md` and `DECISIONS.md` to understand the methodological choices learned the hard way (e.g., 9-county MARC geography, dynamic vs. balanced universes, missing != zero, PTR != class size).
3. Read the machine-readable registries:
   - `registry/measures.csv`
   - `registry/universes.csv`
   - `registry/operationalizations.csv`
   - `data/upstream_artifacts.csv`
   - `analysis/results/claims.csv`
4. Inspect or run `python scripts/validate_observatory.py`. Ensure all 21 named validation checks pass with 0 errors and 0 warnings.
5. Strictly respect the frozen core: `EDU-001` (PTR), `EDU-002` (Enrollment), and `EDU-003` (Teacher FTE) are AUDITED and PERMANENTLY FROZEN. Do not reopen them or propose alternative calculations unless the strict reopening criteria in `HANDOFF.md` Section 8 are demonstrated.
6. Epistemic Trust Hierarchy: Do not trust old conversational summaries or prose completion memos if they conflict with the machine-readable registries and `claims.csv`.

Once you have reviewed the repository, provide a concise briefing that reports:
- The current project state (Milestone 1 Complete, Paused);
- What is frozen (EDU-001, EDU-002, EDU-003 and their 20 claims);
- Unresolved empirical limitations (e.g., personnel role composition pending state microdata);
- The logical options for the next measure (with `EDU-005 Paraprofessional FTE` as the planned next candidate).

Do not begin any code implementation or research until I review your briefing and explicitly choose the next task.
```
