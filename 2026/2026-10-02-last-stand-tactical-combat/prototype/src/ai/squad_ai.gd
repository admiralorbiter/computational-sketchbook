class_name SquadAI extends Node

enum SquadState { ADVANCING, ENGAGED, PINNED, RETREATING, ROUTED }

@export var units: Array = []
@export var squad_leader: Node

var squad_morale: float = 100.0
var current_state: SquadState = SquadState.ADVANCING

signal support_requested(squad: SquadAI)

func update_morale(delta: float) -> void:
	# Morale regenerates slowly over time
	squad_morale = clamp(squad_morale + delta * 2.0, 0.0, 100.0)
	
	if squad_morale < 20.0:
		current_state = SquadState.ROUTED
	elif squad_morale < 50.0:
		current_state = SquadState.RETREATING

func get_squad_state() -> SquadState:
	return current_state
	
func coordinate_advance() -> Vector2:
	# Pick next cover position for squad (stubbed)
	if is_instance_valid(squad_leader):
		return squad_leader.global_position + Vector2(100, 0)
	return Vector2.ZERO

func request_support() -> void:
	support_requested.emit(self)
