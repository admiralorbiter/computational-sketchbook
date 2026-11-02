# Kansas City — Paths Not Taken (`2026-10-12-kc-paths-not-taken`)

> **Category:** `[SKETCHBOOK EXPERIMENT / DATA-DRIVEN EDUCATIONAL & GEOSPATIAL PATHWAYS GAME]`  
> **Date:** October 12, 2026  
> **Focal Geography:** South Kansas City (Hickman Mills C-1) & Midtown KC  
> **Host Stack:** Python 3.12, Jupyter (`nbformat`), Pandas, GeoJSON, Folium, HTML5/Leaflet, Pytest  
> **Companion Repositories:** [`life-sim-v2`](https://github.com/admiralorbiter/life-sim-v2), [`kc-industries`](https://github.com/admiralorbiter/kc-industries), [`delphi`](https://github.com/admiralorbiter/delphi), [`student_futures_lab`](https://github.com/admiralorbiter/student_futures_lab)  

---

## 1. Project Concept & Pedagogical Philosophy

*Kansas City — Paths Not Taken* is a data-driven opportunity and career-pathway exploration game grounded in real Kansas City geography, verified school programs, and institutional constraints.

Rather than presenting a static reporting dashboard with game mechanics grafted on afterward, or attempting to predict an individual student's destiny based on neighborhood census tract demographics (an ecological fallacy that previously stalled early predictive simulations), *Paths Not Taken* adapts the design principle of Oliver's (@Olliesiin) San Francisco Housing Game:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       THE PATHWAYS PROGRESSION CHAIN                        │
│                                                                             │
│   [ PLACE ]  ──►  [ SCHOOL ]  ──►  [ PROGRAM ]  ──►  [ CREDENTIAL ] ──► [ CAREER ]
│   Hickman          Ruskin HS        Health Start       CNA / Pharm Tech    Healthcare
│   Mills            (Grades 9-12)    (MCC-Penn Valley)  AAS Nursing         Allied Health
│                                                                             │
│   Progression is governed by:                                               │
│   • Verified Institutional Rules (Eligibility GPAs, application windows)    │
│   • Physical Geography & Transit (Locations, commute, shuttle friction)     │
│   • Resource Scarcity (Planning time / Action Points, trade-offs)           │
└─────────────────────────────────────────────────────────────────────────────┘
```

The game does not tell a student what their future will be. It allows players to discover **what becomes possible, difficult, expensive, or blocked** when specific circumstances, policies, or decisions change.

---

## 2. The Core Epistemic Demarcation

To prevent misleading claims or causal overreach, all information displayed in the notebook and game is partitioned into three strictly labeled categories:

1. `verified_fact`: Supported by official school district portals, DESE records, or higher education catalogs (with URLs and checked dates).
2. `simulation_assumption`: A declared scenario rule (e.g. 2 Action Points per planning round) designed to make trade-offs playable.
3. `unknown`: Explicitly declared empirical or institutional unknowns (e.g. annual cohort seat caps, clinical transit schedules) that require inquiry rather than algorithmic fabrication.

> [!IMPORTANT]
> **No Demographic Determinism:**  
> The simulation rejects assigning individual success probabilities ($P(\text{degree} \mid \text{race}, \text{poverty}) = 0.65$). Feasibility is the primary gameplay objective: can the player assemble a coherent, evidence-informed pathway within explicit institutional and logistical constraints?

---

## 3. Vertical Slice 01: "A Future in Healthcare"

The first playable vertical slice takes place in South Kansas City with a fictional 10th-grade student attending **Ruskin High School**:

- **Budget:** 3 Planning Rounds $\times$ 2 Action Points (AP) per round = **6 AP maximum**. Unspent AP expires at round end.
- **Starting Choice (Replay Variant):**
  - **Reliable Transportation:** Dependable personal or family transit for off-campus programs.
  - **Transportation Needs Coordination:** Relies on public transit or district shuttles; requires an extra 1-AP logistics inquiry before preparing a Health Start inquiry.
- **Action Catalog (7 Actions):**
  - `speak_counselor` (1 AP, Round 1+, Ruskin High)
  - `investigate_health_start` (1 AP, Round 1+, RWL Center)
  - `investigate_transport` (1 AP, Round 1+, Ruskin High; available for coordination profile)
  - `prepare_health_start_inquiry` (2 AP, Round 1+, RWL Center; requires counselor + program research + transport documentation if Profile B)
  - `explore_mcc_health` (1 AP, Round 2+, MCC–Penn Valley)
  - `compare_college_options` (1 AP, Round 2+, MCC–Penn Valley)
  - `draft_postgrad_plan` (1 AP, Round 2+, MCC–Penn Valley)
- **Three Deterministic Endings:**
  1. `health_start_prepared`: High-school academy pathway plan completed.
  2. `postgrad_plan_prepared`: Postsecondary college exploration plan completed.
  3. `still_exploring`: Partial progress debrief highlighting the opportunity cost of uncoordinated exploration.

---

## 4. Directory Architecture

```text
2026-10-12-kc-paths-not-taken/
├── README.md                           # Observatory overview and architectural summary
├── docs/
│   ├── VERTICAL_SLICE_01.md            # Detailed vertical slice 01 specification
│   ├── GAME_RULES.md                   # Formal state machine definition and budget proofs
│   └── DATA_SOURCES.md                 # Verified factual registry, URLs, and checked dates
├── data/
│   ├── locations.geojson               # Verified coordinates for Ruskin, RWL Center, and MCC-Penn Valley
│   ├── programs.json                   # Verified program facts for Health Start, Early College, and MCC
│   ├── sources.json                    # Provenance registry with URLs and checked dates
│   └── scenarios.json                  # Scenario configuration for Mission 01
├── src/
│   ├── build_notebook.py               # Programmatic Jupyter notebook generation script
│   └── kc_paths/
│       ├── __init__.py                 # Package exports
│       ├── types.py                    # Typed data models (GameState, Action, Outcome, etc.)
│       ├── data_loader.py              # Strict JSON / GeoJSON data loaders and validators
│       ├── engine.py                   # Pure deterministic simulation engine and state transitions
│       └── widget.py                   # Self-contained Leaflet / HTML5 playable widget for notebooks
├── notebooks/
│   └── 01_kc_paths_not_taken.ipynb     # Interactive research and playable game notebook
└── tests/
    └── test_game_engine.py             # 16-test automated verification suite
```

---

## 5. Verification & Test Suite

All core engine mechanics and data integrity guarantees are covered by automated unit tests (`tests/test_game_engine.py`):

```powershell
pytest 2026/2026-10-12-kc-paths-not-taken/tests/test_game_engine.py -v
```

- **16 of 16 tests passing:**
  - 1 AP action deduction and 2 AP budget rejection under 1 AP remaining
  - Duplicate action prevention
  - Prerequisite graph enforcement
  - Transportation coordination constraint enforcement
  - Terminal ending evaluations (`health_start_prepared`, `postgrad_plan_prepared`, `still_exploring`)
  - Clean replay state isolation
  - GeoJSON coordinate bounding box and provenance tagging
  - Zero unverified program claims

---

## 6. How to Play & Inspect

1. **In Jupyter or VS Code:**  
   Open [`notebooks/01_kc_paths_not_taken.ipynb`](notebooks/01_kc_paths_not_taken.ipynb). Run all cells to inspect the geospatial maps, trace programmatic playthroughs, and interact with the embedded Leaflet game board directly in the notebook cell.
2. **Side-by-Side Replay:**  
   After completing your first run under "Reliable Transportation," select "Replay / Change Circumstances" to run the scenario under "Needs Coordination." The game renders a side-by-side comparison illustrating how the 1-AP transit friction reshapes feasible pathway choices.
3. **Transition to Standalone Web App:**  
   When ready to expand beyond the notebook, the pure TypeScript specification in [`docs/VERTICAL_SLICE_01.md`](docs/VERTICAL_SLICE_01.md) and [`docs/GAME_RULES.md`](docs/GAME_RULES.md) is structured for immediate scaffolding into a standalone Vite + React + MapLibre GL repository.
