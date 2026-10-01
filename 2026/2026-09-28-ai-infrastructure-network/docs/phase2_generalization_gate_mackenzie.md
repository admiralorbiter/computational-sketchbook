# Phase 2.3 Generalization Gate: IREN Mackenzie Data-Sufficiency & Abstraction Audit

**Document ID:** GATE-PHASE2-GENERALIZATION-MACKENZIE  
**Status:** Certified Epistemic Audit & Comparative Architectural Gate  
**Date:** October 1, 2026  
**Projects Compared:**  
1. **Polaris Forge 1 (PF1):** $3.94B Dual-Silo 144A Fixed Notes (Ellendale, ND) — *Binary Rent Step-Up Archetype*  
2. **Project Jupiter:** ~$18.0B Syndicated Bank Facility & Microgrid (Santa Teresa, NM) — *Multi-State Offtake Carry Archetype*  
3. **IREN Mackenzie:** Up-to-$2.4B Staged GPU Equipment Financing Facility (Mackenzie, BC) — *Staged Equipment Acceptance & Availability Window Cliff Archetype*  

---

## 1. Executive Summary & The Third Generalization Challenge

Phase 2.1 proved and froze the deterministic milestone surface architecture for **Polaris Forge 1 (`PF1`)**, establishing how fixed semiannual debt service interacts with utility energization delays and parent completion guarantees. Phase 2.2 tested **Project Jupiter**, uncovering that hyperscale offtake contracts feature multi-state pre-operational carry regimes rather than binary on/off rent, and demonstrating a documented **65–71 day lead time** from physical pipeline permitting orders to financial debt-trading recognition.

However, both PF1 and Jupiter center on large-scale **civil infrastructure and power energization bottlenecks** (utility grid interconnections and natural gas pipeline rights-of-way). To test whether the observatory's abstraction survives an entirely different failure topology, Phase 2.3 executes the Generalization Gate on **IREN Mackenzie** (`IE Mackenzie Compute Ltd.`):

```
                   [The Three Infrastructure-Finance Archetypes]

   Polaris Forge 1 (`PF1`)           Project Jupiter              IREN Mackenzie
─────────────────────────────   ──────────────────────────   ─────────────────────────────
Capital: $3.94B 144A Notes      Capital: ~$18.0B Bank Loan   Capital: Up-to-$2.4B Facility
         Fixed 9.25% & 7.00%             SOFR + 250 bps               Fixed 9.0% (MFSA + Notes)
Physical: Substation Energize   Physical: Gas Pipeline ROW   Physical: GPU Delivery & Acceptance
Site:    Greenfield 400 MW      Site:    Greenfield 2.4 GW   Site:    Existing 80 MW Operating
Clock 1: Civil Construction     Clock 1: State Land Permit   Clock 1: Hardware Logistics / RFS
Clock 2: Utility (MDU)          Clock 2: Fuel Availability   Clock 2: Customer Acceptance Test
Offtake: Binary Rent Step-Up    Offtake: Multi-State Carry   Offtake: Compute Cloud Revenue
Legal:   Parent Capex Support   Legal:   Tenant Force Majeure Legal:   Parent Payment Guaranty
Binding: Lumpy Semiannual Dates Binding: Floating SOFR Carry Binding: Dec 31, 2026 Window Cliff
```

### The Central Discovery of the Mackenzie Gate:
1. **Power Energization Is Not the Binding Hazard:** Mackenzie is not a greenfield construction project awaiting utility energization. IREN’s Mackenzie site has been energized and operating at ~80 MW of data center capacity since **April 2022** (disclosed in SEC Form 10-K filings for fiscal years 2022–2026). The site owns its 11-acre freehold land, substation, and grid interconnect. The physical hazard is **purely hardware logistics, cluster deployment, and customer acceptance qualification testing**.
2. **Committed Capacity vs. Drawn Debt:** The August 25, 2026 financing agreements establish up to **$2.4B of committed financing capacity**, not $2.4B of funded debt. Borrowings are drawn *in stages* upon customer acceptance of hardware. Undrawn principal bears **zero 9.0% coupon interest** (facility and commitment fees remain unobserved in the public summary).
3. **The Availability Window Cliff:** Financing is strictly available from signing (August 25, 2026) through **December 31, 2026** (a 128-day window). Any equipment not delivered and customer-accepted by December 31, 2026 permanently loses facility draw eligibility, creating a **replacement-funding requirement** for unfinanced hardware capex.
4. **Dynamic Tranche Maturities:** Borrowings mature **30 months from the relevant funding date** of each individual draw. Delays in draws do not consume loan maturity; rather, each draw initializes its own independent 30-month maturity clock.

---

## 2. IREN Mackenzie 10-Dimension Data-Sufficiency Audit

We audit public evidence availability for IREN Mackenzie under the observatory's two-field epistemic standard (`source_status` and `model_treatment`), drawing directly from primary SEC Form 10-K disclosures (filed August 28, 2026 for fiscal year ended June 30, 2026):

| # | Dimension | Empirical Disclosed Value / Term | `source_status` | `model_treatment` | Generalization & Portability Assessment |
| :-: | :--- | :--- | :---: | :---: | :--- |
| **1** | **Exact Debt Principal / Facilities** | **Up to $2.4B** total facility capacity, split pro rata 50/50:<br>• **~$1.2B MFSA** (Master Financing and Security Agreement) with Blue Owl Capital Corporation (`OBDC`) as Admin, Collateral, and Intercreditor Agent + syndicated lenders<br>• **~$1.2B Senior Notes** with PIMCO (Pacific Investment Management Company LLC as adviser to purchasers) and OBDC as Note Agent | `PRIMARY_DISCLOSED` (Form 10-K Note 24) | `EXACT` (Committed Facility Capacity: $2.4B) / `POINT_IN_TIME` (Drawn Principal: unknown point-in-time draw, $\le \$2.4\text{B}$) | **Facility Capacity vs. Drawn Debt:** Clear contractual distinction between committed facility capacity ($2.4B) and drawn debt. It must NEVER be modeled as $2.4B active funded debt at inception. Undrawn principal bears no 9.0% interest; commitment fee terms are unobserved. |
| **2** | **Rate & Payment Dates** | Fixed **9.0% per annum** across both the MFSA borrowings and the Senior Notes; payment/reset frequency unstated | `PRIMARY_DISCLOSED` (Form 10-K Note 24) | `EXACT` (9.0% Fixed Rate) / `CONDITIONAL` (Payment Cycle: monthly/quarterly/semi-annual) | **Zero Floating Benchmark Risk:** Fixed 9.0% interest rate eliminates benchmark interest rate volatility (unlike Jupiter's floating SOFR exposure). Payment frequency is not assumed to be monthly; it remains conditional pending Form 10-Q exhibits. |
| **3** | **Amortization / Maturity Rules** | Staged tranches mature **30 months after the relevant funding date** of that specific draw. Principal amortizes in accordance with applicable amortization schedules. | `PRIMARY_DISCLOSED` (Form 10-K Note 24) | `EXACT` (30-month tranche maturity clock tied to draw date) | **Dynamic Tranche Maturities:** Unlike PF1's static 2030/2031 bullet dates or Jupiter's 4-year term, each draw creates its own independent 30-month maturity clock: $$T_{\text{maturity}}^{(k)} = T_{\text{draw}}^{(k)} + 30\text{ months}$$ Delays in draws do NOT consume the maturity of undrawn amounts. |
| **4** | **Reserve Accounts** | Debt Service Reserve Account (DSRA) or capitalized interest reserve terms are unstated in Note 24 summary. | `UNOBSERVED` (Private exhibits) | `UNOBSERVED / CONDITIONAL` | **Liquidity Shield Unobserved:** No dedicated DSRA is mentioned in the public summary. DSRA status remains strictly `UNOBSERVED` (not implicitly assumed $0 without exhibit verification). |
| **5** | **Revenue / Commercial Offtake Mechanics** | Commercial revenue generated through AI Cloud Services customer contracts as GPU compute clusters achieve Ready-for-Service (`RFS`) and pass customer acceptance testing. | `PRIMARY_DISCLOSED` (Business & Risk Factors) | `CONDITIONAL` (Unit revenue $/GPU-hour or $/MW-month) | **Linear / Staged Revenue Step-Up:** Revenue scales cluster-by-cluster with equipment acceptance, rather than switching on as a single monolithic facility commercial operation date. |
| **6** | **Equipment Acceptance & Funding Draw Conditionality** | Staged borrowings require formal customer acceptance:<br>*"Upon acceptance of the relevant equipment the Borrower will submit a funding request pursuant to which it will borrow under the MFSA and issue Notes under the Note Purchase Agreement on a pro-rata basis."*<br>Availability Period: August 25, 2026 to **December 31, 2026**. | `PRIMARY_DISCLOSED` (Form 10-K Note 24) | `EXACT` (Causal conditionality: Delivery $\to$ Acceptance $\to$ Funding Request $\to$ Draw; Hard cliff: Dec 31, 2026) | **The Central Synchronization Mechanism:** Borrowings are conditioned on physical customer acceptance testing. Protects the borrower from debt-service drag during equipment shipment, but creates a hard 128-day availability window ending December 31, 2026. |
| **7** | **Construction Cash & Equipment Procurement Outlays** | Financed equipment consists of GPU servers and ancillary equipment located at the Mackenzie facility, expected to take delivery in stages through December 31, 2026. | `PRIMARY_DISCLOSED` (Asset class: GPUs) / `UNOBSERVED` (Vendor payment schedule) | `INTERVAL` (Staged GPU delivery schedule) | **Procurement Capital at Risk:** If delivery or customer acceptance slips past December 31, 2026, the borrower cannot draw on the facility to fund the hardware, creating a replacement-funding requirement. |
| **8** | **Sponsor Support / Recourse Structure** | Parent company `IREN Limited` entered into an **unconditional payment guaranty** in favor of the Collateral Agent:<br>• **Limited to Payment Only:** Guarantees payment obligations of the Borrower; does *not* guarantee performance of other obligations.<br>• **Zero Maintenance Covenants:** No financial maintenance covenants on IREN Limited.<br>• **Zero Parent Asset Liens:** IREN Limited has *not* granted any security interest in any of its parent assets (only the financed equipment at Mackenzie is pledged). | `PRIMARY_DISCLOSED` (Form 10-K Note 24) | `EXACT` (Parent payment guaranty, no maintenance covenants, no parent asset liens) | **Clean Recourse Specification:** Exceptional contractual clarity. Unlike Applied Digital's completion guarantees (which fund capex cost overruns) or Jupiter's private JV terms, IREN Limited provides an unconditional payment guaranty with zero parent asset encumbrance. |
| **9** | **Physical Milestone Gating Cash Flow** | **GPU hardware delivery, cluster commissioning, and customer acceptance testing.**<br>Note: Utility energization is **100% complete** (operating at ~80 MW since April 2022). | `PRIMARY_DISCLOSED` (Form 10-K 2022–2026 filings) | `EXACT` (Physical risk dimension: GPU acceptance testing, NOT power energization) | **Physical Decoupling from Grid Risk:** Decisively refutes the assumption that all AI infrastructure stress is utility substation energization delay. Here, the grid interconnect is historical; the physical bottleneck is hardware logistics and qualification. |
| **10** | **Payment or Suspension Outcome upon Failure / Default Boundary** | • **Pre-Cliff Delay:** Equipment unaccepted $\to$ zero debt drawn $\to$ zero 9.0% debt service liability.<br>• **Cliff Boundary:** Post-Dec 31, 2026 unaccepted equipment permanently loses loan eligibility $\to$ creates replacement-funding requirement (mitigated by customer prepayments and liquidity).<br>• **Post-Draw Default:** Funded debt service missed $\to$ parent guaranty called $\to$ collateral agent forecloses on GPU hardware. | `PRIMARY_DISCLOSED` (Contract terms) / `DETERMINISTIC_MECHANIC` (Boundary logic) | `EXACT` (Availability cliff creates replacement-funding requirement; post-draw default triggers parent guaranty and equipment repossession) | **Availability Window Cliff Boundary:** Establishes a completely distinct failure topology: failure to meet a physical milestone does not trigger debt default, but causes **loss of committed debt financing**, creating a capital replacement requirement. |

---

## 3. Testing PF1's 5 Core Modeling Objects Against IREN Mackenzie

To verify whether the observatory's core abstractions generalize across diverse infrastructure archetypes, we map the 5 abstract modeling objects directly to IREN Mackenzie:

```
                            [The 5 Abstract Modeling Objects]
                                            │
        ┌───────────────────┬───────────────┴───────────────┬───────────────────┐
        ▼                   ▼                               ▼                   ▼
1. Segregated Financial 2. Physical-Commercial      3. Contractual       4. Contractual Cash-Flow   5. Absorbing
   Liquidity States        Milestone Clocks            Payment Grid         & Protection States        Shortfall Boundary
```

### Object 1: Segregated Financial Liquidity States
- **PF1 Implementation:** `AccountState(construction_cash, dsra_cash, operating_cash)`.
- **Mackenzie Generalization:**
  $$\text{FinancialState} = \{\text{CommittedFacilityCapacity}(t),\; \text{FundedDebtPrincipal}(t),\; \text{AvailableAlternativeLiquidity}(t)\}$$
  - $\text{CommittedFacilityCapacity}(t)$: Up to $2.4B total capacity available during the Availability Period ($t \le \text{Dec 31, 2026}$). Drains either through conversion into funded debt or through cliff expiration on December 31, 2026.
  - $\text{FundedDebtPrincipal}(t)$: Cumulative drawn tranches $\sum P_k$. Carries active 9.0% debt service.
  - $\text{AvailableAlternativeLiquidity}(t)$: Corporate liquidity, customer prepayments, and operating cash flows of `IREN Limited` available to absorb replacement funding if the availability window closes.
- **Audit Verdict: CLEAN STRUCTURAL GENERALIZATION.** The state vector cleanly tracks committed capacity vs. active debt principal.

### Object 2: Physical-Commercial Milestone Clocks
- **PF1 Implementation:** Scalar schedule delay $\Delta t$ shifting substation energization and commercial operations.
- **Mackenzie Generalization:**
  - Physical power energization is fully solved (80 MW operational since April 2022).
  - The operative physical clock is the **staged delivery and qualification trajectory of GPU clusters**:
    $$\text{GPU Delivery Manifest} \longrightarrow \text{Rack & Stack Installation} \longrightarrow \text{Customer Acceptance Testing (RFS)}$$
    $$\text{AcceptedCapacity}(t) \in [0,\; \text{Total Cluster MW}]$$
  - The physical milestone clock governs the **timing and magnitude of funding draw eligibility**:
    $$P_{\text{draw\_eligible}}(t) = f\left(\text{AcceptedEquipment}(t)\right)$$
- **Audit Verdict: ESSENTIAL ABSTRACTION EXPANSION.** Demonstrates that physical clocks in the observatory must support typed physical dimensions: `utility_load_online_mw`, `service_ready_it_mw`, `gpu_equipment_accepted_units`, and `gpu_compute_operational_mw`.

### Object 3: Contractual Payment Calendar
- **PF1 Implementation:** Semiannual fixed payment dates (Months 6, 12, 18...) with fixed bullet maturities (2030, 2031).
- **Mackenzie Generalization:**
  - Fixed **9.0% annual interest rate** across all tranches; payment cycle frequency is unobserved pending Form 10-Q exhibits.
  - **Dynamic, Tranche-Specific Maturity Clocks:** Each tranche $k$ drawn at date $t_k$ creates an independent debt service schedule:
    $$\text{InterestDue}_k(t) = P_k \times \frac{9.0\%}{\text{PaymentsPerYear}} \quad \text{for } t \in [t_k,\; t_k + 30\text{ months}]$$
    $$\text{TrancheMaturity}_k = t_k + 30\text{ months}$$
  - Schedule slippage prior to draw does *not* consume loan maturity. Undrawn principal has no active maturity clock.
- **Audit Verdict: CLEAN PARAMETERIZATION EXTENSION.** The payment grid engine naturally accommodates dynamic tranche inception dates and 30-month loan tenors.

### Object 4: Contractual Cash-Flow & Protection States
- **PF1 Implementation:** Binary rent step-up ($R=0 \to R>0$); parent completion guarantee funds construction cash shortfalls.
- **Mackenzie Generalization:**
  - **The Equipment Acceptance Shield:** Staged draw conditionality acts as a contractual shield for the project:
    $$\text{Undrawn Commitment} \xrightarrow{\text{Acceptance Condition}} \text{Funded Debt}$$
    The SPV bears zero 9.0% interest liability for equipment delayed in manufacturing, transit, or customs (commitment fees unobserved).
  - **The Availability Expiration Cliff:**
    $$\text{AvailableCommitment}(t) = \begin{cases} \$2.4\text{B} - \sum_{k} P_k, & t \le \text{Dec 31, 2026} \\ 0, & t > \text{Dec 31, 2026} \end{cases}$$
    On December 31, 2026, any undrawn commitment permanently vanishes.
- **Audit Verdict: CLEAN STRUCTURAL GENERALIZATION.** Expands the protection state library to include staged acceptance conditionality and availability window expiration.

### Object 5: Absorbing Shortfall Boundary
- **PF1 Implementation:** Unfunded coupon shortfall triggers `POST_SHORTFALL_ABSORBED`, censoring unmodeled post-default continuation.
- **Mackenzie Generalization:**
  - Mackenzie features **two distinct, ordered boundaries**:
    1. **Boundary A: The Availability Expiration Boundary ($t = \text{Dec 31, 2026}$):** An absorbing boundary for the credit facility. Undrawn commitments cannot be reinstated. Unfinanced capex becomes a replacement-funding requirement.
    2. **Boundary B: The Debt Payment Shortfall Boundary:** If funded GPU cash flows are insufficient to pay 9.0% debt service on drawn tranches, the parent payment guaranty is triggered. If IREN Limited fails to pay, lenders foreclose on the GPU collateral.
- **Audit Verdict: CLEAN CONCEPTUAL GENERALIZATION.** Reaffirms the necessity of absorbing boundaries, distinguishing between facility expiration boundaries (capital replacement) and debt default boundaries (payment shortfall).

---

## 4. Mathematical Comparison of the Three Risk Topologies

The structural comparison reveals three completely distinct topologies of infrastructure financial stress:

```
[PF1: Construction Capex Reconvergence]     [Jupiter: Offtake Dispute & Carry]       [Mackenzie: Availability Window Cliff]
───────────────────────────────────────     ──────────────────────────────────       ──────────────────────────────────────
        [Silo 1]       [Silo 2]                  [NMSLO Gas Pipeline ROW Denial]                 [GPU Supply Chain / Testing]
            │              │                                    │                                             │
            │ (Capex       │ (Capex                             ▼                                             ▼
            │  Deficit)    │  Deficit)            [Route Impairment & Fuel Risk]             [Acceptance Clock vs Dec 31 Cliff]
            ▼              ▼                                    │                                             │
   [Applied Digital Parent Support]                             ▼                             ┌───────────────┴───────────────┐
   (Absorbs construction shortfalls;              [Oracle Force-Majeure Notice]               ▼                               ▼
    debt default is independent)                  (Disputes rent step-up timing;      [Accepted by Dec 31]         [Unaccepted at Dec 31]
                                                   extends development carry)                 │                               │
                                                                │                             ▼                               ▼
                                                        ┌───────┴───────┐             [Draws 9% Debt]               [Draw Eligibility Lost]
                                                        ▼               ▼             (30-Mo Maturity)              (Replacement Funding
                                                   [Dev Carry]    [Debt Liquidity]                                   Requirement)
                                                   (Up to 3-yr)   (Trades @ 89-91c)
```

1. **Polaris Forge 1 (`PF1`):** Debt is fully funded at inception ($3.94B notes issued up-front). Delay burns interest reserves and construction cash. The primary stress is **construction cost shortfall reconvergence onto parent balance sheet** and coupon date cliffs.
2. **Project Jupiter:** Debt is syndication-committed (~$18.0B). Delay stems from **regulatory right-of-way permitting for fuel infrastructure**. Stress transmits through **commercial contract disputes** (force majeure modifying development carry vs. operational rent) and secondary loan pricing discounts.
3. **IREN Mackenzie:** Debt is available as a staged draw facility (up to $2.4B). Power infrastructure is 100% operational. Stress stems from **hardware qualification synchronization against a calendar expiration cliff** (December 31, 2026), threatening loss of committed debt capital rather than interest reserve depletion.

---

## 5. The Tri-Project Clock-Collision Detector Matrix

Synthesizing the three projects into the Clock-Collision Detector framework:

| Clock Dimension | Polaris Forge 1 (`PF1`) | Project Jupiter | IREN Mackenzie |
| :--- | :--- | :--- | :--- |
| **Physical Clock** | Substation civil works $\to$ utility interconnect (MDU 350 MW incremental) | Gas pipeline ROW (0.6-mile state land) $\to$ Bloom fuel cells | GPU server logistics $\to$ cluster install $\to$ customer acceptance |
| **Contract Clock** | Phased lease commencement per 100 MW building | Offtake state: development carry $\to$ FM carry $\to$ operational rent | Equipment acceptance window (Aug 25, 2026 $\to$ Dec 31, 2026) |
| **Financial Clock** | Lumpy semiannual coupon payment dates (Months 6, 12, 18...) | Floating SOFR + 250 bps carry; 4-yr maturity / 2-yr extension | **Hard December 31, 2026 Facility Availability Expiration Cliff** |
| **Support Clock** | Parent completion guarantee (Applied Digital) | Sponsor support terms unobserved in public record | Unconditional parent payment guaranty (IREN Limited) |
| **Binding Collision Question** | *Does utility energization occur before debt service reserves drain to zero?* | *Does pipeline permitting delay exceed the 3-year tenant carry obligation?* | *Does customer acceptance complete before the December 31, 2026 availability cliff?* |
| **Observable Leading Signal** | Utility interconnection dockets (MDU, Otter Tail Power) | State Land Office permit denial orders & public land commission dockets | Shipping manifests, customer acceptance logs, Form 10-Q draw exhibits |
| **Documented Lead Time** | **`MONITORING_WINDOW`**: 90–180 calendar days | **`OBSERVED`**: 65 days (permit $\to$ loan stress), 71 days (permit $\to$ FM) | **`MONITORING_WINDOW`**: 30–60 calendar days preceding cliff |

---

## 6. Generalization Gate Verdict & Conclusion

### Epistemic Verdict:
$$\mathbf{TRI\text{-}PROJECT\ STRUCTURAL\ PORTABILITY\ DEMONSTRATED.}$$
$$\mathbf{STRUCTURAL\ GENERALIZATION\ SUPPORTED\ ACROSS\ THREE\ CASE\text{-}STUDY\ ARCHETYPES.}$$

### Core Findings & Epistemic Rules:
1. **The Shared State-Machine Survives:**
   $$\boxed{\text{Physical State} + \text{Contract State} + \text{Liquidity State} + \text{Financing Clock}}$$
   successfully maps all three archetypes without bespoke hacks:
   - **PF1:** Fixed project notes, utility grid energization, binary rent step-up, parent capex guarantee.
   - **Jupiter:** Syndicated construction bank debt, fuel pipeline permitting, multi-state offtake carry, force-majeure defense.
   - **Mackenzie:** Staged equipment financing, hardware acceptance testing, dynamic tranche tenors, availability expiration cliff.
2. **Empirical Discipline for Mackenzie Modeling:**
   - We **will not model** Mackenzie as an active $2.4B funded debt liability at inception.
   - We **will not model** Mackenzie as facing electric power energization risk.
   - We **will strictly track** drawn principal $\sum P_k$ as a point-in-time state variable disclosed in subsequent SEC filings (Form 10-Q for quarter ended September 30, 2026).
3. **The Minimal Date Boundary Calculator:**
   Rather than producing synthetic equity calls or dollar predictions, the subordinate calculator for Mackenzie evaluates date slack:
   $$\text{AcceptanceSlackDays} = \text{Dec 31, 2026} - T_{\text{acceptance}}$$
   - If $\text{AcceptanceSlackDays} \ge 0$: Acceptance occurs prior to cliff (on track).
   - If $\text{AcceptanceSlackDays} < 0$: Financial availability boundary precedes acceptance by $|\text{AcceptanceSlackDays}|$ days.
   - If explicit accepted-equipment value / remaining eligible financing is later disclosed, it calculates $\text{FinancingCapacityAtRisk}$, establishing a replacement-funding requirement.
