# Technical Roadmap

## Purpose
This document breaks technical implementation into concrete layers and dependency order. It should be used as the primary engineering roadmap.

## Guiding Principle
Every system should be implemented in the smallest useful version first, then expanded only when needed by gameplay.

---

## Layer 1 - Project Foundations

### Objective
Make the repository runnable, testable, and easy to extend.

### Work Items
1. create package scaffold
2. add TypeScript config
3. add Vite config
4. add Phaser dependency
5. add ESLint/Prettier or equivalent
6. define path aliases if useful
7. add environment/config files
8. create docs folder
9. define naming conventions
10. define shared constants

### Outputs
- clean project boot
- consistent dev workflow
- reduced setup ambiguity

### Dependencies
None

### Risks
- overconfiguring before gameplay exists

### Mitigation
- keep tooling minimal but stable

---

## Layer 2 - Scene and App Shell

### Objective
Create the Phaser app shell and scene routing.

### Work Items
1. create Phaser config module
2. create BootScene
3. create PreloadScene
4. create CombatScene
5. add scene switching helpers
6. add placeholder asset loading
7. add camera/bounds test

### Outputs
- app launches into playable scene
- assets load consistently

### Dependencies
Layer 1

### Risks
- too much scene logic early

### Mitigation
- keep gameplay in dedicated systems, not in scene class body

---

## Layer 3 - Core Domain Types

### Objective
Define the data types that the rest of the project depends on.

### Work Items
1. define player state enums
2. define move/input enums
3. define character definition interfaces
4. define move definition interfaces
5. define hitbox/hurtbox types
6. define match state enums
7. define debug flag types

### Outputs
- shared type contracts
- lower refactor cost later

### Dependencies
Layer 1

### Risks
- prematurely locking types too tightly

### Mitigation
- keep types extensible and pragmatic

---

## Layer 4 - Input System

### Objective
Normalize local keyboard/gamepad input into a consistent representation.

### Work Items
1. create input action enum
2. create player input mapping config
3. create keyboard input adapter
4. create optional gamepad adapter
5. create input frame object
6. create input buffer
7. expose current and previous input state

### Outputs
- gameplay systems consume clean input objects
- future recording/replay becomes feasible

### Dependencies
Layers 1-3

### Risks
- direct polling all over the codebase

### Mitigation
- require all gameplay input to flow through InputManager

---

## Layer 5 - Player Entity and Movement

### Objective
Build the player shell and movement controller.

### Work Items
1. create PlayerEntity model
2. create movement config object
3. implement ground movement
4. implement jump
5. implement gravity tuning
6. implement landing detection
7. implement dash
8. implement air control rules
9. implement facing direction
10. add movement state transitions

### Outputs
- 2 players can move cleanly
- movement values are tuneable

### Dependencies
Layers 2-4

### Risks
- movement rules hidden inside scene code
- hardcoded per-player logic

### Mitigation
- movement controller operates on PlayerEntity and config data

---

## Layer 6 - Generic State Machine

### Objective
Support clean character and combat transitions.

### Work Items
1. create state machine utility
2. support state enter/update/exit hooks
3. add timer tracking
4. implement movement/combat state enum mapping
5. validate transitions in debug mode

### Outputs
- stable state control
- easier combat extension

### Dependencies
Layers 3-5

### Risks
- overengineered state framework

### Mitigation
- build only states currently needed

---

## Layer 7 - Combat Definitions and Executor

### Objective
Create reusable move definitions and execution pipeline.

### Work Items
1. define move schema
2. define attack lifecycle model
3. create MoveExecutor
4. resolve startup/active/recovery windows
5. apply move-level movement impulses
6. enforce resource costs and availability
7. expose current move state for debug/UI

### Outputs
- generic move system for all characters

### Dependencies
Layers 3-6

### Risks
- character logic baked into executor

### Mitigation
- use data-driven move definitions and optional scripted hooks sparingly

---

## Layer 8 - Hit Detection Systems

### Objective
Implement attack collision and resolution.

### Work Items
1. create hitbox structure
2. create hurtbox structure
3. create hitbox manager
4. register active hurtboxes per player
5. detect overlaps
6. prevent repeated hit spam from same active box unless intended
7. add hit confirmation events
8. add debug drawing

### Outputs
- reliable hit detection pipeline

### Dependencies
Layers 5-7

### Risks
- relying on sprite bounds instead of explicit gameplay boxes

### Mitigation
- always define gameplay boxes explicitly

---

## Layer 9 - Damage, Knockback, and Guard

### Objective
Resolve the meaning of a successful hit.

### Work Items
1. implement damage application
2. implement knockback vectors
3. implement hitstun states
4. implement block direction checks
5. implement guard reduction rules
6. implement guard break or pressure logic
7. implement invulnerability windows where needed

### Outputs
- complete core combat interaction loop

### Dependencies
Layers 6-8

### Risks
- conflicting state authority between combat and movement

### Mitigation
- define precedence rules for stun, block, dash, airborne, etc.

---

## Layer 10 - Character Data and Specials

### Objective
Build the first two characters on top of the generic systems.

### Work Items
1. define character A data
2. define character B data
3. implement unique specials using generic systems first
4. add special-case hooks only when generic tools are insufficient
5. implement resource flavor labels and values
6. create placeholder animation/VFX identifiers

### Outputs
- distinct playable prototype roster

### Dependencies
Layers 5-9

### Risks
- introducing too many bespoke one-off systems too early

### Mitigation
- keep special-case code minimal and documented

---

## Layer 11 - Stage Systems

### Objective
Support the first level and themed interactions.

### Work Items
1. define stage config
2. place spawn points
3. place collision geometry
4. place anchor points
5. define out-of-bounds or clamp behavior
6. support stage reset hooks

### Outputs
- combat-ready stage with identity

### Dependencies
Layers 2-5

### Risks
- stage logic coupled to one specific character

### Mitigation
- anchor points and interactables exposed as stage entities/interfaces

---

## Layer 12 - Match State and Round Flow

### Objective
Turn the sandbox into a real match.

### Work Items
1. create match state enum
2. implement round start flow
3. implement countdown if desired
4. implement KO detection
5. implement round end flow
6. implement score tracking
7. implement rematch/reset flow

### Outputs
- complete playable match loop

### Dependencies
Layers 5-11

### Risks
- reset bugs leaving stale state behind

### Mitigation
- centralize reset pipeline and entity cleanup

---

## Layer 13 - HUD and Debug UI

### Objective
Expose important information to player and developer.

### Work Items
1. implement health bars
2. implement resource bars
3. implement round UI
4. implement win banner
5. implement debug overlay
6. implement hitbox toggle
7. implement state/frame display
8. implement quick restart/debug hotkeys

### Outputs
- readable game state
- faster debugging

### Dependencies
Layers 5-12

---

## Layer 14 - Instrumentation and Replay Prep

### Objective
Prepare for sustainable tuning and future networking.

### Work Items
1. log input frames
2. log major gameplay events
3. add simple replay serialization experiment
4. document serialization schema
5. isolate visual-only events from gameplay events

### Outputs
- better reproduction of bugs
- lower multiplayer expansion risk

### Dependencies
Layers 4-13

---

## Layer 15 - Stabilization and Refactor Pass

### Objective
Reduce technical debt before expansion.

### Work Items
1. remove dead code
2. consolidate duplicate combat logic
3. normalize config/data locations
4. improve docs
5. review naming consistency
6. fix top-priority bugs from playtesting

### Outputs
- stable MVP codebase
- better foundation for post-MVP work
