class_name AARUI
extends Control
## After-Action Report displayed at the end of a scenario.

signal retry_requested
signal next_requested

@onready var result_label: Label = Label.new()
@onready var reason_label: Label = Label.new()
@onready var stats_label: Label = Label.new()
@onready var retry_btn: Button = Button.new()
@onready var next_btn: Button = Button.new()

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var bg := ColorRect.new()
	bg.color = Color(0, 0, 0, 0.9)
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	
	var center_panel := PanelContainer.new()
	center_panel.set_anchors_preset(Control.PRESET_CENTER)
	center_panel.custom_minimum_size = Vector2(400, 300)
	add_child(center_panel)
	
	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 20)
	margin.add_theme_constant_override("margin_top", 20)
	margin.add_theme_constant_override("margin_right", 20)
	margin.add_theme_constant_override("margin_bottom", 20)
	center_panel.add_child(margin)
	
	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 20)
	margin.add_child(vbox)
	
	result_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	result_label.add_theme_font_size_override("font_size", 32)
	vbox.add_child(result_label)
	
	reason_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	reason_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8))
	vbox.add_child(reason_label)
	
	stats_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vbox.add_child(stats_label)
	
	var hbox := HBoxContainer.new()
	hbox.alignment = BoxContainer.ALIGNMENT_CENTER
	hbox.add_theme_constant_override("separation", 20)
	vbox.add_child(hbox)
	
	retry_btn.text = "RETRY"
	retry_btn.custom_minimum_size = Vector2(120, 40)
	retry_btn.pressed.connect(func() -> void: retry_requested.emit(); hide())
	hbox.add_child(retry_btn)
	
	next_btn.text = "NEXT"
	next_btn.custom_minimum_size = Vector2(120, 40)
	next_btn.disabled = true
	next_btn.pressed.connect(func() -> void: next_requested.emit(); hide())
	hbox.add_child(next_btn)

func setup(result_data: Dictionary) -> void:
	var result: int = result_data.get("result", Objectives.Result.LOSE)
	var reason: String = result_data.get("reason", "Unknown")
	var time_survived: float = result_data.get("time_survived", 0.0)
	var enemies_killed: int = result_data.get("enemies_killed", 0)
	var defenders_lost: int = result_data.get("defenders_lost", 0)
	
	if result == Objectives.Result.WIN:
		result_label.text = "VICTORY"
		result_label.modulate = Color.GREEN
	else:
		result_label.text = "DEFEAT"
		result_label.modulate = Color.RED
		
	reason_label.text = reason
		
	stats_label.text = "Time Survived: %ss\nEnemies Killed: %d\nDefenders Lost: %d" % [
		snapped(time_survived, 0.1), enemies_killed, defenders_lost
	]
