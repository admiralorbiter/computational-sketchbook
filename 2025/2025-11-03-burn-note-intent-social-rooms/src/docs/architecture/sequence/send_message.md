# Sequence — Send Message to Room (MVP, Plaintext)

## Context
- MVP uses plaintext over TLS; server stores message body; retention limited per policy

## Steps
1. User types message and presses Send
2. Client assigns a temporary local id and posts to `POST /v1/messages`
3. Server validates size/limits, persists, enqueues fan-out; returns canonical id and timestamps
4. Client replaces optimistic bubble id with canonical id
5. Other clients receive via long-poll/WebSocket (MVP: long-poll)

## Errors
- 413 Payload too large
- 429 Rate limited (slow-mode or per-session limits)
- 400/422 Validation errors


