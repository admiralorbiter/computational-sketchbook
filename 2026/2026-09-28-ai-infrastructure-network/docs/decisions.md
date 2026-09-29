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
- **Status:** Accepted (2026-09-28, Updated Phase 0.6)
- **Context:** Initial XBRL extraction picked single unaggregated concepts (e.g. DebtCurrent instead of total debt) and mixed instant balance sheet facts with non-comparable duration flows. Furthermore, early-break logic dropped 10-Q quarterly flows when 10-K reported annual totals under different concepts (e.g. APLD Q3 $126.6M vs FY26 $611.3M).
- **Decision:** Explicitly separate instant balance sheet facts from duration flow facts (3-month quarterly vs 12-month annual). Ingest across all concepts with priority deduplication. Synthesize derived Q4 flows (FY - 9M) where 10-K only reports annual numbers (e.g. MSFT Q4 $90.01B, APLD Q4 $258.75M). Aggregate funded debt components (`LongTermDebtNoncurrent` + `DebtCurrent` + `ConvertibleNotes` or `DebtInstrumentCarryingAmount`).
- **Consequences:** Restores true balance sheet totals across all nodes: APLD ($4.98B debt), CRWV ($35.55B debt principal), SMCI ($8.72B total debt), ORCL ($125.34B debt), and NVDA ($33.37B debt), and guarantees complete quarterly and annual flow coverage.

---

### ADR-003: MultiDiGraph Adoption and Elimination of False Netting
- **Status:** Accepted (2026-09-28, Phase 0.5)
- **Context:** Initial graph modeling used `nx.DiGraph`, overwriting multiple distinct agreements between identical counterparty pairs. Furthermore, the repository computed `outgoing - incoming = net contractual exposure`, netting a 15-year lease against a 2-year purchase commitment or equity stake.
- **Decision:** Migrate to `nx.MultiDiGraph(edge_key=obligation_id)`. Delete the `net_contractual_exposure_usd` metric. Categorize exposure strictly by `amount_type` (`principal_outstanding`, `lifetime_contract_value`, `remaining_commitment`, `recognized_revenue`, `contingent_guarantee`, `equity_investment`, `facility_capacity`).
- **Consequences:** Preserves distinct facilities (DDTLs, notes, convertibles, leases, springing guarantees) and eliminates non-fungible netting distortions.

---

### ADR-004: Explicit Separation of Reachability Footprints vs Financial Stress
- **Status:** Accepted (2026-09-28, Phase 0.5)
- **Context:** The initial stress engine marked 100% of face value as impaired for all edges within two hops of an assumption. While valuable as a topological exposure metric, calling this "financial stress loss" was misleading.
- **Decision:** Bifurcate into two distinct tools:
  1. `src/reachability.py` (`ContractualReachability`): Evaluates topological reachability and assumption dependency footprints (% of network face value within 1-2 hops).
  2. `src/stress.py` (`FinancialStressEngine`): Implements quantitative mathematical transmission functions:
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

---

### ADR-007: Contract-Calibrated Transmission Functions, Springing Guaranty Predicates, and Pure Amount-Type Reachability
- **Status:** Accepted (2026-09-28, Phase 0.6)
- **Context:** 
  1. The reachability engine previously summed non-fungible dollars ($34.2B purchase commitments + $11.0B lease + $35.5B debt principal) into an unweighted single dollar pool, producing distorted ratios.
  2. The Microsoft edge was characterized as an annualized $1.725B 5-year take-or-pay contract, whereas SEC filings report customer concentration (67% of FY25 revenue = $3.438B recognized revenue).
  3. The stress engine claimed to be a "true quantitative financial stress engine" when several transmission functions were stylized rather than contract-calibrated (rate shocks applied to fixed-rate notes; Polaris Forge 1 treated as unenergized rather than 100 MW operational + 300 MW expansion; Supermicro purchase commitments treated as 100% cash write-offs rather than US-GAAP NRV write-downs; springing guaranty modeled on an arbitrary coverage threshold rather than the legal predicate of an SPV colocation lease shortfall).
- **Decision:**
  1. Reframe stress engine claim from "true quantitative financial stress engine" to **"parameterized financial stress prototype"**.
  2. Eliminate cross-category dollar mixing in `src/reachability.py`; report reachability strictly by `amount_type` (`principal_outstanding`, `remaining_commitment`, `lifetime_contract_value`, `recognized_revenue`, `contingent_guarantee`) plus edge count %.
  3. Re-characterize Microsoft relationship to `REL-MSFT-CRWV-REVENUE-CONCENTRATION` ($3.438B recognized revenue, 67% concentration) under `amount_type = "recognized_revenue"`.
  4. Decompose CoreWeave debt into individual facilities (DDTL 1.0, 2.0, 2.1, 3.0, 4.0, 5.0, Senior Notes, Convertibles, OEM Financing, Magnetar Loan) and segment Applied Digital debt into fixed-rate notes ($2.35B 9.25% notes, $2.15B 6.75% notes) and corporate credit facilities ($476M).
  5. Ground economic transmission functions in contractual realities:
     - DDTL haircut: Evaluated against DDTL 5.0 71.42% advance rate formula and labeled *Modeled Borrowing Base Contraction*.
     - Springing Guaranty: Modeled on the literal legal predicate of an SPV colocation lease shortfall.
     - Refinancing Shock: Applied strictly to floating debt ($10.8B CRWV DDTLs, $476M APLD corporate debt); fixed debt suffers zero immediate cash interest impact but faces maturity rollover risk.
     - Grid Delay: Accounts for phased reality of Polaris Forge 1 (~100 MW operational generating $183.3M/yr base rent ongoing; ~300 MW unenergized expansion deferred, with carrying cost on construction debt).
     - OEM Purchase Commitments: Modeled via US-GAAP NRV expected-loss write-down provision (40% loss severity on 15% excess allocation = $2.05B pre-tax charge vs SMCI cash/equity).
- **Consequences:** Elevates the mathematical and legal fidelity of the research observatory to institutional standards, ensuring full contractual calibration and zero data drift.
