# System — Arena / Map (Cell Structure, Organelles, Breaches, Navigation)

Date: 2026-01-05

This doc describes the arena representation and gameplay rules for the cell map.

---

## 1) Coordinate system & scale
- World units: arbitrary (e.g., 1.0 = 1 tile width)
- The cell is a **circular arena**:
  - `cell_radius` (75 world units - increased from 50 for better gameplay space)
- Membrane ring thickness is visual; collision boundary is the ring edge.
- Organelles scale proportionally with cell radius to maintain relative sizes.

---

## 2) Cell structure layout (2D cross-section)
Core elements:
- **Membrane ring:** boundary; breaches appear on ring segments.
- **Cytoplasm:** default traversable region.
- **Organelles:** circular/oval obstacles + functional zones:
  - Nucleus (objective)
  - ER/Golgi (manufacturing origin)
  - Mitochondria (ATP zones)

Optional later:
- Lysosome “spawner” organelle for mobile cleaners
- Vacuole / ribosome clusters

---

## 3) Organelle placement rules
### Fixed layouts (recommended for MVP)
- Create 5–10 handcrafted layouts for readability and balance.
- Each layout defines:
  - positions/sizes of organelles
  - weakspot segments
  - starting breach points (optional)

### Seeded variation (optional)
Within a layout, allow small jitter:
- nucleus position fixed or near center (±2 units)
- mitochondria in allowed annulus band (e.g., radius 20–35)
- ER/Golgi placed away from nucleus (min distance 10)

### Constraints
- Organelles must not overlap.
- Nucleus must not be too close to membrane (min distance 15).
- ER/Golgi must have at least one clear shipping corridor.

---

## 4) Membrane breach mechanics
### Membrane segmentation
- Divide circumference into N segments (e.g., 24 or 32).
- Each segment has HP and weakspot modifiers (see Economy doc).

### Breach lifecycle
1. **Threat pressure** targets a segment (from wave + enemy behaviors).
2. **Breach attempt** (probabilistic rate) creates a **Breach Opening** if successful.
3. Breach opening lasts `open_duration` (e.g., 6–12 sec) and spawns enemies.
4. Opening closes; segment HP remains reduced until repaired.

### Breach interactions
- Some modules can “seal” or “stabilize” segments temporarily.
- Infection at the membrane edge can increase breach attempt rates.

---

## 5) Collision and navigation representation
### Collision
- Organelles: simple circles/ovals for physics + avoidance
- Membrane: circle boundary
- Modules: do not block enemies by default (unless you add “barrier” modules)

### Navigation grid (for flow field)
- Use a grid sized to your needs (128×128 recommended start).
- Mark blocked cells from organelle shapes.
- Precompute a distance/flow field toward targets.

### Updates
- If organelles are static, you can compute once per run.
- If breaches add “targets,” only recompute vector field to reflect new targets as needed.

---

## 6) Map generation vs fixed layouts
**MVP:** fixed layouts with seeded minor variation.
**Later:** procedural generation with constraints is possible, but ensure readability.

Procedural approach outline:
- Place nucleus at center band
- Place ER/Golgi in mid-radius band
- Place mitochondria with non-overlap packing
- Assign weakspots based on nearest organelle distances
- Validate navigability (no sealed compartments)

---

## Definition of Done
- [ ] Arena loads from a layout definition (data-driven).
- [x] Organelles rendered (nucleus, ER/Golgi, mitochondria) with proper z-ordering.
- [ ] Organelles block movement and affect zones (ATP, factory origin) - visual only currently.
- [ ] Membrane segments exist and can spawn breach openings.
- [ ] Navigation grid/flow field works for enemy movement.
- [ ] At least 3 layouts feel distinct and fair.
