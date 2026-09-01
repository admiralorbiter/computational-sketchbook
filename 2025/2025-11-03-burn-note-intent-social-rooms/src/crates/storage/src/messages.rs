use sqlx::SqlitePool;
use sqlx::Row;
use anyhow::Result;

use core::{Message, MessageType, MediaInfo};

pub struct MessageRepository;

impl MessageRepository {
    pub async fn create_message(pool: &SqlitePool, message: Message) -> Result<Message, anyhow::Error> {
        let (media_url, media_type, media_size) = if let Some(ref media) = message.media {
            (Some(media.url.clone()), Some(media.media_type.clone()), Some(media.size as i64))
        } else {
            (None, None, None)
        };
        
        sqlx::query(
            r#"
            INSERT INTO messages (
                id, room_id, sender_mask, message_type, body,
                media_url, media_type, media_size,
                created_at, tombstoned, whisper_id, parent_post_id
            )
            VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12)
            "#,
        )
        .bind(&message.id)
        .bind(&message.room_id)
        .bind(&message.sender_mask)
        .bind(serde_json::to_string(&message.message_type).unwrap_or_else(|_| "text".to_string()))
        .bind(&message.body)
        .bind(&media_url)
        .bind(&media_type)
        .bind(&media_size)
        .bind(message.created_at.to_rfc3339())
        .bind(if message.tombstoned { 1 } else { 0 })
        .bind(&message.whisper_id)
        .bind(&message.parent_post_id)
        .execute(pool)
        .await?;
        
        Ok(message)
    }

    pub async fn get_messages(
        pool: &SqlitePool,
        room_id: &str,
        after: Option<&str>,
        limit: Option<u32>,
    ) -> Result<Vec<Message>, anyhow::Error> {
        let limit = limit.unwrap_or(50).min(100) as i64;
        
        let rows = if let Some(after_id) = after {
            sqlx::query(
                r#"
                SELECT id, room_id, sender_mask, message_type, body,
                       media_url, media_type, media_size,
                       created_at, tombstoned, whisper_id, parent_post_id
                FROM messages
                WHERE room_id = ?1 AND created_at > (
                    SELECT created_at FROM messages WHERE id = ?2
                ) AND tombstoned = 0
                ORDER BY created_at ASC
                LIMIT ?3
                "#,
            )
            .bind(room_id)
            .bind(after_id)
            .bind(limit)
            .fetch_all(pool)
            .await?
        } else {
            sqlx::query(
                r#"
                SELECT id, room_id, sender_mask, message_type, body,
                       media_url, media_type, media_size,
                       created_at, tombstoned, whisper_id, parent_post_id
                FROM messages
                WHERE room_id = ?1 AND tombstoned = 0
                ORDER BY created_at ASC
                LIMIT ?2
                "#,
            )
            .bind(room_id)
            .bind(limit)
            .fetch_all(pool)
            .await?
        };
        
        let mut messages = Vec::new();
        for row in rows {
            let message_type_str: String = row.get("message_type");
            let message_type: MessageType = serde_json::from_str(&message_type_str)
                .unwrap_or(MessageType::Text);
            
            let media = {
                let url: Option<String> = row.get("media_url");
                let mt: Option<String> = row.get("media_type");
                let size: Option<i64> = row.get("media_size");
                if let (Some(url), Some(media_type), Some(size)) = (url, mt, size) {
                    Some(MediaInfo {
                        url,
                        media_type,
                        size: size as u64,
                    })
                } else {
                    None
                }
            };
            
            messages.push(Message {
                id: row.get("id"),
                room_id: row.get("room_id"),
                sender_mask: row.get("sender_mask"),
                message_type,
                body: row.get("body"),
                media,
                created_at: {
                    let created_at_str: String = row.get("created_at");
                    chrono::DateTime::parse_from_rfc3339(&created_at_str)?.with_timezone(&chrono::Utc)
                },
                tombstoned: row.get::<i64, _>("tombstoned") != 0,
                whisper_id: row.get("whisper_id"),
                parent_post_id: row.get("parent_post_id"),
            });
        }
        
        Ok(messages)
    }

    pub async fn get_recent_messages(
        pool: &SqlitePool,
        room_id: &str,
        limit: u32,
    ) -> Result<Vec<Message>, anyhow::Error> {
        let limit = limit.min(100) as i64;
        
        let rows = sqlx::query(
            r#"
            SELECT id, room_id, sender_mask, message_type, body,
                   media_url, media_type, media_size,
                   created_at, tombstoned, whisper_id, parent_post_id
            FROM messages
            WHERE room_id = ?1 AND tombstoned = 0
            ORDER BY created_at DESC
            LIMIT ?2
            "#,
        )
        .bind(room_id)
        .bind(limit)
        .fetch_all(pool)
        .await?;
        
        let mut messages = Vec::new();
        for row in rows.into_iter().rev() { // Reverse to get chronological order
            let message_type_str: String = row.get("message_type");
            let message_type: MessageType = serde_json::from_str(&message_type_str)
                .unwrap_or(MessageType::Text);
            
            let media = {
                let url: Option<String> = row.get("media_url");
                let mt: Option<String> = row.get("media_type");
                let size: Option<i64> = row.get("media_size");
                if let (Some(url), Some(media_type), Some(size)) = (url, mt, size) {
                    Some(MediaInfo {
                        url,
                        media_type,
                        size: size as u64,
                    })
                } else {
                    None
                }
            };
            
            messages.push(Message {
                id: row.get("id"),
                room_id: row.get("room_id"),
                sender_mask: row.get("sender_mask"),
                message_type,
                body: row.get("body"),
                media,
                created_at: {
                    let created_at_str: String = row.get("created_at");
                    chrono::DateTime::parse_from_rfc3339(&created_at_str)?.with_timezone(&chrono::Utc)
                },
                tombstoned: row.get::<i64, _>("tombstoned") != 0,
                whisper_id: row.get("whisper_id"),
                parent_post_id: row.get("parent_post_id"),
            });
        }
        
        Ok(messages)
    }

    pub async fn get_posts(
        pool: &SqlitePool,
        room_id: &str,
        after: Option<&str>,
        limit: Option<u32>,
    ) -> Result<Vec<Message>, anyhow::Error> {
        let limit = limit.unwrap_or(50).min(50) as i64;
        
        let rows = if let Some(after_id) = after {
            sqlx::query(
                r#"
                SELECT id, room_id, sender_mask, message_type, body,
                       media_url, media_type, media_size,
                       created_at, tombstoned, whisper_id, parent_post_id
                FROM messages
                WHERE room_id = ?1 
                  AND message_type = ?2
                  AND parent_post_id IS NULL
                  AND created_at < (
                      SELECT created_at FROM messages WHERE id = ?3
                  )
                  AND tombstoned = 0
                ORDER BY created_at DESC
                LIMIT ?4
                "#,
            )
            .bind(room_id)
            .bind(serde_json::to_string(&MessageType::Post).unwrap_or_else(|_| "\"post\"".to_string()))
            .bind(after_id)
            .bind(limit)
            .fetch_all(pool)
            .await?
        } else {
            sqlx::query(
                r#"
                SELECT id, room_id, sender_mask, message_type, body,
                       media_url, media_type, media_size,
                       created_at, tombstoned, whisper_id, parent_post_id
                FROM messages
                WHERE room_id = ?1 
                  AND message_type = ?2
                  AND parent_post_id IS NULL
                  AND tombstoned = 0
                ORDER BY created_at DESC
                LIMIT ?3
                "#,
            )
            .bind(room_id)
            .bind(serde_json::to_string(&MessageType::Post).unwrap_or_else(|_| "\"post\"".to_string()))
            .bind(limit)
            .fetch_all(pool)
            .await?
        };
        
        let mut posts = Vec::new();
        for row in rows {
            let message_type_str: String = row.get("message_type");
            let message_type: MessageType = serde_json::from_str(&format!("\"{}\"", message_type_str))
                .unwrap_or(MessageType::Post);
            
            let media = {
                let url: Option<String> = row.get("media_url");
                let mt: Option<String> = row.get("media_type");
                let size: Option<i64> = row.get("media_size");
                if let (Some(url), Some(media_type), Some(size)) = (url, mt, size) {
                    Some(MediaInfo {
                        url,
                        media_type,
                        size: size as u64,
                    })
                } else {
                    None
                }
            };
            
            posts.push(Message {
                id: row.get("id"),
                room_id: row.get("room_id"),
                sender_mask: row.get("sender_mask"),
                message_type,
                body: row.get("body"),
                media,
                created_at: {
                    let created_at_str: String = row.get("created_at");
                    chrono::DateTime::parse_from_rfc3339(&created_at_str)?.with_timezone(&chrono::Utc)
                },
                tombstoned: row.get::<i64, _>("tombstoned") != 0,
                whisper_id: row.get("whisper_id"),
                parent_post_id: row.get("parent_post_id"),
            });
        }
        
        Ok(posts)
    }

    pub async fn get_post_replies(
        pool: &SqlitePool,
        post_id: &str,
        after: Option<&str>,
        limit: Option<u32>,
    ) -> Result<Vec<Message>, anyhow::Error> {
        let limit = limit.unwrap_or(50).min(50) as i64;
        
        let rows = if let Some(after_id) = after {
            sqlx::query(
                r#"
                SELECT id, room_id, sender_mask, message_type, body,
                       media_url, media_type, media_size,
                       created_at, tombstoned, whisper_id, parent_post_id
                FROM messages
                WHERE parent_post_id = ?1
                  AND created_at > (
                      SELECT created_at FROM messages WHERE id = ?2
                  )
                  AND tombstoned = 0
                ORDER BY created_at ASC
                LIMIT ?3
                "#,
            )
            .bind(post_id)
            .bind(after_id)
            .bind(limit)
            .fetch_all(pool)
            .await?
        } else {
            sqlx::query(
                r#"
                SELECT id, room_id, sender_mask, message_type, body,
                       media_url, media_type, media_size,
                       created_at, tombstoned, whisper_id, parent_post_id
                FROM messages
                WHERE parent_post_id = ?1
                  AND tombstoned = 0
                ORDER BY created_at ASC
                LIMIT ?2
                "#,
            )
            .bind(post_id)
            .bind(limit)
            .fetch_all(pool)
            .await?
        };
        
        let mut replies = Vec::new();
        for row in rows {
            let message_type_str: String = row.get("message_type");
            let message_type: MessageType = serde_json::from_str(&format!("\"{}\"", message_type_str))
                .unwrap_or(MessageType::Post);
            
            let media = {
                let url: Option<String> = row.get("media_url");
                let mt: Option<String> = row.get("media_type");
                let size: Option<i64> = row.get("media_size");
                if let (Some(url), Some(media_type), Some(size)) = (url, mt, size) {
                    Some(MediaInfo {
                        url,
                        media_type,
                        size: size as u64,
                    })
                } else {
                    None
                }
            };
            
            replies.push(Message {
                id: row.get("id"),
                room_id: row.get("room_id"),
                sender_mask: row.get("sender_mask"),
                message_type,
                body: row.get("body"),
                media,
                created_at: {
                    let created_at_str: String = row.get("created_at");
                    chrono::DateTime::parse_from_rfc3339(&created_at_str)?.with_timezone(&chrono::Utc)
                },
                tombstoned: row.get::<i64, _>("tombstoned") != 0,
                whisper_id: row.get("whisper_id"),
                parent_post_id: row.get("parent_post_id"),
            });
        }
        
        Ok(replies)
    }

    pub async fn get_reply_count(
        pool: &SqlitePool,
        post_id: &str,
    ) -> Result<i64, anyhow::Error> {
        let row = sqlx::query(
            r#"
            SELECT COUNT(*) as count
            FROM messages
            WHERE parent_post_id = ?1 AND tombstoned = 0
            "#,
        )
        .bind(post_id)
        .fetch_one(pool)
        .await?;
        
        Ok(row.get::<i64, _>("count"))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use sqlx::sqlite::SqliteConnectOptions;
    use sqlx::SqlitePool;
    use std::str::FromStr;
    use crate::RoomRepository;
    use core::PolicyFlags;

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
    fn test_create_message() {
        run_async_test(async {
        let pool = setup_test_db().await;
        let room_id = create_test_room(&pool).await;
        
        let message = Message::new(
            room_id.clone(),
            "user123".to_string(),
            MessageType::Text,
            "Hello, world!".to_string(),
            None,
            None,
        ).unwrap();
        
        let created = MessageRepository::create_message(&pool, message.clone()).await.unwrap();
        assert_eq!(created.id, message.id);
        assert_eq!(created.body, "Hello, world!");
        assert_eq!(created.room_id, room_id);
        });
    }

    #[test]
    fn test_get_messages() {
        run_async_test(async {
        let pool = setup_test_db().await;
        let room_id = create_test_room(&pool).await;
        
        let msg1 = Message::new(
            room_id.clone(),
            "user1".to_string(),
            MessageType::Text,
            "First message".to_string(),
            None,
            None,
        ).unwrap();
        
        let msg2 = Message::new(
            room_id.clone(),
            "user2".to_string(),
            MessageType::Text,
            "Second message".to_string(),
            None,
            None,
        ).unwrap();
        
        MessageRepository::create_message(&pool, msg1).await.unwrap();
        MessageRepository::create_message(&pool, msg2).await.unwrap();
        
        let messages = MessageRepository::get_messages(&pool, &room_id, None, None).await.unwrap();
        assert_eq!(messages.len(), 2);
        assert_eq!(messages[0].body, "First message");
        assert_eq!(messages[1].body, "Second message");
        });
    }

    #[test]
    fn test_get_messages_with_limit() {
        run_async_test(async {
        let pool = setup_test_db().await;
        let room_id = create_test_room(&pool).await;
        
        for i in 0..5 {
            let msg = Message::new(
                room_id.clone(),
                format!("user{}", i),
                MessageType::Text,
                format!("Message {}", i),
                None,
                None,
            ).unwrap();
            MessageRepository::create_message(&pool, msg).await.unwrap();
        }
        
        let messages = MessageRepository::get_messages(&pool, &room_id, None, Some(3)).await.unwrap();
        assert_eq!(messages.len(), 3);
        });
    }

    #[test]
    fn test_get_messages_with_after() {
        run_async_test(async {
        let pool = setup_test_db().await;
        let room_id = create_test_room(&pool).await;
        
        let msg1 = Message::new(
            room_id.clone(),
            "user1".to_string(),
            MessageType::Text,
            "First".to_string(),
            None,
            None,
        ).unwrap();
        
        let msg2 = Message::new(
            room_id.clone(),
            "user2".to_string(),
            MessageType::Text,
            "Second".to_string(),
            None,
            None,
        ).unwrap();
        
        let created1 = MessageRepository::create_message(&pool, msg1).await.unwrap();
        MessageRepository::create_message(&pool, msg2).await.unwrap();
        
        let messages = MessageRepository::get_messages(&pool, &room_id, Some(&created1.id), None).await.unwrap();
        assert_eq!(messages.len(), 1);
        assert_eq!(messages[0].body, "Second");
        });
    }

    #[test]
    fn test_get_empty_messages() {
        run_async_test(async {
        let pool = setup_test_db().await;
        let room_id = create_test_room(&pool).await;
        
        let messages = MessageRepository::get_messages(&pool, &room_id, None, None).await.unwrap();
        assert_eq!(messages.len(), 0);
        });
    }
}