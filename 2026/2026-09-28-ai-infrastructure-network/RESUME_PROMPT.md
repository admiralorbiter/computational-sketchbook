# AI Infrastructure Financial Network — Fresh Session Resume Prompt

Copy and paste the prompt below into a fresh ChatGPT, Claude, or Antigravity session when resuming work on this repository:

---

```text
I am resuming work on the AI Infrastructure Financial Network in the repository `admiralorbiter/computational-sketchbook` located at:
`2026/2026-09-28-ai-infrastructure-network/` (or root junction `ai_infrastructure_network/`).

Before proposing any changes or running new extractions, follow these strict preflight instructions:

1. Read `README.md` first. It provides the executive synthesis, empirical findings, and architecture.
2. Read `docs/methodology.md` and `docs/decisions.md` to understand the foundational modeling choices (e.g., 3 epistemic layers, 5 modes of opacity, the join-centric ontology, SPV perimeter unwrapping).
3. Read `docs/evidence_contract.md` to understand the trust hierarchy (Class A Contractual/Filed, Class B Asserted, Class C Inferred). Every edge MUST link to an immutable SEC accession number or documented public receipt.
4. Inspect the processed data artifacts:
   - `data/processed/entities.parquet` (or `.csv`)
   - `data/processed/financials.parquet` (or `.csv`)
   - `data/processed/obligations.parquet` (or `.csv`)
   - `data/processed/obligation_events.parquet` (or `.csv`)
   - `data/processed/obligation_facts.parquet` (or `.csv`)
   - `data/processed/obligation_terms.parquet` (or `.csv`)
   - `data/processed/assumptions.parquet` (or `.csv`)
   - `data/processed/evidence_claims.parquet` (or `.csv`)
   - `outputs/tables/financial_stress_summary.csv`
5. Inspect the executed research notebook: `notebooks/01_five_company_pilot.ipynb`. All cells have been pre-executed with live outputs and figures.
6. Phase 0 Freeze & Phase 1 Wave 1 Hardening Status (ADR-017, ADR-018, ADR-019): Phase 0 pilot network remains 100% frozen with zero data drift. Phase 1 Wave 1 is hardened with attribute-level contract provenance (`obligation_terms.parquet`), BDC legal identity disambiguation (`BLUE_OWL_OBDC` CIK `0001655888`), and multi-era knowledge reconciliation (5 contemporaneous Form 8-K exhibits eliminating historical knowledge censoring). The repository now models 46 entities (21 parent nodes after dynamic SPV unwrapping), 13,754 standardized financial facts across 19 SEC filers, 47 decomposed obligations, 51 lifecycle events, 59 bitemporal facts, 38 attribute terms, 2 discrete rate legs, and 48 audited primary SEC claims with 40 certified as 100% contiguous verbatim substrings in cached primary SEC HTML filings. Zero CIK collisions and zero data drift confirmed via `src/validate.py`.

Once you have reviewed the repository, provide a concise briefing that reports:
- The current state of the hardened observatory (Phase 0 baseline + Phase 1 Wave 1 expansion);
- The key takeaways from the cross-layer join density (e.g. Meta $27B offtake, CoreWeave/Core Scientific 590 MW colocation, Blue Owl/PIMCO GPU financing, Hut 8 Coatue note extinction);
- Recommendations for the next immediate milestone (e.g. Wave 2 ingestion of electrical equipment/grid bottlenecks, or cross-boundary macro stress testing).

Do not write any new code or modify existing data until I review your briefing and give explicit direction.
```

