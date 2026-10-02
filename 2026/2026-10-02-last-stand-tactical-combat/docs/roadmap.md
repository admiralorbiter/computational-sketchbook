# Development Roadmap

---

## Phase 0 — Design (Current)
**Duration:** 1–2 days

- [x] Core concept and game design document
- [x] POC specification (Battle 001)
- [x] Nail down Battle 001 math: weapon stats, cover values, suppression curves
- [x] Define exact unit data (HP, speed, accuracy, weapon stats)
- [x] Define deployable data (cost, HP, cover value)
- [x] Define enemy archetype data
- [ ] Document AI behavior rules (individual level)

---

## Phase 1 — Skeleton Prototype
**Duration:** 1 weekend
**Engine:** Godot 4.x (GDScript)

### Milestone: "Rectangles That Fight"

Goal: Colored rectangles on a plain map. Units move, shoot, take damage, die.

- [x] Godot project setup
- [ ] Tile-based or simple map rendering
- [x] Unit entity with position, HP, team
- [ ] Basic movement (click to move, pathfinding)
- [ ] Weapon firing (raycast, damage calc)
- [ ] Unit death/incapacitation
- [x] Basic selection UI (click, box select)
- [ ] Camera controls (pan, zoom)

---

## Phase 2 — Core Combat
**Duration:** 1 week

### Milestone: "Combat Feels Like Something"

Goal: Cover and suppression make positioning matter.

- [ ] Cover system (walls block LOS, sandbags reduce damage)
- [ ] Suppression system (incoming fire → accuracy penalty → hunker)
- [ ] Weapon differentiation (MG suppresses, rifle is accurate, shotgun is close)
- [ ] Basic AI: enemies advance, use cover, shoot
- [ ] Preparation phase: place walls, sandbags, wire, mines
- [ ] Battle phase: real-time with pause

---

## Phase 3 — Orders & Intent
**Duration:** 1 week

### Milestone: "I'm Commanding, Not Babysitting"

Goal: Watch Sector mechanic works. Units execute orders autonomously.

- [ ] Watch Sector order (drag arc, units orient and engage within it)
- [ ] Hold Position order
- [ ] Fallback order (designate retreat position)
- [ ] Suppress Area order
- [ ] Control groups (Ctrl+1-9)
- [ ] Unit local AI (auto-cover, avoid grenades, reload)
- [ ] Order visualization (arcs, lines, zones on map)

---

## Phase 4 — Enemy Intelligence
**Duration:** 1 week

### Milestone: "They're Actually Trying"

Goal: Enemies behave like a coordinated force, not individual pathfinders.

- [ ] Enemy squad AI (groups move together)
- [ ] Enemy commander AI (picks approach, adapts)
- [ ] Reactive AI: avoid killzones after taking casualties
- [ ] Breacher behavior: target walls/doors
- [ ] Rusher behavior: charge through gaps
- [ ] Basic morale system (enemies retreat when losing badly)

---

## Phase 5 — Game Loop
**Duration:** 1 week

### Milestone: "I Want to Play Again"

Goal: Complete Briefing → Prep → Orders → Battle → After-Action loop.

- [ ] Briefing screen (scenario info, intel)
- [ ] Preparation phase timer / budget
- [ ] After-action report (casualties, timeline, events)
- [ ] Retry scenario button
- [ ] Scenario permutations (enemy comp/approach variants)
- [ ] Victory/defeat conditions
- [ ] Basic score/rating

---

## Phase 6 — Polish & Feel
**Duration:** 1–2 weeks

### Milestone: "It Looks and Sounds Like a Game"

- [ ] Sprite-based or improved visuals
- [ ] Tracer effects, muzzle flash
- [ ] Sound effects (gunfire, explosions, impacts)
- [ ] Hit/miss indicators
- [ ] Unit status icons (suppressed, wounded, reloading)
- [ ] Minimap
- [ ] Improved UI for orders and selection
- [ ] Debug overlay toggle (LOS rays, AI state, utility scores)

---

## Future Phases (Post-POC)

These are documented in the GDD but not scheduled:

- [ ] Multiple scenarios / maps
- [ ] Persistent roster (squad management between missions)
- [ ] Contract / mission selection system
- [ ] Equipment and loadout customization
- [ ] Conditional orders / doctrine editor
- [ ] Fire simulation
- [ ] Smoke simulation  
- [ ] Gas simulation
- [ ] Electricity / power grid
- [ ] Structural integrity / destruction
- [ ] Sound propagation
- [ ] Visibility / fog of war
- [ ] Weather system
- [ ] Intelligence / recon layer
- [ ] Additional enemy archetypes (horde, predators, machines, giant)
- [ ] Replay system
- [ ] Automated balance testing
- [ ] Modding support / data-driven content pipeline

---

## Technical Principles

1. **Simulation separate from presentation** — The sim says "projectile at x,y"; the renderer draws it.
2. **Data-driven everything** — Weapons, units, deployables, scenarios defined in data files, not code.
3. **Fixed-tick simulation** — 10–20 updates/sec, independent from rendering. Enables pause, speed control, replays, deterministic testing.
4. **Debug visualization is not optional** — LOS rays, cover values, AI state, target selection, suppression levels, utility scores.
5. **Orders are data** — Order objects with type, subjects, target, priority, conditions. Prepares for the conditional doctrine system.
6. **Three-level AI** — Individual (utility scoring) → Squad (coordination) → Commander (strategy). Never one giant behavior tree.
