# Economics Modeling Strategy & Philosophy (for KC Econ Lab)

*Last updated: Aug 10, 2025*

## Why we’re doing this

We want to **learn by building**—from first principles to modern models—so the math, code, and intuition are transparent. Every step is:

1. minimal but correct,
2. experiment-driven, and
3. documented so others can follow, poke, and improve.

---

## Core principles

1. **Start tiny, then add frictions.** Build the smallest model that answers a question; add one complication at a time (sticky prices, heterogeneity, frictions).
2. **Make learning visible.** Each project ships: equations, code, figures, and a 1–2 page “What changed / What I learned.”
3. **Two lenses: national + local (Kansas City).** We connect national context (CPI, rates, GDP) to **KC MSA (CBSA 28140)** indicators (labor, housing, mobility).
4. **Reproducible by default.** Same data → same results. Pin environments, track sources, seed random draws.
5. **Model ↔ data feedback loop.** Model predicts; data challenges; we refine.
6. **Explorable results.** Sliders, toggles, and scenario switches so anyone can play and build intuition.
7. **Compare, don’t proclaim.** Always show baseline vs modified; plot differences and elasticities.
8. **Document assumptions explicitly.** Write them down before running code.

---

## The modeling loop (every project)

**Question → Minimal model → Data → Code → Experiments → Compare → Explain**

* **Question**: One sentence, falsifiable (“Does a reserve price raise expected revenue here?”).
* **Minimal model**: Primitives, constraints, equilibrium concept (or estimator), 3–6 equations.
* **Data**: Series list with sources and units. National + KC where possible.
* **Code**: Clean functions (in `src/`), notebook for runs, seeds fixed.
* **Experiments**: Sensitivity grid, stress test, and one policy or friction.
* **Compare**: Baseline vs change; IRFs or delta plots.
* **Explain**: 1–2 pages; include “What surprised me” + “Next question.”

---

## Project scaffolding we’ll reuse

* **Folders:** `data/bronze → silver → gold`, `src/ingest|transform|features|viz`, `notebooks/`, `docs/`, `tests/`.
* **IDs & units:** `geo_id` (`US`, `US-MW`, `CBSA-28140`), `time_id` (`YYYY-MM`, `YYYY-Q#`), `unit` clear.
* **Outputs:** Save figures (`.png/.svg`) + CSV of chart data so plots are verifiable.
* **Notes:** `notes/<project>.md` with 3 insights and 1 “next change.”

---

## Data strategy (quick, sane, expandable)

* **Start with FRED** (no scraping, strong uptime): CPI (CPIAUCSL), Policy rates, GDP, FHFA HPI for **KC** (ATNHPIUS28140Q).
* **Add BLS/BEA/Census as needed**: LAUS (KC unemployment), OEWS (wages), BEA metro GDP, ACS demographics.
* **KC sources** for local color: Redfin/Zillow (housing), Open Data KC (permits, 311), RideKC/Streetcar (ridership).
* **Bronze → Silver → Gold:** raw pulls → standardized columns → model-ready (rebased, seasonally adjusted, joined).

---

## How we show learning (visible artifacts)

* **Play notebooks:** small, runnable, with sliders or parameter blocks.
* **Experiment tables:** each row = scenario; columns = key outcomes (e.g., output gap, welfare, revenue).
* **“Difference” plots:** show Δ from baseline, not just raw levels.
* **One-pager notes:** equations, assumptions, results, limits, next step.

---

## The ladder of models (from foundation to advanced)

Each topic below lists: **Foundation → Build → Experiments → KC tie-in → Stretch**
Use these as checklists for deep dives.

### 1) Markets & Equilibrium (Micro Foundations)

**Foundation**

* Supply–demand (linear/isoelastic); consumer/producer surplus; tax incidence.
* Consumer problem (Cobb-Douglas/CES); Marshallian vs Hicksian; Slutsky.

**Build**

* Firms with costs; partial equilibrium; comparative statics.
* Duopoly (Cournot vs Bertrand) with differentiation.

**Experiments**

* Per-unit vs ad valorem tax; price floor/ceiling; shock sensitivity.
* Best-response dynamics; capacity constraints.

**KC tie-in**

* Use KC housing as the “market”: ZHVI/HPI (price), Redfin (inventory), permits as supply proxy.

**Stretch**

* General equilibrium sketch; discrete choice demand linking to IO.

---

### 2) Games, Auctions, and Market Design

**Foundation**

* Normal-form games; pure/mixed Nash; replicator dynamics.

**Build**

* First-price vs second-price auctions (independent private values).

**Experiments**

* Revenue under reserve prices; asymmetry in valuations.
* Strategy-proofness checks in matching (Gale–Shapley) mini-lab.

**KC tie-in**

* Education seat allocation stylized models; simple matching demos for community sessions.

**Stretch**

* Quantal response; dynamic auctions; school choice rules (priorities, tie-breaks).

---

### 3) Growth & Business Cycles (Macro)

**Foundation**

* Solow (transition dynamics, golden rule).
* Ramsey (VFI + Euler shooting).

**Build**

* Tiny RBC (log-linear); impulse responses to TFP.
* 3-equation New Keynesian (IS, NKPC, Taylor).

**Experiments**

* Speed of convergence; capital shocks; Taylor rule coefficients; determinacy maps.

**KC tie-in**

* Compare **KC HPI** and employment to national shocks; simple gap indicators.

**Stretch**

* Zero lower bound (piecewise); habit formation; 2-sector RBC.

---

### 4) Time Series, State Space, and VARs

**Foundation**

* Stationarity, ARIMA/C; lag selection; unit roots.

**Build**

* Small VAR (prices–wages–unemployment); IRFs and FEVD.
* Kalman filter for a simple output gap estimate.

**Experiments**

* Identification schemes (Cholesky vs sign restrictions); robustness to lag length.

**KC tie-in**

* Nowcast KC unemployment using LAUS + national leading series.

**Stretch**

* Bayesian VAR; time-varying parameters.

---

### 5) Causal Inference (Policy & Programs)

**Foundation**

* Potential outcomes; identification; DiD/event-study; IV basics.

**Build**

* Staggered adoption DiD with cohort-weighted estimators.

**Experiments**

* Placebo pre-trends; heterogeneous treatment effects; sensitivity to timing.

**KC tie-in**

* Evaluate impacts of a local policy change (e.g., fare-free periods, zoning change) using city/metro time series and matched metros.

**Stretch**

* Synthetic control; IV with shift-share instruments (educational programs ↔ occupations).

---

### 6) Spatial & Networks

**Foundation**

* Spatial autocorrelation (Moran’s I); contiguity and distance weights.

**Build**

* Network diffusion (threshold model) on synthetic graphs.

**Experiments**

* Seeding strategies; cascade sizes vs topology; spatial lags vs errors.

**KC tie-in**

* LEHD LODES flows (tract-level jobs and commuting); job-density hot spots.

**Stretch**

* Spatial panel models; network games of adoption.

---

### 7) Agent-Based & Computational Experiments

**Foundation**

* Simple trader types; market-clearing rules.

**Build**

* ACE market with chartists vs fundamentalists; calibration to stylized facts.

**Experiments**

* Type shares; noise variance; learning rules.

**KC tie-in**

* “What if” scenarios for sectoral shocks; toy labor-search agents tuned to KC.

**Stretch**

* Multi-market interactions; expectation formation variants.

---

## Experiment design pattern (copy-paste template)

* **Hypothesis:** *If we increase parameter α, metric Y should… because…*
* **Scenarios:** Baseline (α₀), Low (α₀ − Δ), High (α₀ + Δ).
* **Metrics:** Pick 3: {welfare, consumption, unemployment, revenue, volatility, RMSE}.
* **Method:** Fix seed; run N=500 draws if stochastic; log every run.
* **Plots:** Line (paths), Bar (Δ vs baseline), Heatmap (α × β grid).
* **Readout:** 3 bullets (confirm/refute/surprise).
* **Next:** The **one** change you’d try next and why.

---

## Documentation pattern (per project)

1. **Problem statement (≤3 sentences)**
2. **Assumptions & equations** (primitives, constraints, solution concept)
3. **Data (table)**: series, geo, units, cadence
4. **Algorithm/estimator** (what you solved & how)
5. **Results**: figures + 3 bullets
6. **Limits**: what this model cannot say
7. **Next step**: 1 concrete extension

---

## Code & product ethos

* **Backend:** Flask (blueprints, app factory).
* **Frontend:** HTML/CSS/Bootstrap + small JS (Chart.js). Keep it simple and fast.
* **APIs:** `/api/series/<id>` returning `{series_id, geo_id, unit, observations:[{date,value}]}`.
* **Pipelines:** `make refresh` to rebuild gold layer; notebooks read gold.
* **Tests:** Smoke tests for endpoints and schema validation; at least one numeric sanity test per model (e.g., steady state exists and is stable).

---

## Suggested first three “visible learning” projects

1. **Supply–Demand Lab (national → KC housing)**

   * Minimal: linear curves, tax wedge, DWL.
   * KC: overlay HPI and inventory proxy; talk elasticities.
   * One slider: demand slope; one toggle: tax vs quota.

2. **CPI & HPI dashboard**

   * Fetch CPI & KC FHFA HPI; rebase to 100; show IRFs to simple shocks (toy).
   * Add affordability index (mortgage rate + income proxy).

3. **KC Unemployment Nowcast (first pass)**

   * LAUS series; dynamic regression vs naive; rolling error chart.
   * Write “What I learned about revisions.”

---

## Collaboration & pedagogy

* **Plain-English captions** for every figure: “What to look at; why it matters.”
* **Parameter cards** with hover tooltips linking to definitions.
* **“Try this” boxes** in notebooks: quick prompts for students to change a parameter and re-run.
* **Office hours notebooks**: short variants designed for workshops.

---

## 30/60/90 focus

* **30 days:** FRED CPI + KC HPI + Supply–Demand Lab + two clear experiment notes.
* **60 days:** LAUS/OEWS wired; KC snapshot page; Time-series VAR mini-lab.
* **90 days:** First causal study (DiD) on a local intervention; publish a tutorial post.

---

## What “done” looks like (quality bar)

* Notebook runs top-to-bottom; figures and CSVs saved; parameters declared up front.
* README explains **how to reproduce** in ≤3 steps.
* At least one test asserts a model property (e.g., capital converges).
* “Limits & Next” section exists; we never ship without it.

---

## Appendix: minimal math checklist (per model)

* Objective & constraints written explicitly.
* FOCs/KKT listed (when applicable).
* Stationary equilibrium / steady state defined.
* If linear solution: matrix form and stability condition noted.
* If estimated: identification statement + estimator and standard errors.

---

### Final note

We’re building a **learner’s lab**, not a black-box tool. Every plot should be something you can explain on a whiteboard, and every parameter should be one you can defend. If we keep models small, comparisons honest, and docs humane, the complexity will take care of itself—one layer at a time.
