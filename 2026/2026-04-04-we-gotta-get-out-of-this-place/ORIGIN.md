# Origin: We Gotta Get Out of This Place (`we_gotta_get_out_of_this_place`)

- **Original Repository:** `https://github.com/admiralorbiter/we_gotta_get_out_of_this_place`
- **Creation Date:** April 4, 2026 (~3 hours visible development / ~10 commits)
- **Primary Technology:** Rust, Macroquad, Miniquad, RON (Rusty Object Notation)
- **Extracted To:** `computational-sketchbook/2026/2026-04-04-we-gotta-get-out-of-this-place/`
- **Consolidation Date:** 2026-09-01
- **Preservation Status:** Concept Extracted / Standalone Repo Set to Private & Archived (Safe for Deletion)

---

## Retrospective Summary

*We Gotta Get Out of This Place* is a 2D rocket engineering and orbital physics sandbox built in Rust over a single afternoon in April 2026.

### Core Architectural Accomplishments:
1. **2D Flight & Orbital Physics:** Fixed-step integration calculating active thrust, ISP mass flow, variable vessel mass, atmospheric drag, and inverse-square planetary gravity.
2. **Orbital Telemetry & State Classifier:** Calculates orbital energy, angular momentum, eccentricity, apoapsis/periapsis, and classifies trajectories into *Stable Orbit*, *Suborbital*, *Escaping*, *Ballistic*, and *Descending*.
3. **External Blueprint Builder:** Loads modular parts from external RON schemas, computes total $\Delta V$, and launches custom configurations into the live physics engine.

### Why It Belongs in the Computational Sketchbook:
The prototype successfully proved the physical sandbox and builder loop ($\text{Build} \to \text{Launch} \to \text{Diagnose} \to \text{Retry}$), but stopped before implementing Phase 5 (Missions / Objectives / Progression). Because it serves as an exploratory physics probe rather than an active multi-month research workspace, it is preserved permanently in the Computational Sketchbook.
