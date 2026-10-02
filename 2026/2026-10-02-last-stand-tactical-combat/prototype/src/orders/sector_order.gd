class_name SectorOrder extends BaseOrder

enum FireDiscipline { FREE_FIRE, CONSERVE_AMMO, HOLD_FIRE }

@export var sector_origin: Vector2
@export var sector_direction: Vector2 # Direction vector (normalized)
@export var sector_angle: float # Half-angle of the arc in radians
@export var engagement_range: float
@export var fire_discipline: FireDiscipline = FireDiscipline.FREE_FIRE

func _init() -> void:
	type = OrderType.WATCH_SECTOR

## Checks if a position falls within the firing arc
func is_target_in_sector(target_pos: Vector2) -> bool:
	var dist: float = sector_origin.distance_to(target_pos)
	if dist > engagement_range:
		return false
	
	var dir_to_target: Vector2 = (target_pos - sector_origin).normalized()
	var angle_to_target: float = sector_direction.angle_to(dir_to_target)
	
	return abs(angle_to_target) <= sector_angle
