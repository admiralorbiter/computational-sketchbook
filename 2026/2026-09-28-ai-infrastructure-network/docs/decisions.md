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

---

### ADR-008: Exact Debt Reconciliation, Rate Shock Splitting, Springing Events Predicate Engine, and Multi-Channel Commitments
- **Status:** Accepted (2026-09-28, Phase 0.7)
- **Context:** Following external code review of Phase 0.6 (commit `845f8c1`), several areas required elevated contractual and numerical precision:
  1. *CoreWeave Debt Reconciliation:* Note 7 Table 36 reports $35,551M in total future principal across 11 tranches. The pilot previously accounted for $31.832B across 9 tranches, omitting DDTL 4.0 ($2.837B drawn out of $8.500B capacity) and Non-Recourse OEM financing ($882M).
  2. *Polaris Forge 1 Building-Level Phasing:* APLD Form 10-K Item 1 details 3 distinct buildings: Building 2 (100 MW operational), Building 3 (150 MW: ~50 MW operational, ~100 MW pending), and Building 4 (150 MW under construction). This totals ~150 MW operational producing $275.0M/yr base rent ongoing, and ~250 MW pending expansion deferring $458.3M/yr.
  3. *Rate Transmission Bifurcation:* A single generic rate shock improperly blended floating benchmark increases with credit spread blowout. Furthermore, CoreWeave's Credit Agreement (DDTL 5.0 Section 5.14) covenants that CoreWeave maintain interest rate hedges on $\ge 95\%$ of floating debt, insulating near-term recourse cash from SOFR spikes. Conversely, credit spread widening has zero immediate effect on fixed coupons or active credit margins, but hits maturing debt upon refinancing.
  4. *Springing Guaranty Legal Predicates:* The springing guaranty does not trigger on an arbitrary synthetic coverage threshold, but rather on discrete contractual conditions defined in Exhibit 10.1: (i) SPV bankruptcy, (ii) material adverse amendment, default, or termination of the Colocation Agreement, or circumstances permitting the customer to cease or materially reduce monthly payments, (iii) separateness covenant breach, or (iv) debt acceleration.
  5. *Dual-Channel Transmission on Purchase Commitments:* Supermicro's $34.2B purchase commitments propagate across two distinct channels: an ASC 330 non-cash NRV loss provision reducing equity versus a negotiated cash settlement or inventory delivery liquidity drain.
  6. *Clarification of GPU Advance Rate / MTM:* DDTL 5.0 Exhibit 10.1 defines the borrowing base advance rate as 71.42% of Funding Date Capex (cost) with 6-year straight-line depreciation, rather than an automated secondary market mark-to-market appraisal cure covenant. A -40% secondary GPU price shock is a Class C analytical stress proxy, not a contractually automated margin call.
- **Decision:**
  1. Decompose CoreWeave indebtedness across all 11 tranches from Form 10-Q Note 7 Table 36, adding non-recourse DDTL 4.0 ($2.837B drawn) and non-recourse OEM financing ($0.882B) to achieve exact reconciliation to $35.551B (0.00% drift).
  2. Implement Building 2, 3, and 4 operational phasing at Polaris Forge 1 (150 MW operational, 250 MW pending).
  3. Split rate transmission into two distinct scenarios:
     - **Scenario 3A (SOFR Benchmark Shock):** Accounts for the 95% swap hedging covenant, limiting recourse floating cash hit to $16.2M/yr ($72.5M/yr total hedged drain including DDTL 4.0 and APLD floating).
     - **Scenario 3B (Credit Spread Rollover Shock at Maturity):** Affects refinancing of maturing debt ($4.41B in 2026, $6.18B in 2027), adding $317.9M/yr in refinancing interest by 2027 ($450.4M/yr through 2028).
  4. Implement an explicit Springing Events predicate engine in `src/stress.py` mapping Exhibit 10.1 triggers and formulating the conditional join: *if* Microsoft is the Building ELN-03 tenant and trims payments, Event (ii) springs the $11.0B parent guarantee.
  5. Split Supermicro purchase commitment stress into dual channels: a non-cash US-GAAP ASC 330 NRV write-down provision ($2.05B pre-tax charge reducing equity) vs a negotiated cash settlement ($769.5M cash, 10.2%) or inventory delivery ($5.13B cash, 68.2%).
  6. Explicitly tag the GPU MTM collateral shock as a *Hypothetical MTM Financing Sensitivity (71.42% Funding-Ratio Proxy)* (Class C analytical sensitivity).
  7. In `sec_ingest.py`, enforce strict same-concept-family and identical `start_date` matching for derived Q4 flow calculations, and present both Full Year (FY) and Latest Quarter revenue columns in documentation to prevent time-horizon ambiguity.
- **Consequences:** Eliminates all contractual over-claiming, reconciles debt to the penny ($35.551B), isolates accounting equity write-downs from cash drains, and establishes an institutional-grade foundation for the five-company pilot.

---

### ADR-009: Hedge Scope Calibration, Split Springing Guarantees ($6.88B / 250 MW), Operational MW Parameterization, and Config-Driven Ingestion Overrides
- **Status:** Accepted (2026-09-28, Phase 0.7.1)
- **Context:** Following external review of Phase 0.7 (commit `3a4a0902`), seven narrower evidentiary and contract-boundary findings required calibration before expanding beyond the 5-company universe:
  1. *Hedge Scope Calibration:* Phase 0.7 applied a 95% swap hedging ratio across all $10.8B of floating DDTLs, yielding a minimal $72.5M/yr rate shock. However, Credit Agreement Section 5.14 only mandates $\ge 95\%$ hedges specifically for DDTL 4.0 and DDTL 5.0. Form 10-Q Note 8 reports an empirical total of $4,661M in active interest-rate swaps against $12.206B in total floating borrowings. Unhedged floating debt is $7.545B, producing an empirical cash drain of $226.4M/yr (CRWV) + $14.3M/yr (APLD) = $240.6M/yr at +300 bps.
  2. *Split Springing Guarantee Scope:* Phase 0.7 assigned an $11.0B springing guarantee across the entire 400 MW Polaris Forge 1 campus. Underlying filings establish two separate guarantees: Exhibit 10.1 (ELN-02, Building 2, 100 MW, $2.750B contracted value) and Exhibit 10.2 (ELN-03, Building 3, 150 MW, $4.125B contracted value), totaling $6.875B across 250 MW. Building 4 (150 MW, $4.125B) carries no CoreWeave parent springing guarantee (APLD guarantees the landlord).
  3. *Verbatim Quoting of Springing Events:* `CLM-APLD-005` in evidence claims misstated the legal events. Exhibit 10.1 establishes nine discrete event groups, including an equipment-financing rating trigger [***], colocation agreement default/modification/reduction, and equipment financing acceleration.
  4. *Class C Operational MW Parameterization:* APLD Form 10-K notes Building 3 is partially operational but does not state 50 MW is live. The 50 MW live figure is an inferred Class C analytical proxy.
  5. *Refinancing Principal vs Amortization:* CoreWeave's $10.60B maturing across 2026–2027 represents scheduled contractual principal payments; refinancing rollovers should be explicitly parameterized.
  6. *Terminology & Ingest Scaling:* Replace "11 distinct debt tranches" with "11 modeled debt components/edges", parameterize Supermicro's cancellation fee rate, and replace hardcoded ticker overrides in `sec_ingest.py` with a config-driven `FINANCIAL_METRIC_OVERRIDES` mapping.
- **Decision:**
  1. In `src/stress.py`, calibrate the SOFR rate shock to report the empirical swaps baseline ($240.6M/yr) and expose a sensitivity band ($32.6M to $309.2M/yr).
  2. In `config/entities.yml` and `src/curate_obligations.py`, split landlord SPVs into `APLD_ELN02_LLC`, `APLD_ELN03_LLC`, and `APLD_ELN02C_LLC`, and split springing guarantees into `OBL-CRWV-APLD-GUARANTY-ELN02` ($2.750B) and `OBL-CRWV-APLD-GUARANTY-ELN03` ($4.125B), totaling $6.875B covering 250 MW.
  3. Update `CLM-APLD-005` to quote verbatim text covering the 9 Springing Events from Exhibit 10.1, add `CLM-APLD-006` for Exhibit 10.2, and calibrate `CLM-CRWV-005` to quote Note 7 and Note 8 swap text verbatim.
  4. Parameterize `building3_operational_mw` (default 50.0 MW, Class C proxy) with an exposed sensitivity band (25–100 MW live), `refi_rollover_fraction` (default 1.0, range 0.5–1.0), and `cancellation_fee_rate` (default 0.15).
  5. Migrate `sec_ingest.py` to a config-driven `FINANCIAL_METRIC_OVERRIDES` mapping for debt reconciliation.
  6. Update `src/validate.py` to enforce zero data drift, assert 20 obligations, verify split springing guarantees, perform verbatim claim substring checks, and output `ALL INTERNAL CONSISTENCY CHECKS PASSED: ZERO DATA DRIFT`.
- **Consequences:** Eliminates all remaining contractual over-claims and parameter mischaracterizations, grounds rate shocks in empirical SEC swap disclosures, and establishes full evidentiary precision before universe expansion.

## ADR-010: Phase 0.7.2 Corrective Patch & Pilot Freeze
- **Status:** Accepted (Phase 0.7.2 Pilot Freeze)
- **Context:**
  Following Phase 0.7.1, a final pre-expansion pressure test identified two material economic misclassifications and two epistemic precision issues:
  1. *Springing Guarantee Amounts & Scope:* Legal guarantee contracts (Exhibit 10.1 & 10.2) are uncapped performance and rent indemnities without fixed dollar amounts. Stating fixed amounts ($2.75B and $4.125B) conflated legal indemnity with nominal lease value. Furthermore, Exhibit 10.1 specifically covers "Phase 2/4 Space (2 of 4 data halls in Building 2)", not the entire 100 MW. Exhibit 10.2 covers Building 3 (150 MW assigned to SPV), carrying a Class C reference exposure proxy of $4.125B ($150/400 \text{ MW} \times \$11.0\text{B}$).
  2. *Applied Digital Debt Duality & Floating Exposure:* Form 10-K balance sheet reports net carrying debt of $4.976B ($4,959.5M net long-term + $16.4M current debt), while Note 8 reports gross contractual principal payments of $5.307B ($5,306.7M), with $330.7M in unamortized discount and debt issuance costs. The debt was artificially lumped into a $475.9M corporate residual rather than reflecting actual contractual instruments: $2.35B PF1 notes (fixed), $2.15B PF2 notes (fixed), $450M convertible notes (fixed), $300M floating bridge facility (SOFR), and $56.68M other debt. Only the $300M bridge facility was floating (adding $9.0M/yr interest shock at +300 bps), establishing a network SOFR baseline of $235.4M/yr ($226.4M CRWV + $9.0M APLD). Note: APLD refinanced the bridge facility on June 16, 2026 into 7.00% fixed notes.
  3. *Verbatim Quoting Fidelity & Exhibit Caching:* The springing event quote in `CLM-APLD-005` contained bracketed omissions. We cached primary SEC exhibit HTML files (`APLD_ex10_1.htm` and `APLD_ex10_2.htm`) and enforced 100% exact contiguous verbatim substring verification in the automated validator.
  4. *GPU MTM Reframing:* Under DDTL 5.0 Section 2.05, secondary price declines do not trigger automatic cash prepayment margin calls. The $4.32B impact was reframed as a Modeled Refinancing-Capacity Gap (Class C proxy) eliminating undrawn availability, while CoreWeave cash remains $5.52B intact.
  5. *Validator Latest-Period Check:* Replaced `.max()` with `.sort_values("period_end").iloc[-1]["value"]` to validate latest reported period rather than historical maximums (fixing Oracle $134.60B -> $125.34B and SMCI $8.77B -> $8.72B).
- **Decision:**
  1. Updated `FINANCIAL_METRIC_OVERRIDES` in `src/sec_ingest.py` to record APLD contractual principal ($5.306680B).
  2. In `src/curate_obligations.py`, expanded obligations to 22: set springing guarantees to `amount = None`, `amount_type = "contingent_obligations"`, ELN-02 scope to "Phase 2/4 Space (2 of 4 data halls in Building 2)", ELN-03 to $4.125B Class C reference proxy, and decomposed APLD debt into 5 real contractual instruments summing to $5,306.68M (0.00% drift).
  3. In `src/stress.py`, updated Scenario 1 to modeled refinancing gap ($4.32B Class C proxy, cash intact), Scenario 2 to uncapped springing guaranty activation, and Scenario 3A to $235.4M/yr baseline cash drain ($226.4M CRWV + $9.0M APLD; sensitivity band $27.3M to $303.9M/yr).
  4. In `src/validate.py`, added APLD debt decomposition assertion, uncapped springing guaranty assertion, exact contiguous verbatim substring check against `data/raw/sec/APLD_ex10_1.htm`, latest-period debt verification, and updated documentation checks.
  5. Rebuilt and executed `notebooks/01_five_company_pilot.ipynb` (13/13 cells executed cleanly).
  6. Froze the 5-company pilot in Phase 0.7.2.
- **Consequences:**
  Eliminates all narrative drift and contractual over-claims. The 5-company pilot is now epistemically certified with zero data drift, providing an unshakeable foundation for Phase 1 universe expansion.

---

### ADR-011: Pre-Phase-1 Engineering Hardening & Epistemic Contract Certification
- **Status:** Accepted (2026-09-28, Pre-Phase-1 Hardening)
- **Context:**
  Following review of commit `e9b3169` (Phase 0.7.2), five engineering and data-contract hardening items were identified as prerequisites before expanding the universe to 25 companies:
  1. *APLD Contract-Literal Debt Tranches:* OBL-APLD-DEBT-PF1 was listed under borrower `APLD_ELN_LLC` maturing 2029-06-30. Form 10-K Note 8 reveals the $2.35B 9.25% notes were issued by `APLD_COMPUTECO` (after a corporate reorganization placing ELN-02 and ELN-03 underneath it) maturing December 15, 2030. `OBL-APLD-DEBT-PF2` ($2.15B 6.75% notes) was issued by `APLD_COMPUTECO2` maturing March 15, 2031. `OBL-APLD-DEBT-OTHER` ($56.68M) required explicit typing as `aggregate_residual_debt`.
  2. *Dynamic SPV Unwrapping:* Graph perimeter consolidation previously relied on static, hardcoded dictionary mappings (`{"CRWV_SPV_VIII": "CRWV", ...}`). For a 25-company universe, hardcoded maps create structural brittleness and drift risk.
  3. *Uncapped Obligations & NaN Safety:* Legal indemnities without fixed principal (e.g. springing guarantees) carry `amount = None`, `amount_known = False`, and `amount_type = "contingent_obligations"`. Mathematical aggregations and graph plotting routines require first-class null-safety to prevent `np.nan` contamination.
  4. *Temporal Modeling & Facility Supersession:* Debt and contract structures change across reporting dates. APLD entered into a $300M bridge facility on May 1, 2026 (active at the May 31, 2026 balance sheet date), and subsequently refinanced it on June 16, 2026 via $1.59B 7.00% senior notes. To prevent temporal distortions, obligations require explicit temporal attributes (`observed_as_of`, `valid_from`, `valid_to`, `superseded_by`), and the graph must support point-in-time queries via `network.as_of(date_str)`.
  5. *Quote Categorization & Exact Substring Verification:* Evidence claims blend verbatim quotes, truncated excerpts, and analytical summaries. Explicit categorization (`quote_type = "exact_quote" | "source_excerpt" | "analyst_summary"`) enables the test harness to enforce 100% exact contiguous verbatim substring verification against cached raw SEC exhibits (`APLD_ex10_1.htm` and `APLD_ex10_2.htm`).
- **Decision:**
  1. Update `config/entities.yml` with parent entity relationships across corporate hierarchies (`parent_entity_id: CRWV` for `CRWV_SPV_VIII`; `parent_entity_id: APLD_COMPUTECO` for `APLD_ELN02_LLC` and `APLD_ELN03_LLC`; `parent_entity_id: APLD` for `APLD_COMPUTECO`, `APLD_COMPUTECO2`, and `APLD_ELN02C_LLC`).
  2. Implement dynamic recursive parent traversal `get_root_parent(entity_id)` in `src/graph.py` and `unwrap_spv_perimeter()`, leaving 0 SPV nodes in the consolidated graph.
  3. Implement `as_of(date_str)` temporal filtering in `src/graph.py` and parameterize `simulate_sofr_base_rate_shock(as_of_date=...)` in `src/stress.py`, reporting both the May 31 snapshot ($235.4M/yr) and post-refinancing ($226.4M/yr) metrics.
  4. Enforce contract-literal legal entities, maturities, effective dates, and debt types for all 5 APLD debt tranches in `src/curate_obligations.py` and `src/validate.py`.
  5. Categorize claims with `quote_type` in `src/curate_obligations.py` and add 100% exact contiguous verbatim substring validation for `APLD_ex10_2.htm` Section 1 in `src/validate.py`.
  6. Harden all aggregation, reachability, and plotting routines against `amount = None` in `src/graph.py`, `src/reachability.py`, and `src/build_notebook.py`.
- **Consequences:**
  Eliminates structural fragility, guarantees 100% data contract certification, cleanly separates point-in-time historical reporting from forward refinancing events, and ensures the codebase is fully prepared for multi-company universe expansion in Phase 1.

---

### ADR-012: Bitemporal Graph Architecture, Information Clock vs Economic Clock, and Debt Conservation Supersession
- **Status:** Accepted (2026-09-28, Phase 0 Freeze & Pre-Phase-1 Hardening)
- **Context:**
  Following review of commit `107c05c`, four temporal and architectural requirements were identified before scaling to Phase 1:
  1. *Obligation Conservation through Transformations:* While `OBL-APLD-DEBT-BRIDGE` was marked as extinguished on June 16, 2026, the successor financing agreement ($1.59B 7.00% Senior Secured Notes due 2031) was not instantiated as an active edge. Consequently, `network.as_of("2026-09-28")` caused debt to simply vanish rather than modeling its transformation from floating bridge to fixed long-term notes.
  2. *Information Time vs Economic Time (Look-Ahead Bias):* A single `as_of(date)` filtering on `valid_from` and `valid_to` models economic reality, but introduces look-ahead bias when evaluating what public market participants could have known at a given historical point in time. For instance, querying `as_of("2026-06-30")` would include 10-K disclosures published in late July or August 2026. Evaluating systemic risk and answering "Could an observer have detected the bubble at the time?" requires an explicit information clock.
  3. *Stress Engine Temporal Coupling:* The stress engine previously hardcoded date conditionals (`apld_floating_debt = 300M if date < June 16 else 0`) rather than deriving active floating exposures dynamically from the active graph topology.
  4. *Reachability Contingent Obligation Metric:* Reachability previously attempted to compute a dollar percentage for contingent obligations (which have no dollar denominator), rather than reporting edge reachability counts and percentages.
- **Decision:**
  1. Formally add `OBL-APLD-DEBT-7PCT-2026` ($1.59B principal, fixed 7.00%, due 2031-06-15, `supersedes = "OBL-APLD-DEBT-BRIDGE"`) and link `OBL-APLD-DEBT-BRIDGE` (`superseded_by = "OBL-APLD-DEBT-7PCT-2026"`), conserving obligations across transformations (22 active edges at May 31 $\to$ 22 active edges at Sep 28).
  2. Implement bitemporal graph query semantics with two distinct clocks in `src/graph.py`:
     - **Economic Clock (`network.economic_as_of(date)`):** Filters on `economic_valid_from <= date` and `(economic_valid_to is None or economic_valid_to >= date)`, reconstructing historical physical reality.
     - **Information Clock (`network.known_as_of(date)`):** Filters on `publicly_known_from <= date` AND economic validity, reconstructing strictly what an outside observer could have known without look-ahead bias.
     - `network.as_of(date, mode="economic"|"known")` acts as the unified dispatcher.
  3. Couple `FinancialStressEngine` dynamically to the network by implementing `get_active_floating_debt(entity_id)` which inspects active graph edges for `rate_type == "floating"` or `benchmark_rate == "SOFR"`, completely removing hardcoded date conditionals inside stress functions.
  4. In `src/reachability.py`, report contingent obligations by edge count and edge reachability percentage, and remove the obsolete `outgoing_contingent_guarantees_usd` dictionary key in `src/graph.py`.
  5. Add `CLM-APLD-007` citing Form 10-K Note 19 Subsequent Events.
- **Consequences:**
  Eliminates look-ahead bias, establishes institutional-grade bitemporal graph querying, ensures conservation of obligations across debt rollovers, and decouples the stress simulation engine from hardcoded calendar dates.

---

### ADR-013: Fact-Level Bitemporality (`obligation_facts`), Half-Open Validity Intervals, ComputeCo 3 Hierarchy, and Epistemic Stress Decoupling
- **Status:** Accepted (2026-09-28, Phase 0 Epistemic Hardening & Certification)
- **Context:**
  Following review of commit `fdfafb5`, four temporal, epistemic, and entity-modeling issues were identified to achieve true look-ahead-free backtesting certification:
  1. *Fact-Level Bitemporality (`obligation_facts`):* While `known_as_of()` filtered entire obligations on `publicly_known_from`, an obligation's contract existence can be known long before its periodic measured attributes are known. For example, CoreWeave's DDTL 1.0 facility economically existed from 2023 and was publicly disclosed in 2024, but its June 30, 2026 principal balance ($1.300B) was not disclosed until August 12, 2026 (Form 10-Q Note 7). Under `known_as_of("2026-06-30")`, the edge must exist in the topology, but its balance must resolve to `None` (`amount_known = False`), avoiding edge-value look-ahead leakage.
  2. *Half-Open Validity Intervals $[v\_from, v\_to)$:* Using closed intervals $[v\_from, v\_to]$ caused a double-counting boundary clash on June 16, 2026, where both the $300M bridge and the $1.59B 7% notes were active simultaneously (23 edges). Implementing half-open intervals $[v\_from, v\_to)$ (excluding when `date >= valid_to`) cleanly retires the bridge at the start of June 16, conserving exactly 22 edges.
  3. *Contract-Literal Issuer & Hierarchy for $1.59B Notes:* Form 8-K (filed 2026-06-18) establishes that the $1.59B 7.00% Senior Secured Notes were issued by `APLD ComputeCo 3 LLC` (`APLD_COMPUTECO3`), a direct subsidiary of `APLD HPC Holdings 2 LLC` (`APLD_HPC_HOLDINGS2`), whose parent is `Applied Digital Corporation` (`APLD`), with recourse classified as `senior_secured_spv`.
  4. *Epistemic Decoupling of Stress Engine:* In `simulate_sofr_base_rate_shock()`, swap notional and floating exposures must be dynamically derived from the active graph/fact ledger. When evaluated under `known_as_of("2026-06-30")` (before the August 12 swap disclosure), `swap_notional_known` is flagged `False`, `swap_notional_reported_usd` is `None`, and the engine reports an explicit epistemic uncertainty band ($18.3M fully hedged to $366.2M unhedged) rather than leaking post-period disclosures.
- **Decision:**
  1. Create `obligation_facts.parquet` and `.csv` (27 rows) decoupling invariant contract definitions from time-varying point-in-time measurements (`principal_outstanding`, `swap_notional`, `facility_capacity`, `capacity_mw`, `reference_exposure_estimate`).
  2. Implement fact-level bitemporal attribute resolution in `ObligationNetwork.economic_as_of()` and `ObligationNetwork.known_as_of()`, attaching `amount = None` and `amount_known = False` if the measured fact has not yet been publicly disclosed as of `publicly_known_from`.
  3. Implement half-open validity intervals $[v\_from, v\_to)$ (`date < valid_to`).
  4. Add `APLD_HPC_HOLDINGS2` and `APLD_COMPUTECO3` to `config/entities.yml` (total 20 entities) and implement `get_parent(entity_id)` and recursive `get_root_parent(entity_id)` multi-tier unwrapping in `src/graph.py`.
  5. Add claim `CLM-APLD-008` citing the June 18, 2026 Form 8-K (total 17 claims).
  6. Dynamically couple `FinancialStressEngine` to the fact ledger for swap notional and floating debt, surfacing epistemic uncertainty ranges under knowledge-mode evaluation.
- **Consequences:**
  Guarantees 100% look-ahead-free backtesting capability, exact obligation conservation across debt rollovers, contract-literal SPV perimeter consolidation, and complete epistemic transparency across historical and public knowledge timelines.

---

### ADR-014: Obligation Lifecycle Events Ledger, Dual Truth vs. Knowledge Claims, Zero-Lookahead Stress Engine, and Audited Quote Taxonomy
- **Status:** Accepted (2026-09-29, Phase 0 Epistemic Certification)
- **Context:**
  Following review of commit `3a6421b`, five critical temporal, epistemic, and evidence integrity requirements were identified to achieve complete epistemic observatory certification:
  1. *Edge Lifecycle Extinction Void (June 16–18 Boundary):* In `known_as_of()`, applying `economic_valid_to` directly caused an outside observer on June 17 to mysteriously know that the $300M bridge had been extinguished on June 16, even though the refinancing Form 8-K was not filed until June 18. This created an unphysical 24-hour void where the bridge vanished from knowledge before the market knew about it, while the 7% notes were not yet known.
  2. *Future-Known Fallback Leakage in Stress Simulation:* When simulating SOFR shocks on June 30 under knowledge mode, the engine used `if crwv_floating_debt == 0.0: crwv_floating_debt = 12206000000.0`. This fallback leaked the August 12 10-Q total into the June 30 epistemic range, calculating an artificial $18.3M - $366.2M cash drain. When floating debt amounts are unmeasured and unknown, zero-lookahead requires reporting `floating_principal_known = False`, `unknown_floating_edges`, `crwv_reported_floating_usd = None`, `max_cash_drain_usd = None`, and `network_cash_drain_reported_baseline_usd = None`.
  3. *Historical Fact Isolation (No Back-Projection):* In `economic_as_of()` and `known_as_of()`, querying dates prior to any fact observation (e.g. `2025-01-01`) previously retained current amounts from base edges. Mutable fact fields (`amount`, `amount_known`, `floating_principal`, `facility_capacity`, `capacity_mw`, `reference_exposure_estimate`) must be explicitly reset to `None` / `False` prior to applying matching point-in-time facts.
  4. *Evidence Claim Duality (Truth vs Knowledge Claims):* Every mutable fact in `obligation_facts.parquet` requires dual claim tracking:
     - `truth_claim_id`: Audited document certifying factual accuracy (e.g. Form 10-K / 10-Q Note 7).
     - `knowledge_claim_id`: Contemporaneous filing establishing earliest public awareness (e.g. Form 8-K on transaction date).
     - Strict temporal invariant: `fact.publicly_known_from >= claims[fact.knowledge_claim_id].filing_date`.
     - 13 contemporaneous claims added (`CLM-APLD-009` through `013`, `CLM-CRWV-007` through `014`), bringing audited evidence claims from 17 to 30.
  5. *Quote Categorization Nuance:* Distinguish between exact character-level substring certification (for cached primary exhibits `APLD_ex10_1.htm` and `APLD_ex10_2.htm`) vs audited SEC source excerpts from full EDGAR filings.
- **Decision:**
  1. Create `obligation_events.parquet` (24 rows: 23 `created` + 1 `superseded`) tracking discrete lifecycle state changes with independent `economic_effective_at` and `publicly_known_at` dates. On June 17, an outside observer in knowledge mode observes the $300M bridge active, with 7% notes absent (18 edges). On June 18 (filing date), the bridge is retired and 7% notes appear.
  2. In `src/graph.py`, filter edge active lifecycle strictly through `obligation_events` and reset mutable fields before overlaying point-in-time facts.
  3. In `src/stress.py`, eliminate the $12.206B fallback in known mode. When floating debt is unknown, output `floating_principal_known = False`, `max_cash_drain_usd = None`, `crwv_reported_floating_usd = None`, and list `unknown_floating_edges`.
  4. Extend `obligation_facts.parquet` with `truth_claim_id` and `knowledge_claim_id` and assert `publicly_known_from >= claims[knowledge_claim_id].filing_date`.
  5. Enforce all constraints in `src/validate.py`.
- **Consequences:**
  Achieves 100% certified zero-lookahead backtesting invariance, complete lifecycle edge auditability, and mathematically unassailable epistemic integrity across all historical and public knowledge queries.

---

### ADR-015: Historical Debt Evidence Calibration, Discrete Instrument De-aggregation, Borrower SPV Perimeter, and Bitemporal Financial Snapshot Resolution
- **Status:** Accepted (2026-09-29, Phase 0 Epistemic Certification)
- **Context:**
  Following review of commit `1d99702`, while the bitemporal graph architecture (ADR-013 & ADR-014) operated cleanly, an audit of the underlying evidence claims revealed critical historical, structural, and financial statement integrity defects:
  1. *Fabricated CoreWeave Contemporaneous SEC Filings:* `CLM-CRWV-007` through `CLM-CRWV-014` cited fictitious 2024 Form 10-K and Form 10-Q accession numbers (`0001769628-24-000012`, etc.) prior to CoreWeave becoming an SEC reporting company. CoreWeave filed its initial Form S-1 on March 3, 2025 (`0001193125-25-045330`) and Form S-1/A on March 20, 2025 (`0001193125-25-058309`). All historical credit facilities entered in 2023 and 2024 (DDTL 1.0, DDTL 2.0, Magnetar Credit Agreement) were disclosed through credit agreement exhibits and Note 7 of the S-1/A. Subsequent Senior Notes and Convertibles were announced via genuine Form 8-K submissions throughout 2025 and 2026.
  2. *Applied Digital $1.59B 7.00% Notes Closing Date:* Form 8-K announcing the closing of the $1.59B notes and retirement of the bridge facility was filed on **June 16, 2026** (`0001493152-26-028899`, `CLM-APLD-008`), not June 18.
  3. *Debt Aggregation and Structural Opacity:* CoreWeave's $35.551B debt portfolio was over-aggregated into coarse umbrella facilities rather than contract-literal instruments with distinct borrower SPVs, facility capacities, and recourse provisions:
     - DDTL 1.0: Originated 2023-07-30 via `CoreWeave CCAC II LLC` (`CRWV_CCAC_II`).
     - DDTL 2.0 & 2.1: Originated 2024-05-16 and 2025-09-25 via `CoreWeave CCAC IV LLC` (`CRWV_CCAC_IV`).
     - DDTL 3.0: Originated 2025-07-28 via `CoreWeave CCAC VII LLC` (`CRWV_CCAC_VII`).
     - DDTL 4.0: Originated 2026-03-30 via `CoreWeave SPV VIII LLC` (`CRWV_SPV_VIII`) from MUFG Bank syndicate; strictly non-recourse with zero parent guarantee.
     - DDTL 5.0: Originated 2026-05-15 via `CoreWeave Financing DDTL V LLC` (`CRWV_FINANCING_DDTL_V`) from Morgan Stanley syndicate.
     - Senior Notes (5 tranches) and Convertible Notes (2 tranches) issued directly by parent `CRWV`.
     - OEM Financing (2 tranches: recourse and non-recourse) and Magnetar Credit Agreement.
     - 5 explicit parent guarantee edges (`amount_type = "contingent_guarantee"`, `amount = None`) from parent `CRWV` to lender syndicates.
  4. *Facility Capacity vs Periodic Balance Conflation:* Initial commitment capacities were conflated with later periodic principal drawn amounts as of 2026-06-30.
  5. *Balance Sheet Look-Ahead Leakage:* `FinancialStressEngine` loaded fixed latest-period financial statements (e.g. Q2 2026 cash and debt) regardless of the simulation's `as_of_date` and `temporal_mode`.
- **Decision:**
  1. Purge all fabricated claims. Cache 100% authentic raw SEC EDGAR submissions JSON for all 6 entities in `data/raw/sec/` (over 5,000 verified filings).
  2. Implement `validate_sec_source_existence()` in `src/validate.py` verifying every accession number, filing form, and filing date against raw SEC records. Enforce `event.publicly_known_at >= claim.filing_date`.
  3. Add 6 new entities to `config/entities.yml` (total 26 entities): `CRWV_CCAC_II`, `CRWV_CCAC_IV`, `CRWV_CCAC_VII`, `CRWV_FINANCING_DDTL_V`, `MUFG_BANK_SYN`, `MORGAN_STANLEY_SYN`.
  4. Decompose CoreWeave funded debt into 16 discrete tranches totaling exactly $35,551,000,000.00 (0.00% drift). Model 5 recourse parent guarantee edges and confirm DDTL 4.0 is non-recourse.
  5. Expand ledger structures: 33 obligations, 34 lifecycle events, 42 bitemporal facts, 32 verified evidence claims.
  6. Implement `resolve_temporal_financials(as_of_date, temporal_mode)` in `src/stress.py` to pull point-in-time XBRL financials based strictly on `filed_date <= as_of_date` in knowledge mode, eliminating financial statement look-ahead bias.
- **Consequences:**
  Achieves Phase 0 Epistemic Certification with zero hallucinations, 100% verified primary SEC EDGAR citations, contract-literal discrete debt tranches with verified borrower SPVs and guarantee perimeters, and complete temporal consistency across both obligation graph and financial balance sheet dimensions.

---

### ADR-016: Phase 0 Epistemic Certification Freeze: Primary SEC Exhibit Substring Binding, Customary Bad-Acts Carve-Out Guaranty Edge, Joint Co-Borrower Entities, and Exact Contractual Maturity Semantics
- **Status:** Accepted (2026-09-29, Phase 0 Epistemic Certification)
- **Context:**
  Following review of commit `b1f9c77` and `0ef593b`, four final calibration issues were identified to achieve complete epistemic observatory certification and eliminate all remaining look-ahead leaks and semantic ambiguities:
  1. *SEC Exhibit Substring Binding:* `validate_sec_html_content()` in `src/validate.py` previously searched cached HTML files globally, creating a potential false-positive match path across unrelated documents. Every verifiable claim must be explicitly mapped to its specific cited file (`CLAIM_TO_SEC_FILE`), verifying that the normalized quote is 100% an exact contiguous verbatim substring strictly inside that specific document.
  2. *DDTL 4.0 Limited Parent Guarantee:* DDTL 4.0 was previously modeled as having zero parent guarantee. Form 8-K Exhibit 10.2 explicitly establishes that CoreWeave, Inc. executes a Limited Guarantee covering specified customary non-recourse carve-out obligations (bad acts, fraud, environmental indemnities). Modeled as `OBL-CRWV-GUARANTY-DDTL4` (`recourse = "limited_bad_acts"`, `amount = None`, `reference_exposure_estimate = 2837000000.0`, `reference_exposure_class = "Class C (Underlying Principal Reference)"`).
  3. *DDTL 3.0 Joint Co-Borrower Entity:* Form 8-K (July 28, 2025) establishes that both `CRWV CCAC VII LLC` and `CRWV CCAC V LLC` were co-borrowers under DDTL 3.0. Added entity `CRWV_CCAC_V` and edge `OBL-CRWV-COBORROWER-DDTL3` (`obligation_type = "joint_co_borrower"`, `amount = None`), capturing the true legal perimeter without duplicating the $2.215B debt edge.
  4. *Contractual Draw-Level Maturity Semantics for DDTL 2.0 & 2.1:* Replaced static 5-year facility dates with contractual draw-level maturity semantics (`maturity_rule = "funding_date + 5 years"`), reported facility balloons (August 2030 for DDTL 2.0, March 2031 for DDTL 2.1), and corrected DDTL 2.1 execution to September 29, 2025 (Fifth Amendment) and Form 8-K filing to October 2, 2025 (`CLM-CRWV-010`, accession `0001193125-25-227562`, `d910811d8k.htm`).
  5. *9.75% Notes Add-On Decomposition:* Split into initial April 14, 2026 issuance ($1.750B, `EVT-CRWV-DEBT-NOTES-2031-975-CREATED`) and April 21, 2026 add-on amendment ($1.000B, `EVT-CRWV-DEBT-NOTES-2031-975-ADDON`). Verified bitemporal queries resolve to $1.750B on April 15 and $2.750B on April 22 under `known_as_of()`.
  6. *Zero-Lookahead Stress Engine Hardening:* Eliminated metric and narrative leaks across `simulate_anchor_customer_trim()` (debt service derived dynamically; returns `None` in `known` mode on June 30), `simulate_grid_energization_delay()` (returns `None` prior to July 29, 2026 APLD Form 10-K), `simulate_oem_purchase_commitment_markdown()` (stripped `($34.2B)` narrative leak), and `simulate_gpu_collateral_haircut()` (dynamic contractual caveat).
  7. *SEC Note Citation Alignment:* Updated CoreWeave June 30, 2026 Form 10-Q note numbers in claims metadata from Note 7 to Note 10 (Debt) and Note 3 (Derivative Instruments).
- **Decision:**
  1. Bind all 29 primary SEC claims to their cited files in `validate_sec_html_content()`.
  2. Add `OBL-CRWV-GUARANTY-DDTL4` and `OBL-CRWV-COBORROWER-DDTL3` to `obligations.parquet` (35 rows).
  3. Expand `obligation_events.parquet` to 37 rows and `obligation_facts.parquet` to 45 rows.
  4. Fully freeze Phase 0 at commit `dc9ddc5` / `f4ff3bd` with zero data drift across all 27 entities, 35 obligations, 37 lifecycle events, 45 facts, and 37 claims.
- **Consequences:**
  Achieves mathematically certified, 100% verified Phase 0 baseline with zero hallucinations, complete bitemporal fidelity, and zero narrative or metric look-ahead leakage.

---

### ADR-017: Phase 1 Boundary-Crossing Architecture, Multi-Modal Ingestion Ontology, and Discovery-Driven Universe Expansion
- **Status:** Accepted (2026-09-29, Phase 1 Architecture)
- **Context:**
  Phase 0 validated the structural, bitemporal, and epistemic machinery across a 5-company pilot and its immediate counterparties. Moving to Phase 1 requires expanding the observatory across the broader AI compute supply chain. However, a naive expansion strategy suffers from four foundational architectural traps:
  1. *Pipeline Monolith Trap (Conflating Ingestion Modality with Universe Membership):* A preliminary 30-entity expansion proposal mixed domestic public filers, foreign private issuers, private companies, asset management parents, and grid operators into a single nominal list. The automated SEC XBRL pipeline (`sec_ingest.py`) cannot ingest foreign 20-F/6-K filers, cannot tolerate missing balance sheets for private companies, and fails to handle non-company infrastructure nodes.
  2. *Lender Identity Trap (Conflating Asset Manager Corporate Debt with Managed Fund Loans):* Entities such as `BLACKSTONE`, `BLUE_OWL`, `ARES`, `APOLLO`, `MUFG`, and `MORGAN_STANLEY` are critical capital providers. However, treating the asset manager parent's corporate 10-K balance sheet as the lender exposure is conceptually wrong: Apollo corporate debt is corporate debt, whereas Apollo-managed private credit funds or bank syndicates hold the loan asset. The borrower's credit agreement exhibits are the primary source for exposure mapping.
  3. *Infrastructure Taxonomy Trap (Treating Grid Operators as Corporates):* Regional transmission organizations (`PJM_INTERCONNECTION`, `ERCOT_GRID`) are non-profit grid operators governing interconnection queues and energization delays, not operating companies with balance sheets. Regulated electric utilities (`AEP`) are corporate utilities. Meanwhile, physical supply chain bottleneck vendors (`Vertiv`, `Eaton`, `GE Vernova`) represent physical transformer and gas turbine equipment constraints that force data center developers to turn to behind-the-meter generation.
  4. *Static Roster Trap (Framing Expansion as a Fixed Company List):* The core research objective of Phase 1 is **boundary-crossing edge expansion**, not accumulating 25–30 disconnected balance sheets. Companies are merely entry points. Every primary filing analyzed must be authorized to spawn borrower SPVs, project vehicles, lender funds, equipment vendors, and anchor customer relationships outside the nominal list.
- **Decision:**
  1. **Define Five Formal Ingestion & Source Classes:**
     - `public_us_xbrl` (18 nominal entry nodes): US domestic reporting companies filing Form 10-K/10-Q with structured XBRL. Ingested via automated `data.sec.gov` pipeline. Includes corporate electric utility `AEP`. Note that `IREN` (IREN Limited, CIK `0001878848`), while Australian-incorporated, files US domestic Form 10-K/10-Q and is ingested via `public_us_xbrl`.
     - `foreign_private_issuer` (1 nominal entry node): Foreign private issuers using Form 20-F and Form 6-K (`NBIS` Nebius Group N.V., CIK `0001513845`). Ingested via specialized 20-F/6-K parsing adapter.
     - `private_evidence_only` (3 nominal entry nodes): Unregistered private operating companies (`LAMBDA`, `CRUSOE`, `TOGETHER`). Ingested via relationship-first / evidence-ledger mechanisms (Form D filings, official credit announcements, verified contract disclosures). Explicitly tolerated with `financials.parquet` accounting baseline omitted/set to `None`.
     - `capital_provider` (6 nominal entry nodes): Asset managers, private credit fund sponsors, and bank syndicates (`BLACKSTONE`, `BLUE_OWL`, `ARES`, `APOLLO`, `MUFG`, `MORGAN_STANLEY`). Identity rule: `manager_parent` $\to$ `fund/lender vehicle / administrative agent` $\to$ `borrower`. Exposure mapping derives primarily from borrower credit agreement disclosures, not manager parent corporate balance sheets.
     - `infrastructure_operator` (2 nominal entry nodes): Independent System Operators / Regional Transmission Organizations (`PJM_INTERCONNECTION`, `ERCOT_GRID`) classified under `category: iso_rto / grid_operator`. Governs interconnection queues and transmission constraints with no balance-sheet debt edges.
     - `boundary_discovery_priority` / Wave 2 Bottleneck Candidates: Physical electrical and turbine bottleneck vendors (`VRT` Vertiv, `ETN` Eaton, `GEV` GE Vernova) are designated as discovery-priority targets to be spawned dynamically when equipment procurement or power interconnection edges point to them, keeping the nominal entry roster strictly at 30 nodes.
  2. **Classify and Reconcile Proposed Universe (30 Nominal Universe Entry Nodes):**
     Formally set the nominal entry denominator to 30 nodes (comprising 6 existing Phase 0 corporate nodes [`CRWV`, `APLD`, `NVDA`, `SMCI`, `MSFT`, `ORCL`] and 24 net-new entry targets: 18 + 1 + 3 + 6 + 2 = 30):
     - Correct SEC CIKs: `APLD` is canonicalized to CIK `0001144879`; `CORZ` (Core Scientific post-reorganization) is canonicalized to CIK `0001839341`.
     - Canonicalize legal registrant name for `IREN` as `IREN Limited`.
  3. **Establish Discovery-Driven Entity Creation Protocol:**
     Every primary filing is authorized to dynamically spawn:
     - Borrower SPVs (`borrower_spv`)
     - Holding SPVs (`holding_spv`)
     - Dedicated Lender Funds & Syndicates (`lender_spv`, `debt_syndicate`)
     - Physical Facilities & Campuses (`campus_facility`)
     - Bottleneck Equipment Vendors (`boundary_discovery_priority`)
     - Unmodelled Commercial Customers & Suppliers
  4. **Phase 1 Wave 1 Manifest (Prioritizing by Cross-Layer Join Density):**
     Prioritize 12 initial entities maximized for cross-layer join density:
     `NBIS`, `IREN`, `CORZ`, `WULF`, `HUT`, `DELL`, `HPE`, `AMD`, `META`, `AMZN`, `GOOGL`, and `BLUE_OWL`.
     Establish all prospective cross-entity edges under "Candidate High-Value Joins to Verify", maintaining that relationships remain unverified until certified with an audited claim ID.
     Strict rule: Do not ingest raw XBRL or expand datasets until ADR-017 is codified, manifest is aligned, and generic engine refinements are implemented.
  5. **Engine Refinement Sequencing:**
     Execute Step 2 engine refinements (Generic Epistemic Resolver with typed knowledge state, typed contractual-rate schema, and universal zero-lookahead temporal invariant) prior to running analytical Phase 1 notebooks or ingesting Wave 1 data.
- **Consequences:**
  Establishes an epistemically sound, scalable architecture for network expansion; eliminates false balance-sheet conflations; handles private and foreign entities natively; and focuses observatory research on repeated cross-boundary structural joins and systemic fragility.

---

### ADR-018: Phase 1 Wave 1 Ingestion, Verbatim Exhibit Certification, Dynamic Multi-Jurisdiction SPV Unwrapping, and Invariant Dual-Layer Validation
- **Status:** Accepted (2026-09-29, Phase 1 Wave 1)
- **Context:**
  Following ADR-017 and Step 2 engine refinements (ADR-016), Phase 1 Wave 1 ingests 12 high-join-density entities across hyperscalers (`META`, `AMZN`, `GOOGL`), compute/OEM hardware (`DELL`, `HPE`, `AMD`), next-generation neoclouds and HPC data centers (`NBIS`, `IREN`, `CORZ`, `WULF`, `HUT`), and private credit capital providers (`BLUE_OWL`).
  The operational requirements demand expanding this multi-layered graph while strictly preserving the repository's epistemic integrity:
  1. *Universal Zero-Lookahead Temporal Invariance:* Facts and events must never leak into temporal knowledge views prior to filing dissemination (`publicly_known_at >= claim.filing_date`).
  2. *100% Exact Verbatim Primary SEC Exhibit Certification:* Every cited claim must be a 100% exact contiguous substring within a locally cached SEC filing HTML exhibit.
  3. *Contract-Literal Debt & Financing Semantics:* No synthetic fallback rates or spreads (fail-closed principle); multi-leg floating facilities (e.g. DDTL 4.0) must use explicit rate leg tables.
  4. *Multi-Jurisdiction SPV Unwrapping:* Transnational financing entities across Delaware, Finland, and British Columbia must unwrap dynamically to canonical corporate parents without leaving orphaned or unmapped SPVs in consolidated representations.
  5. *Zero Data Drift on Frozen Phase 0 Baseline:* The pilot 5-company subnetwork topology and accounting baselines must remain 100% invariant across all canonical query dates.
- **Decision:**
  1. **Ingest and Cache Raw SEC Filings:**
     - Ingested raw SEC company facts and submission histories for all 12 Wave 1 entities into `data/raw/sec/`.
     - Ingested and cached 7 primary SEC HTML exhibits (`NBIS` 20-F & two 6-Ks, `IREN` 10-K, `CORZ` 10-Q, `HUT` 10-Q, `WULF` 10-Q).
     - Extended `src/sec_ingest.py` with custom parsing logic to handle Foreign Private Issuer Form 20-F and Form 6-K filings for Nebius Group N.V. (`NBIS`).
  2. **Entity Hierarchy and Discovery Vehicles (`config/entities.yml` & `entities.parquet`):**
     - Registered 46 entities total, including 7 dynamically discovered financing and project vehicles:
       - `NBIS_COMPUTECO_II_LLC` (Delaware SPV, borrower for MUFG facility)
       - `NBIS_COMPUTECO_II_OY` (Finnish SPV, co-borrower for MUFG facility)
       - `NBIS_INC` (US operating sub, guarantor for MUFG facility)
       - `IREN_MACKENZIE_COMPUTE` (British Columbia SPV, borrower for Blue Owl/PIMCO GPU financing)
       - `BLUE_OWL_OBDC` (Blue Owl Capital Corp, administrative agent / co-lender)
       - `PIMCO` (Pacific Investment Management Co, co-lender for IREN MFSA)
       - `COATUE` (Coatue Management, convertible noteholder for Hut 8)
  3. **Canonical Financials Regeneration (`financials.parquet`):**
     - Regenerated accounting ledgers containing 13,983 facts across 19 SEC reporting entities.
     - Preserved Phase 0 debt totals identically: CoreWeave ($35.55B total obligations), Applied Digital ($4.98B), Supermicro ($8.72B), Oracle ($125.34B), Nvidia ($33.37B).
  4. **Master Obligation Ledgers Expansion:**
     - `obligations.parquet`: 47 rows (12 new Wave 1 contracts across credit facilities, equipment leases, and long-term offtake/colocation agreements).
     - `obligation_events.parquet`: 50 rows (13 new lifecycle events).
     - `obligation_facts.parquet`: 55 rows (10 new bitemporal facts).
     - `evidence_claims.parquet`: 43 rows (6 new audited primary SEC claims).
     - `obligation_rate_legs.parquet`: 2 rows (discrete spread legs for DDTL 4.0).
  5. **100% Verbatim Primary SEC Exhibit Certification:**
     - `CLM-NBIS-001` (MUFG $775M facility @ Term SOFR + 2.50%): 100% exact substring in `NBIS_6K_20260717_mufg.htm`.
     - `CLM-NBIS-002` (Meta $27B commercial offtake agreement): 100% exact substring in `NBIS_6K_20260316_meta.htm`.
     - `CLM-IREN-001` (IREN $2.4B GPU financing: $1.2B MFSA + $1.2B Notes): 100% exact substring in `IREN_10K_20260630.htm`.
     - `CLM-CORZ-001` (Core Scientific 590 MW colocation for CoreWeave): 100% exact substring in `CORZ_10Q_20260630.htm`.
     - `CLM-HUT-001` (Coatue $150M note conversion extinction to equity): 100% exact substring in `HUT_10Q_20260630.htm`.
     - `CLM-WULF-001` (TeraWulf $2.525B convertible notes schedule): 100% exact substring in `WULF_10Q_20260630.htm`.
     - Total certified claims bound to primary SEC HTML exhibits: 35.
  6. **Dynamic Multi-Jurisdiction SPV Unwrapping:**
     - Developed automated graph unwrapping logic that collapses subsidiary/SPV edges to ultimate root parents:
       - `NBIS_COMPUTECO_II_LLC` & `NBIS_COMPUTECO_II_OY` $\to$ `NBIS`
       - `IREN_MACKENZIE_COMPUTE` $\to$ `IREN`
       - `BLUE_OWL_OBDC` $\to$ `BLUE_OWL`
     - Consolidated graph contains exactly 21 parent entities with 0 SPVs remaining.
  7. **Dual-Layer Network Topology Assertions in `src/validate.py`:**
     - Implemented dual network validation confirming both the frozen Phase 0 subnetwork (35 obligations) and the expanded Phase 1 network (47 obligations) across canonical historical dates:
       - Phase 0 economic edges: 32 (May 31, Jun 15, Jun 16, Jun 17), 34 (Jun 18, Sep 28).
       - Phase 0 known edges: 28 (Jun 17), 30 (Jun 18, Jun 30), 34 (Sep 28).
       - Phase 1 economic edges: 37 (May 31, Jun 15, Jun 16, Jun 17), 39 (Jun 18, Jun 30), 45 (Sep 28).
       - Phase 1 known edges: 29 (May 31, Jun 17), 31 (Jun 18, Jun 30), 45 (Sep 28).
     - Confirmed 0.00% data drift on Phase 0 obligations.
- **Consequences:**
  Validates the full vertical integration of Phase 1 Wave 1. The infrastructure network model now interconnects hyperscalers, GPU cloud specialists, HPC colocation providers, and private credit syndicates under rigorous contract-literal and bitemporal rules.

---

### ADR-019: Attribute-Level Contract Provenance, BDC Legal Identity Disambiguation, and Multi-Era Knowledge Reconciliation
- **Status:** Accepted (2026-09-29, Post-Wave-1 Hardening)
- **Context:**
  Following post-ingestion audit of Phase 1 Wave 1 (commit `bbf335f`), several critical epistemic vulnerabilities were discovered:
  1. *Row-Level Citation Fallacy:* A single claim citing an omnibus balance sheet debt table (e.g. Note 7 in a Form 10-Q) verified principal amounts but allowed unverified or hallucinated attributes (interest rates, maturities, legal recourse) into contract rows. For example, TeraWulf's convertibles had incorrect coupons (0.00% across all tranches) and maturities.
  2. *Lender Entity CIK Collision:* `BLUE_OWL_OBDC` (Blue Owl Capital Corporation, CIK `0001655888`, ticker `OBDC`) was improperly mapped to parent asset manager `BLUE_OWL` (Blue Owl Capital Inc., CIK `0001823945`, ticker `OWL`), violating ADR-017's lender-identity rule and duplicating parent corporate facts.
  3. *Temporal Censorship from Pre-Filing Inception:* Pegging contract public knowledge strictly to subsequent Form 10-Q filings (e.g. August 2026) avoided lookahead but created historical information blindspots ("temporal censorship") for contracts entered into via Form 8-K in 2024 or 2025.
  4. *Rigid vs Rule-Based Facility Maturities:* In multi-draw GPU financing facilities (e.g. IREN's Blue Owl/PIMCO MFSA and Notes), assigning arbitrary fixed maturities misrepresented the contract when individual tranches mature 30 months from each respective draw.
  5. *Foreign Private Issuer Disclosure Separation:* Nebius Group N.V. utilizes Form 20-F for annual financials and Form 6-K for material contracts, requiring explicit pipeline separation.
- **Decision:**
  1. **Field-Level Contract Provenance (`obligation_terms.parquet` / `.csv`):**
     - Decompose contract terms into discrete attribute-level facts with dedicated provenance links:
       `term_id`, `obligation_id`, `attribute`, `value`, `claim_id`, `source_locator`, `evidence_class`.
     - Explicitly verify and certify 38 attribute-level terms across principal amounts, interest rates, effective dates, maturities, recourse ranks, and contracted capacities.
  2. **BDC Legal Identity Disambiguation:**
     - Disambiguated `BLUE_OWL_OBDC` to SEC CIK `0001655888`, ingesting 62 distinct BDC accounting facts and purging duplicated parent submissions.
     - Added an automated CIK uniqueness assertion in `src/validate.py` ensuring zero CIK collisions across all reporting entities.
  3. **Contemporaneous Primary SEC Exhibits & Multi-Era Knowledge Reconciliation:**
     - Ingested and cached 5 contemporaneous Form 8-K primary HTML exhibits in `data/raw/sec/`:
       - `WULF_8K_20241025_conv2030.htm` ($500M 2.75% notes due 2030, filed 2024-10-25)
       - `WULF_8K_20250822_conv2031.htm` ($1,000M 1.00% notes due 2031, filed 2025-08-20)
       - `WULF_8K_20251031_conv2032.htm` ($1,025M 0.00% notes due 2032, filed 2025-10-31)
       - `HUT_8K_20240624_coatue.htm` ($150M Coatue note agreement executed 2024-06-21, filed 2024-06-24)
       - `CORZ_8K_20240604_crwv.htm` (CoreWeave ~200 MW 12-yr contract, filed 2024-06-04)
     - Verified all quotes as 100% exact normalized contiguous substrings in local HTML filings (total certified primary HTML claims: 40).
     - Separated `truth_claim_id` (verifying reported balance) from `knowledge_claim_id` (verifying earliest public disclosure).
  4. **Rule-Based Facility Maturity Modeling:**
     - For IREN GPU facilities, set `maturity_date = None`, `maturity_rule = "funding_date + 30 months"`, and `reported_final_possible_maturity = "2029-06-30"`, maintaining strict parity with the CoreWeave DDTL 2.0 convention.
  5. **Subsidiary Operational Clarity:**
     - Reclassified `NBIS_INC` as an operating subsidiary contracting with Meta, distinct from the parent guarantor `NBIS`.
  6. **Observatory Invariant Baseline:**
     - Master datasets: 46 entities, 13,754 standardized financials, 47 obligations, 51 lifecycle events, 59 bitemporal facts, 38 attribute terms, 7 assumptions, and 48 audited evidence claims.
     - Phase 0 pilot network remains 100% invariant with zero data drift.
- **Consequences:**
  Prevents attribute hallucination, enforces legal identity boundaries for private credit BDCs, restores historical public information sets without lookahead bias, and establishes institutional-grade evidentiary rigor across all network layers.

---

### ADR-019.1: BDC Legal Consolidation Isolation, Multi-Era Capacity Expansion, and Field-Level Provenance Certification
- **Status:** Accepted (2026-09-29, Wave 1 Epistemic Finalization)
- **Context:**
  Following implementation of ADR-019 (commit `549cec9`), six residual evidentiary and structural boundary issues were audited prior to opening Wave 2:
  1. *Lender Entity Consolidation Trap:* In `config/entities.yml`, `BLUE_OWL_OBDC` retained `parent_entity_id: BLUE_OWL`. Because OBDC is an externally managed public BDC (Blue Owl Capital Corporation, CIK `0001655888`, ticker `OBDC`) and not a corporate subsidiary of Blue Owl Capital Inc. (`OWL`, CIK `0001823945`), recursive SPV unwrapping improperly collapsed OBDC into its manager parent, recreating the Lender Identity Trap in the unwrapped network.
  2. *Greenshoe Two-Day Back-Projection:* For TeraWulf's 2031 convertible notes, the initial Form 8-K filed August 20, 2025 (`CLM-WULF-003`) only established an $850.0M private offering plus a 13-day option for up to $150.0M additional notes. The greenshoe option was exercised August 21 and the additional notes were issued August 22, 2025, as disclosed in Form 8-K Item 3.02 filed August 22, 2025 (`CLM-WULF-003A`). Modeling $1.0B as known and effective on August 20 back-projected the greenshoe by two days.
  3. *Stale RATE_METADATA Overrides:* In `src/curate_obligations.py`, `RATE_METADATA` contained placeholder fixed coupons for WULF 2031 (`0.0300`) and WULF 2032 (`0.0325`), overriding the contract table attributes at build time and diverging from `obligation_terms`.
  4. *Step-Function Capacity Evolution Under-Observation:* CoreWeave's colocation hosting contract with Core Scientific was modeled as jumping directly from the initial 200 MW contract (June 4, 2024) to the final 590 MW expansion (mid-2026), omitting the sequential contractual option exercises (Option 1 to 270 MW on 2024-06-25, Option 2 to 382 MW on 2024-08-06, Option 3 to 500 MW on 2024-10-23, and Option 4 / Denton expansion to 590 MW on 2025-02-27). This caused historical point-in-time capacity queries (e.g. `known_as_of("2025-01-01")`) to return 200 MW rather than the active 500 MW.
  5. *Hut 8 Coatue Maturity & Extension Terms:* The Coatue note maturity was recorded as an arbitrary month-end date (`2029-06-30`) instead of the exact 5-year initial term from closing (`2029-06-28`), and lacked formal term provenance for the three one-year extension options.
  6. *Absence of Automated Terms Field-Mapping Cross-Check:* `src/validate.py` validated existence and claim IDs of `obligation_terms` but lacked an automated cross-check asserting that attribute-level values match canonical fields in `obligations.parquet`.
- **Decision:**
  1. **BDC Legal Consolidation Isolation:**
     - Set `parent_entity_id: null` and `manager_entity_id: BLUE_OWL` for `BLUE_OWL_OBDC` in `config/entities.yml`.
     - In `src/validate.py`, assert that `net.get_root_parent("BLUE_OWL_OBDC") == "BLUE_OWL_OBDC"`, that `BLUE_OWL_OBDC` is present as an independent root node in the unwrapped graph (21 collapsed nodes), and that `BLUE_OWL` does not appear as a lender node.
  2. **Two-Stage Greenshoe Bitemporal Modeling:**
     - Split WULF 2031 into two discrete lifecycle events and facts: $850.0M on 2025-08-20 (`CLM-WULF-003`, `EVT-WULF-DEBT-CONV-2031-CREATED`, `FACT-WULF-CONV-2031-PRIN-20250820`) and $1,000.0M on 2025-08-22 (`CLM-WULF-003A`, `EVT-WULF-DEBT-CONV-2031-GREENSHOE`, `FACT-WULF-CONV-2031-PRIN-20250822`).
     - Cached primary HTML exhibits for both filings (`WULF_8K_20250820_conv2031.htm` and `WULF_8K_20250822_greenshoe.htm`).
  3. **RATE_METADATA Alignment:**
     - Corrected `fixed_coupon` to `0.0100` for WULF 2031 and `0.0000` for WULF 2032 in `src/curate_obligations.py`.
  4. **Multi-Era Colocation Capacity Evolution:**
     - Ingested four sequential Form 8-K exhibits (`CORZ_8K_20240625_opt1.htm`, `CORZ_8K_20240806_opt2.htm`, `CORZ_8K_20241023_opt3.htm`, `CORZ_8K_20250227_opt4.htm`).
     - Added four amendment events (`EVT-CRWV-CORZ-COLOCATION-OPT1` through `OPT4`), four bitemporal facts (270 MW, 382 MW, 500 MW, 590 MW), and four attribute-level provenance terms.
  5. **Contract-Literal Hut 8 Maturity:**
     - Updated maturity date to `2029-06-28` and added attribute-level provenance for the initial term and extension options (`CLM-HUT-003`).
  6. **Bidirectional Term-Field Cross-Certification:**
     - Implemented automated field-mapping cross-validation in `src/validate.py` comparing `obligation_terms` against canonical `obligations.parquet` attributes (`principal_amount`, `facility_capacity`, `contract_value`, `interest_rate`, `effective_date`, `maturity_date`, `maturity_rule`, `recourse`, `contracted_capacity_mw`, `term_years`, `margin_bps`, `floor_bps`, `benchmark`, `reference_exposure_estimate`).
     - Asserted exact evidence class distribution: 43 Class A + 1 Class C term.
  7. **Certified Invariant Baseline:**
     - Master datasets: 46 entities, 13,754 financials, 47 obligations, 56 lifecycle events, 64 bitemporal facts, 44 terms (43 Class A, 1 Class C), 7 assumptions, 54 evidence claims, 46 primary HTML verbatim verified exhibits, 0 CIK collisions, 21 collapsed parent nodes, and 0.00% Phase 0 data drift.
---

### ADR-020: Facility-Level Power Backplane & Physical Dependency Architecture
- **Status:** Accepted (2026-09-30, Task 020 / Power Backplane Sprint)
- **Context:**
  1. *Limits of Corporate/Financial Topology:* Phase 0 and Phase 1 Wave 1 mapped contractual and debt perimeters across 46 legal entities. However, the Phase 1 Analysis Sprint (commits `f6ac4da` and `35bd01e`) revealed that the network is heavily CoreWeave-centric (an articulation point whose removal shatters the giant component into 4 isolated pieces).
  2. *The Abstract Assumption Trap:* Systemic assumption `A004: POWER_DELIVERY_TIMELINE` was previously an abstract topological tag attached to real estate leases and credit facilities. It did not represent real-world physical transmission, utility counterparties, or grid interconnection queues.
  3. *The Anti-Pattern of Arbitrary Company Ingestion:* Simply ingesting a list of large utilities (e.g. AEP, Southern Co., Duke) or RTOs (ERCOT, PJM, MISO) as abstract public companies without linking them to actual data center campuses creates administrative bloat without topological depth.
  4. *Evidentiary Discrepancies in Power Metrics:* Primary SEC disclosures reveal that headline power numbers are non-fungible across distinct physical metrics. For example, Applied Digital reports 400 MW of "critical IT load" at Polaris Forge 1, while Montana-Dakota Utilities (`MDU`, CIK `0000067716`) reports an approved electric service agreement for 180 MW initial + 350 MW additional = 530 MW of "gross utility service capacity". Without typed MW measures, these numbers appear contradictory.
  5. *Actual Facility Footprints from Primary Disclosures:*
     - `APLD` Polaris Forge 1 (Ellendale, ND) is served by Montana-Dakota Utilities (`MDU`) purchasing power from the `MISO` market.
     - `CORZ` ~590 MW CoreWeave footprint spans 5 actual utilities: Denton Municipal Electric (`DME`, Texas / ERCOT large-load), Dalton Utilities (GA / Southern Co.), Oklahoma Gas & Electric (`OG&E`, OK / SPP), Duke Energy / Murphy (NC), and Austin Energy (TX / ERCOT).
     - `WULF` Lake Mariner (Somerset, NY) connects to NYISO Zone A with a 90 MW allocation from New York Power Authority (`NYPA`).
     - `IREN` connects Childress directly to ERCOT with an amended AEP connection, and Sweetwater 2 has a 600 MW grid-connection agreement with AEP Texas in ERCOT.
     - `NBIS` operates Mäntsälä, Finland (75 MW) with district heat recovery via Nivos Oy and plans Lappeenranta (up to 310 MW), with national transmission via Fingrid Oyj; but utility/interconnection contracts must only be assigned when substantiated by primary evidence, with unknown counterparties remaining `null`.
- **Decision:**
  1. **Four Dedicated Physical Layer Datasets:**
     - `facilities.parquet` (and `.csv`): Primary key `facility_id`, corporate `operator_entity_id`, legal landlord entity, campus name, location (city, county, state/country), operational status, grid region / RTO.
     - `power_relationships.parquet` (and `.csv`): Primary key `power_rel_id`, `facility_id`, `utility_entity_id`, `grid_operator_entity_id`, relationship type (`electric_service_agreement`, `interconnection_agreement`, `power_purchase_agreement`, `capacity_allocation`), tariff/pricing structure, firm vs. interruptible status, curtailment terms, and evidence claim links.
     - `power_facts.parquet` (and `.csv`): Bitemporal factual ledger (`fact_id`, `facility_id`, `mw_type`, `value_mw`, `economic_as_of`, `publicly_known_from`, `truth_claim_id`, `knowledge_claim_id`).
     - `power_terms.parquet` (and `.csv`): Attribute-level contractual terms (`term_id`, `power_rel_id`, `attribute`, `value`, `claim_id`, `source_locator`, `evidence_class`).
  2. **Strictly Typed MW Ontology (Eliminating False Contradictions):**
     Every MW measurement must specify its exact physical concept:
     - `critical_it_mw`: Actual computing power capacity inside data halls.
     - `leased_customer_mw`: MW contracted/leased to specific AI tenants (e.g. CoreWeave).
     - `gross_utility_capacity_mw`: Substation / transformer nameplate service capacity delivered by utility.
     - `contracted_service_mw`: Contractually agreed power delivery under ESA/PPA.
     - `energized_mw`: Currently live and drawing power.
     - `planned_mw`: Future phased expansion load.
     - `interconnection_request_mw`: MW entered in RTO/ISO interconnection queue.
  3. **Conservative Evidentiary Attribution:**
     - No geographic guessing: an RTO or utility is connected only if SEC filings, utility commission dockets, or executed contracts cite it.
     - If the specific contractual supplier is undisclosed in primary materials, `utility_entity_id = null`.
  4. **The Graph Join Experiment:**
     - Query whether the physical power layer bridges the 4 non-CoreWeave components. Specifically: does ERCOT or AEP Texas reconnect Core Scientific and IREN? Does the network form a shared physical backbone, or does it resolve into fragmented local utility silos?
- **Consequences:**
  Establishes a rigorous facility-first physical ontology underneath the financial network, reconciles divergent power metrics with typed MW attributes, avoids speculative utility node injection, and tests whether physical power infrastructure provides an independent macro-connection across the AI buildout.

---

### ADR-020.1: Power Measurement Certification & Facility-First Topology Hardening
- **Status:** Accepted (2026-09-30, Task 020.1 / Physical Layer Hardening)
- **Context:**
  1. *Audit of ADR-020 Implementation:* An audit of ADR-020 revealed that while the core thesis (ERCOT serves as an inter-operator physical bridge) was directionally verified, several structural topology and empirical measurement defects required remediation:
     - *Synthetic Topology Shortcuts:* uild_joint_network() previously added direct operator <-> grid edges and omitted explicit physical facility nodes from the graph projection, collapsing five distinct Core Scientific campuses into CORZ and creating synthetic electrical shortcuts.
     - *SERC Reliability Corporation Misclassification:* SERC was improperly classified as a grid_operator_rto. SERC is a NERC Regional Entity enforcing reliability standards across 16 states, not an operational balancing authority, RTO, or dispatch coordinator.
     - *Core Scientific Colocation Footprint:* Reconstructed exact gross utility capacities from CORZ 2025 Form 10-K Item 2 Properties table: Denton = 394 MW, Dalton = 195 MW, Muskogee = 100 MW, Marble = 117 MW (Murphy Electric Power Board 35 MW + Duke Energy Carolinas 82 MW), Austin = 20 MW. Gross colocation footprint = 826 MW. Added MURPHY_ELECTRIC to entity registry.
     - *IREN Empirical Disaggregation:* Disaggregated Childress (750 MW executed grid connection / ~650 MW operating data center capacity) from greenfield developments Sweetwater 1 (1,400 MW development) and Sweetwater 2 (600 MW executed connection agreement with AEP Texas).
     - *Lake Mariner Non-Overlapping Representation:* Separated the 90 MW NYPA hydro allocation from the 500 MW expansion envelope. Energized operating capacity = 226 MW (145 MW mining + 81 MW critical IT HPC leasing).
     - *Polaris Forge 1 Disaggregation:* Separated the 180 MW initial hosting data center (2023) from the 350 MW incremental ESA approved by NDPSC (60 MW online as of Q2 2026). Refrained from treating the 130 MW delta as cooling overhead without primary engineering documentation.
     - *Mechanism-Specific Reliability Regimes:* Replaced binary curtailable flags with 5 discrete legal/regulatory mechanisms: irm_service, mandatory_grid_emergency_curtailment, oluntary_price_response, interconnection_not_energized, and interruptible_tariff.
     - *Concentration Metric Reframing:* Renamed HHI to **Grid Exposure Concentration Index (HHI-form)**, eliminated inappropriate DOJ/antitrust analogies, and evaluated concentration strictly on non-overlapping capacity_basis_mw per relationship.
- **Decision:**
  1. **Literal Multi-Layer Topology (operator -> facility -> utility -> grid):**
     - Model explicit physical facility nodes (FAC-*) in the network.
     - Corporate operator connects to facility (operator_facility); facility connects to utility (acility_utility); utility connects to grid operator (utility_grid).
     - In the absence of an intermediate utility (e.g. direct high-voltage transmission interconnects), facility connects directly to grid (acility_direct_grid).
     - Prohibit all synthetic operator -> grid and operator -> utility shortcuts.
  2. **Decouple SERC from Operational Grid Graph:**
     - Reclassify SERC in config/entities.yml as 
erc_regional_entity.
     - Exclude SERC from power_relationships.parquet and acilities.parquet grid operator fields.
  3. **Non-Overlapping Capacity Basis Accounting:**
     - Exactly one capacity_basis_mw assigned per power relationship.
     - Compute Grid Exposure Concentration Index on mutually exclusive regional capacity shares.
  4. **Validator Hardening for Power Data:**
     - Validate power_claims against raw SEC EDGAR submissions JSON and require 100% exact normalized contiguous verbatim substrings in cached HTML filings.
     - Cross-check power_terms attribute values against power_relationships (capacity_basis_mw) and power_facts (alue_mw).
     - Assert 100% Class A evidence for all contractual terms and enforce the public knowledge invariant (publicly_known_from >= claim.filing_date).
- **Consequences:**
  - The literal facility-first topology confirms that ERCOT remains an articulation point and structural bridge (betweenness centrality = 0.2576, ranking 3rd behind CoreWeave and Core Scientific).
  - The joint network forms 2 connected components: a 44-node giant component and a 2-node SMCI/supplier component.
  - Excision of CoreWeave reveals that the 21-node Texas/credit component survives intact via the CORZ -> ERCOT -> IREN physical bridge.
  - Excision of ERCOT fragments the network, isolating IREN, AEP Texas, and credit syndicates from the broader AI infrastructure graph.
  - Non-overlapping Grid Exposure Concentration Index (HHI-form) is certified at **5,443.8** on capacity basis (4,401.0 MW) and **5,045.7** on energized capacity (1,111.0 MW).
  - 100% certified consistency: 62 entities, 12 facilities, 13 power relationships, 29 power facts, 14 power terms (100% Class A), 8 power claims, and zero drift on the Phase 0/Wave 1 financial baseline.

---

### ADR-020.1a: Power Certification Cleanup, Reliability Field-Level Provenance & Unenergized Capital Exposure
- **Status:** Accepted (2026-09-30, Task 020.1a / Physical Layer Freezing & Certification)
- **Context:**
  1. *Audit of ADR-020.1 Implementation:* A spot-check of commit `77450c3` verified that the literal multi-layer topology, empirical MW corrections, and ERCOT bridge findings are sound. Rerunning the network using only currently operational/served power relationships (excluding all `interconnection_not_energized` projects such as Sweetwater 1/2 and Lappeenranta) confirms a 41-node giant component plus the 2-node SMCI island; after excising CoreWeave, a 19-node `CORZ–ERCOT–IREN` cluster survives intact. The ERCOT finding is not manufactured by future development projects.
  2. *Machine Output vs. Prose Arithmetic Alignment:* The machine JSON/CSV outputs correctly aggregate measured energized MW to 1,111.0 MW (ERCOT = 750.0 MW / 67.51%; `firm_service` = 361.0 MW; `mandatory_grid_emergency_curtailment` = 100.0 MW; `voluntary_price_response` = 650.0 MW). The prose report contained stale sums (770 MW, 456 MW, 120 MW) because Austin's 20.0 MW gross utility capacity had been informally treated as energized. Because there is no separate audited `energized_mw` fact for Austin, Austin must remain unasserted (unobserved/unmeasured, not zero).
  3. *Primary Evidence Certification Accuracy:* Previously, `validate.py` stated that all power claims were verified against EDGAR submissions and HTML quotes. In fact, 7 claims were SEC filings and 1 (`CLM-PWR-NBIS-002`) was a primary utility press release by Nivos Oy. Non-SEC primary sources require their own dedicated validation path with local document caching, SHA-256 cryptographic verification, and exact verbatim substring checking.
  4. *Field-Level Provenance for Reliability Classifications:* Reliability regimes (`firm_service`, `mandatory_grid_emergency_curtailment`, `voluntary_price_response`, `interconnection_not_energized`) were previously stored on `power_relationships` without dedicated field-level claims. For Denton, `CLM-PWR-CORZ-002` (Form 8-K) proves large-load emergency curtailment, whereas `CLM-PWR-CORZ-001` proves utility nameplate capacity. For Childress, voluntary price response and ERCOT demand response participation are disclosed in IREN's Form 10-K Note 7 / Item 1 (`CLM-PWR-IREN-002`).
  5. *Concentration Metric Precision:* HHI across measured energized MW (5,045.7) must be explicitly designated as **Grid Exposure Concentration Index (Measured Energized MW Basis, HHI-form)** across 1,111.0 MW of observed operational capacity, not total operating power. Unobserved operating capacity (e.g. Austin 20 MW, Dalton) is unmeasured, not zero. The capacity basis index (5,443.8) reflects heterogeneous legal bases (utility capacity, connection agreements, hydro allocations, development envelopes).
  6. *Physical Common-Dependency Backplane Framing:* The path `CORZ → Denton facility → DME → ERCOT ← AEP Texas ← Childress ← IREN` is a shared regulatory, operational, and nodal market exposure backplane, not an electrical transmission line or power flow pathway.
  7. *The 52.5% Unenergized Capacity Finding:* Crucially, 52.49% of the modeled capacity basis (2,310.0 MW out of 4,401.0 MW) is currently unenergized (`interconnection_not_energized`). This surfaces the central question bridging Phase 1 to Task 021: How much debt and commercial obligation is written against physical capacity that does not yet exist operationally?
- **Decision:**
  1. **Strict Metric and Arithmetic Alignment:**
     - Harmonize all documentation with machine facts: measured energized MW = 1,111.0 MW; ERCOT energized = 750.0 MW (67.51%); `firm_service` energized = 361.0 MW; `mandatory_grid_emergency_curtailment` energized = 100.0 MW; `voluntary_price_response` = 650.0 MW.
     - Document that Austin (20 MW) has no primary `energized_mw` disclosure and is appropriately excluded from energized load aggregation.
  2. **Dedicated Non-SEC Primary Source Validation Path:**
     - Cache Nivos Oy primary disclosure in `data/raw/utility/NIVOS_PR_20260331.htm`.
     - In `src/validate.py`, implement `validate_utility_primary_sources()` asserting file existence, exact SHA-256 hash (`86355307b3952738465b1813e6d5ea612a8e11d037b0daf3f97315fbf0e1204d`), and 100% normalized contiguous verbatim substring matching.
     - Certify 8 primary SEC EDGAR claims + 1 primary utility disclosure.
  3. **Field-Level Provenance for Reliability Regimes:**
     - Add `reliability_claim_id` and `reliability_evidence_class` to `power_relationships.parquet`.
     - Ingest `CLM-PWR-IREN-002` (IREN Form 10-K Note 7 & Item 1 verbatim disclosure on ERCOT demand response and curtailment).
     - Expand `power_terms.parquet` to 27 rows by adding 13 contractual `reliability_regime` attribute terms (12 Class A, 1 Class B) cross-certified against `power_relationships`.
  4. **Epistemic Naming Precision:**
     - Designate concentration indices as `Grid Exposure Concentration Index (Capacity Basis, HHI-form): 5,443.8` and `Grid Exposure Concentration Index (Measured Energized MW Basis, HHI-form): 5,045.7`.
     - Reframe ERCOT from an electrical flow network to a `physical common-dependency backplane`.
  5. **Freeze Power Layer & Bridge to Task 021:**
     - Officially declare the power layer frozen under ADR-020.1a.
     - Formulate Task 021: **Energization-at-Risk / Obligation-to-MW Join**, mapping dollars of debt and customer commitments per energized MW, unenergized pipeline exposure, and quarterly slippage vulnerability.
- **Consequences:**
  - Complete, end-to-end field-level auditability across all physical power attributes.
  - Zero financial data drift ($35.551B CRWV, $6.597B APLD, 47 obligations conserved).
  - Eliminates all textual arithmetic discrepancies.
  - Solidifies the structural ERCOT invariant as an empirical foundation for Task 021.

---

### ADR-021: Capital-to-Physical Attribution Layer & Energization-at-Risk Framework
- **Status:** Accepted (2026-09-30, Task 021 Stage A & Stage B Implementation)
- **Context:**
  1. *Residual Power-Data Cleanup (ADR-020.1b):* Auditing `power_relationships` revealed several fields that outran their evidence: specifically `effective_date`, `term_years`, `tariff_structure`, and generic `curtailment_rights`. For Core Scientific, 12-year terms had been inherited from CoreWeave colocation contracts rather than utility ESAs; dates such as 2024-06-04 and 2024-10-23 reflected CoreWeave option dates rather than utility inception. These unproven fields risked contaminating timing clocks in Task 021.
  2. *The Fallacy of Synthetic Dollar/MW Ratios:* Attempting to calculate "corporate debt ÷ energized MW" (e.g. APLD $6.597B total debt ÷ 60 MW MDU incremental load at Ellendale, or IREN $2.4B Blue Owl/PIMCO financing ÷ 650 MW Childress load) represents a catastrophic multi-layer JOIN fallacy. APLD's $6.597B includes $2.15B PF2 notes (Harwood, ND), $450M corporate convertibles, $56.68M residual debt, and the retired bridge. Crucially, IREN's $2.4B financing is borrowed by `IE Mackenzie Compute Ltd.` to finance GPUs at the Mackenzie campus in British Columbia, Canada—completely independent of the 650 MW Childress campus in Texas.
  3. *The Central Empirical Question:* Rather than dividing aggregated corporate debt by partial utility meters, the true structural question is: **How much legally attributable capital and customer obligation depends on MW or compute capacity that has not yet reached productive service?**
- **Decision:**
  1. **Residual Power-Data Cleanup:**
     - Nulled all unproven `effective_date`, `term_years`, `tariff_structure`, and unproven generic `curtailment_rights` across `power_relationships.parquet`. Retained only audited, claim-backed attributes (e.g. Denton EEA alert curtailment via `CLM-PWR-CORZ-002`, Childress voluntary price response via `CLM-PWR-IREN-002`).
  2. **Expanded Physical Facilities Roster (14 Campuses):**
     - Added `FAC-IREN-MACKENZIE`: 80 MW campus in British Columbia, Canada (`CA-BC`) housing GPU servers financed under the August 2026 Blue Owl / PIMCO agreements.
     - Added `FAC-APLD-POLARIS-FORGE-2`: 200 MW critical IT campus in Harwood, ND (`US-ND`) financed by $2.15B APLD ComputeCo 2 6.750% Senior Secured Notes.
  3. **Stage A: Attribution Layer (`obligation_facility_links.parquet` / `.csv`):**
     - Established 51 granular attribution links across all 47 decomposed financial obligations.
     - Enforced the **Universal Attribution Rule:** No facility-level dollar allocation unless the dollar obligation is demonstrably attributable to that facility.
     - Corporate debt remains `corporate_unallocated` with null `facility_id` and null `allocated_amount` ($39.808B across CoreWeave corporate/SPV debt, APLD corporate convertibles/residual debt, WULF convertibles, HUT convertible, NBIS credit facility, and SMCI purchase commitments).
     - Multi-facility contracts (`OBL-CRWV-CORZ-COLOCATION-2024` reserving 590 MW across 5 Core Scientific campuses) maintain discrete topological links to each facility with `allocated_amount = None` to prevent synthetic pro-ration.
  4. **Stage B: Energization-at-Risk Quantitative Findings:**
     - **Facility-Attributable Funded Debt:** Exactly **$8,490.0M ($8.490B)** across 3 campuses:
       - Polaris Forge 1 (`FAC-APLD-POLARIS-FORGE-1`): **$3,940.0M** ($2.35B PF1 Notes + $1.59B 7% Notes).
       - Polaris Forge 2 (`FAC-APLD-POLARIS-FORGE-2`): **$2,150.0M** (PF2 Notes).
       - Mackenzie (`FAC-IREN-MACKENZIE`): **$2,400.0M** ($1.2B MFSA + $1.2B Notes).
     - **Capital-at-Risk Before Service:** Exactly **$8,490.0M (100.0% of attributable debt)** is anchored to incomplete facilities where operational capacity is below contracted capacity:
       - Polaris Forge 1: 60 MW measured energized vs 400 MW contracted lease (**85.0% energization gap**).
       - Polaris Forge 2: 0 MW measured energized vs 200 MW contracted lease (**100.0% energization gap**).
       - Mackenzie: Staged deliveries through Dec 31, 2026 (**100.0% energization gap** prior to full cluster acceptance).
     - **Customer / Lease Commitments Dependent on Incomplete Capacity:** **$11,000.0M ($11.0B)** 15-year CoreWeave lease on Polaris Forge 1 plus uncapped ELN-02/03 completion indemnities ($4.125B Class C reference proxy).
     - **Annual Debt Carrying Cost on Incomplete Capacity:** **$631.02M/year** ($415.0M/yr APLD project interest + $216.0M/yr IREN equipment interest).
  5. **Temporal Mismatch & Slippage Sensitivity:**
     - Modeled 6-, 12-, and 18-month substation and GPU delivery delays:
       - **6-Month Delay:** $315.5M carrying cost, $366.7M delayed APLD lease revenue; IREN availability window risk.
       - **12-Month Delay:** $631.0M carrying cost, $733.3M delayed APLD lease revenue; cash flow deficits require dilutive equity or liquidity draws.
       - **18-Month Delay:** $946.5M carrying cost, $1,100.0M delayed lease revenue; consumes 60% of IREN's 30-month loan term, posing severe debt service restructuring risk.
- **Consequences:**
  - Prevents bad JOINs between unallocated corporate debt and partial utility meters.
  - Successfully tests the core thesis: *Financial commitments are crystallizing significantly earlier than productive physical capacity.*
  - Establishes a permanent, field-audited bridge between contractual balance sheet liabilities and physical infrastructure commissioning state.


## ADR-021.1: Attribution Epistemic Repair & Capital Synchronization Resilience

- **Status:** Accepted (2026-09-30, Task 021 Stage B Certification)
- **Context:**
  1. *Inherited Baseline & Chronology Errors:* Post-implementation audit of ADR-021 revealed that `CLM-APLD-010` cited a June 17, 2024 Form 8-K concerning a $15M CIM promissory note and warrant rather than the $2.35B PF1 project notes (which were actually issued November 20, 2025 at 9.25%, disclosed in Form 10-Q filed Jan 8, 2026). `CLM-APLD-011` cited a Jan 24, 2025 SMBC agreement for the $2.15B PF2 notes (which actually closed March 10, 2026 at 6.75%, with proceeds held in escrow until condition satisfaction on June 18, 2026).
  2. *Validator Bypass Elimination:* The validator previously relied on a hand-written `CLAIM_TO_SEC_FILE` dictionary that allowed unmapped claims (such as claims 010–013) to evade verbatim substring checks.
  3. *Conflation of Committed Capacity with Funded Debt:* In `obligation_facility_links`, IREN's $2.4B under the August 2026 financing was labeled as funded principal. In reality, it represents committed equipment financing capacity (`amount_type = "facility_capacity"`), funding pro rata upon GPU delivery and acceptance through Dec 31, 2026, with point-in-time drawn debt undisclosed.
  4. *Dimensional Incommensurability & Zero Imputation:* Generic subtraction of `contracted_mw - energized_mw` collapsed utility service MW with critical IT MW and imputed zero to operating sites (e.g. Mackenzie, operating since April 2022 at ~80 MW data center load).
  5. *Approximated Carrying Costs and Lease Delays:* Carrying costs were approximated ($631M/yr) rather than derived from exact coupon terms, and lease delay analysis assumed 100% delay despite Building 2 (100 MW) being service-ready since October 2025.
- **Decision:**
  1. **Primary SEC Source Curation & Full Auto-Binding:**
     - Cached primary filings in `data/raw/sec/` (`APLD_10Q_20251130.htm`, `APLD_8K_20260304_notes2031.htm`, `APLD_8K_20241105_conv2030.htm`, `APLD_8K_20260107_q2release.htm`, `APLD_8K_20250602.htm`, `MSFT_10K_20260630.htm`, `ORCL_10K_20260531.htm`).
     - Replaced the hand-written `CLAIM_TO_SEC_FILE` bypass with automatic binding and verbatim substring verification across all 64 Class A SEC claims.
  2. **Bitemporal Attribution Layer (`obligation_facility_links.parquet`):**
     - Upgraded all 51 links with discrete `truth_claim_id` and `knowledge_claim_id`, strictly enforcing `publicly_known_from >= knowledge_claim.filing_date`.
     - Enforced `allocation_fraction = 1.0` for all single-facility direct allocations.
  3. **Strict Debt Semantics & Conserved Balances:**
     - Reclassified IREN's $2.4B to `amount_type = "facility_capacity"`.
     - Certified facility-attributable funded debt at strictly **$6,090.0M ($6.090B)** across APLD ComputeCo SPVs only.
     - Certified committed equipment financing capacity at **$2,400.0M ($2.400B)** for IREN Mackenzie.
     - Certified active corporate unallocated debt at **$39,357.68M ($39.358B)** as of Sep 28, 2026 (excluding retired $300M bridge and extinguished $150M Coatue note).
  4. **Typed Completion Dimensions:**
     - Replaced generic subtractions with typed dimensions: `utility_service_capacity_mw`, `utility_load_online_mw`, `critical_it_contracted_mw`, `service_ready_it_mw`, `gpu_equipment_deployment_state`, and `gpu_compute_operational_mw`. Preserved null/unknown without zero imputation.
  5. **Exact Carrying Costs & Phased Lease Delay:**
     - Derived exact coupon carrying cost for APLD funded debt: **$473.800M/year** ($217.375M PF1 + $111.300M PF1 Bldg 4 + $145.125M PF2).
     - Separated IREN's **$216.000M/year** as full-capacity coupon equivalent, not observed carrying cost.
     - Phased uncommissioned lease delay to Buildings 3 and 4 (300 MW / 75%): **$550.000M/year** maximum delayed cash flow.
  6. **Structural Capital Synchronization Resilience:**
     - Reframed findings around institutional synchronization mechanisms: escrow gating (PF2 held until June 18, 2026), staged funding upon equipment delivery and acceptance (IREN Dec 31, 2026 cliff), and springing completion indemnities (CoreWeave ELN-02/03).
     - Labeled qualitative risk tiers explicitly as "Modeled Hypotheses".
- **Consequences:**
  - Eradicates inherited date and citation drift with 100% primary source audit trails.
  - Guarantees zero data drift and zero timing invariant violations across all observatory layers.
  - Provides a trustworthy, contract-literal foundation for Phase 2 systemic contagion and cascade modeling.

---

## ADR-021.1a: Source-Registry Epistemic Auto-Binding, Bitemporal Completion Facts, and Layered Synchronization Architecture

- **Status:** Accepted (2026-09-30, Task 021 Stage B Certification)
- **Context:**
  1. *Validator Cross-Filing Vulnerability:* In ADR-021.1, `validate_sec_html_content()` checked whether each quote existed in *any* cached SEC HTML file. Global quote searching allowed cross-filing false positives (e.g. repeated boilerplate in one 10-Q validating citations to another).
  2. *Contemporaneous Knowledge Clock for APLD Debt:* PF1 ($2.35B) was closed November 20, 2025, but its knowledge clock was pinned to the Jan 8, 2026 Form 10-Q, overlooking the contemporaneous Form 8-K filed November 20, 2025 (`0001493152-25-024479`). PF2 ($2.15B) announced March 4, 2026 was missing distinct truth/knowledge claims for its economic closing on March 10, 2026 (`0001493152-26-009538`). The Bridge facility knowledge clock was pinned to the July 29, 2026 10-K rather than the contemporaneous May 5, 2026 Form 8-K (`0001493152-26-021333`).
  3. *Unsegmented Funded Debt:* Characterizing all $6.090B of funded project debt as "before service" overstated pre-service exposure because Building 2 (100 MW) at Polaris Forge 1 is already service-ready and operational.
  4. *Building 3 Partial-Operation Uncertainty:* Building 3 (150 MW) is described in Form 10-K Note 8 as partially operational, meaning the uncommissioned campus capacity is an uncertainty range (150 MW to 300 MW, 37.5% to 75.0%), and $550M/yr represents a delay ceiling rather than an exact delayed cash flow.
  5. *Hardcoded Facility Structures in Analysis Script:* The analysis engine contained a 150-line Python dictionary rather than querying a canonical database table.
- **Decision:**
  1. **Source-Registry Epistemic Auto-Binding (`data/raw/sec/source_registry.json`):**
     - Established a machine-generated source registry mapping `(accession_number, document_url) -> local_file + sha256`.
     - Hardened `validate_sec_html_content()` so that every Class A SEC claim binds strictly to its registered source document. Global search across non-registered documents is eliminated.
  2. **Contemporaneous Primary Source Curations:**
     - Downloaded and verified: `APLD_8K_20251120_pf1closing.htm`, `APLD_8K_20260310_pf2closing.htm`, `APLD_8K_20260505_bridge.htm`.
     - Updated `CLM-APLD-010` (PF1 closing Nov 20, 2025 8-K) and `CLM-APLD-013` (Bridge May 5, 2026 8-K).
     - Added `CLM-APLD-016` (PF2 closing March 10, 2026 8-K), `CLM-APLD-017` (APLD PF1 parent completion guarantee), and `CLM-APLD-018` (10-K Note 8 truth claim for Bridge).
     - Aligned public knowledge dates for `OBL-APLD-DEBT-PF1` (`2025-11-20`) and `OBL-APLD-DEBT-BRIDGE` (`2026-05-05`).
  3. **Canonical Completion Facts Table (`facility_completion_facts.parquet` / `.csv`):**
     - Created `src/curate_completion_facts.py` to curate typed completion dimensions (`utility_service_capacity_mw`, `utility_load_online_mw`, `critical_it_contracted_mw`, `service_ready_it_mw`, `gpu_equipment_deployment_state`, `gpu_compute_operational_mw`, `equipment_accepted_fraction`, `completion_status`, `next_milestone`) with bitemporal dates and claim IDs across all 14 facilities.
     - Refactored `src/analyze_energization_at_risk.py` to load directly from parquet with zero hardcoded numbers.
  4. **Re-segmented Funded Project Debt:**
     - Split $6.090B into:
       * **$3.740B Pre-Service Funded Debt:** $1.590B Building 4 7.00% notes + $2.150B PF2 6.75% notes.
       * **$2.350B Mixed Completion/Operational Exposure:** PF1 ELN-02/03 9.25% notes (Building 2 100 MW service-ready).
     - Separated active funded debt ($45.448B = $39.358B corporate + $6.090B project) from $2.400B committed equipment financing capacity ($47.848B total obligations).
  5. **Building 3 Partial-Operation Uncertainty Range:**
     - Defined uncommissioned campus capacity range: 150 MW floor (Building 4, 37.5%) to 300 MW ceiling (Buildings 3 & 4, 75.0%).
     - Relabeled contract-value delay exposure as: **$275.0M/year definitive floor** to **$550.0M/year maximum ceiling**.
  6. **Layered Synchronization Devices:**
     - Formally characterized direct parent completion guarantees (APLD PF1 shortfall funding; PF2 construction completion guarantee), escrow accounts (Goldman Sachs PF2 escrow released June 18, 2026), tenant springing guaranties (CoreWeave ELN-02/03), and staged equipment drawdown windows (IREN Mackenzie cliff Dec 31, 2026).
- **Consequences:**
  - Zero cross-filing false positives via cryptographic source-registry binding.
  - Complete elimination of hardcoded facility facts in analytical scripts.
  - Faithful representation of completion uncertainty, pre-service risk segmentation, and institutional synchronization resilience.

---

## ADR-023.1: Calibrated SEC Legibility vs. Public Awareness & Two-Clock Contractual Dynamics

- **Status:** Accepted (2026-09-30, Task 023.1 Calibration)
- **Context:**
  1. *The Fallacy of Continuous Observability:* Retrospective quantitative modeling routinely back-projects later-disclosed liabilities onto historical dates, introducing look-ahead bias and misrepresenting market informational states.
  2. *Refinement from Binary Opacity:* Binary "public invisibility" models conflate SEC/EDGAR filing legibility with total public ignorance. While public headline awareness (via press releases) often occurred within 1–4 days in audited anchor cases, detailed legal legibility (SPVs, advance rates, collateral lien scope, springing guarantees) and mid-quarter drawn balances remained opaque on EDGAR for hundreds of days.
- **Decision:**
  1. **Four-Level Information Resolution Framework:**
     - Level 0: Economic Reality ($t_{\text{eco}}$, binding contract execution).
     - Level 1: Public Headline Awareness ($t_{\text{press}}$, 1–4 days lag in audited CoreWeave anchor cases via press releases naming lenders and facility sizes; illustrative framework, not a 45-contract ledger).
     - Level 2: SEC/EDGAR Detailed Legal Legibility ($t_{\text{sec}}$, 300–600 days lag via Form S-1/10-Q exhibit filing disclosing SPVs, advance rates, and collateral liens).
     - Level 3: Current Balance Measurability ($t_{\text{meas}}$, quarterly 10-Q financial footnotes, 40–45 days lag).
     - *Anchor Illustration:* DDTL 1.0 was announced as a \$2.3B facility in 4 days (Aug 3, 2023), gained SEC legal legibility on Mar 20, 2025 (599d lag), and had an outstanding drawn balance of \$1.300B at June 30, 2026. DDTL 2.0 was announced as a \$7.5B facility in 1 day (May 17, 2024), was defined in SEC credit agreements as up to \$7.6B, and had a drawn balance of \$3.190B at June 30, 2026.
  2. **Role-Aware Lag Taxonomy ($N=45$ Inceptions):**
     - Separated 45 contract inceptions from 2 periodic measurements (`REL-MSFT-CRWV-REVENUE-CONCENTRATION` [425d] and `OBL-SMCI-SUPPLIER-COMMIT` [426d]).
     - **Public / 144A Capital Market Notes ($N=14$):** Mean lag of **-0.07 days** (median 0.0 days, range -6 to 3 days), driven by Form 8-K Items 1.01/2.03 and Rule 135c.
     - **Privately Placed Equipment / Growth Debt ($N=3$):** Mean lag of **0.00 days** (median 2.0 days, range -4 to 2 days).
     - **Commercial Colocation & Leases ($N=3$):** Mean lag of **3.00 days** (median 3.0 days, range 1 to 5 days).
     - **Parent Guarantees & Springing Indemnities ($N=12$):** Mean lag of **78.33 days** (median 3.0 days, max 599 days).
     - **Private Credit Delayed-Draw Facilities ($N=8$):** Mean lag of **169.25 days** (median 5.0 days, max 599 days).
     - Overall contract inceptions mean lag: **77.84 days** (median 3.0 days, max 599 days).
  3. **Calibrated Debt Baseline & Unresolved Current-Principal Residual Ceiling:**
     - Withdrew the uncalibrated $32.801B / 73.52% "shadow debt" headline resulting from point-in-time fact-ledger queries.
     - Carried forward the known **$25.682B public note pool** ($16.617B CoreWeave, $6.540B Applied Digital, $2.525B TeraWulf) disclosed in prior Form 8-Ks.
     - Established that on July 1, 2026 ($44.616B economic debt), the true **unresolved current-principal residual ceiling** was **$18.934B (42.44%)**.
     - **Residual Decomposition:** All \$18.934B is CoreWeave non-public-note principal: \$13.643B across 6 DDTLs + \$5.102B OEM hardware/software financing + \$0.189B Magnetar promissory note.
     - **Q1 10-Q Context:** CoreWeave filed its Q1 10-Q on May 8, 2026 showing \$25.149B total debt with itemized balances as of March 31, 2026. Therefore, \$18.934B was not previously unknown debt, but the maximum ceiling of liabilities whose June 30 current balance was not pinned down by the public-note baseline alone prior to the Q2 10-Q on Aug 12, 2026 (stale balances / unobservable Q2 draws, not nonexistent debt).
  4. **Modeled Topology Labels & The Hidden Hub:**
     - Throughout 2024 and early 2025, CoreWeave's active legal-edge degree led EDGAR legibility by 3 to 5 edges, and its unique-root counterparty degree led by 1 to 3 corporate parents.
     - In March 2025, EDGAR showed $k=1$ (`CORZ`), whereas economic reality connected CoreWeave to 4 modeled root counterparty nodes (`BLACKSTONE_MAGNETAR_SYN`, `CORZ`, `MSFT`, `OEM_FINANCING_PARTNERS`) across 6 active legal edges.
  5. **Surviving Regulatory & Contagion Thesis:**
     - Form 8-K Item 2.03 already applies to registrants; the vulnerability is private infrastructure borrowers operating outside SEC registration.
     - *The surviving thesis:* **"The important information was often not secret. What remained opaque was the JOIN."**
- **Consequences:**
  - Eliminates look-ahead bias and fact-ledger coverage artifacts.
  - Formulates the calibrated two-clock baseline for Phase 2 dynamic contagion and liquidity cascade modeling without data drift.

---

## ADR-024: Cross-Layer JOIN Gain, Multi-Layer Network Topology, and Structural Reconvergence

- **Status:** Accepted (2026-09-30, Task 024 Certification)
- **Context:**
  1. *The Disclosure Silo Fallacy:* Traditional financial regulation and risk assessment examine corporate entities via isolated disclosure silos: corporate 10-K/10-Q balance sheets, exhibit-level credit agreements, or utility regulatory filings. In each silo, risk appears legally contained, bankruptcy-remote, or over-collateralized.
  2. *Empirical Verification of "The Risk Lives in the JOIN":* A core thesis of this observatory is that systemic fragility is not visible on isolated balance sheets but emerges from the cross-layer topological join bridging corporate parents, SPVs, debt facilities, leases, physical data center facilities, electric utilities, and regional balancing authorities.
  3. *Pre-Registered Falsification Criterion:* Before running the analysis, a pre-registered falsification rule was enacted: *If the joined multi-layer network ($G_{\text{join}}$) does not increase reachable financial liabilities, expose common terminal dependencies, or alter network articulation points by at least 50% relative to single-layer views across all three empirical shock cases, the "risk lives in the JOIN" thesis is falsified.*
- **Decision:**
  1. **Four-Layer Structural Graph Formulation:**
     - Evaluated four distinct topological views from the identical frozen dataset at commit `42f9a74`:
       * **Layer 1: Corporate Balance Sheet Graph ($G_{\text{fin}}$):** 19 corporate nodes, 17 simple edges (45 multigraph edges), 3 components ($N_{\max}=14$), 6 articulation points, \$45.448B funded debt, \$38.0B leases, **0 MW physical capacity**.
       * **Layer 2: Contractual / Legal Obligation Graph ($G_{\text{cont}}$):** 36 nodes (16 project SPVs, 20 corporate parents/syndicates), 48 simple edges (62 multigraph edges), 3 components ($N_{\max}=30$), 7 articulation points, \$45.448B funded debt, \$38.0B leases, **0 MW physical capacity**.
       * **Layer 3: Physical Facility & Power Graph ($G_{\text{phys}}$):** 26 active physical nodes (11 facilities, 10 utilities, 5 grid operators), 19 simple edges, 7 disconnected components ($N_{\max}=9$, ERCOT cluster), 9 articulation points, 4,401 MW capacity, **\$0.0B debt**.
       * **Layer 4: Multi-Layer Joined Network ($G_{\text{join}}$):** 65 active nodes, 99 simple edges (133 multigraph edges), 2 components (giant component contains 63 nodes / 96.9% share), **19 articulation points**, 4,401 MW capacity, \$45.448B funded debt.
  2. **Pre-Registered Falsification Verdict: NOT FALSIFIED (PASSED):**
     - **Case A (Hyperscaler Demand Shock - MSFT):** In single-layer views ($G_{\text{fin}}$, $G_{\text{cont}}$), MSFT reaches \$3.940B debt / \$45.448B component debt, but **0 MW physical capacity** across 0 facilities. In $G_{\text{join}}$, MSFT connects directly to 6 data center sites totaling **1,176 MW** (capacity basis) / 1,226 MW (critical IT) and 4,401 MW component capacity. **Gain: +$\infty$ (>1000% $\ge 50\%$)**. Reachable network perimeter expands from 30 to 63 nodes (**+110.0% $\ge 50\%$**).
     - **Case B (GPU Collateral Value Depletion - Blackstone/Magnetar & GPU SPVs):** In single-layer views, collateral haircuts hit corporate debt but reveal **0 MW physical capacity** and 0 facilities. In $G_{\text{join}}$, GPU collateral depreciation cascades through the SPV borrowing bases, tenant lease cash flows, and threatens **1,176 MW** of operational data center capacity across 6 facilities. **Gain: +$\infty$ (>1000% $\ge 50\%$)**.
     - **Case C (Transmission Substation Delay - MDU Substation / Polaris Forge 1):** In single-layer views ($G_{\text{phys}}$), an energization delay at MDU affects only 3 nodes (MDU, Polaris Forge 1, MISO) and **\$0.0B financial debt**. In $G_{\text{join}}$, the substation delay propagates through the project links to capture **\$3.940B in direct project debt** (\$2.35B PF1 + \$1.59B 7% Notes), \$11.0B in master lease commitments, APLD parent shortfall completion obligations, and \$45.448B in component liabilities. **Gain: +$\infty$ (>1000% $\ge 50\%$)**. Reachable nodes jump from 3 to 63 (**+2,000% $\ge 50\%$**).
  3. **Emergence of Physical Facilities as Network Cut-Vertices (Articulation Points):**
     - Articulation points jump from 6 in $G_{\text{fin}}$ and 9 in $G_{\text{phys}}$ to **19 in $G_{\text{join}}$ (+216.7% vs $G_{\text{fin}}$, +111.1% vs $G_{\text{phys}}$)**.
     - Six physical data center facilities emerge as network articulation points: `FAC-APLD-POLARIS-FORGE-1`, `FAC-NBIS-MANTSALA`, `FAC-WULF-LAKE-MARINER`, `FAC-CORZ-DALTON`, `FAC-CORZ-MARBLE`, and `FAC-CORZ-MUSKOGEE`.
     - CoreWeave betweenness centrality increases from 0.4510 ($G_{\text{fin}}$) to **0.6955 ($G_{\text{join}}$) (+54.2%)**, cementing its structural role as the central bipartite router linking debt syndicates to physical colocation sites.
  4. **Empirical Certification of Triple Reconvergence:**
     - *Tenant Reconvergence:* 6 distinct physical sites (Ellendale, Denton, Dalton, Muskogee, Marble, Austin) totaling 1,226 MW and supporting \$17.583B in corporate/project debt reconverge entirely onto CoreWeave (`CRWV`) and Microsoft (`MSFT`).
     - *Grid Backplane Reconvergence:* 5 facilities totaling 3,164 MW (65.9% of portfolio capacity) reconverge onto ERCOT, coupling Core Scientific (`CORZ`) and Iris Energy (`IREN`) through shared grid reliability regimes despite having zero direct financial contracts.
     - *Protection Compression:* 4 distinct legal protections on PF1 (DSRA, sponsor guarantee, springing indemnity, master lease) collapse onto only 2 underlying terminal support nodes (`APLD_PARENT_LIQUIDITY` and `CRWV_BALANCE_SHEET`).
- **Consequences:**
  - Definitively confirms that systemic exposure cannot be diagnosed from single-issuer financial statements or isolated grid filings.
  - Replaces qualitative "shadow risk" narratives with mathematically exact, reproducible graph metrics ($\Delta N$, $\Delta E$, $\Delta \text{Debt}$, $\Delta \text{MW}$, $\Delta \text{Art}$).
  - Seals Task 024 and establishes the certified multi-layer graph topology required for Phase 2 dynamic contagion simulation.
