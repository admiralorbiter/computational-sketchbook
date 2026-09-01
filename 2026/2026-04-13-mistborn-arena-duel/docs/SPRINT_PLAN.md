# Sprint Plan

> **How to use this file:** Sprint definitions are at the top for planning. The full ticket list and weekly build order are below for day-to-day implementation reference.

---

## Sprints

### Sprint 1 — Bootstrap + Movement
**Goals:** working Phaser project, playable movement

- [x] setup project tooling
- [x] create core scenes
- [x] implement input abstraction
- [x] implement player movement controller
- [x] add debug movement overlay

### Sprint 2 — Combat Core
**Goals:** attacks can be executed and resolved

- [x] create state machine
- [x] define move schema
- [x] implement hitbox/hurtbox systems
- [x] implement damage and knockback
- [x] implement block state

### Sprint 3 — Character Identity
**Goals:** both characters become distinct

- implement character A specials
- implement character B specials
- implement resource meters
- implement stage anchor interactions

### Sprint 4 — Match Loop + HUD
**Goals:** full local match start-to-finish

- create match state machine
- implement UI/HUD
- implement result screens
- implement reset/rematch flow

### Sprint 5 — Debug + Tune
**Goals:** playtest-ready build

- add hitbox visualization
- add input/frame logs
- tune values
- fix major combat bugs

---

## Recommended Build Order

1. project bootstrap
2. movement controller
3. state machine
4. light/heavy attack pipeline
5. hitbox/hurtbox systems
6. damage/knockback/block
7. character-specific specials
8. stage anchor system
9. round flow and HUD
10. debug tooling and playtesting
11. multiplayer preparation work

---

## Weekly Build Schedule

### Week 1
- create repo
- install Phaser / Vite / TypeScript
- create BootScene, PreloadScene, CombatScene
- display placeholder stage and player rectangles
- wire input for two local players

### Week 2
- implement movement controller
- implement jump/fall/landing states
- implement dash
- add debug text for movement state and velocity

### Week 3
- implement attack state machine
- implement light/heavy attacks
- implement hitboxes and hurtboxes
- implement damage and knockback

### Week 4
- implement block
- implement hitstun/recovery
- add hitstop and minimal feedback
- begin character-specific move data

### Week 5
- implement coin shot
- implement push/pull mobility
- implement lashing burst
- implement slam/knock-up
- add resource meter logic

### Week 6
- implement HUD
- implement round flow
- implement reset/rematch
- add debug toggles and quick restart

### Week 7
- stabilize bugs
- tune values
- run playtests
- update docs and backlog

---

## Full Ticket List

### Ticket 001 — Create Project Shell
- [x] setup Vite
- [x] setup TypeScript
- [x] install Phaser
- [x] create app entry
- [x] verify browser boot

### Ticket 002 — Add Scene Pipeline
- [x] BootScene
- [x] PreloadScene
- [x] CombatScene
- [x] scene transition wiring

### Ticket 003 — Add Local Input Manager
- [x] player 1 keyboard map
- [x] player 2 keyboard map
- [x] action enum
- [x] input state polling

### Ticket 004 — Create Player Entity
- [x] basic player model
- [x] placeholder sprite/body
- [x] health/resource fields
- [x] state field

### Ticket 005 — Implement Horizontal Movement
- [x] run speed
- [x] acceleration/deceleration
- [x] facing
- [x] bounds checks

### Ticket 006 — Implement Jump/Fall
- [x] jump logic
- [x] gravity tuning
- [x] land detection
- [x] air control

### Ticket 007 — Implement Dash
- [x] dash state
- [x] timer/cooldown
- [x] movement impulse
- [x] debug display

### Ticket 008 — Add State Machine
- [x] base state framework
- [x] movement states
- [x] attack state placeholders
- [x] transition validation

### Ticket 009 — Define Move Schema
- [x] move interface
- [x] startup/active/recovery fields
- [x] hitbox definitions
- [x] resource cost field

### Ticket 010 — Add Hitbox/Hurtbox System
- [x] spawn hitbox
- [x] register hurtboxes
- [x] resolve overlaps
- [x] add debug drawing

### Ticket 011 — Add Damage/Knockback
- [x] damage application
- [x] knockback vectors
- [x] hitstun
- [x] KO detection hook

### Ticket 012 — Add Block System
- [x] block state
- [x] frontal validation
- [x] block reaction
- [x] heavy pressure rule

### Ticket 013 — Implement Character A Specials
- coin shot
- push/pull mobility
- resource cost rules

### Ticket 014 — Implement Character B Specials
- lashing burst
- slam/knock-up
- aerial behavior rules

### Ticket 015 — Implement Stage 01
- layout collision
- spawn points
- anchor points
- bounds

### Ticket 016 — Implement Match Loop
- round start
- round end
- score tracking
- reset pipeline

### Ticket 017 — Implement HUD
- health bars
- resource bars
- round indicators
- result text

### Ticket 018 — Add Debug Overlay
- [x] state display
- [x] velocity display
- [x] hitboxes
- [x] frame/input info

### Ticket 019 — Add Playtest Tools
- quick restart
- debug toggles
- match stats logging

### Ticket 020 — Add Input Recording Prototype
- record frame inputs
- export basic log
- document format
