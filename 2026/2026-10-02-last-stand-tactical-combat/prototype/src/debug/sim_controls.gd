class_name SimControls
extends Node
## Handles game simulation speed (pause, fast forward, etc.).

var current_speed: float = 1.0
var is_paused: bool = false

func _unhandled_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed:
		return
		
	match event.keycode:
		KEY_SPACE:
			is_paused = !is_paused
			Engine.time_scale = 0.0 if is_paused else current_speed
		KEY_COMMA:
			_set_speed(0.5)
		KEY_PERIOD:
			_set_speed(1.0)
		KEY_SLASH:
			if Input.is_key_pressed(KEY_SHIFT):
				_set_speed(4.0)
			else:
				_set_speed(2.0)

func _set_speed(speed: float) -> void:
	current_speed = speed
	if not is_paused:
		Engine.time_scale = current_speed
	# TODO: Notify HUD to update speed label
