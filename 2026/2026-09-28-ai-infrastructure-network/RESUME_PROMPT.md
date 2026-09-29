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
   - `data/processed/assumptions.parquet` (or `.csv`)
   - `data/processed/evidence_claims.parquet` (or `.csv`)
   - `outputs/tables/financial_stress_summary.csv`
5. Inspect the executed research notebook: `notebooks/01_five_company_pilot.ipynb`. All cells have been pre-executed with live outputs and figures.
6. Phase 0 Hardened Status: Pre-Phase-1 Engineering, Bitemporal, and Epistemic Hardening are complete (ADR-011 through ADR-014). The Five-Company Pilot (NVDA, SMCI, CRWV, APLD, ORCL + MSFT, Blackstone/Magnetar, Polaris Forge 1) is FULLY CERTIFIED and FROZEN (Zero Data Drift across 20 entities, 23 obligations, 24 lifecycle events, 27 obligation facts, and 30 audited claims). Dynamic multi-tier SPV unwrapping (`APLD_COMPUTECO3` -> `APLD_HPC_HOLDINGS2` -> `APLD`), discrete obligation lifecycle events (`obligation_events.parquet`) eliminating extinction voids across filing boundaries (e.g. June 17 bridge persistence), fact-level bitemporality (`obligation_facts.parquet`) with dual truth vs knowledge claims (`truth_claim_id` vs `knowledge_claim_id`) strictly enforcing `publicly_known_from >= filing_date`, strict zero-lookahead stress simulation (reporting unknown floating debt as None rather than leaking future disclosures), half-open validity intervals $[v\_from, v\_to)$ conserving exactly 22 edges across refinancing boundaries, and 100% exact contiguous verbatim substring verification on cached raw SEC exhibits are verified.

Once you have reviewed the repository, provide a concise briefing that reports:
- The current state of the hardened pilot;
- The key takeaways from the Phase 0 stress tests (e.g. Hyperscaler capex trim impairing 98.7% of contract value, Microsoft 67% concentration on CoreWeave, SPV isolation);
- The candidate entity universe for Phase 1 expansion (e.g., expanding from 5 to 25–30 companies across upstream silicon, electrical equipment, and private credit lenders);
- Recommendations for the next immediate milestone.

Do not write any new code or modify existing data until I review your briefing and give explicit direction.
```

