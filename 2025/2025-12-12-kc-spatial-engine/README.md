# Kansas City Spatial Engine & MapLibre Vector Substrate (December 2025)

> **Category:** `[SKETCHBOOK EXPERIMENT / GEOSPATIAL VECTOR INFRASTRUCTURE & MULTI-LAYER CHOROPLETHS]`  
> **Date:** December 12–23, 2025  
> **Stack:** Node.js, Express, MapLibre GL JS, MBTiles, Python (Pandas/GeoPandas), SQLite / GeoPackage  
> **Original Origin:** `admiralorbiter/map` (HEAD: `eac9abf`)  

---

## 1. Project Purpose & Lineage Role

*Map* was created to test the technical feasibility of hosting a high-performance, self-contained local geospatial rendering platform capable of layering arbitrary civic datasets over vector maps of the Kansas City metropolitan area:

```text
               ┌────────────────────────────────────────────────────────┐
               │           KANSAS CITY SPATIAL ENGINE (map)             │
               │   "Local OSM vector tiles as a multi-layer visual      │
               │    substrate for external civic and census datasets"   │
               └──────────────────────────┬─────────────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        ▼                                 ▼                                 ▼
LOCAL MBTILES TILE SERVER         MAPLIBRE 3D CLIENT                CENSUS & CIVIC ETL
├── Local vector tile serving     ├── 3D Building Extrusions        ├── Python ACS / TIGER scripts
├── SpatialService layer query    ├── Dynamic layer toggles         ├── ZIP-code GeoJSON export
└── POI / place feature filter    └── 4 Census ZIP choropleths      └── Node REST data endpoints
```

---

## 2. Implemented Capabilities: Built vs. Designed

- **BUILT:**
  - *Vector Tile Server (`src/spatial-service.js`):* Node/Express server parsing MBTiles vector tiles, converting layers back to GeoJSON on demand, and filtering by bounding box.
  - *MapLibre 3D Web Client (`client/index.html`):* 3D building extrusions, terrain, OSM roads/water/landuse toggles, address search, and interactive POI markers.
  - *Census Choropleth Engine (`scripts/`, `src/data/sources/census-source.js`):* Python ETL pipeline ingesting ACS Census demographic/economic variables by ZIP code, paired with an interactive frontend switcher for median income, total population, home values, and median age.
- **DESIGNED (NOT BUILT):**
  - Generalized multi-source pipeline for real-time weather and transportation feeds.
  - Phase 3 agent-based economic/demographic simulation engine (stubs only).

---

## 3. The Lineage Transition to KC Industries

*Map* proved the technical vector substrate. Its architectural lessons (MapLibre rendering, multi-metric choropleths, spatial queries) were subsequently absorbed into **KC Industries** (`admiralorbiter/kc-industries`), where the substrate was anchored to a concrete regional economic and education mission.
