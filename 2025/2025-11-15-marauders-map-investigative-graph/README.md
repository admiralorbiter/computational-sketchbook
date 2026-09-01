# Marauder's Map — Investigative Knowledge Graph & Spatial Provenance (November 2025)

> **Category:** `[SKETCHBOOK EXPERIMENT / INVESTIGATIVE KNOWLEDGE GRAPHS & SPATIAL PROVENANCE]`  
> **Date:** November 15–16, 2025  
> **Stack:** Python 3, Flask, SQLite (FTS5), HTML5/JS  
> **Original Origin:** `admiralorbiter/marauders_map` (HEAD: `22ae5ff`)  

---

## 1. Project Vision & The Convergence of Space and Evidence

*Marauder's Map* represents the conceptual convergence of two major lines of inquiry:
1. **Semantic Knowledge Graphs (`skien`):** Entities, claims, typed epistemic relationships, and evidence sources.
2. **Open-Data Geographic Substrates (`map-data`):** Resolving entities and institutions to physical place.

```text
               ┌────────────────────────────────────────────────────────┐
               │                MARAUDER'S MAP CONVERGENCE              │
               │   "Entities exist simultaneously in spatial territory  │
               │    and relational influence space with source evidence"│
               └──────────────────────────┬─────────────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        ▼                                 ▼                                 ▼
GEOGRAPHIC SUBSTRATE              RELATIONAL TOPOLOGY               EVIDENTIARY PROVENANCE
├── Physical Addresses & Lots     ├── Entity Networks               ├── Source URL & Timestamp
└── Spatial Bounding Viewports    ├── Relationship Roles            ├── Strength ≠ Confidence
                                  └── Explainable "Power Paths"     └── Explanatory Post-Mortems
```

---

## 2. Core Conceptual Innovations

1. **Relationship Strength vs. Evidence Confidence:**
   - *Strength:* How influential or intense the connection is (e.g., Major Donor vs. Casual Associate).
   - *Confidence:* The certainty of the evidence backing the claim (e.g., Verified SEC Filing vs. Uncorroborated Lead).
2. **Explainable "Power Paths":** Rather than simple unweighted shortest paths ($A 	o B 	o C$), algorithms compute influence paths weighted by edge strength, evidence certainty, recency, and intermediary centrality—always paired with an *Explain Panel*.
3. **Transparent Evidence Chips:** Every asserted edge requires a source citation or defaults to Draft status.

---

## 3. Implementation Status: Built vs. Designed

- **BUILT (Slice 1):** Flask application factory, SQLite database with FTS5 search table and synchronization triggers, Entity CRUD (create, read, update, soft-delete), search endpoints, and end-to-end pytest suite.
- **DESIGNED (Slices 2–7):** Relationships table, Leaflet map module, graph network visualizer, Wikipedia/Wikidata entity enrichment, Power Path calculations, and multi-tenant workspaces.
