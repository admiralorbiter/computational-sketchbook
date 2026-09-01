# System — Infection Overlay

## Summary
Infection is a spreading field that disrupts systems and spawns nodes that intensify spread.

## Representation
Recommended for MVP:
- Grid-based scalar field (float 0..1 per cell)
Alternative:
- Voronoi/mesh field (more complex)

## Spread rule (simple)
Each tick:
- infection[x,y] += source_rate
- diffuse a fraction to neighbors
- clamp 0..1
- if above threshold, can spawn a node (rare) or apply stronger debuffs

## Debuffs by intensity
0.0–0.3: minor slow to vesicles
0.3–0.6: chance to add signal noise / small cooldown penalty
0.6–1.0: chance to disable nodes temporarily; severe shipping slowdown

## Infection nodes
- Spawned by certain enemies or by high-intensity field.
- Nodes act as strong local sources until cleansed.

## Cleansing
- Mobile cleaner unit reduces field in radius over time.
- Cleanse effector reduces field instantly + damages nodes.

## Performance notes
- Update infection at fixed interval (e.g., 5–10 Hz), not every frame.
- Consider dirty-rect updates near active sources.

## Definition of Done
- [ ] Infection grows from at least 2 source types.
- [ ] Cleansing visibly reduces infection.
- [ ] Infection meaningfully impacts shipping or circuits.
- [ ] Infection nodes exist and can be targeted/removed.
