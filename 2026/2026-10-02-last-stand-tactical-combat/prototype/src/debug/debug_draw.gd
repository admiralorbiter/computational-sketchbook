class_name DebugDraw
extends Node2D
## Custom canvas item for drawing debug overlay shapes and labels.

var overlay: CanvasLayer

func _process(_delta: float) -> void:
	if overlay and overlay.is_active:
		queue_redraw()

func _draw() -> void:
	if not overlay or not overlay.is_active or not is_instance_valid(overlay.units_container):
		return
	for unit in overlay.units_container.get_children():
		draw_circle(unit.position, 16.0, Color(1.0, 0.0, 0.0, 0.2))
		if unit.has_method("get_debug_state"):
			var state: Dictionary = unit.get_debug_state()
			var action_str: String = str(state.get("action", ""))
			if not action_str.is_empty():
				draw_string(ThemeDB.fallback_font, unit.position + Vector2(0, -20), action_str, HORIZONTAL_ALIGNMENT_CENTER, -1, 12, Color.YELLOW)
