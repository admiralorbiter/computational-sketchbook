# Content and Data Model

## 1. Goal

The game should be as data-driven as practical. Parts, missions, and some balancing constants should live outside the main code path so the game can be tuned quickly.

## 2. Content Categories

Recommended externalized content:

- part definitions
- mission definitions
- rocket presets
- balancing constants
- text strings for mission descriptions and feedback where practical

## 3. Part Schema

Suggested fields:

- `id`
- `display_name`
- `category`
- `dry_mass`
- `fuel_capacity`
- `thrust`
- `isp`
- `drag_coefficient`
- `cost`
- `draw_id`
- `attachment_points`
- `tags`

Potential tags:
- `command`
- `engine`
- `tank`
- `decoupler`
- `recovery`
- `payload`
- `stability`

## 4. Example Part Definition

```ron
// Part definition — use snake_case ids, keep tags minimal in MVP
(
    id: "engine_small_lv1",
    display_name: "LV-1 Sparrow",
    category: Engine,
    dry_mass: 0.5,
    fuel_capacity: 0.0,
    thrust: 45.0,
    isp: 250.0,
    drag_coefficient: 0.4,
    cost: 120,
    draw_id: "engine_small_lv1",
    attachment_points: [Top],
    tags: [Engine],
    cost: 120, // Retained for forward compatibility
)
```

## 5. Rocket Blueprint Model

A rocket blueprint should represent the player’s design in a serializable format.

Suggested contents:

- blueprint id
- part instances
- attachment hierarchy
- stage assignments
- metadata such as display name or creation time

Keep runtime state separate from blueprint data.

## 6. Stage Data

Each stage should contain:

- stage order
- activated engine instance ids
- activated decoupler instance ids
- optional notes or label

## 7. Mission Schema

Suggested mission fields:

- `id`
- `display_name`
- `description`
- `objectives`
- `unlock_requirements`
- `rewards` if used
- `failure_conditions`

Objective examples:
- reach altitude X
- reach speed X
- leave atmosphere
- maintain orbit for N seconds
- land safely
- carry payload mass Y to orbit

## 8. Example Mission Definition

```ron
// Mission definition — objectives and failure conditions use typed enums
(
    id: "reach_space_01",
    display_name: "Cross the Line",
    description: "Get above the atmosphere, even if you can't stay there.",
    objectives: [
        // Karman line equivalent for this planet
        (type: ReachAltitude, value: 70000.0),
    ],
    unlock_requirements: [],
    failure_conditions: [
        (type: DestroyVehicle),
    ],
)
```

## 9. Balancing Constants

Candidates for external tuning:

- gravity strength
- atmosphere height
- density curve constants

> Note: For ease of tooling development in Phase 6, these constants are currently stored in `assets/physics_constants.ron`.
- control authority multiplier
- heat / recovery thresholds if later added

## 10. Save Categories

### 10.1 Settings Save
- audio settings
- graphics toggles if any
- keybindings if implemented

### 10.2 Rocket Design Save
- saved blueprints
- favorite or pinned designs

### 10.3 Progress Save
- unlocked missions
- best mission results
- unlocked parts if used

## 11. Validation Rules

The data layer should validate:

- unique ids
- valid categories
- required numeric fields present
- no negative mass or impossible values unless explicitly allowed
- mission objective types recognized
- attachment references valid

## 12. Naming Conventions

Suggested ids:
- lowercase snake_case
- stable ids even if display names change

Examples:
- `pod_mk1`
- `tank_small_100`
- `engine_small_lv1`
- `mission_orbit_01`

## 13. Content Authoring Guidance

When adding parts:
- add one new tradeoff at a time
- avoid nearly identical parts in MVP
- prefer few distinctive options over many minor variants

When adding missions:
- teach one new skill at a time
- keep text concise
- make success conditions concrete and readable

## 14. Helpful Future Content Docs

Possible later additions:
- part balance spreadsheet or balance notes
- mission pacing matrix
- flavor writing guide
