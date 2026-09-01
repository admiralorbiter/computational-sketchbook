use sqlx::SqlitePool;
use sqlx::Row;
use anyhow::Result;
use chrono::Utc;

use core::Resource;

pub struct ResourceRepository;

impl ResourceRepository {
    pub async fn create_resource(pool: &SqlitePool, resource: Resource) -> Result<Resource, anyhow::Error> {
        sqlx::query(
            r#"
            INSERT INTO resources (
                id, room_id, title, url, description, category,
                curator_mask, created_at, updated_at, is_verified
            )
            VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)
            "#,
        )
        .bind(&resource.id)
        .bind(&resource.room_id)
        .bind(&resource.title)
        .bind(&resource.url)
        .bind(&resource.description)
        .bind(&resource.category)
        .bind(&resource.curator_mask)
        .bind(resource.created_at.to_rfc3339())
        .bind(resource.updated_at.to_rfc3339())
        .bind(if resource.is_verified { 1 } else { 0 })
        .execute(pool)
        .await?;
        
        Ok(resource)
    }

    pub async fn get_resources(
        pool: &SqlitePool,
        room_id: &str,
        after: Option<&str>,
        limit: Option<u32>,
        category: Option<&str>,
    ) -> Result<Vec<Resource>, anyhow::Error> {
        let limit = limit.unwrap_or(50).min(50) as i64;
        
        let rows = if let Some(after_id) = after {
            if let Some(cat) = category {
                sqlx::query(
                    r#"
                    SELECT id, room_id, title, url, description, category,
                           curator_mask, created_at, updated_at, is_verified
                    FROM resources
                    WHERE room_id = ?1 
                      AND category = ?2
                      AND created_at < (
                          SELECT created_at FROM resources WHERE id = ?3
                      )
                    ORDER BY created_at DESC
                    LIMIT ?4
                    "#,
                )
                .bind(room_id)
                .bind(cat)
                .bind(after_id)
                .bind(limit)
                .fetch_all(pool)
                .await?
            } else {
                sqlx::query(
                    r#"
                    SELECT id, room_id, title, url, description, category,
                           curator_mask, created_at, updated_at, is_verified
                    FROM resources
                    WHERE room_id = ?1 
                      AND created_at < (
                          SELECT created_at FROM resources WHERE id = ?2
                      )
                    ORDER BY created_at DESC
                    LIMIT ?3
                    "#,
                )
                .bind(room_id)
                .bind(after_id)
                .bind(limit)
                .fetch_all(pool)
                .await?
            }
        } else {
            if let Some(cat) = category {
                sqlx::query(
                    r#"
                    SELECT id, room_id, title, url, description, category,
                           curator_mask, created_at, updated_at, is_verified
                    FROM resources
                    WHERE room_id = ?1 
                      AND category = ?2
                    ORDER BY created_at DESC
                    LIMIT ?3
                    "#,
                )
                .bind(room_id)
                .bind(cat)
                .bind(limit)
                .fetch_all(pool)
                .await?
            } else {
                sqlx::query(
                    r#"
                    SELECT id, room_id, title, url, description, category,
                           curator_mask, created_at, updated_at, is_verified
                    FROM resources
                    WHERE room_id = ?1
                    ORDER BY created_at DESC
                    LIMIT ?2
                    "#,
                )
                .bind(room_id)
                .bind(limit)
                .fetch_all(pool)
                .await?
            }
        };
        
        let mut resources = Vec::new();
        for row in rows {
            let created_at_str: String = row.get("created_at");
            let created_at = match chrono::DateTime::parse_from_rfc3339(&created_at_str) {
                Ok(dt) => dt.with_timezone(&chrono::Utc),
                Err(e) => {
                    tracing::error!("Failed to parse created_at '{}' for resource {}: {}", created_at_str, row.get::<String, _>("id"), e);
                    // Use current time as fallback
                    Utc::now()
                }
            };
            
            let updated_at_str: String = row.get("updated_at");
            let updated_at = match chrono::DateTime::parse_from_rfc3339(&updated_at_str) {
                Ok(dt) => dt.with_timezone(&chrono::Utc),
                Err(e) => {
                    tracing::error!("Failed to parse updated_at '{}' for resource {}: {}", updated_at_str, row.get::<String, _>("id"), e);
                    // Use current time as fallback
                    Utc::now()
                }
            };
            
            resources.push(Resource {
                id: row.get("id"),
                room_id: row.get("room_id"),
                title: row.get("title"),
                url: row.get("url"),
                description: row.get("description"),
                category: row.get("category"),
                curator_mask: row.get("curator_mask"),
                created_at,
                updated_at,
                is_verified: row.get::<i64, _>("is_verified") != 0,
            });
        }
        
        Ok(resources)
    }

    pub async fn get_resource_by_id(
        pool: &SqlitePool,
        resource_id: &str,
    ) -> Result<Option<Resource>, anyhow::Error> {
        let row = sqlx::query(
            r#"
            SELECT id, room_id, title, url, description, category,
                   curator_mask, created_at, updated_at, is_verified
            FROM resources
            WHERE id = ?1
            "#,
        )
        .bind(resource_id)
        .fetch_optional(pool)
        .await?;
        
        if let Some(row) = row {
            let created_at_str: String = row.get("created_at");
            let created_at = match chrono::DateTime::parse_from_rfc3339(&created_at_str) {
                Ok(dt) => dt.with_timezone(&chrono::Utc),
                Err(e) => {
                    let resource_id: String = row.get("id");
                    tracing::error!("Failed to parse created_at '{}' for resource {}: {}", created_at_str, resource_id, e);
                    // Use current time as fallback
                    chrono::Utc::now()
                }
            };
            
            let updated_at_str: String = row.get("updated_at");
            let updated_at = match chrono::DateTime::parse_from_rfc3339(&updated_at_str) {
                Ok(dt) => dt.with_timezone(&chrono::Utc),
                Err(e) => {
                    let resource_id: String = row.get("id");
                    tracing::error!("Failed to parse updated_at '{}' for resource {}: {}", updated_at_str, resource_id, e);
                    // Use current time as fallback
                    chrono::Utc::now()
                }
            };
            
            Ok(Some(Resource {
                id: row.get("id"),
                room_id: row.get("room_id"),
                title: row.get("title"),
                url: row.get("url"),
                description: row.get("description"),
                category: row.get("category"),
                curator_mask: row.get("curator_mask"),
                created_at,
                updated_at,
                is_verified: row.get::<i64, _>("is_verified") != 0,
            }))
        } else {
            Ok(None)
        }
    }

    pub async fn update_resource(
        pool: &SqlitePool,
        resource: &Resource,
    ) -> Result<Resource, anyhow::Error> {
        sqlx::query(
            r#"
            UPDATE resources
            SET title = ?1, url = ?2, description = ?3, category = ?4, updated_at = ?5
            WHERE id = ?6
            "#,
        )
        .bind(&resource.title)
        .bind(&resource.url)
        .bind(&resource.description)
        .bind(&resource.category)
        .bind(resource.updated_at.to_rfc3339())
        .bind(&resource.id)
        .execute(pool)
        .await?;
        
        Ok(resource.clone())
    }

    pub async fn delete_resource(
        pool: &SqlitePool,
        resource_id: &str,
    ) -> Result<bool, anyhow::Error> {
        let result = sqlx::query("DELETE FROM resources WHERE id = ?1")
            .bind(resource_id)
            .execute(pool)
            .await?;
        
        Ok(result.rows_affected() > 0)
    }

    pub async fn get_resources_by_category(
        pool: &SqlitePool,
        room_id: &str,
        category: &str,
    ) -> Result<Vec<Resource>, anyhow::Error> {
        let rows = sqlx::query(
            r#"
            SELECT id, room_id, title, url, description, category,
                   curator_mask, created_at, updated_at, is_verified
            FROM resources
            WHERE room_id = ?1 AND category = ?2
            ORDER BY created_at DESC
            "#,
        )
        .bind(room_id)
        .bind(category)
        .fetch_all(pool)
        .await?;
        
        let mut resources = Vec::new();
        for row in rows {
            let created_at_str: String = row.get("created_at");
            let created_at = match chrono::DateTime::parse_from_rfc3339(&created_at_str) {
                Ok(dt) => dt.with_timezone(&chrono::Utc),
                Err(e) => {
                    tracing::error!("Failed to parse created_at '{}' for resource {}: {}", created_at_str, row.get::<String, _>("id"), e);
                    // Use current time as fallback
                    Utc::now()
                }
            };
            
            let updated_at_str: String = row.get("updated_at");
            let updated_at = match chrono::DateTime::parse_from_rfc3339(&updated_at_str) {
                Ok(dt) => dt.with_timezone(&chrono::Utc),
                Err(e) => {
                    tracing::error!("Failed to parse updated_at '{}' for resource {}: {}", updated_at_str, row.get::<String, _>("id"), e);
                    // Use current time as fallback
                    Utc::now()
                }
            };
            
            resources.push(Resource {
                id: row.get("id"),
                room_id: row.get("room_id"),
                title: row.get("title"),
                url: row.get("url"),
                description: row.get("description"),
                category: row.get("category"),
                curator_mask: row.get("curator_mask"),
                created_at,
                updated_at,
                is_verified: row.get::<i64, _>("is_verified") != 0,
            });
        }
        
        Ok(resources)
    }
}

