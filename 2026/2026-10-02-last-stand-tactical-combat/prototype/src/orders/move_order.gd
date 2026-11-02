class_name MoveOrder extends BaseOrder

enum MoveStance { SPRINT, NORMAL, CAREFUL }

@export var target_position: Vector2
@export var move_stance: MoveStance = MoveStance.NORMAL

func _init() -> void:
	type = OrderType.MOVE

func is_complete() -> bool:
	if subjects.is_empty() or not is_instance_valid(subjects[0]):
		return true
	var distance: float = subjects[0].global_position.distance_to(target_position)
	return distance <= 64.0
