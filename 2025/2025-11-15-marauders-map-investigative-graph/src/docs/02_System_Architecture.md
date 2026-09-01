# 02 — System Architecture (Flask)

## Runtime model
- **Single‑user** application served by Flask.
- **Client**: vanilla JavaScript with D3 (graph) and Leaflet (map), Tailwind for styling.
- **Data**: SQLite with FTS5 for search, JSON columns for flexible metadata.
- **Cache**: enrichment cache with 30‑day TTL; in‑memory hot entity cache.
- **Storage**: workspace‑scoped media folder; backup folder with rotation.
- **Security posture**: local-first, optional DB encryption; encrypted backups default.

## Components
1. **API layer (Flask)** — entities, relationships, search, enrichment, analysis, workspaces, import/export.
2. **Data layer (SQLite)** — normalized tables, FTS5 virtual table; constraints and triggers for integrity and search sync.
3. **Client app** — Shell (header/search/palette), Map/Graph/Hybrid canvas, Filters, Entity Panel, Modals.
4. **Analysis engine** — in‑process computations for shortest path, power path weighting, centrality, and clusters.
5. **Ops subsystem** — backup/restore, health summary, metrics logging, configuration.

## Cross‑cutting concerns
- **Explainability**: each smart search or analytical result provides an “Explain” message describing how/why it matched.
- **Undoability**: entity/relationship operations recorded in a per‑workspace undo/redo log (target depth ~100).
- **Provenance**: every enrichment or claimed fact attaches its source and confidence to data_sources; UI always surfaces sources.
- **Workspace isolation**: every query and mutation is scoped to the active workspace unless explicitly overridden.

## Extension points
- **Relationship vocabulary registry**: add canonical types and aliases without changing the schema.
- **Entity metadata schemas**: per‑type JSON Schema for validation; unknown fields stored under metadata.extra.
- **Export formats**: add more exporters beside edgelist/matrix/JSON via an export registry.
