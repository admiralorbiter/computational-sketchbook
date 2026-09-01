# Testing Strategy

## Testing Priorities
1. movement feel
2. combat correctness
3. state transition stability
4. round reset stability
5. reproducibility of bugs

## Manual Test Cases

### Movement
- both players can move simultaneously
- jump works repeatedly without sticky input
- dash behaves consistently

### Combat
- light/heavy attacks hit only during active windows
- block prevents valid hits when facing correctly
- attacks cannot be triggered during forbidden states

### Match
- KO ends round
- round resets all key state
- rematch works without stale projectiles or state timers

## Debug Requirements
- hitbox/hurtbox toggles
- state text
- frame/input logs
- quick reset

## Later Automated Targets
- move schema validation
- state machine transition tests
- pure utility/math function tests
