# System — Enemy Adaptation (Selection Pressure)

## Summary
After each wave, choose 1–2 adaptation traits based on the player's recent strategy usage.

## Inputs
Track per wave:
- damage_by_type (ros, lysosome, execute, etc.)
- cc_by_type (slow, snare, knockback)
- percent_kills_by_system
- avg_time_to_kill
- infection_usage (how often player cleanses)

## Strategy features (examples)
- AoE reliance
- Execute reliance
- Slow reliance
- Tag/mark reliance
- High throughput (many modules installed per wave)

## Adaptation traits (examples)
- Antioxidant Shell: reduces ROS damage
- Stealth Coat: ignored by basic receptors unless scanner present
- Tunneling: bypasses actin nets
- Decoy Proteins: wastes execute/tag
- Biofilm: increases armor, slower

## Selection algorithm (simple)
- Compute weights = f(strategy_features)
- Randomly pick 1–2 traits with cooldowns (don’t repeat too often)
- Apply to a subset of enemies next wave (not all)

## UI requirements
- End-of-wave banner: “Pathogens adapted: Antioxidant Shell”
- Hover explanation: what it does + suggested counters

## Definition of Done
- [ ] The system selects traits based on measurable player behavior.
- [ ] Trait application is visible (icons on enemies).
- [ ] Player gets clear messaging and counter hints.
