# 13 — Security & Privacy (Local-first)

## Threat model (v1)
- Single-user, local environment; primary risks are local data loss, accidental exposure via backups, and malicious files.

## Controls
- **Encryption**: DB encryption optional; backup archives encrypted by default (passphrase-based).
- **Uploads**: limit file types and sizes; validate MIME + magic bytes; sanitize filenames; store per workspace.
- **Input validation**: strict server-side validation for names, dates, coordinates, and relationship types; JSON schema for metadata.
- **No secrets**: no external API keys are required for built‑in enrichment.

## Data retention
- Backups keep 7 rotating copies by default; older backups pruned.
- Delete operations are hard deletes; consider soft‑delete in future ADR if needed.

## Incident response (local)
- On crash or corruption, use last good backup from the Runbook; document timestamp and actions taken.
