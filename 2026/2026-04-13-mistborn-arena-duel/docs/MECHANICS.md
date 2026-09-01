# Mechanics

## Movement

### Ground Move
Responsive horizontal movement with capped speed and clear acceleration/deceleration.

### Jump
Single jump with optional jump buffer and coyote time depending on feel testing.

### Air Control
Reduced but meaningful steering.

### Dash
Short burst for spacing or escape. Should be strong enough to matter but committed enough to punish.

## Combat

### Light Attack
Fast, lower commitment, lower damage.

### Heavy Attack
Slower, stronger, better pressure, possibly better guard impact.

### Specials
Character-defining abilities. Resource-gated.

### Block
Frontal defense option. May reduce or negate damage. Vulnerable to pressure or specific counters.

## State Logic
Recommended minimum states:
- idle
- run
- jump
- fall
- dash
- attack
- block
- hitstun
- KO

## Resource
Internally unified energy-like meter with character-specific presentation.

### Rules
- max value fixed
- special moves spend resource
- regeneration may differ by character
- no overly complex sub-resources in MVP

## Combat Rules
- keep combos short
- prioritize knockback and spacing over long strings
- special moves should rarely create infinite pressure
- avoid excessive stun duration

## Collision Model
- stage collision uses Arcade Physics
- combat collision uses explicit hitboxes/hurtboxes
