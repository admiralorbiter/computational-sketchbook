# API — Rooms (MVP)

## POST /v1/rooms/{id}/join
Join a room as an ephemeral member.

### Response
- 200: { sessionMask, limits }
- 409: room full (include alternates hint)

## GET /v1/rooms/{id}/highlights
List curated highlights (plaintext MVP).


