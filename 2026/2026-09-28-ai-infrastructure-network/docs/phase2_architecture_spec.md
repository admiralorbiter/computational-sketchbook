# Phase 2 Architecture Specification: Probabilistic Project-Finance State Machine & Network Transmission

**Specification ID:** SPEC-PHASE2-ARCHITECTURE  
**Status:** Calibrated Architecture & POC Pre-Implementation Blueprint  
**Base Commit:** [`16a9916`](https://github.com/admiralorbiter/computational-sketchbook/commit/16a9916)  
**Date:** September 30, 2026  

---

## 1. Executive Summary & Paradigm Shift

Phase 1 established that systemic vulnerability in the AI infrastructure buildout resides at the **JOIN** between corporate finance, commercial contracts, and physical power delivery. 

However, transitioning from retrospective case reconstruction to forward-looking modeling introduces a critical methodological hazard: **the temptation of unconstrained macroeconomic speculation**. Attempting to model "whether the AI economy collapses" is ill-posed, prior-dominated, and unfalsifiable.

Phase 2 replaces macroeconomic forecasting with a grounded, engineering-grade financial framework:

$$\mathbf{A\ Probabilistic\ Project\text{-}Finance\ State\ Machine\ with\ Network\ Transmission}$$

### Core Conceptual Shift:
- **From:** Speculative macro predictions (*"Will AI capex crash in 2027?"*).
- **To:** Observable project survival (*"How much schedule slippage can each financing silo absorb before (a) debt service reserves are tapped, (b) sponsor completion support is required, and (c) an uncured default event becomes possible?"*).
- **From:** Arbitrary correlation matrices (*"Assume a 0.7 correlation between Project A and Project B"*).
- **To:** Graph-derived factor exposures (*"Project A and Project B share the ERCOT South transmission backplane, an anchor tenant, and a private credit syndicate"*).

This framework formalizes the convergence between rating agency project-finance criteria (S&P, Moody's), nonbank financial intermediation frameworks (BIS), and the Computational Observatory's bitemporal knowledge graph.

---

## 2. The Three-Level Modeling Hierarchy

To ensure tractability and prevent premature complexity, Phase 2 is structured into three strictly decoupled levels:

```
[Level 1: Project Delay-Tolerance Engine]
   │  Contract-bounded cash waterfall across legally segregated accounts.
   │  Output: Conditional Delay-Tolerance Surface T*(R_0, C_capex, R_rent).
   ▼
[Level 2: Probabilistic Single-Project Transition Model]
   │  Duration-dependent semi-Markov / hazard rate state machine.
   │  Bayesian updating driven by incoming bitemporal physical/regulatory evidence.
   │  Output: Survival Probability Distribution P(Survival | t).
   ▼
[Level 3: Correlated Network Portfolio Model]
      Graph-derived factor exposure model (B_kf Z_f + eps_k).
      Endogenous correlation arising from shared physical and credit nodes.
      Output: Correlated Simultaneous Impairment & Liquidity Contagion.
```

---

### Level 1: Contract-Bounded Deterministic Delay-Tolerance Engine
- **Purpose:** Model the contractual cash waterfall of a project's discrete financing silos to evaluate schedule slippage capacity.
- **Epistemic Classification:** **Contract-Bounded Deterministic Delay Tolerance**.
  - It is *exact* where all boundary-critical inputs (debt principal, fixed coupons, maturity dates, parent guarantees) are contractually observed.
  - It is *interval/conditional* where boundary-critical inputs (exact initial DSRA balance, literal building cash rent schedules, remaining capex burn) are not fully disclosed in public filings.
- **Output:** Rather than manufacturing a single synthetic scalar (e.g. $T^* = 13\ \text{months}$), the engine computes a **Conditional Delay-Tolerance Surface**:
  $$T^*(R_0, C_{\text{remaining}}, R_{\text{B2}}, R_{\text{B3}})$$
  mapping reserve assumptions and capex burn rates directly to tolerance horizons. If future filings disclose exact balances, the surface collapses into a point.

---

### Level 2: Probabilistic Single-Project Transition Model
- **Purpose:** Model the monthly progression of physical infrastructure from groundbreaking to stabilized commercial operations under uncertainty.
- **Engine:** **Duration-Dependent Semi-Markov / Hazard Rate State Machine**.
  - Rejects the memoryless Markov assumption: construction risk is duration-dependent (a project delayed at a substation milestone for 18 months faces fundamentally different failure hazards than one delayed for 1 month).
  - Models hazard transitions conditioned on elapsed time in state and incoming evidence:
    $$P(S_{t+1} \mid S_t, \tau_{\text{elapsed}}, E_t)$$
  - Supports **multi-state concurrency**: a campus can occupy multiple states simultaneously across discrete buildings:
    $$X_t = \left(S_{\text{B2}, t},\; S_{\text{B3}, t},\; S_{\text{B4}, t}\right)$$
- **Observable Physical-Commercial States:**
  1. `S0: Financed / Pre-Construction`
  2. `S1: Civil & Shell Construction`
  3. `S2: MEP & Power Delivery (Substation / Fuel Line)`
  4. `S3: Energized & Commissioned`
  5. `S4: Tenant Commercial Acceptance (Rent Commencement)`
  6. `S5: Stabilized Cash Flow Operations`
- **Output:** Distribution of commercial rent commencement dates and default hazard $P(\text{Default} \mid \text{Priors})$.

---

### Level 3: Correlated Network Portfolio Model
- **Purpose:** Evaluate systemic fragility across a portfolio of infrastructure developments without imposing arbitrary correlation matrices.
- **Engine:** **Graph-Derived Factor Exposure Model**:
  $$\text{Project Shock}_k = \sum_f B_{kf} Z_f + \epsilon_k$$
  Where factor loadings $B_{kf}$ are derived directly from the multi-layer knowledge graph:
  - **Power Backplane Factors ($Z_{\text{grid}}$):** Derived from physical grid interconnects (ERCOT, PJM, MISO) and typed power service regimes (firm vs interruptible).
  - **Syndicate Liquidity Factors ($Z_{\text{credit}}$):** Derived from shared private credit BDCs and bank lending syndicates.
  - **Commercial Offtake Factors ($Z_{\text{tenant}}$):** Derived from anchor tenant concentration (e.g. CoreWeave, Oracle, Microsoft).
  - **Macro Benchmark Factors ($Z_{\text{macro}}$):** Benchmark rate shifts (SOFR) and credit spread blowout affecting refinancing at maturity.
- **Output:** Endogenous joint distress distributions and common-cause liquidity drains.

---

## 3. Mathematical Formulation: Legally Segregated Accounts & Tiered Failure Boundaries

In project finance, cash is not fungible; dollars are trapped in legally segregated accounts with strict contractual priorities. A project can hold $200M of nominal cash and still default if that cash is restricted to construction disbursements.

### Segregated Account State Vector:
For any financing silo $k$ at month $t$, the financial state is tracked across distinct accounts:

$$\mathbf{C}_{k,t} = \begin{bmatrix} C_{\text{construction}, t} \\ C_{\text{DSRA}, t} \\ C_{\text{operating}, t} \\ C_{\text{unrestricted}, t} \end{bmatrix}, \quad \text{plus} \quad \text{SponsorSupportAvailable}_t$$

1. **$C_{\text{construction}, t}$ (Construction Account):** Funded from note proceeds/draws; strictly restricted to certified EPC and equipment capex:
   $$C_{\text{construction}, t+1} = C_{\text{construction}, t} + \Delta C^{\text{draw}}_t - K^{\text{capex}}_t$$
2. **$C_{\text{DSRA}, t}$ (Debt Service Reserve Account):** Restricted to debt service; typically sized to 6–12 months of coupon carry:
   $$C_{\text{DSRA}, t+1} = C_{\text{DSRA}, t} - \text{Draw}^{\text{DSRA}}_t + \text{Replenish}^{\text{DSRA}}_t$$
3. **$C_{\text{operating}, t}$ (Operating Cash Account):** Ingests tenant rent from operational capacity and pays ongoing opex and primary debt service:
   $$C_{\text{operating}, t+1} = C_{\text{operating}, t} + R^{\text{tenant}}_t - O^{\text{opex}}_t - I^{\text{coupon}}_t - P^{\text{amort}}_t$$
4. **$\text{SponsorSupportAvailable}_t$:** Corporate parent completion support under Applied Digital's contractual completion guarantees (Nov 20, 2025 and June 16, 2026 Form 8-Ks). Strictly distinct from CoreWeave's tenant-side springing guaranty (Exhibit 10.1).

---

### Tiered Failure Boundaries: The 6-Milestone Staircase
Rather than a single binary failure condition ($L_t < 0$), the Level 1 engine tracks a **6-milestone contractual staircase**:

```
[Normal Operations] ──> [T_coverage: Operating Cash Flow Deficit] 
                    ──> [T_operating_exhaustion: Operating Account Depletion] 
                    ──> [T_DSRA: Debt Service Reserve Draw] 
                    ──> [T_completion_support: Parent Completion Guarantee Economically Required] 
                    ──> [T_default: Uncured Contractual Payment Default] 
                    ──> [T_refi: Final Maturity / Refinancing Boundary]
```

1. **$T_{\text{coverage}}$ (Operating Flow Deficit):** First month recurring operating cash inflows do not cover recurring uses ($R^{\text{tenant}}_t < I^{\text{coupon}}_t + P^{\text{amort}}_t + O^{\text{opex}}_t$). The project enters a cash burn state, though prior operating cash reserves may still buffer payments.
2. **$T_{\text{operating\_exhaustion}}$ (Operating Account Depletion):** First month the operating cash account balance reaches its contractual floor or zero ($C_{\text{operating}, t} = 0$).
3. **$T_{\text{DSRA}}$ (Debt Service Reserve Draw):** Operating cash is fully depleted, forcing the project SPV to execute its first draw on the capitalized Debt Service Reserve Account ($C_{\text{DSRA}, t} < C_{\text{DSRA}, 0}$).
4. **$T_{\text{completion\_support}}$ (Parent Completion Funding Required):** First month when remaining eligible project funds are insufficient to fund the remaining construction capex necessary to achieve the contractual commencement/completion milestone. Under the November 20, 2025 (Silo 1) and June 16, 2026 (Silo 2) Form 8-Ks, this activates Applied Digital's mandatory parent completion funding obligations before the Outside Completion Date.
5. **$T_{\text{default}}$ (Contractual Payment Default):** DSRA is fully exhausted and parent cure capacity is insufficient or refused, triggering an Event of Default under the applicable indenture.
6. **$T_{\text{refi}}$ (Final Maturity / Refinancing Boundary):** Final bullet maturity dates (2030 for 9.25% notes, 2031 for 7.00% notes) where remaining principal must be repaid or refinanced under prevailing credit spreads.

---

## 4. The Epistemic Defense: Two-Field Provenance & Sensitivity Auditing

To maintain absolute scientific transparency, every modeling parameter is decoupled into two independent dimensions: its **evidential source status** in public filings versus its **mathematical model treatment**:

```
+-------------------------------------------------------------------------------------------------------+
| Field 1: source_status                                                                                |
+--------------------------+----------------------------------------------------------------------------+
| PRIMARY_DISCLOSED        | Verbatim fact certified in audited SEC EDGAR filings or indentures.        |
| MARKET                   | Observable market price, yield curve, or index (SOFR, HY spread).          |
| HISTORICAL               | Public institutional base rate (e.g. LBNL interconnection queues).         |
| UNOBSERVED               | Omitted from public filings; unobservable from public record at t_0.       |
+--------------------------+----------------------------------------------------------------------------+
| Field 2: model_treatment                                                                              |
+--------------------------+----------------------------------------------------------------------------+
| EXACT                    | Pinned to certified primary contract value without free parameters.        |
| INTERVAL                 | Bounded by disclosed constraints (e.g. [0 MW, 150 MW]).                    |
| CONDITIONAL              | Explored across parameter grid surface (e.g. T*(R_0, K_burn)).             |
| ANALYST_SCENARIO         | User-defined stress scenario (subject to mandatory sensitivity auditing).   |
+--------------------------+----------------------------------------------------------------------------+
```

### Analytical Sensitivity Governance:
- For any analyst scenario parameter $\theta_i$, sensitivity is evaluated via finite differences across a preregistered plausible uncertainty interval ($\pm 10\%$ or its stated range):
  $$\Delta P = P\left(\text{Distress} \mid \theta_i + \delta\right) - P\left(\text{Distress} \mid \theta_i - \delta\right)$$
- **Analytical Governance Threshold:** If a 10% shift in a subjective prior produces a $> 20\%$ relative shift in boundary milestone arrival (elasticity $|\mathcal{E}_i| > 2.0$), the finding **cannot be presented as a forecast**. It must be explicitly reported as a *Prior-Sensitive Structural Boundary*.

---

## 5. Candidate Proof-of-Concept: Polaris Forge 1 (Ellendale, ND)

### Financing Silo Decomposition (Rejecting Fungible Debt Pooling):
Polaris Forge 1 does not possess a single fungible debt stack; it contains two legally distinct project financing silos and a corporate parent support overlay:

```
[Campus Parent Support: Applied Digital Corporation (APLD)]
  │  (Completion Guarantees: Nov 20, 2025 Form 8-K & June 16, 2026 Form 8-K)
  │
  ├── [Silo 1: APLD_COMPUTECO / HPC_HOLDINGS] ──> $2.350B 9.25% Senior Notes (due 2030)
  │    Financing: Building 2 (100 MW operational) & Building 3 (150 MW partially operational)
  │    Annual Coupon Carry: $217.375M/yr ($2.350B × 9.25%)
  │    Scheduled Amortization: Semiannual principal amortization begins December 15, 2027
  │    Final Maturity: 2030
  │
  └── [Silo 2: APLD_COMPUTECO3] ────────────────> $1.590B 7.00% Senior Notes (due 2031)
       Financing: Building 4 (150 MW under construction)
       Annual Coupon Carry: $111.300M/yr ($1.590B × 7.00%)
       Scheduled Amortization: Semiannual principal amortization begins first payment date
                               after the final Commencement Date (State-Dependent)
       Final Maturity: 2031
```

- **Combined Annual Coupon Carry:** **$328.675M/year** ($217.375M + $111.300M).
- **State-Dependent Principal Amortization (Structural Offset):**
  - In Silo 2, scheduled principal amortization begins on the *first payment date following the final Commencement Date*.
  - This introduces a **non-monotonic interaction with delay**: a construction delay postpones tenant commercial rent commencement and burns interest carry, but simultaneously **defers scheduled principal amortization cash outflows**. The Level 1 engine explicitly models this contractual interaction rather than assuming bullet-only debt.
- **Interest Rate Sensitivity:** Because both note stacks carry fixed coupons, benchmark rate movements (Fed/SOFR) produce **zero immediate cash coupon shock**. Rate risk lives exclusively at final maturity (2030/2031 refinancing).

---

### Phase 2.0 Data Sufficiency Gate: Polaris Forge 1

Before writing simulation code, we evaluate public data availability under the two-field schema:

| Parameter / Variable | Model Role | Value in Frozen Corpus | `source_status` | `model_treatment` | Impact on Delay Tolerance ($T^*$) |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Silo 1 Principal** | Required | **$2,350.0M** | `PRIMARY_DISCLOSED` | `EXACT` | Pinned baseline |
| **Silo 1 Coupon** | Required | **9.25%** | `PRIMARY_DISCLOSED` | `EXACT` | Exact: $217.375M/yr carry |
| **Silo 1 Amortization** | Required | Semiannual from Dec 15, 2027 | `PRIMARY_DISCLOSED` | `EXACT` | Exact contractual schedule |
| **Silo 2 Principal** | Required | **$1,590.0M** | `PRIMARY_DISCLOSED` | `EXACT` | Pinned baseline |
| **Silo 2 Coupon** | Required | **7.00%** | `PRIMARY_DISCLOSED` | `EXACT` | Exact: $111.300M/yr carry |
| **Silo 2 Amortization** | Required | Semiannual post-Commencement | `PRIMARY_DISCLOSED` | `EXACT` | State-dependent schedule |
| **Final Maturities** | Required | **2030 / 2031** | `PRIMARY_DISCLOSED` | `EXACT` | Refinancing horizons |
| **Initial DSRA Balances** | Required | Disclosed as existing; balance unstated | `UNOBSERVED` | `CONDITIONAL` | **Requires surface parameter $R_0$** |
| **Remaining Construction Account** | Required | Unstated in SEC 10-Q | `UNOBSERVED` | `CONDITIONAL` | **Requires surface parameter $C_{\text{capex}}$** |
| **Building 2 Literal Cash Rent** | Required | Contract: $11B / 15yr / 400MW | `PRIMARY_DISCLOSED` | `CONDITIONAL` | **Requires surface parameter $R_{\text{B2}}$** *(Proportional proxy = $183.3M/yr)* |
| **Building 3 Operational MW** | Physical | 150 MW shell; live MW unstated | `PRIMARY_DISCLOSED` | `INTERVAL` | **Interval $[0\ \text{MW}, 150\ \text{MW}]$** *(Campus load = 60 MW)* |
| **Remaining B3/B4 Capex Burn**| Required | Unstated month-by-month | `UNOBSERVED` | `ANALYST_SCENARIO` | **Requires scenario parameter $K_{\text{burn}}$** |
| **Parent Completion Support** | Support | Nov 20, 2025 & June 16, 2026 8-Ks | `PRIMARY_DISCLOSED` | `EXACT` | Insufficiency trigger certified |

---

### Architectural Decision: Outputting Milestone Boundary Surfaces
Because initial DSRA balances, exact monthly construction burn, and literal building-level rent cash flows are **UNOBSERVED in public SEC filings**, Level 1 does not output a single fragile scalar (e.g. $T^* = 13\ \text{months}$).

Instead, Level 1 computes the **Contract-Bounded Milestone Surfaces**:

$$\mathcal{T}_{\text{milestone}} = \left\{ T_{\text{coverage}},\; T_{\text{operating\_exhaustion}},\; T_{\text{DSRA}},\; T_{\text{completion\_support}},\; T_{\text{default}},\; T_{\text{refi}} \right\} = f(R_0,\; K_{\text{burn}},\; R_{\text{B2}},\; \text{MW}_{\text{B3}})$$

This maintains complete epistemic fidelity: it evaluates how contractual protections, reserve accounts, and state-dependent amortization interact under physical delay without fabricating undisclosed balance sheet figures.

---

## 6. Pre-Implementation Roadmap

```
[Gate 2.0: Sufficiency Audit] ──> Data sufficiency verified (Two-field schema locked).
[Phase 2.1: Level 1 POC]      ──> Build deterministic cash waterfall for PF1 (Silo 1 vs Silo 2).
[Phase 2.2: Surface Engine]   ──> Map the 6-milestone staircase across reserve and delay intervals.
[Phase 2.3: Hazard Engine]    ──> Implement duration-dependent semi-Markov transitions for Level 2.
[Phase 2.4: Graph Exposure]   ──> Couple project state machines to multi-layer graph factor model.
```

