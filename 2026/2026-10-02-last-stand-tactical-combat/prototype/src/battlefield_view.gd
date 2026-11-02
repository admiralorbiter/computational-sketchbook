class_name BattlefieldView
extends Node2D
## Renders the tactical map: grid, compound walls, east field, and Central Relay objective.

@export var map_size_tiles: Vector2i = Vector2i(60, 40)
@export var tile_size: int = 32

var relay_tile: Vector2i = Vector2i(18, 20)
var relay_hp: float = 200.0
var relay_max_hp: float = 200.0
var relay_position: Vector2

var show_threat_arrows: bool = true

func _ready() -> void:
	relay_position = Vector2(relay_tile * tile_size) + Vector2(tile_size, tile_size) * 0.5
	z_index = -10

func _draw() -> void:
	var total_w := map_size_tiles.x * tile_size
	var total_h := map_size_tiles.y * tile_size
	
	# 1. Base Ground (East Field: dark earthy terrain)
	draw_rect(Rect2(0, 0, total_w, total_h), Color(0.12, 0.14, 0.12))
	
	# 2. Compound Floor (Tiles 5..26 x, 8..32 y - reinforced concrete)
	var compound_rect := Rect2(5 * tile_size, 8 * tile_size, 22 * tile_size, 24 * tile_size)
	draw_rect(compound_rect, Color(0.18, 0.20, 0.22))
	
	# Courtyard outline
	draw_rect(compound_rect, Color(0.25, 0.28, 0.32), false, 2.0)
	
	# 3. Defensive Perimeter Line (East boundary of compound)
	var fence_x := 27 * tile_size
	draw_line(Vector2(fence_x, 8 * tile_size), Vector2(fence_x, 32 * tile_size), Color(0.6, 0.5, 0.2, 0.8), 3.0)
	
	# 4. Tactical Grid (Subtle)
	var grid_color := Color(0.2, 0.25, 0.22, 0.15)
	for x in range(0, total_w + 1, tile_size):
		draw_line(Vector2(x, 0), Vector2(x, total_h), grid_color, 1.0)
	for y in range(0, total_h + 1, tile_size):
		draw_line(Vector2(0, y), Vector2(total_w, y), grid_color, 1.0)
		
	# 5. Sector Zone Labels
	var font = ThemeDB.fallback_font
	draw_string(font, Vector2(10 * tile_size, 10 * tile_size), "SECURE DEFENSIVE PERIMETER", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.4, 0.6, 0.8, 0.5))
	draw_string(font, Vector2(32 * tile_size, 10 * tile_size), "HOSTILE SECTOR: EAST FIELD", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.8, 0.3, 0.3, 0.5))
	draw_string(font, Vector2(fence_x + 8, 20 * tile_size), "--> PERIMETER BARRIER LINE <--", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(0.7, 0.6, 0.2, 0.7))
	
	if show_threat_arrows:
		var fortify_rect = Rect2(fence_x - 3 * tile_size, 10 * tile_size, 3 * tile_size, 20 * tile_size)
		draw_rect(fortify_rect, Color(0.2, 0.8, 0.3, 0.1))
		draw_dashed_line(Vector2(fortify_rect.position.x, fortify_rect.position.y), Vector2(fortify_rect.end.x, fortify_rect.position.y), Color(0.3, 0.9, 0.4, 0.6), 2.0, 8.0)
		draw_dashed_line(Vector2(fortify_rect.position.x, fortify_rect.end.y), Vector2(fortify_rect.end.x, fortify_rect.end.y), Color(0.3, 0.9, 0.4, 0.6), 2.0, 8.0)
		draw_dashed_line(Vector2(fortify_rect.position.x, fortify_rect.position.y), Vector2(fortify_rect.position.x, fortify_rect.end.y), Color(0.3, 0.9, 0.4, 0.6), 2.0, 8.0)
		draw_string(font, Vector2(fence_x - 2.8 * tile_size, 20 * tile_size), "FORTIFY HERE", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.3, 0.9, 0.4, 0.7))
		
		# Threat Approach Arrows
		var pulse := (sin(Time.get_ticks_msec() * 0.005) + 1.0) * 0.5
		var arrow_color = Color(0.9, 0.2, 0.2, 0.6 + pulse * 0.4)
		var arrow_xs = 40 * tile_size
		for approach_y in [14 * tile_size, 20 * tile_size, 26 * tile_size]:
			var pts = PackedVector2Array([
				Vector2(arrow_xs, approach_y - 24),
				Vector2(arrow_xs - 48, approach_y),
				Vector2(arrow_xs, approach_y + 24),
				Vector2(arrow_xs - 16, approach_y)
			])
			draw_colored_polygon(pts, arrow_color)
	
	# 6. Central Relay Station Objective
	_draw_relay()

func _draw_relay() -> void:
	var font = ThemeDB.fallback_font
	var pulse := (sin(Time.get_ticks_msec() * 0.004) + 1.0) * 0.5
	var outer_color := Color(0.2, 0.6, 0.9, 0.3 + pulse * 0.3)
	
	# Relay base building (2x2 tiles)
	var base_rect := Rect2(relay_tile.x * tile_size - 8, relay_tile.y * tile_size - 8, 48, 48)
	draw_rect(base_rect, Color(0.1, 0.15, 0.25))
	draw_rect(base_rect, Color(0.3, 0.7, 1.0), false, 2.0)
	
	# Hexagon / Core Pulse
	draw_circle(relay_position, 20.0 + pulse * 4.0, outer_color)
	draw_circle(relay_position, 12.0, Color(0.4, 0.8, 1.0))
	draw_circle(relay_position, 6.0, Color.WHITE)
	
	# Relay Label & HP Bar
	var label_pos := relay_position + Vector2(-60, -32)
	draw_string(font, label_pos, "COMM RELAY STATION", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(0.4, 0.8, 1.0))
	
	var bar_rect := Rect2(relay_position.x - 30, relay_position.y + 28, 60, 6)
	draw_rect(bar_rect, Color(0.2, 0.2, 0.2))
	var hp_pct := clampf(relay_hp / relay_max_hp, 0.0, 1.0)
	draw_rect(Rect2(bar_rect.position, Vector2(bar_rect.size.x * hp_pct, bar_rect.size.y)), Color(0.2, 0.8, 0.4))

func take_damage(amount: float) -> void:
	relay_hp = maxf(0.0, relay_hp - amount)
	queue_redraw()
