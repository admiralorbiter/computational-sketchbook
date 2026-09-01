# 10 — Risks & ADRs

## Top risks & mitigations
- **Duplicate entities** from imports/enrichment → strict normalization, fuzzy thresholds, merge flow with provenance carryover.
- **Graph performance** on large datasets → switch to Canvas; progressive expansion; hide labels until zoomed; debounce interactions.
- **Ambiguous enrichment** → explicit user disambiguation; field‑level apply; cached raw JSON; easy rollback.
- **Data loss** → nightly backups + pre‑import auto‑backup; restore flow tested in CI; backup health indicator.
- **Vocabulary drift** → controlled list with alias mapping; periodic review; analytics on “related_to” overuse.

## ADRs (concise)
1. **SQLite + FTS5** for single‑user simplicity and performance; WAL mode recommended.
2. **SVG→Canvas** switch at ~500 nodes; progressive expansion >1K.
3. **Optional DB encryption**, **encrypted backups default**.
4. **Provenance required** for sensitive relationship types; otherwise Draft state.
5. **KC defaults** implemented via workspace presets and controls, not schema.
