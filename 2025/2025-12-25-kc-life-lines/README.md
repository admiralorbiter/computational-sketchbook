# KC: Life Lines — Data-Driven Opportunity & Life-Course Simulation (December 2025)

> **Category:** `[SKETCHBOOK EXPERIMENT / DATA-DRIVEN EDUCATIONAL SIMULATION & CAUSAL MODELING]`  
> **Date:** December 25–26, 2025  
> **Stack:** Python 3, Pandas, GeoPandas, Census ACS API, TIGER Geography  
> **Original Origin:** `admiralorbiter/life-sim` (HEAD: `56ec37e`)  

---

## 1. Project Vision & The Structural Opportunity Metaphor

*KC: Life Lines* explored an ambitious educational premise:
> *"Can you make structural opportunity playable without making individual outcomes feel predetermined?"*

```text
               ┌────────────────────────────────────────────────────────┐
               │                 KC: LIFE LINES (life-sim)              │
               │   "Simulate life trajectories conditioned on real-world │
               │    Kansas City Census and neighborhood opportunity data"│
               └──────────────────────────┬─────────────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        ▼                                 ▼                                 ▼
TRACT-LEVEL PUBLIC DATA           TRANSPARENT "DATA MODE"           TIME-DYNAMIC REHEARSAL
├── 477 KC Census Tracts          ├── Exposes exact data vintage    ├── Middle school to adulthood
├── 49 ACS Demog/Econ Variables   ├── Margins of error displayed    ├── Choices vs. shocks vs. place
└── TIGER Boundary joins          └── Models vs. observed inputs    └── Counterfactual reflection
```

---

## 2. The Core Epistemic Insight

> [!WARNING]
> **The Ecological Inference Boundary:**  
> Area-level statistics (e.g. 27% poverty in a Census tract) **do not** equal individual transition probabilities $P(	ext{outcome} \mid 	ext{traits}, 	ext{choices})$. The hard scientific challenge of life simulation is not collecting 20 datasets, but deriving defensible transition models without turning neighborhood averages into deterministic causal destiny.

---

## 3. Implementation Status: Built vs. Designed

- **BUILT:** Comprehensive Game Design Document (GDD v0.1), Data Source Catalog v0.1, regional configuration (9-county KC metro), Census ACS API ingestion (49 variables, margins of error), TIGER tract boundary normalization, and pipeline runner.
- **DESIGNED (NOT BUILT):** Cross-source integration (NCES, BLS, GTFS, CDC PLACES), derived Opportunity Index scoring, synthetic person generation, event decision tree, playable game UI, and counterfactual reflection screen.
