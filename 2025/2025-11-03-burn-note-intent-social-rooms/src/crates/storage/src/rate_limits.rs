use sqlx::SqlitePool;
use sqlx::Row;
use anyhow::Result;
use chrono::{DateTime, Utc};
use uuid::Uuid;

pub struct RateLimitRepository;

#[derive(Debug, Clone)]
pub struct RateLimitEvent {
    pub id: String,
    pub session_id: String,
    pub action_type: String,
    pub timestamp: DateTime<Utc>,
    pub bucket: String,
}

impl RateLimitRepository {
    /// Check if an action is allowed within the rate limit
    /// Returns true if allowed, false if rate limited
    pub async fn check_rate_limit(
        pool: &SqlitePool,
        session_id: &str,
        action_type: &str,
        window_seconds: i64,
        max_count: usize,
    ) -> Result<bool> {
        let cutoff_time = Utc::now() - chrono::Duration::seconds(window_seconds);
        
        let count: i64 = sqlx::query(
            r#"
            SELECT COUNT(*) as count
            FROM rate_limit_events
            WHERE session_id = ?1 AND action_type = ?2 AND timestamp > ?3
            "#,
        )
        .bind(session_id)
        .bind(action_type)
        .bind(cutoff_time.to_rfc3339())
        .fetch_one(pool)
        .await
        .map(|row: sqlx::sqlite::SqliteRow| row.get::<i64, _>("count"))?;

        Ok((count as usize) < max_count)
    }

    /// Record an action for rate limiting
    pub async fn record_action(
        pool: &SqlitePool,
        session_id: &str,
        action_type: &str,
        bucket: &str,
    ) -> Result<()> {
        let event = RateLimitEvent {
            id: Uuid::new_v4().to_string(),
            session_id: session_id.to_string(),
            action_type: action_type.to_string(),
            timestamp: Utc::now(),
            bucket: bucket.to_string(),
        };

        sqlx::query(
            r#"
            INSERT INTO rate_limit_events (id, session_id, action_type, timestamp, bucket)
            VALUES (?1, ?2, ?3, ?4, ?5)
            "#,
        )
        .bind(&event.id)
        .bind(&event.session_id)
        .bind(&event.action_type)
        .bind(event.timestamp.to_rfc3339())
        .bind(&event.bucket)
        .execute(pool)
        .await?;

        Ok(())
    }

    /// Clean up old rate limit events (older than specified days)
    pub async fn cleanup_old_events(pool: &SqlitePool, days_old: i64) -> Result<usize> {
        let cutoff_time = Utc::now() - chrono::Duration::days(days_old);
        let result = sqlx::query(
            r#"
            DELETE FROM rate_limit_events
            WHERE timestamp < ?1
            "#,
        )
        .bind(cutoff_time.to_rfc3339())
        .execute(pool)
        .await?;

        Ok(result.rows_affected() as usize)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use sqlx::sqlite::SqliteConnectOptions;
    use sqlx::SqlitePool;
    use std::str::FromStr;

    fn run_async_test<F>(f: F)
    where
        F: std::future::Future<Output = ()>,
    {
        tokio::runtime::Runtime::new().unwrap().block_on(f);
    }

    async fn setup_test_db() -> SqlitePool {
        let pool = SqlitePool::connect_with(
            SqliteConnectOptions::from_str("sqlite::memory:").unwrap()
        ).await.unwrap();
        
        // Initialize schema (just the rate_limit_events table for these tests)
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS rate_limit_events (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                bucket TEXT NOT NULL
            )
            "#
        )
        .execute(&pool)
        .await
        .unwrap();
        
        pool
    }

    #[test]
    fn test_check_rate_limit_allows() {
        run_async_test(async {
            let pool = setup_test_db().await;
            let session_id = "test-session";
            let action_type = "join";

            // Should be allowed (no events yet)
            let allowed = RateLimitRepository::check_rate_limit(&pool, session_id, action_type, 60, 5)
                .await
                .unwrap();
            assert!(allowed);
        });
    }

    #[test]
    fn test_check_rate_limit_blocks_after_limit() {
        run_async_test(async {
            let pool = setup_test_db().await;
            let session_id = "test-session";
            let action_type = "join";
            let max_count = 2;

            // Record 2 actions (at limit)
            RateLimitRepository::record_action(&pool, session_id, action_type, "bucket1")
                .await
                .unwrap();
            RateLimitRepository::record_action(&pool, session_id, action_type, "bucket1")
                .await
                .unwrap();

            // Should be blocked (at limit)
            let allowed = RateLimitRepository::check_rate_limit(&pool, session_id, action_type, 60, max_count)
                .await
                .unwrap();
            assert!(!allowed);
        });
    }
}
