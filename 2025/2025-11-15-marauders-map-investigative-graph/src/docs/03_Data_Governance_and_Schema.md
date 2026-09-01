# 03 — Data Governance & Schema Semantics

## Entity model (semantics)
- **Types**: person, organization, place, event (controlled for v1; extensible later).
- **Required**: name, entity_type. **Recommended**: display_name, aliases, tags, description, lat/lng, address.
- **Uniqueness**: `(workspace_id, normalized_name, entity_type)` unique. Normalize by trimming, Unicode NFKC, and case folding.
- **Metadata**: typed JSON per entity type; unknown fields preserved in `metadata.extra` to avoid schema churn.
- **Aliases**: string array; used by search ranking and duplicate detection.

## Relationship model (semantics)
- **Required**: source, target, relationship_type.
- **Fields**: role/title, start_date, end_date, is_current (derived from dates by default), strength (1–5, tie intensity), confidence (1–5, evidence trust), metadata.
- **Allowed pairs**: validated at save time (e.g., person→org for employee/board_member; entity→place for located_in/headquartered_in).
- **Current vs past**: `is_current` true when no end_date or end_date ≥ today unless explicitly overridden with audit note.

## Controlled vocabulary and alias mapping
- Canonical types: employee, executive, board_member, advisor, founder, investor, partner, vendor, subsidiary, affiliate, member_of, attended, spoke_at, organized, located_in, headquartered_in, related_to (fallback).
- Aliases map to canonical types (e.g., "works_at" → employee, "CEO_of" → executive). Maintain synonyms per locale.
- Maintain **validation rules** per type (required fields, directionality, allowed pairs, provenance requirement flags).

## Provenance & sources
- Each enriched or asserted fact records: source_type, title, url (optional), confidence_level, fetched_at, raw_data snapshot.
- **UI policy**: show source chips on entity/relationship panels; clicking opens a source drawer with details.
- Some relationship types (board_member, executive, investor, donor, advisor) **require** ≥1 source or must be saved as **Draft**.

## Tags, notes, and media
- **Tags**: name, color, category; used for search facets and legends.
- **Notes**: attach to entity/relationship; note_type (research, todo, question); optional geo_bounds for area annotations.
- **Media attachments**: images, PDFs, CSVs; stored per workspace; thumbnails for images; external link attachments permitted.

## Deduplication & merge
- **Duplicate detection**: normalized name + entity type, optional location; fuzzy thresholds; matching by Wikidata QID when present.
- **Guided merge**: choose canonical record; transfer relationships/tags/notes/media/sources; keep alias redirect from merged name.
- **Invariants to maintain**:
  - No orphaned relationships (FK constraints).
  - No cycles in directed “subtype” vocab (if extended later).
  - Search index mirrors entity rows (trigger‑based updates).
