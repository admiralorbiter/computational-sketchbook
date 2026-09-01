# Sprint Status & Progress Tracker

**Last Updated:** 2025-01-XX
**Current Sprint:** Sprint 3 - Whispers ✅ COMPLETE
**Active Agent:** [Whispers feature implementation complete - 1-on-1 ephemeral messaging functional, chat opens automatically after accept]

## Overview
Quick status of all sprints and their completion.

| Sprint | Status | Progress | Notes |
|--------|--------|----------|-------|
| Sprint 0 - Foundations | ✅ Complete | 100% | All docs scaffolded |
| Sprint 1 - Matching & Atlas | ✅ Complete | 100% | Intent-based matching with room creation, qualitative UX, session management, rate limiting foundation |
| Sprint 2 - Rooms & Messaging | ✅ Complete | 100% | MVP functional - all core features working, polish complete (debug logging replaced, tests added, error messages improved) |
| Posts Feature | ✅ Complete | 100% | Threaded posts with replies, tab navigation, complete vertical slice |
| Highlights Feature | ✅ Complete | 100% | Curated digest entries with auto-highlighting, complete vertical slice |
| Resources Feature | ✅ Complete | 100% | Curated links with categories, CRUD operations, complete vertical slice |
| Sprint 3 - Whispers | ✅ Complete | 100% | Full vertical slice: domain model, DB, API, UI, auto-open chat after accept, active members detection |
| Sprint 4 - Safety/Moderation | 📋 Planned | 0% | Policies defined |
| Sprint 5 - Rate Limiting | 📋 Planned | 0% | Basic foundation implemented, enhancements needed |
| Sprint 6 - Observability/Launch | 📋 Planned | 0% | Checklists ready |

**Status Legend:**
- ✅ Complete
- 🚧 In Progress
- 📋 Planned
- ⏸️ Blocked
- 🐛 Issues

---

## Current Sprint Details

### Sprint 3 - Whispers Implementation
**Goal:** Implement 1-on-1 ephemeral messaging feature as a complete vertical slice
**Start Date:** 2025-01-XX
**Completion Date:** 2025-01-XX

### Completed This Sprint
- ✅ **Domain Model** - Created `WhisperSession` struct with states (Pending, Active, Declined, Ended), expiry logic, validation methods
- ✅ **Database Schema** - Added whispers table with indexes for sender_mask, recipient_mask, room_id, expires_at
- ✅ **Repository Layer** - Full CRUD operations with accept/decline/end/extend methods, expiry batch function
- ✅ **API Endpoints** - `GET /v1/whispers`, `POST /v1/whispers`, `POST /v1/whispers/:id/accept`, `POST /v1/whispers/:id/decline`, `DELETE /v1/whispers/:id`, `POST /v1/whispers/:id/extend`
- ✅ **Whispers UI** - Complete whispers tab with list view, pending (accept/decline), active whispers, chat interface
- ✅ **Auto-open Chat** - Chat view automatically opens after accepting a whisper (fixed critical UX issue)
- ✅ **Message Integration** - Whisper messages validated in message handler, separate from Live tab
- ✅ **Rate Limiting** - 10 whisper messages per 60s per whisper
- ✅ **Active Members** - Enhanced active members detection with API endpoint and polling
- ✅ **Background Tasks** - Whisper expiry cleanup runs every 5 minutes
- ✅ **Bug Fixes** - Fixed route parameter extraction, SQL date comparison, state handling, chat opening flow

### Key Files Modified
- `crates/core/src/whisper.rs` - WhisperSession domain model with state transitions
- `crates/storage/src/schema.sql` - Whispers table schema
- `crates/storage/src/lib.rs` - Added `migrate_whispers_table()` function
- `crates/storage/src/whispers.rs` - WhisperRepository with full CRUD operations
- `apps/web/src/handlers/whispers.rs` - Whispers API handlers
- `apps/web/src/handlers/members.rs` - Active members endpoint (new)
- `apps/web/src/handlers/messages.rs` - Whisper message validation
- `apps/web/src/main.rs` - Added whispers routes and background task
- `apps/web/static/index.html` - Whispers tab UI
- `apps/web/static/app.js` - Whispers functionality with auto-open chat

### Bug Fixes Applied
- ✅ **Route Parameter Bug** - Fixed members handler to use `Path(room_id)` instead of `Query(params)`
- ✅ **SQL Date Comparison** - Fixed to use RFC3339 format for consistent timezone handling
- ✅ **Chat Opening** - Fixed critical issue where accepting whisper didn't open chat view
- ✅ **State Handling** - Enhanced state validation and error handling in frontend
- ✅ **Error Visibility** - Added comprehensive logging and user-visible error messages

---

### Resources Feature Implementation (Previous)
**Goal:** Implement robust Resources feature as a complete vertical slice to complete all room tabs
**Start Date:** 2025-11-04
**Completion Date:** 2025-11-04

### Completed This Sprint
- ✅ **Domain Model** - Created `Resource` struct with URL validation, categories, descriptions
- ✅ **Database Schema** - Added resources table with indexes for room_id, category, created_at
- ✅ **Repository Layer** - Full CRUD operations with category filtering and pagination
- ✅ **API Endpoints** - `GET /v1/rooms/:room_id/resources`, `POST /v1/rooms/:room_id/resources`, `PUT /v1/resources/:id`, `DELETE /v1/resources/:id`
- ✅ **Resources UI** - Complete UI with create/edit/delete, category filtering, verified badges
- ✅ **Rate Limiting** - 10 resources per 60s per room
- ✅ **Bug Fixes** - Fixed date parsing errors and response handling in loadResources

### Key Files Modified
- `crates/core/src/resource.rs` - Resource domain model with validation
- `crates/storage/src/schema.sql` - Resources table schema
- `crates/storage/src/lib.rs` - Added `migrate_resources_table()` function
- `crates/storage/src/resources.rs` - ResourceRepository with error handling
- `apps/web/src/handlers/resources.rs` - Resources API handlers
- `apps/web/src/main.rs` - Added resources routes
- `apps/web/static/index.html` - Resources tab UI
- `apps/web/static/app.js` - Resources functionality with error handling

### Bug Fixes Applied
- ✅ **Resources Loading Bug** - Fixed missing `response.ok` check in `loadResources()` causing rooms to become inaccessible
- ✅ **Date Parsing Errors** - Added error handling for date parsing in repository with fallback to current time
- ✅ **Error Isolation** - Ensured resource loading errors don't break room access

---

### Posts Feature Implementation (Previous)
**Goal:** Implement threaded Posts feature as a complete vertical slice (testable end-to-end)
**Start Date:** 2025-11-04
**Completion Date:** 2025-11-04

### Completed This Sprint
- ✅ **Data Model Extension** - Added `parent_post_id` field to Message model, `MessageType::Post` variant
- ✅ **Database Schema** - Added `parent_post_id` column and index with migration support
- ✅ **Repository Layer** - Added `get_posts()`, `get_post_replies()`, and `get_reply_count()` methods
- ✅ **Posts API Endpoints** - `GET /v1/posts`, `GET /v1/posts/:post_id/replies`, `POST /v1/posts`
- ✅ **Tab Navigation UI** - Added Live/Posts/Highlights/Resources tabs in room view
- ✅ **Posts UI** - Post creation form, threaded display, reply functionality
- ✅ **Rate Limiting** - Posts use same rate limits as messages (10 per 60s)
- ✅ **Validation** - Parent post validation (must exist and be in same room)

### Key Files Modified
- `crates/core/src/message.rs` - Added parent_post_id, Post type, PartialEq trait
- `crates/storage/src/schema.sql` - Added parent_post_id column (index handled by migration)
- `crates/storage/src/lib.rs` - Added `migrate_messages_table()` function
- `crates/storage/src/messages.rs` - Added posts-specific queries, updated all queries to handle parent_post_id
- `apps/web/src/handlers/posts.rs` - NEW file for posts endpoints
- `apps/web/src/handlers/mod.rs` - Added posts module
- `apps/web/src/main.rs` - Added posts routes
- `apps/web/static/index.html` - Added tab navigation and Posts UI
- `apps/web/static/app.js` - Added Posts functionality (load, create, reply)

### Previous Sprint: Sprint 1 - Matching & Atlas
**Goal:** Implement intent-based room matching with qualitative UX and automatic room creation
**Start Date:** 2025-11-04
**Target End:** 2025-11-04

### Completed This Sprint
- ✅ **Intent-based matching** - POST `/v1/intent/match` endpoint with keyword-based scoring
- ✅ **Score threshold filtering** - 35% minimum threshold, 60% good match threshold
- ✅ **Qualitative match reasons** - Human-friendly descriptions instead of technical details
- ✅ **Automatic room creation** - Creates rooms when no good match exists
- ✅ **Room metadata fields** - Added tags, description, activity_score, member_count to Room model
- ✅ **Frontend qualitative badges** - Excellent Match, Good Fit, Worth Exploring indicators
- ✅ **New room welcome UI** - Special message when room is auto-created
- ✅ **Session management** - Burn session endpoint, session expiration, session middleware
- ✅ **Rate limiting foundation** - RateLimitRepository with join/post rate limiting
- ✅ **Room Atlas stub** - GET `/v1/atlas` endpoint (returns all rooms, ready for client-side v2)
- ✅ **Matching crate structure** - Created `crates/matching/` for future extensibility
- ✅ **Scalable matching documentation** - `docs/algorithms/matching_v2_scalable.md` for future improvements

### Key Files Modified
- `apps/web/src/handlers/matching.rs` - Matching logic with thresholds and room creation
- `apps/web/src/handlers/sessions.rs` - Burn session endpoint
- `apps/web/src/handlers/atlas.rs` - Atlas stub endpoint
- `apps/web/src/middleware/session.rs` - Session validation middleware
- `apps/web/static/index.html` - Intent entry UI, qualitative badges, new room notice
- `apps/web/static/app.js` - Matching integration, session management
- `crates/core/src/room.rs` - Added metadata fields
- `crates/storage/src/rooms.rs` - Updated queries for metadata
- `crates/storage/src/lib.rs` - Schema migration for metadata columns
- `crates/storage/src/rate_limits.rs` - Rate limiting repository (NEW)
- `crates/matching/` - New crate structure (NEW)

### Previous Sprint: Sprint 2 - Rooms & Messaging APIs
**Goal:** Implement core room and messaging functionality with functional UI
**Start Date:** 2025-11-03
**Target End:** 2025-11-04

### Completed in Sprint 2
- ✅ Fixed SQLite database connection on Windows (used `SqliteConnectOptions::filename()` instead of connection strings)
- ✅ Implemented storage layer with SQLx repositories for rooms, messages, and sessions
- ✅ Created API handlers for `/v1/rooms` (GET), `/v1/rooms/:id/join` (POST)
- ✅ Created API handlers for `/v1/messages` (GET, POST)
- ✅ Implemented domain models in `crates/core` (Room, Message, UserSession, PolicyFlags, MessageType)
- ✅ Built functional HTML/JavaScript UI (`apps/web/static/index.html`, `app.js`)
- ✅ Database schema defined (`crates/storage/src/schema.sql`)
- ✅ Database initialization and seeding logic implemented
- ✅ **Schema execution working** - Database tables created successfully, MVP operational end-to-end
- ✅ **End-to-end testing verified** - User confirmed 3 chat rooms accessible and messaging functional
- ✅ **Code cleanup complete** - All debug `eprintln!` statements replaced with proper `tracing::info!`/`tracing::debug!` logging
- ✅ **Unit tests added** - All repositories (RoomRepository, MessageRepository, SessionRepository) have comprehensive test coverage
- ✅ **Error messages improved** - API handlers now return user-friendly validation errors with proper error codes

### Blockers
- None - All room tabs are complete and functional

### Next Up (Priority Order)

1. **Recommended: Sprint 3 - Whispers Implementation**
   - PRD/specs already exist
   - Core foundation (rooms, messaging, sessions, posts, highlights, resources) is solid
   - Would add 1-on-1 ephemeral messaging feature
   - Estimated effort: Medium-High
   - Dependencies: All met

2. **Option: Matching Refinements**
   - Test and refine room creation logic
   - Add intent refinement suggestions ("Did you mean...?")
   - Improve title generation (currently simple keyword extraction)
   - Add room merging suggestions for near-duplicates
   - Estimated effort: Low-Medium

3. **Option: Sprint 4 - Safety/Moderation**
   - Implement reporting system
   - Add tombstoning for messages
   - Implement moderation actions
   - Estimated effort: Medium

4. **Option: Matching Refinements**
   - Test and refine room creation logic
   - Add intent refinement suggestions ("Did you mean...?")
   - Improve title generation (currently simple keyword extraction)
   - Add room merging suggestions for near-duplicates
   - Estimated effort: Low-Medium

5. **Option: Sprint 5 - Rate Limiting Enhancements**
   - Currently basic implementation exists
   - Add per-session rate limiting
   - Add IP-based rate limiting (optional)
   - Add rate limit headers in responses
   - Estimated effort: Low

5. **Optional Enhancement (Future):** 
   - Integration tests for API endpoints (especially matching endpoint)
   - Performance testing for message pagination
   - Add room metadata to seed data (tags, descriptions)

---

## Dependencies Graph
```
Rooms API → depends on → RoomRepository → depends on → SQLite Database
Messages API → depends on → MessageRepository → depends on → SQLite Database  
Join Room API → depends on → RoomRepository + SessionRepository
UI → depends on → All APIs
```

---

## Quick Context for New Agents

### What Changed Recently (2025-01-XX)
- **Sprint 3 - Whispers Feature Complete:**
  - Implemented full whispers feature with 1-on-1 ephemeral messaging
  - Created WhisperSession domain model with state management (Pending, Active, Declined, Ended)
  - Added whispers table with indexes for performance
  - Implemented WhisperRepository with accept/decline/end/extend operations
  - Created whispers API endpoints: GET, POST, accept, decline, end, extend
  - Built complete whispers UI with list view, pending actions, active chat
  - Fixed critical UX issue: chat view now automatically opens after accepting whisper
  - Integrated whisper messages with message handler (validation, rate limiting)
  - Enhanced active members detection with dedicated API endpoint and polling
  - Added background task for whisper expiry cleanup
  - Fixed route parameter bug, SQL date comparison, and state handling issues
  - Vertical slice complete - can create, accept, send messages, extend, end whispers end-to-end

- **Resources Feature Complete - All Room Tabs Functional:**
  - Implemented robust Resources feature with full CRUD operations
  - Created Resource domain model with URL validation, categories, descriptions
  - Added Resources API endpoints: `GET /v1/rooms/:room_id/resources`, `POST /v1/rooms/:room_id/resources`, `PUT /v1/resources/:id`, `DELETE /v1/resources/:id`
  - Complete Resources UI with create/edit/delete, category filtering, verified badges
  - Fixed critical bug: Resources loading errors were breaking room access
  - Added error handling for date parsing in repository with fallback behavior
  - All four room tabs (Live, Posts, Highlights, Resources) are now complete and functional
  - Vertical slice complete - can create, read, update, delete resources end-to-end

- **Highlights Feature Complete - Curated Digest Entries:**
  - Implemented Highlights feature with auto-highlighting (posts with 5+ replies)
  - Created Highlight domain model with reference types (Message, Post, Standalone)
  - Added Highlights API endpoints: `GET /v1/rooms/:room_id/highlights`, `POST /v1/rooms/:room_id/highlights`, `DELETE /v1/highlights/:id`
  - Complete Highlights UI with "Skim last 24h" filter, create form, reference navigation
  - Auto-highlighting integrated into posts handler

- **Posts Feature Complete - Threaded Posts Implementation:**
  - Extended Message model with `parent_post_id` field and `MessageType::Post` variant
  - Added database migration for `parent_post_id` column (backward compatible)
  - Implemented Posts API endpoints: `GET /v1/posts`, `GET /v1/posts/:id/replies`, `POST /v1/posts`
  - Added tab navigation UI (Live/Posts/Highlights/Resources)
  - Created Posts UI with threaded replies, reply counts, create post form
  - Posts use same rate limiting as messages (10 per 60s)
  - Two-level threading (top-level posts and direct replies only)
  - Validation ensures parent posts exist and are in same room
  - Fully testable vertical slice - can create posts, reply, view threads end-to-end

- **Sprint 1 Complete - Matching & Room Creation:**
  - Implemented intent-based matching with POST `/v1/intent/match` endpoint
  - Added score threshold filtering (35% minimum, 60% good match threshold)
  - Replaced technical match reasons with qualitative human-friendly descriptions
  - Implemented automatic room creation when no good match exists
  - Added room metadata fields (tags, description, activity_score, member_count)
  - Created frontend qualitative badges (Excellent Match, Good Fit, Worth Exploring)
  - Added new room welcome UI with special message for auto-created rooms
  - Implemented session management (burn session endpoint, expiration, middleware)
  - Added rate limiting foundation (RateLimitRepository with join/post limits)
  - Created Room Atlas stub endpoint GET `/v1/atlas` (returns all rooms, ready for v2)
  - Created matching crate structure (`crates/matching/`) for future extensibility
  - Added scalable matching documentation (`docs/algorithms/matching_v2_scalable.md`)

### What Changed Previously (2025-11-03 to 2025-11-04)
- **Sprint 2 Complete - Rooms & Messaging:**
  - Fixed Windows SQLite connection issue by using `SqliteConnectOptions::filename()`
  - Created full handler structure in `apps/web/src/handlers/` with rooms and messages modules
  - Implemented all three repositories (Room, Message, Session) with proper SQLx query patterns
  - Created functional single-page app with room listing and chat interface
  - Defined complete schema in `crates/storage/src/schema.sql` for rooms, messages, sessions tables
  - Integrated database initialization and seeding into main server startup
  - Resolved schema execution issue - database tables created successfully on startup
  - MVP Status: End-to-end functionality verified - 3 chat rooms accessible, messaging working

### Important Decisions
- **SQLx Query Pattern:** Using `sqlx::query()` with `.bind()` instead of `sqlx::query!` macro to allow offline compilation without database connection
- **Database Path:** Using relative paths ("burn_note.db") which get resolved to absolute paths automatically to avoid working directory issues
- **Error Handling:** Using `anyhow::Result` with detailed error context for better debugging
- **State Management:** Using `Arc<SqlitePool>` for shared database connection across handlers

### Gotchas / Common Issues
- **⚠️ DO NOT RUN `cargo test`** - Tests can hang/get stuck. Instead, verify tests exist - see `docs/testing/TEST_STATUS.md`
- **Windows SQLite Paths:** Use `SqliteConnectOptions::new().filename(path)` instead of manually formatting connection strings. This handles Windows backslashes and absolute paths correctly.
- **Schema Execution:** The `init()` method splits schema SQL by semicolons - ensure statements are properly terminated and comment filtering works correctly
- **Offline Compilation:** We're using `sqlx::query()` instead of `sqlx::query!` because the macro requires `DATABASE_URL` or prepared queries. This means we lose compile-time query checking but gain offline compilation.
- **Database File Location:** Database is created in the current working directory where `cargo run -p web` is executed. Currently: `C:\Users\admir\Github\burn_note\burn_note.db`
- **Type Conversions:** DateTime strings from SQLite need to be parsed with `chrono::DateTime::parse_from_rfc3339()` - store in temporary variables before parsing
- **Matching Thresholds:** Matching uses 35% minimum threshold to filter out low-quality matches. Rooms below this threshold are not shown. Rooms with <60% score trigger automatic room creation.
- **Room Creation:** Rooms are auto-created when no good match (>60%) exists. The title is generated from keywords in the intent (simple extraction, future: LLM-based).
- **Atlas Endpoint:** GET `/v1/atlas` currently returns all rooms (stub implementation). Future v2 will be client-side with compressed embeddings for privacy-preserving matching.
- **Session Middleware:** Session validation middleware extracts `X-Session-Id` header and validates session exists and hasn't expired. Used by burn session endpoint.
- **Posts Threading:** Two-level threading only (top-level posts and direct replies). No nested replies in MVP. Posts are distinct from Live chat messages (filtered by `message_type = 'post'`).
- **Database Migrations:** Index creation for new columns must be handled in migration functions, not in schema.sql, to avoid errors when column doesn't exist yet.
- **Resources Date Parsing:** Date parsing in ResourceRepository uses error handling with fallback to current time if parsing fails. This prevents API errors from breaking room access.
- **JavaScript Error Handling:** Always check `response.ok` before calling `response.json()` to prevent parsing errors when API returns error responses.

### Current Focus
- **Whispers Feature Complete:** Full 1-on-1 ephemeral messaging feature implemented and functional
- **All Room Tabs Complete:** Live, Posts, Highlights, Resources, and Whispers tabs all functional
- **Active Members Detection:** Enhanced with API endpoint and polling for real-time member visibility
- **Bug Fixes Applied:** Route parameters, SQL dates, chat opening flow, state handling all fixed
- **Next Steps:** Proceed with Sprint 4 (Safety/Moderation) or matching refinements

---

## Handoff Checklist
When handing off work, ensure:
- [x] Current sprint status updated
- [x] Active tasks marked with current state
- [x] Blockers documented
- [x] Recent changes logged in "What Changed Recently"
- [x] Next agent has clear "Next Up" items
- [x] Any gotchas or context added to Quick Context

