class_name WeaponData extends Resource
## Weapon Data Resource
## Defines combat properties for a weapon type.

enum WeaponCategory {
	RIFLE,
	MACHINE_GUN,
	SHOTGUN,
	PISTOL,
	MELEE
}

@export var category: WeaponCategory = WeaponCategory.RIFLE
@export var damage: float = 35.0
@export var rpm: int = 600
@export var base_accuracy: float = 0.85
@export var moving_accuracy: float = 0.40
@export var effective_range: float = 400.0 # Pixels or units
@export var max_range: float = 800.0 # Pixels or units
@export var suppression_per_round: float = 5.0
@export var magazine_size: int = 30
@export var reload_time: float = 2.5
@export var setup_time: float = 0.0

## Returns range modifier based on falloff curve.
func get_range_modifier(distance: float) -> float:
	if distance <= effective_range:
		return 1.0
	elif distance >= max_range:
		return 0.0
	else:
		# Linear falloff between effective and max range
		var range_diff = max_range - effective_range
		var current_diff = distance - effective_range
		return 1.0 - (current_diff / range_diff)

## Converts RPM to shots per fixed simulation tick.
func get_shots_per_tick() -> float:
	var rps: float = float(rpm) / 60.0
	return rps * GameConstants.TICK_DELTA
