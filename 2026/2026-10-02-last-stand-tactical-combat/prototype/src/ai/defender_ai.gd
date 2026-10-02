class_name DefenderAI extends Node

enum ActionType { FIRE, MOVE_TO_COVER, RELOAD, HOLD, RETREAT, HEAL_ALLY }

var unit: Node
var order_manager: OrderManager

func _ready() -> void:
	unit = get_parent()
	order_manager = get_tree().get_first_node_in_group("order_manager")

func evaluate(visible_enemies: Array, delta: float) -> Dictionary:
	var current_order: BaseOrder = order_manager.get_current_order(unit) if order_manager else null
	
	# Check ammo (assuming unit has weapon stats)
	var ammo_pct: float = unit.get_ammo_percent() if unit.has_method("get_ammo_percent") else 1.0
	if ammo_pct < 0.2 and visible_enemies.is_empty():
		return {"action": ActionType.RELOAD, "target": null, "utility_score": 100.0, "reason": "Auto-reload when clear"}
		
	# Check suppression
	var suppression: float = unit.suppression_level if "suppression_level" in unit else 0.0
	if suppression > 0.8:
		# Seek cover
		return {"action": ActionType.MOVE_TO_COVER, "target": null, "utility_score": 90.0, "reason": "Heavily suppressed"}
	
	if current_order is SectorOrder:
		var best_target: Node = null
		var best_score: float = -1.0
		var weapon: Resource = unit.weapon if "weapon" in unit else null
		
		for enemy in visible_enemies:
			if current_order.is_target_in_sector(enemy.global_position):
				var eval_data: Dictionary = AIUtility.score_target(unit, enemy, weapon)
				if eval_data.score > best_score:
					best_score = eval_data.score
					best_target = enemy
		
		if best_target != null:
			return {"action": ActionType.FIRE, "target": best_target, "utility_score": best_score, "reason": "Target in sector"}
		else:
			return {"action": ActionType.HOLD, "target": current_order.sector_direction, "utility_score": 10.0, "reason": "Holding sector"}
			
	return {"action": ActionType.HOLD, "target": null, "utility_score": 0.0, "reason": "No actionable order"}
