//! storage: db + blobs

mod messages;
mod rooms;
mod sessions;
mod rate_limits;
mod highlights;
mod resources;
mod whispers;

pub use messages::MessageRepository;
pub use rooms::RoomRepository;
pub use sessions::SessionRepository;
pub use rate_limits::RateLimitRepository;
pub use highlights::HighlightRepository;
pub use resources::ResourceRepository;
pub use whispers::WhisperRepository;

use sqlx::{sqlite::SqliteConnectOptions, SqlitePool};
use anyhow::Result;
use std::path::Path;

use core::{Message, MessageType, PolicyFlags};

pub struct StorageClient {
    pool: SqlitePool,
}

impl StorageClient {
    pub async fn new<P: AsRef<Path>>(database_path: P) -> Result<Self> {
        let path = database_path.as_ref();
        
        // Get absolute path to avoid working directory issues
        let abs_path = if path.is_absolute() {
            path.to_path_buf()
        } else {
            std::env::current_dir()?.join(path)
        };
        
        // Ensure parent directory exists
        if let Some(parent) = abs_path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        
        // Use SqliteConnectOptions directly - this handles Windows paths correctly
        let options = SqliteConnectOptions::new()
            .filename(&abs_path)
            .create_if_missing(true);
        
        tracing::info!("Connecting to database at: {}", abs_path.display());
        
        let pool = SqlitePool::connect_with(options)
            .await
            .map_err(|e| {
                anyhow::anyhow!("Failed to connect to database at '{}': {}", 
                    abs_path.display(), e)
            })?;
        
        Ok(Self { pool })
    }

    pub async fn init(&self) -> Result<()> {
        // Run schema migrations
        let schema = include_str!("schema.sql");
        
        // Split by semicolon and execute each statement
        // Note: SQLite allows multiple statements separated by semicolons
        for (idx, statement) in schema.split(';').enumerate() {
            let statement = statement.trim();
            
            // Skip empty statements and comments
            if statement.is_empty() {
                continue;
            }
            
            // Skip comment-only lines
            let non_comment_lines: Vec<&str> = statement
                .lines()
                .filter(|line| {
                    let trimmed = line.trim();
                    !trimmed.is_empty() && !trimmed.starts_with("--")
                })
                .collect();
            
            if non_comment_lines.is_empty() {
                continue;
            }
            
            // Execute the statement
            tracing::debug!("Executing schema statement {}: {}", idx + 1, 
                statement.lines().next().unwrap_or("").trim());
            
            sqlx::query(statement)
                .execute(&self.pool)
                .await
                .map_err(|e| {
                    anyhow::anyhow!("Failed to execute schema statement {}: {}\nStatement: {}", 
                        idx + 1, e, statement)
                })?;
        }
        
        // Migrate existing databases: add new columns to rooms table if they don't exist
        // SQLite doesn't support IF NOT EXISTS for ALTER TABLE, so we check first
        self.migrate_rooms_table().await?;
        self.migrate_messages_table().await?;
        self.migrate_highlights_table().await?;
        self.migrate_resources_table().await?;
        self.migrate_whispers_table().await?;
        
        tracing::info!("Schema initialization completed successfully");
        Ok(())
    }

    async fn migrate_rooms_table(&self) -> Result<()> {
        // Check if new columns exist by trying to query them
        // If they don't exist, add them with ALTER TABLE
        
        // Helper to check if a column exists
        async fn column_exists(pool: &SqlitePool, column: &str) -> bool {
            let query = format!("SELECT {} FROM rooms LIMIT 1", column);
            sqlx::query(&query)
                .execute(pool)
                .await
                .is_ok()
        }

        // Add tags column if it doesn't exist
        if !column_exists(&self.pool, "tags").await {
            tracing::info!("Adding 'tags' column to rooms table");
            sqlx::query("ALTER TABLE rooms ADD COLUMN tags TEXT DEFAULT ''")
                .execute(&self.pool)
                .await?;
        }

        // Add description column if it doesn't exist
        if !column_exists(&self.pool, "description").await {
            tracing::info!("Adding 'description' column to rooms table");
            sqlx::query("ALTER TABLE rooms ADD COLUMN description TEXT DEFAULT ''")
                .execute(&self.pool)
                .await?;
        }

        // Add activity_score column if it doesn't exist
        if !column_exists(&self.pool, "activity_score").await {
            tracing::info!("Adding 'activity_score' column to rooms table");
            sqlx::query("ALTER TABLE rooms ADD COLUMN activity_score REAL DEFAULT 0.0")
                .execute(&self.pool)
                .await?;
        }

        // Add member_count column if it doesn't exist
        if !column_exists(&self.pool, "member_count").await {
            tracing::info!("Adding 'member_count' column to rooms table");
            sqlx::query("ALTER TABLE rooms ADD COLUMN member_count INTEGER DEFAULT 0")
                .execute(&self.pool)
                .await?;
        }

        Ok(())
    }

    async fn migrate_messages_table(&self) -> Result<()> {
        // Check if parent_post_id column exists by trying to query it
        // If it doesn't exist, add it with ALTER TABLE
        
        // Helper to check if a column exists
        async fn column_exists(pool: &SqlitePool, column: &str) -> bool {
            let query = format!("SELECT {} FROM messages LIMIT 1", column);
            sqlx::query(&query)
                .execute(pool)
                .await
                .is_ok()
        }

        // Add parent_post_id column if it doesn't exist
        if !column_exists(&self.pool, "parent_post_id").await {
            tracing::info!("Adding 'parent_post_id' column to messages table");
            sqlx::query("ALTER TABLE messages ADD COLUMN parent_post_id TEXT")
                .execute(&self.pool)
                .await?;
            
            // Add index for parent_post_id
            tracing::info!("Adding index for 'parent_post_id' column");
            sqlx::query("CREATE INDEX IF NOT EXISTS idx_messages_parent_post ON messages(parent_post_id)")
                .execute(&self.pool)
                .await?;
        }

        Ok(())
    }

    async fn migrate_highlights_table(&self) -> Result<()> {
        // Check if highlights table exists by trying to query it
        async fn table_exists(pool: &SqlitePool) -> bool {
            let query = "SELECT name FROM sqlite_master WHERE type='table' AND name='highlights'";
            sqlx::query(query)
                .fetch_optional(pool)
                .await
                .map(|row| row.is_some())
                .unwrap_or(false)
        }

        // Create highlights table if it doesn't exist
        if !table_exists(&self.pool).await {
            tracing::info!("Creating highlights table");
            sqlx::query(
                r#"
                CREATE TABLE highlights (
                    id TEXT PRIMARY KEY,
                    room_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    reference_type TEXT NOT NULL,
                    reference_id TEXT,
                    curator_mask TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    is_auto INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (room_id) REFERENCES rooms(id)
                )
                "#,
            )
            .execute(&self.pool)
            .await?;

            // Add indexes
            tracing::info!("Adding indexes for highlights table");
            sqlx::query("CREATE INDEX IF NOT EXISTS idx_highlights_room_id ON highlights(room_id)")
                .execute(&self.pool)
                .await?;
            sqlx::query("CREATE INDEX IF NOT EXISTS idx_highlights_created_at ON highlights(created_at DESC)")
                .execute(&self.pool)
                .await?;
        }

        Ok(())
    }

    async fn migrate_resources_table(&self) -> Result<()> {
        // Check if resources table exists by trying to query it
        async fn table_exists(pool: &SqlitePool) -> bool {
            let query = "SELECT name FROM sqlite_master WHERE type='table' AND name='resources'";
            sqlx::query(query)
                .fetch_optional(pool)
                .await
                .map(|row| row.is_some())
                .unwrap_or(false)
        }

        // Create resources table if it doesn't exist
        if !table_exists(&self.pool).await {
            tracing::info!("Creating resources table");
            sqlx::query(
                r#"
                CREATE TABLE resources (
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
                )
                "#,
            )
            .execute(&self.pool)
            .await?;

            // Add indexes
            tracing::info!("Adding indexes for resources table");
            sqlx::query("CREATE INDEX IF NOT EXISTS idx_resources_room_id ON resources(room_id)")
                .execute(&self.pool)
                .await?;
            sqlx::query("CREATE INDEX IF NOT EXISTS idx_resources_category ON resources(category)")
                .execute(&self.pool)
                .await?;
            sqlx::query("CREATE INDEX IF NOT EXISTS idx_resources_created_at ON resources(created_at DESC)")
                .execute(&self.pool)
                .await?;
        }

        Ok(())
    }

    async fn migrate_whispers_table(&self) -> Result<()> {
        // Check if whispers table exists by trying to query it
        async fn table_exists(pool: &SqlitePool) -> bool {
            let query = "SELECT name FROM sqlite_master WHERE type='table' AND name='whispers'";
            sqlx::query(query)
                .fetch_optional(pool)
                .await
                .map(|row| row.is_some())
                .unwrap_or(false)
        }

        // Create whispers table if it doesn't exist
        if !table_exists(&self.pool).await {
            tracing::info!("Creating whispers table");
            sqlx::query(
                r#"
                CREATE TABLE whispers (
                    id TEXT PRIMARY KEY,
                    sender_mask TEXT NOT NULL,
                    recipient_mask TEXT NOT NULL,
                    room_id TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    last_activity_at TEXT NOT NULL,
                    FOREIGN KEY (room_id) REFERENCES rooms(id)
                )
                "#,
            )
            .execute(&self.pool)
            .await?;

            // Add indexes
            tracing::info!("Adding indexes for whispers table");
            sqlx::query("CREATE INDEX IF NOT EXISTS idx_whispers_sender ON whispers(sender_mask, room_id, state)")
                .execute(&self.pool)
                .await?;
            sqlx::query("CREATE INDEX IF NOT EXISTS idx_whispers_recipient ON whispers(recipient_mask, room_id, state)")
                .execute(&self.pool)
                .await?;
            sqlx::query("CREATE INDEX IF NOT EXISTS idx_whispers_expires_at ON whispers(expires_at)")
                .execute(&self.pool)
                .await?;
            sqlx::query("CREATE INDEX IF NOT EXISTS idx_whispers_room_id ON whispers(room_id)")
                .execute(&self.pool)
                .await?;
        }

        Ok(())
    }

    pub async fn seed_rooms(&self) -> Result<()> {
        // Check if rooms already exist
        let rooms = RoomRepository::list_rooms(&self.pool).await?;
        if !rooms.is_empty() {
            return Ok(()); // Already seeded
        }

        // Create starter rooms
        let starter_rooms = vec![
            ("General Chat", "en", PolicyFlags::default()),
            ("Tech Talk", "en", PolicyFlags::default()),
            ("Random Thoughts", "en", PolicyFlags::default()),
        ];

        for (title, lang, flags) in starter_rooms {
            RoomRepository::create_room(
                &self.pool,
                title.to_string(),
                lang.to_string(),
                flags,
            ).await?;
        }

        // Get the rooms we just created and add some sample messages
        let rooms = RoomRepository::list_rooms(&self.pool).await?;
        for room in rooms.iter().take(2) {
            // Add a welcome message to first two rooms
            let welcome_msg = Message::new(
                room.id.clone(),
                "System".to_string(),
                MessageType::Text,
                format!("Welcome to {}! Start chatting...", room.title),
                None,
                None,
            )?;
            
            MessageRepository::create_message(&self.pool, welcome_msg).await?;
        }

        Ok(())
    }

    pub fn pool(&self) -> &SqlitePool {
        &self.pool
    }
}