# Threat Model — MVP Scope (Plaintext Server)

## Assets
- User content (messages, whispers)
- Session masks and membership
- Room Atlas (public)

## Adversaries
- Abusive users; spam networks
- Passive network observers (mitigated by TLS)
- Compromised app server or engineer account

## Attack Surfaces
- API endpoints for join/messaging/whispers
- Storage of plaintext content
- Logs and admin tooling

## Mitigations (MVP)
- TLS everywhere; CORS restrictions; minimal logs
- Short retention; no intents stored; least-privilege DB access
- Rate limits, slow-mode, reporting and moderation workflow

## Residual Risks
- Server compromise could expose plaintext content
- Traffic analysis at network edges

## Roadmap Mitigations
- E2E (MLS/DR), OHTTP relays, consented report enclave


