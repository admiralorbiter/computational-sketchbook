use sqlx::SqlitePool;
use sqlx::Row;
use anyhow::Result;

use core::{WhisperSession, WhisperState};

pub struct WhisperRepository;

impl WhisperRepository {
    pub async fn create_whisper(pool: &SqlitePool, whisper: WhisperSession) -> Result<WhisperSession, anyhow::Error> {
        sqlx::query(
            r#"
            INSERT INTO whispers (
                id, sender_mask, recipient_mask, room_id, state,
                created_at, expires_at, last_activity_at
            )
            VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)
            "#,
        )
        .bind(&whisper.id)
        .bind(&whisper.sender_mask)
        .bind(&whisper.recipient_mask)
        .bind(&whisper.room_id)
        .bind(match whisper.state {
            core::WhisperState::Pending => "pending",
            core::WhisperState::Active => "active",
            core::WhisperState::Declined => "declined",
            core::WhisperState::Ended => "ended",
        })
        .bind(whisper.created_at.to_rfc3339())
        .bind(whisper.expires_at.to_rfc3339())
        .bind(whisper.last_activity_at.to_rfc3339())
        .execute(pool)
        .await?;
        
        Ok(whisper)
    }

    pub async fn get_whisper(pool: &SqlitePool, whisper_id: &str) -> Result<Option<WhisperSession>, anyhow::Error> {
        let row = sqlx::query(
            r#"
            SELECT id, sender_mask, recipient_mask, room_id, state,
                   created_at, expires_at, last_activity_at
            FROM whispers
            WHERE id = ?1
            "#,
        )
        .bind(whisper_id)
        .fetch_optional(pool)
        .await?;
        
        if let Some(row) = row {
            Ok(Some(Self::row_to_whisper(row)?))
        } else {
            Ok(None)
        }
    }

    pub async fn get_active_whisper(
        pool: &SqlitePool,
        sender_mask: &str,
        recipient_mask: &str,
        room_id: &str,
    ) -> Result<Option<WhisperSession>, anyhow::Error> {
        let row = sqlx::query(
            r#"
            SELECT id, sender_mask, recipient_mask, room_id, state,
                   created_at, expires_at, last_activity_at
            FROM whispers
            WHERE ((sender_mask = ?1 AND recipient_mask = ?2) OR (sender_mask = ?2 AND recipient_mask = ?1))
              AND room_id = ?3
              AND state = 'active'
            LIMIT 1
            "#,
        )
        .bind(sender_mask)
        .bind(recipient_mask)
        .bind(room_id)
        .fetch_optional(pool)
        .await?;
        
        if let Some(row) = row {
            Ok(Some(Self::row_to_whisper(row)?))
        } else {
            Ok(None)
        }
    }

    pub async fn get_whispers_for_mask(
        pool: &SqlitePool,
        mask: &str,
        room_id: Option<&str>,
    ) -> Result<Vec<WhisperSession>, anyhow::Error> {
        let rows = if let Some(room) = room_id {
            sqlx::query(
                r#"
                SELECT id, sender_mask, recipient_mask, room_id, state,
                       created_at, expires_at, last_activity_at
                FROM whispers
                WHERE (sender_mask = ?1 OR recipient_mask = ?1)
                  AND room_id = ?2
                  AND (state = 'pending' OR state = 'active')
                ORDER BY last_activity_at DESC
                "#,
            )
            .bind(mask)
            .bind(room)
            .fetch_all(pool)
            .await?
        } else {
            sqlx::query(
                r#"
                SELECT id, sender_mask, recipient_mask, room_id, state,
                       created_at, expires_at, last_activity_at
                FROM whispers
                WHERE (sender_mask = ?1 OR recipient_mask = ?1)
                  AND (state = 'pending' OR state = 'active')
                ORDER BY last_activity_at DESC
                "#,
            )
            .bind(mask)
            .fetch_all(pool)
            .await?
        };
        
        let mut whispers = Vec::new();
        for row in rows {
            whispers.push(Self::row_to_whisper(row)?);
        }
        Ok(whispers)
    }

    pub async fn accept_whisper(pool: &SqlitePool, whisper_id: &str) -> Result<WhisperSession, anyhow::Error> {
        let now = chrono::Utc::now();
        let new_expires_at = now + chrono::Duration::hours(24);
        
        sqlx::query(
            r#"
            UPDATE whispers
            SET state = 'active',
                expires_at = ?1,
                last_activity_at = ?2
            WHERE id = ?3
            "#,
        )
        .bind(new_expires_at.to_rfc3339())
        .bind(now.to_rfc3339())
        .bind(whisper_id)
        .execute(pool)
        .await?;
        
        // Retrieve the updated whisper
        Self::get_whisper(pool, whisper_id)
            .await?
            .ok_or_else(|| anyhow::anyhow!("Whisper not found after accept"))
    }

    pub async fn decline_whisper(pool: &SqlitePool, whisper_id: &str) -> Result<WhisperSession, anyhow::Error> {
        sqlx::query(
            r#"
            UPDATE whispers
            SET state = 'declined'
            WHERE id = ?1
            "#,
        )
        .bind(whisper_id)
        .execute(pool)
        .await?;
        
        // Retrieve the updated whisper
        Self::get_whisper(pool, whisper_id)
            .await?
            .ok_or_else(|| anyhow::anyhow!("Whisper not found after decline"))
    }

    pub async fn end_whisper(pool: &SqlitePool, whisper_id: &str) -> Result<(), anyhow::Error> {
        sqlx::query(
            r#"
            UPDATE whispers
            SET state = 'ended'
            WHERE id = ?1
            "#,
        )
        .bind(whisper_id)
        .execute(pool)
        .await?;
        
        Ok(())
    }

    pub async fn extend_whisper(pool: &SqlitePool, whisper_id: &str, hours: i64) -> Result<WhisperSession, anyhow::Error> {
        // First get current whisper to check current expiry
        let whisper = Self::get_whisper(pool, whisper_id)
            .await?
            .ok_or_else(|| anyhow::anyhow!("Whisper not found"))?;
        
        let new_expires_at = whisper.expires_at + chrono::Duration::hours(hours);
        
        sqlx::query(
            r#"
            UPDATE whispers
            SET expires_at = ?1
            WHERE id = ?2
            "#,
        )
        .bind(new_expires_at.to_rfc3339())
        .bind(whisper_id)
        .execute(pool)
        .await?;
        
        // Retrieve the updated whisper
        Self::get_whisper(pool, whisper_id)
            .await?
            .ok_or_else(|| anyhow::anyhow!("Whisper not found after extend"))
    }

    pub async fn update_activity(pool: &SqlitePool, whisper_id: &str) -> Result<(), anyhow::Error> {
        let now = chrono::Utc::now().to_rfc3339();
        sqlx::query(
            r#"
            UPDATE whispers
            SET last_activity_at = ?1
            WHERE id = ?2
            "#,
        )
        .bind(&now)
        .bind(whisper_id)
        .execute(pool)
        .await?;
        
        Ok(())
    }

    pub async fn expire_whispers(pool: &SqlitePool) -> Result<usize, anyhow::Error> {
        let now = chrono::Utc::now().to_rfc3339();
        let result = sqlx::query(
            r#"
            UPDATE whispers
            SET state = 'ended'
            WHERE (state = 'pending' OR state = 'active')
              AND expires_at < ?1
            "#,
        )
        .bind(&now)
        .execute(pool)
        .await?;
        
        Ok(result.rows_affected() as usize)
    }

    fn row_to_whisper(row: sqlx::sqlite::SqliteRow) -> Result<WhisperSession, anyhow::Error> {
        let created_at_str: String = row.get("created_at");
        let expires_at_str: String = row.get("expires_at");
        let last_activity_at_str: String = row.get("last_activity_at");
        
        let state_str: String = row.get("state");
        // Remove quotes if present (from old JSON serialization)
        let state_str_clean = state_str.trim_matches('"');
        let state: WhisperState = match state_str_clean {
            "pending" => WhisperState::Pending,
            "active" => WhisperState::Active,
            "declined" => WhisperState::Declined,
            "ended" => WhisperState::Ended,
            _ => {
                // Try JSON deserialization as fallback
                serde_json::from_str(&format!("\"{}\"", state_str_clean))
                    .unwrap_or(WhisperState::Pending)
            }
        };
        
        Ok(WhisperSession {
            id: row.get("id"),
            sender_mask: row.get("sender_mask"),
            recipient_mask: row.get("recipient_mask"),
            room_id: row.get("room_id"),
            state,
            created_at: chrono::DateTime::parse_from_rfc3339(&created_at_str)?.with_timezone(&chrono::Utc),
            expires_at: chrono::DateTime::parse_from_rfc3339(&expires_at_str)?.with_timezone(&chrono::Utc),
            last_activity_at: chrono::DateTime::parse_from_rfc3339(&last_activity_at_str)?.with_timezone(&chrono::Utc),
        })
    }
}

