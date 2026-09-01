use sqlx::SqlitePool;
use sqlx::Row;
use anyhow::Result;
use chrono::Utc;

use core::{Highlight, HighlightReferenceType};

pub struct HighlightRepository;

impl HighlightRepository {
    pub async fn create_highlight(pool: &SqlitePool, highlight: Highlight) -> Result<Highlight, anyhow::Error> {
        sqlx::query(
            r#"
            INSERT INTO highlights (
                id, room_id, title, reference_type, reference_id,
                curator_mask, created_at, is_auto
            )
            VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)
            "#,
        )
        .bind(&highlight.id)
        .bind(&highlight.room_id)
        .bind(&highlight.title)
        .bind(serde_json::to_string(&highlight.reference_type).unwrap_or_else(|_| "standalone".to_string()))
        .bind(&highlight.reference_id)
        .bind(&highlight.curator_mask)
        .bind(highlight.created_at.to_rfc3339())
        .bind(if highlight.is_auto { 1 } else { 0 })
        .execute(pool)
        .await?;
        
        Ok(highlight)
    }

    pub async fn get_highlights(
        pool: &SqlitePool,
        room_id: &str,
        after: Option<&str>,
        limit: Option<u32>,
        last_24h: bool,
    ) -> Result<Vec<Highlight>, anyhow::Error> {
        let limit = limit.unwrap_or(50).min(50) as i64;
        
        let cutoff_time = if last_24h {
            Some(Utc::now() - chrono::Duration::hours(24))
        } else {
            None
        };
        
        let rows = if let Some(after_id) = after {
            let query = if let Some(cutoff) = cutoff_time {
                sqlx::query(
                    r#"
                    SELECT id, room_id, title, reference_type, reference_id,
                           curator_mask, created_at, is_auto
                    FROM highlights
                    WHERE room_id = ?1 
                      AND created_at >= ?2
                      AND created_at < (
                          SELECT created_at FROM highlights WHERE id = ?3
                      )
                    ORDER BY created_at DESC
                    LIMIT ?4
                    "#,
                )
                .bind(room_id)
                .bind(cutoff.to_rfc3339())
                .bind(after_id)
                .bind(limit)
            } else {
                sqlx::query(
                    r#"
                    SELECT id, room_id, title, reference_type, reference_id,
                           curator_mask, created_at, is_auto
                    FROM highlights
                    WHERE room_id = ?1 
                      AND created_at < (
                          SELECT created_at FROM highlights WHERE id = ?2
                      )
                    ORDER BY created_at DESC
                    LIMIT ?3
                    "#,
                )
                .bind(room_id)
                .bind(after_id)
                .bind(limit)
            };
            query.fetch_all(pool).await?
        } else {
            let query = if let Some(cutoff) = cutoff_time {
                sqlx::query(
                    r#"
                    SELECT id, room_id, title, reference_type, reference_id,
                           curator_mask, created_at, is_auto
                    FROM highlights
                    WHERE room_id = ?1 
                      AND created_at >= ?2
                    ORDER BY created_at DESC
                    LIMIT ?3
                    "#,
                )
                .bind(room_id)
                .bind(cutoff.to_rfc3339())
                .bind(limit)
            } else {
                sqlx::query(
                    r#"
                    SELECT id, room_id, title, reference_type, reference_id,
                           curator_mask, created_at, is_auto
                    FROM highlights
                    WHERE room_id = ?1
                    ORDER BY created_at DESC
                    LIMIT ?2
                    "#,
                )
                .bind(room_id)
                .bind(limit)
            };
            query.fetch_all(pool).await?
        };
        
        let mut highlights = Vec::new();
        for row in rows {
            let reference_type_str: String = row.get("reference_type");
            let reference_type: HighlightReferenceType = serde_json::from_str(&format!("\"{}\"", reference_type_str))
                .unwrap_or(HighlightReferenceType::Standalone);
            
            highlights.push(Highlight {
                id: row.get("id"),
                room_id: row.get("room_id"),
                title: row.get("title"),
                reference_type,
                reference_id: row.get("reference_id"),
                curator_mask: row.get("curator_mask"),
                created_at: {
                    let created_at_str: String = row.get("created_at");
                    chrono::DateTime::parse_from_rfc3339(&created_at_str)?.with_timezone(&chrono::Utc)
                },
                is_auto: row.get::<i64, _>("is_auto") != 0,
            });
        }
        
        Ok(highlights)
    }

    pub async fn get_highlights_by_reference(
        pool: &SqlitePool,
        reference_id: &str,
    ) -> Result<Vec<Highlight>, anyhow::Error> {
        let rows = sqlx::query(
            r#"
            SELECT id, room_id, title, reference_type, reference_id,
                   curator_mask, created_at, is_auto
            FROM highlights
            WHERE reference_id = ?1
            ORDER BY created_at DESC
            "#,
        )
        .bind(reference_id)
        .fetch_all(pool)
        .await?;
        
        let mut highlights = Vec::new();
        for row in rows {
            let reference_type_str: String = row.get("reference_type");
            let reference_type: HighlightReferenceType = serde_json::from_str(&format!("\"{}\"", reference_type_str))
                .unwrap_or(HighlightReferenceType::Standalone);
            
            highlights.push(Highlight {
                id: row.get("id"),
                room_id: row.get("room_id"),
                title: row.get("title"),
                reference_type,
                reference_id: row.get("reference_id"),
                curator_mask: row.get("curator_mask"),
                created_at: {
                    let created_at_str: String = row.get("created_at");
                    chrono::DateTime::parse_from_rfc3339(&created_at_str)?.with_timezone(&chrono::Utc)
                },
                is_auto: row.get::<i64, _>("is_auto") != 0,
            });
        }
        
        Ok(highlights)
    }

    pub async fn delete_highlight(
        pool: &SqlitePool,
        highlight_id: &str,
    ) -> Result<bool, anyhow::Error> {
        let result = sqlx::query("DELETE FROM highlights WHERE id = ?1")
            .bind(highlight_id)
            .execute(pool)
            .await?;
        
        Ok(result.rows_affected() > 0)
    }

    pub async fn get_highlight_by_id(
        pool: &SqlitePool,
        highlight_id: &str,
    ) -> Result<Option<Highlight>, anyhow::Error> {
        let row = sqlx::query(
            r#"
            SELECT id, room_id, title, reference_type, reference_id,
                   curator_mask, created_at, is_auto
            FROM highlights
            WHERE id = ?1
            "#,
        )
        .bind(highlight_id)
        .fetch_optional(pool)
        .await?;
        
        if let Some(row) = row {
            let reference_type_str: String = row.get("reference_type");
            let reference_type: HighlightReferenceType = serde_json::from_str(&format!("\"{}\"", reference_type_str))
                .unwrap_or(HighlightReferenceType::Standalone);
            
            Ok(Some(Highlight {
                id: row.get("id"),
                room_id: row.get("room_id"),
                title: row.get("title"),
                reference_type,
                reference_id: row.get("reference_id"),
                curator_mask: row.get("curator_mask"),
                created_at: {
                    let created_at_str: String = row.get("created_at");
                    chrono::DateTime::parse_from_rfc3339(&created_at_str)?.with_timezone(&chrono::Utc)
                },
                is_auto: row.get::<i64, _>("is_auto") != 0,
            }))
        } else {
            Ok(None)
        }
    }

    pub async fn maybe_auto_highlight_post(
        pool: &SqlitePool,
        post_id: &str,
        room_id: &str,
    ) -> Result<Option<Highlight>, anyhow::Error> {
        // Check if post already has a highlight
        let existing = sqlx::query(
            "SELECT COUNT(*) as count FROM highlights WHERE reference_id = ?1 AND reference_type = 'post'"
        )
        .bind(post_id)
        .fetch_one(pool)
        .await?;
        
        let count: i64 = existing.get("count");
        if count > 0 {
            return Ok(None); // Already highlighted
        }
        
        // Check reply count
        use crate::MessageRepository;
        let reply_count = MessageRepository::get_reply_count(pool, post_id).await?;
        
        if reply_count >= 5 {
            // Auto-create highlight
            let post = sqlx::query("SELECT body FROM messages WHERE id = ?1")
                .bind(post_id)
                .fetch_optional(pool)
                .await?;
            
            let title = if let Some(row) = post {
                let body: String = row.get("body");
                // Create title from first 50 chars of post body
                let truncated = if body.len() > 50 {
                    format!("{}...", &body[..50])
                } else {
                    body
                };
                format!("Popular post: {}", truncated)
            } else {
                "Popular discussion".to_string()
            };
            
            let highlight = Highlight::new_auto(
                room_id.to_string(),
                title,
                HighlightReferenceType::Post,
                Some(post_id.to_string()),
            )?;
            
            return Ok(Some(highlight));
        }
        
        Ok(None)
    }
}

