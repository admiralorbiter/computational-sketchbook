class_name DeployableNode
extends Node2D
## Visual instance of a placed defensive structure or hazard.

var deployable: Deployable
var hp: float = 100.0
var max_hp: float = 100.0

func setup(data: Deployable) -> void:
	deployable = data
	hp = data.hp
	max_hp = data.hp
	queue_redraw()

func _draw() -> void:
	if not deployable:
		return
	var sz := float(GameConstants.TILE_SIZE)
	var half_sz := sz * 0.5
	var rect := Rect2(-half_sz, -half_sz, sz, sz)
	
	match deployable.deployable_name.to_lower():
		"wall", "wall segment":
			# Heavy reinforced wall
			draw_rect(rect, Color(0.35, 0.35, 0.40))
			draw_rect(rect, Color(0.55, 0.55, 0.60), false, 2.0)
			# Cross rivets
			draw_line(rect.position, rect.end, Color(0.25, 0.25, 0.30), 1.0)
		"sandbag":
			# Khaki sandbag barricade
			draw_rect(rect.grow(-4), Color(0.72, 0.60, 0.38))
			draw_rect(rect.grow(-4), Color(0.85, 0.75, 0.50), false, 1.5)
			draw_line(Vector2(-half_sz + 4, 0), Vector2(half_sz - 4, 0), Color(0.55, 0.45, 0.25), 2.0)
		"barbed wire", "wire":
			# Razor/Barbed wire coils
			draw_rect(rect.grow(-6), Color(0.4, 0.4, 0.4, 0.4))
			draw_line(Vector2(-half_sz, -half_sz), Vector2(half_sz, half_sz), Color(0.8, 0.8, 0.85), 1.5)
			draw_line(Vector2(-half_sz, half_sz), Vector2(half_sz, -half_sz), Color(0.8, 0.8, 0.85), 1.5)
			draw_arc(Vector2.ZERO, 10.0, 0, TAU, 12, Color(0.7, 0.7, 0.8), 1.5)
		"land mine", "mine":
			# Concealed ground charge
			draw_circle(Vector2.ZERO, 7.0, Color(0.25, 0.35, 0.22))
			draw_circle(Vector2.ZERO, 3.0, Color(0.9, 0.2, 0.2))
		"ammo box":
			# Green supply cache
			draw_rect(rect.grow(-4), Color(0.2, 0.4, 0.25))
			draw_rect(rect.grow(-4), Color(0.4, 0.7, 0.4), false, 1.5)
			# Yellow stencil cross
			draw_line(Vector2(-4, 0), Vector2(4, 0), Color.YELLOW, 2.0)
			draw_line(Vector2(0, -4), Vector2(0, 4), Color.YELLOW, 2.0)
		_:
			draw_rect(rect, Color(0.5, 0.5, 0.5))
			
	# Damage bar if below max HP
	if hp < max_hp and hp > 0.0:
		var pct := hp / max_hp
		draw_rect(Rect2(-half_sz, -half_sz - 4, sz * pct, 3), Color.ORANGE)

func take_damage(amount: float) -> void:
	hp -= amount
	queue_redraw()
	if hp <= 0.0:
		queue_free()
