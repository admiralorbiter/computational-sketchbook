class_name FallbackOrder extends BaseOrder

enum TriggerCondition { MANUAL, HEALTH_LOW, OVERRUN, SQUAD_CASUALTIES }

@export var fallback_position: Vector2
@export var trigger_condition: TriggerCondition = TriggerCondition.MANUAL
@export var health_threshold: float = 0.3

func _init() -> void:
	type = OrderType.FALLBACK

func is_triggered(unit: Node) -> bool:
	if trigger_condition == TriggerCondition.HEALTH_LOW:
		if unit.has_method("get_health_percent") and unit.get_health_percent() <= health_threshold:
			return true
	return false
