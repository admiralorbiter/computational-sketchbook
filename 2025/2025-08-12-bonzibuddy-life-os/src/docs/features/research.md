# Research Feature Spec (v0 → v2)

**Status:** 🚧 v0 IN PROGRESS (Spec Drafted; partial UI implemented)
**Scope:** Research and learning management for a local, single‑user Flask app (SQLite, manual migrations). This replaces Google Sheets tracking for current events, sources, notes, and highlights. This doc is the canonical spec for the Research feature.

## 🎯 Implementation Status

### 🎯 v0 Goals (Initial Release)
- Current Events log: headline, date, outlet, summary/story, URL, tags
- Sources library: papers/reports/blogs/videos with unified metadata and tags
- Notes and Highlights linked to sources (location + text)
- Questions and Evidence links (question ↔ source, stance)
- Tagging across entities (reuse global `tag`/`tag_map`)
- Basic search (filtering) and CSV import for events/sources
- Minimal HTML views and JSON API for CRUD

### 🚧 v1+ Enhancements (Planned)
- SQLite FTS5 full‑text search across sources/notes/highlights/events
- Importers: DOI/ArXiv enrichment, RSS feeds, URL metadata, PDF text extract
- Saved searches, reading queue, reading progress, BibTeX export
- Attachments management for PDFs and snapshots; quick open
- De‑duplication (URL/DOI/ArXiv ID) and merge flows

### 🧪 v2 (Advanced)
- Summaries, embeddings, semantic search, Q&A over local corpus
- Topic models, tag suggestions, auto‑linking sources ↔ questions
- Optional collaboration mode (multi‑user) behind local auth

---

## 1) Goals & Non‑Goals

### Goals
- Replace spreadsheets with a structured, extensible system
- Capture both “current events” and “research sources” with shared tagging
- Keep everything local; enable robust offline search and attachments
- Make capture fast (keyboard‑friendly) and review easy (saved searches)

### Non‑Goals (v0)
- No web scraping beyond basic URL metadata fetch
- No cloud sync; no multi‑user; no third‑party uploads
- No automated summarization or embeddings (reserved for v2)

---

## 2) Data Model (manual SQL)

Tables marked (existing) come from migration 0004. New tables are proposed with future migration numbers under “Migrations”.

### Core / Shared
- `schema_version` (existing)
- `tag` (existing) / `tag_map` (proposed shared): lightweight tagging across entities
- `attachment` (existing) / `attachment_map` (proposed shared): link files to any entity
- `audit` (existing)

### Research Entities
- `question` (existing): `id, text, area, status, created_at`
- `source` (existing, extend):
  - Minimal: `id, kind, title, author, year, url, citation`
  - Proposed v0+ fields: `venue, publisher, published_date, language, abstract, doi, arxiv_id, via_url, added_ts DEFAULT CURRENT_TIMESTAMP`
- `note` (existing): `id, source_id NULL, question_id NULL, ts DEFAULT CURRENT_TIMESTAMP, body`
  - v1 add: `kind (note|summary)`, `pinned BOOL`
- `highlight` (existing): `id, source_id NOT NULL, location TEXT, text`
  - v1 add: `comment TEXT`
- `news_event` (new v0): `id, date_ts, headline, outlet, summary, url, added_ts DEFAULT CURRENT_TIMESTAMP`
- `evidence_link` (new v0): `id, question_id, source_id, stance (supports|refutes|neutral), note`

### Tagging (shared)
- `tag_map` (new v0): `id, entity_type, entity_id, tag_id` with unique `(entity_type, entity_id, tag_id)`

### Attachments (shared)
- `attachment_map` (new v1): `id, entity_type, entity_id, attachment_id`
  - `attachment` holds: `id, path, mime, bytes, note`

### Full‑Text Search (v1)
- `source_fts`, `note_fts`, `highlight_fts`, `news_event_fts` (SQLite FTS5 virtual tables)
  - Content: titles, authors, venues, abstracts, note bodies, highlight text, headlines/summaries
  - Triggers to keep in sync on INSERT/UPDATE/DELETE

### Indexes & retention
- B‑tree indexes on foreign keys and time fields (`date_ts`, `ts`, `added_ts`)
- FTS for text fields (v1)
- No auto‑purge; explicit export/backup only

---

## 3) Views & Flows

### Research Home (dashboard)
- Quick capture: new event, new source by URL/DOI/arXiv, quick note
- Cards: This week’s events, New sources, Open questions, Saved searches

### Current Events
- List: date, headline, outlet, tags
- Detail: full summary, URL, related tags, quick convert to `source`
- Quick add: headline, date, outlet, URL, summary, tags
 - Inline edit on list rows (headline/outlet/url)

### Sources Library
- Table: kind, title, authors, year/venue, tags, attachments
- Filters: kind, year, tag chips, has PDF
- Detail: metadata, attachments, related notes/highlights, evidence links
 - Inline edit on list rows (title/kind/author/year/url)

### Questions & Evidence
- Board/list of questions (status: open, in‑progress, answered)
- For each question: linked sources with stance, notes, highlights
- Evidence matrix: rows = sources, cols = stance; export as Markdown/CSV

### Notes & Highlights
- Inline capture while reading; optional `location` (page, CFI, timestamp)
- Highlights shown in context; notes summarized at source & question level

### Tags & Saved Searches (v1)
- Tag manager; bulk add/remove on selections
- Saved searches: named queries (free‑text + filters JSON)

---

## 4) Integrations & Imports (later)

### CSV / Sheets
- Import events and sources from CSV (column mapping UI; dedup)
- Sources CSV mapping supported: `Title`→`title`, `Date`→`year` (parsed), `Type`→`kind`, `Notes`→`abstract`, `Tags`→tags, `URL`→`url`, `Biblo`→`citation`
- Optional list-level tag at import time via `list_tag` (applied to all imported rows)
- Export CSV/JSON for all entities

### Metadata Enrichment (v1)
- DOI lookup (Crossref) and ArXiv metadata fetch
- URL metadata (OpenGraph/HTML title); readable article extraction for summaries

### Feeds (v1)
- RSS/Atom subscriptions to populate `news_event`
- Manual “inbox” queue to review and file as event or source

### PDFs & Files (v1)
- Attach local PDFs to `source`; optional text extraction for FTS
- Snapshot URL to PDF/PNG (manual)

---

## 5) Business Rules (initial)
- Deduplication keys (priority order): `doi` → `arxiv_id` → normalized `url`
- Canonical author string normalization (strip punctuation; last‑name first optional)
- Tag inheritance: tags on `source` surface on its `notes/highlights` (view‑level)
- Evidence stance is per question+source; default `neutral`
- “Reading time” estimate derived from word count (when available)

---

## 6) UI/UX Notes
- Keyboard shortcuts: `n` new note, `h` new highlight, `e` new event, `/` search
- Filter chips for tags/kind/year; clear‑all button
- Attachment quick‑open from source detail
- Mobile‑first capture forms

---

## 7) Privacy & Risk
- Local‑only storage; no external uploads
- Copyright sensitivity: store only metadata/excerpts; use attachments for locally owned PDFs
- Respect robots/licenses when fetching metadata; user‑initiated only

---

## 8) Metrics & Dashboards
- Tiles: events this week, new sources, open questions, notes added, highlights added
- Trends: events/week, sources/month by kind, top tags

---

## 9) API (v0 minimal → v1 extended)

### Dashboard
- `GET /research/` — Research dashboard HTML (basic)
- `GET /research/dashboard` — Aggregate counts JSON

### Current Events
- `GET /research/events` — List events (filters: `q, tag, from, to, outlet`)
- `POST /research/events` — Create `{date_ts, headline, outlet?, summary?, url?, tags?}`
- `GET /research/events/{id}` — Retrieve
- `PUT /research/events/{id}` — Update
- `DELETE /research/events/{id}` — Delete
- `POST /research/events/import/csv` — CSV import (dry‑run option)

### Sources
- `GET /research/sources` — List (filters: `q, kind, year, tag, has_pdf`)
- `POST /research/sources` — Create `{kind, title, author?, year?, url?, doi?, arxiv_id?, venue?, publisher?, abstract?, tags?}`
- `GET /research/sources/{id}` — Retrieve
- `PUT /research/sources/{id}` — Update
- `DELETE /research/sources/{id}` — Delete
- `POST /research/sources/{id}/attachments` — Attach local file `{path, note?}`

### Notes & Highlights
- `GET /research/notes` — List (filters: `source_id?, question_id?, q`)
- `POST /research/notes` — Create `{source_id?, question_id?, body, kind?}`
- `PUT /research/notes/{id}` — Update `{body?, kind?, pinned?}`
- `DELETE /research/notes/{id}` — Delete
- `GET /research/highlights` — List (filters: `source_id?, q`)
- `POST /research/highlights` — Create `{source_id, text, location?, comment?, tags?}`
- `PUT /research/highlights/{id}` — Update
- `DELETE /research/highlights/{id}` — Delete

### Questions & Evidence
- `GET /research/questions` — List questions (filters: `status?, tag?`)
- `POST /research/questions` — Create `{text, area?, status?}`
- `PUT /research/questions/{id}` — Update
- `DELETE /research/questions/{id}` — Delete
- `GET /research/questions/{id}/evidence` — List evidence links
- `POST /research/questions/{id}/evidence` — Link source `{source_id, stance?, note?}`
- `DELETE /research/evidence/{id}` — Unlink

### Search (v1)
- `GET /research/search` — Unified search across FTS tables `{q}` → grouped results

### Tags (shared)
- `GET /research/tags` — List tags used in research
- `POST /research/tags/bulk_map` — Bulk add/remove on selections

---

## 10) Testing
- Unit: dedup keys, import mappers, evidence linking, FTS tokenization (v1)
- Feature: quick‑add flows for events/sources/notes/highlights
- Fixtures: sample CSVs (events, sources), tiny DB snapshots
- Coverage target: ≥80% for research services

---

## 11) Backlog

### v0
- Entities: `news_event`, `evidence_link`, `tag_map`
- CRUD APIs + minimal HTML views
- CSV importers for events and sources (mapping UI + dry‑run)
- Dashboard counts JSON

### v1
- FTS5 tables + triggers; unified `/research/search`
- Importers: DOI/ArXiv, RSS feeds, URL metadata, PDF text
- Saved searches; reading queue; attachments UI (`attachment_map`)
- BibTeX/CSL JSON export

### v2
- Summaries & embeddings; semantic search; Q&A
- Tag suggestions; topic modeling; auto evidence linking

---

## 12) Split Candidates

| Area                         | Complexity | Data Volume | UX Surface | Recommend Split? | Notes                                      |
| ---------------------------- | ---------: | ----------: | ---------: | ---------------- | ------------------------------------------ |
| Current Events               |      Medium|        High |      Medium| Maybe            | Feeds/importers can grow over time.        |
| Sources Library              |      Medium|        High |       High | Yes              | Metadata, filters, attachments.            |
| Notes & Highlights           |      Medium|        High |       High | Yes              | Capture flows, FTS, context links.         |
| Questions & Evidence         |      Medium|      Medium |      Medium| Maybe            | Matrix views, stance logic.                |
| Importers & ETL              |       High|      Medium |      Medium| Yes              | DOI/ArXiv, RSS, HTML extract, PDF text.    |
| Search & Indexing (FTS/emb)  |       High|        High |      Medium| Yes              | FTS + semantic later.                      |
| Attachments                  |      Medium|      Medium |      Medium| Maybe            | Cross‑domain shared component.             |

---

## 13) Migrations (proposed adds)
- `0013_research_events.sql` — create `news_event`, `evidence_link`, `tag_map`
- `0014_research_fts.sql` — FTS tables (`source_fts`, `note_fts`, `highlight_fts`, `news_event_fts`) + triggers
- `0015_attachments_map.sql` — `attachment_map` table for cross‑entity linking

Each migration uses `BEGIN; ... INSERT INTO schema_version(...); COMMIT;`.

---

## 14) Open Questions
1. Required `source.kind` enum values (paper, report, blog, article, video, podcast, dataset, other)?
2. Minimum event fields for CSV import; column headers to support (current: headline, date, outlet, summary, url, tags)
3. Evidence stance scale: keep 3‑way (supports/refutes/neutral) or expand to 5‑point confidence?
4. Preferred PDF text extractor (none in v0; v1 choose pdfminer, pypdf, or poppler tools)?
5. Saved searches format: plain string + filter JSON OK?

---

## 15) ADR Hooks
## 16) Planning
- See Implementation Plan: `../planning/ResearchImplementationPlan.md`

## 17) External Integrations (Google Docs/Sheets - planned)
- Desktop OAuth with local token cache under `var/google/`
- Read-only scopes by default (Docs, Sheets, Drive metadata)
- Import flows:
  - Google Doc → create `source(kind='doc')` + insert body as `note(kind='summary')`
  - Google Sheet → map rows into `news_event` or `source` via preset templates
- Helper module `app/integrations/google.py` with:
  - `fetch_doc(doc_id) -> text`
  - `fetch_sheet(sheet_id, range) -> rows`
  - `append_rows(sheet_id, rows)` (optional write)
  - For now, prefer storing links via `external_link` and only import when needed.

- ADR‑R‑0001 — Research v0 entities & flows (this doc)
- ADR‑R‑0002 — Search strategy: SQLite FTS5 vs external index
- ADR‑R‑0003 — Importer strategy (DOI/ArXiv/RSS/URL metadata)
- ADR‑R‑0004 — Deduplication keys & merge policy


