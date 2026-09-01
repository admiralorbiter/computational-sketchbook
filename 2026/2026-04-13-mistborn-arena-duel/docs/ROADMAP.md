# Roadmap

## Roadmap Philosophy
The roadmap prioritizes **playable slices** over framework-heavy setup. Every milestone should produce something testable in-game.

## Phase 0 - Preproduction

### Goals
- Lock the core game shape
- Define technical approach
- Establish repo structure and conventions
- Reduce design ambiguity before implementation

### Deliverables
- README
- game vision
- mechanics doc
- technical architecture doc
- roadmap
- character briefs
- stage brief
- initial backlog

### Exit Criteria
- project scope written down
- MVP locked
- first technical assumptions accepted
- no major uncertainty around genre shape

---

## Phase 1 - Project Bootstrap

### Goals
- Create runnable Phaser 3 TypeScript project
- Establish scene pipeline
- Add debugging utilities and project conventions

### Tasks
- initialize repo
- configure Vite + TypeScript
- define lint/format setup
- create base Phaser config
- create boot scene
- create preload scene
- create test combat scene
- add placeholder asset loading
- add debug config toggles
- define constants and shared enums

### Deliverables
- app boots in browser
- test scene renders
- placeholder sprites/boxes display
- hot reload works

### Exit Criteria
- one scene playable
- dev environment stable
- team can add gameplay features without project setup churn

---

## Phase 2 - Movement Vertical Slice

### Goals
- Build a reliable player controller
- Validate the feel of local movement

### Features
- horizontal run
- jump
- air control
- dash
- facing direction
- landing detection
- idle/run/jump/fall state transitions

### Tasks
- create player entity shell
- implement movement component
- implement input mapping
- add jump buffering
- add coyote time if needed
- add dash behavior
- clamp velocities
- add gravity tuning values
- add debug overlay for position/velocity/state

### Deliverables
- 2 local players can move around stage
- movement values are editable from config/data
- movement is readable and responsive

### Exit Criteria
- movement feels good with placeholder visuals
- no major jitter or controller conflicts
- core state transitions are stable

---

## Phase 3 - Combat Foundation

### Goals
- Implement attack flow independent of final visuals
- Prove that combat interactions feel readable

### Features
- light attack
- heavy attack
- attack startup/active/recovery
- hitbox spawning
- hurtbox detection
- damage
- knockback
- hit pause
- hitstun
- block

### Tasks
- design move data schema
- implement move executor
- implement hitbox manager
- implement hurtbox registration
- create collision resolution rules
- implement attack state transitions
- implement block rules
- add hit reaction states
- add knockback application
- add hitstop and screen shake hooks
- add combat debug overlay

### Deliverables
- 2 placeholder fighters can hit each other
- attacks have timing and resolution
- light vs heavy interactions are testable

### Exit Criteria
- 1v1 sparring is playable
- combat can be tuned through data, not only code
- no frame-breaking bugs in core combat loop

---

## Phase 4 - Signature Abilities

### Goals
- Give each character a unique and readable identity
- Validate theme-inspired mechanics

### Character A: Coinshot/Lurcher-inspired duelist
- coin shot projectile
- anchor-aware push/pull mobility
- metal anchor interaction

### Character B: Windrunner-inspired vanguard
- lashing burst movement
- aerial directional movement
- slam / knock-up attack

### Tasks
- define per-character move list
- implement projectile system
- implement anchor point system
- implement directional special inputs
- implement resource spending rules
- add ability VFX placeholders
- add UI feedback for special readiness/resource

### Deliverables
- both characters feel mechanically distinct
- each has 2 viable specials
- stage supports identity mechanics

### Exit Criteria
- players can clearly describe the difference between the two fighters
- abilities are readable in motion
- no character requires final art to understand their gameplay

---

## Phase 5 - Match Loop and UI

### Goals
- Turn the sandbox into a real playable match

### Features
- round start
- round end
- score / rounds won
- timer optional
- win condition
- rematch flow
- pause flow
- health bars
- resource UI

### Tasks
- implement match state machine
- implement round reset positions
- implement spawn/reset pipeline
- build HUD
- build result overlay
- add pause handling
- add rematch prompt
- add debug toggles for instant restart

### Deliverables
- complete local best-of-3 flow
- UI communicates essential state

### Exit Criteria
- full match playable from start to finish
- state transitions are bug-resistant
- match reset is reliable

---

## Phase 6 - Tooling, Balance, and Polish

### Goals
- Make the prototype easy to tune and test repeatedly

### Features
- training mode toggles
- input display
- frame/state display
- collision box display
- damage logs
- tuning pass

### Tasks
- build debug panel
- expose config values
- support move data hot tuning where feasible
- create balance spreadsheet or JSON notes
- add simple sound cues
- add placeholder VFX polish
- clean timing windows

### Deliverables
- playtest-ready build
- team can diagnose gameplay problems quickly

### Exit Criteria
- at least 3-5 playtest rounds can be run without major failure
- bugs are reproducible with debug info

---

## Phase 7 - Future Multiplayer Preparation

### Goals
- Reduce risk before actual networking work begins

### Features
- input recording
- frame logging
- deterministic-ish update review
- state serialization experiments

### Tasks
- record input stream per frame
- implement match replay serialization prototype
- review all random sources
- separate visual effects from gameplay decisions
- document network assumptions

### Exit Criteria
- local simulation is sufficiently clean to evaluate room-based multiplayer later

---

## Suggested Timeline by Build Order
1. bootstrap
2. movement
3. combat foundation
4. special abilities
5. match loop
6. debugging and polish
7. multiplayer preparation

## Hard Rule
Never move to networking before the local combat loop is genuinely fun.

---

## Epics

Each epic maps to a roadmap phase and owns the feature set for that phase.

### Epic 1 — Project Bootstrap *(Phase 1)*
Create the technical base needed to support rapid game iteration.
- project initialization
- scene pipeline
- shared constants
- dev tooling
- placeholder asset pipeline

### Epic 2 — Player Controller *(Phase 2)*
Build a responsive and reusable player movement foundation.
- movement states
- local input mapping
- jump/dash behavior
- movement tuning hooks

### Epic 3 — Combat Framework *(Phase 3)*
Build the generic combat systems that all characters use.
- move definitions
- state machine
- attack timing
- hitboxes/hurtboxes
- hit resolution
- damage/knockback/block

### Epic 4 — Character A Implementation *(Phase 4)*
Implement Coinshot/Lurcher-inspired prototype fighter.
- normals
- specials
- projectile rules
- anchor interaction
- resource behavior

### Epic 5 — Character B Implementation *(Phase 4)*
Implement Windrunner-inspired prototype fighter.
- normals
- directional lashing
- aerial behavior
- slam / control moves
- resource behavior

### Epic 6 — Stage and Environment *(Phase 4)*
Create the first stage and its gameplay interactions.
- geometry
- anchor points
- spawn points
- boundaries

### Epic 7 — Match Flow and HUD *(Phase 5)*
Build the systems that make the prototype feel like a complete game.
- round states
- UI
- win conditions
- pause/rematch

### Epic 8 — Debugging and Tuning *(Phase 6)*
Add the tools required to make development sustainable.
- overlays
- logs
- tuning values
- debugging shortcuts

### Epic 9 — Multiplayer Readiness *(Phase 7)*
Prepare the codebase for later network experimentation.
- input recording
- serialization design
- deterministic review
- simulation isolation
