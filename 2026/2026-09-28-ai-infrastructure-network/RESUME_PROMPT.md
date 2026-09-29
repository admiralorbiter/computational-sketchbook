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
6. Phase 0 Epistemic Certification Status: Epistemic Hardening and Certification are complete (ADR-011 through ADR-015). The Five-Company Pilot (NVDA, SMCI, CRWV, APLD, ORCL + MSFT, Blackstone/Magnetar, MUFG, Morgan Stanley, Polaris Forge 1) is FULLY CERTIFIED and FROZEN (Zero Data Drift across 26 entities, 33 obligations, 34 lifecycle events, 42 obligation facts, and 32 audited primary claims). CoreWeave indebtedness is de-aggregated into 16 discrete tranches totaling exactly $35.551B (0.00% drift) with verified borrowing SPVs (`CRWV_CCAC_II`, `CRWV_CCAC_IV`, `CRWV_CCAC_VII`, `CRWV_FINANCING_DDTL_V`), 5 recourse parent guarantee edges (`amount = None`), and strictly non-recourse DDTL 4.0 (`CRWV_SPV_VIII`, 0 parent guarantee edge). 100% of SEC evidence claims are verified against raw EDGAR submissions JSON (`validate_sec_source_existence()`). Dynamic multi-tier SPV unwrapping, discrete obligation lifecycle events (`obligation_events.parquet`), fact-level bitemporality (`obligation_facts.parquet`) with dual truth vs knowledge claims strictly enforcing `publicly_known_from >= filing_date`, strict zero-lookahead stress simulation (reporting unmeasured floating debt as None rather than leaking future disclosures), point-in-time XBRL financial snapshot resolution (`resolve_temporal_financials`), half-open validity intervals $[v\_from, v\_to)$ conserving edges across refinancing boundaries, and 100% exact contiguous verbatim substring verification on cached raw SEC exhibits are verified.

Once you have reviewed the repository, provide a concise briefing that reports:
- The current state of the hardened pilot;
- The key takeaways from the Phase 0 stress tests (e.g. Hyperscaler capex trim impairing 98.7% of contract value, Microsoft 67% concentration on CoreWeave, SPV isolation);
- The candidate entity universe for Phase 1 expansion (e.g., expanding from 5 to 25–30 companies across upstream silicon, electrical equipment, and private credit lenders);
- Recommendations for the next immediate milestone.

Do not write any new code or modify existing data until I review your briefing and give explicit direction.
```

