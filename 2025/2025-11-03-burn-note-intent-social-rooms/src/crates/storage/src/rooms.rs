use sqlx::SqlitePool;
use sqlx::Row;
use anyhow::Result;

use core::{PolicyFlags, Room, ValidationError};

pub struct RoomRepository;

impl RoomRepository {
    pub async fn create_room(
        pool: &SqlitePool,
        title: String,
        language: String,
        policy_flags: PolicyFlags,
    ) -> Result<Room, ValidationError> {
        let room = Room::new(title, language, policy_flags)?;
        
        sqlx::query(
            r#"
            INSERT INTO rooms (id, title, language, policy_flags, created_at, updated_at, tags, description, activity_score, member_count)
            VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)
            "#,
        )
        .bind(&room.id)
        .bind(&room.title)
        .bind(&room.language)
        .bind(room.policy_flags.bitset() as i64)
        .bind(room.created_at.to_rfc3339())
        .bind(room.updated_at.to_rfc3339())
        .bind(&room.tags)
        .bind(&room.description)
        .bind(room.activity_score)
        .bind(room.member_count)
        .execute(pool)
        .await
        .map_err(|e| ValidationError::Failed(format!("Failed to create room: {}", e)))?;
        
        Ok(room)
    }

    pub async fn get_room(pool: &SqlitePool, room_id: &str) -> Result<Option<Room>, anyhow::Error> {
        let row = sqlx::query(
            r#"
            SELECT id, title, language, policy_flags, created_at, updated_at, tags, description, activity_score, member_count
            FROM rooms
            WHERE id = ?1
            "#,
        )
        .bind(room_id)
        .fetch_optional(pool)
        .await?;
        
        if let Some(row) = row {
            let created_at_str: String = row.get("created_at");
            let updated_at_str: String = row.get("updated_at");
            // Handle potential NULL values for new columns (migration compatibility)
            let tags: String = row.try_get("tags").unwrap_or_default();
            let description: String = row.try_get("description").unwrap_or_default();
            let activity_score: f64 = row.try_get("activity_score").unwrap_or(0.0);
            let member_count: i32 = row.try_get("member_count").unwrap_or(0);
            Ok(Some(Room {
                id: row.get("id"),
                title: row.get("title"),
                language: row.get("language"),
                policy_flags: PolicyFlags::from_bitset(row.get::<i64, _>("policy_flags") as u8),
                created_at: chrono::DateTime::parse_from_rfc3339(&created_at_str)?.with_timezone(&chrono::Utc),
                updated_at: chrono::DateTime::parse_from_rfc3339(&updated_at_str)?.with_timezone(&chrono::Utc),
                tags,
                description,
                activity_score,
                member_count,
            }))
        } else {
            Ok(None)
        }
    }

    pub async fn list_rooms(pool: &SqlitePool) -> Result<Vec<Room>, anyhow::Error> {
        let rows = sqlx::query(
            r#"
            SELECT id, title, language, policy_flags, created_at, updated_at, tags, description, activity_score, member_count
            FROM rooms
            ORDER BY created_at DESC
            "#
        )
        .fetch_all(pool)
        .await?;
        
        let mut rooms = Vec::new();
        for row in rows {
            let created_at_str: String = row.get("created_at");
            let updated_at_str: String = row.get("updated_at");
            // Handle potential NULL values for new columns (migration compatibility)
            let tags: String = row.try_get("tags").unwrap_or_default();
            let description: String = row.try_get("description").unwrap_or_default();
            let activity_score: f64 = row.try_get("activity_score").unwrap_or(0.0);
            let member_count: i32 = row.try_get("member_count").unwrap_or(0);
            rooms.push(Room {
                id: row.get("id"),
                title: row.get("title"),
                language: row.get("language"),
                policy_flags: PolicyFlags::from_bitset(row.get::<i64, _>("policy_flags") as u8),
                created_at: chrono::DateTime::parse_from_rfc3339(&created_at_str)?.with_timezone(&chrono::Utc),
                updated_at: chrono::DateTime::parse_from_rfc3339(&updated_at_str)?.with_timezone(&chrono::Utc),
                tags,
                description,
                activity_score,
                member_count,
            });
        }
        
        Ok(rooms)
    }

    pub async fn update_activity_score(pool: &SqlitePool, room_id: &str, score: f64) -> Result<(), anyhow::Error> {
        let score = score.max(0.0).min(1.0);
        sqlx::query(
            r#"
            UPDATE rooms
            SET activity_score = ?1, updated_at = ?2
            WHERE id = ?3
            "#,
        )
        .bind(score)
        .bind(chrono::Utc::now().to_rfc3339())
        .bind(room_id)
        .execute(pool)
        .await?;
        Ok(())
    }

    pub async fn update_member_count(pool: &SqlitePool, room_id: &str, count: i32) -> Result<(), anyhow::Error> {
        let count = count.max(0);
        sqlx::query(
            r#"
            UPDATE rooms
            SET member_count = ?1, updated_at = ?2
            WHERE id = ?3
            "#,
        )
        .bind(count)
        .bind(chrono::Utc::now().to_rfc3339())
        .bind(room_id)
        .execute(pool)
        .await?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use sqlx::sqlite::SqliteConnectOptions;
    use sqlx::SqlitePool;
    use std::str::FromStr;

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

    #[test]
    fn test_create_room() {
        run_async_test(async {
        let pool = setup_test_db().await;
        
        let room = RoomRepository::create_room(
            &pool,
            "Test Room".to_string(),
            "en".to_string(),
            PolicyFlags::default(),
        ).await.unwrap();
        
        assert_eq!(room.title, "Test Room");
        assert_eq!(room.language, "en");
        });
    }

    #[test]
    fn test_get_room() {
        run_async_test(async {
        let pool = setup_test_db().await;
        
        let created = RoomRepository::create_room(
            &pool,
            "Test Room".to_string(),
            "en".to_string(),
            PolicyFlags::default(),
        ).await.unwrap();
        
        let retrieved = RoomRepository::get_room(&pool, &created.id).await.unwrap();
        assert!(retrieved.is_some());
        let room = retrieved.unwrap();
        assert_eq!(room.id, created.id);
        assert_eq!(room.title, "Test Room");
        });
    }

    #[test]
    fn test_get_nonexistent_room() {
        run_async_test(async {
        let pool = setup_test_db().await;
        
        let result = RoomRepository::get_room(&pool, "nonexistent-id").await.unwrap();
        assert!(result.is_none());
        });
    }

    #[test]
    fn test_list_rooms() {
        run_async_test(async {
        let pool = setup_test_db().await;
        
        RoomRepository::create_room(
            &pool,
            "Room 1".to_string(),
            "en".to_string(),
            PolicyFlags::default(),
        ).await.unwrap();
        
        RoomRepository::create_room(
            &pool,
            "Room 2".to_string(),
            "en".to_string(),
            PolicyFlags::default(),
        ).await.unwrap();
        
        let rooms = RoomRepository::list_rooms(&pool).await.unwrap();
        assert_eq!(rooms.len(), 2);
        assert!(rooms.iter().any(|r| r.title == "Room 1"));
        assert!(rooms.iter().any(|r| r.title == "Room 2"));
        });
    }

    #[test]
    fn test_list_empty_rooms() {
        run_async_test(async {
        let pool = setup_test_db().await;
        
        let rooms = RoomRepository::list_rooms(&pool).await.unwrap();
        assert_eq!(rooms.len(), 0);
        });
    }
}