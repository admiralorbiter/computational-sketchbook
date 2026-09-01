# ADR 0002 — Stubbed E2E for MVP (TLS Only)

## Status
Accepted (Nov 2025)

## Context
E2E (MLS/DR) is core to vision but costly to implement upfront. We need to validate UX flows first.

## Decision
Ship MVP with plaintext over TLS and server-side storage; document caveats; restrict to internal testing.

## Consequences
- Rapid delivery of features; simpler debugging
- Elevated privacy risk → strict retention, minimal logging, internal-only
- Clear migration plan to MLS/DR before external release


