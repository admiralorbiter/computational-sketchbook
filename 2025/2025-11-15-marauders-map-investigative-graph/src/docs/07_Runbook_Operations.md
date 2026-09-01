# 07 — Runbook & Operations

## Folders and files
- Application data root contains: 
  - `database/` (SQLite DB file; optional SQLCipher), 
  - `media/{workspace}/` (attachments), 
  - `backups/` (rotating JSON backups), 
  - `logs/` (structured logs as NDJSON).

## Configuration
- Workspace defaults (KC viewport, quick center).
- Cache TTLs (enrichment 30 days).
- Attachment limits (default 25 MB/file; 1 GB/workspace soft cap).
- Encryption: DB off by default; encrypted backups on by default (zip + passphrase).

## Backups
- **Automatic** nightly backups; 7‑day rotation.
- **Manual** backup from settings at any time.
- **Restore**: validate schema version; preview counts; confirm overwrite; restore media and DB together; log success.

## Health checks
- System Status panel shows: DB size, last backup time, cache entries, FTS doc count, analysis cache entries.
- Red flags: last backup > 24 h; FTS count mismatch; media path missing.

## Logging & metrics
- Log API latency (p50/p95), FTS query time, enrichment cache hits, analysis durations, import outcomes.
- Surface counters in a simple dashboard.

## Migrations
- Schema migrations are additive and backward‑compatible when possible; include a one‑time migration for new constraints and indexes; always auto‑backup before migrating.

## Security posture
- Local‑only by default; no external secrets required.
- Optional DB encryption; encrypted backups default.
- Attachment validation by MIME + magic bytes; filename sanitization.
