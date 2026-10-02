class_name Deployable
extends Resource
## Base class for deployable defensive structures or items.

@export var deployable_name: String = "Deployable"
@export var cost: int = 100
@export var hp: float = 100.0
@export var cover_value: float = 0.5 ## 0.0 to 1.0 (percentage of incoming fire blocked)
@export var blocks_los: bool = false
@export var blocks_movement: bool = true

## Special effects or properties.
## e.g., {"slow_factor": 0.3} for wire, {"damage": 80, "radius": 2} for mine
@export var special: Dictionary = {}

## Color used when previewing placement.
@export var ghost_color: Color = Color(0.2, 0.8, 0.2, 0.5)
