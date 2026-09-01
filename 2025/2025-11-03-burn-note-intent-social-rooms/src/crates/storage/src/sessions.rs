use sqlx::SqlitePool;
use sqlx::Row;
use anyhow::Result;

use core::UserSession;

pub struct SessionRepository;

impl SessionRepository {
    pub async fn create_session(pool: &SqlitePool, session: UserSession) -> Result<UserSession, anyhow::Error> {
        sqlx::query(
            r#"
            INSERT INTO sessions (id, room_id, session_mask, created_at, expires_at)
            VALUES (?1, ?2, ?3, ?4, ?5)
            "#,
        )
        .bind(&session.id)
        .bind(&session.room_id)
        .bind(&session.session_mask)
        .bind(session.created_at.to_rfc3339())
        .bind(session.expires_at.to_rfc3339())
        .execute(pool)
        .await?;
        
        Ok(session)
    }

    pub async fn get_session(pool: &SqlitePool, session_id: &str) -> Result<Option<UserSession>, anyhow::Error> {
        let row = sqlx::query(
            r#"
            SELECT id, room_id, session_mask, created_at, expires_at
            FROM sessions
            WHERE id = ?1
            "#,
        )
        .bind(session_id)
        .fetch_optional(pool)
        .await?;
        
        if let Some(row) = row {
            let created_at_str: String = row.get("created_at");
            let expires_at_str: String = row.get("expires_at");
            Ok(Some(UserSession {
                id: row.get("id"),
                room_id: row.get("room_id"),
                session_mask: row.get("session_mask"),
                created_at: chrono::DateTime::parse_from_rfc3339(&created_at_str)?.with_timezone(&chrono::Utc),
                expires_at: chrono::DateTime::parse_from_rfc3339(&expires_at_str)?.with_timezone(&chrono::Utc),
            }))
        } else {
            Ok(None)
        }
    }

    pub async fn get_session_by_mask(pool: &SqlitePool, room_id: &str, mask: &str) -> Result<Option<UserSession>, anyhow::Error> {
        let row = sqlx::query(
            r#"
            SELECT id, room_id, session_mask, created_at, expires_at
            FROM sessions
            WHERE room_id = ?1 AND session_mask = ?2
            "#,
        )
        .bind(room_id)
        .bind(mask)
        .fetch_optional(pool)
        .await?;
        
        if let Some(row) = row {
            let created_at_str: String = row.get("created_at");
            let expires_at_str: String = row.get("expires_at");
            Ok(Some(UserSession {
                id: row.get("id"),
                room_id: row.get("room_id"),
                session_mask: row.get("session_mask"),
                created_at: chrono::DateTime::parse_from_rfc3339(&created_at_str)?.with_timezone(&chrono::Utc),
                expires_at: chrono::DateTime::parse_from_rfc3339(&expires_at_str)?.with_timezone(&chrono::Utc),
            }))
        } else {
            Ok(None)
        }
    }

    pub async fn delete_session(pool: &SqlitePool, session_id: &str) -> Result<(), anyhow::Error> {
        sqlx::query(
            r#"
            DELETE FROM sessions
            WHERE id = ?1
            "#,
        )
        .bind(session_id)
        .execute(pool)
        .await?;
        
        Ok(())
    }

    pub async fn expire_sessions(pool: &SqlitePool) -> Result<usize, anyhow::Error> {
        let now = chrono::Utc::now().to_rfc3339();
        let result = sqlx::query(
            r#"
            DELETE FROM sessions
            WHERE expires_at < ?1
            "#,
        )
        .bind(&now)
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
    use crate::RoomRepository;
    use core::{PolicyFlags, UserSession};

    // Helper to run async tests without tokio::test macro (avoids core crate name conflict)
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
        
        // Initialize schema
        let schema = include_str!("schema.sql");
        for statement in schema.split(';') {
            let statement = statement.trim();
            if statement.is_empty() || statement.starts_with("--") {
                continue;
            }
            sqlx::query(statement).execute(&pool).await.unwrap();
        }
        
        pool
    }

    async fn create_test_room(pool: &SqlitePool) -> String {
        let room = RoomRepository::create_room(
            pool,
            "Test Room".to_string(),
            "en".to_string(),
            PolicyFlags::default(),
        ).await.unwrap();
        room.id
    }

    #[test]
    fn test_create_session() {
        run_async_test(async {
        let pool = setup_test_db().await;
        let room_id = create_test_room(&pool).await;
        
        let session = UserSession::new(room_id.clone(), 24);
        let created = SessionRepository::create_session(&pool, session.clone()).await.unwrap();
        
        assert_eq!(created.id, session.id);
        assert_eq!(created.room_id, room_id);
        });
    }

    #[test]
    fn test_get_session() {
        run_async_test(async {
        let pool = setup_test_db().await;
        let room_id = create_test_room(&pool).await;
        
        let session = UserSession::new(room_id.clone(), 24);
        let created = SessionRepository::create_session(&pool, session.clone()).await.unwrap();
        
        let retrieved = SessionRepository::get_session(&pool, &created.id).await.unwrap();
        assert!(retrieved.is_some());
        let session = retrieved.unwrap();
        assert_eq!(session.id, created.id);
        assert_eq!(session.room_id, room_id);
        });
    }

    #[test]
    fn test_get_nonexistent_session() {
        run_async_test(async {
        let pool = setup_test_db().await;
        
        let result = SessionRepository::get_session(&pool, "nonexistent-id").await.unwrap();
        assert!(result.is_none());
        });
    }

    #[test]
    fn test_get_session_by_mask() {
        run_async_test(async {
        let pool = setup_test_db().await;
        let room_id = create_test_room(&pool).await;
        
        let session = UserSession::new(room_id.clone(), 24);
        let created = SessionRepository::create_session(&pool, session.clone()).await.unwrap();
        
        let retrieved = SessionRepository::get_session_by_mask(&pool, &room_id, &created.session_mask).await.unwrap();
        assert!(retrieved.is_some());
        let session = retrieved.unwrap();
        assert_eq!(session.id, created.id);
        assert_eq!(session.session_mask, created.session_mask);
        });
    }

    #[test]
    fn test_delete_session() {
        run_async_test(async {
        let pool = setup_test_db().await;
        let room_id = create_test_room(&pool).await;
        
        let session = UserSession::new(room_id.clone(), 24);
        let created = SessionRepository::create_session(&pool, session.clone()).await.unwrap();
        
        SessionRepository::delete_session(&pool, &created.id).await.unwrap();
        
        let result = SessionRepository::get_session(&pool, &created.id).await.unwrap();
        assert!(result.is_none());
        });
    }

    #[test]
    fn test_expire_sessions() {
        run_async_test(async {
        let pool = setup_test_db().await;
        let room_id = create_test_room(&pool).await;
        
        // Create a session that should expire (0 hours TTL means it expires immediately)
        let session = UserSession::new(room_id.clone(), 0);
        SessionRepository::create_session(&pool, session).await.unwrap();
        
        // Wait a moment and then expire
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        let expired_count = SessionRepository::expire_sessions(&pool).await.unwrap();
        
        // Should have expired at least one session
        assert!(expired_count >= 1);
        });
    }
}