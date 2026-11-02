class_name BuildGhost
extends Node2D
## Shows a placement preview for deployables during the preparation phase.

var current_deployable: Deployable = null
var valid_placement: bool = false
var grid_size: int = 32

var valid_color: Color = Color(0.2, 0.8, 0.2, 0.5)
var invalid_color: Color = Color(0.8, 0.2, 0.2, 0.5)

func _process(_delta: float) -> void:
	if current_deployable:
		global_position = get_global_mouse_position().snapped(Vector2(grid_size, grid_size))
		queue_redraw()

func _draw() -> void:
	if not current_deployable:
		return
		
	var draw_color: Color = valid_color if valid_placement else invalid_color
	# If the deployable defines a specific ghost color, blend it or use it as base
	if current_deployable.ghost_color != Color.TRANSPARENT:
		draw_color = current_deployable.ghost_color
		draw_color.a = 0.5
		if not valid_placement:
			draw_color = invalid_color
			
	var rect := Rect2(-grid_size/2.0, -grid_size/2.0, grid_size, grid_size)
	draw_rect(rect, draw_color)
	draw_rect(rect, Color.WHITE, false) # Border

## Sets the deployable to preview. Pass null to hide.
func set_deployable(deployable: Deployable) -> void:
	current_deployable = deployable
	visible = (deployable != null)
	queue_redraw()

## Updates the visual state based on whether placement is valid.
func set_valid(is_valid: bool) -> void:
	valid_placement = is_valid
	queue_redraw()
