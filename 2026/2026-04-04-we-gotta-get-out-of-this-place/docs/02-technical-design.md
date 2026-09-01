# Technical Design

## 1. Technical Strategy

The game will use a code-first architecture built in Rust with macroquad. The simulation should remain largely independent from rendering and player-facing UI. Content such as parts and missions should be externalized into data files wherever practical.

## 2. Stack

### Runtime
- Rust
- macroquad
- Cargo

### Likely supporting crates
- `serde`
- `ron` (chosen data format — supports comments, enums, and Rust types naturally)
- `thiserror` or `anyhow`
- `tracing` or `log`
- optional `egui-macroquad` for developer tools

## 3. Architectural Principles

1. **Fixed-step simulation** for physics stability and predictability
2. **Render and sim separation** so gameplay logic is testable and less tangled
3. **Data-driven content** for rapid balancing and mission tuning
4. **Logical rocket model first** rather than rigid-body part joints
5. **Tool-first development** so every later system is easier to debug

## 4. Runtime Layers

### 4.1 App Layer
Responsible for global state, screen routing, settings, and high-level transitions.

### 4.2 Simulation Layer
Responsible for all gameplay math and rules.

Includes:
- part aggregation
- rocket state
- flight integration
- atmosphere and drag
- orbit parameter calculations
- mission evaluation

### 4.3 UI Layer
Responsible for player-facing widgets, menus, HUD, and builder interactions.

### 4.4 Render Layer
Responsible for drawing the world, rocket, map, particles, and debug visuals.

### 4.5 Data Layer
Responsible for loading and validating parts, missions, save files, and balancing values.

### 4.6 Debug Layer
Responsible for overlays, event logs, scenario loading, tunables, and regression harnesses.

## 5. Proposed Folder Structure

```text
src/
  main.rs
  app/
    mod.rs
    state.rs
    screens.rs
    input.rs
    config.rs
  sim/
    mod.rs
    parts.rs
    rocket.rs
    stages.rs
    flight.rs
    orbit.rs
    atmosphere.rs
    mission.rs
    integrator.rs
  ui/
    mod.rs
    widgets.rs
    layout.rs
    builder_ui.rs
    hud_ui.rs
    map_ui.rs
    menu_ui.rs
    debrief_ui.rs
    theme.rs
  render/
    mod.rs
    world.rs
    vehicle.rs
    map.rs
    particles.rs
    debug_draw.rs
  data/
    mod.rs
    load.rs
    parts.rs
    validate.rs
    schema/
      mod.rs
      part.rs
      blueprint.rs
      physics_constants.rs
  debug/
    mod.rs
    overlay.rs
assets/
  parts/
    engine_sparrow.ron
    engine_hammer.ron
    tank_small.ron
    tank_medium.ron
    pod_mk1.ron
  presets/
    beater.ron
    featherweight.ron
    bruiser.ron
  physics_constants.ron
```

## 6. App States

Recommended top-level states:

- `MainMenu`
- `MissionSelect`
- `Builder`
- `Flight`
- `Map`
- `Debrief`
- `Paused`

Keep state transitions explicit and simple.

## 7. Simulation Model

## 7.1 Why a Logical Rocket Model

The first implementation should not simulate each part as a fully independent rigid body with joints. That adds a lot of instability and complexity too early.

Instead:

- the rocket is assembled as a structured set of parts and stages
- aggregate values are calculated from the structure
- stage activation changes the logical state
- visuals are drawn from the logical arrangement

This will make tuning, debugging, and testing much easier.

## 7.2 Rocket State

The runtime rocket state should include at least:

- world position
- velocity
- rotation angle
- angular velocity or simplified steering state
- current stage index
- remaining fuel by tank or stage
- throttle value
- control input state
- structural validity flags

## 7.3 Part Definitions

Each part should define:

- unique id
- display name
- category
- dry mass
- fuel capacity
- thrust
- efficiency / ISP
- drag coefficient
- cost
- sprite or draw id
- attachment rules
- optional flags like `is_command`, `is_recovery`, `is_decoupler`

## 7.4 Stage Model

Each stage needs:

- ordered activation sequence
- set of engines activated
- decouplers fired
- fuel source rules
- stage name or label for debug readability

## 7.5 Flight Integration

Use a fixed simulation timestep.

At each step:

1. read control state
2. compute current mass
3. determine active engine thrust
4. consume fuel
5. compute gravity
6. compute atmosphere density
7. compute drag
8. integrate acceleration to velocity
9. integrate velocity to position
10. update orbit parameters
11. evaluate mission progress

## 8. Physics Simplifications

The game should fake aggressively where it improves clarity, but stay physically grounded enough that decisions matter.

Approved simplifications for MVP:

- **Gravity field**: single-body inverse-square (not constant, avoids breaking orbit math later, trivially cheap).
- **Atmosphere**: exponential density model (e.g. `density = rho0 * exp(-alt / scale_height)`).
- **Steering**: simplified angular velocity (player directly controls rotation rate, not full mechanical torque).
- **Part flex**: none in MVP, rocket is rigid logical stack.
- **2D execution**: the game runs in full 2D space right from launch, avoiding 1D vertical constraints.

The design goal is meaningful decisions, not aerospace maximalism.

## 9. Orbit System

The orbit module should derive readable orbital parameters from the rocket state vector.

Responsibilities:

- determine apoapsis and periapsis
- classify whether current path is suborbital, orbital, escaping, or descending
- provide geometry for map rendering
- provide mission checks for stable orbit achievements

### Trajectory Preview

Decision: use a Kepler-analytic approximation rather than running a secondary simulation pass.

Rationale: the game uses a single-body gravity field, which makes analytic Keplerian orbits exact (or near-exact for the point in the trajectory where the preview begins). A secondary simulation pass adds CPU cost, latency, and accuracy mismatch.

If analytic preview proves meaningfully wrong during atmosphere-heavy ascent phases, revisit. For now, prefer the simpler path.

## 10. Builder System

The builder system should manage:

- placement and removal of parts
- parent-child attachment tree
- stage assignment and reordering
- aggregate stat calculation
- validation warnings

The builder should produce a serializable rocket blueprint that can be passed into flight.

## 11. Data Model Strategy

Prefer external data for:

- part definitions
- mission definitions
- tuning constants
- test rocket presets

Benefits:

- balance changes without code edits
- easier experimentation
- easier AI-assisted content generation
- less hardcoded project drift

## 12. Save Model

Plan for these save categories even if only part of them are implemented in MVP:

- settings
- saved rocket designs
- mission progression
- debug scenario presets

## 13. Debugging and Observability

Build these early:

- on-screen debug overlay
- structured event log
- scenario loader / test harness
- tunables panel for live parameter edits
- visual debug vectors and markers

## 14. Error Handling

The project should fail loudly in development when core data is invalid.

Examples:

- invalid part schema
- missing asset ids
- cyclic attachment graph
- empty stage sequence on a supposedly launchable rocket

Runtime player-facing failures should be graceful, but development-time failures should be obvious.

## 15. Performance Expectations

The project is intentionally low graphics and should be light on rendering demands.

Likely performance hotspots:

- trajectory prediction
- repeated stat aggregation if rebuilt every frame
- debug draw spam
- expensive UI layout or text rendering if poorly cached

Optimization guidance:

- cache derived rocket stats where practical
- compute trajectory previews on demand or at reduced cadence
- keep render passes simple

## 16. Recommended Implementation Order

1. App shell and fixed-step main loop
2. World coordinate system and camera
3. Hardcoded rocket flight toy
4. Rocket data schema and loading
5. Builder blueprint model
6. Stage and fuel logic
7. HUD and debrief shell
8. Orbit calculations and map screen
9. Mission system
10. Debug tools expansion

## 17. Risks

### 17.1 Scope Creep
Risk: adding too many simulation systems early.

Mitigation: keep orbit, builder, and mission loop as the definition of done for MVP.

### 17.2 Homemade UI Burden
Risk: building all UI from scratch eats time.

Mitigation: define a small reusable widget library and keep layouts strict and plain.

### 17.3 Overtuning Physics Too Early
Risk: spending too long polishing realism before the loop is fun.

Mitigation: optimize for understandable and tunable behavior first.

## 18. World Coordinate System

- Origin (0, 0) is the planet's center of mass.
- Y-up convention (positive Y moves away from the planet, negative Y towards the center).
- Measurements are in meters.
- The `macroquad` `Camera2D` uses a negative `zoom.y` to invert the default screen space (where Y goes down).
