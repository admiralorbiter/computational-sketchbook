# Product Requirements — Burn Note MVP (Web SPA, Stubbed E2E)

## Context
- Problem: People want topical, anonymous rooms without profiles or exposure.
- Vision: One-line intent → relevant room → ephemeral participation; “Say it once, leave no trail.”
- Constraints (MVP): Web SPA only; server sees plaintext (internal testing); design path to E2E.

## Goals & Non-Goals
### Goals
- Anonymous entry via intent; local match against Room Atlas
- Rooms with Live chat, Posts, Highlights, Resources
- Whispers (opt-in 1:1), session masks, Burn Session
- Basic safety: reports, slow-mode, rate limits on ciphertext envelopes (design), plaintext for MVP impl
### Non-Goals
- Full E2E (MLS/DR), OHTTP relays, PIR Atlas — documented, not implemented in MVP

## Personas
- Nora (hobby): quick chat and recs; no profile
- Chris (sensitive): privacy trust, whispers, resources
- Devon (lurker): read-first, highlights

## Top User Stories
- As a visitor, I type my intent and land in a relevant room in <2s.
- As a member, I can post in Live or create a Post with tags/spoilers.
- As a cautious user, I can join read-only for 60s.
- As a participant, I can start/accept a whisper that expires by default.
- As a user, I can Burn Session to leave and wipe my mask locally.
- As a user, I can report harmful content and continue safely.

## Scope (MVP)
- Intent box → local ranking vs Atlas v1 (design) → join best room
- Rooms: Live chat (plaintext MVP), Posts, Highlights (manual curation MVP)
- Whispers: consent handshake, expiry (plaintext MVP)
- Safety: reports (consented plaintext), slow-mode, rate limits (token bucket design)

## Acceptance Criteria (MVP)
- P50 time submit → inside room ≤ 2.0s (P95 ≤ 4.0s)
- No account creation required
- Clear privacy banner (MVP internal): server-visible plaintext; E2E planned
- Reporting flow with consent copy and outcomes (tombstone, slow-mode, block/mute)

## Success Metrics (aggregated; MVP approximations)
- Match Fit thumbs-up rate; Time-to-first-reply; 7-day healthy return
- Abuse rates (reports per 100 messages); mod TTR for severe categories

## Risks & Mitigations
- Privacy risk (plaintext MVP) → internal-only, minimal logging, short retention, E2E migration plan
- Abuse/spam → anonymous rate limits (MVP tokens), slow-mode, mod workflow
- Cold start → seed starter rooms, highlights

## References
- See `mvp_design_technical_spec_anonymous_topic_rooms_working_title_whisper_rooms.md`
- See `ui_ux_brainstorm_whisper_rooms.md`


