extends Node
## Simulation Manager Autoload
## Handles the fixed-tick accumulator and game state for the simulation layer.

enum GameState {
	BRIEFING,
	PREPARATION,
	ORDERS,
	BATTLE,
	AFTER_ACTION
}

signal tick_processed(tick: int)
signal phase_changed(new_phase: GameState)
signal battle_started()
signal battle_ended()

var current_state: GameState = GameState.BRIEFING
var is_paused: bool = false
var speed_multiplier: float = 1.0
var current_tick: int = 0

var _accumulator: float = 0.0

func _process(delta: float) -> void:
	if is_paused or current_state != GameState.BATTLE:
		return
		
	_accumulator += delta * speed_multiplier
	
	while _accumulator >= GameConstants.TICK_DELTA:
		_process_tick(GameConstants.TICK_DELTA)
		_accumulator -= GameConstants.TICK_DELTA

func _process_tick(delta_tick: float) -> void:
	current_tick += 1
	# In a full implementation, we would call sim_tick on all simulation objects here.
	tick_processed.emit(current_tick)

func set_speed(multiplier: float) -> void:
	speed_multiplier = clampf(multiplier, 0.0, 10.0)

func pause() -> void:
	is_paused = true

func resume() -> void:
	is_paused = false

func change_state(new_state: GameState) -> void:
	if current_state == new_state:
		return
	
	current_state = new_state
	phase_changed.emit(current_state)
	
	if current_state == GameState.BATTLE:
		battle_started.emit()
	elif new_state == GameState.AFTER_ACTION:
		battle_ended.emit()
