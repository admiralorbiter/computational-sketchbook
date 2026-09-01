# Anonymous Rate Limiting — MVP (Design)

## Goal
Throttle abuse without identifying users; provide unlinkability caveats for MVP.

## MVP Token Design
- Per-session HMAC token issued on join; includes coarse time bucket
- Token presented on rate-limited actions (join, post, whisper start)
- Server validates HMAC; stores short-lived spend record

## Quotas
- Join: 1 per minute, burst 3
- Post: 10 per minute, burst 20 (room-level slow-mode can override)
- Whisper start: 3 per hour

## Caveats
- Tokens are linkable within session (MVP). Document and restrict to internal.

## Migration
- Move to VOPRF-based blind tokens; separate issuer and verifier; wallet of unlinkable tokens


