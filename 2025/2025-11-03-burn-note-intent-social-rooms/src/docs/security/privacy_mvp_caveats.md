# Privacy Caveats — MVP (Plaintext, Internal Testing Only)

## Context
MVP ships faster with plaintext on the server, protected by TLS in transit. This is for internal testing only.

## Data Classification (MVP)
- User content (messages, whispers): Sensitive (Confidential)
- Intents: Sensitive; DO NOT persist
- Metadata (timestamps, roomId, size): Internal

## Collection & Storage (MVP)
- Store message/plaintext for rooms and whispers with short retention
- Do not store raw intents; keep local only
- Avoid IP logging beyond web server defaults; disable/rotate frequently in dev

## Retention (MVP)
- Rooms: 30–90 days configurable; default 30
- Whispers: 24h default expiry
- Logs: ≤ 7 days; scrub message bodies

## Access Controls
- Limit database access to engineers on the project; audit access
- No direct production user access until E2E lands

## Migration Plan to E2E
1. Introduce MLS for rooms; server stores ciphertext envelopes only
2. Adopt X3DH + Double Ratchet for whispers
3. Add OHTTP relays; stop seeing client IP at app server
4. Update reporting to consented plaintext uploads to a TEE enclave

## Disclosures (Internal)
- Clear banner in dev builds: “MVP stores plaintext. For internal testing only.”


