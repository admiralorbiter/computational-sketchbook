class_name Unit extends Node2D
## Base Unit Simulation Class
## Handles health, morale, suppression, orders, firing, and visual presentation.

enum Team {
	DEFENDER,
	ATTACKER
}

enum State {
	IDLE,
	MOVING,
	FIRING,
	RELOADING,
	SUPPRESSED,
	PINNED,
	DOWNED,
	DEAD
}

signal damaged(amount: float, source: Unit)
signal killed(source: Unit)
signal downed()
signal suppression_changed(new_value: float)
signal state_changed(new_state: State)

var team: Team = Team.DEFENDER
var unit_type: String = "rifleman"
var role_label: String = "RFL"

var max_hp: float = GameConstants.BASE_HP
var hp: float = max_hp
var speed_multiplier: float = GameConstants.SPEED_NORMAL
var suppression: float = 0.0
var morale: float = GameConstants.MORALE_CONFIDENT

var weapon: WeaponData = null
var current_order = null 

var current_state: State = State.IDLE
var target_position: Vector2 = Vector2.ZERO
var facing_direction: Vector2 = Vector2.RIGHT
var is_selected: bool = false

var fire_cooldown: float = 0.0
var ammo_current: int = 30
var ammo_max: int = 30

var tracer_end: Vector2 = Vector2.ZERO
var tracer_alpha: float = 0.0
var advance_pause_timer: float = 0.0

var ai_node: Node = null

func _ready() -> void:
	if team == Team.DEFENDER:
		add_to_group("defenders")
	else:
		add_to_group("attackers")

func set_selected(val: bool) -> void:
	is_selected = val
	queue_redraw()

func issue_order(order_type: String, params: Dictionary) -> void:
	match order_type:
		"move":
			target_position = params.get("position", global_position)
			facing_direction = global_position.direction_to(target_position)
			current_order = null
			change_state(State.MOVING)
		"watch_sector":
			var sector := SectorOrder.new()
			sector.sector_origin = global_position
			sector.sector_direction = params.get("direction", Vector2.RIGHT)
			sector.sector_angle = params.get("angle", PI * 0.35) # ~63 deg half-angle = ~126 deg total
			sector.engagement_range = params.get("range", 35.0 * GameConstants.TILE_SIZE)
			current_order = sector
			facing_direction = sector.sector_direction
			change_state(State.IDLE)
		"suppress":
			var target_pos: Vector2 = params.get("position", global_position + facing_direction * 200.0)
			facing_direction = global_position.direction_to(target_pos)
			current_order = null
			_fire_at_position(target_pos)
		"fallback":
			target_position = params.get("position", global_position)
			facing_direction = global_position.direction_to(target_position)
			current_order = null
			change_state(State.MOVING)
	queue_redraw()

func change_state(new_state: State) -> void:
	if current_state != new_state:
		current_state = new_state
		state_changed.emit(current_state)
		queue_redraw()

func _process(delta: float) -> void:
	if tracer_alpha > 0.0:
		tracer_alpha = maxf(0.0, tracer_alpha - delta * 8.0)
		queue_redraw()

func sim_tick(delta_tick: float) -> void:
	if current_state == State.DEAD or current_state == State.DOWNED:
		return
		
	_process_movement(delta_tick)
	_process_suppression_decay(delta_tick)
	_process_combat(delta_tick)

func _process_movement(delta_tick: float) -> void:
	if current_state == State.MOVING:
		var dir := global_position.direction_to(target_position)
		var dist := global_position.distance_to(target_position)
		var move_step := speed_multiplier * GameConstants.TILE_SIZE * delta_tick
		facing_direction = dir
		
		if dist <= move_step:
			global_position = target_position
			change_state(State.IDLE)
		else:
			global_position += dir * move_step
		queue_redraw()

func _process_suppression_decay(delta_tick: float) -> void:
	if suppression > 0:
		suppression = maxf(0.0, suppression - (GameConstants.SUPPRESSION_DECAY * delta_tick))
		suppression_changed.emit(suppression)
		_eval_state_from_suppression()

func _eval_state_from_suppression() -> void:
	if current_state in [State.DEAD, State.DOWNED]:
		return
		
	var sup_level = Suppression.get_suppression_level(suppression)
	if sup_level == Suppression.SuppressionLevel.PINNED:
		change_state(State.PINNED)
	elif sup_level in [Suppression.SuppressionLevel.HEAVY, Suppression.SuppressionLevel.MEDIUM]:
		if current_state == State.IDLE:
			change_state(State.SUPPRESSED)
	else:
		if current_state in [State.PINNED, State.SUPPRESSED]:
			change_state(State.IDLE)

func _process_combat(delta_tick: float) -> void:
	if fire_cooldown > 0.0:
		fire_cooldown = maxf(0.0, fire_cooldown - delta_tick)
		return
		
	if current_state == State.PINNED:
		return # Cannot fire while pinned!
		
	# Find enemies
	var enemy_group := "attackers" if team == Team.DEFENDER else "defenders"
	var enemies := get_tree().get_nodes_in_group(enemy_group)
	if enemies.is_empty():
		return
		
	var best_target: Unit = null
	var min_dist: float = 999999.0
	
	for enemy in enemies:
		if not is_instance_valid(enemy) or enemy.current_state in [State.DEAD, State.DOWNED]:
			continue
		var dist: float = global_position.distance_to(enemy.global_position)
		
		# If we have a Sector Order, check if target is inside sector
		if current_order is SectorOrder:
			if not current_order.is_target_in_sector(enemy.global_position):
				continue
		elif dist > 35.0 * GameConstants.TILE_SIZE: # max range
			continue
			
		if dist < min_dist:
			min_dist = dist
			best_target = enemy
			
	if best_target:
		facing_direction = global_position.direction_to(best_target.global_position)
		_fire_at_target(best_target)
	elif team == Team.ATTACKER and current_state == State.IDLE:
		# Attackers advance toward compound if no defender in immediate range
		if advance_pause_timer > 0.0:
			advance_pause_timer = maxf(0.0, advance_pause_timer - delta_tick)
		else:
			var target_loc = Vector2(18 * GameConstants.TILE_SIZE, 20 * GameConstants.TILE_SIZE)
			var dist = global_position.distance_to(target_loc)
			if dist > 4.0 * GameConstants.TILE_SIZE:
				var bound_dist = randf_range(3.0, 5.0) * GameConstants.TILE_SIZE
				target_position = global_position.move_toward(target_loc, bound_dist)
				if unit_type == "rusher":
					advance_pause_timer = 0.0
				elif unit_type == "breacher":
					advance_pause_timer = randf_range(2.0, 3.0)
				else:
					advance_pause_timer = randf_range(1.0, 2.0)
			else:
				target_position = target_loc
			change_state(State.MOVING)

func _fire_at_target(target: Unit) -> void:
	if not weapon:
		return
		
	fire_cooldown = 60.0 / float(weapon.rpm)
	tracer_end = target.global_position
	tracer_alpha = 1.0
	
	var shot_result = CombatResolver.resolve_shot(self, target, weapon, Cover.CoverType.NONE)
	
	if shot_result.hit:
		target.take_damage(shot_result.damage, self)
		target.take_suppression(shot_result.suppression)
	elif shot_result.near_miss:
		target.take_suppression(shot_result.suppression)
		
	queue_redraw()

func _fire_at_position(pos: Vector2) -> void:
	if not weapon:
		return
	fire_cooldown = 60.0 / float(weapon.rpm)
	tracer_end = pos
	tracer_alpha = 1.0
	queue_redraw()

func take_damage(amount: float, source: Unit) -> void:
	if current_state == State.DEAD:
		return
		
	hp -= amount
	damaged.emit(amount, source)
	queue_redraw()
	
	if hp <= 0:
		hp = 0
		change_state(State.DEAD)
		killed.emit(source)

func take_suppression(amount: float) -> void:
	if current_state in [State.DEAD, State.DOWNED]:
		return
		
	suppression = minf(GameConstants.SUPPRESSION_MAX, suppression + amount)
	suppression_changed.emit(suppression)
	_eval_state_from_suppression()
	queue_redraw()

func _draw() -> void:
	var font = ThemeDB.fallback_font
	
	if current_state == State.DEAD:
		# Draw casualty marker
		draw_circle(Vector2.ZERO, 12.0, Color(0.15, 0.15, 0.15, 0.8))
		draw_line(Vector2(-6, -6), Vector2(6, 6), Color(0.9, 0.2, 0.2), 2.5)
		draw_line(Vector2(-6, 6), Vector2(6, -6), Color(0.9, 0.2, 0.2), 2.5)
		draw_string(font, Vector2(-10, 22), role_label, HORIZONTAL_ALIGNMENT_CENTER, 20, 10, Color(0.6, 0.6, 0.6, 0.7))
		return
		
	# 1. Watch Sector Arc (If selected and active order)
	if current_order is SectorOrder:
		var order: SectorOrder = current_order
		if is_selected:
			var arc_angle: float = order.sector_angle
			var arc_range: float = minf(order.engagement_range, 300.0)
			var center_angle: float = order.sector_direction.angle()
			var points: PackedVector2Array = [Vector2.ZERO]
			var steps: int = 16
			for i in range(steps + 1):
				var a: float = center_angle - arc_angle + (arc_angle * 2.0 * float(i) / float(steps))
				points.append(Vector2(cos(a), sin(a)) * arc_range)
			points.append(Vector2.ZERO)
			draw_colored_polygon(points, Color(0.2, 0.8, 0.3, 0.04))
			draw_polyline(points, Color(0.3, 0.9, 0.4, 0.5), 1.5)
		else:
			var d := order.sector_direction.normalized()
			var p2 = d * 20.0
			var p1 = p2 - d.rotated(0.5) * 8.0
			var p3 = p2 - d.rotated(-0.5) * 8.0
			draw_line(Vector2.ZERO, p2, Color(0.3, 0.9, 0.4, 0.5), 1.5)
			draw_line(p2, p1, Color(0.3, 0.9, 0.4, 0.5), 1.5)
			draw_line(p2, p3, Color(0.3, 0.9, 0.4, 0.5), 1.5)
		
	# 2. Selection Ring
	if is_selected:
		draw_circle(Vector2.ZERO, 19.0, Color(0.2, 1.0, 0.4, 0.2))
		draw_arc(Vector2.ZERO, 19.0, 0, TAU, 32, Color(0.3, 1.0, 0.4, 0.9), 2.0)
		
	# 3. Main Token Body
	var body_color := Color(0.18, 0.52, 0.88) if team == Team.DEFENDER else Color(0.85, 0.22, 0.22)
	var outline_color := Color(0.4, 0.8, 1.0) if team == Team.DEFENDER else Color(1.0, 0.5, 0.4)
	
	if current_state == State.PINNED:
		body_color = body_color.darkened(0.5) # Cowering dark tone
		
	draw_circle(Vector2.ZERO, 14.0, body_color)
	draw_arc(Vector2.ZERO, 14.0, 0, TAU, 24, outline_color, 1.5)
	
	# 4. Facing indicator nose
	var nose := facing_direction.normalized() * 18.0
	draw_line(Vector2.ZERO, nose, Color.WHITE, 2.0)
	
	# 5. Role Label
	draw_string(font, Vector2(-10, 4), role_label, HORIZONTAL_ALIGNMENT_CENTER, 20, 10, Color.WHITE)
	
	# 6. Status Overlays: HP bar & Suppression bar
	var bar_w := 24.0
	var bar_h := 3.0
	var hp_y := -18.0
	
	# HP background & fill
	draw_rect(Rect2(-bar_w * 0.5, hp_y, bar_w, bar_h), Color(0.2, 0.2, 0.2, 0.8))
	var hp_pct := clampf(hp / max_hp, 0.0, 1.0)
	var hp_col := Color(0.2, 0.9, 0.3) if hp_pct > 0.5 else (Color.YELLOW if hp_pct > 0.25 else Color.RED)
	draw_rect(Rect2(-bar_w * 0.5, hp_y, bar_w * hp_pct, bar_h), hp_col)
	
	# Suppression bar (appears if suppressed)
	if suppression > 5.0:
		var sup_y := -23.0
		var sup_pct := clampf(suppression / GameConstants.SUPPRESSION_MAX, 0.0, 1.0)
		draw_rect(Rect2(-bar_w * 0.5, sup_y, bar_w, bar_h), Color(0.2, 0.2, 0.2, 0.8))
		var sup_col := Color(1.0, 0.3, 0.1) if sup_pct > 0.7 else Color(1.0, 0.8, 0.1)
		draw_rect(Rect2(-bar_w * 0.5, sup_y, bar_w * sup_pct, bar_h), sup_col)
		
	if current_state == State.PINNED:
		draw_string(font, Vector2(-18, -28), "PINNED!", HORIZONTAL_ALIGNMENT_CENTER, 36, 9, Color(1.0, 0.2, 0.2))
		
	# 7. Bullet Tracer
	if tracer_alpha > 0.0:
		var local_tracer := to_local(tracer_end)
		var tracer_dir := local_tracer.normalized()
		var tracer_len := minf(local_tracer.length(), 60.0)
		draw_line(Vector2.ZERO, tracer_dir * tracer_len, Color(1.0, 0.9, 0.4, tracer_alpha), 1.5)
		draw_circle(Vector2.ZERO, 5.0, Color(1.0, 1.0, 0.7, tracer_alpha))
