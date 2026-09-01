# 06 — API Contracts (descriptive; no code)

## Entities
- **List entities**: filters include entity_type, workspace, tags, map bounds; returns paginated results and counts.
- **Create entity**: requires name and type; optional description, location, metadata, tags.
- **Get entity**: expands relationships, tags, notes, media, sources.
- **Update entity**: partial updates, validation for uniqueness per workspace.
- **Delete entity**: cascades to relationships and dependent records with safeguards.

## Relationships
- **List relationships**: filters by entity, source, target, type, current flag.
- **Create relationship**: validates allowed source/target pairs and any provenance requirements.
- **Update relationship**: supports role/date/strength/confidence changes with change history.
- **Delete relationship**: validates that no computed artifacts depend on it (e.g., pinned analysis).

## Search
- **Smart search**: accepts a free‑text query and returns entities + an “explain” string; supports pattern shortcuts and bounds, date, and tag filters.

## Enrichment
- **Enrich entity**: returns candidate matches with match strength; supports field‑level apply and writes provenance + cache entry; supports force refresh.

## Analysis
- **Paths**: returns shortest or power path summary including nodes, hops, and optional influence score; includes an explain string.
- **Centrality**: returns top‑N rows with metric values and metadata (computed_at, parameters).
- **Clusters**: returns cluster IDs and members with cluster metrics.

## Workspaces
- **List** / **Create** workspaces; **Activate** a workspace; **Save view state** (view type, viewport, filters, pins/hidden).

## Export/Import
- **Export**: edgelist CSV, matrix CSV, or JSON (backup).
- **Import**: CSV ingest via staging + dry‑run; returns a conflict report prior to commit; idempotent re‑runs update rather than duplicate.

## Errors
- Error taxonomy includes: VALIDATION_ERROR, DUPLICATE_ENTITY, IMPORT_SCHEMA_MISMATCH, ENRICHMENT_NO_MATCH, ANALYSIS_NO_PATH, ENTITY_NOT_FOUND.
- Every response follows a consistent envelope with human‑readable messages.
