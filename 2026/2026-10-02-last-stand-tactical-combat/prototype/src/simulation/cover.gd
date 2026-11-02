class_name Cover extends RefCounted
## Cover System Utility
## Defines cover types and their modifiers for combat resolution.

enum CoverType {
	NONE,
	SOFT,
	SANDBAG,
	HARD,
	FULL
}

## Returns the accuracy modifier for the shooter (how hard it is to hit the target).
static func get_accuracy_modifier(type: CoverType) -> float:
	match type:
		CoverType.NONE:
			return 1.0
		CoverType.SOFT:
			return 1.0 - GameConstants.COVER_SOFT
		CoverType.SANDBAG:
			return 1.0 - GameConstants.COVER_SANDBAG
		CoverType.HARD:
			return 1.0 - GameConstants.COVER_HARD
		CoverType.FULL:
			return 1.0 - GameConstants.COVER_FULL
	return 1.0

## Returns the damage reduction multiplier for the target.
static func get_damage_reduction(type: CoverType) -> float:
	# Assume damage reduction is equivalent to the cover value for now.
	match type:
		CoverType.NONE:
			return 0.0
		CoverType.SOFT:
			return GameConstants.COVER_SOFT
		CoverType.SANDBAG:
			return GameConstants.COVER_SANDBAG
		CoverType.HARD:
			return GameConstants.COVER_HARD
		CoverType.FULL:
			return GameConstants.COVER_FULL
	return 0.0

## Returns a generic survivability multiplier if needed by AI.
static func get_survivability_multiplier(type: CoverType) -> float:
	var acc_mod = get_accuracy_modifier(type)
	var dmg_red = get_damage_reduction(type)
	# Simplistic combination: You get hit less, and take less damage.
	# A lower acc_mod is better, a higher dmg_red is better.
	return (1.0 / acc_mod) * (1.0 + dmg_red)
