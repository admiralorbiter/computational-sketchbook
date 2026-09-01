# Kansas City Open-Data Geographic Substrate (October 2025)

> **Category:** `[SKETCHBOOK EXPERIMENT / GEOSPATIAL INTELLIGENCE & OPEN-DATA ETL]`  
> **Date:** October 18–28, 2025  
> **Stack:** Python 3, Flask, SQLite, Leaflet.js, Pandas, Shapely, PyProj, GeoJSON  
> **Original Origin:** `admiralorbiter/map-data` (HEAD: `ef1067a`)  

---

## 1. Core Architectural Breakthrough: Geography as Universal Schema

*Map Data* represents the moment where **geography became the universal integration schema for heterogeneous public open data**:

> *"I have a place (Kansas City). What open datasets describe it?"*

```text
                     ┌──────────────────────────────────────────────┐
                     │          CENSUS TIGER BLOCK GROUP            │
                     │          (Universal Spatial Join Key)        │
                     └──────────────────────┬───────────────────────┘
                                            │
        ┌───────────────────┬───────────────┴───────────────┬───────────────────┐
        ▼                   ▼                               ▼                   ▼
PHYSICAL & CIVIC      MUNICIPAL OPS                   DEMOGRAPHICS        WORKFORCE DYNAMICS
├── OSM (3.1M Geoms)  ├── KCPD Crime Incidents        └── ACS (200+ vars  ├── LODES WAC (Workplace)
└── Land Bank Lots    ├── 311 Service Requests             across 1,717   ├── LODES RAC (Residence)
                      ├── Business Licenses                block groups)  └── LODES OD (Commute Flows)
                      └── Dangerous Buildings
```

### The Spatial Aggregation Engine:
Using `tools/compute_block_group_aggregations.py`, point and polygon records from disparate municipal and federal agencies were spatially joined into standardized Census Block Groups, making physical infrastructure, civic distress signals, demographics, and labor markets mutually comparable.

---

## 2. Downstream Evolutionary Lineage

The multi-source spatial breakthroughs here directly seeded three specialized descendants:
1. **`admiralorbiter/map`:** Next-generation MapLibre vector tile rendering and agent-based urban simulation.
2. **`admiralorbiter/marauders_map`:** Investigative knowledge graph mapping (entities $\leftrightarrow$ provenance $\leftrightarrow$ network graph $\leftrightarrow$ geography).
3. **`admiralorbiter/kc-industries`:** Specialized education $\leftrightarrow$ industry pipeline and workforce intelligence platform.

---

## 3. Preserved Artifacts

- **ETL Pipelines (`tools/`):** Dedicated normalization scripts for OSM, 311, Crime, Businesses, Dangerous Buildings, Land Bank, Census TIGER, ACS 5-Year, and LEHD/LODES.
- **Service Layer (`web/services/`):** Viewport query optimization, geocoding, and block-group aggregation endpoints.
- **Frontend (`web/templates/` & `web/static/`):** Multi-layer Leaflet UI with radius filtering, choropleth rendering, and demographic attribute querying.
