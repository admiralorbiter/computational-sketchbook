# Changelog - Work Tracking

Track significant changes, decisions, and milestones for agent handoffs.

Format: `[YYYY-MM-DD] [Type] [Description]`

---

## [2025-11-04] Implementation - WebSocket Real-time Infrastructure

### Added
- **WebSocket Server** (`apps/web/src/handlers/websocket.rs` - NEW):
  - `GET /v1/ws?session_id={id}` endpoint for WebSocket connection upgrade
  - Session-based authentication via `X-Session-Id` header
  - Connection lifecycle management (connect, disconnect, cleanup)
- **Connection Manager** (`apps/web/src/websocket/connection.rs` - NEW):
  - Tracks active WebSocket connections with unique connection IDs
  - Room and whisper subscription management
  - Broadcast methods: `broadcast_to_room()`, `broadcast_to_whisper()`
  - Automatic cleanup of disconnected connections
- **Event Bus Integration** (`apps/web/src/main.rs`):
  - Global event forwarding task that subscribes to all relevant events
  - Converts `bus::Event` to `ServerMessage` via `convert_event_to_message()`
  - Forwards events to subscribed connections via ConnectionManager
  - Event types: `message.created`, `whisper.*`, `post.*`, `member.*`
- **WebSocket Message Types** (`apps/web/src/websocket/events.rs`):
  - Client messages: `Subscribe`, `Unsubscribe`, `Ping`
  - Server messages: `Message`, `WhisperMessage`, `MemberJoined`, `MemberLeft`, `WhisperCreated`, `WhisperAccepted`, `WhisperDeclined`, `WhisperEnded`, `PostCreated`, `PostReplied`, `SubscriptionConfirmed`, `Error`, `Pong`
  - Event conversion logic from `bus::Event` to `ServerMessage`
- **AppState** (`apps/web/src/main.rs`):
  - Centralized state management struct with `Arc<SqlitePool>`, `Arc<ConnectionManager>`, `Arc<EventBus>`
  - `FromRef` implementations for Axum to extract individual components
- **Event Publishing** (Updated handlers):
  - `create_message`: Publishes `message.created` events
  - `create_whisper`, `accept_whisper`, `decline_whisper`, `end_whisper`: Publish whisper events
  - `create_post`: Publishes `post.created` or `post.replied` events
  - `join_room`: Publishes `member.joined` events
  - `burn_session`: Publishes `member.left` events
- **Client-side WebSocket Client** (`apps/web/static/app.js`):
  - `WebSocketClient` class with auto-reconnect and exponential backoff
  - Heartbeat mechanism (ping every 30 seconds)
  - Subscribe/unsubscribe to rooms and whispers
  - Event handlers for all server message types
  - Real-time UI updates for messages, whispers, members, posts

### Changed
- **Real-time Updates**: Replaced polling with WebSocket events for:
  - Live chat messages (instant delivery)
  - Whisper messages (instant delivery when whisper chat is open)
  - Active members list (updates via `member_joined`/`member_left` events)
  - Whisper list (updates via `whisper_created`/`whisper_accepted`/`whisper_declined`/`whisper_ended` events)
  - Posts and replies (updates via `post_created`/`post_replied` events)
- **Whisper Chat**: Real-time updates when whisper chat is open (auto-subscribes on open, unsubscribes on close)
- **Message Handling**: Messages now appear instantly in UI without page refresh or manual polling

### Fixed
- **Whisper Real-time Updates**: Fixed issue where whisper messages only updated after re-clicking whisper
  - Added automatic subscription when opening whisper chat
  - Added unsubscribe when switching/closing whispers
  - Improved ID comparison (string conversion to avoid type mismatches)
  - Added duplicate message detection

### Decisions
- **WebSocket over Polling**: Chose WebSocket for real-time updates to reduce server load and improve UX
- **Event Bus Pattern**: Uses in-process pub/sub (`bus` crate) for decoupling event producers from WebSocket distribution
- **Connection Manager**: Centralized connection tracking simplifies subscription management and cleanup
- **Client Auto-reconnect**: Exponential backoff with max 10 attempts for reliability
- **Subscription Model**: Clients explicitly subscribe to rooms/whispers to receive events (filtered at server)

### Notes
- **Real-time Features Complete**: All major features now have real-time updates via WebSocket
- **No Polling**: Removed polling for active members and whispers list
- **Event Types**: All events follow `{entity}.{action}` naming convention (e.g., `message.created`, `whisper.accepted`)
- **Future Enhancement**: Could add WebSocket metrics (connection count, message throughput) for observability

---

## [2025-11-XX] Documentation Complete

### Added
- Complete sprint plan documentation (Sprints 0-6)
- PRD and HLD documents
- API contracts for rooms, messages, whispers, highlights
- Security policies (MVP privacy caveats, threat model)
- Moderation workflows and safety policies
- Observability and testing plans
- Agent handoff system (this changelog and related docs)

### Decisions
- Web SPA only for MVP (ADR 0001)
- Stubbed E2E, TLS only for MVP (ADR 0002)
- Axum-based API server (ADR 0003)
- Room Atlas v1 schema and delivery design (ADR 0004)

---

## [2025-11-04] Implementation - Sprint 1 Matching & Atlas

### Added
- **Intent-based matching** (`apps/web/src/handlers/matching.rs`):
  - POST `/v1/intent/match` endpoint with keyword-based scoring
  - Score threshold filtering (35% minimum, 60% good match threshold)
  - Qualitative match reasons (human-friendly descriptions)
  - Automatic room creation when no good match exists
  - Helper functions: `generate_match_reason()`, `summarize_topics()`, `create_room_from_intent()`
- **Room metadata fields** (`crates/core/src/room.rs`):
  - Added `tags`, `description`, `activity_score`, `member_count` to Room model
  - `Room::new_with_metadata()` constructor for rooms with metadata
  - Update methods: `update_activity_score()`, `update_member_count()`, `update_metadata()`
- **Session management**:
  - Burn session endpoint (`apps/web/src/handlers/sessions.rs`): DELETE `/v1/sessions/:id`
  - Session validation middleware (`apps/web/src/middleware/session.rs`)
  - Background task for session expiration (runs every 5 minutes)
- **Rate limiting foundation** (`crates/storage/src/rate_limits.rs`):
  - `RateLimitRepository` with `check_rate_limit()`, `record_action()`, `cleanup_old_events()`
  - Applied to join_room (1 per minute per room) and create_message (10 per minute)
- **Room Atlas stub** (`apps/web/src/handlers/atlas.rs`):
  - GET `/v1/atlas` endpoint returning all rooms (stub for future client-side v2)
- **Matching crate structure** (`crates/matching/`):
  - New crate with `MatchingStrategy` trait for future extensibility
  - Ready for embeddings, collaborative filtering, contextual matching
- **Frontend improvements** (`apps/web/static/`):
  - Intent entry view as default home page
  - Qualitative badges (Excellent Match, Good Fit, Worth Exploring)
  - New room welcome message UI
  - Session controls (burn session button in header and room view)
  - Alternatives section with collapsible toggle
- **Database schema migration** (`crates/storage/src/lib.rs`):
  - `migrate_rooms_table()` function to add metadata columns to existing databases
  - Backward compatible - uses `try_get()` for graceful handling of missing columns
- **Scalable matching documentation** (`docs/algorithms/matching_v2_scalable.md`):
  - Future roadmap for handling 2000+ rooms per topic
  - Hierarchical embeddings, multi-signal scoring, room clustering strategies

### Changed
- **Matching algorithm**:
  - Replaced technical match reasons ("title:tech, tag:programming") with qualitative descriptions
  - Score calculation now includes activity_score and member_count boosts
  - Filtering applied before sorting (rooms below 35% threshold excluded)
- **Room creation logic**:
  - Automatic room creation when no good match (<60%) exists
  - Title generation from intent keywords (simple extraction, future: LLM-based)
  - Tag extraction from intent
- **UI flow**:
  - Intent entry is now the default home page (instead of room listing)
  - Room listing moved to dev-only "Browse all rooms" link
  - Matched results show top 3 rooms + alternatives section
- **Database queries** (`crates/storage/src/rooms.rs`):
  - Updated `get_room()` and `list_rooms()` to retrieve metadata fields
  - Migration-compatible using `try_get()` with defaults

### Decisions
- **Matching thresholds**: 35% minimum, 60% good match (chosen to balance relevance with discovery)
- **Room creation**: Automatic creation for unique intents (aligns with product vision of no dead ends)
- **Qualitative UX**: Hide technical match details from users to maintain "mystery" and prevent gaming
- **Rate limiting**: Basic implementation using room_id/sender_mask as temporary identifiers (MVP approach)
- **Atlas stub**: Server-side endpoint for now, will migrate to client-side in v2 for privacy

### Notes
- **Room creation**: Currently uses simple keyword extraction for title generation. Future enhancement could use LLM for creative titles.
- **Matching crate**: Structure is ready for future strategies (embeddings, collaborative filtering). Current implementation remains in handler for simplicity.
- **Testing**: Manual testing recommended for matching scenarios (good match, no match, borderline match, new room creation)
- **Next steps**: Ready for Sprint 3 (Whispers) or matching refinements

---

## [2025-01-XX] Implementation - Sprint 3 Whispers Complete

### Added
- **Whispers domain model** (`crates/core/src/whisper.rs` - NEW):
  - Created `WhisperSession` struct with id, sender_mask, recipient_mask, room_id, state, created_at, expires_at, last_activity_at
  - Created `WhisperState` enum (Pending, Active, Declined, Ended)
  - State transition methods: `accept()`, `decline()`, `end()`, `extend()`
  - Expiry logic with `is_expired()` method
  - Default TTL: 24 hours
- **Database schema** (`crates/storage/src/schema.sql`):
  - Added whispers table with all required columns
  - Added indexes for sender_mask, recipient_mask, room_id, expires_at for performance
- **Database migration** (`crates/storage/src/lib.rs`):
  - Added `migrate_whispers_table()` function to create whispers table for existing databases
  - Integrated into initialization flow
- **Repository layer** (`crates/storage/src/whispers.rs` - NEW):
  - `create_whisper()` - Insert new whisper
  - `get_whisper()` - Get whisper by ID
  - `get_active_whisper()` - Get active whisper between two participants
  - `get_whispers_for_mask()` - List whispers for a user (filtered by room_id if provided)
  - `accept_whisper()` - Update whisper state to Active
  - `decline_whisper()` - Update whisper state to Declined
  - `end_whisper()` - Update whisper state to Ended
  - `extend_whisper()` - Extend whisper expiry time
  - `update_activity()` - Update last_activity_at timestamp
  - `expire_whispers()` - Batch expire whispers (used by background task)
  - State stored as plain strings ("pending", "active", etc.) for database compatibility
- **Whispers API handlers** (`apps/web/src/handlers/whispers.rs` - NEW):
  - `GET /v1/whispers` - List whispers with mask and optional room_id filter
  - `POST /v1/whispers` - Create whisper request (validates sender/recipient, checks for existing active whisper)
  - `POST /v1/whispers/:id/accept` - Accept whisper (returns full whisper object)
  - `POST /v1/whispers/:id/decline` - Decline whisper
  - `DELETE /v1/whispers/:id` - End whisper session
  - `POST /v1/whispers/:id/extend` - Extend whisper expiry
  - Full validation: sender must have active session, recipient must have messages or active session
  - Rate limiting: 10 whisper messages per 60s per whisper
- **Active Members API** (`apps/web/src/handlers/members.rs` - NEW):
  - `GET /v1/rooms/:room_id/members` - Get active members in a room (from sessions table)
  - Uses RFC3339 format for date comparison
  - Returns distinct session_mask values where expires_at > now
- **Message handler integration** (`apps/web/src/handlers/messages.rs`):
  - Whisper message validation: checks whisper_id exists, is active, not expired
  - Updates whisper last_activity_at when whisper message is sent
  - Separate rate limiting for whisper messages (10 per 60s per whisper vs 10 per 60s per room)
  - Whisper messages filtered from Live tab display
- **Whispers UI** (`apps/web/static/index.html`, `app.js`):
  - Complete Whispers tab with list view showing pending and active whispers
  - Pending whispers show Accept/Decline buttons
  - Active whispers show chat interface with message list, input area, extend/end buttons
  - Whisper list items show participant, state, expiry time
  - Chat view automatically opens after accepting whisper (critical UX fix)
  - Message filtering: whisper messages only shown in whisper chat, hidden from Live tab
  - Active members sidebar in Live tab with "Whisper" button per member
- **Background tasks** (`apps/web/src/main.rs`):
  - Whisper expiry cleanup runs every 5 minutes
  - Expires whispers where expires_at < now

### Changed
- **Message model** - Extended to support whisper messages via `MessageType::Whisper` and `whisper_id` field
- **Message handler** - Added whisper validation and activity tracking
- **Room view** - Added Whispers tab to navigation (5 tabs total: Live, Posts, Highlights, Resources, Whispers)
- **Active members detection** - Enhanced from message-based to session-based with API endpoint and polling

### Fixed
- **Route parameter bug** - Fixed members handler to use `Path(room_id)` instead of `Query(params)` (critical bug)
- **SQL date comparison** - Fixed to use RFC3339 format instead of `datetime('now')` for consistent timezone handling
- **Chat opening after accept** - Fixed critical UX issue where accepting whisper didn't open chat view
  - Modified `acceptWhisper()` to capture full response and immediately call `openWhisperChat()`
  - Enhanced `accept_whisper` handler to return full whisper object instead of partial data
- **State handling** - Added case-insensitive state comparison and comprehensive validation
- **Error visibility** - Added detailed logging and user-visible error messages throughout
- **Active members not showing** - Fixed by implementing dedicated API endpoint and frontend polling

### Decisions
- **Whisper state storage** - Stored as plain strings in database ("pending", "active", etc.) for compatibility
- **Rate limiting** - Whisper messages have separate rate limit (10 per 60s per whisper) vs room messages
- **Recipient validation** - Allows whispers to members who have sent messages OR have active sessions (lenient for UX)
- **Auto-open chat** - Chat view automatically opens after accept to improve UX (no manual click needed)
- **Active members** - Uses sessions table as source of truth, with message-based fallback for backward compatibility
- **Expiry handling** - Background task runs every 5 minutes to clean up expired whispers

### Notes
- **Vertical slice complete** - Entire Whispers feature is testable end-to-end: create, accept/decline, send messages, extend, end
- **State management** - Four states: Pending (waiting for accept), Active (can send messages), Declined (recipient rejected), Ended (either party ended)
- **Expiry logic** - Whispers expire after 24 hours by default, can be extended via API
- **Message integration** - Whisper messages use same message table but with `type: "whisper"` and `whisper_id` field
- **UI improvements** - Chat automatically opens after accept, active members shown in Live tab with whisper buttons
- **Next steps** - Ready for Sprint 4 (Safety/Moderation) or matching refinements

---

## [Future Entries]

### Example Format:
```
[YYYY-MM-DD] Implementation

### Added
- [Feature/component added]
- [File paths changed]

### Changed
- [What was modified]

### Fixed
- [Bugs fixed]

### Decisions
- [Any new ADRs or decisions]

### Notes
- [Important context for agents]
```

---

## How to Use This Changelog

- **Agents:** Add entries when completing significant work
- **On Handoff:** Review recent entries to understand what changed
- **Scope:** Focus on implementation milestones, not every commit

## [2025-11-04] Implementation - Sprint 2 Core APIs

### Added
- Storage layer with SQLx repositories (`crates/storage/src/`):
  - `RoomRepository` - CRUD operations for rooms
  - `MessageRepository` - Message creation and retrieval with pagination
  - `SessionRepository` - User session management
- API handlers (`apps/web/src/handlers/`):
  - `rooms.rs` - GET `/v1/rooms`, POST `/v1/rooms/:id/join`
  - `messages.rs` - GET `/v1/messages`, POST `/v1/messages`
- Domain models (`crates/core/src/`):
  - `Room` - Room domain model with validation
  - `Message` - Message domain model with type support (Text, Media, Whisper)
  - `UserSession` - Session management with expiration
  - `PolicyFlags` - Room policy flags (sensitive, curated, slow_mode)
- Database schema (`crates/storage/src/schema.sql`):
  - Rooms, messages, and sessions tables with indexes
- Functional UI (`apps/web/static/`):
  - `index.html` - Single-page app with room listing and chat interface
  - `app.js` - Client-side JavaScript for API interaction
- Database initialization and seeding in `StorageClient`

### Changed
- Fixed SQLite database connection on Windows:
  - Switched from manual connection string formatting to `SqliteConnectOptions::filename()`
  - Handles Windows paths correctly (backslashes, absolute paths)
  - Resolves relative paths to absolute using `std::env::current_dir()`
- Updated SQLx query patterns:
  - Using `sqlx::query()` with `.bind()` instead of `sqlx::query!` macro
  - Allows offline compilation without database connection
  - Added `use sqlx::Row;` for row data access

### Fixed
- Windows SQLite connection error (code 14: unable to open database file)
- Type conversion issues with DateTime parsing from SQLite strings
- Missing `Row` trait imports in repository files

### Decisions
- Use `SqliteConnectOptions` API instead of connection strings for better cross-platform support
- Use runtime queries (`sqlx::query()`) instead of compile-time queries for offline compilation
- Store database file in project root directory (relative to where `cargo run` executes)

### Notes
- **Current Issue:** Schema execution in `init()` method needs debugging. Tables are not being created properly despite connection working. Added detailed logging to help diagnose.
- **Next Steps:** Fix schema execution, then test complete end-to-end flow
- **Testing:** Manual testing via UI shows API endpoints are responding, but database operations fail due to missing tables

---

## [2025-11-04] Implementation - Sprint 2 MVP Complete

### Fixed
- **Schema execution blocker resolved** - Database tables are now created successfully on startup
  - Schema SQL statements executing correctly through `StorageClient::init()`
  - All tables (rooms, messages, sessions) and indexes created properly
  - Database seeding working as expected

### Changed
- **Sprint 2 status updated** - Progress from 60% to 95% complete
- MVP is now fully operational end-to-end

### Notes
- **MVP Verification:** User testing confirmed 3 chat rooms accessible and messaging functional
- **End-to-End Status:** All core features working - room listing, joining, message sending/receiving
- **Next Steps:** Code cleanup (replace debug logging) and optional polish work, or proceed to next sprint
- **Schema Execution:** The schema splitting logic in `init()` is working correctly - statements execute successfully despite initial concerns

---

## [2025-11-04] Implementation - Resources Feature Complete + Bug Fixes

### Added
- **Resources domain model** (`crates/core/src/resource.rs` - NEW):
  - Created `Resource` struct with id, room_id, title, url, description, category, curator_mask, created_at, updated_at, is_verified
  - URL validation (must start with http:// or https://)
  - Field length validation (title: 200 chars, description: 500 chars, category: 50 chars)
  - Helper methods: `new()`, `new_verified()`, `update()`, `validate()`
- **Database schema** (`crates/storage/src/schema.sql`):
  - Added `resources` table with all required columns
  - Added indexes for room_id, category, and created_at (DESC) for performance
- **Database migration** (`crates/storage/src/lib.rs`):
  - Added `migrate_resources_table()` function to create resources table for existing databases
  - Integrated into initialization flow
- **Repository layer** (`crates/storage/src/resources.rs` - NEW):
  - `create_resource()` - Insert new resource
  - `get_resources()` - Get all resources for a room (newest first, paginated, optional category filter)
  - `get_resource_by_id()` - Get single resource by ID
  - `update_resource()` - Update resource (title, url, description, category)
  - `delete_resource()` - Remove resource
  - `get_resources_by_category()` - Filter resources by category
  - All methods include error handling for date parsing with fallback behavior
- **Resources API handlers** (`apps/web/src/handlers/resources.rs` - NEW):
  - `GET /v1/rooms/:room_id/resources` - List resources with pagination and category filter
  - `POST /v1/rooms/:room_id/resources` - Create resource with URL validation
  - `PUT /v1/resources/:id` - Update resource (partial updates supported)
  - `DELETE /v1/resources/:id` - Delete resource
  - Rate limiting: 10 resources per 60s per room
  - Full validation for all inputs
- **Resources UI** (`apps/web/static/index.html`, `app.js`):
  - Complete Resources tab with list view
  - Category filter dropdown (auto-populated from existing resources)
  - Create resource form with title, URL, description, category fields
  - Resource cards with metadata (verified badge, category badge, curator, timestamps)
  - Edit resource functionality (prompt-based for MVP)
  - Delete resource functionality
  - URL validation on client side
  - Category suggestions (health, legal, tools, guides, support, education)

### Changed
- **Room tabs complete** - All four tabs (Live, Posts, Highlights, Resources) are now fully functional
- **Error handling improved** - Resources loading errors are isolated and don't break room access

### Fixed
- **Resources loading bug** (`apps/web/static/app.js`):
  - Added `response.ok` check before parsing JSON in `loadResources()`
  - Proper error message extraction from API error responses
  - Added container existence check before DOM manipulation
  - Errors in resource loading no longer break room view
- **Date parsing errors** (`crates/storage/src/resources.rs`):
  - Added error handling for date parsing in all repository methods
  - If date parsing fails, logs error and uses current time as fallback
  - Prevents repository errors from breaking the API
  - Applied to `get_resources()`, `get_resource_by_id()`, and `get_resources_by_category()`

### Decisions
- **Categories are free-form strings** - Allows flexibility, can standardize later
- **Verification is simple boolean** - Future: moderation workflow
- **URL validation is basic** - Checks for http:// or https:// prefix, basic format validation
- **Edit uses prompts for MVP** - Future: modal with pre-filled form
- **Error isolation** - Resource loading errors are caught and don't affect room access

### Notes
- **All room tabs complete** - Live, Posts, Highlights, and Resources are all functional
- **Vertical slice complete** - Entire Resources feature is testable end-to-end: create, read, update, delete, filter
- **Bug fixes ensure stability** - Rooms with resources are now accessible, date parsing errors handled gracefully
- **Next steps** - Proceed with Whispers (Sprint 3) or matching refinements

---

## [2025-11-04] Implementation - Highlights Feature Complete

### Added
- **Highlights domain model** (`crates/core/src/highlight.rs` - NEW):
  - Created `Highlight` struct with id, room_id, title, reference_type, reference_id, curator_mask, created_at, is_auto
  - Created `HighlightReferenceType` enum (Message, Post, Standalone)
  - Validation logic for title length and reference type consistency
- **Database schema** (`crates/storage/src/schema.sql`):
  - Added highlights table with all required columns
  - Added indexes for performance
- **Database migration** (`crates/storage/src/lib.rs`):
  - Added `migrate_highlights_table()` function
  - Integrated into initialization flow
- **Repository layer** (`crates/storage/src/highlights.rs` - NEW):
  - CRUD operations for highlights
  - Auto-highlighting logic (posts with 5+ replies)
  - Helper methods for querying
- **Highlights API handlers** (`apps/web/src/handlers/highlights.rs` - NEW):
  - `GET /v1/rooms/:room_id/highlights` - List highlights with pagination and 24h filter
  - `POST /v1/rooms/:room_id/highlights` - Create highlight with validation
  - `DELETE /v1/highlights/:id` - Delete highlight
  - Rate limiting (5 highlights per 60s)
- **Highlights UI** (`apps/web/static/index.html`, `app.js`):
  - Highlights tab with list view
  - "Skim last 24h" filter button
  - Create highlight form with reference selection
  - Highlight cards with metadata and actions
  - Reference navigation to posts/messages
  - Delete functionality
- **Auto-highlighting integration** (`apps/web/src/handlers/posts.rs`):
  - Auto-highlights posts with 5+ replies
  - Triggers after post creation (both top-level and replies)

### Notes
- **Auto-highlighting rule** - Simple rule-based (5+ replies) for MVP, can be enhanced later
- **Vertical slice complete** - Entire Highlights feature is testable end-to-end

---

## [2025-11-04] Implementation - Posts Feature Complete

### Added
- **Posts data model** (`crates/core/src/message.rs`):
  - Added `parent_post_id: Option<String>` field to Message struct
  - Added `MessageType::Post` variant to enum
  - Added `PartialEq` trait to MessageType for validation comparisons
  - Updated `Message::new()` to accept `parent_post_id` parameter
  - Validation: if `parent_post_id` is set, `message_type` must be `Post`
- **Database schema** (`crates/storage/src/schema.sql`):
  - Added `parent_post_id TEXT` column to messages table (nullable, foreign key)
  - Index creation handled by migration function (not in schema.sql to avoid errors)
- **Database migration** (`crates/storage/src/lib.rs`):
  - Added `migrate_messages_table()` function to add `parent_post_id` column to existing databases
  - Creates index after column is added (backward compatible)
- **Repository layer** (`crates/storage/src/messages.rs`):
  - Updated all queries to include `parent_post_id` in SELECT and INSERT
  - Added `get_posts()` - returns top-level posts for a room (newest first, paginated)
  - Added `get_post_replies()` - returns replies to a specific post (oldest first, paginated)
  - Added `get_reply_count()` - counts replies for a post
  - Updated all Message construction to include `parent_post_id`
  - Updated tests to use new Message::new() signature
- **Posts API handlers** (`apps/web/src/handlers/posts.rs` - NEW):
  - `GET /v1/posts` - List top-level posts for a room with reply counts
  - `GET /v1/posts/:post_id/replies` - Get replies to a specific post
  - `POST /v1/posts` - Create a new post or reply (validates parent_post_id if provided)
  - Rate limiting: 10 posts per 60 seconds (same as messages)
  - Validation: parent post must exist and be in same room
- **Tab navigation UI** (`apps/web/static/index.html`):
  - Added tab navigation: Live / Posts / Highlights / Resources
  - Wrapped existing Live chat in tab container
  - Added placeholder tabs for Highlights and Resources
- **Posts UI** (`apps/web/static/index.html`, `app.js`):
  - Post creation form with textarea
  - Posts list with threaded display
  - Reply functionality with toggle forms
  - Reply counts displayed per post
  - Replies shown indented under parent posts
  - CSS styling for posts, replies, and forms

### Changed
- **Message model** - Extended to support posts and replies via `parent_post_id`
- **MessageRepository** - All queries updated to handle `parent_post_id` field
- **Room view** - Restructured to use tab navigation instead of single view
- **UI organization** - Live chat and Posts are now separate tabs in room view

### Fixed
- **Compilation errors** - Added `PartialEq` trait to `MessageType` enum
- **SQL queries** - Fixed message_type comparison to use bind parameters (JSON serialized)
- **Import errors** - Added `use sqlx::Row;` to posts handler
- **Database migration** - Index creation moved to migration function to avoid errors on existing databases

### Decisions
- **Posts reuse Message model** - Simpler MVP, avoids duplication, leverages existing infrastructure
- **Two-level threading** - Top-level posts and direct replies only (no nested replies in MVP)
- **Separate `/v1/posts` endpoints** - Clear API separation from Live chat messages
- **Rate limiting** - Posts use same limits as messages (10 per 60s)
- **Tab navigation** - All room features accessible via tabs (Live, Posts, Highlights, Resources)

### Notes
- **Posts are distinct from Live chat** - Filtered by `message_type = 'post'` and `parent_post_id IS NULL` for top-level
- **Migration strategy** - Index creation must be in migration function, not schema.sql, to handle existing databases
- **Threading depth** - Limited to 2 levels for MVP simplicity (can be extended later)
- **Vertical slice complete** - Entire Posts feature is testable end-to-end: create post, reply, view threads
- **Next steps** - Highlights and Resources tabs are ready for implementation (simple list views)

---

## [2025-11-04] Implementation - Sprint 2 Polish Complete

### Completed
- **Debug logging cleanup** - All `eprintln!` statements replaced with proper `tracing::info!` and `tracing::debug!` logging in `crates/storage/src/lib.rs`
- **Unit tests added** - Comprehensive test coverage for all repositories:
  - `RoomRepository`: Tests for create_room, get_room, list_rooms, get_nonexistent_room
  - `MessageRepository`: Tests for create_message, get_messages, pagination (limit, after), edge cases
  - `SessionRepository`: Tests for create_session, get_session, get_session_by_mask, delete_session, expire_sessions
  - All tests use in-memory SQLite database with proper schema initialization
- **Error messages improved** - API handlers now return user-friendly validation errors:
  - Input validation for empty strings, length limits, format validation
  - Better error codes (VALIDATION_ERROR, INTERNAL_ERROR, ROOM_NOT_FOUND, etc.)
  - Clear, descriptive error messages instead of internal error details

### Changed
- **Sprint 2 status updated** - Progress from 95% to 100% complete
- Sprint 2 is now fully complete and ready for next sprint

### Notes
- **All polish tasks completed** - Debug logging replaced, unit tests added, error messages improved
- **Ready for next sprint** - Sprint 1 (Matching & Atlas) or Sprint 3 (Whispers) can begin
- **Test coverage** - All repository operations have unit tests with proper setup/teardown using in-memory SQLite

---

