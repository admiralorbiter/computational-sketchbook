extends Node
## Game Constants Autoload
## Stores all constant values from the combat math spec.

# General
const TICK_RATE: int = 20
const TICK_DELTA: float = 1.0 / TICK_RATE
const TILE_SIZE: int = 32
const BUILD_BUDGET: int = 200

# Health & Recovery
const BASE_HP: float = 100.0
const BLEEDOUT_TIME: float = 30.0
const HEAL_RATE: float = 5.0
const STABILIZE_TIME: float = 3.0

# Suppression
const SUPPRESSION_MAX: float = 100.0
const SUPPRESSION_DECAY: float = 12.0 # Per second (tuning: was 8.0, increased per CE/JA2 research)
const NEAR_MISS_SUPPRESSION: float = 0.70 # Suppression multiplier applied for near misses
const EXPLOSION_SUPPRESSION: float = 30.0
const ALLY_KILLED_SUPPRESSION: float = 15.0

# Cover Modifiers (Damage Reduction or Accuracy Modifiers depending on formula context)
const COVER_NONE: float = 0.0
const COVER_SOFT: float = 0.20
const COVER_SANDBAG: float = 0.40
const COVER_HARD: float = 0.60
const COVER_FULL: float = 1.00

# Movement Speeds (tiles per second, likely need scaling by TILE_SIZE)
const SPEED_SPRINT: float = 6.0
const SPEED_NORMAL: float = 4.0
const SPEED_CROUCH: float = 2.0
const SPEED_CRAWL: float = 0.5

# Morale System
const MORALE_CONFIDENT: float = 60.0
const MORALE_SHAKEN: float = 40.0
const MORALE_WAVERING: float = 20.0
const MORALE_BREAKING: float = 1.0
const MORALE_RECOVERY_SAFE: float = 2.0 # Per second
const MORALE_RECOVERY_COVER: float = 0.5 # Per second
