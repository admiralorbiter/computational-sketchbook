# The Great Exchange — Experiential Emergence of Money Simulation (September 2025)

> **Category:** `[SKETCHBOOK EXPERIMENT / INTERACTIVE PEDAGOGY PROTOTYPE]`  
> **Date:** September 11 – October 13, 2025  
> **Stack:** HTML5 / Nunjucks, CSS3, JavaScript (Canvas, Chart.js, Custom 27KB Agent Simulation Engine)  
> **Original Origin:** `admiralorbiter/Portfolio` (`src/great-exchange/`)  

---

## 1. The Core Educational Thesis

*The Great Exchange* is an interactive, 6-chapter narrative learning environment exploring the **emergence of commodity money** from first principles:

> *"Can an abstract economic model be converted into an experiential historical learning environment where learners experience the friction that motivates money rather than merely being told why money exists?"*

### The Pedagogical Sequence:
```text
Historical Narrative ──► Direct Barter Friction ──► Prediction ──► Interactive Simulation ──► Observed Outcome ──► Reflection ──► Next Economic Layer
```

---

## 2. Implemented Chapters & Simulations

1. **Chapter 1: The Problem (`01-the-problem.md`):** Ancient Mesopotamia barter friction & double coincidence of wants.
2. **Chapter 2: First Exchange (`02-first-exchange.md`):** Basic barter agent simulation (`simulations/basic-barter/`).
3. **Chapter 3: Storage Costs (`03-storage-costs.md`):** Perishability, carrying cost, and trade durability (`simulations/storage-costs/`).
4. **Chapter 4: Speculation (`04-speculation.md`):** Accepting goods you do not consume in anticipation of future trade.
5. **Chapter 5: Emergence (`05-emergence.md`):** Kiyotaki–Wright search equilibrium simulation (`simulations/emergence-patterns/`).
6. **Chapter 6: Modern Connections (`06-modern-connections.md`):** Fiat money, trust networks, and digital currencies.

---

## 3. Epistemic Findings & Simulation Boundaries

> [!WARNING]
> **Didactic Demonstration vs. Validated Research Model:**  
> While conceptually brilliant as an instructional interface, the simulation engine (`simulation-engine.js`) contains intentional simplifications:
> 1. **Commodity Conservation Bug:** In speculative trades, Agent 1 receives Agent 2's good while Agent 2's inventory was left unchanged in development commits (violating conservation of goods).
> 2. **Hardcoded Emergence Bias:** For the emergence patterns mode, barley receives hardcoded acceptance bonuses (starting at 60%, escalating to 90% as circulation grows with a low 0.15 threshold). The model encodes rather than organically discovers barley becoming money.
> 3. **Non-Reproducible Seeds:** Uses unseeded `Math.random()`. Treat as a **didactic instructional animation**, not an empirical economic simulation.
