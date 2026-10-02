class_name CommanderAI extends Node

var active_squads: Array = []
var reserves: Array = []
var dangerous_zones: Array = []

var time_since_last_evaluation: float = 0.0
const EVALUATION_INTERVAL: float = 5.0

func _process(delta: float) -> void:
	time_since_last_evaluation += delta
	if time_since_last_evaluation >= EVALUATION_INTERVAL:
		evaluate_battlefield()
		assign_squads_to_objectives()
		commit_reserves()
		time_since_last_evaluation = 0.0

func evaluate_battlefield() -> void:
	# Assess which sectors are weakly defended (stubbed)
	pass

func assign_squads_to_objectives() -> void:
	# Distribute squads to attack lanes (stubbed)
	pass

func commit_reserves() -> void:
	if not reserves.is_empty():
		# Logic to decide when to commit
		var squad: SquadAI = reserves.pop_front()
		active_squads.append(squad)

func react_to_losses(zone_center: Vector2) -> void:
	# Mark zones as dangerous, redirect squads
	dangerous_zones.append(zone_center)
	for squad in active_squads:
		if is_instance_valid(squad) and squad.get_squad_state() == SquadAI.SquadState.ADVANCING:
			# Redirect away from dangerous_zone
			pass
