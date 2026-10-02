class_name CombatResolver extends RefCounted
## Combat Resolver Utility
## Handles hit calculations, damage, and suppression for a single shot.

class ShotResult:
	var hit: bool = false
	var near_miss: bool = false
	var damage: float = 0.0
	var suppression: float = 0.0
	
	func _init(_hit: bool = false, _near_miss: bool = false, _damage: float = 0.0, _suppression: float = 0.0):
		self.hit = _hit
		self.near_miss = _near_miss
		self.damage = _damage
		self.suppression = _suppression

## Resolves a single shot between two units.
static func resolve_shot(attacker: Unit, target: Unit, weapon: WeaponData, cover_type: Cover.CoverType = Cover.CoverType.NONE) -> ShotResult:
	var dist := attacker.global_position.distance_to(target.global_position)
	var range_mod := weapon.get_range_modifier(dist)
	
	if range_mod <= 0.0:
		return ShotResult.new(false, false, 0.0, 0.0) # Out of range
		
	var acc_mod_cover := Cover.get_accuracy_modifier(cover_type)
	var sup_mod := Suppression.get_suppression_modifier(attacker.suppression)
	
	# Movement penalty (simplified)
	var movement_mod := 1.0
	if attacker.current_state == Unit.State.MOVING:
		movement_mod = weapon.moving_accuracy / weapon.base_accuracy
		
	# Final hit probability
	var hit_chance := weapon.base_accuracy * acc_mod_cover * sup_mod * range_mod * movement_mod
	var roll := randf()
	
	if roll <= hit_chance:
		# Hit!
		var dmg_reduction := Cover.get_damage_reduction(cover_type)
		var final_damage := weapon.damage * (1.0 - dmg_reduction)
		return ShotResult.new(true, false, final_damage, weapon.suppression_per_round)
	elif roll <= hit_chance + 0.30:
		# Near miss (flat 30% window beyond hit chance — ensures MG generates suppression reliably)
		return ShotResult.new(false, true, 0.0, weapon.suppression_per_round * GameConstants.NEAR_MISS_SUPPRESSION)
	else:
		# Wide miss
		# Wide misses might still apply fractional suppression, but for now 0.
		return ShotResult.new(false, false, 0.0, 0.0)
