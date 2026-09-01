# Game Design Document

## 1. High Concept

**We Gotta Get Out of This Place** is a 2D rocket engineering game where the player designs modular launch vehicles, flies them through atmosphere and into orbit, and completes increasingly demanding missions.

The game aims to be easier to enter than a full 3D sandbox space program sim while preserving the deep satisfaction of staging, ascent planning, fuel tradeoffs, and orbital success.

## 2. Vision Statement

Build a small, readable, emotionally distinct rocket game where the player feels clever, underfunded, and a little desperate, but capable of brute-forcing brilliance out of physics.

## 3. Player Fantasy

The player should feel like:

- an inventive rocket engineer
- a problem solver, not just a pilot
- someone making ugly but functional machines
- someone learning from every failure

## 4. Product Identity

This game is:

- deliberately 2D
- mission-first rather than purely sandbox-first
- low graphics but high systems clarity
- built around retries and iteration
- interested in engineering tradeoffs more than spectacle

This game is not:

- a massive universe simulator
- a content-heavy sci-fi RPG
- a colony builder
- a realism-maximalist aerospace simulator

## 5. Design Pillars

### 5.1 Readable Depth
The player should be able to understand what the rocket is doing and why. Depth should come from decisions and interactions, not from obscurity.

### 5.2 Systems over Spectacle
The core fun is thrust, mass, drag, staging, and orbit. Presentation supports those systems rather than dominating the experience.

### 5.3 Fast Iteration
The game should encourage short test loops. Build, launch, fail, learn, adjust, retry.

### 5.4 Failure with Feedback
Failures are expected and valuable. The UI and debrief systems should explain whether the rocket failed because it was too heavy, underpowered, unstable, mis-staged, or flown poorly.

### 5.5 Tight Scope
Version 1 should stay narrow enough to ship: one planet, a manageable parts list, a handful of meaningful missions, and no giant progression web.

## 6. Core Loop

1. Choose or continue a mission
2. Assemble or revise a rocket
3. Review predicted stats and staging
4. Launch and control ascent
5. Switch to map view as needed to understand trajectory
6. Succeed or fail
7. Review debrief data and make changes
8. Retry or unlock the next mission

## 7. Session Shape

A strong short session should look like this:

- load a mission
- tweak a design
- launch
- discover a specific weakness
- make one or two changes
- attempt again
- either solve the mission or learn something precise

## 8. MVP Scope

### 8.1 Included

- modular rocket builder
- core part categories
- stage management
- thrust, fuel, gravity, and drag simulation
- launch and flight controls
- basic map/orbit view
- mission goals and debrief screen
- quick retry loop

### 8.2 Excluded

- multiple planets
- docking and rendezvous as MVP requirements
- EVA and crews beyond a simple command pod abstraction
- science tree and career economy
- power systems and communications
- realistic part bending and advanced aero modeling
- multiplayer

## 9. Core Features

### 9.1 Rocket Builder
The player assembles a rocket from a limited but meaningful set of parts.

Initial part list:

- command pod
- fuel tank
- liquid engine
- decoupler
- fin
- parachute
- payload mass block

Builder capabilities:

- add and remove parts
- snap to valid locations
- assign stage membership
- inspect part stats
- see aggregate rocket stats
- receive warnings for invalid or risky designs

### 9.2 Flight
The player launches and controls the rocket in real time.

Controls:

- throttle up / down
- rotate left / right
- activate stage
- pause
- toggle map view
- restart

Flight concerns:

- thrust-to-weight ratio
- fuel burn and dry mass changes
- gravity turn timing
- drag losses
- maintaining control long enough to reach the mission goal

### 9.3 Map / Orbit View
The player needs a strategic view that explains trajectory.

Map responsibilities:

- show planet and atmosphere boundary
- show current path
- show apoapsis and periapsis markers
- show whether orbit is stable
- show mission target orbit or milestone context

### 9.4 Mission System
The mission layer gives the game shape.

Starting mission types:

- reach altitude threshold
- cross the edge of space
- survive descent and land safely
- achieve stable orbit
- place payload in orbit

### 9.5 Debrief
Every run ends with clear feedback.

Debrief outputs:

- success or failure
- mission progress summary
- max altitude
- peak speed
- stage usage summary
- probable failure reason
- retry or return actions

## 10. Progression Philosophy

The progression should feel purposeful but not bloated.

Recommended early approach:

- a mission list with escalating complexity
- gentle unlocks of new part variants
- no heavy economy layer in MVP

Post-MVP options:

- budget constraints
- part research
- contracts
- reputation

## 11. Tone and Presentation

The title gives the game a slightly plaintive, determined feeling. The writing and presentation should reflect that without becoming melodramatic.

Tone targets:

- dry and a little wry
- grounded rather than goofy
- human and stubborn
- low-fi but evocative

## 12. Success Metrics for the Prototype

The prototype is successful if:

- building and launching is immediately understandable
- players can tell why a design might fail before launch
- a successful orbit feels earned
- failed attempts teach something specific
- the game loop is compelling even with placeholder art

## 13. Non-Goals

Do not chase these before the core loop is proven:

- giant part catalogs
- realistic n-body simulation
- cinematic presentation layers that hide important data
- complex campaign economy
- wide feature breadth before the rocket loop feels good
