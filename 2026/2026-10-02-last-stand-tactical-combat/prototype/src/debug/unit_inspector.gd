class_name UnitInspector
extends Panel
## UI Panel showing detailed internal state of a specific unit.

var target_unit: Node = null
@onready var info_label: Label = Label.new()

func _ready() -> void:
	hide()
	custom_minimum_size = Vector2(250, 300)
	set_anchors_preset(Control.PRESET_RIGHT_WIDE)
	
	var vbox := VBoxContainer.new()
	vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(vbox)
	
	vbox.add_child(info_label)

func _process(_delta: float) -> void:
	if not visible or not is_instance_valid(target_unit):
		return
		
	if target_unit.has_method("get_debug_state"):
		var state: Dictionary = target_unit.get_debug_state()
		var text := "Unit: " + target_unit.name + "\n"
		for key in state:
			text += str(key) + ": " + str(state[key]) + "\n"
		info_label.text = text

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		# Very naive click detection for debugging
		if get_parent() and get_parent().get("is_active"):
			# Debug overlay is active, try to pick a unit
			var click_pos: Vector2 = get_viewport().get_canvas_transform().affine_inverse() * event.position
			var units_node: Node = get_tree().get_first_node_in_group("units_container")
			if units_node:
				for unit in units_node.get_children():
					if unit.global_position.distance_to(click_pos) < 20.0:
						target_unit = unit
						show()
						get_viewport().set_input_as_handled()
						return
			target_unit = null
			hide()
