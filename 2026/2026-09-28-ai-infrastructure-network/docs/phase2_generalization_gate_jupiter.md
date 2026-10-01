# Phase 2.2 Generalization Gate: Project Jupiter Data-Sufficiency & Abstraction Audit

**Document ID:** GATE-PHASE2-GENERALIZATION-JUPITER  
**Status:** Certified Epistemic Audit & Comparative Architectural Gate  
**Reference Commit:** [`401193d`](https://github.com/admiralorbiter/computational-sketchbook/commit/401193d)  
**Date:** September 30, 2026  
**Projects Compared:**  
1. **Polaris Forge 1 (PF1):** $3.94B Dual-Silo 144A Project Notes (Ellendale, ND)  
2. **Project Jupiter:** ~$18.0B Syndicated Construction Loan & Microgrid (Santa Teresa, NM)  
3. **IREN Mackenzie (Preview):** Up-to-$2.4B Staged GPU Equipment Financing (Mackenzie, BC)  

---

## 1. Executive Summary & The Falsification Challenge

Phase 2.1 successfully proved and froze the deterministic milestone surface architecture for Polaris Forge 1 (`PF1`). However, building a successful model on a single project carries an inherent epistemic risk: **overfitting the conceptual architecture to the idiosyncratic legal and capital structure of that project**.

To determine whether the Computational Observatory has uncovered a **general theory of infrastructure-finance synchronization** or merely built a specialized "PF1 calculator," Phase 2.2 executes a rigorous **Generalization Gate**.

Rather than testing Polaris Forge 2 (`PF2`)—which shares Applied Digital, bankruptcy-remote note silos, DSRAs, and similar parent completion guarantees—we test **Project Jupiter** as the primary out-of-sample falsification target.

```
                    [The Synchronization Dilemma: Cross-Project Comparison]

       Project 1: Polaris Forge 1                       Project 2: Project Jupiter
─────────────────────────────────────────      ─────────────────────────────────────────
Capital:    $3.94B Dual-Silo Fixed Notes       Capital:    ~$18.0B Syndicated Floating Loan
Physical:   Electric Grid Substation           Physical:   Bloom Fuel Cells + Gas Pipeline ROW
Clock 1:    Civil / Shell Construction         Clock 1:    State Land Regulatory Permitting
Clock 2:    Utility Energization (MDU)         Clock 2:    Pipeline ROW -> Fuel Availability
Offtake:    Post-Commencement Cash Rent        Offtake:    Pre-Energization Standby Carry
Legal Key:  Parent Completion Guarantee        Legal Key:  Tenant Force-Majeure Defense
Sponsor:    Applied Digital Corporation        Sponsors:   STACK Infrastructure / Blue Owl
Real Shock: Synthetic Delay Permutations       Real Shock: Documented July 2026 Permitting Denial
```

### The Core Research Question:
> **Does the same synchronization framework explain Jupiter when the operative clocks are:**
> $$\text{Gas Pipeline Permitting (NMSLO)} \longrightarrow \text{Physical Fuel Availability} \longrightarrow \text{Tenant Force-Majeure Defense} \longrightarrow \text{Construction Debt Carry} \longrightarrow \text{Sponsor / Syndicate Exposure}$$
> **rather than PF1's:**
> $$\text{Construction Burn} \longrightarrow \text{Commencement} \longrightarrow \text{Tenant Rent} \longrightarrow \text{State-Dependent Amortization} \longrightarrow \text{DSRA / Completion Support}?$$

---

## 2. Project Jupiter 10-Dimension Data-Sufficiency Audit

Before adapting or extending engine code, we audit public evidence availability for Project Jupiter under the observatory's two-field epistemic standard (`source_status` and `model_treatment`):

| # | Dimension | Empirical Value / Parameter in Repo Corpus | `source_status` | `model_treatment` | Generalization & Portability Assessment |
| :-: | :--- | :--- | :---: | :---: | :--- |
| **1** | **Exact Debt Principal / Facilities** | **~$18.0B** aggregate syndicated construction debt facility (`OBL-JUPITER-CONSTRUCTION-DEBT`) | `MARKET / FINANCIAL_PRESS` | `INTERVAL` | **Partially Disclosed:** Reported by Reuters/FT on Sept 18, 2026; individual bank/private credit tranche commitments are unfiled on EDGAR (unlike PF1's exact $2.35B and $1.59B 144A indentures). Requires interval parameterization around $18B. |
| **2** | **Rate & Payment Dates** | Benchmark: `FLOATING_SOFR_MARGIN` (~8.25% initial estimate: ~5.25% SOFR + 300 bps); monthly/quarterly payment cycle | `UNOBSERVED` | `CONDITIONAL` | **Floating Benchmark Exposure:** Unlike PF1's fixed 9.25% and 7.00% coupons, Jupiter's debt carry fluctuates with SOFR. Monthly/quarterly cycles require standard frequency parameterization. |
| **3** | **Amortization / Maturity Rules** | Construction-period interest-only; conversion to permanent term financing gated upon Commercial Operations Date (COD); ~5-year facility term (2024–2029) | `UNOBSERVED` | `CONDITIONAL` | **Milestone Conversion Gating:** No contractual amortization schedule is active during construction; the critical financial event is the *conversion milestone* to permanent financing. Failure to reach COD triggers maturity extensions or syndication distress. |
| **4** | **Reserve Accounts** | Construction Interest Reserve funded out of facility proceeds; post-completion DSRA unstated | `UNOBSERVED` | `CONDITIONAL` | **Standard Construction Mechanic:** Construction facilities rely on capitalized interest reserves rather than operating cash flow. Sizing requires conditional surface treatment. |
| **5** | **Rent / Lease Commencement Mechanics** | Anchor tenant colocation lease (`OBL-ORCL-JUPITER-LEASE`) for up to 2,450 MW; facility-specific rent unstated | `PRIMARY_DISCLOSED` (Parent) / `UNOBSERVED` (Facility) | `CONDITIONAL` | **Stated Amount Unstated at t_0:** Parent Oracle Form 10-K discloses $13.309B company-wide power commitments, but does not isolate Jupiter. Rent commencement is strictly gated by power availability. |
| **6** | **Force-Majeure Rent Suspension Mechanics** | Formal force-majeure notice issued Sept 24, 2026 citing NMSLO gas pipeline permit denial to suspend pre-energization rent and standby liabilities | `PRIMARY_DISCLOSED` (Post-Event Press) | `EXACT` (Event) / `CONDITIONAL` (Clause) | **Operative Legal Shield:** Oracle exercised a contractual defense to halt cash outflow. Disclosed in post-event reporting; specific contract language remains confidential. |
| **7** | **Construction Cash & Remaining Capex** | Multi-gigawatt development budget across 1,400 acres; monthly burn rate unstated in public filings | `UNOBSERVED` | `ANALYST_SCENARIO` | **Scenario Bounded:** Similar to PF1, remaining capex burn is an analyst scenario parameter, not a certified EDGAR disclosure. |
| **8** | **Sponsor Support / Recourse** | Joint venture developers: `STACK_INFRA` (lead operator) and `BLUE_OWL` (co-sponsor/asset manager); `BORDERPLEX` regional partner | `PRIMARY_DISCLOSED` (Corporate) / `UNOBSERVED` (Recourse Terms) | `CONDITIONAL` | **Private Credit Recourse:** Construction loans are typically non-recourse to fund sponsors, but contain completion guarantees, equity commitment letters, or springing indemnities. |
| **9** | **Physical Milestone Gating Cash Flow** | **NMSLO Natural Gas Pipeline Right-of-Way (ROW) Permit Approval** feeding 2,450 MW Bloom Energy fuel-cell microgrid | `PRIMARY_DISCLOSED` (Regulatory Order) | `EXACT` | **Upstream Regulatory Choke-Point:** Denied by NMSLO on July 15, 2026. Without pipeline ROW, gas cannot flow; without gas, fuel cells cannot generate power; without power, tenant cannot accept facility. |
| **10** | **Payment or Suspension Outcome upon Failure** | Tenant cash inflows suspend via force majeure; debt interest carry continues accruing; loan trades at discount (89–91c); syndicate initiates conversion review | `PRIMARY_DISCLOSED` (Reporting) | `EXACT` | **Risk Redirection:** Unmitigated carrying costs shift from tenant onto SPV, sponsors, and lenders, demonstrating that legal shields redirect rather than eliminate capital carry. |

---

## 3. The Hard Abstraction Test: Testing PF1's 5 Core Objects against Jupiter

To determine whether the architecture generalizes without ad-hoc project-specific hacks, we map the 5 abstract objects defined in Phase 2.1 directly to Project Jupiter:

```
                            [The 5 Abstract Modeling Objects]
                                            │
        ┌───────────────────┬───────────────┴───────────────┬───────────────────┐
        ▼                   ▼                               ▼                   ▼
1. Isolated Cash     2. Physical-Commercial         3. Contractual       4. Protection /       5. Absorbing
   Accounts             Milestone Clocks               Payment Grid         Support Predicates    Shortfall Boundary
```

### Object 1: Isolated Cash Accounts
- **PF1 Implementation:** `AccountState(construction_cash, dsra_cash, operating_cash)`.
- **Project Jupiter Mapping:**
  - *Construction Facility Cash:* Capitalized disbursements from the ~$18.0B facility earmarked for physical equipment and civil works.
  - *Interest Reserve:* Capitalized loan balance reserved to pay monthly floating interest carry during construction.
  - *Operating Account:* Tenant cash rent proceeds (strictly zero prior to energization / suspended under force majeure).
- **Audit Verdict: CLEAN GENERALIZATION.** The tripartite segregation of construction cash, debt service reserve, and operating cash naturally represents Jupiter's SPV account structure without modifications.

### Object 2: Physical-Commercial Milestone Clocks
- **PF1 Implementation:** Scalar schedule delay $\Delta t$ shifting commercial commencement:
  $$T_{\text{commence}} = T_{\text{scheduled}} + \Delta t$$
- **Project Jupiter Mapping:**
  - In PF1, commencement represents electric utility substation energization and tenant fit-out.
  - In Jupiter, commencement is a **two-stage dependency chain**:
    $$\text{Regulatory ROW Approval} \longrightarrow \text{Pipeline Lateral Buildout} \longrightarrow \text{Fuel Cell Energization} \longrightarrow T_{\text{commence}}$$
  - The real-world delay was not a generic schedule slip, but an external regulatory permit denial by the New Mexico State Land Office on July 15, 2026.
- **Audit Verdict: STRUCTURAL GENERALIZATION REQUIRED.** While the Level 1 financial waterfall still receives a scalar commencement month $T_{\text{commence}}$, Level 2 (the state transition machine) cannot treat power as a monolithic state. It must support typed upstream regulatory/fuel dependencies:
  $$\text{PowerAvailable}(t) = \mathbf{1}_{\{\text{PipelineApproved}\}} \times \mathbf{1}_{\{\text{FuelCellsInstalled}\}}$$

### Object 3: Contractual Payment Calendar
- **PF1 Implementation:** Semiannual fixed payment dates (Months 6, 12, 18, 24...) with fixed coupon arithmetic.
- **Project Jupiter Mapping:**
  - Jupiter's debt stack is a syndicated commercial credit facility. These facilities operate on **monthly or quarterly interest cycles** pegged to floating benchmark rates (1M/3M Term SOFR + spread).
  - Debt service is not constant carry:
    $$\text{InterestDue}(t) = P_{\text{drawn}}(t) \times \frac{\text{SOFR}_t + \text{Margin}}{12}$$
- **Audit Verdict: PARAMETERIZATION EXTENSION (NO HACK REQUIRED).** The engine's `payment_frequency` parameter already supports monthly/quarterly cycles. Supporting floating benchmark legs requires passing a benchmark trajectory $\text{SOFR}_t$ (which the Phase 1 stress engine already implements).

### Object 4: Protection & Support Predicates (The Critical Divergence)
- **PF1 Implementation:** Sponsor completion guarantee funds construction cash shortfalls:
  $$\text{SupportRequired}(t) = \max\left(0,\; \text{Capex}(t) - C_{\text{construction}}(t-1)\right)$$
  Tenant rent is strictly positive post-commencement and zero pre-commencement.
- **Project Jupiter Mapping:**
  - In Jupiter, the offtake lease agreement between Oracle and the SPV contained **pre-energization standby carry obligations** that exposed the tenant to project carrying costs prior to full operations.
  - On September 24, 2026, Oracle invoked a **Force-Majeure Rent Suspension Predicate** ($\mathbf{1}_{\text{FM}}$):
    $$\text{TenantInflow}(t) = \begin{cases} R_{\text{standby}}(t), & \text{if } t < T_{\text{commence}} \text{ and } \neg \mathbf{1}_{\text{FM}}(t) \\ 0, & \text{if } \mathbf{1}_{\text{FM}}(t) = 1 \text{ (Force Majeure Asserted)} \\ R_{\text{operational}}(t), & \text{if } t \ge T_{\text{commence}} \end{cases}$$
  - When $\mathbf{1}_{\text{FM}}$ activates, the tenant cash inflow instantly collapses to zero.
  - The carrying burden of the ~$18.0B debt does not vanish; it redirects to the **Sponsor Equity Cure Predicate**:
    $$\text{SponsorCarrySupport}(t) = \max\left(0,\; \text{DebtServiceDue}(t) - \text{InterestReserve}(t-1)\right)$$
- **Audit Verdict: FUNDAMENTAL ARCHITECTURAL GENERALIZATION.** This is where PF1's implementation was project-specific! In PF1, sponsor support *only* funded construction capex shortfalls, and tenant rent had no force-majeure suspension clause. Jupiter proves that in large hyperscale contracts:
  1. Offtake contracts may require pre-commencement standby carry.
  2. Force-majeure clauses act as **tenant risk shields** that halt cash inflows.
  3. Sponsor support must be capable of funding *debt carry shortfalls* (equity cure) when tenant inflows are suspended, not merely construction capex.

### Object 5: Absorbing Shortfall Boundary
- **PF1 Implementation:** Silo enters `POST_SHORTFALL_ABSORBED` upon unfunded debt payment shortfall ($T_{\text{payment\_shortfall}}$), censoring subsequent unmodeled continuation support.
- **Project Jupiter Mapping:**
  - When Jupiter's interest reserve exhausts and tenant rent is suspended by force majeure, the SPV cannot service the ~$18.0B debt stack.
  - In reality, syndicated loans do not instantly liquidate; the debt traded down to 89–91 cents on the dollar, and lenders initiated syndicate portfolio reviews.
- **Audit Verdict: CLEAN GENERALIZATION (VALIDATED BY REAL-WORLD DATA).** The absorbing boundary concept holds with 100% empirical fidelity. Project Jupiter confirms that post-shortfall cash flows enter an unmodeled restructuring regime where debt trades at distressed discounts and syndicates negotiate restructuring terms.

---

## 4. Mathematical Comparison: Risk Reconvergence vs. Risk Redirection

The structural comparison between PF1 and Jupiter clarifies how contractual terms alter the topology of financial stress:

```
[PF1: Parent Support Reconvergence]             [Project Jupiter: Force-Majeure Risk Redirection]

        [Silo 1]       [Silo 2]                                    [NMSLO Permit Denial]
            │              │                                                 │
            │ (Capex       │ (Capex                                          ▼
            │  Deficit)    │  Deficit)                       [Physical Fuel Supply Blocked]
            ▼              ▼                                                 │
   [Applied Digital Parent Support]                                          ▼
   (Absorbs construction shortfalls;                         [Oracle Invokes Force Majeure]
    debt default is independent)                                             │
                                                     ┌───────────────────────┴───────────────────────┐
                                                     ▼                                               ▼
                                         [Tenant Cash Shielded]                          [SPV Cash Starved]
                                         (Rent & carry suspended)                    (Debt carry unpaid)
                                                                                             │
                                                                                             ▼
                                                                                 [Sponsors / Syndicate Bear Carry]
                                                                                 (Debt trades at 89-91c discount;
                                                                                  syndicate conversion review)
```

### The Analytical Formulation:
In PF1, the sponsor acts as a **unilateral liquidity injector** to complete construction. In Jupiter, legal protections act as a **risk redirector**:
$$\text{Risk Elimination} = 0$$
$$\text{Economic Carry Shock} = \Delta \text{TenantObligation} + \Delta \text{SPVDeficit} + \Delta \text{SponsorEquityCure} + \Delta \text{SyndicateDiscount} \equiv \text{Constant}$$

When Oracle asserts force majeure, $\Delta \text{TenantObligation} \to -\Delta \text{Carry}$. The conservation of capital carry dictates that the unmitigated carry cost must reappear as an equivalent liquidity drain on the project SPV, its equity sponsors (STACK / Blue Owl), or debt syndicate valuation discounts.

---

## 5. Tri-Project Generalization Matrix: PF1 vs. Jupiter vs. Mackenzie

To guide Phase 2.2 and subsequent expansions, we map the three core empirical projects across all structural and physical dimensions:

| Dimension | Polaris Forge 1 (`PF1`) | Project Jupiter | IREN Mackenzie (`Preview`) |
| :--- | :--- | :--- | :--- |
| **Asset Location** | Ellendale, North Dakota | Santa Teresa, New Mexico | Mackenzie, British Columbia |
| **Capital Stack** | $3.94B Dual-Silo 144A Fixed Notes ($2.35B @ 9.25%, $1.59B @ 7.00%) | ~$18.0B Syndicated Floating Credit Facility (SOFR + margin) | Up-to-$2.4B Staged Equipment Financing Facility |
| **Physical Infrastructure** | 400 MW campus; utility grid interconnect (MDU / Otter Tail Power) | 2,450 MW campus; behind-the-meter Bloom Energy fuel-cell microgrid | ~80 MW operating site retrofitted for staged high-density GPU deployment |
| **Operative Physical Clock** | Civil construction $\to$ utility substation energization $\to$ tenant commissioning | Natural gas pipeline ROW permitting (NMSLO) $\to$ gas delivery $\to$ fuel cells | Hardware procurement $\to$ GPU delivery $\to$ testing/acceptance $\to$ commercial deployment |
| **Gating Milestone** | Commercial Commencement Date per building | Fuel pipeline operational availability & microgrid energization | Pro-rata equipment acceptance testing by customer |
| **Contractual Revenue Clock** | Long-term colocation rent begins post-commencement | Colocation lease with pre-energization standby carry liability | GPU cloud revenue generated as equipment clusters are accepted |
| **Protective Legal Shield** | None on tenant side; parent completion guarantee on sponsor side | **Tenant Force-Majeure Clause** (suspends pre-energization carry) | Staged funding tied to equipment delivery (undrawn funds not at risk) |
| **Maturity / Cliff Hazard** | Fixed bullet maturities (Dec 2030 / June 2031); state-dependent Silo 2 amortization | Construction loan conversion milestone to permanent term debt | **Hard December 31, 2026 Facility Availability Window Expiration** |
| **Sponsor Support Structure** | Formal parent completion guarantees (Applied Digital) | Equity commitment letters / sponsor equity cures (STACK / Blue Owl) | Parent performance and payment guaranty (IREN) |
| **Observed Real-World Stress** | Construction schedule slippage; parent cash constraints | **July 15, 2026 NMSLO permit denial; Sept 18 debt discount (89-91c); Sept 24 force majeure** | Hardware delivery logistics and acceptance window synchronization |

---

## 6. Verdict on Generalization & Architectural Roadmap for Phase 2.2

### Verdict: **GENERALIZATION SUPPORTED (WITH 2 PARAMETER EXTENSIONS)**

The abstraction audit confirms that Project Jupiter does **not** require ad-hoc project-specific hacks. The underlying thesis holds:
> Hyperscale infrastructure finance is governed by the deterministic synchronization between physical availability milestones, contractual payment calendars, reserve runways, and legal risk-allocation clauses.

However, moving from PF1 to Jupiter requires formalizing **two generalized parameterizations** in the Phase 2 engine architecture:

1. **Generalized Upstream Gating Dependency (`GatingMechanism`):**
   - *PF1 Mode:* `electric_grid_substation` (direct schedule slippage).
   - *Jupiter Mode:* `fuel_pipeline_regulatory_permitting` (upstream state regulatory approval gates physical fuel delivery).

2. **Bilateral Offtake Risk Allocation (`OfftakeContractTerms`):**
   - *PF1 Mode:* Standard commercial rent starting post-commencement (`standby_carry = False`, `force_majeure_active = False`).
   - *Jupiter Mode:* Offtake with standby carry and force-majeure suspension:
     - Parameter: `pre_energization_carry_rate_usd`
     - Parameter: `force_majeure_invoked: bool`
     - Consequence: If invoked, tenant rent drops to zero, and debt service carries directly into the SPV interest reserve / sponsor equity cure waterfall.

### Recommended Implementation Roadmap:
1. **Phase 2.2 Stage A:** Formalize `JupiterDataSufficiency` specification and test Jupiter's debt-service carry vs. interest reserve runway under force-majeure rent suspension.
2. **Phase 2.2 Stage B:** Replicate the 5-node linear conduit discovered in Task 025.2 (`NMSLO -> FAC -> SPV -> ORCL -> SYNDICATE`) inside the Level 1 financial waterfall.
3. **Phase 2.2 Stage C (Mackenzie Gate):** Audit IREN Mackenzie's staged equipment financing and December 31, 2026 availability window cliff to complete the tri-project synchronization suite.
