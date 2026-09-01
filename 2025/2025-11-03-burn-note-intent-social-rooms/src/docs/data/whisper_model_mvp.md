# Data Model — Whisper (MVP)

## Fields
- id: string
- participantA: sessionMask
- participantB: sessionMask
- state: enum (`pending`, `active`, `ended`, `expired`)
- expiresAt: timestamp
- createdAt / updatedAt

## Behavior
- Auto-expire after default 24h if not extended
- Deletion: tombstone messages; retain minimal audit (internal)


