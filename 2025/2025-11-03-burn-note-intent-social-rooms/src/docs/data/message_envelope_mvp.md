# Data Model — Message Envelope (MVP, Plaintext)

## Fields
- id: string
- roomId: string
- senderMask: string (per session)
- type: enum (`text`, `media`, `whisper`)
- body: string (plaintext MVP)
- media: optional { url, type, size }
- createdAt: timestamp
- tombstoned: boolean
- whisperId: optional string

## Limits (MVP)
- body size ≤ 4 KB
- media disabled or capped by size/type whitelist


