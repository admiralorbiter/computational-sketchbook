# Burn Note — Intent-Driven Ephemeral Social Network (November 2025)

> **Category:** `[SKETCHBOOK EXPERIMENT / EPHEMERAL SOCIAL SYSTEMS & RUST BACKEND]`  
> **Date:** November 3–4, 2025  
> **Stack:** Rust (Axum, Tokio, SQLx, SQLite, WebSockets, Serde)  
> **Original Origin:** `admiralorbiter/burn_note`  

---

## 1. Core Systems & Empirical Thesis

*Burn Note* is a 25-hour functional MVP investigating **intent-driven ephemeral social structures** rather than persistent social graphs:

> *"Say it once → find your people → leave no trail."*

```text
TRADITIONAL SOCIAL GRAPH:
Identity (Profile) ──► Follows / Friends ──► Static Communities ──► Content

BURN NOTE PARADIGM:
Present Intent ("I am interested in X") ──► Semantic Match ──► Temporary Room ──► Interaction ──► Burn / Disappear
```

---

## 2. Architecture & Implementation Status

- **BUILT & EXECUTABLE:**
  - **Rust Multi-Crate Workspace:** `apps/web` (Axum server, REST API, WebSocket subscriptions), `apps/cli`, `crates/core` (ephemeral masks like `Fox-7291`, room models, whisper states), `crates/storage` (SQLite repositories with comprehensive test coverage), `crates/bus` (broadcast event bus).
  - **Real-Time Communication:** WebSockets distributing live messages, posts, highlights, and whisper state transitions (`Pending` $	o$ `Active` $	o$ `Ended`) with auto-reconnect backoff.
  - **Keyword Intent Matcher:** Server-side tokenization matching user intents to active room topics.
- **ASPIRATIONAL / UNIMPLEMENTED:**
  - On-device embedding generation, MLS group encryption, Signal-style Double Ratchet whispers, OHTTP IP blinding, and blind-signed tokens.

---

## 3. The Critical Privacy Architecture Lesson

> [!WARNING]
> **Dataflow Violations in Early Prototypes:**  
> The project highlighted a fundamental systems lesson: **Privacy cannot be bolted on as an afterthought if the application dataflow inherently persists sensitive traces.** In the MVP, unmatched raw intents were saved directly into the SQLite database as the room description (`"Room for discussing: {intent}"`), violating the "raw intents never persist" design guarantee.
