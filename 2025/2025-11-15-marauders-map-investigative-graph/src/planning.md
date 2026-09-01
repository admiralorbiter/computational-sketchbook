Slice 1 — Entities CRUD + Live Search (vanilla JS + Tailwind)
==============================================================

- Frontend structure under `app/client/static`:
  - `index.html` — shell layout, header + search, entities panel, map/graph placeholders.
  - `js/api.js` — fetch helpers for health, entities list, CRUD, and search.
  - `js/entities.js` — entities state, rendering, form handling, edit/delete interactions.
  - `js/shell.js` — header wiring, health check, search box, initial data load.
  - `js/map.js` / `js/graph.js` — stubs for future slices.
  - `js/bootstrap.js` — entrypoint that wires everything together on `DOMContentLoaded`.

- Backend scope:
  - Extend `entities` schema for soft delete and updates.
  - Add `PATCH /api/entities/<id>`, `DELETE /api/entities/<id>`, and `GET /api/entities/search`.

- UX behaviors:
  - Search box debounces input (~200 ms) and calls the search endpoint.
  - Entities list supports add, edit (prompt-based), and delete with confirmation.
  - Empty, loading, and error states are visible in the entities panel.

Slice 2 — Locations + Relationships on Map (canvas skeleton)
============================================================

- Backend scope:
  - Add `relationships` table aligned with `03_Data_Governance_and_Schema.md`:
    - `id, source_id, target_id, relationship_type, role, start_date, end_date, is_current, strength, confidence, provenance_json, created_at, updated_at, is_deleted`.
  - Extend `entities` with optional location fields: `lat`, `lng`, and `location_label`.
  - New relationship endpoints following the same `{ ok, data|error }` envelope:
    - `GET /api/relationships?entity_id=...`
    - `POST /api/relationships`
    - `PATCH /api/relationships/<id>`
    - `DELETE /api/relationships/<id>`

- Frontend structure under `app/client/static/js`:
  - `state/selection.js` — shared selection + hover state for active entity/relationship.
  - `map/index.js` — `setupMap(container)` entry; draws markers and relationship lines from entities/relationships.
  - `map/interactions.js` — map click/drag interactions:
    - select entities via marker clicks;
    - “start connection” flow: click source, click target, open relationship editor.
  - `map/controls.js` — KC quick center button and basic zoom helpers.
  - Existing `entities.js` continues to own the side panel and reads/writes `selection` state.

- UX behaviors (first cut):
  - User can set location for an entity via the entity panel; entities without `lat/lng` simply don’t appear on the map.
  - Map supports pan/zoom; clicking a marker selects the entity and highlights its relationships.
  - Creating a relationship:
    - User selects entity A, then entity B, then chooses `relationship_type` and optional role/dates/strength/confidence.
    - Relationship is persisted via the relationships API and rendered as a line between markers.
  - Line style reflects current vs past (`is_current`): solid for current, dashed for past.
  - Basic edge tooltip shows type, role, dates, and strength/confidence values.

