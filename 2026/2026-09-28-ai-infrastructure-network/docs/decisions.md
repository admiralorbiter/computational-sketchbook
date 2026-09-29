# Architectural Decisions Log (`docs/decisions.md`)

This log records the durable architectural, methodological, and data design choices for the AI Infrastructure Financial Network project.

---

### ADR-001: Separation of Obligation Graph (Layer 2) from Financial Statements (Layer 1)
- **Status:** Accepted (2026-09-28)
- **Context:** Standard equity and credit research models focus on individual corporate financial statements (Revenue, Debt/EBITDA, Cash Flow). However, systemic risk in large infrastructure buildouts emerges from the joint contractual obligations between entities ("the bubble in the joins").
- **Decision:** Separate the analytical architecture into three distinct layers: (1) Standardized accounting financials via SEC XBRL, (2) The contractual obligation graph where contracts are directed edges with rich legal attributes, and (3) Shared systemic assumptions.
- **Consequences:** Financial statements provide the baseline solvency capacity of individual nodes, while the obligation graph provides the transmission network across which shocks propagate.

---

### ADR-002: Direct SEC EDGAR XBRL Ingestion with Duration & Debt Normalization
- **Status:** Accepted (2026-09-28, Updated Phase 0.5)
- **Context:** Initial XBRL extraction picked single unaggregated concepts (e.g. DebtCurrent instead of total debt) and mixed instant balance sheet facts with non-comparable duration flows.
- **Decision:** Explicitly separate instant balance sheet facts from duration flow facts (3-month quarterly vs 12-month annual). Aggregate funded debt components (`LongTermDebtNoncurrent` + `DebtCurrent` + `ConvertibleNotes` or `DebtInstrumentCarryingAmount`). Never use `GrossProfit` as a fallback for revenue.
- **Consequences:** Restores true balance sheet totals across all nodes: APLD ($4.98B debt), CRWV ($35.55B debt principal), SMCI ($8.72B total debt), ORCL ($125.34B debt), and NVDA ($33.37B debt).

---

### ADR-003: MultiDiGraph Adoption and Elimination of False Netting
- **Status:** Accepted (2026-09-28, Phase 0.5)
- **Context:** Initial graph modeling used `nx.DiGraph`, overwriting multiple distinct agreements between identical counterparty pairs. Furthermore, the repository computed `outgoing - incoming = net contractual exposure`, netting a 15-year lease against a 2-year purchase commitment or equity stake.
- **Decision:** Migrate to `nx.MultiDiGraph(edge_key=obligation_id)`. Delete the `net_contractual_exposure_usd` metric. Categorize exposure strictly by `amount_type` (`principal_outstanding`, `lifetime_contract_value`, `remaining_commitment`, `annualized_run_rate`, `contingent_guarantee`, `equity_investment`).
- **Consequences:** Preserves distinct facilities (DDTLs, notes, convertibles, leases, springing guarantees) and eliminates non-fungible netting distortions.

---

### ADR-004: Explicit Separation of Reachability Footprints vs Financial Stress
- **Status:** Accepted (2026-09-28, Phase 0.5)
- **Context:** The initial stress engine marked 100% of face value as impaired for all edges within two hops of an assumption. While valuable as a topological exposure metric, calling this "financial stress loss" was misleading.
- **Decision:** Bifurcate into two distinct tools:
  1. `src/reachability.py` (`ContractualReachability`): Evaluates topological reachability and assumption dependency footprints (% of network face value within 1-2 hops).
  2. `src/stress.py` (`FinancialStressEngine`): Implements true mathematical transmission functions:
     $$\text{Shock} \longrightarrow \Delta \text{ Cash Flow} \longrightarrow \text{Collateral / Covenant Breach} \longrightarrow \text{Liquidity Cure} \longrightarrow \text{Next Edge}$$
- **Consequences:** Provides rigorous topological exposure metrics without conflating reachability with financial default.

---

### ADR-005: Modeling Contingent Springing Guarantees in Perimeter Opacity
- **Status:** Accepted (2026-09-28, Phase 0.5)
- **Context:** CoreWeave assigned its Polaris Forge 1 lease obligations to `CoreWeave SPV VIII`, releasing parent corporate liability on Building ELN-03. However, CoreWeave concurrently executed an **Unconditional Springing Guaranty of Payment and Performance**.
- **Decision:** Model the lease (`OBL-CRWV-APLD-LEASE`) and the parent guarantee (`OBL-CRWV-APLD-GUARANTY`) as coexisting edges in the MultiDiGraph.
- **Consequences:** Accurately captures the legal perimeter: bankruptcy-remoteness protects the parent under normal operations, but default activates a contingent liquidity cliff that springs directly back onto the parent balance sheet.

---

### ADR-006: Verifiable Evidence Contract & Multi-Claim Audit Linking
- **Status:** Accepted (2026-09-28, Phase 0.5)
- **Context:** Disclosures must carry exact verbatim quotes from SEC EDGAR filings with immutable accession numbers, prohibiting paraphrased or synthesized quotes.
- **Decision:** Support many-to-many linking between obligations and claims. Enforce verbatim quote audits via `src/validate.py`.
- **Consequences:** Guarantees 100% epistemic auditability and zero narrative drift.
