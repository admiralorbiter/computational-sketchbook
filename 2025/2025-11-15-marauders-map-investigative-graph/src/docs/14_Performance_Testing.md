# 14 — Performance & Testing Plan

## Budgets
- Search p95 < 200 ms; pathfinding (≤1K nodes) < 1.5 s; graph settle (≤500 nodes) < 1 s; 60 fps interactions at threshold.

## Test datasets
- **Small**: ~200 entities, 300 relationships.
- **Medium**: ~1K entities, 2K relationships.
- **Large**: ~3K entities, 10K relationships (progressive expansion emphasis).

## Scenarios
- Live search typing under load; bound‑aware search on the map.
- Switch Map↔Graph on medium/large sets; stress Canvas and label LOD.
- Enrichment cache hit vs miss; merge conflicts after imports.
- Backup/restore cycle on medium dataset.

## Quality gates
- Automated run of performance scenarios on each release candidate.
- A11y checklist pass for key flows (search, add entity, add relationship, pathfinding).
