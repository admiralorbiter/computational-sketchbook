# Privacy & Security (local single‑user)

- Local database (`var/bonzibuddy.db`) not encrypted in v0.
- Secrets via `.env` only (no secrets in repo).
- Backups stored locally under `/backups`; consider external drive sync.
- Incident playbook: lost device → rotate machine login, delete DB or restore from backup, review audit.
- Option: evaluate SQLCipher or OS‑level disk encryption later.
