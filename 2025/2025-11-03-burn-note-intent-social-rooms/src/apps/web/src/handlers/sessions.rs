use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use sqlx::SqlitePool;
use std::sync::Arc;

use storage::SessionRepository;
use crate::middleware::session::SessionExt;
use bus::EventBus;

pub async fn burn_session(
    State(pool): State<Arc<SqlitePool>>,
    State(event_bus): State<Arc<EventBus>>,
    Path(session_id): Path<String>,
    axum::extract::Extension(SessionExt(session)): axum::extract::Extension<SessionExt>,
) -> impl IntoResponse {
    // Validate that the session ID in the path matches the authenticated session
    if session.id != session_id {
        return (
            StatusCode::FORBIDDEN,
            Json(serde_json::json!({
                "code": "FORBIDDEN",
                "message": "Cannot delete another user's session"
            })),
        ).into_response();
    }

    // Store room_id and session_mask before deleting
    let room_id = session.room_id.clone();
    let session_mask = session.session_mask.clone();

    // Delete the session
    match SessionRepository::delete_session(&pool, &session_id).await {
        Ok(_) => {
            // Publish member.left event
            event_bus.publish(bus::Event {
                event_type: "member.left".to_string(),
                room_id: Some(room_id),
                whisper_id: None,
                payload: serde_json::json!({
                    "mask": session_mask,
                }),
            });
            
            (StatusCode::NO_CONTENT, ()).into_response()
        }
        Err(e) => {
            tracing::error!("Failed to delete session: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to delete session"
                })),
            ).into_response()
        }
    }
}
