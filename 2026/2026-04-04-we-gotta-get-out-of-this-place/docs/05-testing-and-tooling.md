# Testing and Tooling

## 1. Philosophy

Tooling is not a bonus feature. It is a multiplier for every future feature. The goal is to make problems visible early and make regressions cheap to catch.

## 2. Front-Loaded Tooling

These should come unusually early:

- fixed-step timing visibility
- debug overlay
- event log
- preset rocket loader
- basic smoke checklist

These systems will save time on every later epic.

## 3. Debug Overlay

Decision: debug tools are controlled by a **runtime toggle**, not a compile flag.

Rationale: compile flags prevent sharing a build and asking someone to reproduce an issue. A runtime toggle (e.g., `F3` or `--debug` CLI flag) keeps debug capability always compiled in but invisible by default. This is the right tradeoff for a solo project where fast iteration and occasional external feedback both matter.

The overlay should always be cheap to enable and disable.

Recommended fields:
- current app state
- FPS
- sim time scale
- rocket position
- velocity
- altitude
- angle
- mass
- drag force
- thrust force
- current stage
- fuel remaining
- mission flags

## 4. Event Log

Record notable events as structured entries.

Examples:
- launch started
- stage activated
- decoupler fired
- fuel tank emptied
- apoapsis passed
- stable orbit achieved
- crash detected
- parachute deployed
- mission completed / failed

Uses:
- debrief reconstruction
- debugging stage errors
- regression comparisons

## 5. Scenario Loader

A scenario loader or test harness should support:

- loading known rocket blueprints
- starting in specific app states
- setting altitude, velocity, and heading
- switching mission context quickly
- bypassing menus for test flows

## 6. Time Controls

Useful time modes:
- pause
- normal speed
- 2x / 4x / 8x for testing

These are valuable for orbit and descent testing even before full player-facing time warp exists.

## 7. Tunables Panel

A developer-only panel should allow live edits to a subset of tuning values.

Good candidates:
- gravity multiplier
- drag multiplier
- atmosphere height
- engine thrust multiplier
- fuel density or burn rate multiplier
- mission thresholds

Benefits:
- faster balancing
- easier bug isolation
- less compile-run-edit friction

## 8. Visual Debug Modes

Helpful overlays:
- center of mass marker
- thrust vector
- velocity vector
- drag vector
- predicted path line
- stage highlighting
- atmosphere boundary

## 9. Regression Assets

Keep a small pack of known rockets and expected outcomes.

Suggested presets:
- single-stage hopper
- two-stage basic orbiter
- low-TWR failure case
- bad staging case
- over-drag unstable case
- safe descent parachute case

Use these after major changes.

## 10. Test Types

## 10.1 Unit Tests
Best targets:
- mass aggregation
- fuel depletion math
- stage sequencing
- orbit parameter calculations
- mission evaluation
- schema validation helpers

## 10.2 Integration Tests
Best targets:
- blueprint to flight handoff
- mission start and mission completion flow
- save/load compatibility for blueprints

## 10.3 Manual Smoke Tests
Use at every meaningful milestone:
- app launches
- rocket launches
- restart works
- stage works
- builder stats update
- map opens and closes
- mission state updates
- debrief appears

## 11. Acceptance Smoke Checklist Template

Use this checklist after any major merge or refactor:

- [ ] App starts without asset or data errors
- [ ] Main menu opens
- [ ] Builder opens
- [ ] A valid rocket can be built or loaded
- [ ] Launch succeeds from builder
- [ ] Stage activation works
- [ ] Fuel drains correctly
- [ ] Mission checks update
- [ ] Debrief appears after mission end
- [ ] Save / load still works for implemented save categories

## 12. Bug Triage Guidance

When a bug appears, ask first:

1. Is this a simulation bug, a UI bug, or a data bug?
2. Can it be reproduced with a preset rocket?
3. Is the failure visible in the event log?
4. Do we need a new regression scenario after fixing it?

## 13. Tooling Delivery Order

1. Debug text overlay
2. Event log shell (implemented early in Phase 1)
3. Rocket preset loader
4. Visual debug vectors
5. Tunables panel
6. Scenario editor / richer harness

## 14. Definition of “Safe to Expand”

The project is safe to add post-MVP complexity when:

- the smoke checklist is fast to run
- at least a few core systems have automated tests
- major flight bugs can be reproduced quickly
- tuning key physics constants is no longer painful
