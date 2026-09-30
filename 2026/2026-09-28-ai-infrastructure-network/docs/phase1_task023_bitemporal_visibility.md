# Task 023.1: SEC Legibility vs. Public Awareness Calibration (Two-Clock Contractual Dynamics)

**Date:** September 30, 2026  
**Status:** Certified Empirical Research Report (Calibrated from Binary Opacity)  
**Dataset Reference:** Frozen Dataset at Commit `42f9a74` (Zero Schema or Data Expansion)  
**Primary Artifacts Generated:**  
- Monthly Trajectory: `outputs/analysis/bitemporal_monthly_trajectory.csv`
- Obligation Lag Catalog: `outputs/analysis/bitemporal_lag_summary.csv`
- Headline Summary JSON: `outputs/analysis/bitemporal_visibility_summary.json`
- Figure 1: `outputs/figures/bitemporal_debt_opacity_trajectory.png`
- Figure 2: `outputs/figures/bitemporal_network_topology_lag.png`

---

## Executive Summary: The Layered Information Resolution Framework

A standard assumption in quantitative financial research is that public markets operate under continuous informational visibility. In early versions of Task 023, this assumption was challenged through a binary "public invisibility" model. Following rigorous audit, we refine this framing:

> [!IMPORTANT]
> **Methodological Refinement: SEC/EDGAR Legibility vs. Public Headline Awareness**
> The frozen observatory measures **SEC/EDGAR filing legibility**, not total public ignorance.
> For major AI infrastructure financings, headline awareness was often rapid: press releases announced facility sizes and participating institutions within days.
> What remained opaque was the **contractual architecture**—the borrowing SPV ring-fencing, borrowing-base advance rates, recourse standards, springing conditions, cross-default links, and current drawn balances necessary to execute the cross-stack JOIN.

To capture this distinction, we replace the binary opacity model with a **Four-Level Information Resolution Framework**:

```
LEVEL 0: Economic Reality (t_eco)
         Binding credit agreement / facility execution.
         │
         ▼ (Headline Awareness Lag: 1 - 4 Days)
LEVEL 1: Public Headline Announcement (t_press)
         Press releases / news: facility existence, approximate size, named lenders.
         │
         ▼ (SEC Contractual Legibility Lag: 300 - 600 Days)
LEVEL 2: SEC/EDGAR Detailed Legal Legibility (t_sec)
         Form S-1 / 10-Q filing: borrower SPVs, advance rates, collateral lien scope,
         recourse carve-outs, covenants, and maturity schedule.
         │
         ▼ (Periodic Reporting Lag: 40 - 45 Days)
LEVEL 3: Current Balance Measurability (t_meas)
         Quarter-end 10-Q financial footnotes: drawn principal, floating rate legs, swaps.
```

### Core Calibrated Empirical Findings:
1. **Headline Visibility was Rapid; Legal-Detail Legibility was Slow:**
   - **CoreWeave DDTL 1.0 (\$1.300B):**
     * *Level 0 (Economic Inception):* July 30, 2023.
     * *Level 1 (Public Headline Announcement):* August 3, 2023 (Blackstone / Magnetar press release naming Coatue, DigitalBridge, PIMCO, Carlyle—**4-day lag**).
     * *Level 2 (SEC/EDGAR Detailed Legibility):* March 20, 2025 (Form S-1 registration statement disclosing CCAC II SPV, advance rates, and full-recourse guaranty—**599-day lag**).
   - **CoreWeave DDTL 2.0 (\$3.190B / \$7.5B Facility):**
     * *Level 0 (Economic Inception):* May 16, 2024.
     * *Level 1 (Public Headline Announcement):* May 17, 2024 (Blackstone press release—**1-day lag**).
     * *Level 2 (SEC/EDGAR Detailed Legibility):* March 20, 2025 (Form S-1 filing—**308-day lag**).
2. **Calibration of the Summer 2026 Debt Gap:**
   - On July 1, 2026, total active economic debt across the network was **\$44.616B**.
   - Point-in-time fact-ledger queries returned only \$11.815B because several public note facts were pegged to June 30 published August 12. However, the face amounts of those distributed public notes (\$16.617B CoreWeave, \$6.540B Applied Digital, \$2.525B TeraWulf = **\$25.682B total**) were already public knowledge from their initial offering Form 8-Ks.
   - Carrying forward this known \$25.682B baseline establishes that the true **unresolved current-principal gap** on July 1, 2026 was at most:
     $$\Delta D_{\text{calibrated}} = \$44.616\text{B} - \$25.682\text{B} = \mathbf{\$18.934\text{B}} \quad (\mathbf{42.44\%})$$
   - This \$18.934B gap represents unobservable quarter-end DDTL drawdowns prior to CoreWeave's Form 10-Q filing on August 12, 2026. The preliminary "73.52% shadow debt" headline is formally withdrawn as a fact-ledger coverage artifact.
3. **Role-Aware Inception Lag Distribution ($N=45$ Inceptions):**
   - **Public / 144A Capital Market Notes ($N=14$):** Mean lag is **$-0.07$ days** (median: **$0.0$ days**, range: -6 to 3 days). Form 8-K Items 1.01/2.03 ensure real-time disclosure.
   - **Commercial Colocation & Real Estate Master Leases ($N=3$):** Mean lag is **$3.0$ days** (median: **$3.0$ days**, range: 1 to 5 days).
   - **Privately Placed Equipment / Growth Debt ($N=3$):** Mean lag is **$0.0$ days** (median: **$2.0$ days**, range: -4 to 2 days).
   - **Parent Guarantees & Springing Indemnities ($N=12$):** Mean lag is **$78.33$ days** (median: **$3.0$ days**, max: 599 days).
   - **Private Credit Delayed-Draw Facilities ($N=8$):** Mean lag is **$169.25$ days** (median: **$5.0$ days**, max: 599 days).
4. **Separation of Contract Inceptions from Periodic Measurements:**
   - Periodic measurements—such as Microsoft customer revenue concentration (FY25, 425 days from period start to Form 10-K) and Supermicro supplier commitments (\$34.2B, 426 days to Form 10-K Note 12)—are separated from contract-inception statistics.
5. **Topological Lag: The Discovery of the CoreWeave Hub:**
   - Throughout 2024 and early 2025, CoreWeave’s **active legal-edge degree** in economic reality led EDGAR legibility by 3 to 5 connections, and its **unique-root counterparty degree** led by 1 to 3 distinct corporate parents. In March 2025, EDGAR reflected 1 counterparty (Core Scientific), whereas economic reality connected CoreWeave to 4 distinct corporate counterparties (Blackstone, Magnetar, Core Scientific, and Microsoft).

---

## 1. Empirical Lag Distribution across Calibrated Institutional Regimes

To prevent misclassifying instruments based on superficial ID strings, we apply a role-aware classification across the 47 obligations:

| Calibrated Institutional Category | Obligation Count ($N$) | Mean Lag ($\Delta t_{\text{sec}}$, Days) | Median Lag (Days) | Min Lag (Days) | Max Lag (Days) | Primary Regulatory Mechanism |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Public / 144A Capital Market Notes** | 14 | **-0.07** | **0.0** | -6 | 3 | Form 8-K Items 1.01/2.03; Rule 135c Press Releases |
| **Privately Placed Equipment / Growth Debt** | 3 | **0.00** | **2.0** | -4 | 2 | Form 8-K Direct Placement Disclosures |
| **Commercial Colocation & Master Leases** | 3 | **3.00** | **3.0** | 1 | 5 | Form 8-K Item 1.01 Material Definitive Agreements |
| **Parent Guarantees & Springing Indemnities**| 12 | **78.33** | **3.0** | 1 | 599 | Filed as Credit Agreement Exhibits on EDGAR |
| **Strategic Equity Investments** | 1 | **113.00** | **113.0** | 113 | 113 | Investor Quarterly Form 10-Q / Schedule 13F |
| **Private Credit Delayed-Draw Facilities** | 8 | **169.25** | **5.0** | 1 | **599** | Bilateral Confidential Facilities; S-1/10-Q Catch-Up |
| **Corporate Residual & OEM Debt** | 4 | **272.00** | **248.0** | 4 | 588 | Periodic Form 10-Q Footnote Disclosures |
| **Total Contract Inceptions** | **45** | **77.84** | **3.0** | **-6** | **599** | **Full Contractual Baseline** |

### Dedicated Measurement-Period Observations ($N=2$):
Periodic reporting metrics represent aggregated operational states rather than contract inceptions:
- `REL-MSFT-CRWV-REVENUE-CONCENTRATION`: Measures FY25 customer concentration (~67% revenue), disclosed on March 2, 2026 (**425 days from period inception**).
- `OBL-SMCI-SUPPLIER-COMMIT`: Measures non-cancelable purchase commitments (\$34.2B), disclosed in annual Form 10-K Note 12 on August 31, 2026 (**426 days from period start**).

---

## 2. Publication Visualizations

### Figure 1: Calibrated Bitemporal Debt Trajectory & Unresolved Principal Gap
![Figure 1: Calibrated Debt Trajectory](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-28-ai-infrastructure-network/outputs/figures/bitemporal_debt_opacity_trajectory.png)

#### Analysis of Figure 1:
- **Panel A (Debt Trajectory & Unresolved Principal):** Contrasts economic reality debt (red curve) against the **Calibrated Known Debt Baseline** (blue dashed curve, carrying forward the \$25.682B public notes pool) and the strict EDGAR fact-ledger coverage (grey dotted curve). The shaded pink region represents the **Unresolved Current-Principal Gap**. On July 1, 2026, this gap stands at **\$18.934B (42.44%)**, reflecting unobservable quarter-end DDTL drawdowns prior to 10-Q filing.
- **Panel B (Calibrated Opacity Ratio & Edge Gap):** Traces the percentage of debt with unresolved current principal alongside the active undisclosed legal edge count ($\Delta E$). Opacity dropped sharply as public notes were issued in 2025 and 2026, rising temporarily during quarterly reporting lags.

---

### Figure 2: Network Topology Lag & Empirical Inception Lag Distribution
![Figure 2: Topology Lag & Distribution](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-28-ai-infrastructure-network/outputs/figures/bitemporal_network_topology_lag.png)

#### Analysis of Figure 2:
- **Panel A (Giant Component & Counterparty Hub Discovery):** Compares giant component emergence in economic reality against EDGAR legibility. In addition, it tracks CoreWeave's **unique-root counterparties** (green curves). In March 2025, EDGAR reflected only 1 root counterparty (Core Scientific), whereas economic reality already connected CoreWeave to 4 distinct corporate parents.
- **Panel B (Empirical Lag Boxplot):** Demonstrates the stark regulatory bifurcation: public 144A notes cluster tightly around zero lag (-6 to 3 days), while private credit DDTLs, parent guarantees, and OEM facilities extend out to multi-hundred-day disclosure delays.

---

## 3. The Four Historical Visibility Eras (2024–2026 Chronology)

```
[ ERA 1: PRIVATE CREDIT INCUBATION ] ──► [ ERA 2: DISCOVERY SURGE ] ──► [ ERA 3: PROJECT FINANCE ] ──► [ ERA 4: REPORTING LAG ]
       Jan 2024 - Mar 2025                    Apr 2025 - Oct 2025           Nov 2025 - May 2026              Jun 2026 - Aug 2026
       • $9.9B Capacity Invisible on EDGAR    • S-1 / 144A Circulars Filed  • APLD PF1 / PF2 Issued          • $18.9B Unresolved DDTL Draws
       • Press releases public; SPVs hidden   • Public Edges Jump (4 to 9)  • 0-Day Notes Transparency       • 42.4% Pre-Filing Gap
```

### Era 1: The Private Credit Incubation Cloak (January 2024 – March 2025)
- **Macro Backdrop:** CoreWeave scaled GPU procurement via private credit facilities from Blackstone, Magnetar, Coatue, and Carlyle.
- **Informational Asymmetry:** Press releases announced headline facility sizes (\$2.3B in August 2023; \$7.5B in May 2024) within 1 to 4 days. However, **EDGAR filings contained zero detailed documentation**. No public observer could inspect borrower SPV ring-fencing, borrowing-base advance rates, or recourse terms.
- **Topological Divergence:** The economic network possessed 4 to 12 active entities and a 4-to-7 node giant component; the EDGAR graph showed zero active nodes in mid-2024 and only 3 nodes in late 2024.

### Era 2: The Capital Markets Transition & Discovery Surge (April 2025 – October 2025)
- **Macro Backdrop:** Neoclouds and Bitcoin miners transitioned toward public 144A bond markets.
- **Informational Asymmetry:** CoreWeave’s Form S-1 registration filing in early 2025 officially brought the historical DDTL stack onto EDGAR. Known edges on EDGAR jumped from 4 to 9 in April 2025 as the private credit infrastructure was retrospectively surfaced. Simultaneously, public 144A bond offerings (\$1.75B CoreWeave 2030 notes, \$2.525B TeraWulf converts) were disclosed via Form 8-K with zero lag ($\Delta t \le 1$ day).

### Era 3: The Project Finance & Pre-Construction Expansion (November 2025 – May 2026)
- **Macro Backdrop:** Transition from pure equipment debt to large-scale data center campus project finance (Polaris Forge 1 and 2 in North Dakota).
- **Informational Asymmetry:** Bitemporal visibility bifurcated across legal dimensions. Note issuances (\$2.35B PF1, \$2.15B PF2, \$1.59B 7% notes) were disclosed immediately on Form 8-K. However, construction shortfall funding conditions, escrow release triggers, and tenant springing performance guaranties (ELN-02/03) remained complex legal clauses embedded in 100-page indentures.

### Era 4: The Summer 2026 Periodic Disclosures Reporting Gap (June 30 – August 12, 2026)
- **Macro Backdrop:** CoreWeave operated over \$35B in funded debt across DDTLs, senior notes, and convertible notes.
- **Informational Asymmetry:** On July 1, 2026, the public market knew the \$25.682B face value of public notes, but had no visibility into mid-year DDTL draw levels. For 43 days until the Form 10-Q filing on August 12, 2026, **\$18.934B of debt (42.44% of total system debt)** remained an unresolved current-principal gap.

---

## 4. Topological Lag: The Hidden Hub

The bitemporal delay distorted network centrality. We distinguish **Active Legal-Edge Degree** (total contractual edges attached to CoreWeave) from **Unique-Root Counterparty Degree** (distinct consolidated corporate parents):

| Timestamp | CoreWeave Legal Edges ($E_{\text{eco}}$ vs $E_{\text{sec}}$) | Legal-Edge Gap ($\Delta E$) | CoreWeave Root Counterparties ($CP_{\text{eco}}$ vs $CP_{\text{sec}}$) | Root Counterparty Gap ($\Delta CP$) | Systemic Hub Reality | EDGAR Perception |
| :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **2024-01-01** | 1 vs 0 | **+1** | 1 vs 0 | **+1** | Incubation | Undisclosed private firm |
| **2024-06-01** | 3 vs 0 | **+3** | 1 vs 0 | **+1** | Multi-SPV Borrowing Hub | Undisclosed private firm |
| **2024-12-01** | 4 vs 1 | **+3** | 2 vs 1 | **+1** | Colocation Anchor | Emerging specialized cloud |
| **2025-03-01** | 6 vs 1 | **+5** | 4 vs 1 | **+3** | Dominant Private Credit Center | Colocation customer only |
| **2025-06-01** | 8 vs 5 | **+3** | 5 vs 3 | **+2** | Master Lease Offtaker | Major AI Neocloud |
| **2025-12-01** | 11 vs 8 | **+3** | 6 vs 4 | **+2** | Multi-Tranche Issuer | Recognized Industry Hub |
| **2026-03-01** | 13 vs 9 | **+4** | 7 vs 4 | **+3** | Multi-Lender Syndicate Hub | Major Market Issuer |
| **2026-06-01** | 19 vs 17 | **+2** | 9 vs 8 | **+1** | Systemic Infrastructure Hub | Central AI Hub |
| **2026-09-01** | 21 vs 21 | **0** | 9 vs 9 | **0** | Fully Disclosed Hub | Recognized Systemic Node |

> [!NOTE]
> **Topological Insight:**
> In March 2025, EDGAR filings showed CoreWeave connected to only 1 corporate counterparty (Core Scientific). In economic reality, CoreWeave was already connected to 4 distinct corporate counterparties (Blackstone, Magnetar, Core Scientific, and Microsoft) across 6 legal edges.
> Network centralization occurred quarters before public regulatory databases reflected that architecture.

---

## 5. Scope & Boundary Clarifications

1. **Financial and Contractual Scope:** Task 023 measures financial and contractual visibility on SEC EDGAR. It does **not** model historical month-by-month physical energization or substation commissioning states, as `facility_completion_facts` is a certified current-state snapshot.
2. **Regulatory Context:** Form 8-K Item 2.03 already mandates prompt disclosure of material direct financial obligations for SEC registrants. The opacity observed here is **not** an evasion of 8-K rules by public companies. Rather, it is the structural consequence of **large private infrastructure borrowers operating outside the SEC registration perimeter** while becoming systemic counterparties to public firms.
3. **Analytical Interpretation:** We make no empirical claims that unobserved debt caused market failures or immediate cascade defaults. The finding is strictly epistemic: **headline financing visibility was rapid, but the contractual architecture required to execute cross-company credit JOINs lagged by quarters to years.**

---

## 6. The Surviving Thesis: Where the Crisis Lives

Sprint 2 and Task 023 converge on the central finding of this research program:

$$\textbf{The important information was often not secret. What remained opaque was the JOIN.}$$

- A market participant reading press releases in 2023–2024 knew that CoreWeave had raised billions from Blackstone and Magnetar.
- A market participant reading Core Scientific filings in 2024 knew that CoreWeave was contracting hundreds of megawatts of colocation space.
- A market participant reading Applied Digital filings in 2025 knew that CoreWeave had leased 400 MW at Ellendale.

What was impossible to deduce from press releases alone—and what required detailed SEC indentures, borrowing-base formulas, and bitemporal resolution to uncover—was that:
1. CoreWeave’s lease payments at Ellendale were backstopping Applied Digital’s \$3.94B project debt;
2. Those lease payments depended on CoreWeave’s operating cash flows, which relied 67% on Microsoft;
3. CoreWeave’s server hardware was pledged to private credit syndicates under advance rates vulnerable to secondary GPU price depreciation; and
4. Ellendale’s data halls could not monetize without MDU transmission substation energization.

The systemic vulnerability does not live in hidden baseline facts; **it lives in the contractual dependencies and lagged legal disclosures required to JOIN public facts correctly.**
