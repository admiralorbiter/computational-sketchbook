# Origin: Last Stand Tactical Combat (`2026-10-02-last-stand-tactical-combat`)

- **Original Repository:** `computational-sketchbook`
- **Creation Date:** October 2, 2026
- **Primary Technology:** Godot 4.7.2, GDScript, Fixed-Tick Simulation (20 TPS)
- **Extracted To:** `computational-sketchbook/2026/2026-10-02-last-stand-tactical-combat/`
- **Consolidation Date:** 2026-10-02
- **Preservation Status:** Active Prototype / Scaffolded & Tested

---

## Retrospective Summary

*Last Stand: Tactical Combat* is an exploratory combat simulation distilling the best parts of RimWorld's raid defense into a focused, highly replayable tactical game without colony chore simulation.

### Core Architectural Accomplishments:
1. **Three-Layer Command Model:** Separates Engineering (battlefield prep), Doctrine (intent-based sector/fallback orders), and Command (real-time exceptional micro).
2. **Fixed-Tick Simulation vs. Presentation:** Strict separation between authoritative 20-tick/sec mathematical simulation (`Unit`, `WeaponData`, `CombatResolver`, `Suppression`, `Cover`) and rendering/presentation.
3. **Data-Driven Combat Formulas:** Integrated combat math cross-referenced with RimWorld Combat Extended, XCOM, and real-world military doctrine (Find, Fix, Flank, Finish), featuring directional cover and dynamic suppression saturation.
4. **Signature Mechanics:** StarCraft-style control language (`1–9` control groups, box selection) unified with spatial intent orders (`W + drag` Watch Sector arcs, `F` Suppress Area, `R` Fallback).

### Why It Belongs in the Computational Sketchbook:
It captures the transition from conceptual game design discourse into an immediate, testable Godot 4 architecture with clean decoupling between AI utility scoring, order data structures, and combat math.
