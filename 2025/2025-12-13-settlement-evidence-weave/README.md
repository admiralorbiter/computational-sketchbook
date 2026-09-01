# Settlement — Evidence Weave & Systemic Bureaucracy (December 2025)

> **Category:** `[SKETCHBOOK EXPERIMENT / SYSTEMIC BUREAUCRACY & EVIDENCE PUZZLE MECHANICS]`  
> **Date:** December 13, 2025  
> **Stack:** TypeScript, Phaser 3, Vite, Vitest  
> **Original Origin:** `admiralorbiter/settlement` (HEAD: `56ec37e`)  

---

## 1. Project Vision & The Evidence Weave Metaphor

*Settlement* explored turning institutional struggle, contested records, and legal/civic bureaucracy into game mechanics:

```text
               ┌────────────────────────────────────────────────────────┐
               │              THE EVIDENCE WEAVE PUZZLE                 │
               │   "Assemble valid proof chains before information      │
               │    environment is consumed by institutional taint"     │
               └──────────────────────────┬─────────────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        ▼                                 ▼                                 ▼
EVIDENCE TILES                    CORRUPTION / TAINT                FAILURE-FORWARD PRECEDENTS
├── Documents & Testimony         ├── Contagious spreading         ├── "Struggle alters the rules"
├── ChainDetector (valid links)   ├── Contested evidence status     ├── Disclosure Precedents
└── Target Proof Requirements     └── Turn-limited race             └── Persistent Tier Protection
```

---

## 2. Core Conceptual Innovations

1. **Information Asymmetry as Spatial Puzzles:** Assembling proof chains (connecting documents and testimony) while systemic corruption spreads across adjacent cells.
2. **Failure-Forward Institutional Precedents:** Rather than simple reset or "+5% stat" meta-progression, losing or winning establishes institutional precedents (e.g. Disclosure Precedent speeding up audits, Tier Protection setting minimum standing floors) that alter the rules of subsequent runs.
3. **The 3-Axis Resource Model:** *Capacity* (logistics/volunteers), *Standing* (institutional legitimacy), and *Momentum* (public trust/collective power).
4. **Legacy Contract Tower:** Preserves a prototype where players physically climb and push contractual clauses (`IF`, `THEN`, `AND`, `OR`, `AUDIT`).

---

## 3. Implementation Status: Built vs. Designed

- **BUILT:** Phaser 3 / Vite / TypeScript shell, Evidence Weave grid, tile placement rules, chain detection logic, taint spread engine, hand management, HUD/input controllers, deterministic seeded setups, and Vitest suites.
- **DESIGNED (NOT BUILT):** Civic Board indicators (Resolver Scrutiny, Heat, Media Narrative), full day/night narrative VN loop, Resolver boss hearing, and 10-phase campaign.
