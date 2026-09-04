# Kansas City Concentric Gastronomy Explorer

> **Category:** `[SKETCHBOOK EXPERIMENT / GEOSPATIAL GASTRONOMY]`  
> **Date:** 2026-09-04  
> **Origin:** Standalone single-page spatial probe (`src/index.html`)  
> **Stack:** HTML5, Tailwind CSS (CDN), Chart.js (CDN), HTML5 Canvas, Vanilla JS, LocalStorage  

---

## 1. Concept & Spatial Framework

The **Kansas City Concentric Gastronomy Explorer** is a spatial decision-support system and culinary inquiry tool anchored at a residential epicenter: **1609 E 75th Terrace, Kansas City, MO** (the Waldo / South Troost corridor).

Rather than evaluating dining options through generic city-wide listicles or algorithmic map search, the explorer models gastronomy as expanding concentric rings of accessibility:
- **Zone 1: Hyper-Local Corridor (0–2 miles):** 18 spots encompassing the Waldo and South Troost corridors. Characterized by high density of independent bakeries, Palestinian delis, street taco trucks, legacy soul food institutions, and neighborhood taverns.
- **Zone 2: Near Outskirts & Enclaves (2–5 miles):** 14 spots spanning Brookside, Crestwood, Fairway, and Prairie Village. Features elevated casual bistros, oyster bars, craft custard, and long-standing regional Italian kitchens.
- **Zone 3: Metropolitan Destination Dining (5+ miles):** 10 spots reaching into Midtown, the Crossroads Arts District, River Market, and Overland Park. Centers on competition barbecue pits, chef-driven tasting rooms, and innovative fusion concepts.

---

## 2. What Was Built

The application is implemented as an entirely self-contained single-page web artifact (`src/index.html`) featuring five interactive modules:

1. **Concentric Spatial Radar (HTML5 Canvas):**
   - A custom polar coordinate visualizer mapping dining nodes onto 3 concentric isochrone rings around the 75th Terrace epicenter.
   - Interactive mouse click detection and visual highlight of the active venue without requiring third-party map API keys or heavy vector tile pipelines.
2. **"What Should I Eat Today?" Craving Wheel:**
   - A multi-criteria recommendation engine filtering by radius (Zone 1, 2, 3, or all), budget tier (`$`, `$$`, `$$$`), and craving vibe (Smoky BBQ, Italian/Pasta, Mexican/Tacos, Bakery/Sweets, Mediterranean, Chicken/Burgers).
   - Generates random curated recommendations with one-click bookmarking or directory location.
3. **Visual Analytics (Chart.js):**
   - **Cuisine Distribution by Zone:** Stacked bar chart showing the spatial shift in dining types from hyper-local delis and fast-casual to destination fine dining.
   - **Price Accessibility Breakdown:** Doughnut chart analyzing economic accessibility across the 42 venues (28.6% `$`, 42.9% `$$`, 28.6% `$$$`).
4. **Comprehensive Filterable Directory:**
   - Dual-view interface toggling between responsive card grid and structured tabular format.
   - Real-time text search indexing venue names, street addresses, cuisines, and signature items.
5. **Priority Hit List & Detail Modal:**
   - Persistent `localStorage`-backed bookmarking system allowing users to queue venues for future dining trips.
   - Modal views revealing report commentary, signature dishes, and historical highlights (e.g., gas-station gyros, plate breaking, competition briskets).

---

## 3. Archaeological Significance & Future Evolution

### Why It Belongs in the Sketchbook
This prototype represents an ideal specimen of the *Computational Sketchbook* philosophy: a zero-dependency, single-file browser probe solving a tangible daily-life problem (choice fatigue conditioned on physical proximity) through spatial geometry and clean visual design. It avoids premature database overhead while fully validating the data model and user experience.

### Future Work & Database Expansion
As noted during creation, this sketch serves as the direct precursor to a full-stack database-backed application:
- **Relational Schema:** Transitioning `RESTAURANT_DATA` into SQLite / PostgreSQL tables with normalized schemas for venues, cuisines, price tiers, hours of operation, and visit histories.
- **True GIS Isochrones:** Integrating real drive-time and bike-time polygon isochrones (via OpenStreetMap and Valhalla/OSRM) rather than idealized Euclidean distance rings.
- **Personal Log & Rating Ledger:** Tracking dining dates, tasting notes, order receipts, and personal dish rankings.
