# Agent Context Summary

**Last Updated:** 2025-01-XX
**Purpose:** Quick onboarding for agents joining the project mid-sprint

---

## Project Overview

**Burn Note** - Anonymous topic-based chat rooms (MVP)

- **Status:** Whispers feature complete - rooms, messaging, matching, posts, highlights, resources, and whispers all working
- **Tech Stack:** Rust (Axum), Web SPA (functional MVP)
- **MVP Constraint:** Plaintext server-side (internal testing only), E2E planned post-MVP

---

## Key Architectural Decisions

1. **Web SPA Only** (ADR 0001) - No native apps in MVP
2. **Stubbed E2E** (ADR 0002) - TLS only, server sees plaintext
3. **Axum Backend** (ADR 0003) - Rust async web framework
4. **Room Atlas v1** (ADR 0004) - Public signed dataset for matching

See `docs/adr/` for full details.

---

## Codebase Structure

```
burn_note/
├── apps/
│   ├── web/          # Axum API server (MVP backend)
│   └── cli/          # CLI utilities (placeholder)
├── crates/
│   ├── core/         # Domain types & logic
│   ├── storage/      # Database & blob storage
│   ├── index/        # Vector search (for Atlas matching)
│   ├── bus/          # In-process pub/sub
│   └── matching/     # Matching strategies (future-ready)
└── docs/             # All documentation
    ├── product/      # PRD, UX specs
    ├── architecture/ # HLD, sequences
    ├── algorithms/   # Matching algorithms & scalable strategies
    ├── api/          # API contracts
    ├── adr/          # Architecture Decision Records
    └── work/         # This tracking system
```

---

## Current Implementation Status

### ✅ Complete
- **Documentation:** Full sprint plan, PRD, HLD, API contracts, policies
- **Project Scaffolding:** Cargo workspace, basic Axum server skeleton
- **Database Layer:** SQLite storage with repositories (Room, Message, Session, RateLimit)
- **Domain Models:** Core domain types implemented (Room, Message, UserSession, PolicyFlags, MessageType)
- **API Handlers:** 
  - Rooms and Messages (`/v1/rooms`, `/v1/rooms/:id/join`, `/v1/messages`)
  - Posts (`/v1/posts`, `/v1/posts/:id/replies`)
  - Highlights (`/v1/rooms/:room_id/highlights`, `/v1/highlights/:id`)
  - Resources (`/v1/rooms/:room_id/resources`, `/v1/resources/:id`)
  - Whispers (`/v1/whispers`, `/v1/whispers/:id/accept`, `/v1/whispers/:id/decline`, `/v1/whispers/:id`, `/v1/whispers/:id/extend`)
  - Active Members (`/v1/rooms/:room_id/members`)
  - Intent matching (`/v1/intent/match`) with room creation
  - Room Atlas stub (`/v1/atlas`)
  - Session management (`/v1/sessions/:id` DELETE for burn session)
- **Matching System:** Intent-based keyword matching with score thresholds, qualitative UX, automatic room creation
- **Session Management:** Session expiration, burn session endpoint, session validation middleware
- **Rate Limiting:** RateLimitRepository with join/post/highlight/resource rate limiting foundation
- **UI:** Functional HTML/JavaScript single-page app with tab navigation (Live/Posts/Highlights/Resources/Whispers)
- **Posts Feature:** Threaded posts with replies, two-level threading, create post form, reply functionality
- **Highlights Feature:** Curated digest entries with auto-highlighting (posts with 5+ replies), "Skim last 24h" filter
- **Resources Feature:** Curated links with categories, full CRUD operations, URL validation, category filtering
- **Whispers Feature:** 1-on-1 ephemeral messaging with state management (Pending/Active/Declined/Ended), auto-expiry, extend/end operations
- **WebSocket Real-time Infrastructure:** Real-time updates via WebSocket for messages, whispers, members, posts
  - WebSocket endpoint: `GET /v1/ws?session_id={id}`
  - Connection manager tracks subscriptions to rooms and whispers
  - Event bus forwards events to subscribed clients
  - Client-side WebSocket client with auto-reconnect
- **Room Metadata:** Tags, description, activity_score, member_count fields added to Room model
- **Database Connection:** Windows SQLite path handling resolved
- **Schema Execution:** Database initialization working correctly, tables created on startup with migrations
- **MVP Status:** End-to-end functionality verified - rooms, messaging, matching, posts, whispers, and real-time updates all operational

### 📋 Ready to Start
- **Recommended: Sprint 4 - Safety/Moderation**
  - Policies defined, all dependencies met
  - Core foundation (rooms, messaging, sessions, posts, highlights, resources, whispers) is complete
  - Would add reporting system, tombstoning, moderation actions
  - Estimated: Medium effort
- **Option: Matching Refinements**
  - Test and refine room creation logic
  - Add intent refinement suggestions ("Did you mean...?")
  - Improve title generation (currently simple keyword extraction)
  - Add room merging suggestions for near-duplicates
  - Estimated: Low-Medium effort
- **Option: Sprint 4 - Safety/Moderation**
  - Implement reporting system, tombstoning, moderation actions
  - Estimated: Medium effort
- **Option: Sprint 5 - Rate Limiting Enhancements**
  - Enhance existing rate limiting foundation
  - Add per-session rate limiting
  - Add rate limit headers in responses
  - Estimated: Low-Medium effort
- **Sprint 6:** Observability & launch prep

### 📋 Documentation Index
- Start here: `docs/README.md`
- PRD: `docs/product/prd_burn_note_mvp.md`
- Architecture: `docs/architecture/HLD.md`
- API Standards: `docs/api/standards.md`

---

## Development Workflow

### Local Setup
```bash
# Start API server
cargo run -p web

# Health check
curl http://localhost:8080/healthz

# ⚠️ AGENTS: DO NOT run cargo test
# Instead, verify tests exist - see docs/testing/TEST_STATUS.md

# See: docs/runbooks/local_env.md
```

### Code Standards
- Follow Rust conventions (`cargo fmt`, `cargo clippy`)
- Write ADRs for significant decisions
- Update relevant docs when making changes
- See: `docs/process/contributing.md`
- **Agent Guidelines:** `docs/process/AGENT_GUIDELINES.md` - Quick reference
- **Philosophy:** `docs/process/PHILOSOPHY.md` - Development principles

---

## Important Constraints & Caveats

### Privacy (MVP)
- **Server sees plaintext** - This is for internal testing only
- Clear migration path to E2E documented
- See: `docs/security/privacy_mvp_caveats.md`

### Performance Targets
- Join P50 ≤ 2.0s, P95 ≤ 4.0s
- See: `docs/observability/metrics.md`

### API Contracts
- All endpoints use `/v1/` prefix
- Follow standards in `docs/api/standards.md`
- Names/semantics defined, implementation TBD

---

## Common Gotchas

1. **No E2E in MVP** - Don't implement MLS/DR yet, just document the path
2. **Plaintext Storage** - Acceptable for MVP internal testing, but document clearly
3. **Matching Thresholds** - Matching uses 35% minimum threshold to filter low-quality matches. Rooms below this are not shown. Rooms with <60% score trigger automatic room creation.
4. **Room Creation** - Rooms are auto-created when no good match (>60%) exists. Title is generated from keywords (simple extraction, future: LLM-based).
5. **Atlas Endpoint** - GET `/v1/atlas` currently returns all rooms (stub). Future v2 will be client-side with compressed embeddings for privacy-preserving matching.
6. **Web SPA Functional** - Full MVP UI working with intent entry, room matching, qualitative badges, session controls, tab navigation, and messaging
7. **Schema Execution Working** - The `init()` method successfully creates all tables on startup, including metadata columns via migration
8. **Session Middleware** - Session validation middleware extracts `X-Session-Id` header and validates session exists and hasn't expired. Used by burn session endpoint.
9. **Posts Feature** - Threaded posts with two-level replies (top-level posts and direct replies only). Posts use `MessageType::Post` and are filtered separately from Live chat. Fully testable end-to-end.
10. **Tab Navigation** - Room view has tabs: Live (chat), Posts (threaded Q&A), Highlights (curated digest), Resources (curated links). All tabs are complete and functional.
11. **Database Migrations** - Index creation for new columns must be in migration functions, not schema.sql, to avoid errors when column doesn't exist yet in existing databases.
12. **Whispers Feature** - Full 1-on-1 ephemeral messaging with state management. Chat view automatically opens after accepting whisper. Whisper messages use `MessageType::Whisper` and are filtered from Live tab. Rate limiting: 10 messages per 60s per whisper.
13. **Active Members** - Uses sessions table as source of truth with API endpoint `/v1/rooms/:room_id/members`. Frontend polls every 5 seconds when Live tab is active. Message-based fallback for backward compatibility.
14. **Whisper States** - Four states: Pending (waiting for accept), Active (can send messages), Declined (recipient rejected), Ended (either party ended). State transitions validated in domain model.
15. **Whisper Expiry** - Default 24 hour TTL, can be extended via API. Background task expires whispers every 5 minutes. Expired whispers cannot be accepted or used for messaging.
16. **WebSocket Real-time** - All major features use WebSocket for real-time updates (messages, whispers, members, posts). Clients subscribe to rooms and whispers to receive events. Connection manager handles subscription lifecycle. Event bus (`crates/bus`) publishes events from handlers, global forwarding task distributes to WebSocket clients.
17. **WebSocket Client** - Client-side `WebSocketClient` class handles connection, auto-reconnect with exponential backoff, heartbeat, and subscription management. Automatically subscribes to current room on connect, subscribes to whispers when chat is opened.

---

## Testing Strategy

- **⚠️ IMPORTANT:** Agents should NEVER run `cargo test` - see `docs/testing/TEST_STATUS.md`
- Unit tests for core logic (verify they exist, don't run them)
- Integration tests for API endpoints (planned)
- Performance tests per `docs/testing/perf_test_plan.md`
- See: `docs/testing/TEST_STATUS.md` for current test coverage and guidelines

---

## Handoff Process

1. Update `docs/work/SPRINT_STATUS.md` with current progress
2. Create handoff using `docs/work/HANDOFF_TEMPLATE.md`
3. Update this file's "Last Updated" timestamp
4. Document any new gotchas or patterns

---

## Getting Help

- **Start here:** `docs/process/AGENT_GUIDELINES.md` - Quick reference for agents
- **Philosophy:** `docs/process/PHILOSOPHY.md` - Core principles and mindset
- **ADRs:** `docs/adr/` - Architectural decisions
- **Specs:** `docs/product/`, `docs/architecture/` - Product and architecture docs
- **Runbooks:** `docs/runbooks/` - Operational guides
- **Status:** `docs/work/SPRINT_STATUS.md` - Current progress

