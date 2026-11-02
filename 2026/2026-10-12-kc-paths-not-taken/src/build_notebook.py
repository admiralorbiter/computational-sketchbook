"""Script to build the Jupyter notebook for Kansas City — Paths Not Taken."""

import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "name": "python",
        "version": "3.12.0"
    }
}

cells = []

# Cell 1: Markdown Title & Abstract
cells.append(nbf.v4.new_markdown_cell("""# Kansas City — Paths Not Taken
## A Data-Driven Game About Education, Careers, Geography, and Opportunity in Kansas City

> **Experiment:** `2026-10-12-kc-paths-not-taken`  
> **Mission 01:** *A Future in Healthcare* (Ruskin High School · Grade 10)  
> **Host Environment:** Python 3.12, Folium, Pandas, GeoJSON, Leaflet  
> **Companion Repositories:** [`life-sim-v2`](https://github.com/admiralorbiter/life-sim-v2), [`kc-industries`](https://github.com/admiralorbiter/kc-industries), [`delphi`](https://github.com/admiralorbiter/delphi), [`student_futures_lab`](https://github.com/admiralorbiter/student_futures_lab)  

---

## 1. Project Concept & The Epistemic Demarcation

Most civic and educational software collapses into one of two traps:
1. **The Static Report Card:** A dashboard displaying school test scores, attendance, or neighborhood median incomes that treats student outcomes as pre-ordained fates.
2. **The Predictive Ecological Trap:** Attempting to assign individual causal probabilities ($P(\\text{degree} \\mid \\text{census tract poverty})$), committing the **ecological fallacy** by pretending geographic aggregate correlations govern individual possibilities.

*Paths Not Taken* borrows the architectural principle articulated by Oliver (@Olliesiin) in the San Francisco Housing Game: **a puzzle game built directly on verified institutional rules, real geography, and scarce human resources**.

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

### The Three Epistemic Categories
To ensure integrity and prevent misleading claims, every assertion in this notebook and game belongs to one of three strictly labeled categories:
- `verified_fact`: Verified against official school district portals, DESE records, or higher education catalogs (with URLs and checked dates).
- `simulation_assumption`: A declared scenario rule (e.g. 2 Action Points per planning round) designed to make tradeoffs playable.
- `unknown`: Explicitly declared empirical or institutional unknowns (e.g. annual cohort seat caps, clinical transit schedules) that require inquiry rather than algorithmic fabrication."""))

# Cell 2: Code Setup & Imports
cells.append(nbf.v4.new_code_cell("""import sys
import json
from pathlib import Path
import pandas as pd
import folium

# Add project src to sys.path
SRC_DIR = Path.cwd().parent / "src" if (Path.cwd().parent / "src").exists() else Path.cwd() / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from kc_paths.data_loader import (
    load_locations,
    load_programs,
    load_sources,
    load_scenario,
    get_scenario_actions,
    get_scenario_endings
)
from kc_paths.engine import (
    create_game,
    get_available_actions,
    can_afford_action,
    apply_action,
    advance_round,
    evaluate_outcome,
    run_playthrough
)
from kc_paths.widget import render_playable_game

print(f"KC Pathways simulation substrate initialized successfully from: {SRC_DIR}")"""))

# Cell 3: Markdown Geospatial Foundation
cells.append(nbf.v4.new_markdown_cell("""---

## 2. The Verified Kansas City Geospatial & Educational Substrate

Vertical Slice 01 focuses on three verified physical locations in South and Midtown Kansas City:
1. **Ruskin High School** (`38.923090, -94.506760`): Comprehensive high school in Hickman Mills C-1 serving grades 9–12 (NCES ID: `291434003156`).
2. **Hickman Mills Real-World Learning Center** (`38.939400, -94.532954`): District center coordinating off-campus academies and workforce connections.
3. **MCC–Penn Valley Health Science Institute** (`39.064955, -94.590989`): Metropolitan Community College's specialized medical and allied health facility in Midtown KC.

Let's load the verified GeoJSON dataset and inspect its fields."""))

# Cell 4: Code Load Locations
cells.append(nbf.v4.new_code_cell("""locations_data = load_locations()

# Convert GeoJSON features into a clean inspection DataFrame
loc_rows = []
for f in locations_data["features"]:
    props = f["properties"]
    coords = f["geometry"]["coordinates"]
    loc_rows.append({
        "Location ID": f["id"],
        "Name": props["name"],
        "Category": props["category_label"],
        "Address": props["address"],
        "Coordinates": f"({coords[1]:.4f}, {coords[0]:.4f})",
        "Provenance": props["provenance_type"],
        "Role in Game": props["role_in_game"]
    })

df_locations = pd.DataFrame(loc_rows)
df_locations"""))

# Cell 5: Markdown Mapping
cells.append(nbf.v4.new_markdown_cell("""### Interactive Geospatial Map (Folium)

The map below illustrates the real geographic relationship across South KC and Midtown. Notice the spatial distance:
- Ruskin High School to the RWL Center: **~1.8 miles** northwest.
- Ruskin High School to MCC–Penn Valley HSI: **~10.5 miles** north along the Broadway/Troost corridor.

This distance establishes why transportation is not a theoretical detail, but a physical constraint on off-campus participation."""))

# Cell 6: Code Folium Map
cells.append(nbf.v4.new_code_cell("""# Center map between South KC and Midtown
kc_map = folium.Map(location=[38.995, -94.545], zoom_start=11, tiles="CartoDB dark_matter")

colors = {
    "ruskin-high": "dodgerblue",
    "rwl-center": "lightgreen",
    "mcc-penn-valley-hsi": "purple"
}

icons = {
    "ruskin-high": "graduation-cap",
    "rwl-center": "briefcase",
    "mcc-penn-valley-hsi": "plus"
}

for f in locations_data["features"]:
    props = f["properties"]
    lon, lat = f["geometry"]["coordinates"]
    loc_id = f["id"]
    
    popup_html = f\"\"\"
    <div style='font-family: sans-serif; font-size: 12px; width: 220px;'>
        <b style='color: #0284c7;'>{props['name']}</b><br/>
        <span style='color: #64748b;'>{props['category_label']}</span><br/>
        <p style='margin-top: 4px;'>{props['address']}</p>
        <span style='background: #e0f2fe; color: #0369a1; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 10px;'>
            {props['provenance_type']}
        </span>
    </div>
    \"\"\"
    
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=props["name"],
        icon=folium.Icon(color=colors.get(loc_id, "blue"), icon=icons.get(loc_id, "info-sign"))
    ).add_to(kc_map)

# Draw transit pathway connection lines
coords_ruskin = [38.923090, -94.506760]
coords_rwl = [38.939400, -94.532954]
coords_mcc = [39.064955, -94.590989]

folium.PolyLine(
    [coords_ruskin, coords_rwl],
    color="#38bdf8",
    weight=3,
    dash_array="5, 10",
    tooltip="District Shuttle Corridor (1.8 miles)"
).add_to(kc_map)

folium.PolyLine(
    [coords_ruskin, coords_mcc],
    color="#a855f7",
    weight=3,
    dash_array="5, 10",
    tooltip="Regional Transit / Commute Corridor to Midtown (10.5 miles)"
).add_to(kc_map)

kc_map"""))

# Cell 7: Markdown Programs & Verification
cells.append(nbf.v4.new_markdown_cell("""---

## 3. Verified Educational Programs & Institutional Rules

Let's examine the verified program records:
- **Health Start Academy**: Ruskin High School career pathway partnering with MCC-Penn Valley. Offers high school dual credit and eligibility for Certified Nursing Assistant (CNA), Pharmacology Technician, and Phlebotomy credentials. Recruitment window: January–April.
- **Early College Academy**: Hickman Mills program providing up to 42 transferable credits through MCC-Longview with district-paid tuition (eligibility: 3.0 unweighted GPA + Accuplacer placement).
- **MCC Healthcare Pathways**: Postsecondary training ranging from short-term certifications (EMT, phlebotomy, CNA) to 2-year Associate of Applied Science degrees (Registered Nursing, Radiologic Technology)."""))

# Cell 8: Code Load Programs
cells.append(nbf.v4.new_code_cell("""programs_data = load_programs()

prog_rows = []
for p in programs_data["programs"]:
    prog_rows.append({
        "Program Name": p["name"],
        "Institution / Host": p.get("host_school") or p.get("institution"),
        "Grades": str(p["serves_grades"]),
        "Key Opportunities": "; ".join(p["opportunities"][:2]),
        "Unknowns (Requiring Inquiry)": "; ".join(p.get("unknowns", [])[:2]),
        "Source URL": p["verified_source_url"]
    })

df_programs = pd.DataFrame(prog_rows)
df_programs"""))

# Cell 9: Markdown Simulation Engine Rules
cells.append(nbf.v4.new_markdown_cell("""---

## 4. The Game Engine: Turns, Action Points, and Prerequisite Graphs

In Mission 01, the player has a fixed budget of **3 Planning Rounds** with **2 Action Points (AP) per round** (total 6 AP maximum). Unspent points expire at round end.

The player chooses one of two starting transportation conditions:
- `reliable`: Student has dependable family or personal transport.
- `needs-coordination`: Student relies on transit or shuttles. Preparing an off-campus Health Start inquiry requires an additional 1-AP transportation investigation.

### Complete Action Catalog (7 Actions)
1. `speak_counselor` (1 AP, Round 1+, Ruskin High): Consultation with high school counselor.
2. `investigate_health_start` (1 AP, Round 1+, RWL Center): Research academy opportunities and credentials.
3. `investigate_transport` (1 AP, Round 1+, Ruskin High): Logistical inquiry (available for `needs-coordination`).
4. `prepare_health_start_inquiry` (2 AP, Round 1+, RWL Center): Terminal preparation for Health Start. Requires counselor + program research + transport documentation (if coordination profile).
5. `explore_mcc_health` (1 AP, Round 2+, MCC–Penn Valley): Discover postsecondary training in Round 2.
6. `compare_college_options` (1 AP, Round 2+, MCC–Penn Valley): Compare short-term certificates vs. AAS degrees.
7. `draft_postgrad_plan` (1 AP, Round 2+, MCC–Penn Valley): Terminal preparation for postsecondary pathway."""))

# Cell 10: Code Action Table
cells.append(nbf.v4.new_code_cell("""actions = get_scenario_actions()

act_rows = []
for a in actions:
    act_rows.append({
        "Action ID": a.id,
        "Title": a.title,
        "Cost (AP)": a.cost_ap,
        "Round Available": a.round_available,
        "Location": a.location_id,
        "Prerequisites": ", ".join(a.requires) if a.requires else "None",
        "Transport Specific": "Yes (Coordination)" if a.requires_transport_profile or a.requires_transport_investigation else "No"
    })

df_actions = pd.DataFrame(act_rows)
df_actions"""))

# Cell 11: Markdown Programmatic Simulations
cells.append(nbf.v4.new_markdown_cell("""---

## 5. Programmatic Simulation Tracing & Counterfactual Replay

Let's use the pure Python simulation engine (`kc_paths.engine`) to trace three distinct playthroughs and analyze the resulting outcomes.

### Playthrough A: The Health Start Academy Route (Reliable Transport)
- **Round 1 (2 AP):** Speak with Counselor (1 AP) + Investigate Health Start (1 AP).
- **Round 2 (2 AP):** Prepare Health Start Inquiry (2 AP). **Plan Completed!**
- **Round 3 (2 AP):** Explore MCC Health Programs (1 AP) + Compare College Options (1 AP)."""))

# Cell 12: Code Playthrough A
cells.append(nbf.v4.new_code_cell("""playthrough_a = {
    1: ["speak_counselor", "investigate_health_start"],
    2: ["prepare_health_start_inquiry"],
    3: ["explore_mcc_health", "compare_college_options"]
}

state_a = run_playthrough(playthrough_a, transport_profile="reliable")
print(f"=== PLAYTHROUGH A (Reliable Transport) ===")
print(f"Final Status: {state_a.status}")
print(f"Outcome Title: {state_a.outcome.title}")
print(f"Status Badge: {state_a.outcome.status_badge}")
print(f"Completed Actions: {state_a.completed_actions}")
print(f"Real-World Takeaway: {state_a.outcome.real_world_takeaway}")"""))

# Cell 13: Markdown Playthrough B
cells.append(nbf.v4.new_markdown_cell("""### Playthrough B: The Postsecondary MCC Route (Reliable Transport)
- **Round 1 (2 AP):** Speak with Counselor (1 AP) + Investigate Health Start (1 AP).
- **Round 2 (2 AP):** Explore MCC Health Programs (1 AP) + Compare College Options (1 AP).
- **Round 3 (2 AP):** Draft Postgraduation Plan (1 AP). **Plan Completed!**"""))

# Cell 14: Code Playthrough B
cells.append(nbf.v4.new_code_cell("""playthrough_b = {
    1: ["speak_counselor", "investigate_health_start"],
    2: ["explore_mcc_health", "compare_college_options"],
    3: ["draft_postgrad_plan"]
}

state_b = run_playthrough(playthrough_b, transport_profile="reliable")
print(f"=== PLAYTHROUGH B (MCC Postsecondary Route) ===")
print(f"Final Status: {state_b.status}")
print(f"Outcome Title: {state_b.outcome.title}")
print(f"Status Badge: {state_b.outcome.status_badge}")
print(f"Completed Actions: {state_b.completed_actions}")
print(f"Real-World Takeaway: {state_b.outcome.real_world_takeaway}")"""))

# Cell 15: Markdown Playthrough C
cells.append(nbf.v4.new_markdown_cell("""### Playthrough C: Transportation Constraint Replay (Counterfactual Comparison)
Now run the exact same intent as Playthrough A, but under **Transportation Needs Coordination**:
- If the student attempts to prepare Health Start without investigating transportation, the engine strictly blocks the action.
- The student must spend 1 AP on `investigate_transport`.
- This increases the total cost of Health Start from 4 AP to 5 AP, forcing real trade-offs."""))

# Cell 16: Code Playthrough C
cells.append(nbf.v4.new_code_cell("""# Successful Health Start under Coordination requires:
playthrough_c = {
    1: ["speak_counselor", "investigate_health_start"],
    2: ["investigate_transport", "explore_mcc_health"],
    3: ["prepare_health_start_inquiry"]
}

state_c = run_playthrough(playthrough_c, transport_profile="needs-coordination")
print(f"=== PLAYTHROUGH C (Transportation Coordination Route) ===")
print(f"Final Status: {state_c.status}")
print(f"Outcome Title: {state_c.outcome.title}")
print(f"Total Actions: {len(state_c.completed_actions)}")
print(f"Notice the tradeoff: The player had to spend 5 AP out of 6 AP to secure Health Start, leaving no budget to compare college options!")"""))

# Cell 17: Markdown Interactive Widget
cells.append(nbf.v4.new_markdown_cell("""---

## 6. Interactive Playable Game UI (Embedded in Notebook)

The cell below renders the complete, interactive client-side game widget directly inside this notebook. You can:
1. Select your starting transportation profile (**Reliable** vs. **Needs Coordination**).
2. Click locations on the interactive Kansas City map to view addresses and verified descriptions.
3. Spend Action Points to complete counseling, research, and planning tasks across 3 planning rounds.
4. Open the **Why?** drawer to inspect official source URLs and data provenance.
5. Reach the terminal debrief screen and test counterfactual replays side-by-side!"""))

# Cell 18: Code Interactive Widget Display
cells.append(nbf.v4.new_code_cell("""# Render the complete interactive game directly in the notebook cell
render_playable_game(height=780)"""))

# Cell 19: Markdown Analytical Synthesis
cells.append(nbf.v4.new_markdown_cell("""---

## 7. Analytical Synthesis: Feasibility as Gameplay

### Key Findings from Vertical Slice 01:
1. **Mathematical Trade-Off Proof:** Completing Health Start requires 4 AP (reliable) or 5 AP (coordinated); completing the MCC postsecondary plan requires 3 AP. Because the mission caps total planning at 6 AP, a student **cannot complete both full pathways**. Prioritization is structurally necessary.
2. **The Transportation Penalty:** The need to coordinate transportation costs 1 AP (16.7% of the entire planning budget). This small friction is enough to eliminate exploratory time, preventing students without private vehicles from comparing college options while pursuing high school academies.
3. **Epistemic Truthfulness:** No individual success probabilities were generated. No student was told they had a "65% chance of passing." The game communicates reality through **institutional requirements, deadlines, and coordination costs**.

---

## 8. Development Roadmap: From Notebook to Citywide Simulation

| Version | Scope | Key New Substrate | Status |
| :--- | :--- | :--- | :--- |
| **Slice 01 (This Notebook)** | 1 School, 2 Pathways, 3 Rounds | Verified NCES, District Portals, GeoJSON | **Complete** |
| **Slice 02: Regional Labor Evidence** | Occupational wage benchmarks & O*NET skills | `kc-industries` BLS OEWS / O*NET crosswalk | Next Phase |
| **Slice 03: Public Transit Substrate** | Real bus travel times and transfer penalties | RideKC static GTFS transit schedule feed | Planned |
| **Slice 04: Attendance Boundaries** | 9-County school assignment & feeder patterns | NCES EDGE / Missouri DESE boundary layers | Planned |
| **Slice 05: Multi-Year Longitudinal Progression** | Middle School $\\to$ High School $\\to$ Postsecondary | Synthesis of `student_futures_lab` & `delphi` | Future |

*To transition this experiment into a standalone production application, the pure TypeScript game engine from `docs/GAME_RULES.md` and `docs/VERTICAL_SLICE_01.md` will be scaffolded into a dedicated Vite + React + MapLibre repository.*"""))

nb.cells = cells

# Save notebook
out_path = Path(__file__).resolve().parent.parent / "notebooks" / "01_kc_paths_not_taken.ipynb"
with open(out_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Jupyter notebook written successfully to: {out_path}")
