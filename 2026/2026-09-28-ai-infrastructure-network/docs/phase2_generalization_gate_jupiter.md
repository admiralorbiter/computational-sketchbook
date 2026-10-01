# Phase 2.2 Generalization Gate: Project Jupiter Data-Sufficiency & Abstraction Audit

**Document ID:** GATE-PHASE2-GENERALIZATION-JUPITER  
**Status:** Certified Epistemic Audit & Comparative Architectural Gate  
**Reference Commit:** [`fe3b88e`](https://github.com/admiralorbiter/computational-sketchbook/commit/fe3b88e)  
**Date:** September 30, 2026  
**Projects Compared:**  
1. **Polaris Forge 1 (PF1):** $3.94B Dual-Silo 144A Project Notes (Ellendale, ND)  
2. **Project Jupiter:** ~$18.0B Syndicated Construction Loan & Microgrid (Santa Teresa, NM)  
3. **IREN Mackenzie (Preview):** Up-to-$2.4B Staged GPU Equipment Financing (Mackenzie, BC)  

---

## 1. Executive Summary & The Falsification Challenge

Phase 2.1 successfully proved and froze the deterministic milestone surface architecture for Polaris Forge 1 (`PF1`). However, building a successful model on a single project carries an inherent epistemic hazard: **overfitting the conceptual architecture to the idiosyncratic legal and capital structure of that project**.

To determine whether the Computational Observatory has uncovered a **general theory of infrastructure-finance synchronization** or merely built a specialized "PF1 calculator," Phase 2.2 executes a rigorous **Generalization Gate**.

Rather than testing Polaris Forge 2 (`PF2`)—which shares Applied Digital, bankruptcy-remote note silos, DSRAs, and similar parent completion guarantees—we test **Project Jupiter** as the primary out-of-sample falsification target.

```
                    [The Synchronization Dilemma: Cross-Project Comparison]

       Project 1: Polaris Forge 1                       Project 2: Project Jupiter
─────────────────────────────────────────      ─────────────────────────────────────────
Capital:    $3.94B Dual-Silo Fixed Notes       Capital:    ~$18.0B Syndicated Credit Stack
Physical:   Electric Grid Substation           Physical:   Bloom Fuel Cells + Gas Pipeline ROW
Clock 1:    Civil / Shell Construction         Clock 1:    State Land Regulatory Permitting
Clock 2:    Utility Energization (MDU)         Clock 2:    Pipeline ROW -> Fuel Availability
Offtake:    Post-Commencement Cash Rent        Offtake:    Multi-State Development Carry & Rent
Legal Key:  Parent Completion Guarantee        Legal Key:  Tenant Force-Majeure Defense
Sponsor:    Applied Digital Corporation        Sponsors:   STACK Infrastructure / Blue Owl
Real Shock: Synthetic Delay Permutations       Real Shock: Documented July 2026 Permitting Denial
```

### The Core Research Question:
> **Does the same synchronization framework explain Jupiter when the operative clocks are:**
> $$\text{Gas Pipeline Permitting (NMSLO)} \longrightarrow \text{Physical Fuel Availability} \longrightarrow \text{Offtake Cash-Flow State (FM)} \longrightarrow \text{Construction Debt Carry} \longrightarrow \text{Sponsor / Syndicate Exposure}$$
> **rather than PF1's:**
> $$\text{Construction Burn} \longrightarrow \text{Commencement} \longrightarrow \text{Tenant Rent} \longrightarrow \text{State-Dependent Amortization} \longrightarrow \text{DSRA / Completion Support}?$$

---

## 2. Project Jupiter 10-Dimension Data-Sufficiency Audit

Before writing engine code, we audit public evidence availability for Project Jupiter under the observatory's two-field epistemic standard (`source_status` and `model_treatment`):

| # | Dimension | Empirical Value / Parameter in Repo Corpus | `source_status` | `model_treatment` | Generalization & Portability Assessment |
| :-: | :--- | :--- | :---: | :---: | :--- |
| **1** | **Exact Debt Principal / Facilities** | **~$18.0B** aggregate syndicated construction debt facility (`OBL-JUPITER-CONSTRUCTION-DEBT`) | `MARKET / FINANCIAL_PRESS` | `INTERVAL` | **Partially Disclosed:** Reported by Reuters/FT on Sept 18, 2026; individual bank/private credit tranche commitments are unfiled on EDGAR (unlike PF1's exact $2.35B and $1.59B 144A indentures). Requires interval parameterization around $18B. |
| **2** | **Rate & Payment Dates** | Benchmark: `FLOATING_SOFR_MARGIN` (~8.25% initial modeled estimate: ~5.25% SOFR + 300 bps); monthly/quarterly payment cycle | `UNOBSERVED` | `ANALYST_SCENARIO` | **Analyst Modeled Assumption:** Unlike PF1's fixed 9.25% and 7.00% coupons, Jupiter's detailed facility credit agreement is unfiled on EDGAR. Rates and reset intervals in the repository are analyst scenario inputs, not certified contract terms. |
| **3** | **Amortization / Maturity Rules** | Construction-period interest-only; conversion to permanent term financing gated upon Commercial Operations Date (COD); ~5-year facility term (2024–2029) | `UNOBSERVED` | `ANALYST_SCENARIO` | **Milestone Conversion Gating:** No contractual amortization schedule is active during construction; conversion terms to permanent debt are confidential syndicate covenants rather than public facts. |
| **4** | **Reserve Accounts** | Construction Interest Reserve funded out of facility proceeds; post-completion DSRA unstated | `UNOBSERVED` | `CONDITIONAL` | **Standard Construction Mechanic:** Construction facilities rely on capitalized interest reserves rather than operating cash flow. Specific sizing is unobserved and requires conditional surface treatment. |
| **5** | **Rent / Lease Commencement Mechanics** | Anchor tenant colocation lease (`OBL-ORCL-JUPITER-LEASE`) for up to 2,450 MW; facility-specific rent unstated | `PRIMARY_DISCLOSED` (Parent) / `UNOBSERVED` (Facility) | `CONDITIONAL` | **Facility Stated Amount Unstated at $t_0$:** Parent Oracle Form 10-K discloses $13.309B company-wide power commitments, but does not break out Jupiter. Commercial rent commencement is gated by operational availability. |
| **6** | **Force-Majeure Rent Mechanics** | Formal notice issued Sept 24, 2026 citing NMSLO gas pipeline permit denial to defer higher operational rent and extend development-stage payments | `PRIMARY_DISCLOSED` (Post-Event Press) | `EXACT` (Event) / `CONDITIONAL` (Terms) | **Offtake State Modifier (Not Zero Cash):** Reuters reports Oracle sought to delay higher operational rent if targets are missed, extending lower development-stage rent. FT reports Oracle is obligated to cover project carry costs (interest + equity returns) for up to 3 years even without power. Blue Owl stated financial commitments remain unaltered. |
| **7** | **Construction Cash & Remaining Capex** | Multi-gigawatt development budget across 1,400 acres; monthly burn rate unstated in public filings | `UNOBSERVED` | `ANALYST_SCENARIO` | **Scenario Bounded:** Similar to PF1, remaining capex burn is an analyst scenario parameter, not a certified EDGAR disclosure. |
| **8** | **Sponsor Support / Recourse** | Joint venture developers: `STACK_INFRA` (lead operator) and `BLUE_OWL` (co-sponsor/asset manager); `BORDERPLEX` regional partner | `PRIMARY_DISCLOSED` (Corporate) / `UNOBSERVED` (Recourse Terms) | `CONDITIONAL` | **Private Credit Recourse:** Construction loans in digital infrastructure are typically limited recourse, backed by completion guarantees, equity commitment letters, or springing indemnities whose exact terms remain confidential. |
| **9** | **Physical Milestone Gating Cash Flow** | **NMSLO Natural Gas Pipeline Right-of-Way (ROW) Permitting** across 0.6-mile state land segment feeding 2,450 MW Bloom Energy microgrid | `PRIMARY_DISCLOSED` (Regulatory Order) | `EXACT` | **Route Impairment & Availability Risk:** Denied by NMSLO on July 15, 2026. Denies a 0.6-mile segment of a 17-mile pipeline route, creating route impairment, fuel availability risk, and commissioning uncertainty, while permitting potential rerouting or litigation. |
| **10** | **Payment or Suspension Outcome upon Failure** | Secondary debt trading under pressure at 89–91c (Sept 18 baseline); syndicate reviews conversion milestones; legal dispute over development carry vs operational rent | `PRIMARY_DISCLOSED` (Reporting) | `EXACT` | **Pre-Event Market Stress & Legal Dispute:** Debt discounting was already present on Sept 18 ($t_0$ baseline). No actual contractual payment shortfall or debt default has been empirically observed in the historical record. |

---

## 3. The Hard Abstraction Test: Testing PF1's 5 Core Objects against Jupiter

To determine whether the architecture generalizes without ad-hoc project-specific hacks, we map the 5 abstract objects defined in Phase 2.1 directly to Project Jupiter:

```
                            [The 5 Abstract Modeling Objects]
                                            │
        ┌───────────────────┬───────────────┴───────────────┬───────────────────┐
        ▼                   ▼                               ▼                   ▼
1. Isolated Cash     2. Physical-Commercial         3. Contractual       4. Contractual Cash-Flow   5. Absorbing
   Accounts             Milestone Clocks               Payment Grid         & Protection States        Shortfall Boundary
```

### Object 1: Isolated Cash Accounts
- **PF1 Implementation:** `AccountState(construction_cash, dsra_cash, operating_cash)`.
- **Project Jupiter Mapping:**
  - *Construction Facility Cash:* Capitalized disbursements from the ~$18.0B facility earmarked for physical equipment and civil works.
  - *Interest Reserve:* Capitalized loan balance reserved to service monthly floating interest carry during construction.
  - *Operating Account:* Tenant cash rent proceeds (distinguishing development carry from operational rent).
- **Audit Verdict: CLEAN GENERALIZATION.** The tripartite segregation of construction cash, debt service reserve, and operating cash naturally represents Jupiter's SPV account structure without modifications.

### Object 2: Physical-Commercial Milestone Clocks
- **PF1 Implementation:** Scalar schedule delay $\Delta t$ shifting commercial commencement:
  $$T_{\text{commence}} = T_{\text{scheduled}} + \Delta t$$
- **Project Jupiter Mapping:**
  - In PF1, commencement represents electric utility substation energization and tenant fit-out.
  - In Jupiter, commencement is subject to an **upstream regulatory permitting dependency**:
    $$\text{NMSLO 0.6-Mile Pipeline ROW Denial} \longrightarrow \text{Pipeline Route Impairment} \longrightarrow \text{Fuel Availability Risk} \longrightarrow T_{\text{commence}} \text{ at Risk}$$
  - The NMSLO denial affects a 0.6-mile segment of a 17-mile pipeline across state trust land. This does not represent an instantaneous fatal shutdown; it introduces route impairment, potential rerouting costs, regulatory litigation, and delivery schedule risk.
- **Audit Verdict: STRUCTURAL GENERALIZATION REQUIRED FOR LEVEL 2.** At Level 1, the downstream financial impact can still be explored across a parameterized schedule delay grid $\Delta t$. At Level 2, the hazard model must support typed regulatory route impairment rather than assuming monolithic utility energization.

### Object 3: Contractual Payment Calendar
- **PF1 Implementation:** Semiannual fixed payment dates (Months 6, 12, 18, 24...) with fixed coupon arithmetic.
- **Project Jupiter Mapping:**
  - Syndicated construction facilities typically operate on **monthly or quarterly interest cycles** pegged to floating benchmark rates (Term SOFR + spread).
  - Debt service is variable carry:
    $$\text{InterestDue}(t) = P_{\text{drawn}}(t) \times \frac{\text{SOFR}_t + \text{Margin}}{12}$$
  - **Epistemic Caution:** While `payment_frequency` supports monthly/quarterly cycles, the specific margin (e.g. 300 bps) and drawn balances are *analyst scenario inputs*, not certified contract facts.
- **Audit Verdict: PARAMETERIZATION EXTENSION (CONDITIONAL SCENARIO).** Moving from fixed coupons to floating benchmark debt carry is straightforward using the Phase 1 benchmark trajectory engine, but must be explicitly labeled as an analyst scenario rather than a literal contract extraction.

### Object 4: Contractual Cash-Flow & Protection States (The Fundamental Falsification Finding)
- **PF1 Implementation:** Binary on/off commercial cash flow:
  $$\text{TenantRent}(t) = \begin{cases} 0, & t < T_{\text{commence}} \\ R_{\text{operational}}, & t \ge T_{\text{commence}} \end{cases}$$
  Sponsor completion support strictly funds construction capex shortfalls.
- **Project Jupiter Mapping:**
  - In Jupiter, the offtake lease agreement between Oracle and the SPV features a **multi-state pre-operational cash-flow regime**.
  - **What Current Evidence Actually Discloses:**
    - Reuters reports that Oracle's force-majeure notice sought to delay higher payments if the project missed targets, **extending the period of lower development-stage rent**, rather than setting payments to zero.
    - Financial Times reports that Oracle is obligated under contract to cover project **carry costs** (including interest and equity returns) for up to three years even if the site lacks power.
    - Blue Owl publicly stated that the force-majeure notice does not alter the parties' financial commitments.
  - **The Generalized Mathematical Formulation:**
    Commercial cash flow is not a binary switch ($\text{FM} = 0/1 \implies \text{Rent} = 0$). It is a **contractual payment state transition**:
    $$\text{TenantPayment}_t = f\left(\text{development-stage payment},\; \text{operational rent},\; \text{carry obligation},\; \text{FM state}\right)$$
    $$\text{OfftakePaymentState} \in \{\text{development carry},\; \text{FM-adjusted carry},\; \text{operational rent}\}$$
- **Audit Verdict: ESSENTIAL GENERALIZATION DISCOVERY.** This confirms the value of the Generalization Gate as a falsification exercise. PF1's assumption that pre-commencement cash flow is zero and that force majeure eliminates cash flow does not hold. In sophisticated hyperscale project financings, offtake contracts define pre-operational carry regimes, and force-majeure notices dispute the timing and step-up between development-stage carry and full operational rent.

### Object 5: Absorbing Shortfall Boundary
- **PF1 Implementation:** Silo enters `POST_SHORTFALL_ABSORBED` upon unfunded debt payment shortfall ($T_{\text{payment\_shortfall}}$), censoring subsequent unmodeled continuation support.
- **Project Jupiter Mapping:**
  - The September 18 debt trading at 89–91 cents on the dollar was an established **pre-event baseline condition at $t_0$**, reflecting market syndication friction and power availability concerns prior to Oracle's September 24 notice.
  - There is **no observed event in the historical record** showing an actual contractual payment shortfall: interest reserves were not reported exhausted, scheduled debt service was not missed, and no loan acceleration or formal restructuring took place.
- **Audit Verdict: CLEAN CONCEPTUAL GENERALIZATION; NOT EMPIRICALLY TRIGGERED.** The absorbing boundary concept holds as an indispensable model constraint (preventing unmodeled post-default continuation), but it must be clearly stated that the observed Jupiter episode has **not** empirically triggered this boundary.

---

## 4. Mathematical Comparison: Risk Reconvergence vs. Risk Redirection

The structural comparison clarifies how contractual terms alter the topology of financial stress:

```
[PF1: Parent Support Reconvergence]             [Project Jupiter: Offtake Carry Dispute & Redirection]

        [Silo 1]       [Silo 2]                                    [NMSLO 0.6-Mile ROW Denial]
            │              │                                                 │
            │ (Capex       │ (Capex                                          ▼
            │  Deficit)    │  Deficit)                       [Route Impairment & Fuel Risk]
            ▼              ▼                                                 │
   [Applied Digital Parent Support]                                          ▼
   (Absorbs construction shortfalls;                         [Oracle Invokes Force Majeure]
    debt default is independent)                             (Disputes transition to higher
                                                              operational rent; seeks extended
                                                              development-stage carry)
                                                                             │
                                                     ┌───────────────────────┴───────────────────────┐
                                                     ▼                                               ▼
                                         [Tenant Development Cash]                       [SPV Carry Cash Flow]
                                         (Ongoing carry obligation                   (Debt service covered vs
                                          for up to 3 years)                          reserve drain depending on
                                                                                      dispute resolution)
                                                                                             │
                                                                                             ▼
                                                                                 [Lender Syndicate Pricing]
                                                                                 (Debt trades at 89-91c baseline;
                                                                                  conversion milestone review)
```

In PF1, the sponsor acts as a **unilateral liquidity injector** to fund remaining capex. In Jupiter, legal risk allocation determines **which cash-flow regime applies during physical delay**: whether the tenant continues paying full carry costs, extends development-stage payments, or whether an unresolved gap forces interest reserve depletion and sponsor equity cures.

---

## 5. Tri-Project Generalization Matrix: PF1 vs. Jupiter vs. Mackenzie

| Dimension | Polaris Forge 1 (`PF1`) | Project Jupiter | IREN Mackenzie (`Preview`) |
| :--- | :--- | :--- | :--- |
| **Asset Location** | Ellendale, North Dakota | Santa Teresa, New Mexico | Mackenzie, British Columbia |
| **Capital Stack** | $3.94B Dual-Silo 144A Fixed Notes ($2.35B @ 9.25%, $1.59B @ 7.00%) | ~$18.0B Syndicated Credit Facility (SOFR + margin; details unobserved) | Up-to-$2.4B Staged Equipment Financing Facility |
| **Physical Infrastructure** | 400 MW campus; utility grid interconnect (MDU) | 2,450 MW campus; Bloom Energy fuel-cell microgrid | ~80 MW operating site retrofitted for GPU clusters |
| **Operative Physical Clock** | Civil construction $\to$ substation energization $\to$ commissioning | Gas pipeline ROW permitting (NMSLO) $\to$ fuel delivery $\to$ fuel cells | Hardware procurement $\to$ GPU delivery $\to$ acceptance testing |
| **Gating Milestone** | Commercial Commencement Date per building | Fuel pipeline operational availability & microgrid energization | Pro-rata equipment acceptance testing by customer |
| **Contractual Revenue Clock** | Long-term colocation rent begins post-commencement | Multi-state: development carry $\to$ operational rent | GPU cloud revenue generated as equipment clusters are accepted |
| **Protective Legal Shield** | None on tenant side; parent completion guarantee on sponsor side | **Tenant Force-Majeure Clause** (disputes rent step-up / carry timing) | Staged funding tied to equipment delivery (undrawn funds not at risk) |
| **Maturity / Cliff Hazard** | Fixed bullet maturities (Dec 2030 / June 2031); state-dependent Silo 2 amortization | Construction loan conversion milestone to permanent term debt | **Hard December 31, 2026 Facility Availability Window Expiration** |
| **Sponsor Support Structure** | Formal parent completion guarantees (Applied Digital) | Private credit completion guarantees / equity commitment letters | Parent performance and payment guaranty (IREN) |
| **Observed Real-World Stress** | Construction schedule slippage; parent cash constraints | **July 15 NMSLO permit denial; Sept 18 debt discount (89-91c); Sept 24 force majeure** | Hardware delivery logistics and acceptance window synchronization |

---

## 6. Verdict on Generalization & Architectural Roadmap for Phase 2.2

### Revised Verdict:
$$\mathbf{STRUCTURAL\ GENERALIZATION\ SUPPORTED;}$$
$$\mathbf{JUPITER\text{-}SPECIFIC\ FINANCIAL\ PARAMETERIZATION\ NOT\ YET\ DATA\text{-}SUFFICIENT.}$$

### Findings of the Audit:
1. **The 5 Core Abstractions Generalize Structurally:**
   - Segregated financial state accounts
   - Physical/commercial milestone clocks
   - Contractual payment calendars
   - Contractual cash-flow and protection state transitions
   - Absorbing modeled-boundary semantics
2. **The Falsification Discovery:**
   - PF1's binary on/off commercial cash flow assumption does **not** generalize to complex hyperscale offtake agreements. Offtake contracts feature richer pre-operational payment regimes (`development carry`, `FM-adjusted carry`, `operational rent`).
3. **Epistemic Discipline:**
   - We **will not write** an ostensibly "contract-literal" `phase2_jupiter_engine.py` using synthetic assumptions masquerading as Jupiter loan facts.

### Next Bounded Task: Jupiter Contract-Mechanics Recovery Pass
Before any simulation code is written, execute a targeted investigative pass focused strictly on three empirical unknowns:
1. **Tenant Pre-Operational Obligations:** What exact payment obligations does Oracle bear prior to commercial operations, and what carry costs (interest, equity returns) are contractually mandated?
2. **The Force-Majeure Dispute Scope:** Exactly what payment obligations does the September 24 force-majeure notice seek to suspend or extend versus what remains payable?
3. **Syndicated Debt Terms:** What public SEC, municipal bond, or docket evidence exists for the ~$18.0B loan's actual benchmark margin, interest reset frequency, reserve structure, conversion covenants, and sponsor recourse?

If these parameters remain confidential in the public record, Jupiter Level 1 will be formulated explicitly as a **conditional mechanism surface**:
$$T_{\text{runway}} = f\left(R_{\text{interest reserve}},\; P_{\text{development carry}},\; P_{\text{FM-adjusted carry}},\; r_{\text{debt}},\; \Delta t\right)$$
mapping the sensitivity of debt carry to offtake dispute outcomes, maintaining the rigorous epistemic standard established in Phase 2.1.
