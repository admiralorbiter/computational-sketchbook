# AI Infrastructure Financial Network — Feedback & Review Pack (Phase 0.7)

This document is a self-contained briefing pack. You can point an AI agent to this file, or copy and paste its contents directly into an LLM session (ChatGPT, Claude, etc.) to solicit expert critical feedback on the framework, empirical findings, and next steps.

---

## Copy-Paste Prompt for LLM / Expert Review

```text
I am conducting research on systemic financial vulnerability and coordination failure in the AI infrastructure buildout. The core hypothesis is:

"The thing that blows up in a financial bubble is often not hidden data. It is a hidden relationship between data that everybody can see. The crisis lives in the JOIN."

I have completed Phase 0.7 (Contract-Calibrated Five-Company Pilot & Parameterized Financial Stress Prototype) in my computational sketchbook. The pilot maps the closed capital, hardware, and lease chain across five public companies: NVIDIA (NVDA), Supermicro (SMCI), CoreWeave (CRWV), Applied Digital (APLD), and Oracle (ORCL), connected to Microsoft (MSFT), institutional bondholders, and private credit syndicates.

Please review the methodology, empirical findings, and contract-calibrated stress test results below, and provide critical feedback on:
1. Theoretical Rigor: Does the taxonomy of 5 opacities (Perimeter, Network, Contract, Valuation, Temporal) effectively capture where 2020s project-finance bubbles hide?
2. Empirical Soundness: Are the extracted contractual obligations, SPV springing guarantee, decomposed debt facilities, and customer revenue concentration accurately characterized from the SEC disclosures?
3. Contract-Calibrated Transmission: Does the parameterized financial stress model (evaluating borrowing base formulas, springing guaranty predicates, floating vs fixed rate insulation, phased grid delays, and NRV loss provisions) effectively model the domino transmission mechanism?
4. Epistemic Discipline: Does the separation of pure amount-type reachability footprints from financial stress simulation maintain mathematical rigor?

---

### 1. The Three Epistemic Layers
- Layer 1: Standardized SEC EDGAR XBRL Financials (Duration-aware flows, derived Q4 flows, and aggregated funded debt).
- Layer 2: The Contractual Obligation Multi-Graph (MultiDiGraph preserving distinct facilities; categorized strictly by amount_type with zero false netting or non-fungible dollar mixing).
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

### 3. The Obligation Ledger (Phase 0.7 Pilot)
1. `OBL-CRWV-APLD-LEASE` ($11.0B lifetime value): CoreWeave SPV VIII leases 400 MW at Polaris Forge 1 from APLD ELN project LLCs for 15 years. Phased across Buildings 2, 3, and 4: ~150 MW operational (Building 2 100 MW + Building 3 partial 50 MW, generating $275.0M/yr base rent), ~250 MW pending expansion (Building 3 remaining 100 MW + Building 4 150 MW, deferring $458.3M/yr). (APLD 10-K, Item 1 & Note 14).
2. `OBL-CRWV-APLD-GUARANTY` ($11.0B contingent guarantee): CoreWeave parent provided an Unconditional Springing Guaranty of Payment and Performance for SPV VIII obligations. Springs into active parent liability upon explicit Exhibit 10.1 predicates: (i) SPV bankruptcy, (ii) material adverse amendment, default, or termination of the Colocation Agreement, or circumstances permitting customer to cease or materially reduce monthly payments, (iii) separateness covenant breach, or (iv) debt acceleration. (APLD 10-K, Note 14 & Exhibit 10.1).
3. `OBL-CRWV-DEBT-DDTL1` ($1.300B principal drawn): CoreWeave DDTL 1.0 from Blackstone/Magnetar syndicate (Maturity Mar 2028, floating SOFR + 2.75%). (CRWV 10-Q, Note 7).
4. `OBL-CRWV-DEBT-DDTL2` ($3.190B principal drawn): CoreWeave DDTL 2.0 (Maturity Aug 2030, floating SOFR + 3.25%). (CRWV 10-Q, Note 7).
5. `OBL-CRWV-DEBT-DDTL2-1` ($3.000B principal drawn): CoreWeave DDTL 2.1 (Maturity Mar 2031, floating SOFR + 3.25%). (CRWV 10-Q, Note 7).
6. `OBL-CRWV-DEBT-DDTL3` ($2.215B principal drawn): CoreWeave DDTL 3.0 (Maturity Aug 2030, floating SOFR + 3.50%). (CRWV 10-Q, Note 7).
7. `OBL-CRWV-DEBT-DDTL4` ($2.837B principal drawn, $8.500B capacity): CoreWeave DDTL 4.0 Non-Recourse SPV credit commitment ($2.837B drawn as of Q2 2026). (CRWV 10-Q, Note 7).
8. `OBL-CRWV-DEBT-DDTL5` ($1.101B principal drawn): CoreWeave DDTL 5.0 (Maturity Nov 2031, floating SOFR + 3.50%, governed by 71.42% funding-ratio formula). (CRWV 10-Q, Note 7 & Exhibit 10.1).
9. `OBL-CRWV-DEBT-NOTES` ($10.029B principal): CoreWeave Senior Secured Notes across USD and EUR tranches (Fixed coupons 9.00% to 9.75%). (CRWV 10-Q, Note 7).
10. `OBL-CRWV-DEBT-CONV` ($6.588B principal): CoreWeave Convertible Senior Notes 2031 and 2032 (Cash coupon 1.75% to 2.00%). (CRWV 10-Q, Note 7).
11. `OBL-CRWV-DEBT-OEM` ($4.220B principal): CoreWeave Recourse OEM and software license financing arrangements (~11% installment rate). (CRWV 10-Q, Note 7).
12. `OBL-CRWV-DEBT-OEM-NR` ($882M principal drawn): CoreWeave Non-Recourse OEM equipment financing facility. (CRWV 10-Q, Note 7).
13. `OBL-CRWV-DEBT-MAGNETAR` ($189M principal): CoreWeave Magnetar subordinated loan (Maturity Jan 2029). (CRWV 10-Q, Note 7).
    *(CoreWeave 11 tranches sum exactly to $35.551B future principal: $1.300B + $3.190B + $3.000B + $2.215B + $2.837B + $1.101B + $10.029B + $6.588B + $4.220B + $0.882B + $0.189B = $35.551B, exact 0.00% drift).*
14. `REL-MSFT-CRWV-REVENUE-CONCENTRATION` ($3.44B recognized revenue): Microsoft customer concentration representing 67% of CoreWeave's recognized revenue in FY25 ($5.131B total); characterized as recognized revenue concentration, not an unverified 5-year take-or-pay contract. (CRWV 10-K, Note 17).
15. `OBL-SMCI-SUPPLIER-COMMIT` ($34.20B remaining commitment): Supermicro non-cancelable purchase commitments primarily with GPU and component suppliers through next 12 months. (SMCI 10-K, Note 12).
16. `OBL-NVDA-CRWV-EQUITY` ($2.00B equity): NVIDIA January 2026 strategic Series C Preferred Stock private placement. (CRWV 10-Q, Note 10).
17. `OBL-APLD-DEBT-PF1` ($2.35B principal): Applied Digital Polaris Forge 1 9.25% Senior Secured Notes due 2029 (Fixed rate coupon). (APLD 10-K, Note 8).
18. `OBL-APLD-DEBT-PF2` ($2.15B principal): Applied Digital ComputeCo 2 6.75% Senior Notes due 2030 (Fixed rate coupon). (APLD 10-K, Note 8).
19. `OBL-APLD-DEBT-CORP` ($475.9M principal): Applied Digital corporate credit facilities and notes. (APLD 10-K, Note 8).

### 4. Shared Systemic Assumptions
- `A001: GPU_RESIDUAL_VALUE`: H100/H200 hardware retains >=45% secondary market resale value, supporting borrowing base advance rates on $10.8B DDTLs.
- `A002: REFINANCING_AVAILABILITY`: Private credit and high-yield spreads remain viable (+450 bps over SOFR) when 5-year loans mature.
- `A003: CLUSTER_UTILIZATION`: Deployed capacity maintains >=85% billable utilization to cover fixed 15-year lease obligations.
- `A004: POWER_DELIVERY_TIMELINE`: Regional utilities energize 400 MW substations on schedule without 12-24 month interconnection delays.
- `A005: ANCHOR_CUSTOMER_CONTINUATION`: Microsoft continues offloading compute demand rather than transitioning to custom silicon (Maia).
- `A006: HYPERSCALER_CAPEX_EXPANSION`: Cloud hyperscalers continue expanding infrastructure capex at >20% CAGR.
- `A007: BACKLOG_CASH_CONVERSION`: Reported backlogs convert to cash without renegotiation or performance disputes.

### 5. Parameterized Financial Stress Prototype Results (`src/stress.py`)
- **Hypothetical MTM Financing Sensitivity (-40% GPU collateral value):** Evaluates drawn DDTLs against a 71.42% funding-ratio proxy, creating a **$4.32B funding deficit**, consuming **78.2% of CoreWeave's cash** and freezing capex. (Class C analytical sensitivity; contractually DDTL 5.0 defines 71.42% of capex cost with 6-yr depreciation).
- **Anchor Customer Demand Trim (-30% Microsoft volume, $3.44B base):** Reduces CoreWeave recognized revenue by **$1.03B/yr cash flow loss**, conditionally triggering **Springing Event (ii)** under Exhibit 10.1 and activating the **$11.0B parent Springing Guaranty** if Microsoft is the Building ELN-03 tenant.
- **SOFR Base Rate Shock (+300 bps SOFR benchmark):** Contractual **95% swap hedging mandate** under DDTL 5.0 limits CoreWeave recourse floating drain to **$16.2M/yr**; DDTL 4.0 floating adds $42.0M/yr; APLD floating adds $14.3M/yr, for a total hedged cash drain of **$72.5M/yr**.
- **Credit Spread / Refinancing Shock (+300 bps credit spread at maturity):** Existing contractual spreads unaffected; shock hits debt as it rolls over: $4.41B in 2026 and $6.18B in 2027 ($10.60B maturing over 24 months), adding **$317.9M/yr in added refi interest** by 2027 ($450.4M/yr through 2028).
- **Phased Grid Energization Delay (12-month delay at Polaris Forge 1):** Models operational reality across Buildings 2, 3, and 4: ~150 MW operational (Building 2 + Building 3 partial) generates **$275.0M/yr** base rent ongoing, while ~250 MW pending expansion is deferred ($458.3M rent delayed), leaving APLD with **$135.9M** in construction debt carrying costs (consuming only **8.5% of APLD cash**).
- **OEM Purchase Commitment Expected Loss (SMCI 15% Demand Pause on $34.2B):** Dual-channel transmission: Accounting channel incurs a non-cash US-GAAP ASC 330 NRV write-down provision of **$2.05B** reducing equity (40% recovery haircut on $5.13B excess allocation). Cash liquidity channel: negotiated cancellation settlement consumes **$769.5M cash (10.2%)**, while inventory delivery would consume **$5.13B cash (68.2%)**.

---
Please provide your critique of this Phase 0.7 pilot, identify any unmodeled contractual nuances or blind spots, and suggest specific refinements for maintaining epistemic rigor.
```
