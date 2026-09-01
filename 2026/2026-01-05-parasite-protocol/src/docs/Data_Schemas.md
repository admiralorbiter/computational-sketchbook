# Data_Schemas — Suggested Data-Driven Definitions

Use this as a reference for JSON/YAML/ScriptableObject fields. Keep it versioned.

## Enemy schema (example)
```json
{
  "id": "virus_swarm_01",
  "name": "Virion Swarm",
  "family": "virus",
  "tags": ["swarm", "fast"],
  "stats": { "hp": 12, "speed": 2.8, "armor": 0 },
  "resistances": { "ros": 0.0, "slow": 0.0, "tag": 0.0 },
  "abilities": [
    { "type": "on_reach_organelle", "effect": "hijack_ribosome_slot", "value": 1, "duration": 6.0 }
  ],
  "infection": { "rate": 0.1, "radius": 1.5, "node_on_death": false },
  "breach": { "preferred_targets": ["weak_membrane"], "bind_time": 0.6 },
  "adaptation_flags": ["anti_aoe", "stealth", "tunnel"]
}
```

## Module schema (shared)
Common fields:
- id, name, category: receptor|relay|effector|track|mobile
- costs: ATP + blocks
- timings: build_time (ribosome), assembly_time (ER/Golgi), cooldown (runtime)
- placement: membrane_only, interior_only, near_organelle, min_distance, max_distance
- runtime: radius, max_connections (for relays), power_cost_per_trigger
- vulnerabilities: disruption_chance, infection_sensitivity

### Receptor fields
- event_type: enemy_enter|enemy_type_seen|membrane_damaged|infection_grew|timer_pulse|atp_low
- filters: family, tags, size, boss_only
- threshold: e.g., count>=N within radius

### Relay fields
- behavior: amplify|split|gate|delay|convert
- params: multipliers, branch_count, cooldown_override, delay_seconds
- connection rules: max_in, max_out

### Effector fields
- effect_type: damage|slow|knockback|tag|execute|cleanse|repair
- payload: damage, aoe, duration, stacks, proc_chance
- side_effects: stress_gain, self_damage, atp_spike

## Gene card schema
```json
{
  "id": "gene_autophagy_up",
  "name": "Upregulate Autophagy",
  "rarity": "common",
  "short": "Cleanse is stronger, throughput slows.",
  "effects": [
    { "type": "cleanse_power_mult", "value": 1.25 },
    { "type": "manufacture_speed_mult", "value": 0.9 }
  ],
  "exclusions": ["gene_hyper_ribosomes"]
}
```

## Schema versioning
- Add `schema_version` at the root of each file.
- Validate at load; fail fast with readable errors.
