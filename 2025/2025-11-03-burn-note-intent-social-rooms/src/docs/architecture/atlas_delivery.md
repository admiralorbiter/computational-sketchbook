# Room Atlas — Delivery & Verification (Design)

## Delivery
- Hosted via CDN with cache headers; client fetches manifest first
- Delta updates hourly; full refresh daily

## Client Flow
1. GET manifest → verify signature
2. Download required shards/deltas
3. Verify content hashes in manifest
4. Build local index for cosine search

## Privacy
- Built from aggregated metrics; no user-level events
- No intents sent; local-only processing


