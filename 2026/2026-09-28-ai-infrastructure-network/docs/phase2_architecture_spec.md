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
   $$C_{\text{operating}, t+1} = C_{\text{operating}, t} + R^{\text{tenant}}_t - O^{\text{opex}}_t - I^{\text{coupon}}_t$$
4. **$\text{SponsorSupportAvailable}_t$:** Corporate parent completion guarantees or equity cure capacity under Exhibit 10.1 covenants.

---

### Tiered Failure Boundaries:
Rather than a single binary failure condition ($L_t < 0$), the Level 1 engine tracks **five tiered boundary milestones**:

```
[Normal Operation] ──> [T_account: Operating Cash Shortfall] 
                   ──> [T_DSRA: Debt Service Reserve Draw] 
                   ──> [T_support: Mandatory Sponsor Completion Support Activated] 
                   ──> [T_default: Uncured Contractual Payment Default] 
                   ──> [T_refi: Bullet Maturity / Refinancing Failure]
```

1. **$T_{\text{account}}$ (Project Account Exhaustion):** Operating cash inflows from active buildings are insufficient to cover current monthly debt service ($R^{\text{tenant}}_t < I^{\text{coupon}}_t + O^{\text{opex}}_t$).
2. **$T_{\text{DSRA}}$ (Reserve Account Draw):** Operating cash is exhausted, forcing the project SPV to tap the capitalized Debt Service Reserve Account.
3. **$T_{\text{support}}$ (Sponsor Completion Support Triggered):** DSRA drops below required covenants, or construction delay exceeds contractual thresholds, legally activating parent completion indemnities (e.g. Applied Digital corporate support).
4. **$T_{\text{default}}$ (Contractual Payment Default):** DSRA is fully exhausted and sponsor cure capacity is insufficient or refused, triggering an Event of Default under the indenture.
5. **$T_{\text{refi}}$ (Refinancing Horizon):** The bullet maturity date (2030 for 9.25% notes, 2031 for 7.00% notes) where debt must be repaid or refinanced under prevailing market credit spreads.

---

## 4. The Epistemic Defense: Prior Provenance Ledger & Sensitivity Auditing

To prevent manufactured conclusions, every stochastic and structural parameter is classified into the **Prior Provenance Ledger** (`data/processed/phase2/prior_provenance_ledger.parquet`):

```
+-----------------------------------+-------------------------------------------------------------------+
| Provenance Tier                   | Definition & Evidentiary Standard                                 |
+-----------------------------------+-------------------------------------------------------------------+
| 1. CONTRACT_DERIVED               | Exact terms from indentures, credit agreements, and 8-Ks          |
|                                   | (e.g. note principals, fixed coupons, maturity dates).            |
+-----------------------------------+-------------------------------------------------------------------+
| 2. MARKET_IMPLIED                 | Observable market curves (SOFR forwards, HY credit spread indices)|
+-----------------------------------+-------------------------------------------------------------------+
| 3. RATING_AGENCY_BENCHMARK        | Published institutional stress criteria (S&P, Moody's benchmarks) |
+-----------------------------------+-------------------------------------------------------------------+
| 4. EMPIRICAL_HISTORICAL           | Base rates from public queue datasets (LBNL queues, EIA data)     |
+-----------------------------------+-------------------------------------------------------------------+
| 5. ANALYST_PRIOR                  | Subjective modeling assumptions (strict sensitivity auditing)     |
+-----------------------------------+-------------------------------------------------------------------+
```

### Analytical Sensitivity Governance:
- For any analyst prior $\theta_i$, sensitivity is evaluated via finite differences across a preregistered plausible uncertainty interval ($\pm 10\%$ or its stated range):
  $$\Delta P = P\left(\text{Distress} \mid \theta_i + \delta\right) - P\left(\text{Distress} \mid \theta_i - \delta\right)$$
- **Analytical Governance Threshold:** If a 10% shift in a subjective prior produces a $> 20\%$ relative shift in failure probability (prior elasticity $|\mathcal{E}_i| > 2.0$), the result **cannot be presented as an empirical forecast**. It must be explicitly reported as a *Prior-Sensitive Structural Boundary*.

---

## 5. Candidate Proof-of-Concept: Polaris Forge 1 (Ellendale, ND)

### Financing Silo Decomposition (Rejecting Fungible Debt Pooling):
Polaris Forge 1 does not possess a single fungible debt stack; it contains two legally distinct project financing silos and a corporate parent support overlay:

```
[Campus Parent Support: Applied Digital Corporation (APLD)]
  │
  ├── [Silo 1: APLD_COMPUTECO / HPC_HOLDINGS] ──> $2.350B 9.25% Senior Notes (due 2030)
  │    Financing: Building 2 (100 MW operational) & Building 3 (150 MW partially commissioned)
  │    Annual Coupon Carry: $217.375M/yr
  │
  └── [Silo 2: APLD_COMPUTECO3] ────────────────> $1.590B 7.00% Senior Notes (due 2031)
       Financing: Building 4 (150 MW under construction)
       Annual Coupon Carry: $111.300M/yr
```

- **Combined Annual Coupon Carry:** **$328.675M/year** ($217.375M + $111.300M).
  *(Correction: The earlier $226.4M figure was an unrelated CoreWeave rate stress output; PF1 notes are fixed-rate instruments with a combined $328.675M coupon carry).*
- **Interest Rate Sensitivity:** Because both note stacks carry fixed coupons, benchmark rate movements (Fed/SOFR) produce **zero immediate cash flow shock**. Rate risk lives exclusively at bullet maturity (2030/2031 refinancing).

---

### Phase 2.0 Data Sufficiency Gate: Polaris Forge 1

Before writing simulation code, we evaluate public data availability to determine what can be solved deterministically versus what requires conditional surface mapping:

| Parameter / Variable | Model Necessity | Public Value in Frozen Corpus | Provenance Tier | Knowledge Status | Impact on Delay Tolerance ($T^*$) |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Silo 1 Note Principal** | Required | **$2,350.0M** | `CONTRACT_DERIVED` | **Known** | Exact debt carry baseline |
| **Silo 1 Coupon Rate** | Required | **9.25%** | `CONTRACT_DERIVED` | **Known** | Exact: $217.375M/yr |
| **Silo 2 Note Principal** | Required | **$1,590.0M** | `CONTRACT_DERIVED` | **Known** | Exact debt carry baseline |
| **Silo 2 Coupon Rate** | Required | **7.00%** | `CONTRACT_DERIVED` | **Known** | Exact: $111.300M/yr |
| **Combined Coupon Carry** | Required | **$328.675M/yr** | `CONTRACT_DERIVED` | **Known** | Exact annual cash hurdle |
| **Bullet Maturities** | Required | **2030 / 2031** | `CONTRACT_DERIVED` | **Known** | Exact refinancing horizons |
| **Initial DSRA Balances** | Required | Disclosed as existing; balance unstated | `CONTRACT_DERIVED` | **UNKNOWN** | **Requires conditional parameter $R_0$** |
| **Remaining Construction Account** | Required | Unstated in SEC 10-Q | `CONTRACT_DERIVED` | **UNKNOWN** | **Requires conditional parameter $C_{\text{capex}}$** |
| **Building 2 Literal Cash Rent** | Required | Total contract: $11B / 15yr / 400MW | `CONTRACT_DERIVED` | **UNKNOWN** | **Requires conditional parameter $R_{\text{B2}}$** *(Proportional proxy = $183.3M/yr)* |
| **Building 3 Operational MW** | Parameter | 150 MW shell; live MW unstated | `EMPIRICAL_HISTORICAL` | **UNCERTAIN** | **Requires interval [0 MW, 150 MW]** *(Audited: 60 MW measured utility load)* |
| **Remaining B3/B4 Capex Burn**| Required | Unstated month-by-month | `ANALYST_PRIOR` | **UNKNOWN** | **Requires burn rate parameter $K_{\text{burn}}$** |
| **Parent Completion Support** | Covenants | Exhibit 10.1 Springing Guarantee | `CONTRACT_DERIVED` | **Known** | Legal predicate known; dollar capacity uncertain |

### Architectural Decision:
Because initial DSRA balances, exact monthly construction burn, and literal building-level rent cash flows are **UNKNOWN from public SEC filings**, Level 1 **cannot defensibly output a single scalar delay tolerance (e.g. $T^* = 13\ \text{months}$)**.

Instead, Level 1 will output a **Contract-Bounded Conditional Delay-Tolerance Surface**:

$$T^*(R_0,\; K_{\text{burn}},\; R_{\text{B2}},\; \text{MW}_{\text{B3}})$$

This ensures 100% scientific honesty: the engine reveals the exact structural trade-offs between reserve cushions and schedule delays without inventing unevidenced balance sheet numbers.

---

## 6. Pre-Implementation Roadmap

```
[Gate 2.0: Sufficiency Audit] ──> Data sufficiency table verified (Conditional surface required).
[Phase 2.1: Level 1 POC]      ──> Build deterministic cash waterfall for PF1 (Silo 1 vs Silo 2).
[Phase 2.2: Surface Engine]   ──> Map T_account, T_DSRA, T_support across reserve and delay intervals.
[Phase 2.3: Hazard Engine]    ──> Implement duration-dependent semi-Markov transitions for Level 2.
[Phase 2.4: Graph Exposure]   ──> Couple project state machines to multi-layer graph factor model.
```
