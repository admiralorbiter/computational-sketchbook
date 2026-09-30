# Phase 2 Architecture Specification: Probabilistic Project-Finance State Machine & Network Transmission

**Specification ID:** SPEC-PHASE2-ARCHITECTURE  
**Status:** Draft / Conceptual Blueprint  
**Base Commit:** [`b735b19`](https://github.com/admiralorbiter/computational-sketchbook/commit/b735b19) (`v0.1-phase1`)  
**Date:** September 30, 2026  

---

## 1. Executive Summary & Paradigm Shift

Phase 1 established that the AI infrastructure buildout cannot be evaluated through isolated financial statements, static contractual tables, or regional electric grid topologies alone. The systemic vulnerabilities live in the **JOIN** between domains.

However, moving from retrospective reconstruction to forward-looking analysis introduces a critical methodological hazard: **the temptation of unconstrained macroeconomic speculation**. Attempting to model "whether the AI economy collapses" is intractable, prior-dominated, and unfalsifiable.

Phase 2 replaces macroeconomic forecasting with a grounded, engineering-grade financial framework:

$$\mathbf{A\ Probabilistic\ Project\text{-}Finance\ State\ Machine\ with\ Network\ Transmission}$$

### Core Conceptual Shift:
- **From:** Speculative macro predictions (*"Will AI demand crash in 2027?"*).
- **To:** Observable project survival (*"How many months of schedule slippage can this specific capital structure withstand before liquidity exhaustion?"*).
- **From:** Arbitrary network correlation matrices (*"Assume a 0.7 correlation between Project A and Project B"*).
- **To:** Mechanistic network co-exposure (*"Project A and Project B share the ERCOT South transmission corridor, a common private credit syndicate, and an anchor tenant"*).

This framework formalizes the convergence between rating agency project-finance criteria (S&P, Moody's), nonbank financial intermediation frameworks (BIS), and the Computational Observatory's bitemporal knowledge graph.

---

## 2. The Three-Level Modeling Hierarchy

To ensure tractability and prevent premature complexity, Phase 2 is structured into three strictly decoupled levels:

```
[Level 1: Project Delay-Tolerance Engine]
   │  Deterministic cash waterfall & liquidity cushion vs schedule delay.
   │  Metric: Delay Tolerance Horizon T* (months).
   ▼
[Level 2: Probabilistic Single-Project Transition Model]
   │  Bayesian Markov state machine driven by physical/regulatory priors.
   │  Metric: Survival Probability Distribution P(Survival | t).
   ▼
[Level 3: Correlated Network Portfolio Model]
      Latent macro factors (rates, spreads, grid curtailment, tenant credit).
      Metric: Correlated Simultaneous Impairment & Liquidity Contagion.
```

---

### Level 1: Deterministic Project Delay-Tolerance Engine
- **Purpose:** Given a project's known capital structure, reserves, debt service schedule, and construction budget, calculate the exact number of months of delay the project can absorb before running out of liquidity.
- **Inputs:**
  - Capitalized Interest Reserve ($L_{\text{reserve}}$).
  - Monthly debt service (interest + mandatory amortization).
  - Monthly ongoing carrying/standby costs.
  - Undrawn construction facility commitments.
  - Contracted post-energization base lease rent.
- **Output:** **Delay Tolerance Horizon ($T^*$):**
  $$T^* = \max \left\{ d \in \mathbb{N} \;\middle|\; L(t) \ge 0 \quad \forall t \le t_{\text{energization}} + d \right\}$$
- **Value:** Zero stochastic priors required. Completely auditable from SEC filings and credit agreements.

---

### Level 2: Probabilistic Single-Project Transition Model
- **Purpose:** Model the monthly state transitions of a single project from groundbreaking to stabilized commercial operations under uncertainty.
- **Engine:** Discrete-time Markov state machine with 6 observable physical-commercial states:
  1. `S0: Financed / Pre-Construction`
  2. `S1: Civil & Shell Construction`
  3. `S2: MEP & Power Delivery (Substation / Fuel Line)`
  4. `S3: Energized & Commissioned`
  5. `S4: Tenant Commercial Acceptance (Rent Commencement)`
  6. `S5: Stabilized Cash Flow Operations`
- **Dynamic Bayesian Updating:** Transition probabilities $P(S_{t+1} \mid S_t)$ begin with sector baseline priors and update dynamically as public disclosures arrive across the observatory's bitemporal information clock:
  - *Example:* Utility interconnect approval accelerates $S2 \to S3$; NMSLO pipeline permit denial stalls $S2 \to S2$ or triggers $S2 \to \text{Dispute}$.
- **Output:** Distribution of rent commencement dates and default probability $P(L_t < 0 \mid \text{Priors})$.

---

### Level 3: Correlated Network Portfolio Model
- **Purpose:** Evaluate systemic fragility across a portfolio of monitored infrastructure assets without manufacturing arbitrary correlation matrices.
- **Mechanism:** Correlation arises endogenously because projects share real nodes in the multi-layer graph:
  - **Shared Power Backplanes:** Projects in ERCOT or PJM share transmission queue capacity, gas fuel constraints, and local curtailment risk.
  - **Shared Credit Syndicates:** Private credit BDCs and bank syndicates hold tranches across multiple project SPVs, creating correlated liquidity constraints if multiple projects stall simultaneously.
  - **Shared Hyperscaler Offtakers:** Commercial tenant concentration (e.g. CoreWeave or Oracle) links otherwise independent geographic developments.
  - **Shared Latent Macro Factors:** Risk-free benchmark rate shifts (SOFR), high-yield credit spread widening, and power equipment lead times.

---

## 3. Mathematical Formulation: The Monthly Cash Waterfall

For any project $k$ at monthly time step $t$, liquidity $L_{k,t}$ evolves according to the conservation equation:

$$L_{k,t+1} = L_{k,t} + \Delta C^{\text{draw}}_{k,t} + \Delta C^{\text{equity}}_{k,t} + R^{\text{tenant}}_{k,t} - \left( K^{\text{capex}}_{k,t} + I^{\text{interest}}_{k,t} + P^{\text{principal}}_{k,t} + O^{\text{opex}}_{k,t} \right)$$

Where:
- $\Delta C^{\text{draw}}_{k,t}$: Permitted draws on construction facilities, subject to borrowing base covenants and milestone certification.
- $\Delta C^{\text{equity}}_{k,t}$: Sponsor equity contributions or debt-service cure injections.
- $R^{\text{tenant}}_{k,t}$: Cash rent received from offtaker (strictly zero until State $S4$ is reached, unless pre-energization capacity reservation fees are contractually active).
- $K^{\text{capex}}_{k,t}$: Ongoing construction and equipment expenditures.
- $I^{\text{interest}}_{k,t}$: Contractual interest payment, calculated across discrete fixed and floating rate legs:
  $$I^{\text{interest}}_{k,t} = \sum_{j \in \text{Tranches}} D_{j,t} \cdot \frac{r_{j,t}}{12}$$
- $P^{\text{principal}}_{k,t}$: Mandatory amortization or scheduled bullet maturity refinancing.
- $O^{\text{opex}}_{k,t}$: Land leases, insurance, security, and administrative carry costs.

### Boundary Failure Condition:
The project encounters **Liquidity Distress** at the first time step $t$ where:

$$L_{k,t} < 0 \quad \text{and} \quad \Delta C^{\text{draw}}_{k,t} = 0 \quad \text{and} \quad \Delta C^{\text{equity}}_{k,t} = 0$$

---

## 4. The Epistemic Defense: The Prior Provenance Ledger

The principal risk of probabilistic modeling is the **"manufactured outcome problem"**: an analyst can make any project survive or fail simply by adjusting transition probabilities, recovery rates, or refinancing costs.

To ensure unassailable scientific credibility, Phase 2 mandates a **Prior Provenance Ledger** (`data/processed/phase2/prior_provenance_ledger.parquet`). Every parameter in the simulation must be explicitly classified into one of five evidentiary tiers:

```
+-----------------------------------+-------------------------------------------------------------------+
| Provenance Classification         | Definition & Required Source Reference                            |
+-----------------------------------+-------------------------------------------------------------------+
| 1. CONTRACT_DERIVED               | Extracted directly from credit agreements, indentures, or leases  |
|                                   | (e.g. coupon spreads, debt service reserve size, maturity dates).|
+-----------------------------------+-------------------------------------------------------------------+
| 2. MARKET_IMPLIED                 | Observable market prices and yield curves                         |
|                                   | (e.g. SOFR forward curve, ICE BofA US High Yield spread index).   |
+-----------------------------------+-------------------------------------------------------------------+
| 3. RATING_AGENCY_BENCHMARK        | Published institutional stress criteria                           |
|                                   | (e.g. S&P/Moody's construction delay criteria, recovery scales). |
+-----------------------------------+-------------------------------------------------------------------+
| 4. EMPIRICAL_HISTORICAL           | Base rates derived from public transmission queue datasets        |
|                                   | (e.g. LBNL interconnection wait times, EIA generator lead times). |
+-----------------------------------+-------------------------------------------------------------------+
| 5. ANALYST_PRIOR                  | Subjective hypotheses (subject to mandatory sensitivity auditing).|
+-----------------------------------+-------------------------------------------------------------------+
```

### Mandatory Sensitivity Audit (Prior Elasticity):
For every analyst prior $\theta_i$, the engine must compute the sensitivity elasticity $\mathcal{E}_i$:

$$\mathcal{E}_i = \frac{\partial P(\text{Distress})}{\partial \theta_i} \cdot \frac{\theta_i}{P(\text{Distress})}$$

If $|\mathcal{E}_i| > 2.0$ (i.e. a 10% change in an analyst prior produces more than a 20% shift in the distress probability), the finding **cannot be published as a headline forecast**. It must be explicitly reported as a *Prior-Sensitive Structural Boundary*.

---

## 5. Candidate Proof-of-Concept: Polaris Forge 1 (Applied Digital / CoreWeave)

Rather than building an abstract multi-project simulation immediately, Phase 2 will execute a bounded **Proof-of-Concept** on a single asset with rich public data: **Polaris Forge 1 (Ellendale, ND)**.

### Why Polaris Forge 1 is the Ideal Prototype:
1. **Audited Capital Structure:**
   - $3.940B in dedicated project-level notes ($1.59B 7.00% Senior Secured Notes + $2.35B 9.25% Senior Secured Notes).
   - Capitalized interest reserve accounts verified in SEC Form 8-K.
   - Known annual debt service: ~$226.4M/yr.
2. **Disclose Operational Phasing:**
   - Building 2: 100 MW operational (generating ~$183.3M/yr base rent ongoing).
   - Building 3: 150 MW (~50 MW commissioned, ~100 MW pending energization).
   - Building 4: 150 MW under active construction.
3. **Discrete Contractual Predicates:**
   - CoreWeave colocation lease with documented parent springing guarantee (Exhibit 10.1).
   - MDU utility substation expansion timeline and transmission interconnection queue.

### Proof-of-Concept Objective:
Compute the exact **Delay Tolerance Curve** for Polaris Forge 1:
- What is the maximum construction delay on Buildings 3 & 4 that PF1 can absorb before Building 2 cash flows and interest reserves are exhausted?
- Under what interest rate refinancing scenario does debt service breach the DSCR covenant?

---

## 6. Implementation Milestones

```
[Phase 2.1: Level 1 POC] ──> Deterministic Cash Waterfall & Delay-Tolerance Engine for Polaris Forge 1.
[Phase 2.2: Prior Ledger]──> Curate empirical transmission queue priors & market rate curves.
[Phase 2.3: Level 2 Engine]─> Probabilistic Markov state transitions with Bayesian updating.
[Phase 2.4: Portfolio Join]─> Expand to 3-asset network (PF1 + Project Jupiter + Prospective Watchlist).
```

This roadmap delivers rigorous, quantitative research at every step, avoiding premature scaling while providing institutional-grade analytical utility.
