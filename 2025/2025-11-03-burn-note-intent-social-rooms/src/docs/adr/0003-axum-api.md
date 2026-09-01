# ADR 0003 — Axum-based API Server

## Status
Accepted (Nov 2025)

## Context
Rust ecosystem offers performant, safe web backends. Repo already includes `apps/web` with Axum.

## Decision
Use Axum + Tokio for the MVP API server.

## Consequences
- Strong async performance; good ecosystem for tracing and testing
- Team alignment with Rust tooling; CLI reuse for utilities


