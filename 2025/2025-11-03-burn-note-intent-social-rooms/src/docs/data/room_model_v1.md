# Data Model — Room v1 (MVP)

## Fields
- id: string (opaque)
- title: string
- language: string (ISO 639-1)
- policyFlags: bitset (sensitive, curated, slow-mode)
- createdAt: timestamp
- updatedAt: timestamp

## Lifecycle (MVP)
- Seeded rooms created by admins
- Split/Merge deferred (design documented for later)


