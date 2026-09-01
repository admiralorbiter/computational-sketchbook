# 08 — Vertical Slices (Playbooks)

Each slice is an end‑to‑end increment that ships UI, storage, API, analytics, and ops hooks. Every slice includes tests, telemetry, and docs updates.

## Slice 1 — Entities CRUD + Live Search
**Objective**: Create/list/detail/delete entities with live search.  
**Scope**: entities, FTS index, search UI, empty/loading/error states, KC quick center control visible but disabled if no map yet.  
**Acceptance**: p95 search < 200 ms at 1K entities; delete confirms; empty state and “no results” states present.  
**Telemetry**: entity count; FTS latency; search conversion.

## Slice 2 — Locations + Relationships on Map
**Objective**: Add location fields; show markers and connection lines; provenance warnings for sensitive relationships.  
**Scope**: marker clustering; line styles (solid=current, dashed=past); relationship editor; role/dates/strength/confidence; Center on KC.  
**Acceptance**: set location; draw connections; toggle current/past; hover tooltips show role/dates/confidence; provenance required or Draft.  
**Telemetry**: average degree; map render FPS.

## Slice 3 — Graph + Smart Patterns
**Objective**: Force graph with SVG→Canvas threshold; pattern grammar; shortest path.  
**Scope**: focus mode; pattern “explain” strings; selection sync across map/graph.  
**Acceptance**: 60 fps ≤ 500 nodes; “connected to X” and “board members” patterns work with explanations; seamless view switch.  
**Telemetry**: path request count; graph settle time.

## Slice 4 — Enrichment + Workspaces
**Objective**: Enrichment with disambiguation and 30‑day cache; workspace create/switch with last‑view restore.  
**Scope**: candidate list; field‑level apply; provenance records; cache stats; workspace isolation.  
**Acceptance**: enrichment writes sources; force refresh works; cache hit on second request; view and filters restored per workspace.  
**Telemetry**: cache hit rate; enrichment success %.

## Slice 5 — Power Paths + Centrality + Clusters
**Objective**: Influence‑aware path and analysis dashboard.  
**Scope**: path toggles; Explain drawer; centrality table; clusters with isolate and export.  
**Acceptance**: compute under targets; explainability present; recompute invalidates caches correctly.  
**Telemetry**: compute durations; memory warnings; cache staleness.

## Slice 6 — Import/Export + Backups + Command Palette
**Objective**: Move data safely; admin power tools.  
**Scope**: CSV edgelist/matrix export; CSV staging + dry‑run + idempotent commit; encrypted nightly backups; palette commands (including admin).  
**Acceptance**: re‑run import is idempotent; restore works; palette executes top commands.  
**Telemetry**: import error rate; backup success; palette usage.

## Slice 7 — Polish, Performance, and A11y
**Objective**: Hit budgets and refine UX.  
**Scope**: virtualize lists; Canvas threshold tuning; label LOD; keyboard cheat sheet; a11y pass; empty/error states everywhere.  
**Acceptance**: budgets met; screen‑reader validations on key flows; docs reflect final behaviors.  
**Telemetry**: p95 latencies; a11y checklist completion.
