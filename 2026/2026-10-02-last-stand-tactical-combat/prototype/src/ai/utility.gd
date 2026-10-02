class_name AIUtility extends RefCounted

## how valuable is shooting this target?
static func score_target(unit: Node, target: Node, weapon: Resource) -> Dictionary:
	var score: float = 0.0
	var reasons: Array = []
	
	var dist: float = unit.global_position.distance_to(target.global_position)
	# Assuming weapon has max_range
	var max_range: float = weapon.max_range if weapon and "max_range" in weapon else 500.0
	
	if dist > max_range:
		return {"score": 0.0, "reason": "Out of range"}
	
	# Distance factor: closer is better
	var dist_score: float = (1.0 - (dist / max_range)) * 50.0
	score += dist_score
	reasons.append("Distance (+%f)" % dist_score)
	
	# Threat level (assuming target has threat property)
	var threat: float = target.threat_level if "threat_level" in target else 1.0
	var threat_score: float = threat * 20.0
	score += threat_score
	reasons.append("Threat (+%f)" % threat_score)
	
	# Cover (assuming target has cover property, 0 to 1)
	var cover: float = target.cover_factor if "cover_factor" in target else 0.0
	var cover_penalty: float = cover * -30.0
	score += cover_penalty
	reasons.append("Target Cover (%f)" % cover_penalty)
	
	return {"score": max(0.0, score), "reason": ", ".join(reasons)}

## how good is this cover position?
static func score_cover(unit: Node, cover_position: Vector2, sector_dir: Vector2 = Vector2.ZERO) -> Dictionary:
	var score: float = 100.0
	var reasons: Array = []
	
	var dist: float = unit.global_position.distance_to(cover_position)
	var dist_penalty: float = dist * -0.1
	score += dist_penalty
	reasons.append("Distance Penalty (%f)" % dist_penalty)
	
	return {"score": score, "reason": ", ".join(reasons)}

## how urgent is retreating?
static func score_retreat(unit: Node) -> Dictionary:
	var score: float = 0.0
	var reasons: Array = []
	
	var hp_pct: float = unit.get_health_percent() if unit.has_method("get_health_percent") else 1.0
	if hp_pct < 0.3:
		var hp_score: float = (0.3 - hp_pct) * 300.0
		score += hp_score
		reasons.append("Low HP (+%f)" % hp_score)
		
	return {"score": score, "reason": ", ".join(reasons)}
