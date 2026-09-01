# High-Level Architecture — Burn Note MVP (Web SPA, Stubbed E2E)

## Context
- Client: Web SPA (desktop + mobile web)
- Backend: Axum-based API (`apps/web`)
- Crypto: TLS-only for MVP; server sees plaintext content for internal testing
- Future: Migrate to E2E (MLS for rooms, Double Ratchet for whispers), OHTTP relays

## Components
- Web SPA: intent entry, local ranking UX (design), room UI (Live, Posts, Highlights, Resources), whispers
- API Server: rooms directory, messaging endpoints, highlights listing, reporting, rate limits
- **WebSocket Server**: Real-time event distribution via WebSocket connections
  - Connection management with room and whisper subscriptions
  - Event bus integration for pub/sub event forwarding
  - Client-side WebSocket client with auto-reconnect and heartbeat
- Storage: append-only envelopes (plaintext MVP), object store for media (placeholder), KV for room metadata
- Batch: Atlas builder job (design-only for MVP)

## Key Flows (overview)
- Intent → Match → Join
- Send/Receive Message (room) - **Real-time via WebSocket**
- Start Whisper → Consent → Exchange messages → Expiry - **Real-time via WebSocket**
- Member Join/Left - **Real-time via WebSocket**
- Post Created/Replied - **Real-time via WebSocket**
- Report → Moderation action

## Real-time Infrastructure
- **WebSocket Endpoint**: `GET /v1/ws?session_id={id}` - Upgrades HTTP connection to WebSocket
- **Event Bus**: In-process publish-subscribe system (`crates/bus`) for event distribution
- **Connection Manager**: Tracks active WebSocket connections and their subscriptions (rooms, whispers)
- **Event Types**: `message.created`, `whisper.*`, `post.*`, `member.*` events published from handlers and forwarded to subscribed clients
- **Client Subscription**: Clients subscribe to rooms and whispers via WebSocket messages
- **Auto-reconnect**: Client-side WebSocket client handles reconnection with exponential backoff

## Data (MVP, plaintext)
- Room: id, title, language, policy flags
- Message: id, roomId, senderMask, type, body, createdAt, tombstoned
- Whisper: id, participant masks, state, expiry
- Highlight: id, roomId, reference, curator

## Non-Functional (targets)
- Perf: P50 join ≤ 2.0s; P95 ≤ 4.0s
- Availability: 99.9% for join/messaging (target)
- Privacy (MVP): minimal logs, short retention; no intents stored; migration plan to E2E documented

## Migration to E2E (outline)
1. Introduce MLS client and group management service (server relays Welcome/Commit only)
2. Whispers upgrade to X3DH + Double Ratchet; store only ciphertext and metadata buckets
3. Add OHTTP relay to hide client IP from app server
4. Rotate storage to ciphertext-at-rest; add consented report enclave

## Diagrams
- See sequence docs in `architecture/sequence/`


