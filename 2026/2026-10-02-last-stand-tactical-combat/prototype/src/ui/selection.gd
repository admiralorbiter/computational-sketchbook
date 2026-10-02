class_name SelectionSystem
extends Node2D
## Handles RTS-style unit selection.

signal selection_changed

var selected_units: Array[Node] = []
var control_groups: Dictionary = {}

var _is_dragging: bool = false
var _drag_start: Vector2 = Vector2.ZERO
var _drag_current: Vector2 = Vector2.ZERO

func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if event.pressed:
			_is_dragging = true
			_drag_start = get_viewport().get_canvas_transform().affine_inverse() * event.position
			_drag_current = _drag_start
		else:
			_is_dragging = false
			_process_selection_box(Input.is_key_pressed(KEY_SHIFT))
			queue_redraw()
			
	elif event is InputEventMouseMotion and _is_dragging:
		_drag_current = get_viewport().get_canvas_transform().affine_inverse() * event.position
		queue_redraw()
		
	elif event is InputEventKey and event.pressed:
		_handle_control_groups(event)

func _process_selection_box(append: bool) -> void:
	var rect := Rect2(_drag_start, _drag_current - _drag_start).abs()
	
	if not append:
		clear_selection()
		
	var units_node: Node = get_tree().get_first_node_in_group("units_container")
	if not units_node:
		return
		
	for unit in units_node.get_children():
		if not unit.is_in_group("defenders"):
			continue
			
		var unit_pos: Vector2 = unit.global_position
		# If click (small rect), check distance
		if rect.size.length_squared() < 100:
			if unit_pos.distance_to(_drag_start) < 20.0:
				_select_unit(unit, append)
				break # Only select one on click
		elif rect.has_point(unit_pos):
			_select_unit(unit, true)
			
	selection_changed.emit()

func _select_unit(unit: Node, append: bool) -> void:
	if not append:
		clear_selection()
	if not selected_units.has(unit):
		selected_units.append(unit)
		if unit.has_method("set_selected"):
			unit.set_selected(true)

func clear_selection() -> void:
	for unit in selected_units:
		if is_instance_valid(unit) and unit.has_method("set_selected"):
			unit.set_selected(false)
	selected_units.clear()
	selection_changed.emit()

func _handle_control_groups(event: InputEventKey) -> void:
	# Check keys 1-9
	for i in range(1, 10):
		var key: int = KEY_0 + i
		if event.keycode == key:
			if Input.is_key_pressed(KEY_CTRL):
				_assign_control_group(i)
			else:
				_recall_control_group(i)

func _assign_control_group(group_id: int) -> void:
	control_groups[group_id] = selected_units.duplicate()

func _recall_control_group(group_id: int) -> void:
	if control_groups.has(group_id):
		clear_selection()
		for unit in control_groups[group_id]:
			if is_instance_valid(unit):
				_select_unit(unit, true)
		selection_changed.emit()

func _draw() -> void:
	if _is_dragging:
		var rect := Rect2(_drag_start, _drag_current - _drag_start).abs()
		draw_rect(rect, Color(0.2, 0.8, 0.2, 0.3))
		draw_rect(rect, Color(0.2, 0.8, 0.2, 0.8), false)

# Needs to be called from a CanvasItem _draw (e.g. a UI overlay or dedicated Node2D)
func draw_selection_box(canvas_item: CanvasItem) -> void:
	if _is_dragging:
		var rect := Rect2(_drag_start, _drag_current - _drag_start).abs()
		canvas_item.draw_rect(rect, Color(0.2, 0.8, 0.2, 0.3))
		canvas_item.draw_rect(rect, Color(0.2, 0.8, 0.2, 0.8), false)
