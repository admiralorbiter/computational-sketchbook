class_name Perception extends RefCounted
## Perception and Line of Sight Utility
## Simulates vision and cover evaluation using raycasting logic over tile maps.

## Checks if there is an unobstructed line of sight between two points.
static func has_line_of_sight(from: Vector2, to: Vector2, tilemap: TileMapLayer) -> bool:
	if not tilemap:
		return true
		
	# Placeholder for true raycasting implementation.
	# Usually involves stepping along the line and checking tile properties.
	return true

## Calculates the cover value provided to target_pos against shooter_pos.
static func get_cover_value(target_pos: Vector2, shooter_pos: Vector2, tilemap: TileMapLayer) -> Cover.CoverType:
	if not tilemap:
		return Cover.CoverType.NONE
		
	# Placeholder logic. Will check tiles adjacent to target_pos in the direction of shooter_pos.
	return Cover.CoverType.NONE

## Returns an array of enemy Units currently visible to the given unit.
static func get_visible_enemies(unit: Unit, all_units: Array, tilemap: TileMapLayer) -> Array[Unit]:
	var visible_enemies: Array[Unit] = []
	for other in all_units:
		if other is Unit and other.team != unit.team:
			if has_line_of_sight(unit.global_position, other.global_position, tilemap):
				visible_enemies.append(other)
	return visible_enemies

## Determines if the shooter is flanking the target's cover.
static func is_flanking(shooter_pos: Vector2, target_pos: Vector2, cover_facing: Vector2) -> bool:
	var attack_dir = (target_pos - shooter_pos).normalized()
	# If attack angle is beyond a threshold relative to cover facing, it's a flank.
	var dot = attack_dir.dot(cover_facing)
	# Assuming dot > 0.5 means firing roughly from the protected side.
	# So dot < 0 or something indicates flanking.
	return dot < 0.0
