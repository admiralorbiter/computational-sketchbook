class_name CommandUI
extends Node
## Handles giving commands to selected units.

enum CommandState {
	NORMAL,
	WATCH_SECTOR_DRAG,
	SUPPRESS_TARGET,
	FALLBACK_TARGET,
	BUILD_MODE
}

var current_state: CommandState = CommandState.NORMAL
var selection_system: SelectionSystem
var _drag_start: Vector2 = Vector2.ZERO

func _ready() -> void:
	selection_system = get_parent().get_node_or_null("SelectionSystem")

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		set_state(CommandState.NORMAL)
		return
		
	match current_state:
		CommandState.NORMAL:
			_handle_normal_input(event)
		CommandState.WATCH_SECTOR_DRAG:
			_handle_watch_sector_input(event)
		CommandState.SUPPRESS_TARGET:
			_handle_suppress_input(event)
		CommandState.FALLBACK_TARGET:
			_handle_fallback_input(event)

func set_state(new_state: CommandState) -> void:
	current_state = new_state
	# TODO: Update cursor based on state

func _handle_normal_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		if event.keycode == KEY_W:
			set_state(CommandState.WATCH_SECTOR_DRAG)
		elif event.keycode == KEY_F:
			set_state(CommandState.SUPPRESS_TARGET)
		elif event.keycode == KEY_R:
			set_state(CommandState.FALLBACK_TARGET)
			
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_RIGHT and event.pressed:
		var target_pos: Vector2 = get_viewport().get_canvas_transform().affine_inverse() * event.position
		_issue_order_to_selection("move", {"position": target_pos})

func _handle_watch_sector_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		var pos: Vector2 = get_viewport().get_canvas_transform().affine_inverse() * event.position
		if event.pressed:
			_drag_start = pos
		else:
			var dir: Vector2 = (pos - _drag_start).normalized()
			if dir.length_squared() > 0:
				_issue_order_to_selection("watch_sector", {"position": _drag_start, "direction": dir})
			set_state(CommandState.NORMAL)

func _handle_suppress_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		var target_pos: Vector2 = get_viewport().get_canvas_transform().affine_inverse() * event.position
		_issue_order_to_selection("suppress", {"position": target_pos})
		set_state(CommandState.NORMAL)

func _handle_fallback_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		var target_pos: Vector2 = get_viewport().get_canvas_transform().affine_inverse() * event.position
		_issue_order_to_selection("fallback", {"position": target_pos})
		set_state(CommandState.NORMAL)

func _issue_order_to_selection(order_type: String, params: Dictionary) -> void:
	if not selection_system:
		return
		
	for unit in selection_system.selected_units:
		if is_instance_valid(unit) and unit.has_method("issue_order"):
			unit.issue_order(order_type, params)
