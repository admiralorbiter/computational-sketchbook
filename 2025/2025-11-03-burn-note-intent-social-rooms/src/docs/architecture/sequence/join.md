# Sequence — Intent to Join (MVP, Stubbed E2E)

## Context
- Web SPA matches locally (design) and calls server to join selected room
- No raw intent is stored server-side; plaintext seen in transit to server in MVP

## Steps
1. User enters intent and presses Join
2. Client computes local candidates vs Atlas (design-only in MVP docs)
3. Client selects roomId and calls `POST /v1/intent/join` (MVP: directly `POST /v1/rooms/{id}/join`)
4. Server creates/attaches membership (ephemeral), returns session mask and limits
5. Client navigates to room and begins pulling messages

## Errors
- Room full → return 409 with alternates hint
- Rate limited → 429 with backoff headers
- Validation → 422 with field errors


