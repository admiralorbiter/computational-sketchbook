class_name SpawnRules
extends RefCounted
## Handles rules and logic for spawning enemy units around the map edges.

## Returns an array of dictionaries representing units to spawn for a given wave.
func spawn_wave(wave_data: Dictionary, map_bounds: Rect2) -> Array[Dictionary]:
	var units_to_spawn: Array[Dictionary] = []
	
	if not wave_data.has("units"):
		return units_to_spawn
		
	for unit_group in wave_data["units"]:
		var type: String = unit_group.get("type", "rifleman")
		var count: int = unit_group.get("count", 1)
		var edge: String = unit_group.get("spawn_edge", "top")
		var squad_id: int = unit_group.get("squad_id", -1)
		
		for i in range(count):
			var spawn_pos: Vector2 = get_spawn_position(edge, map_bounds)
			units_to_spawn.append({
				"type": type,
				"position": spawn_pos,
				"squad_id": squad_id
			})
			
	return units_to_spawn

## Calculates a random spawn position along the specified map edge.
func get_spawn_position(edge: String, map_bounds: Rect2) -> Vector2:
	var pos := Vector2.ZERO
	match edge.to_lower():
		"top":
			pos.x = randf_range(map_bounds.position.x, map_bounds.end.x)
			pos.y = map_bounds.position.y
		"bottom":
			pos.x = randf_range(map_bounds.position.x, map_bounds.end.x)
			pos.y = map_bounds.end.y
		"left":
			pos.x = map_bounds.position.x
			pos.y = randf_range(map_bounds.position.y, map_bounds.end.y)
		"right":
			pos.x = map_bounds.end.x
			pos.y = randf_range(map_bounds.position.y, map_bounds.end.y)
		_:
			# Default to random point on any edge if unspecified or invalid
			var random_edge: int = randi() % 4
			match random_edge:
				0: return get_spawn_position("top", map_bounds)
				1: return get_spawn_position("bottom", map_bounds)
				2: return get_spawn_position("left", map_bounds)
				3: return get_spawn_position("right", map_bounds)
				
	return pos
