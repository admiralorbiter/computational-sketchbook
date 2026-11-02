class_name BriefingUI
extends Control
## Displays scenario information before the preparation phase.

signal begin_preparation

var title_label: Label = Label.new()
var desc_label: Label = Label.new()
var obj_label: Label = Label.new()
var begin_button: Button = Button.new()

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	
	# Dimmed backdrop
	var bg := ColorRect.new()
	bg.color = Color(0.05, 0.07, 0.09, 0.88)
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	
	# Centered briefing card panel
	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(650, 420)
	panel.set_anchors_preset(Control.PRESET_CENTER)
	panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	panel.grow_vertical = Control.GROW_DIRECTION_BOTH
	add_child(panel)
	
	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 30)
	margin.add_theme_constant_override("margin_top", 30)
	margin.add_theme_constant_override("margin_right", 30)
	margin.add_theme_constant_override("margin_bottom", 30)
	panel.add_child(margin)
	
	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 18)
	margin.add_child(vbox)
	
	# Header
	var header := Label.new()
	header.text = "MISSION BRIEFING // BATTLE 001"
	header.add_theme_color_override("font_color", Color(0.4, 0.8, 1.0))
	header.add_theme_font_size_override("font_size", 14)
	vbox.add_child(header)
	
	# Scenario Title
	title_label.text = "East Approach Relay Defense"
	title_label.add_theme_font_size_override("font_size", 24)
	title_label.add_theme_color_override("font_color", Color.WHITE)
	vbox.add_child(title_label)
	
	# Divider
	var hsep := HSeparator.new()
	vbox.add_child(hsep)
	
	# Description
	desc_label.text = "A hostile raid force is approaching from the East Field in waves.\nBuild your fortifications and establish defensive firing sectors before commencing engagement."
	desc_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	desc_label.add_theme_font_size_override("font_size", 15)
	desc_label.add_theme_color_override("font_color", Color(0.8, 0.85, 0.9))
	vbox.add_child(desc_label)
	
	# Objectives
	obj_label.text = "OBJECTIVES:\n • Protect the Central Communication Relay (200 HP)\n • Neutralize all approaching hostile raiders\n • Hold position for 8 minutes"
	obj_label.add_theme_font_size_override("font_size", 14)
	obj_label.add_theme_color_override("font_color", Color(0.9, 0.8, 0.3))
	vbox.add_child(obj_label)
	
	# Doctrine Tip
	var tip_label := Label.new()
	tip_label.text = "DOCTRINE TIP: Use the Machine Gun to lock down the open corridor with heavy suppression. Set Riflemen to cover adjacent angles."
	tip_label.add_theme_font_size_override("font_size", 12)
	tip_label.add_theme_color_override("font_color", Color(0.6, 0.7, 0.75))
	vbox.add_child(tip_label)
	
	# Action button
	begin_button.text = "▶ ENTER PREPARATION PHASE"
	begin_button.custom_minimum_size = Vector2(0, 48)
	begin_button.add_theme_font_size_override("font_size", 16)
	begin_button.pressed.connect(_on_begin_pressed)
	vbox.add_child(begin_button)

func setup(scenario: Scenario) -> void:
	if scenario:
		title_label.text = scenario.scenario_name
		desc_label.text = scenario.description
		obj_label.text = "OBJECTIVES:\n" + scenario.objective_text

func _on_begin_pressed() -> void:
	begin_preparation.emit()
	hide()
