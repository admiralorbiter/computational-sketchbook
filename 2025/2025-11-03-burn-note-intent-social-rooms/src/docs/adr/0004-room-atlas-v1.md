# ADR 0004 — Room Atlas v1 Schema & Delivery (Design)

## Status
Accepted (Design for MVP)

## Context
Local matching needs a compact public dataset describing rooms.

## Decision
Define Atlas v1 with centroid (int8), activity, civility, language, freshness; deliver via CDN with signed manifest and hourly deltas.

## Consequences
- Enables on-device ranking and alternates
- Requires build job and signing keys (design-only for MVP)


