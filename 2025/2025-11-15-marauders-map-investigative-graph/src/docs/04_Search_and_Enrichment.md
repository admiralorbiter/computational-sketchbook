# 04 — Search & Enrichment

## Smart search grammar
- **Filters**: type:person, tag:tech, current:true, role:CEO, added:<30d, near:"Kansas City"
- **Patterns**: "board members", "connected to X", "added last week", "person tech", "in downtown"
- **Bounds**: map view applies geographic bounds unless disabled.
- **Explainability**: each query returns a short "Matched by…" explanation and the normalized filter set.

## Ranking model
- Boost order: exact name match > alias match > tag match > description/metadata match.
- **Recency boost** for recently added/updated entities.
- **Spatial proximity** boost within active map bounds.
- Tie‑breakers: entity_type priority and relationship count.

## Enrichment pipeline (Wikipedia + Wikidata)
- **Flow**: user initiates Enrich → candidate list (title, snippet, image) → disambiguation and selection → preview diff → field‑level apply → provenance record → cache raw JSON 30 days.
- **Disambiguation**: match strength computed from title similarity, disambiguation page hints, QID, and context tags; user must choose.
- **Selective merge**: user picks which fields to accept; local edits are never overwritten without explicit confirmation.
- **Cache policy**: 30‑day TTL; force refresh bypasses cache and replaces cached raw JSON with a fresh snapshot.
- **Provenance**: writes to data_sources with confidence_level reflecting the user's trust; change history records field diffs.

## Search help (UI language to ship)
- Try patterns like: board members, connected to "Jane Smith", added last week, person tech, in "downtown"
- Use filters like: type:org, tag:nonprofit, current:true, role:Chair
- Use quotes around multi‑word names and places.
