# API Standards (MVP Contracts — Names/Semantics Only)

## Versioning
- Prefix with `/v1/` for all endpoints
- Breaking changes require v-bump and feature flag

## Resource Naming & HTTP
- Plural nouns: `/v1/rooms`, `/v1/messages`, `/v1/whispers`
- Use standard verbs: GET (fetch), POST (create/action), DELETE (remove)

## IDs & Cursors
- IDs are opaque strings; cursors are opaque, URL-safe

## Pagination
- `limit` (max 100)
- `after` cursor for forward pagination
- Response includes `next` cursor if more available

## Filtering
- Query params: `roomId`, `type`, `since`, `after`

## Errors
- JSON error object: `{ code, message, details? }`
- Use 4xx for client errors; 5xx for server errors
- Common: 400/401/403/404/409/413/422/429

## Idempotency
- Accept `Idempotency-Key` for POST where safe; store for TTL to dedupe

## Rate Limiting
- Return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After` when applicable

## Headers & Security (MVP)
- TLS required; CORS restricted to dev origins
- No intents stored; logs scrubbed


