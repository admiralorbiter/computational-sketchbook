class_name Scenario
extends Resource
## Defines the parameters and configuration for a single combat scenario.

enum VictoryCondition {
	SURVIVE_TIME,
	ELIMINATE_ALL
}

@export var scenario_name: String = "Unknown Scenario"
@export_multiline var description: String = "No description provided."
@export_multiline var objective_text: String = "Survive."

@export var map_size: Vector2i = Vector2i(60, 40)
@export var defender_spawn_positions: Array[Vector2] = []

## Array of Dictionaries defining loadout: {"type": String, "weapon": String}
@export var defender_loadouts: Array[Dictionary] = []

## Array of wave definitions: {"time": float, "units": Array[Dictionary]}
## Unit Dictionary: {"type": String, "count": int, "spawn_edge": String, "squad_id": int}
@export var attacker_waves: Array[Dictionary] = []

@export var victory_condition: VictoryCondition = VictoryCondition.SURVIVE_TIME
@export var victory_time: float = 300.0 ## In seconds

@export var build_budget: int = 1000
@export var available_deployables: Array[Resource] = []

@export var permutation_seed: int = 0
