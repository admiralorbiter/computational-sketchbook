class_name OrderManager extends Node

signal order_assigned(unit: Node, order: BaseOrder)
signal order_completed(unit: Node, order: BaseOrder)
signal order_cancelled(unit: Node, order: BaseOrder)

# active_orders: Dictionary mapping unit (Node) -> Array of Orders (priority-sorted)
var active_orders: Dictionary = {}

func assign_order(unit: Node, order: BaseOrder) -> void:
	if not active_orders.has(unit):
		active_orders[unit] = []
	
	order.subjects = [unit]
	
	# Insert in priority-sorted order (highest priority first)
	var orders: Array = active_orders[unit]
	var inserted: bool = false
	for i in range(orders.size()):
		if order.priority > orders[i].priority:
			orders.insert(i, order)
			inserted = true
			break
	if not inserted:
		orders.append(order)
	
	order_assigned.emit(unit, order)

func get_current_order(unit: Node) -> BaseOrder:
	if active_orders.has(unit) and active_orders[unit].size() > 0:
		return active_orders[unit][0]
	return null

func clear_orders(unit: Node) -> void:
	if active_orders.has(unit):
		for order in active_orders[unit]:
			order_cancelled.emit(unit, order)
		active_orders[unit].clear()

func _process(delta: float) -> void:
	for unit in active_orders.keys():
		var orders: Array = active_orders[unit]
		if orders.size() > 0:
			var current: BaseOrder = orders[0]
			if current.has_method("update"):
				current.update(delta)
			if current.is_complete():
				orders.pop_front()
				order_completed.emit(unit, current)
