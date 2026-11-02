extends Node2D

enum GamePhase {
	BRIEFING,
	PREPARATION,
	ORDERS,
	BATTLE,
	AFTER_ACTION
}

var current_phase: GamePhase = GamePhase.BRIEFING
var scenario: Scenario

@onready var camera: Camera2D = $Camera2D
@onready var units_container: Node2D = $Units
@onready var deployables_container: Node2D = $Deployables
@onready var hud_layer: CanvasLayer = $HUDLayer
@onready var debug_layer: CanvasLayer = $DebugLayer

const BattlefieldViewScript = preload("res://src/battlefield_view.gd")
const DeployableNodeScript = preload("res://src/building/deployable_node.gd")

var battlefield_view: Node2D
var build_manager: BuildManager
var selection_system: SelectionSystem
var command_ui: CommandUI

var battle_time_remaining: float = 480.0
var battle_active: bool = false
var enemy_spawn_timer: float = 2.0
var enemies_to_spawn: Array[Dictionary] = []

var hud: HUD
var active_deployable_to_place: String = ""

var build_mode_active: bool = false
var build_mode_item: String = ""
var build_ghost: Node2D = null

var enemies_killed: int = 0
var defenders_lost: int = 0

func _ready() -> void:
	_setup_camera()
	_setup_battlefield()
	_setup_systems()
	_load_scenario()
	_spawn_initial_defenders()
	_enter_phase(GamePhase.BRIEFING)

func _setup_camera() -> void:
	camera.position = Vector2(880, 640)
	camera.zoom = Vector2(0.7, 0.7)

func _setup_battlefield() -> void:
	battlefield_view = BattlefieldViewScript.new()
	battlefield_view.name = "BattlefieldView"
	add_child(battlefield_view)
	move_child(battlefield_view, 0)
	
	_place_starting_fortification(Vector2(26 * 32, 18 * 32), "sandbag")
	_place_starting_fortification(Vector2(26 * 32, 19 * 32), "sandbag")
	_place_starting_fortification(Vector2(26 * 32, 21 * 32), "sandbag")
	_place_starting_fortification(Vector2(26 * 32, 22 * 32), "sandbag")
	_place_starting_fortification(Vector2(24 * 32, 14 * 32), "sandbag")
	_place_starting_fortification(Vector2(24 * 32, 26 * 32), "sandbag")

func _setup_systems() -> void:
	selection_system = SelectionSystem.new()
	selection_system.name = "SelectionSystem"
	add_child(selection_system)
	selection_system.selection_changed.connect(_on_selection_changed)
	
	command_ui = CommandUI.new()
	command_ui.name = "CommandUI"
	add_child(command_ui)
	
	var sim_controls := SimControls.new()
	sim_controls.name = "SimControls"
	add_child(sim_controls)
	
	build_manager = BuildManager.new()
	build_manager.name = "BuildManager"
	build_manager.initialize(GameConstants.BUILD_BUDGET)
	add_child(build_manager)
	
	hud = HUD.new()
	hud.name = "HUD"
	hud.start_raid_pressed.connect(_on_start_raid)
	hud.build_item_selected.connect(_on_build_item_selected)
	hud_layer.add_child(hud)
	
	var briefing := BriefingUI.new()
	briefing.name = "BriefingUI"
	briefing.begin_preparation.connect(_on_briefing_finished)
	hud_layer.add_child(briefing)
	
	var aar := AARUI.new()
	aar.name = "AARUI"
	aar.hide()
	hud_layer.add_child(aar)
	
	var debug_overlay := DebugOverlay.new()
	debug_overlay.name = "DebugOverlay"
	debug_overlay.units_container = units_container
	debug_layer.add_child(debug_overlay)
	
	SimManager.tick_processed.connect(_on_sim_tick)

func _load_scenario() -> void:
	scenario = Scenario.new()
	scenario.scenario_name = "Battle 001: East Approach Relay Defense"
	scenario.description = "Incoming hostile raiders approaching from the East Field in waves.\nDefend the central communication relay at all costs."
	scenario.objective_text = "Hold the relay for 8 minutes or eliminate all hostile forces."
	scenario.build_budget = GameConstants.BUILD_BUDGET

func _spawn_initial_defenders() -> void:
	_spawn_defender("Machine Gunner", "MG", Vector2(23 * 32, 20 * 32), _create_lmg(), Vector2.RIGHT, PI * 0.3)
	_spawn_defender("Rifleman Alpha", "RFL", Vector2(24 * 32, 17 * 32), _create_rifle(), Vector2(1.0, -0.3).normalized(), PI * 0.35)
	_spawn_defender("Rifleman Bravo", "RFL", Vector2(24 * 32, 23 * 32), _create_rifle(), Vector2(1.0, 0.3).normalized(), PI * 0.35)
	_spawn_defender("Rifleman Charlie", "RFL", Vector2(19 * 32, 13 * 32), _create_rifle(), Vector2(0.5, -1.0).normalized(), PI * 0.4)
	_spawn_defender("Shotgunner", "SHT", Vector2(19 * 32, 20 * 32), _create_shotgun(), Vector2.RIGHT, PI * 0.45)
	_spawn_defender("Field Medic", "MED", Vector2(16 * 32, 20 * 32), _create_pistol(), Vector2.RIGHT, PI * 0.5)

func _spawn_defender(unit_name: String, label: String, pos: Vector2, weapon_data: WeaponData, watch_dir: Vector2, arc_half_angle: float) -> Unit:
	var u := Unit.new()
	u.team = Unit.Team.DEFENDER
	u.unit_type = unit_name
	u.role_label = label
	u.position = pos
	u.weapon = weapon_data
	u.max_hp = 100.0
	u.hp = 100.0
	u.facing_direction = watch_dir
	
	var order := SectorOrder.new()
	order.sector_origin = pos
	order.sector_direction = watch_dir
	order.sector_angle = arc_half_angle
	order.engagement_range = weapon_data.effective_range
	u.current_order = order
	
	u.killed.connect(_on_unit_killed.bind(u))
	
	units_container.add_child(u)
	return u

func _enter_phase(phase: GamePhase) -> void:
	current_phase = phase
	
	match phase:
		GamePhase.BRIEFING:
			hud.hide()
			var briefing: BriefingUI = hud_layer.get_node("BriefingUI")
			briefing.setup(scenario)
			briefing.show()
			
		GamePhase.PREPARATION:
			hud.show()
			hud.update_phase("PREPARATION")
			hud.update_budget(build_manager.budget_remaining)
			
		GamePhase.BATTLE:
			_exit_build_mode()
			hud.show()
			hud.update_phase("BATTLE")
			battle_active = true
			if "show_threat_arrows" in battlefield_view:
				battlefield_view.show_threat_arrows = false
			SimManager.change_state(SimManager.GameState.BATTLE)
			_queue_attacker_waves()
			
		GamePhase.AFTER_ACTION:
			battle_active = false
			SimManager.change_state(SimManager.GameState.AFTER_ACTION)
			hud.hide()
			var aar: AARUI = hud_layer.get_node("AARUI")
			var won: bool = float(battlefield_view.get("relay_hp")) > 0.0
			aar.setup({
				"result": Objectives.Result.WIN if won else Objectives.Result.LOSE,
				"time_survived": 480.0 - battle_time_remaining,
				"enemies_killed": enemies_killed,
				"defenders_lost": defenders_lost,
				"reason": "Relay defended!" if won else "Relay destroyed!"
			})
			aar.show()

func _on_briefing_finished() -> void:
	_enter_phase(GamePhase.PREPARATION)

func _on_start_raid() -> void:
	_enter_phase(GamePhase.BATTLE)

func _queue_attacker_waves() -> void:
	for i in range(4):
		enemies_to_spawn.append({"type": "rusher", "delay": 5.0 + i * 2.5, "label": "RSH", "y": randf_range(10 * 32, 30 * 32)})
	for i in range(6):
		enemies_to_spawn.append({"type": "rifleman", "delay": 30.0 + i * 2.0, "label": "RFL", "y": randf_range(10 * 32, 30 * 32)})
	for i in range(4):
		enemies_to_spawn.append({"type": "rusher", "delay": 60.0 + i * 2.0, "label": "RSH", "y": randf_range(10 * 32, 30 * 32)})
		enemies_to_spawn.append({"type": "rifleman", "delay": 60.0 + i * 2.0, "label": "RFL", "y": randf_range(10 * 32, 30 * 32)})
	for i in range(2):
		enemies_to_spawn.append({"type": "breacher", "delay": 120.0 + i * 3.0, "label": "BRC", "y": randf_range(10 * 32, 30 * 32)})
	for i in range(6):
		enemies_to_spawn.append({"type": "rifleman", "delay": 120.0 + i * 2.0, "label": "RFL", "y": randf_range(10 * 32, 30 * 32)})
	for i in range(6):
		enemies_to_spawn.append({"type": "rusher", "delay": 180.0 + i * 2.0, "label": "RSH", "y": randf_range(10 * 32, 30 * 32)})
	for i in range(4):
		enemies_to_spawn.append({"type": "rifleman", "delay": 180.0 + i * 3.0, "label": "RFL", "y": randf_range(10 * 32, 30 * 32)})
	for i in range(2):
		enemies_to_spawn.append({"type": "breacher", "delay": 180.0 + i * 4.0, "label": "BRC", "y": randf_range(10 * 32, 30 * 32)})

func _process(delta: float) -> void:
	_handle_camera_movement(delta)
	
	if build_mode_active and is_instance_valid(build_ghost):
		build_ghost.global_position = get_global_mouse_position().snapped(Vector2(32, 32))
	
	if current_phase == GamePhase.BATTLE and battle_active:
		battle_time_remaining = maxf(0.0, battle_time_remaining - delta)
		hud.update_timer(battle_time_remaining)
		
		for i in range(enemies_to_spawn.size() - 1, -1, -1):
			enemies_to_spawn[i]["delay"] -= delta
			if enemies_to_spawn[i]["delay"] <= 0.0:
				var info: Dictionary = enemies_to_spawn[i]
				_spawn_attacker(info["type"], info["label"], Vector2(42 * 32, info["y"]))
				enemies_to_spawn.remove_at(i)
				
		var attackers := get_tree().get_nodes_in_group("attackers")
		var living_attackers := 0
		for a in attackers:
			if (a as Unit).current_state != Unit.State.DEAD:
				living_attackers += 1
		
		var defenders := get_tree().get_nodes_in_group("defenders")
		var living_defenders := 0
		for d in defenders:
			if (d as Unit).current_state != Unit.State.DEAD:
				living_defenders += 1
				
		if float(battlefield_view.get("relay_hp")) <= 0.0 or living_defenders == 0:
			_enter_phase(GamePhase.AFTER_ACTION)
		elif battle_time_remaining <= 0.0 or (enemies_to_spawn.is_empty() and living_attackers == 0):
			_enter_phase(GamePhase.AFTER_ACTION)

func _on_sim_tick(tick: int) -> void:
	var delta_tick := GameConstants.TICK_DELTA
	for unit in units_container.get_children():
		if unit is Unit:
			(unit as Unit).sim_tick(delta_tick)

func _spawn_attacker(unit_type: String, label: String, pos: Vector2) -> Unit:
	var u := Unit.new()
	u.team = Unit.Team.ATTACKER
	u.unit_type = unit_type
	u.role_label = label
	u.position = pos
	u.facing_direction = Vector2.LEFT
	
	match unit_type:
		"rusher":
			u.max_hp = 70.0
			u.hp = 70.0
			u.speed_multiplier = GameConstants.SPEED_SPRINT
			u.weapon = _create_melee()
		"breacher":
			u.max_hp = 120.0
			u.hp = 120.0
			u.speed_multiplier = 3.5
			u.weapon = _create_shotgun()
		_:
			u.max_hp = 90.0
			u.hp = 90.0
			u.speed_multiplier = GameConstants.SPEED_NORMAL
			u.weapon = _create_rifle()
			
	u.killed.connect(_on_unit_killed.bind(u))
	
	units_container.add_child(u)
	return u

func _on_unit_killed(source: Unit, dead_unit: Unit) -> void:
	if dead_unit.team == Unit.Team.ATTACKER:
		enemies_killed += 1
	else:
		defenders_lost += 1

func _on_selection_changed() -> void:
	hud.update_selection(selection_system.selected_units)

func _on_build_item_selected(item_type: String) -> void:
	build_mode_active = true
	build_mode_item = item_type
	# Wait one frame so the button click doesn't immediately place
	await get_tree().process_frame
	
	if build_ghost:
		build_ghost.queue_free()
	
	build_ghost = Node2D.new()
	var rect := ColorRect.new()
	rect.color = Color(0.2, 0.8, 1.0, 0.4)
	rect.custom_minimum_size = Vector2(32, 32)
	rect.size = Vector2(32, 32)
	rect.position = Vector2(-16, -16)
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	build_ghost.add_child(rect)
	
	# Add a label showing what we're placing
	var lbl := Label.new()
	lbl.text = item_type.capitalize()
	lbl.position = Vector2(-16, -28)
	lbl.add_theme_font_size_override("font_size", 10)
	lbl.add_theme_color_override("font_color", Color(0.2, 0.9, 1.0))
	lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	build_ghost.add_child(lbl)
	
	add_child(build_ghost)
	hud.update_build_mode(true, item_type)

func _exit_build_mode() -> void:
	build_mode_active = false
	build_mode_item = ""
	if build_ghost:
		build_ghost.queue_free()
		build_ghost = null
	hud.update_build_mode(false, "")

func _place_starting_fortification(pos: Vector2, item_name: String) -> void:
	var dep := Deployable.new()
	dep.deployable_name = item_name
	match item_name:
		"wall":
			dep.hp = 150.0
			dep.cover_value = 1.0
		"sandbag":
			dep.hp = 60.0
			dep.cover_value = 0.40
		"wire":
			dep.hp = 30.0
			dep.cover_value = 0.0
		"mine":
			dep.hp = 1.0
			dep.cover_value = 0.0
	
	var node = DeployableNodeScript.new()
	node.position = pos
	node.setup(dep)
	deployables_container.add_child(node)

func _handle_camera_movement(delta: float) -> void:
	var move_vec := Vector2.ZERO
	if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP): move_vec.y -= 1
	if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN): move_vec.y += 1
	if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT): move_vec.x -= 1
	if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT): move_vec.x += 1
	
	camera.position += move_vec.normalized() * 600.0 * delta

func _unhandled_input(event: InputEvent) -> void:
	if build_mode_active:
		if event is InputEventMouseButton and event.pressed:
			if event.button_index == MOUSE_BUTTON_LEFT:
				var cost := 15
				match build_mode_item:
					"sandbag": cost = 8
					"wire": cost = 5
					"mine": cost = 12
					"ammo": cost = 10
				if build_manager.budget_remaining >= cost:
					build_manager.budget_remaining -= cost
					hud.update_budget(build_manager.budget_remaining)
					_place_starting_fortification(get_global_mouse_position().snapped(Vector2(32, 32)), build_mode_item)
				get_viewport().set_input_as_handled()
			elif event.button_index == MOUSE_BUTTON_RIGHT:
				_exit_build_mode()
				get_viewport().set_input_as_handled()
		elif event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
			_exit_build_mode()
			get_viewport().set_input_as_handled()
	else:
		if event is InputEventMouseButton:
			if event.button_index == MOUSE_BUTTON_WHEEL_UP:
				camera.zoom = (camera.zoom * 1.1).clamp(Vector2(0.4, 0.4), Vector2(2.0, 2.0))
			elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
				camera.zoom = (camera.zoom * 0.9).clamp(Vector2(0.4, 0.4), Vector2(2.0, 2.0))

func _create_rifle() -> WeaponData:
	var w := WeaponData.new()
	w.category = WeaponData.WeaponCategory.RIFLE
	w.damage = 18.0
	w.rpm = 120
	w.base_accuracy = 0.70
	w.moving_accuracy = 0.35
	w.effective_range = 30.0 * 32.0
	w.max_range = 45.0 * 32.0
	w.suppression_per_round = 3.0
	w.magazine_size = 30
	return w

func _create_lmg() -> WeaponData:
	var w := WeaponData.new()
	w.category = WeaponData.WeaponCategory.MACHINE_GUN
	w.damage = 12.0
	w.rpm = 600
	w.base_accuracy = 0.35
	w.moving_accuracy = 0.10
	w.effective_range = 35.0 * 32.0
	w.max_range = 50.0 * 32.0
	w.suppression_per_round = 5.0
	w.magazine_size = 100
	return w

func _create_shotgun() -> WeaponData:
	var w := WeaponData.new()
	w.category = WeaponData.WeaponCategory.SHOTGUN
	w.damage = 35.0
	w.rpm = 40
	w.base_accuracy = 0.85
	w.moving_accuracy = 0.60
	w.effective_range = 6.0 * 32.0
	w.max_range = 10.0 * 32.0
	w.suppression_per_round = 8.0
	w.magazine_size = 8
	return w

func _create_pistol() -> WeaponData:
	var w := WeaponData.new()
	w.category = WeaponData.WeaponCategory.PISTOL
	w.damage = 10.0
	w.rpm = 90
	w.base_accuracy = 0.50
	w.moving_accuracy = 0.35
	w.effective_range = 15.0 * 32.0
	w.max_range = 25.0 * 32.0
	w.suppression_per_round = 1.0
	w.magazine_size = 15
	return w

func _create_melee() -> WeaponData:
	var w := WeaponData.new()
	w.category = WeaponData.WeaponCategory.MELEE
	w.damage = 25.0
	w.rpm = 40
	w.base_accuracy = 0.80
	w.moving_accuracy = 0.80
	w.effective_range = 1.5 * 32.0
	w.max_range = 2.0 * 32.0
	w.suppression_per_round = 4.0
	return w
