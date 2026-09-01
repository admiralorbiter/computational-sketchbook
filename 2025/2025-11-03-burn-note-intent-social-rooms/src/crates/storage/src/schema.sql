-- Rooms table
CREATE TABLE IF NOT EXISTS rooms (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    language TEXT NOT NULL,
    policy_flags INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    tags TEXT DEFAULT '',
    description TEXT DEFAULT '',
    activity_score REAL DEFAULT 0.0,
    member_count INTEGER DEFAULT 0
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL,
    sender_mask TEXT NOT NULL,
    message_type TEXT NOT NULL,
    body TEXT NOT NULL,
    media_url TEXT,
    media_type TEXT,
    media_size INTEGER,
    created_at TEXT NOT NULL,
    tombstoned INTEGER NOT NULL DEFAULT 0,
    whisper_id TEXT,
    parent_post_id TEXT,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (parent_post_id) REFERENCES messages(id)
);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL,
    session_mask TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

-- Rate limit events table (foundation for rate limiting)
-- Note: session_id is a flexible identifier (can be actual session_id or rate limit key)
-- For MVP, we use string-based identifiers that may not reference actual sessions
CREATE TABLE IF NOT EXISTS rate_limit_events (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    bucket TEXT NOT NULL
);

-- Highlights table
CREATE TABLE IF NOT EXISTS highlights (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL,
    title TEXT NOT NULL,
    reference_type TEXT NOT NULL,
    reference_id TEXT,
    curator_mask TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_auto INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

-- Resources table
CREATE TABLE IF NOT EXISTS resources (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    category TEXT,
    curator_mask TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    is_verified INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

-- Whispers table
CREATE TABLE IF NOT EXISTS whispers (
    id TEXT PRIMARY KEY,
    sender_mask TEXT NOT NULL,
    recipient_mask TEXT NOT NULL,
    room_id TEXT NOT NULL,
    state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    last_activity_at TEXT NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_messages_room_id ON messages(room_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_room_created ON messages(room_id, created_at);
-- Note: idx_messages_parent_post is created in migration function after column is added
CREATE INDEX IF NOT EXISTS idx_sessions_room_id ON sessions(room_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_rate_limit_events_session_action ON rate_limit_events(session_id, action_type);
CREATE INDEX IF NOT EXISTS idx_rate_limit_events_timestamp ON rate_limit_events(timestamp);
-- Note: idx_highlights_room_id and idx_highlights_created_at are created in migration function after table is added
-- Note: idx_resources_room_id, idx_resources_category, and idx_resources_created_at are created in migration function after table is added
-- Note: idx_whispers_sender, idx_whispers_recipient, idx_whispers_expires_at, and idx_whispers_room_id are created in migration function after table is added
