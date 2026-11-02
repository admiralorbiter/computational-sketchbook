class_name SuppressOrder extends BaseOrder

@export var target_area_center: Vector2
@export var target_area_radius: float
@export var duration: float = -1.0

var _time_active: float = 0.0

func _init() -> void:
	type = OrderType.SUPPRESS_AREA

func update(delta: float) -> void:
	if duration > 0.0:
		_time_active += delta

func is_complete() -> bool:
	if duration > 0.0 and _time_active >= duration:
		return true
	return false
