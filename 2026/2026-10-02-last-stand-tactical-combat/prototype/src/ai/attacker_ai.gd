class_name AttackerAI extends Node

enum ActionType { FIRE, MOVE, SPRINT, HOLD, RETREAT, BREACH }

var unit: Node

func _ready() -> void:
	unit = get_parent()

func evaluate(visible_enemies: Array, delta: float) -> Dictionary:
	var morale: String = unit.morale_state if "morale_state" in unit else "NORMAL"
	if morale == "BREAKING" or morale == "ROUTED":
		return {"action": ActionType.RETREAT, "target": null, "utility_score": 100.0, "reason": "Morale broken"}
		
	var unit_type: String = unit.unit_type if "unit_type" in unit else "rifleman"
	
	var suppression: float = unit.suppression_level if "suppression_level" in unit else 0.0
	if suppression > 0.5:
		return {"action": ActionType.HOLD, "target": null, "utility_score": 80.0, "reason": "Suppressed, seeking cover"}
	
	if unit_type == "rusher":
		var nearest: Node = get_nearest(visible_enemies)
		if nearest:
			return {"action": ActionType.SPRINT, "target": nearest.global_position, "utility_score": 75.0, "reason": "Rushing target"}
	elif unit_type == "breacher":
		# identify nearest wall/door (stubbed)
		return {"action": ActionType.BREACH, "target": null, "utility_score": 80.0, "reason": "Moving to breach"}
	else:
		# Rifleman
		if not visible_enemies.is_empty():
			return {"action": ActionType.FIRE, "target": visible_enemies[0], "utility_score": 60.0, "reason": "Engaging target"}
		else:
			return {"action": ActionType.MOVE, "target": null, "utility_score": 40.0, "reason": "Advancing"}
			
	return {"action": ActionType.HOLD, "target": null, "utility_score": 0.0, "reason": "Default"}

func get_nearest(enemies: Array) -> Node:
	if enemies.is_empty(): return null
	var best: Node = enemies[0]
	var min_dist: float = unit.global_position.distance_to(best.global_position)
	for i in range(1, enemies.size()):
		var d: float = unit.global_position.distance_to(enemies[i].global_position)
		if d < min_dist:
			min_dist = d
			best = enemies[i]
	return best
