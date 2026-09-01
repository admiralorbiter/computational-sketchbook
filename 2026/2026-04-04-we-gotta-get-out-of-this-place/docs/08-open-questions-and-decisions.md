# Open Questions and Decisions

## 1. Decisions Already Made

### Chosen stack
- Rust
- macroquad
- custom UI
- custom simulation

### Chosen presentation
- 2D only for version 1
- low graphics
- readable, engineering-first visuals

### Chosen product direction
- mission-first with some sandbox flavor
- one-planet MVP
- builder + flight + map + debrief loop

### Chosen development stance
- front-load tooling
- keep simulation mostly logical rather than rigid-body-driven
- preserve a code-first workflow

### Steering model: Simplified angular velocity
Instead of complex internal forces/torque simulation, MVP steering lets players directly influence angular velocity. This bypasses moment-of-inertia tweaking at this stage.

### Data format: RON
RON (Rusty Object Notation) is the chosen format for all external data files (parts, missions, balancing constants, presets). It handles Rust enums, inline comments, and trailing commas naturally. `serde_ron` will be used for serialization. Do not introduce JSON for game content files.

### Debug tools: runtime toggle
Debug tools are enabled via a runtime toggle (e.g., `F3` key or `--debug` CLI flag), not a compile flag. Debug code is always compiled in but hidden by default. This preserves the ability to share a build and request reproduction of an issue.

### Builder interaction: click-to-add, stacked vertically
The player selects a part from the palette and clicks a valid attachment point to place it. The rocket grows vertically. No drag-and-drop for MVP.

### Trajectory preview: Kepler-analytic approximation
The map view trajectory preview uses an analytic Keplerian orbit calculation rather than a secondary simulation pass. The single-body gravity field makes this exact at the preview start point. Revisit only if the preview misleads players during atmosphere-heavy phases.

### render module naming: `vehicle.rs` not `rocket.rs`
The render module for drawing the rocket uses `render/vehicle.rs` to avoid ambiguity with `sim/rocket.rs`.

### World coordinate system
Origin (0, 0) is the planet center, units are meters, using a Y-up convention (negative `zoom.y` in macroquad camera).

### Planet placeholder parameters
Radius `600,000m`, Atmosphere Height `70,000m`, Surface Gravity `9.81 m/s²`. Configured in `config.rs`.

### Fixed timestep rate
60 Hz (`1.0/60.0`). Balanced for physics accuracy and performance.

## 2. Open Design Questions

### 2.1. Orbit Complexity

**Question**: How strict is "stable orbit" detection? Should it be geometric (periapsis > atmosphere) or time-held (staying up there for N seconds)?

**Decision**: **Geometric only** (`periapsis > atmosphere_height`). The Keplerian orbit math is precise for this gravity field. If the geometric boundary is cleared, the orbit is guaranteed stable unless thrust is applied. This avoids confusing players with timers. *Implemented in Phase 4.*

### 2.2 Delta-v Readout

**Question**: Should the builder show raw delta-v numbers or abstract ratings?

**Decision**: **Show raw ΔV**. The identity of the game rests on engineering clarity. Tsiolkovsky's equation will drive the numbers per-stage and display in the builder UI right panel during Phase 5/6.

### 2.4 Progression Model
- Pure mission unlocks only?
- Part unlocks?
- Light economy later?

### 2.5 Recovery Model
- Should safe landing matter in MVP outside specific missions?
- Are parachutes enough, or should simple impact survivability rules exist?

## 3. Open UX Questions

- How much text should missions use?
- Does the tone lean fully dry and reflective, or slightly playful?
- How much telemetry is too much for the default HUD?

## 4. Open Technical Questions

- How often should trajectory preview update for performance and clarity? (Format chosen: Kepler-analytic. Cadence TBD.)

## 5. Future Feature Parking Lot

These ideas are intentionally not MVP requirements, but worth keeping on the horizon:

- reentry heating
- more celestial bodies
- docking
- payload fairings
- science / contracts
- audio identity pass
- richer flavor writing in mission text

## 6. How to Use This Doc

Whenever a new feature idea appears, decide whether it is:

- a current milestone task
- a post-MVP feature
- a parking lot idea
- or a scope threat

This doc should help keep the project honest.

### Phase 3 Builder Interactions and Rendering

**Q: How does a player change a part's stage in the builder?**
**Decision**: Left/Right arrow keys to nudge the stage number on the selected part. Arrows aren't used otherwise in builder mode, and the mental model is immediate ("push part to the right means later stage").
**Status**: Decided and implemented.

**Q: Should the center Build Canvas be a text list or a rocket silhouette?**
**Decision**: We bypassed the text list and built the small rendered rocket silhouette immediately to provide better context. Uniquely colored rects and sizes are stacked proportionally based on the part type to roughly simulate the rocket build visually.
**Status**: Decided and implemented.

**Q: Does `main.rs` need a `GameState` refactor now that `builder_session` exists alongside `RocketState`?**
**Decision**: Log as Tech Debt. We will hold off on adding `GameState` struct wrapping in Phase 3. The current file is still understandable, and we will wait to pull `GameState` formally in Phase 4 / Phase 5 when mission state complicates it further.
**Status**: Decided and implemented. (Added in Phase 6.5)

### Phase 7 Visual Polish Decisions

**Q: Should particles persist and emit during time warp?**
**Decision**: Yes. To keep the visual trail continuous, particle emission scales up linearly with the time warp factor. 
**Status**: Decided and implemented.

**Q: Should the starfield be fixed to the screen or parallax with the camera?**
**Decision**: Given orbital distances, a slight parallax effect (`0.04` factor relative to camera target) makes deep space feel more alive without being distracting.
**Status**: Decided and implemented.

**Q: How does the debrief screen trigger?**
**Decision**: Auto-transition. Once the flight status reaches `Landed` or `Crashed`, the app automatically switches to the Debrief state to show peak flight stats.
**Status**: Decided and implemented.
