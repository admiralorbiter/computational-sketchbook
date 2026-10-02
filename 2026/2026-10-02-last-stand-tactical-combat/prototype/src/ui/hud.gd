class_name HUD
extends CanvasLayer
## In-game Head-Up Display: phase indicators, start raid trigger, build palette, and unit info.

signal start_raid_pressed
signal build_item_selected(deployable_name: String)

@onready var phase_label: Label = Label.new()
@onready var timer_label: Label = Label.new()
@onready var budget_label: Label = Label.new()
@onready var speed_label: Label = Label.new()
@onready var build_mode_label: Label = Label.new()

@onready var start_raid_btn: Button = Button.new()
@onready var build_bar: HBoxContainer = HBoxContainer.new()

@onready var selection_panel: Panel = Panel.new()
@onready var selection_info: Label = Label.new()

func _ready() -> void:
	_setup_ui()

func _setup_ui() -> void:
	var top_bar := HBoxContainer.new()
	top_bar.set_anchors_preset(Control.PRESET_TOP_WIDE)
	top_bar.offset_left = 20
	top_bar.offset_top = 10
	top_bar.offset_right = -20
	top_bar.offset_bottom = 50
	top_bar.add_theme_constant_override("separation", 25)
	add_child(top_bar)
	
	phase_label.text = "PHASE: PREPARATION"
	phase_label.add_theme_color_override("font_color", Color(0.9, 0.85, 0.3))
	top_bar.add_child(phase_label)
	
	budget_label.text = "BUDGET: $200"
	budget_label.add_theme_color_override("font_color", Color(0.3, 0.9, 0.4))
	top_bar.add_child(budget_label)
	
	timer_label.text = "TIME: 480.0s"
	top_bar.add_child(timer_label)
	
	speed_label.text = "SPEED: 1.0x"
	top_bar.add_child(speed_label)
	
	start_raid_btn.text = "▶ START RAID [ENGAGE]"
	start_raid_btn.custom_minimum_size = Vector2(220, 40)
	start_raid_btn.add_theme_color_override("font_color", Color.WHITE)
	start_raid_btn.pressed.connect(func(): start_raid_pressed.emit())
	top_bar.add_child(start_raid_btn)
	
	build_mode_label.set_anchors_preset(Control.PRESET_TOP_WIDE)
	build_mode_label.offset_top = 60
	build_mode_label.offset_bottom = 90
	build_mode_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	build_mode_label.add_theme_color_override("font_color", Color(1.0, 0.8, 0.2))
	build_mode_label.hide()
	add_child(build_mode_label)
	
	build_bar.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	build_bar.offset_left = 40
	build_bar.offset_top = -140
	build_bar.offset_right = -40
	build_bar.offset_bottom = -90
	build_bar.alignment = BoxContainer.ALIGNMENT_CENTER
	build_bar.add_theme_constant_override("separation", 12)
	add_child(build_bar)
	
	_add_build_btn("Wall ($15)", "wall")
	_add_build_btn("Sandbag ($8)", "sandbag")
	_add_build_btn("Wire ($5)", "wire")
	_add_build_btn("Mine ($12)", "mine")
	_add_build_btn("Ammo ($10)", "ammo")
	
	selection_panel.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	selection_panel.offset_top = -80
	selection_panel.offset_left = 20
	selection_panel.offset_right = -20
	selection_panel.offset_bottom = -10
	add_child(selection_panel)
	
	selection_info.set_anchors_preset(Control.PRESET_FULL_RECT)
	selection_info.offset_left = 15
	selection_info.offset_top = 10
	selection_info.offset_right = -15
	selection_info.offset_bottom = -10
	selection_info.text = "Drag box or Click to select defenders. Hotkeys: [W] Watch Sector arc  |  [Right-Click] Move  |  [Space] Pause"
	selection_panel.add_child(selection_info)

func _add_build_btn(label_text: String, item_type: String) -> void:
	var btn := Button.new()
	btn.text = label_text
	btn.custom_minimum_size = Vector2(140, 36)
	btn.pressed.connect(func(): build_item_selected.emit(item_type))
	build_bar.add_child(btn)

func update_phase(phase_name: String) -> void:
	phase_label.text = "PHASE: " + phase_name
	if phase_name == "BATTLE":
		start_raid_btn.hide()
		build_bar.hide()
		update_build_mode(false, "")
	elif phase_name == "PREPARATION":
		start_raid_btn.show()
		build_bar.show()

func update_timer(time_left: float) -> void:
	timer_label.text = "TIME: %0.1fs" % time_left

func update_budget(budget: int) -> void:
	budget_label.text = "BUDGET: $%d" % budget

func update_speed(speed: float) -> void:
	speed_label.text = "SPEED: %0.1fx" % speed

func update_build_mode(active: bool, item_name: String) -> void:
	if active:
		build_mode_label.text = "PLACING: %s — Left-click to place, Right-click to cancel" % item_name.capitalize()
		build_mode_label.show()
	else:
		build_mode_label.hide()

func update_selection(selected_units: Array[Node]) -> void:
	if selected_units.is_empty():
		selection_info.text = "No units selected. Box drag or click to command defenders. [W + Drag] sets Watch Sector!"
	elif selected_units.size() == 1:
		var u: Unit = selected_units[0] as Unit
		if u:
			var order_text: String = "Holding position"
			if u.current_order is SectorOrder:
				order_text = "Watching Sector (Arc active)"
			elif u.current_state == Unit.State.MOVING:
				order_text = "Repositioning"
			selection_info.text = "Selected: %s (%s)  |  HP: %d/%d  |  Suppression: %d%%  |  Order: %s" % [
				u.role_label, u.unit_type, int(u.hp), int(u.max_hp), int(u.suppression), order_text
			]
	else:
		selection_info.text = "Selected: %d Units. Press [W + Drag] to assign a shared Watch Sector arc!" % selected_units.size()
