# Econ Explorer — Interactive Economic Rehearsal Laboratory & Progressive Disclosure Model (August 2025)

> **Category:** `[SKETCHBOOK EXPERIMENT / INTERACTIVE REHEARSAL ARCHITECTURE]`  
> **Date:** August 10, 2025 (~4 hour sprint)  
> **Stack:** Python 3, Flask, Pydantic, FRED API, HTML5 / CSS3 / JavaScript (Chart.js / Canvas), Pytest  

---

## 1. What Was the Idea?
To build an interactive economics learning and modeling laboratory from first principles—bridging empirical economic data (FRED API ingestion) with formal mathematical models and guided interactive web simulations.

---

## 2. What Was Actually Built?
1. **FRED Data Pipeline:** Functioning multi-tier data layer (bronze raw $\to$ silver normalized $\to$ gold rebased series) pulling national CPI and Kansas City Home Price Index data.
2. **Mathematical Supply & Demand Engine:** Backend closed-form solver calculating equilibrium $(p^*, q^*)$, consumer/producer surplus, per-unit/ad-valorem taxation, quotas, price controls, and deadweight loss triangles with strict numerical test assertions.
3. **Interactive Narrative Labs:** 7 browser-based simulation templates utilizing progressive disclosure:
   - Supply & Demand Basics (`lab_supply_basics.html`)
   - Market Equilibrium & Comparative Statics (`lab_market_equilibrium.html`)
   - Consumer Theory & "Consumer's Journey" (`lab_consumer_theory.html`)
   - Producer Theory & Cost Minimization (`lab_producer_theory.html`)
   - Game Theory & Strategic Matrices (`lab_game_theory.html`)
   - Auction Mechanisms (`lab_auctions.html`)
   - Economic Growth Dynamics (`lab_growth_models.html`)

---

## 3. Core Conceptual Inventions Preserved

### A. The Experimental Operating System (`strategy_philosphy.md`)
```text
Question ──► Minimal Model ──► Data ──► Code ──► Experiments ──► Compare ──► Explain
```
- Start tiny; add one friction at a time.
- Write explicit assumptions down.
- Compare predictions to data rather than proclaiming conclusions.
- End every experiment with what surprised you and one concrete next question.

### B. The Pedagogical Learner Loop (`TEACHING_GUIDE.md`)
```text
Explore ──► Predict (before seeing outcome) ──► Run ──► Explain ──► Check ──► Extend
```
- Forces active cognitive commitment (prediction) prior to model manipulation.
- Progressive disclosure: controls and formalisms appear only as the conceptual need arises.

---

## 4. Archaeological & Epistemic Failure Mode: Conceptual Replication Before Validation

- **Rapid Pattern Proliferation:** After establishing the interactive narrative pattern in Lab 1 (Supply & Demand), the remaining 6 labs were scaffolded and added in the final commit before Lab 1 had completed formal QA.
- **Smoke Tests vs. Mathematical Rigor:** Later labs were verified only by HTTP 200 response smoke tests checking for title strings rather than closed-form mathematical assertions.
- **Aspirational Claims:** Pedagogical target claims (e.g., "30% improvement in post-test retention") were aspirational design goals, not evaluated empirical outcomes.
