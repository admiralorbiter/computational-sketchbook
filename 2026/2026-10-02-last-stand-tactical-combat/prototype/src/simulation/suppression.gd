class_name Suppression extends RefCounted
## Suppression System Utility
## Evaluates suppression levels and their impact on unit performance.

enum SuppressionLevel {
	CLEAR,
	LIGHT,
	MEDIUM,
	HEAVY,
	PINNED
}

## Applies suppression to a unit.
static func apply_suppression(unit: Unit, amount: float) -> void:
	unit.take_suppression(amount)

## Decays suppression for a unit over time.
static func decay_suppression(unit: Unit, delta: float) -> void:
	# Handled internally in unit.gd tick, but keeping interface per spec
	if unit.suppression > 0:
		var decay_amount = GameConstants.SUPPRESSION_DECAY * delta
		unit.suppression = maxf(0.0, unit.suppression - decay_amount)
		unit.suppression_changed.emit(unit.suppression)

## Maps a raw suppression value to a SuppressionLevel.
static func get_suppression_level(value: float) -> SuppressionLevel:
	if value < 10.0:
		return SuppressionLevel.CLEAR
	elif value < 30.0:
		return SuppressionLevel.LIGHT
	elif value < 60.0:
		return SuppressionLevel.MEDIUM
	elif value < 90.0:
		return SuppressionLevel.HEAVY
	else:
		return SuppressionLevel.PINNED

## Returns an accuracy multiplier based on suppression.
static func get_suppression_modifier(value: float) -> float:
	var level = get_suppression_level(value)
	match level:
		SuppressionLevel.CLEAR:
			return 1.0
		SuppressionLevel.LIGHT:
			return 0.85
		SuppressionLevel.MEDIUM:
			return 0.60
		SuppressionLevel.HEAVY:
			return 0.30
		SuppressionLevel.PINNED:
			return 0.10
	return 1.0
