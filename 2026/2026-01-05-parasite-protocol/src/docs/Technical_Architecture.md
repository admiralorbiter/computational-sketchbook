# Technical Architecture — Parasite Protocol (Rust + Bevy)

Date: 2026-01-05

This doc describes the intended technical architecture for a 2D Bevy implementation.

---

## 1) Engine / Framework
- **Language:** Rust (stable)
- **Engine:** Bevy (ECS + renderer + input + audio + UI)
- **Primary Bevy features used**
  - ECS (entities/components/resources/schedules)
  - States (AppState, RunState)
  - Events (signal propagation, combat, UI)
  - Plugins (feature isolation)
  - 2D rendering (sprites + meshes for overlays)
  - UI (Bevy UI or a UI crate integration if desired later)

### Optional supporting crates (when needed)
- **serde + ron / json:** data-driven content
- **bevy_egui:** debug tools + in-dev panels
- **bevy_asset_loader:** structured asset loading + states
- **pathfinding:** only if you choose explicit graph algorithms (vesicle routing)
- **rand / rand_pcg:** seeded runs
- **profiling:** puffin or tracy-client (later)

---

## 2) Architecture pattern
### ECS-first, plugin-oriented
- **Feature plugins** own components, resources, events, and systems.
- Systems are **pure transformations** over query + resources.
- Use **events** for cross-system communication (combat → infection, receptor triggers → circuit propagation).

### Why ECS fits this game
- Many small entities (enemies, vesicles, infection nodes, modules)
- Multiple overlapping simulation layers (combat + logistics + infection)
- Easy performance scaling via schedule organization and batching

---

## 3) High-level module map (plugins)

### App / bootstrap
- `app.rs`: Bevy App, window config, global states
- `plugins/mod.rs`: registers all plugins

### Core
- `core_time`: pause/speed, fixed timestep, sim tick counters
- `core_camera`: pan/zoom, bounds
- `core_selection`: mouse picking, hover tooltips, placement previews
- `core_save_seed`: run seed + deterministic setup (optional)

### Simulation plugins
- `arena_map`: membrane + organelles + nav grid
- `enemy`: enemy spawning, movement, AI, boss behavior
- `combat`: damage, status effects, death
- `manufacturing`: ribosome queue + assembly + inventory
- `shipping`: vesicles + routing + delivery states
- `tracks`: microtubule/actin placement + repair + route graph
- `circuits`: graph model, triggers, relays, effectors
- `infection`: infection field update + nodes + debuffs
- `economy`: ATP/blocks/stress/membrane integrity updates
- `waves`: threat budget, wave state machine, recovery choices
- `adaptation`: strategy telemetry + next-wave trait selection

### Presentation plugins
- `render_entities`: sprites/animations
- `render_overlays`: circuit/logistics/infection overlays (toggleable)
- `ui_hud`: HUD + panels + recovery screen
- `audio`: SFX/music routing (optional in MVP)

### Debug / dev tools
- `debug_panel`: spawn enemies, add resources, show fields, force adaptations

---

## 4) State model (Bevy States)
Recommended minimal states:
- `AppState`: `MainMenu | RunSetup | InRun | RunSummary`
- `RunState` (sub-state while `InRun`): `Planning | Combat | Recovery | Defeat | Victory`

Pause/speed is handled by a **TimeScale resource**, not by state transitions.

---

## 5) Fixed timestep & determinism
### Simulation clock
- Run simulation-critical systems on a **fixed timestep** (e.g., 30–60 Hz).
- Rendering can be variable; overlays interpolate visuals if desired.

### Determinism targets (choose your level)
- **MVP:** “stable enough” runs; allow minor nondeterminism.
- **Preferred (good for roguelite seeds):**
  - Use a single seeded RNG resource (PCG)
  - Fixed timestep ordering for simulation systems
  - Avoid order-dependent iteration where it matters (use stable sorting)

---

## 6) Data-driven content strategy
**Goal:** add enemies/modules/gene cards without touching code.

Recommended:
- Store content as **RON** (Rusty Object Notation) for readability.
- Load into `Assets<T>` or custom registries at startup.

Core registries:
- `EnemyDefRegistry`
- `ModuleDefRegistry`
- `GeneCardRegistry`
- `BossDefRegistry`
- `WaveTable` (optional)
- `AdaptationTraitRegistry`

Validation at load:
- Fail fast with readable errors (missing IDs, invalid fields, cycles).

---

## 7) Performance targets & budgets
### Targets
- **FPS:** 60 fps baseline on mid-range hardware; 120 fps “nice to have”.
- **Simulation update:** fixed tick (30–60 Hz) without spikes.

### Budgets (MVP guidance)
- **Entities:** 2,000–10,000 total (depends on implementation)
- **Enemies on screen:** 200–800 (swarm heavy) as a stress test
- **Infection field resolution:** 128×128 or 256×256 grid (tunable)
- **Memory:** keep under 1–2 GB on PC; aim far lower in practice

### Performance hotspots to watch
- Infection diffusion updates (keep to 5–10 Hz or use dirty regions)
- Pathfinding (avoid per-enemy A* if possible)
- UI/layout thrash (minimize dynamic UI rebuilds)
- Excessive event spam in circuits (use gating and batching)

---

## 8) Platform considerations
### MVP platforms
- Windows / macOS / Linux (desktop)

### Later
- Steam Deck: treat like “mid-range desktop”; ensure readable UI scaling.
- Consider GPU fillrate: overlays should be efficient (simple meshes/lines).

---

## 9) System scheduling (recommended order)
Within fixed-timestep schedule:
1. Input → selection/placement intents (buffered as commands)
2. Manufacturing progress
3. Shipping / vesicle movement
4. Track updates (repairs, congestion metrics)
5. Enemy spawn & movement
6. Combat resolution (damage, statuses, deaths)
7. Infection update (at lower frequency; may run every N ticks)
8. Economy update (ATP/stress/membrane integrity)
9. Circuit triggers & propagation (may be event-driven)
10. Cleanup/despawn + telemetry logging

---

## 10) Definition of Done (Architecture)
- [x] Project compiles and runs with plugin separation.
- [x] Fixed timestep sim with pause/speed controls.
- [ ] Content loaded from data files with validation.
- [ ] Debug panel exists to spawn enemies and adjust resources.
- [ ] No single system dominates frame time in MVP stress test.
