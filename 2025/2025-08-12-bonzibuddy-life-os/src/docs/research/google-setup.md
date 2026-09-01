# Google Docs/Sheets Integration Setup (Local)

This guide walks you through enabling Google Docs and Sheets access for the local, single-user Research domain.

## What you'll get
- Read/Write access to personal Google Docs and Sheets
- Local token storage under `var/google/` (never committed)
- Scopes limited to Drive file content for Docs/Sheets

## 1) Create a Google Cloud Project
1. Go to `https://console.cloud.google.com/` and create a project
2. Enable APIs:
   - Google Drive API
   - Google Docs API
   - Google Sheets API

## 2) OAuth credentials (Desktop App)
1. In Google Cloud Console → APIs & Services → Credentials → Create Credentials → OAuth client ID
2. Application type: "Desktop app"
3. Download the JSON and save as `var/google/credentials.json`
   - Do NOT commit this file (gitignored)

## 3) First run and token cache
- On first use, the app will open a browser window to grant access
- Token gets saved to `var/google/token.json`
- If you need to revoke access, delete `var/google/token.json` and repeat auth

## 4) Scopes (proposed)
- Drive: `https://www.googleapis.com/auth/drive.readonly` (read file metadata)
- Docs: `https://www.googleapis.com/auth/documents.readonly` (read Docs content)
- Sheets (read): `https://www.googleapis.com/auth/spreadsheets.readonly`
- Sheets (write, optional): `https://www.googleapis.com/auth/spreadsheets`

Use read-only scopes by default; elevate to write only when needed.

## 5) Python libraries (to be added)
```txt
# requirements additions (planned)
google-api-python-client
google-auth
google-auth-oauthlib
google-auth-httplib2
# optional convenience
gspread
```

## 6) Minimal local helper (planned)
- Module: `app/integrations/google.py`
- Responsibilities:
  - Create OAuth flow from `credentials.json`
  - Cache token to `var/google/token.json`
  - Lightweight helpers:
    - `fetch_doc(doc_id) -> markdown/text`
    - `fetch_sheet(sheet_id, range) -> rows`
    - `append_rows(sheet_id, rows)` (optional write)

## 7) Security notes
- Keep credentials in `var/google/` only; never commit
- Limit scopes to minimum required
- You can revoke tokens from your Google Account Security settings

## 8) Next steps
- Implement `google.py` helper and wire Research importers:
  - Import Google Doc → create `source` with body as a note or attachment snapshot
  - Import Google Sheet rows → create events/sources based on a selected template
- Add UI to configure mappings (v1 simple presets, v2 custom mapping)


