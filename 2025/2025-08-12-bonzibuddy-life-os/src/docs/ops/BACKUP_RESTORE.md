# Backup & Restore

## Backup (sqlite3)
- Manual: `python scripts/db_dump.py`
- Keep last 7 daily, 4 weekly (policy up to you)

## Verify
- `sqlite3 backup.db ".schema"` and test `SELECT COUNT(*)` on key tables

## Restore
- Stop app → `python scripts/db_restore.py --from backups/<file>` → start app
