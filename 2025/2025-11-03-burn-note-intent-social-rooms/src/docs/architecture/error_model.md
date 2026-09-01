# Error Model — API (MVP)

## Response Shape
```json
{ "code": "string", "message": "human readable", "details": {"field": "..."} }
```

## Common Codes
- validation_failed (422)
- rate_limited (429)
- room_full (409)
- unauthorized (401)
- forbidden (403)
- not_found (404)

## Retries
- Use exponential backoff with jitter for 5xx; do not retry 4xx except 409/429 with headers


