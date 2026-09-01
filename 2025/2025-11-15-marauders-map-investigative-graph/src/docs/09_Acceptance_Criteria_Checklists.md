# 09 — Acceptance Criteria & Checklists

## Global Definition of Ready
- Data model deltas enumerated and validated.
- UI states planned: loading, empty, error, retry.
- Telemetry points named and documented.
- Search/analysis “Explain” copy drafted.
- Undo/redo interactions planned.

## Global Definition of Done
- All acceptance criteria pass.
- Provenance chips visible where applicable.
- Performance budgets met and measured.
- Backup/restore smoke test passes.
- Import/export round‑trip test (if touched).
- Docs updated (changelog and affected files).

## Per‑slice acceptance (high‑level)
- **Entities/Search**: live results; highlight; no duplicate creation within workspace.
- **Map/Relationships**: correct line styles; current/past toggles; provenance enforced; tooltips complete.
- **Graph/Patterns**: threshold behavior; pattern explain text; synchronized selection.
- **Enrichment/Workspaces**: disambiguation screen; cache indicators; per‑workspace view restore confirmed.
- **Analysis**: path explain panel; centrality/cluster outputs labeled; recompute control.
- **Import/Export/Backups**: dry‑run conflict report; idempotency keys respected; restore test OK.
