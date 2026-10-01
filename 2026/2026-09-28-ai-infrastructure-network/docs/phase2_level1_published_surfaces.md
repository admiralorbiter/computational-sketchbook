# Polaris Forge 1 (PF1) Level 1 Deterministic Milestone Surfaces & Parent Reconvergence

**Project:** Polaris Forge 1 (Ellendale, ND) — AI Hyperscale Data Center Campus  
**Issuers / Silos:** Silo 1 ($2.350B 9.25% Senior Notes due 2030) & Silo 2 ($1.590B 7.00% Senior Notes due 2031)  
**Parent Sponsor:** Applied Digital Corporation (`APLD`)  
**Engine Version:** Phase 2.1 Level 1 Deterministic Delay Engine (Cents-Safe Precision & Pre-Shortfall Calibration)  
**Git Branch / Commit:** `main` (Post-Calibration Release)  
**Test & Audit Status:** 25/25 unit tests passing (`src/test_phase2_level1.py`); Full repository consistency certified with 0.00% data drift (`src/validate.py`)  

---

## 1. Executive Summary

This report delivers the certified **Phase 2.1 Level 1 Published Delay-Tolerance Milestone Surfaces** for the Polaris Forge 1 hyperscale campus. Following the implementation of strict structural mechanics across Patches 2.1.1–2.1.4, this calibration pass resolves the sub-cent floating-point precision residue and establishes an uncontaminated pre-shortfall economic baseline for all published surfaces.

```
                    [Polaris Forge 1 Capital & Legal Structure]
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
     [Silo 1: APLD ComputeCo]                       [Silo 2: APLD ComputeCo 3]
  $2,350M 9.25% Notes (due Dec 2030)             $1,590M 7.00% Notes (due June 2031)
  Carrying Carry: $217.375M/yr                   Carrying Carry: $111.300M/yr
  Amort Rule: Dec 15, 2027 (Month 18)            Amort Rule: Post-Commencement (State-Dependent)
  Isolated Waterfall & DSRA                      Isolated Waterfall & DSRA
                 │                                               │
                 └───────────────────────┬───────────────────────┘
                                         ▼
                   [Campus Parent Support: Applied Digital]
                   Nov 20, 2025 & June 16, 2026 Completion Guarantees
                   Valid Pre-Shortfall Accumulation (Censored Post-Default)
```

### Key Precision & Empirical Breakthroughs Delivered:

1. **Cents-Safe Monetary Precision (`MONETARY_TOLERANCE_USD = 0.01`):**
   The Silo 2 semiannual coupon ($1.590\text{B} \times 7.00\% / 2 = \$55,650,000.00$) previously generated a 64-bit IEEE 754 floating-point residue of $\sim \$0.0000000075$ against an exact $\$55,650,000.00$ reserve. Enforcing strict monetary quantization (`round(..., 2)`) and cents thresholding (`unfunded_debt_service > MONETARY_TOLERANCE_USD`) ensures exact coupon exhaustion without premature default:
   - Under 6-Month Carry Reserve ($55.65M): Silo 2 now successfully services Month 6 coupon and defaults at Month 12 ($T_{\text{shortfall}} = 12$, previously 6).
   - Under 12-Month Carry Reserve ($111.30M): Silo 2 now services Month 6 and Month 12 coupons, defaulting at Month 18 ($T_{\text{shortfall}} = 18$, previously 12).

2. **Pre-Shortfall Calibration of Parent Support Surfaces:**
   With the timing of Silo 2's payment shortfall correctly calibrated, valid headline parent completion support is:
   - **Zero Reserve:** Both silos default on debt at Month 6 ($T_{\text{shortfall}} = 6$). Construction cash lasts past Month 6, so valid headline parent support is strictly **$0.0M** across all delays (unrestricted post-default continuation diagnostic is $\$215\text{M}–\$250\text{M}$).
   - **6-Month Carry Reserve ($164.3M total):** Both silos default at Month 12. Valid headline support is **$155.0M** at $\Delta t = 0$, and **$170.0M** at $\Delta t \ge 1$ month (unrestricted continuation is $\$215\text{M}–\$250\text{M}$; censorship correctly excludes $\$60\text{M}–\$80\text{M}$ of post-default capex).
   - **12-Month Carry Reserve ($328.7M total):** Both silos default at Month 18. Valid headline support is **$215.0M** at $\Delta t = 0$, **$230.0M** at $\Delta t = 1$, **$245.0M$** at $\Delta t = 2$, and plateaus at **$250.0M** for $\Delta t \ge 3$.

3. **Construction Budget Cap Saturation Finding:**
   In the 12-Month Carry Reserve scenario, cumulative parent support plateaus at **$250.0M** for all delays $\Delta t \ge 3$ months. This occurs because the total remaining capex budgets ($200.0M for Silo 1; $300.0M for Silo 2) are fully saturated ($100.0M initial cash + $100.0M support cap for Silo 1; $150.0M initial cash + $150.0M support cap for Silo 2). Hence, additional schedule slippage beyond 3 months cannot extract further completion funding under the contract cap. Reserve sizing and semiannual coupon payment dates strictly dominate construction delay.

4. **Uncontaminated Pre-Shortfall Amortization Offset (Panel D):**
   Evaluating the state-dependent amortization structural offset under a pre-shortfall liquidity-control scenario (fully solvent through Month 30 with zero arrears) reveals:
   - **Month 24 On-Time:** Owes **$282.79M** ($55.65M coupon + $227.14M principal installment).
   - **Month 24 Delayed 6 Months:** Owes **$55.65M** (coupon only; amortization deferred to Month 30).
   - **Immediate Cash Relief:** **-$227.14M (-80.3%)** exact pre-shortfall cash relief in Month 24.
   - **Month 30 Reversal:** On-time owes **$274.84M** (coupon on reduced balance of $1,362.86M + installment); Delayed begins amortization, owing **$282.79M** (coupon on full $1,590.00M balance + installment).

5. **Explicit Waterfall Priority Arrears Allocation:**
   Evaluating `opex_first` vs `debt_service_first` confirms identical milestone timing due to semiannual payment date lumpiness, but reveals radical divergence in arrears allocation:
   - Under `opex_first`, operating expenses are paid in full ($0 terminal arrears), while noteholder interest absorbs the shortfall ($264.7M Silo 1; $166.7M Silo 2 arrears).
   - Under `debt_service_first`, opex is starved: Silo 1 leaves $52.0M–$55.0M and Silo 2 leaves $60.0M in unpaid opex arrears (100% opex default), diverting facility operational cash to debt service and threatening physical facility shutdown.

---

## 2. Master Publication Visualizations

The calibrated milestone surfaces are rendered in the four-panel publication graphic below:

![Polaris Forge 1 Level 1 Milestone Surfaces](file:///C:/Users/admir/.gemini/antigravity/brain/8d764d06-cc09-4d5f-9c2e-fad2c5a4f555/phase2_delay_tolerance_surfaces.png)

*Figure 1: Calibrated Phase 2.1 Level 1 Milestone Surfaces for Polaris Forge 1 across 3 reserve tiers, independent milestone tracks, 2D decoupled delay matrix, and the uncontaminated pre-shortfall principal amortization offset.*

---

## 3. Four Published Surfaces & Calibrated Results

### Surface 1: Synchronized Delay Tolerance vs. Reserve Grid (Panel A)

Evaluated across 13 synchronized delay durations ($\Delta t \in [0, 24]$ months) for three reserve tiers:
- **Tier 1 (Zero Reserves):** $R_{0,1} = \$0$, $R_{0,2} = \$0$
- **Tier 2 (6-Month Carry Reserve):** $R_{0,1} = \$108.6875\text{M}$, $R_{0,2} = \$55.65\text{M}$ ($\$164.3375\text{M}$ campus total)
- **Tier 3 (12-Month Carry Reserve):** $R_{0,1} = \$217.375\text{M}$, $R_{0,2} = \$111.30\text{M}$ ($\$328.675\text{M}$ campus total)

| Reserve Tier | Delay ($\Delta t$) | $T_{\text{DSRA}, 1}$ | $T_{\text{DSRA}, 2}$ | $T_{\text{shortfall}, 1}$ | $T_{\text{shortfall}, 2}$ | Headline Parent Support (Pre-Shortfall) | Unrestricted Continuation (Diagnostic) | Censored Post-Default Outlay |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Zero Reserve** | 0 mo | None | None | 6 | 6 | **$0.0M** | $215.0M | $215.0M |
| **Zero Reserve** | 1 mo | None | None | 6 | 6 | **$0.0M** | $230.0M | $230.0M |
| **Zero Reserve** | 3 mo | None | None | 6 | 6 | **$0.0M** | $250.0M | $250.0M |
| **Zero Reserve** | 6–24 mo | None | None | 6 | 6 | **$0.0M** | $250.0M | $250.0M |
| **6-Month Carry** | 0 mo | 6 | 6 | 12 | 12 | **$155.0M** | $215.0M | $60.0M |
| **6-Month Carry** | 1 mo | 6 | 6 | 12 | 12 | **$170.0M** | $230.0M | $60.0M |
| **6-Month Carry** | 2 mo | 6 | 6 | 12 | 12 | **$170.0M** | $245.0M | $75.0M |
| **6-Month Carry** | 3–24 mo | 6 | 6 | 12 | 12 | **$170.0M** | $250.0M | $80.0M |
| **12-Month Carry** | 0 mo | 6 | 6 | 18 | 18 | **$215.0M** | $215.0M | $0.0M |
| **12-Month Carry** | 1 mo | 6 | 6 | 18 | 18 | **$230.0M** | $230.0M | $0.0M |
| **12-Month Carry** | 2 mo | 6 | 6 | 18 | 18 | **$245.0M** | $245.0M | $0.0M |
| **12-Month Carry** | 3–24 mo | 6 | 6 | 18 | 18 | **$250.0M** | $250.0M | $0.0M |

---

### Surface 2: Milestone Arrival Decoupling (Panel B)

Under the 6-Month Reserve Tier, the two operational tracks evolve independently:
- **Track B (Construction):** $T_{\text{completion\_support}}$ triggers at Month 7 for Silo 1 (as initial $100M cash depletes) and Month 8 for Silo 2 (as initial $150M cash depletes).
- **Track A (Debt Service):** $T_{\text{DSRA}}$ triggers at Month 6 (the first semiannual coupon payment date), while $T_{\text{payment\_shortfall}}$ arrives at Month 12 when the reserve balance reaches zero.
- **Track Decoupling:** Completion support timing is dictated solely by capex burn and initial construction cash, entirely decoupled from DSRA draws.

---

### Surface 3: 2D Decoupled Silo Delays ($\Delta t_1 \times \Delta t_2$) (Panel C)

Exploring independent delay combinations ($7 \times 7 = 49$ grid points):
- **When Silo 1 is On Time ($\Delta t_1 = 0$):** Total pre-shortfall campus support is strictly **$155.0M** across all Silo 2 delays ($\Delta t_2 \in [0, 24]$).
- **When Silo 1 is Delayed ($\Delta t_1 \ge 3$):** Total pre-shortfall campus support plateaus at **$170.0M** across all Silo 2 delays.
- **Silo Independence:** Because Silo 2 consumes its pre-shortfall capex budget by Month 12 regardless of additional delay, Silo 1's delay alone drives the step from $155.0M to $170.0M. Zero cross-silo subsidization exists.

---

### Surface 4: State-Dependent Principal Amortization Structural Offset (Panel D)

Evaluated under a pre-shortfall liquidity-control scenario (solvent through Month 30 with zero arrears) comparing on-time (Commencement Month 18) vs 6-month delay (Commencement Month 24):

```
Month 18: On-time commences commercial operations.
Month 24:
  - On-time owes: $55.65M coupon + $227.14M scheduled principal = $282.79M total debt service.
  - Delayed owes: $55.65M coupon + $0.00M scheduled principal = $55.65M total debt service.
  ==> NET PRE-SHORTFALL CASH RELIEF IN MONTH 24 FROM 6-MONTH DELAY: -$227.14M (-80.3%)
Month 30:
  - On-time owes: $47.70M coupon (on reduced $1,362.86M balance) + $227.14M principal = $274.84M.
  - Delayed owes: $55.65M coupon (on full $1,590.00M balance) + $227.14M principal = $282.79M.
```

Delaying commercial commencement incurs ongoing coupon carry, but **defers the massive cash drain of scheduled principal amortization**, providing immediate near-term liquidity relief of **$227.14M (-80.3%)** before the amortization staircase begins.

---

### Surface 5: Indenture Waterfall Priority Sensitivity & Arrears Allocation

| Waterfall Priority | Delay ($\Delta t$) | $T_{\text{DSRA}, 1}$ | $T_{\text{shortfall}, 1}$ | Max Opex Arrears 1 | Max Int Arrears 1 | Term Opex Arrears 1 | Term Int Arrears 1 | Max Opex Arrears 2 | Max Int Arrears 2 | Term Opex Arrears 2 | Term Int Arrears 2 | Valid Headline Support |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `opex_first` | 0 mo | 6 | 12 | **$5.0M** | $264.7M | **$0.0M** | $264.7M | **$17.0M** | $166.7M | **$0.0M** | $166.7M | $155.0M |
| `opex_first` | 6 mo | 6 | 12 | **$11.0M** | $356.4M | **$0.0M** | $356.4M | **$23.0M** | $221.7M | **$0.0M** | $221.7M | $170.0M |
| `opex_first` | 12 mo | 6 | 12 | **$17.0M** | $448.0M | **$0.0M** | $448.0M | **$29.0M** | $276.7M | **$0.0M** | $276.7M | $170.0M |
| `debt_service_first` | 0 mo | 6 | 12 | **$52.0M** | $212.7M | **$52.0M** | $212.7M | **$60.0M** | $106.7M | **$60.0M** | $106.7M | $155.0M |
| `debt_service_first` | 6 mo | 6 | 12 | **$55.0M** | $301.4M | **$55.0M** | $301.4M | **$60.0M** | $161.7M | **$60.0M** | $161.7M | $170.0M |
| `debt_service_first` | 12 mo | 6 | 12 | **$55.0M** | $393.0M | **$55.0M** | $393.0M | **$60.0M** | $216.7M | **$60.0M** | $216.7M | $170.0M |

**Priority Finding:**
Under `debt_service_first`, opex arrears jump to $52.0M–$55.0M for Silo 1 and $60.0M for Silo 2 (100% of all operating expenses defaulted), starving facility operations to service senior notes. Under `opex_first`, operating expenses are paid in full ($0 terminal arrears), while noteholder interest absorbs the shortfall.

---

## 4. Methodological Invariant Ledger (21 Certified Invariants)

All 21 invariants are verified across 25 unit tests (`src/test_phase2_level1.py`) and certified against data drift (`src/validate.py`):

| # | Invariant Description | Verification Mechanism | Status |
| :---: | :--- | :--- | :---: |
| 1 | **Strict Silo Isolation** | Cross-silo perturbation test (Case A vs Case B) | **CERTIFIED** |
| 2 | **Exact Fixed Coupon Arithmetic** | Accrual $= P \times r / 12$; Semiannual $= P \times r / 2$ | **CERTIFIED** |
| 3 | **Silo 1 Amortization Boundary** | Amortization strictly zero prior to Month 18 (Dec 15, 2027) | **CERTIFIED** |
| 4 | **Silo 2 State-Dependent Amort** | Start date defers dynamically with commencement | **CERTIFIED** |
| 5 | **Construction Support Isolation** | Completion support funds capex shortfalls only, never debt | **CERTIFIED** |
| 6 | **DSRA Restriction** | DSRA funds debt service only, never capex | **CERTIFIED** |
| 7 | **Independent Milestone Tracks** | $T_{\text{completion\_support}}$ triggers independently of $T_{\text{DSRA}}$ | **CERTIFIED** |
| 8 | **Non-Monotonic Amort Offset** | Delay defers scheduled principal, reducing near-term cash drain | **CERTIFIED** |
| 9 | **Parent Summation Post-Waterfall** | Total support calculated strictly post-waterfall | **CERTIFIED** |
| 10 | **Paid-Only Principal Reduction** | Balance decreases strictly by cash actually paid towards principal | **CERTIFIED** |
| 11 | **Complete Arrears Accounting** | Unpaid opex/coupon/amort recorded and cured by future cash | **CERTIFIED** |
| 12 | **Absorbing Default Boundary** | Silo marked `POST_SHORTFALL_ABSORBED` upon debt payment shortfall | **CERTIFIED** |
| 13 | **Cash Coverage Definition** | $T_{\text{coverage}}$ compares tenant cash rent against cash obligations | **CERTIFIED** |
| 14 | **Exhaustion as Transition** | Initial zero balance is not exhaustion; positive to zero transition required | **CERTIFIED** |
| 15 | **Explicit Waterfall Priority** | Different arrears allocation under `opex_first` vs `debt_service_first` | **CERTIFIED** |
| 16 | **Dynamic Calendar Mapping** | Normalized month-start dates derive calendar indexes dynamically | **CERTIFIED** |
| 17 | **Final Maturity Bullet Balloon** | Remaining principal balloons at final maturity (Months 54 & 60) | **CERTIFIED** |
| 18 | **Bounded Capex Total** | Remaining capex budget strictly caps cumulative construction outlays | **CERTIFIED** |
| 19 | **Zero Silent Priors in Surface API** | Every unobserved parameter must be explicitly passed by caller | **CERTIFIED** |
| 20 | **Absorbing Shortfall Censorship** | Valid headline support ceases accumulating at $T_{\text{payment\_shortfall}}$ | **CERTIFIED** |
| 21 | **Cents-Safe Precision & Residual Elimination** | Exact coupon reserves pay without premature floating-point default | **CERTIFIED** |

---

## 5. Artifact & Code Index

- **Deterministic Engine:** [`src/phase2_level1_engine.py`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-28-ai-infrastructure-network/src/phase2_level1_engine.py)
- **Unit Test Suite (25 Tests):** [`src/test_phase2_level1.py`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-28-ai-infrastructure-network/src/test_phase2_level1.py)
- **Surface Generation Pipeline:** [`src/analyze_phase2_surfaces.py`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-28-ai-infrastructure-network/src/analyze_phase2_surfaces.py)
- **Master Published Figure:** [`outputs/figures/phase2_delay_tolerance_surfaces.png`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-28-ai-infrastructure-network/outputs/figures/phase2_delay_tolerance_surfaces.png)
- **Published Data Tables:**
  - Synchronized Delay Surface: [`outputs/tables/phase2_delay_tolerance_surface_synchronized.csv`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-28-ai-infrastructure-network/outputs/tables/phase2_delay_tolerance_surface_synchronized.csv)
  - Decoupled Delay Matrix: [`outputs/tables/phase2_delay_tolerance_surface_decoupled.csv`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-28-ai-infrastructure-network/outputs/tables/phase2_delay_tolerance_surface_decoupled.csv)
  - Priority Sensitivity & Arrears: [`outputs/tables/phase2_waterfall_priority_sensitivity.csv`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-28-ai-infrastructure-network/outputs/tables/phase2_waterfall_priority_sensitivity.csv)
- **Architecture Specification:** [`docs/phase2_architecture_spec.md`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-28-ai-infrastructure-network/docs/phase2_architecture_spec.md)
