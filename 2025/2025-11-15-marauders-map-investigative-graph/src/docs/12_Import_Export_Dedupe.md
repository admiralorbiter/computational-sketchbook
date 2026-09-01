# 12 — Import, Export, and Dedupe Playbook

## Supported formats
- **Edgelist CSV**: source_name, source_type, target_name, target_type, relationship_type, role, start_date, end_date, confidence, tags.
- **Matrix CSV**: square matrix with entities as both rows and columns; cells contain relationship type/role or blank.
- **JSON backup**: full dump for restore.

## Two-phase import
1) **Staging**: load CSV into staging tables; detect format; trim and normalize names; map aliases to canonical relationship types.  
2) **Dry‑run & report**: show new vs match vs conflict counts; highlight likely duplicates; propose merges.  
3) **Commit**: transactional write; apply idempotency keys; write provenance entries for CSV import.  
4) **Post‑checks**: FTS parity; orphan check; optional summary export of what changed.

## Idempotency keys
- Entities: `workspace|entity_type|normalized_name` (optionally plus place disambiguator).
- Relationships: `workspace|src_key|tgt_key|rel_type|dates`.
- Re‑imports with identical keys update records rather than duplicating them.

## Duplicate detection heuristics
- Name similarity thresholds (Jaro‑Winkler style score).
- Same type and overlapping tags.
- Matching Wikidata QID from enrichment.
- For places, same coordinates within a small radius.

## Merge flow (guided)
- Choose canonical record; bring over relationships, notes, media, tags, and sources; preserve merged name as an alias; record a merge note.
