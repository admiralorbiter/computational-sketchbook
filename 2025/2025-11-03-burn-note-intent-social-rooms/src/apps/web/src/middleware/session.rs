use axum::{
    extract::{Request, State},
    http::{HeaderMap, StatusCode},
    middleware::Next,
    response::{IntoResponse, Response},
    Json,
};
use sqlx::SqlitePool;
use std::sync::Arc;

use core::UserSession;
use storage::SessionRepository;

// Extension key for storing session in request
#[derive(Clone)]
pub struct SessionExt(pub UserSession);

pub async fn session_middleware(
    State(pool): State<Arc<SqlitePool>>,
    headers: HeaderMap,
    mut req: Request,
    next: Next,
) -> Response {
    // Extract session ID from X-Session-Id header
    let session_id = match headers.get("X-Session-Id") {
        Some(header_value) => match header_value.to_str() {
            Ok(s) => s,
            Err(_) => {
                return (
                    StatusCode::BAD_REQUEST,
                    Json(serde_json::json!({
                        "code": "INVALID_HEADER",
                        "message": "Invalid X-Session-Id header"
                    })),
                )
                    .into_response();
            }
        },
        None => {
            return (
                StatusCode::UNAUTHORIZED,
                Json(serde_json::json!({
                    "code": "SESSION_REQUIRED",
                    "message": "X-Session-Id header is required"
                })),
            )
                .into_response();
        }
    };

    // Validate session exists and is not expired
    match SessionRepository::get_session(&pool, session_id).await {
        Ok(Some(session)) => {
            // Check if session is expired
            if session.is_expired() {
                return (
                    StatusCode::UNAUTHORIZED,
                    Json(serde_json::json!({
                        "code": "SESSION_EXPIRED",
                        "message": "Session has expired"
                    })),
                )
                    .into_response();
            }

            // Add session to request extensions
            req.extensions_mut().insert(SessionExt(session));
            next.run(req).await
        }
        Ok(None) => {
            (
                StatusCode::UNAUTHORIZED,
                Json(serde_json::json!({
                    "code": "SESSION_NOT_FOUND",
                    "message": "Session not found"
                })),
            )
                .into_response()
        }
        Err(e) => {
            tracing::error!("Failed to validate session: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to validate session"
                })),
            )
                .into_response()
        }
    }
}
