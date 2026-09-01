# Sequence — Pull Messages (MVP)

## Context
- MVP uses long-polling with pagination cursors

## Steps
1. Client calls `GET /v1/messages?roomId=...&after=cursor`
2. Server returns up to N messages and a next cursor
3. Client appends to Live view; deduplicates by id
4. If no messages within T seconds, server returns empty with same cursor
5. Client repeats after small delay (backoff on errors)

## Errors
- 401 if membership invalid
- 429 if pull rate too high


