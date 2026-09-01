# Oura → Flask + SQLite Integration (Checklist)

## 0) Plan & prerequisites
- [x] You have a Flask app (Bootstrap/HTML/CSS/JS) and Python 3.10+.
- [x] You’re okay storing tokens in SQLite for dev; you’ll switch to a managed DB in prod.
- [x] Decide the **minimum scopes** you need (start with `daily email personal`).

---

## 1) Create your Oura application
- [x] Open Oura Cloud → **My Applications** → **Create app**.
- [x] Add redirect URI for local dev: `http://127.0.0.1:5000/callback` (exact match).
- [x] Save **Client ID** and **Client Secret** (do not commit to git).
- [x] Prefer **OAuth** over Personal Access Tokens (PATs); request minimal scopes only.

---

## 2) Project setup
- [x] `pip install flask authlib requests python-dotenv sqlalchemy`
- [x] Create `.env` with:
  - [x] `OURA_CLIENT_ID=...`
  - [x] `OURA_CLIENT_SECRET=...`
  - [x] `OURA_REDIRECT_URI=http://127.0.0.1:5000/callback`

---

## 3) Database (SQLite) bootstrap
- [ ] Create `oura.db` automatically on first run or pre-create it.
- [ ] Ensure tables exist:
  - [ ] `users(user_id TEXT PRIMARY KEY, email TEXT)`
  - [ ] `tokens(user_id TEXT PRIMARY KEY, access_token TEXT, refresh_token TEXT, expires_at INTEGER, scope TEXT)`

---

## 4) OAuth client (Authlib) config
- [ ] Register OAuth client with:
  - [ ] `authorize_url = https://cloud.ouraring.com/oauth/authorize`
  - [ ] `access_token_url = https://api.ouraring.com/oauth/token`
  - [ ] `api_base_url = https://api.ouraring.com/`
- [ ] Set `client_kwargs.scope = "daily email personal"` (or your minimal set).

---

## 5) Routes (server-side OAuth flow)
- [ ] `GET /login` → redirect to Oura authorize URL.
- [ ] `GET /callback` → exchange code for tokens.
- [ ] On callback:
  - [ ] Store `access_token`, `refresh_token`, `expires_at`, `scope`.
  - [ ] Call `GET /v2/usercollection/personal_info` to get stable `user_id` (and email).
  - [ ] Upsert `users` + `tokens`, then set `session["user_id"]`.

---

## 6) Token refresh
- [ ] Before any API call:
  - [ ] Check `expires_at - now() > 60` seconds.
  - [ ] If expired, `POST https://api.ouraring.com/oauth/token` with `grant_type=refresh_token` and update DB.
  - [ ] Never log tokens; always redact in logs.

---

## 7) Pull daily data (last 7 days example)
- [ ] Add `GET /api/daily` route that:
  - [ ] Computes `start_date` = today - 7 days; `end_date` = today.
  - [ ] Calls:
    - [ ] `GET /v2/usercollection/daily_readiness?start_date=...&end_date=...`
    - [ ] `GET /v2/usercollection/daily_sleep?start_date=...&end_date=...`
    - [ ] `GET /v2/usercollection/daily_activity?start_date=...&end_date=...`
  - [ ] Implements pagination using `next_token` until exhausted.
  - [ ] Returns JSON `{ readiness, sleep, activity }`.

---

## 8) Minimal UI (Bootstrap)
- [ ] `GET /`:
  - [ ] If not authed → show “Connect Oura” button to `/login`.
  - [ ] If authed → fetch `/api/daily` via `fetch()` and render JSON in a `<pre>`.
- [ ] Add convenience buttons: “Refresh” (calls `/api/daily`) and “Disconnect” (clears session).

---

## 9) Optional: real-time via webhooks
- [ ] Add `POST /webhooks/oura` endpoint.
- [ ] Choose and store a `verification_token` (shared secret).
- [ ] Create subscription (e.g., `event_type: create`, `data_type: daily_sleep`, `callback_url: https://your-ngrok-or-domain/webhooks/oura`).
- [ ] Verify webhook authenticity (e.g., header or token check) before processing.
- [ ] Upsert or flag new data in DB on each event.
- [ ] For local dev, run `ngrok http 5000` (or similar) and use the public URL as `callback_url`.

---

## 10) Expanding data (add as needed)
- [ ] Heart rate (needs `heartrate` scope): `GET /v2/usercollection/heart_rate?start_datetime=...&end_datetime=...` (+ pagination).
- [ ] Workouts (needs `workout` scope): `GET /v2/usercollection/workout?...`
- [ ] Daily SpO₂ (needs `spo2` scope): `GET /v2/usercollection/daily_spo2?...`
- [ ] Tags/sessions if you plan to annotate events.

---

## 11) Error handling & resilience
- [ ] Handle HTTP 401 → refresh token → retry once.
- [ ] Handle HTTP 429 → exponential backoff; log rate-limit resets.
- [ ] Guard against data delays (sleep data may arrive after phone sync).
- [ ] Timeouts set (e.g., 20s) and retries capped to avoid loops.

---

## 12) Security & privacy basics
- [ ] Never commit `.env` or tokens to source control.
- [ ] Rotate `CLIENT_SECRET` and webhook `verification_token` periodically.
- [ ] Log only non-sensitive metadata; scrub tokens and PII.
- [ ] Show users exactly which scopes you request and why.

---

## 13) Local run & smoke test
- [ ] `flask --app app run`
- [ ] Visit `http://127.0.0.1:5000/` → **Connect Oura** → complete OAuth.
- [ ] Confirm:
  - [ ] `users` row created with `user_id` + `email`.
  - [ ] `tokens` row with `access_token`, `refresh_token`, `expires_at`.
  - [ ] `/api/daily` returns arrays with recent data.
  - [ ] Pagination works (manually test with longer ranges).

---

## 14) Production prep
- [ ] Use HTTPS; update **redirect URI** in Oura app to your real domain.
- [ ] Set strong `FLASK_SECRET_KEY` in environment.
- [ ] Migrate from SQLite to managed DB (Postgres/MySQL) and add migrations.
- [ ] Add structured logging + alerting for failures and 401/429 spikes.
- [ ] Set a task or webhook to keep data current (avoid polling if webhooks enabled).

---

## 15) Nice-to-haves
- [ ] Cache most recent daily aggregates to speed up page loads.
- [ ] Add charts (client-side JS) for readiness/sleep/activity trends.
- [ ] CLI or admin page to re-consent scopes if you add new data types later.
- [ ] Health check endpoint for uptime monitoring.

---

## 16) Done when…
- [ ] OAuth login completes; tokens persist and refresh automatically.
- [ ] Daily endpoints populate your DB/UI for a chosen date range.
- [ ] Optional webhook events update data without manual polling.
- [ ] Logs are clean (no secrets) and errors are actionable.
