# Research Implementation Plan

**Status:** 🚧 IN PROGRESS  
**Created:** 2025-08-13  
**Scope:** Implementation roadmap for research.md features v0 → v2

---

## 🎯 Objectives (v0)
- Current events capture (headline, date, outlet, summary, URL, tags)
- Sources library (papers/reports/blogs/videos) with tags and attachments (PDFs)
- Notes and highlights linked to sources and questions
- Questions with evidence links (supports/refutes/neutral)
- Minimal HTML views + JSON CRUD API
- CSV import for events and sources (dry‑run option)

## Out of Scope (v0)
- Full‑text search (FTS5), RSS/DOI/ArXiv importers, PDF text extraction (planned v1)
- Semantic embeddings and Q&A (v2)

---

## Links
- Feature Spec: ../features/research.md
- API Endpoints: ../api/ENDPOINTS.md
- Google Integrations (planned): ../research/google-setup.md

---

## Work Log
- 2025‑08‑13: Spec drafted; plan created; endpoints defined; migrations outlined; `0013_research_events.sql` added; basic ResearchService and events/sources endpoints implemented; Research dashboard + Events/Sources HTML views added. Inline quick-add on dashboard; tag chips + CRUD on lists; external links; inline edit on events/sources lists.

---

## Phase 1: Data Layer & Migrations (v0)

### Schema
- [ ] Create `0013_research_events.sql`
  - [ ] `news_event(id, date_ts TEXT, headline TEXT, outlet TEXT, summary TEXT, url TEXT, added_ts TEXT DEFAULT CURRENT_TIMESTAMP)`
  - [ ] `evidence_link(id, question_id INT, source_id INT, stance TEXT, note TEXT)`
  - [ ] `tag_map(id, entity_type TEXT, entity_id INT, tag_id INT, UNIQUE(entity_type, entity_id, tag_id))`
  - [ ] FKs to `source(id)` and `question(id)` where applicable
  - [ ] `INSERT INTO schema_version(...)`
- [ ] Extend `source` with columns: `venue, publisher, published_date, language, abstract, doi, arxiv_id, via_url, added_ts`
- [ ] Extend `note` with optional `kind, pinned` (nullable for v0)
- [ ] Extend `highlight` with optional `comment` (nullable for v0)

### Indices
- [ ] Add indices on time fields (`date_ts`, `added_ts`) and FKs

### Seed/Backfill (optional)
- [ ] Tag seeds if needed

---

## Phase 2: Services & CRUD (v0)

### Service Layer (`app/domains/research/services.py`)
- [ ] Events: list/create/get/update/delete, CSV import (dry‑run)
- [ ] Sources: list/create/get/update/delete, attach file
- [x] Notes: list/create/update/delete
- [x] Highlights: list/create/update/delete
- [x] Questions: list/create/update/delete
- [x] Evidence: list/create/delete
- [ ] Dashboard summary counts

### Validation
- [ ] Dedup keys (`doi` → `arxiv_id` → normalized `url`) for sources
- [ ] Basic URL normalization
- [ ] Tags parsing from CSV (comma/semicolon)

---

## Phase 3: API Endpoints (v0)

Wire routes in `app/domains/research/views.py` to service layer:
- [ ] `GET /research/dashboard`
- [ ] Events: `GET/POST /research/events`, `GET/PUT/DELETE /research/events/<id>`, `POST /research/events/import/csv`
- [ ] Sources: `GET/POST /research/sources`, `GET/PUT/DELETE /research/sources/<id>`, `POST /research/sources/<id>/attachments`
- [ ] Notes: `GET/POST /research/notes`, `PUT/DELETE /research/notes/<id>`
- [ ] Highlights: `GET/POST /research/highlights`, `PUT/DELETE /research/highlights/<id>`
- [ ] Questions: `GET/POST /research/questions`, `GET/PUT/DELETE /research/questions/<id>`
- [ ] Evidence: `GET/POST /research/questions/<id>/evidence`, `DELETE /research/evidence/<id>`

---

## Phase 4: Minimal UI (v0)
- [x] Dashboard view: counts + quick capture links
- [x] Events list + quick add form
- [x] Sources list + detail (metadata, related notes/highlights, evidence)
- [x] Tag filters for events/sources; tag CRUD endpoints (shared)
- [x] External links on sources (Google Docs/Sheets/Web)
- [x] Inline edit on events/sources list rows
- [ ] Notes/highlights inline capture (modal or inline form)
- [ ] Questions list and evidence matrix (simplified)

---

## Phase 5: CSV Import (v0)

### Events CSV
Headers: `date_ts,headline,outlet,summary,url,tags`
- [x] Dry‑run support in services (events, sources)
- [ ] Mapping: normalize headers (case/space insensitive)
- [ ] Tags split on `,` or `;`

### Sources CSV
Headers: `kind,title,author,year,url,doi,arxiv_id,venue,publisher,abstract,tags`
- [ ] Dedup resolution and merge rules
- [ ] Attach tag_map on import

---

## Phase 6: Testing
- [ ] Unit tests: dedup keys, tag parsing, CSV import mappers, evidence linking
- [ ] Feature tests: CRUD flows for events/sources/notes/highlights/questions
- [ ] Fixtures: sample events.csv and sources.csv, tiny DB snapshots
- [ ] Coverage target: ≥80% for research services

---

## v1 Enhancements
- [ ] FTS5 virtual tables + triggers (`0014_research_fts.sql`)
- [ ] Unified `/research/search` endpoint
- [ ] Importers: DOI/ArXiv, RSS/Atom, URL metadata; PDF text extraction
- [ ] Saved searches; reading queue; `attachment_map` (`0015_attachments_map.sql`)
- [ ] Google Docs/Sheets integration (read-only): helper + import flows
- [ ] UI for Google import (Doc → source/note, Sheet → events/sources)

---

## Risks & Mitigations
- Data model creep → Keep v0 small; push indexing/importers to v1
- CSV variety → Add dry‑run and flexible header mapping
- Attachments path handling → Store absolute/relative safely; no auto‑download

---

## Next Steps
1) Write `0013_research_events.sql` migration  
2) Implement `ResearchService` with events/sources CRUD  
3) Wire endpoints in `app/domains/research/views.py`  
4) Minimal HTML templates for dashboard, events, sources  
5) CSV import (events, sources) with dry‑run  
6) Google Docs/Sheets helper module and import endpoints  


