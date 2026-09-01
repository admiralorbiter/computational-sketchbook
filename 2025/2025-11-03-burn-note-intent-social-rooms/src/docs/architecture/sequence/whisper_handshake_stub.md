# Sequence — Whisper Handshake (MVP, Stubbed Crypto)

## Context
- MVP: plaintext whispers; crypto upgrade to X3DH + Double Ratchet post-MVP

## Steps (MVP)
1. Sender clicks Ask to Whisper on member
2. `POST /v1/whispers` creates pending session with expiry (24h default)
3. Recipient accepts via `POST /v1/whispers/{id}/accept`
4. Both sides can send via `POST /v1/messages` with `type=whisper` and `whisperId`
5. Either side can end session or extend expiry

## Errors
- 403 if recipient has blocks/mutes sender
- 409 if already in an active whisper
- 410 if session expired

## Migration (post-MVP)
- Replace steps 2–4 with X3DH bundle fetch and DR session init; store only ciphertext


