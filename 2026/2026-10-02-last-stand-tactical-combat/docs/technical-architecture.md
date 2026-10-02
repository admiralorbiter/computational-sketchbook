# Technical Architecture

---

## Engine Choice: Godot 4.x

**Rationale:**
- Dedicated 2D tooling and navigation
- GDScript for rapid iteration (performance optimization later if needed)
- Free and open source
- Built-in pathfinding (NavigationServer2D)
- Built-in physics for raycasting
- Strong debug drawing capabilities
- Active community and documentation

**Why not Unity?** Could work, but Godot's 2D-first design is better suited for the prototype. Unity becomes attractive if we need hundreds/thousands of agents with ECS optimization.

**Why not Bevy/Rust?** Architecture is beautiful for this (ECS-first), but Rust + code-centric engine adds friction at the moment when game design iteration matters most.

**Why not custom engine?** Write a custom combat simulation framework *inside* Godot, not a custom engine. Important distinction.

---

## Project Structure

```
prototype/
├── project.godot
├── src/
│   ├── simulation/          # Core combat simulation
│   │   ├── unit.gd           # Unit entity: HP, position, team, weapon
│   │   ├── weapon.gd         # Weapon stats and firing logic
│   │   ├── projectile.gd     # Projectile travel and hit detection
│   │   ├── combat.gd         # Damage calculation, hit resolution
│   │   ├── suppression.gd    # Suppression accumulation and effects
│   │   ├── perception.gd     # LOS, cover detection, target acquisition
│   │   └── cover.gd          # Cover system, cover values
│   │
│   ├── ai/                   # AI systems
│   │   ├── defender_ai.gd    # Autonomous defender behavior
│   │   ├── attacker_ai.gd    # Enemy individual AI
│   │   ├── squad_ai.gd       # Squad-level coordination
│   │   ├── commander_ai.gd   # Enemy commander decisions
│   │   └── utility.gd        # Utility scoring functions
│   │
│   ├── orders/               # Order system
│   │   ├── order.gd           # Base order class
│   │   ├── move_order.gd      # Move to position
│   │   ├── sector_order.gd    # Watch sector (firing arc)
│   │   ├── suppress_order.gd  # Suppress area
│   │   ├── fallback_order.gd  # Fallback to position
│   │   └── order_manager.gd   # Order queue and execution
│   │
│   ├── scenario/             # Scenario management
│   │   ├── scenario.gd        # Scenario loader and rules
│   │   ├── spawn_rules.gd     # Enemy wave/spawn logic
│   │   └── objectives.gd      # Victory/defeat conditions
│   │
│   ├── building/             # Preparation phase
│   │   ├── deployable.gd      # Base deployable class
│   │   ├── build_manager.gd   # Placement logic, budget, constraints
│   │   └── build_ghost.gd     # Placement preview
│   │
│   ├── ui/                   # User interface
│   │   ├── selection.gd       # Unit selection (click, box, groups)
│   │   ├── command_ui.gd      # Order input handling
│   │   ├── build_ui.gd        # Build mode UI
│   │   ├── hud.gd             # In-game HUD
│   │   ├── briefing_ui.gd     # Pre-battle briefing screen
│   │   └── aar_ui.gd          # After-action report
│   │
│   └── debug/                # Debug tools
│       ├── debug_overlay.gd   # Toggle-able debug visualization
│       ├── unit_inspector.gd  # Click unit → see AI state
│       └── sim_controls.gd    # Speed control, pause, step
│
├── data/                     # Data-driven definitions
│   ├── weapons/
│   │   ├── assault_rifle.tres
│   │   ├── lmg.tres
│   │   ├── shotgun.tres
│   │   └── pistol.tres
│   ├── units/
│   │   ├── rifleman.tres
│   │   ├── mg_gunner.tres
│   │   ├── shotgunner.tres
│   │   ├── medic.tres
│   │   ├── enemy_rusher.tres
│   │   ├── enemy_rifleman.tres
│   │   └── enemy_breacher.tres
│   ├── deployables/
│   │   ├── wall.tres
│   │   ├── sandbag.tres
│   │   ├── wire.tres
│   │   ├── mine.tres
│   │   └── ammo_box.tres
│   └── scenarios/
│       └── battle_001.tres
│
├── scenes/                   # Godot scenes
│   ├── main.tscn
│   ├── battle.tscn
│   ├── units/
│   ├── deployables/
│   └── ui/
│
└── assets/                   # Art, sound, etc.
    ├── sprites/
    ├── sounds/
    └── fonts/
```

---

## Core Architecture Principles

### Simulation ≠ Presentation

```
┌─────────────────────────────────────┐
│          SIMULATION LAYER           │
│                                     │
│  Units, Weapons, Projectiles,       │
│  Orders, Perception, Cover,         │
│  Suppression, Damage, AI            │
│                                     │
│  Authoritative. Runs on fixed tick. │
│  No rendering code here.            │
└──────────────┬──────────────────────┘
               │ state queries
               ▼
┌─────────────────────────────────────┐
│         PRESENTATION LAYER          │
│                                     │
│  Sprites, Animation, Effects,       │
│  Sound, Particles                   │
│                                     │
│  Reads sim state. Draws it.         │
│  Never modifies sim state.          │
└─────────────────────────────────────┘
               ▲
               │ player input
┌─────────────────────────────────────┐
│          INTERFACE LAYER            │
│                                     │
│  Selection, Orders, Build UI,       │
│  Debug Overlay                      │
│                                     │
│  Translates input into sim commands │
└─────────────────────────────────────┘
```

### Fixed-Tick Simulation

- Target: 20 ticks per second (50ms per tick)
- Independent from rendering framerate
- Enables: pause, slow-mo, fast-forward, replays, deterministic testing
- Seeded RNG per scenario for reproducibility

### Data-Driven Design

Inspired by RimWorld's Def system. Content is data, not code.

Example weapon definition:
```
# data/weapons/lmg.tres or .json
name: "M249 LMG"
category: machine_gun
damage: 12
rpm: 750
accuracy_base: 0.65
accuracy_moving: 0.25
dispersion: 0.08
suppression_per_round: 4.2
magazine_size: 100
reload_time: 5.1
range_effective: 40
range_max: 60
setup_time: 1.5
```

### Orders as Data

```
Order {
    type: OrderType
    issuer: Entity (player or AI)
    subjects: [Entity]
    target: Vector2 | Entity | Sector
    priority: Priority
    completion_condition: Condition
    cancellation_condition: Condition
}
```

This naturally evolves into:
```
ConditionalOrder {
    condition: enemies_in_sector >= 8
    action: fallback(position_charlie)
}
```

The architecture supports the eventual doctrine editor without rewriting AI.

---

## AI Architecture

### Individual AI: Utility Scoring

For each possible action, compute a utility score:

```
shoot target A       0.82
shoot target B       0.44
take nearby cover    0.67
reload               0.21
retreat              0.03
```

Pick the highest reasonable action.

**Expose these numbers in debug mode.**

### Debug Visualization (Non-Optional)

A hotkey toggles:
- LOS rays from each unit
- Cover values on terrain
- Pathfinding overlays
- Target selection lines
- Suppression levels (color-coded)
- AI state labels
- Engagement sector arcs
- Order visualization
- Threat heatmaps

Click any unit to see:
```
CURRENT ACTION: Fire M249
TARGET: Raider 18
REASON: 0.84 utility (threat × proximity × LOS_quality)
ORDER: Hold East Sector
SUPPRESSION: 22%
COVER: 68%
AMMO: 72/100
HP: 85/100
```

This is development infrastructure, not a nice-to-have.
