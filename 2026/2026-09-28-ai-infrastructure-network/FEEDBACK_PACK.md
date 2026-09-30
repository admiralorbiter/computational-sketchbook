# AI Infrastructure Financial Network — Feedback & Review Pack (Phase 0 Epistemic Certification)

This document is a self-contained briefing pack. You can point an AI agent to this file, or copy and paste its contents directly into an LLM session (ChatGPT, Claude, etc.) to solicit expert critical feedback on the framework, empirical findings, and next steps.

---

## Copy-Paste Prompt for LLM / Expert Review

```text
I am conducting research on systemic financial vulnerability and coordination failure in the AI infrastructure buildout. The core hypothesis is:

"The thing that blows up in a financial bubble is often not hidden data. It is a hidden relationship between data that everybody can see. The crisis lives in the JOIN."

I have completed Phase 0 Epistemic Certification (ADR-015) in my computational sketchbook. The pilot maps the closed capital, hardware, and lease chain across five public companies: NVIDIA (NVDA), Supermicro (SMCI), CoreWeave (CRWV), Applied Digital (APLD), and Oracle (ORCL), connected to Microsoft (MSFT), institutional bondholders, and private credit syndicates.

Please review the methodology, empirical findings, and contract-calibrated stress test results below, and provide critical feedback on:
1. Theoretical Rigor: Does the taxonomy of 5 opacities (Perimeter, Network, Contract, Valuation, Temporal) effectively capture where 2020s project-finance bubbles hide?
2. Empirical Soundness: Are the extracted contractual obligations, SPV springing guarantee, decomposed debt facilities, and customer revenue concentration accurately characterized from verified primary SEC EDGAR disclosures?
3. Contract-Calibrated Transmission: Does the parameterized financial stress model (evaluating borrowing base formulas, springing guaranty predicates, floating vs fixed rate insulation, phased grid delays, and NRV loss provisions) effectively model the domino transmission mechanism?
4. Epistemic Discipline: Does the separation of pure amount-type reachability footprints from financial stress simulation maintain mathematical rigor?

---

### 1. The Three Epistemic Layers
- Layer 1: Standardized SEC EDGAR XBRL Financials (Point-in-time snapshot resolution via `resolve_temporal_financials` strictly enforcing `filed_date <= as_of_date` in knowledge mode, eliminating financial statement look-ahead bias).
- Layer 2: The Contractual Obligation Multi-Graph (MultiDiGraph preserving distinct legal facilities; dynamic SPV unwrapping via recursive parent traversal across 46 entities collapsing to 21 parent nodes; bitemporal architecture separating economic time `economic_as_of` from knowledge time `known_as_of` to eliminate look-ahead bias; obligation lifecycle events via `obligation_events` [50 rows total; 37 in Phase 0 subnetwork] tracking discrete creation, supersession, amendment, and extinction events with independent filing dates; fact-level bitemporality via `obligation_facts` [55 rows total; 45 in Phase 0 subnetwork] with dual `truth_claim_id` and `knowledge_claim_id` asserting `publicly_known_from >= filing_date` across 43 audited primary SEC claims; 100% verified against raw SEC EDGAR submissions JSON and 35 verbatim HTML primary sources; strict zero-lookahead stress simulation reporting unmeasured floating debt as None; obligation conservation via refinancing supersession with half-open validity intervals $[v\_from, v\_to)$; categorized strictly by amount_type with zero false netting or non-fungible dollar mixing).
- Layer 3: Shared Systemic Assumptions (Underlying economic propositions supporting multiple independent balance sheets).

### 2. Audited Balance Sheet Baselines (Latest Reported SEC Filings)
| Entity | Category | Cash & Equiv | Total Funded Debt | Lease Liabilities | Net PP&E | Full Year (FY) Revenue | Latest Quarter Revenue |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NVDA** | Hardware Supplier | $22.44B | $33.37B | $5.49B | $14.28B | $215.94B (FY26) | $96.22B (Q2 FY27) |
| **SMCI** | Server OEM | $7.52B | $8.72B | $0.54B | $0.63B | $39.06B (FY26) | $11.12B (Q4 FY26) |
| **CRWV** | Neocloud Operator | $5.52B | $35.55B | $16.32B | $46.74B | $5.13B (FY25) | $2.58B (Q2 2026) |
| **APLD** | Data Center Host | $1.59B | $4.98B | $0.07B | $4.24B | $0.61B (FY26) | $0.26B (Q4 FY26) |
| **ORCL** | Cloud Hyperscaler | $36.37B | $125.34B | $34.62B | $127.84B | $67.36B (FY26) | $19.34B (Q1 FY27) |
| **MSFT** | Cloud Hyperscaler | $20.94B | $46.14B | $21.92B | $313.08B | $331.84B (FY26) | $90.01B (Q4 FY26) |

### 3. The Obligation Ledger (Phase 0 Epistemic Certification: 35 Modeled Obligations in Master Ledger)
1. `OBL-CRWV-APLD-LEASE` ($11.0B lifetime value): CoreWeave SPV VIII leases 400 MW at Polaris Forge 1 from APLD ELN project LLCs for 15 years. Phased across Buildings 2, 3, and 4: ~150 MW operational (Building 2 100 MW + Building 3 partial 50 MW proxy, generating $275.0M/yr base rent), ~250 MW pending expansion (deferring $458.3M/yr). (APLD 10-K, Item 1 & Note 14).
2. `OBL-CRWV-APLD-GUARANTY-ELN02` (uncapped contingent obligation): CoreWeave parent Unconditional Springing Guaranty specifically covering Phase 2/4 Space (2 of 4 data halls in Building 2; capacity_mw = None, unstated face value). Springs into active parent liability upon explicit Exhibit 10.1 predicates. (APLD 10-K, Note 14 & Exhibit 10.1).
3. `OBL-CRWV-APLD-GUARANTY-ELN03` (uncapped contingent obligation with $4.125B Class C reference proxy): CoreWeave parent Unconditional Springing Guaranty for Building 3 (150 MW campus expansion lease assigned to SPV). Springs under Exhibit 10.2. Building 4 (150 MW, ~$4.13B) carries no CoreWeave parent springing guarantee (APLD guarantees the landlord).
4. **CoreWeave Discrete Funded Debt (16 Tranches Reconciling to Exactly $35.551B, 0.00% Drift):**
   - `OBL-CRWV-DEBT-DDTL1`: $1.300B (`CRWV_CCAC_II` $\to$ `BLACKSTONE_MAGNETAR_SYN`, entered 2023-07-30, matures 2028-03-28, SOFR + 9.6196%, Form S-1/A `CLM-CRWV-007` & Form 10-Q `CLM-CRWV-001`/`002`)
   - `OBL-CRWV-DEBT-DDTL2`: $3.190B (`CRWV_CCAC_IV` $\to$ `BLACKSTONE_MAGNETAR_SYN`, entered 2024-05-16, maturity rule funding_date + 5 years, reported final facility maturity August 2030 [2030-08-31], spread grid 6.00%–13.00%, Form 10-Q `CLM-CRWV-016`)
   - `OBL-CRWV-DEBT-DDTL2-1`: $3.000B (`CRWV_CCAC_IV` $\to$ `BLACKSTONE_MAGNETAR_SYN`, entered 2025-09-29 via Fifth Amendment, Form 8-K filed 2025-10-02 `CLM-CRWV-010`, maturity rule funding_date + 5 years, reported final facility maturity March 2031 [2031-03-31], SOFR + 4.25%)
   - `OBL-CRWV-DEBT-DDTL3`: $2.215B (`CRWV_CCAC_VII` with co-borrower `CRWV_CCAC_V` $\to$ `MUFG_BANK_SYN`, entered 2025-07-28, matures 2030-08-21, SOFR + 4.00%, Form 8-K `CLM-CRWV-009` & Form 10-K `CLM-CRWV-010`)
   - `OBL-CRWV-DEBT-DDTL4`: $2.837B drawn of $8.500B capacity (`CRWV_SPV_VIII` $\to$ `MUFG_BANK_SYN`, entered 2026-03-30, matures 2032-03-31, limited bad-acts carve-out parent guarantee under Exhibit 10.2 [$2.837B Class C underlying principal reference], Form 8-K `CLM-CRWV-012` & Form 10-Q Note 10 `CLM-CRWV-004`)
   - `OBL-CRWV-DEBT-DDTL5`: $1.101B (`CRWV_FINANCING_DDTL_V` $\to$ `MORGAN_STANLEY_SYN`, entered 2026-05-15, matures 2031-11-15, SOFR + 4.50%, 71.42% funding ratio, Form 8-K `CLM-CRWV-006`)
   - `OBL-CRWV-DEBT-NOTES-2030`: $2.000B (`CRWV` $\to$ `INSTITUTIONAL_BONDHOLDERS`, issued 2025-05-27, matures 2030-06-01, fixed 9.250%, Senior Unsecured with subsidiary guarantees, Form 8-K `CLM-CRWV-008`)
   - `OBL-CRWV-DEBT-NOTES-2031-900`: $1.750B (`CRWV` $\to$ `INSTITUTIONAL_BONDHOLDERS`, issued 2025-07-25, matures 2031-02-01, fixed 9.000%, Senior Unsecured with subsidiary guarantees, Form 8-K `CLM-CRWV-009A`)
   - `OBL-CRWV-DEBT-NOTES-2031-975`: $2.750B (`CRWV` $\to$ `INSTITUTIONAL_BONDHOLDERS`, initial $1.750B issued 2026-04-14, $1.000B add-on on 2026-04-21, matures 2031-10-15, fixed 9.750%, Senior Unsecured with subsidiary guarantees, Form 8-K `CLM-CRWV-013`/`013A`)
   - `OBL-CRWV-DEBT-NOTES-2032-9625`: $1.250B (`CRWV` $\to$ `INSTITUTIONAL_BONDHOLDERS`, issued 2026-06-18, matures 2032-07-15, fixed 9.625%, Senior Unsecured with subsidiary guarantees, Form 8-K `CLM-CRWV-014`)
   - `OBL-CRWV-DEBT-NOTES-2032-EUR`: $2.279B (`CRWV` $\to$ `INSTITUTIONAL_BONDHOLDERS`, issued 2026-06-18, matures 2032-07-15, fixed 8.500% EUR, Senior Unsecured with subsidiary guarantees, Form 8-K `CLM-CRWV-014`)
   - `OBL-CRWV-DEBT-CONV-2031`: $2.588B (`CRWV` $\to$ `INSTITUTIONAL_BONDHOLDERS`, issued 2025-12-11, matures 2031-12-01, fixed 1.750%, Senior Unsecured convertible, Form 8-K `CLM-CRWV-011`)
   - `OBL-CRWV-DEBT-CONV-2032`: $4.000B (`CRWV` $\to$ `INSTITUTIONAL_BONDHOLDERS`, issued 2026-04-14, matures 2032-10-01, fixed 1.750%, Senior Unsecured convertible, Form 8-K `CLM-CRWV-013`)
   - `OBL-CRWV-DEBT-OEM`: $4.220B (`CRWV` $\to$ `OEM_FINANCING_PARTNERS`, entered 2025-01-01, matures 2030-07-31, Form 10-Q Note 10 `CLM-CRWV-001`)
   - `OBL-CRWV-DEBT-OEM-NR`: $0.882B (`CRWV` $\to$ `OEM_FINANCING_PARTNERS`, entered 2025-06-01, matures 2029-12-31, non-recourse OEM, Form 10-Q Note 10 `CLM-CRWV-004`)
   - `OBL-CRWV-DEBT-MAGNETAR`: $0.189B (`CRWV` $\to$ `BLACKSTONE_MAGNETAR_SYN`, entered 2024-01-15, matures 2029-01-31, Form 10-Q Note 10 `CLM-CRWV-001`)
   - *(Sum of 16 discrete tranches = $35,551,000,000.00 exact; 6 explicit parent guarantee edges modeled from `CRWV` to syndicates with `amount = None`, including 1 limited bad-acts carve-out for DDTL 4.0 with Class C underlying principal reference; 1 co-borrower edge `CRWV_CCAC_V` under DDTL 3.0).*
5. `REL-MSFT-CRWV-REVENUE-CONCENTRATION` ($3.44B recognized revenue): Microsoft customer concentration representing 67% of CoreWeave's recognized revenue in FY25 ($5.131B total); characterized as recognized revenue concentration, not an unverified 5-year take-or-pay contract. (CRWV 10-K, Note 17).
6. `OBL-SMCI-SUPPLIER-COMMIT` ($34.20B remaining commitment): Supermicro non-cancelable purchase commitments primarily with GPU and component suppliers through next 12 months. (SMCI 10-K, Note 12).
7. `OBL-NVDA-CRWV-EQUITY` ($2.00B equity): NVIDIA January 2026 strategic Series C Preferred Stock private placement. (CRWV 10-Q, Note 10).
8. **Applied Digital Discrete Debt (6 Tranches Reconciling to $5,306.68M Gross Principal at May 31, Conserved Across Refinancing):**
   - `OBL-APLD-DEBT-PF1`: $2.350B principal (issued by `APLD_COMPUTECO` due Dec 15, 2030, fixed 9.25%, Form 10-K Note 8)
   - `OBL-APLD-DEBT-PF2`: $2.150B principal (issued by `APLD_COMPUTECO2` due Mar 15, 2031, fixed 6.75%, Form 10-K Note 8)
   - `OBL-APLD-DEBT-CONV`: $450.0M principal (issued by `APLD` due Jun 30, 2030, fixed 2.75%, Form 10-K Note 8)
   - `OBL-APLD-DEBT-BRIDGE`: $300.0M principal (floating SOFR, entered May 1, 2026, due Apr 30, 2027; retired June 16, 2026, superseded by $1.59B 7.00% Senior Secured Notes, Form 10-K Note 8 & Note 19)
   - `OBL-APLD-DEBT-OTHER`: $56.68M principal (promissory notes and equipment debt, Form 10-K Note 8)
   - `OBL-APLD-DEBT-7PCT-2026`: $1.590B principal (issued June 16, 2026 by `APLD_COMPUTECO3` due June 15, 2031, fixed 7.00%, refinancing bridge and funding ELN-04, Form 8-K filed 2026-06-16 `CLM-APLD-008` & Form 10-K Note 19)
   - *(Active gross principal at May 31 = $5,306.68M vs $4,975.94M net carrying debt; post-refinancing at Sep 28 = $6,596.68M; exact 0.00% drift).*

### 4. Shared Systemic Assumptions
- `A001: GPU_RESIDUAL_VALUE`: H100/H200 hardware retains >=45% secondary market resale value, supporting borrowing base advance rates on $10.8B DDTLs.
- `A002: REFINANCING_AVAILABILITY`: Private credit and high-yield spreads remain viable (+450 bps over SOFR) when 5-year loans mature.
- `A003: CLUSTER_UTILIZATION`: Deployed capacity maintains >=85% billable utilization to cover fixed 15-year lease obligations.
- `A004: POWER_DELIVERY_TIMELINE`: Regional utilities energize 400 MW substations on schedule without 12-24 month interconnection delays.
- `A005: ANCHOR_CUSTOMER_CONTINUATION`: Microsoft continues offloading compute demand rather than transitioning to custom silicon (Maia).
- `A006: HYPERSCALER_CAPEX_EXPANSION`: Cloud hyperscalers continue expanding infrastructure capex at >20% CAGR.
- `A007: BACKLOG_CASH_CONVERSION`: Reported backlogs convert to cash without renegotiation or performance disputes.

### 5. Parameterized Financial Stress Prototype Results (`src/stress.py`)
- **Hypothetical MTM Financing Sensitivity (-40% GPU collateral value):** Evaluates drawn DDTLs against a 71.42% funding-ratio proxy, modeling a **$4.32B modeled refi gap** (Class C proxy). Section 2.05 of DDTL 5.0 does NOT trigger mandatory cash prepayment on secondary price declines (cash remains $5.52B intact), but eliminates undrawn capacity.
- **Anchor Customer Demand Trim (-30% Microsoft volume, $3.44B base):** Reduces CoreWeave recognized revenue by **$1.03B/yr cash flow loss**, conditionally triggering **Springing Event (ii)** under Exhibit 10.2 and activating the uncapped parent ELN-03 guaranty (**$4.13B Class C reference proxy**) and Exhibit 10.1 on Building 2 Phase 2/4 Space (2 of 4 halls; uncapped face value). Building 4 excluded.
- **SOFR Base Rate Shock (+300 bps SOFR benchmark):** Note 8 reports **$4,661M** active swap notional against $12.206B floating debt at CRWV, leaving **$7.545B unhedged**, plus APLD's **$300.0M floating bridge facility**. Direct cash drain is **$226.4M CRWV + $9.0M APLD = $235.4M/yr** (Sensitivity band: $27.3M/yr at 95% full coverage to $303.9M/yr if DDTL 1.0–3.0 unhedged).
- **Credit Spread / Refinancing Shock (+300 bps credit spread at maturity):** Existing contractual spreads unaffected; shock hits $10.60B scheduled principal maturing over 2026–2027 ($4.41B in 2026, $6.18B in 2027). Parameterized at 100% rollover (**$317.9M/yr added refi interest**; sensitivity range: $159.0M at 50% to $317.9M at 100%).
- **Phased Grid Energization Delay (12-month delay at Polaris Forge 1):** Models operational reality across Buildings 2, 3, and 4: ~150 MW operational (Building 2 100 MW + Building 3 parameterized at 50 MW live, Class C proxy) generates $275.0M/yr base rent ongoing, while ~250 MW pending expansion is deferred ($458.3M rent delayed), leaving APLD with **$135.9M** in construction debt carrying costs (consuming only **8.5% of APLD cash**; sensitivity range: 6.8% [$108.7M] to 9.4% [$149.4M] across 25–100 MW live).
- **OEM Purchase Commitment Expected Loss (SMCI 15% Demand Pause on $34.2B):** Dual-channel transmission: Accounting channel incurs a non-cash US-GAAP ASC 330 NRV write-down provision of **$2.05B** reducing equity. Cash liquidity channel: negotiated cancellation settlement (parameterized at 15%) consumes **$769.5M cash (10.2%)**, while inventory delivery would consume **$5.13B cash (68.2%)**.

---
Please provide your critique of this Phase 0.7 pilot, identify any unmodeled contractual nuances or blind spots, and suggest specific refinements for maintaining epistemic rigor.
```

