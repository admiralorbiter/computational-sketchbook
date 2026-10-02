class_name Objectives
extends RefCounted
## Manages and checks victory/defeat conditions for a scenario.

enum Result {
	ONGOING,
	WIN,
	LOSE
}

var elapsed_time: float = 0.0
var relay_hp: float = 200.0
var relay_position: Vector2 = Vector2.ZERO

## Checks the current game state against scenario victory conditions.
## Returns a Dictionary with "result": Result, and "reason": String.
func check_victory(scenario: Scenario, game_state: Dictionary) -> Dictionary:
	# Update internal tracking
	elapsed_time = game_state.get("elapsed_time", elapsed_time)
	relay_hp = game_state.get("relay_hp", relay_hp)
	var defender_count: int = game_state.get("defender_count", 0)
	var attacker_count: int = game_state.get("attacker_count", 0)
	
	# Defeat condition 1: Relay destroyed
	if relay_hp <= 0:
		return {"result": Result.LOSE, "reason": "Relay Destroyed"}
		
	# Defeat condition 2: All defenders dead
	if defender_count <= 0:
		return {"result": Result.LOSE, "reason": "All Defenders Eliminated"}
	
	# Victory conditions
	match scenario.victory_condition:
		Scenario.VictoryCondition.SURVIVE_TIME:
			if elapsed_time >= scenario.victory_time:
				return {"result": Result.WIN, "reason": "Time Survived"}
				
		Scenario.VictoryCondition.ELIMINATE_ALL:
			var all_waves_spawned: bool = game_state.get("all_waves_spawned", false)
			if all_waves_spawned and attacker_count <= 0:
				return {"result": Result.WIN, "reason": "All Enemies Eliminated"}
	
	return {"result": Result.ONGOING, "reason": ""}
