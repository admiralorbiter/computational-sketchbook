class_name BaseOrder extends Resource

enum OrderType { MOVE, HOLD, WATCH_SECTOR, SUPPRESS_AREA, FALLBACK, ATTACK, HEAL }
enum OrderPriority { LOW, NORMAL, HIGH, CRITICAL }

@export var type: OrderType = OrderType.HOLD
var issuer: Object # The one who gave the order
var subjects: Array = [] # Array of unit references
var target: Variant # Vector2 or Node (unit)
@export var priority: OrderPriority = OrderPriority.NORMAL

var completion_condition: Callable
var cancellation_condition: Callable

## Returns true if the order is considered complete.
func is_complete() -> bool:
	if completion_condition.is_valid():
		return completion_condition.call()
	return false
