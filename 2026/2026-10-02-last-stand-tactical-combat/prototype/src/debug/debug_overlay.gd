class_name DebugOverlay
extends CanvasLayer
## Visualization overlay for debugging AI and simulation state.

var is_active: bool = false
var units_container: Node2D

const DebugDrawScript = preload("res://src/debug/debug_draw.gd")

func _ready() -> void:
	layer = 100
	var overlay_node = DebugDrawScript.new()
	overlay_node.name = "DrawNode"
	overlay_node.overlay = self
	add_child(overlay_node)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and event.keycode == KEY_F1:
		is_active = !is_active
		visible = is_active
