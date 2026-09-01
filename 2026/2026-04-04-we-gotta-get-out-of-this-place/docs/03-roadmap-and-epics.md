# Roadmap and Epics

## 1. Planning Philosophy

This roadmap is designed for a solo developer. It assumes the project should be built as a sequence of playable slices, each of which improves confidence and preserves forward momentum.

## 2. Phases

## Phase 0 — Foundation (COMPLETED)
Goal: a clean executable shell with basic tooling.

Deliverables:
- [x] Cargo project initialized
- [x] app state routing
- [x] fixed-step simulation loop
- [x] input plumbing
- [x] basic camera and world rendering
- [x] debug overlay shell

Definition of done:
- [x] project launches reliably
- [x] can switch between placeholder screens
- [x] can render basic world coordinates and overlays

## Phase 1 — Vertical Slice Flight Toy (COMPLETED)
Goal: prove the game can feel good before building the whole shell.

Deliverables:
- [x] one hardcoded rocket
- [x] thrust, gravity, drag, and fuel consumption
- [x] launch / restart loop
- [x] minimal flight HUD
- [x] crash or mission-end condition

Definition of done:
- [x] rocket launches and can fail for understandable reasons
- [x] altitude and speed can be read clearly
- [x] player can meaningfully improve flight with controls

## Phase 2 — Data-Driven Rocket Model (COMPLETED)
Goal: stop hardcoding the vehicle and move to real game data.

Deliverables:
- [x] part schema
- [x] sample part library
- [x] rocket blueprint structure
- [x] stage model
- [x] aggregate stat calculation
- [x] design validation rules

Definition of done:
- [x] at least three valid rocket configurations can be described in data
- [x] invalid designs are detected cleanly

## Phase 3 — Builder (COMPLETED)
Goal: let the player assemble rockets instead of loading only presets.

Deliverables:
- [x] parts palette
- [x] placement/removal
- [x] selection and inspection
- [x] stage list UI
- [x] build stats summary
- [x] launch handoff into flight

Definition of done:
- [x] player can build a simple two-stage rocket
- [x] player can launch what they built
- [x] builder provides useful feedback

## Phase 4 — Orbit and Map (COMPLETED)
Goal: make the game feel like spaceflight rather than just altitude chasing.

Deliverables:
- [x] apoapsis and periapsis calculations
- [x] path classification
- [x] map screen
- [x] atmosphere boundary and orbit visualization
- [x] stable orbit check

Definition of done:
- [x] player can tell whether they are close to orbit
- [x] map view helps decision-making rather than just decorating the game

## Phase 5 — Mission Loop
Goal: turn the flight toy into an actual game.

Deliverables:
- mission definitions
- mission select screen
- objective tracker
- debrief screen
- retry flow
- mission unlocks or progression stub

Definition of done:
- game has a clear start-to-finish loop
- at least three mission types are playable

## Phase 6 — Tooling Expansion (COMPLETED)
Goal: make future development safer and faster.

Deliverables:
- [x] scenario loader
- [x] event log
- [x] tunables panel
- [x] visual debug modes
- [x] regression rocket preset set
- [x] time controls

Definition of done:
- [x] common bug classes can be reproduced quickly
- [x] tuning core constants no longer requires repeated code edits

## Phase 7 — Polish and Feel (COMPLETED)
Goal: add readability, feedback, and emotional payoff.

Deliverables:
- [x] better exhaust and stage effects
- [x] camera shake or impact feedback
- [x] improved debrief language
- [ ] audio placeholders (deferred)
- [x] UI refinement
- [x] clearer warnings and failure messages

Definition of done:
- [x] successful launches and failures both feel more satisfying
- [x] the game is easier to read at speed

## 3. Epics

## Epic A — Project Foundation (COMPLETED)
User value: stable development base

Stories:
- [x] As a developer, I can run the app and swap screens so I can work incrementally.
- [x] As a developer, I can inspect fixed-step timing so simulation bugs are easier to diagnose.

Acceptance criteria:
- [x] app runs with named states
- [x] fixed timestep is in place
- [x] debug overlay can render text and values

## Epic B — World Rendering and Camera
User value: readable world space

Stories:
- [x] As a player, I can see my rocket clearly during launch and ascent.
- [x] As a developer, I can zoom and pan in useful ways while testing. (Implemented via Adaptive Zoom)

Acceptance criteria:
- [x] rocket and planet can be drawn consistently
- [x] camera remains readable through ascent

## Epic C — Rocket Data and Parts
User value: meaningful design choices

Stories:
- [x] As a player, I can choose from a few part types with clear tradeoffs.
- [x] As a developer, I can add a new part by editing data rather than rewriting code.

Acceptance criteria:
- [x] parts load from external data
- [x] schema validation catches obvious errors

## Epic D — Rocket Builder
User value: player authorship

Stories:
- [x] As a player, I can assemble and edit a rocket.
- [x] As a player, I can see whether my design is obviously flawed before launch.

Acceptance criteria:
- [x] parts can be added and removed
- [x] stage assignment works
- [x] stats summary updates correctly

## Epic E — Flight Simulation
User value: meaningful flight and failure

Stories:
- [x] As a player, I can launch and control my rocket.
- [x] As a player, I can improve outcomes with better design and better flying.

Acceptance criteria:
- [x] thrust, drag, and gravity interact predictably
- [x] fuel drains correctly
- [ ] stage activation changes the rocket state correctly

## Epic F — Orbit and Map (COMPLETED)
User value: strategic understanding

Stories:
- [x] As a player, I can tell whether I am entering orbit.
- [x] As a player, I can use a map to plan flight decisions.

Acceptance criteria:
- [x] map displays readable trajectory
- [x] stable orbit can be detected

## Epic G — Missions and Debriefs (PARTIAL)
User value: clear goals and learning loop

Stories:
- [ ] As a player, I can attempt clear objectives. (Missions deferred)
- [x] As a player, I can learn from post-flight results.

Acceptance criteria:
- [ ] mission objectives track correctly
- [x] debrief identifies likely failure causes

## Epic H — Menus and HUD (COMPLETED)
User value: game readability and shell

Stories:
- [x] As a player, I can navigate into missions and back out safely.
- [x] As a player, I can read the numbers that matter while flying.

Acceptance criteria:
- [x] menus exist for main flow
- [x] HUD supports core launch and orbit tasks

## Epic I — Tooling and Debugging (COMPLETED)
User value: faster development and fewer regressions

Stories:
- [x] As a developer, I can load known test rockets quickly.
- [x] As a developer, I can inspect rocket state live while tuning.

Acceptance criteria:
- [x] scenario loader works
- [x] event log records meaningful events
- [x] tunables panel can change at least a few parameters live

## Epic J — Persistence
User value: reduced friction

Stories:
- As a player, I can save a rocket design.
- As a player, I can keep mission progress between sessions.

Acceptance criteria:
- save and load of at least one data category works reliably

## 4. Suggested Sequencing Within Epics

Front-load these because they reduce risk later:

- debug overlay
- event logging shell
- fixed timestep
- rocket preset loader
- basic acceptance smoke checklist

Do not front-load these:

- advanced economy systems
- complex unlock trees
- rich audio implementation
- full campaign framing text

## 5. Backlog Prioritization Rules

Use these rules when deciding what to do next:

1. Prefer features that prove the core loop
2. Prefer tools that reduce future debugging pain
3. Prefer data-driven improvements over hardcoded branches
4. Delay content breadth until systems are trustworthy
5. Delay polish until player decisions feel meaningful

## 6. Milestone Checklist

### Milestone 1 — “A Rocket Goes Up”
- app runs
- rocket launches
- fuel drains
- HUD works
- reset works

### Milestone 2 — “A Rocket Is Designed”
- builder works
- stats summary works
- stage assignment works
- launch uses built rocket

### Milestone 3 — “A Rocket Can Reach Orbit” (COMPLETED)
- [x] apoapsis and periapsis shown
- [x] map view works
- [x] orbit detection works

### Milestone 4 — “There Is a Game”
- mission select exists
- objectives work
- debrief works
- retry loop feels good

### Milestone 5 — “It Is Safe to Grow”
- debug suite exists
- regression rockets exist
- tuning tools exist

## 7. Nice-to-Have Post-MVP Epics

- moon or second body
- reentry heating
- payload fairings
- docking and rendezvous
- light progression economy
- challenge contracts
- stronger flavor writing
