use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use serde::Serialize;
use sqlx::{SqlitePool, Row};
use std::sync::Arc;

#[derive(Serialize)]
pub struct MemberResponse {
    pub mask: String,
}

pub async fn get_active_members(
    State(pool): State<Arc<SqlitePool>>,
    Path(room_id): Path<String>,
) -> impl IntoResponse {
    tracing::debug!("Getting active members for room: {}", room_id);
    
    if room_id.trim().is_empty() {
        tracing::warn!("Empty room_id provided to get_active_members");
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Room ID is required"
            })),
        ).into_response();
    }

    // Use RFC3339 format for consistent date comparison
    let now = chrono::Utc::now().to_rfc3339();
    tracing::debug!("Querying active sessions with expiry > {}", now);

    // Get all active sessions for this room
    let sessions = sqlx::query(
        r#"
        SELECT DISTINCT session_mask
        FROM sessions
        WHERE room_id = ?1
          AND expires_at > ?2
        ORDER BY session_mask
        "#,
    )
    .bind(&room_id)
    .bind(&now)
    .fetch_all(&*pool)
    .await;

    match sessions {
        Ok(rows) => {
            let members: Vec<MemberResponse> = rows
                .into_iter()
                .map(|row| MemberResponse {
                    mask: row.get("session_mask"),
                })
                .collect();

            tracing::info!("Found {} active members for room {}", members.len(), room_id);
            
            if members.is_empty() {
                tracing::debug!("No active sessions found for room {}", room_id);
            }

            (
                StatusCode::OK,
                Json(serde_json::json!({
                    "items": members
                })),
            ).into_response()
        }
        Err(e) => {
            tracing::error!("Failed to get active members for room {}: {}", room_id, e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": format!("Failed to fetch active members: {}", e)
                })),
            ).into_response()
        }
    }
}

