# Candy Capitalism — Emergent Multi-Agent Economy & Information Propagation (October 2025)

> **Category:** `[SKETCHBOOK EXPERIMENT / AGENT-BASED SIMULATION & GAME DEV]`  
> **Date:** October 25–26, 2025  
> **Stack:** Python 3, Pygame, Pytest  
> **Original Origin:** `admiralorbiter/candy-capitalism` (HEAD: `c8d4052`)  

---

## 1. Core Systems & Empirical Thesis

*Candy Capitalism* is a 27-hour playable agent-based systems simulation wrapped in a Halloween game theme. It investigates whether heterogeneous autonomous agents acting on imperfect private beliefs generate an emergent market that can be manipulated indirectly via information, incentives, and supply shocks:

> *"Can local autonomous interactions generate a systemic market equilibrium without an explicit top-down model?"*

### The Three-Layer Valuation Model:
1. **Real Value ($V_{	ext{real}}$):** Objective underlying baseline utility.
2. **Believed Value ($V_{	ext{believed}}$):** Individual agent subjective valuation, modified by personality (Value Investor, Hoarder, Panic Seller) and inventory.
3. **Market Price ($P_{	ext{market}}$):** Aggregate price emerging from local pairwise transactions.

---

## 2. Lineage Connections

```text
1. ECONOMICS / REHEARSAL LINEAGE:
   econ-explorer (Formal Supply/Demand Curves)
        │
        ▼
   The Great Exchange (Interactive Narrative Kiyotaki-Wright Simulation)
        │
        ▼
   Candy Capitalism (Autonomous Heterogeneous Agents Creating the Market)

2. INFORMATION & MULTI-AGENT PROPAGATION (Precursor to Terrarium):
   Ground Truth ──► Private Belief ──► Rumor Transmission ──► Mutation ──► Behavioral Shift ──► Systemic Outcome
```

---

## 3. Implementation Status & Artifacts

- **BUILT & PLAYABLE (Sprints 0–3):** Procedural neighborhood generator, autonomous kids (movement, pathfinding, inventory, preferences), houses dispensing candy, autonomous pairwise trading, player possession mechanics, forced bad trades, and supply manipulation spells (curse/bless).
- **TEST SUITE:** 16+ unit and integration test modules (`tests/`) validating economy bookkeeping, inventory math, AI house selection, and spatial collision.
- **DESIGNED / SKELETON:** Rumor propagation (`src/systems/rumor_system.py`), debt cascades, behavioral contagion, and natural cartel formation.
