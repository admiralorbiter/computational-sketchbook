# Technical Architecture

## Architecture Goals
- keep gameplay systems modular
- separate data from behavior where practical
- isolate rendering/audio from game rules
- make local simulation easier to reason about
- avoid architecture that blocks future multiplayer

## Core Runtime Model
The game runs as a Phaser application, but gameplay systems should be treated as layered modules:

1. input layer
2. simulation/gameplay layer
3. presentation layer
4. UI/debug layer

## High-Level System Boundaries

### Input Layer
Responsible for collecting player intent and normalizing it into game-friendly commands.

### Simulation Layer
Responsible for authoritative local gameplay rules:
- movement resolution
- attack timing
- hit detection
- damage
- knockback
- resource usage
- match state transitions

### Presentation Layer
Responsible for:
- sprites/animation
- VFX
- camera
- screen shake
- audio hooks

### UI/Debug Layer
Responsible for:
- HUD
- overlays
- logs
- debug toggles

## Scene Structure

### BootScene
- minimal bootstrapping
- load config required for preload
- initialize global services if needed

### PreloadScene
- load assets
- build asset registry if needed
- transition to gameplay scene

### CombatScene
- main gameplay scene
- owns stage, fighters, HUD, and match loop orchestration

### Optional Future Scenes
- menu scene
- character select scene
- training scene

## Core Gameplay Objects

### PlayerEntity
Represents a fighter instance in the match.

#### Responsibilities
- position/velocity carrier
- current gameplay state
- current health/resource
- character definition reference
- move execution tracking
- hurtbox ownership

### CharacterDefinition
Pure data describing a character.

#### Contains
- movement stats
- health/resource defaults
- move list
- animation keys
- UI labels
- tuning parameters

### MoveDefinition
Pure data describing a move.

#### Contains
- input trigger
- startup frames/time
- active frames/time
- recovery frames/time
- hitbox definitions
- damage/knockback/block values
- cancel rules
- resource cost
- movement impulses

### MatchController
Controls overall match state.

#### Responsibilities
- round state
- win condition
- timer
- reset flow
- score tracking

### StageController
Manages stage geometry metadata and interactables.

#### Responsibilities
- spawn points
- bounds
- anchor points
- hazard definitions if any

## Recommended Module Breakdown

### `/game/input`
- `InputManager`
- `LocalInputSource`
- `InputBuffer`
- `InputFrame`
- input mapping utilities

### `/game/state`
- `StateMachine`
- state enums
- state transition rules
- timers

### `/game/combat`
- `MoveExecutor`
- `HitboxSystem`
- `HurtboxSystem`
- `DamageSystem`
- `KnockbackSystem`
- `BlockSystem`
- `ProjectileSystem`

### `/game/controllers`
- `PlayerController`
- `MovementController`
- `CharacterController`

### `/game/match`
- `MatchController`
- `RoundController`
- `SpawnManager`

### `/game/ui`
- `HudView`
- `HealthBarView`
- `ResourceBarView`
- `DebugOverlay`

### `/game/entities`
- `PlayerEntity`
- `ProjectileEntity`
- `AnchorPointEntity`

## Update Order Recommendation
For each frame/update tick, apply game logic in a consistent order.

1. poll inputs
2. buffer/store inputs
3. resolve movement intentions
4. update state timers
5. execute move transitions
6. spawn/update hitboxes/projectiles
7. resolve hit detection
8. apply damage/knockback/state changes
9. update match conditions
10. update presentation hooks
11. render debug/UI updates

## Why Update Order Matters
A fixed and documented update order reduces weird bugs where visuals, hit detection, and movement disagree.

## Data-Driven Design
Gameplay data should live in structured files where possible.

### Examples
- character stats in `/data/characters`
- move definitions in `/data/moves`
- stage definitions in `/data/stages`

### Benefits
- easier tuning
- easier balancing
- better reuse
- less hardcoded branching

## Physics Strategy
Use Arcade Physics for:
- stage collision
- gravity
- movement body support
- simple overlap support

Do not rely on Arcade Physics as the source of truth for combat semantics.

### Combat Rules Should Be Custom
- attack windows
- hit confirmation
- hurtbox validation
- guard direction checks
- cancel rules
- resource spending

## Deterministic-ish Design Recommendations
Full determinism in browser/Phaser may be difficult, but the design should move in that direction.

### Recommendations
- avoid random combat outcomes
- use explicit timers and state fields
- use compact input representation
- keep move resolution data-driven
- isolate floating-point-sensitive features where possible

## Event Flow Recommendation
Use internal gameplay events for decoupling.

### Example Events
- `move_started`
- `move_hit`
- `block_success`
- `round_started`
- `round_ended`
- `player_ko`

Visual/audio systems can subscribe to these without owning gameplay rules.

## Error-Reduction Practices
- prefer enums/constants over magic strings
- centralize timing values
- centralize collision layer definitions
- log invalid state transitions in debug mode
- avoid animation state becoming the source of truth for gameplay state

## Future Multiplayer Preparation

### Preserve the following boundaries now:
- inputs are explicit
- gameplay state is serializable
- move definitions are data-based
- simulation updates are ordered consistently
- visual effects are non-authoritative

### Avoid now:
- gameplay driven directly by animation callbacks alone
- hidden random behavior
- uncontrolled physics interactions deciding outcomes
- hardcoded character-specific logic scattered across scene files
