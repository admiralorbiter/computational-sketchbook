use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::{IntoResponse, Json},
};
use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use std::sync::Arc;

use storage::{RoomRepository, SessionRepository, RateLimitRepository};
use core::UserSession;
use bus::EventBus;

#[derive(Serialize)]
pub struct RoomResponse {
    pub id: String,
    pub title: String,
    pub language: String,
    pub policy_flags: PolicyFlagsResponse,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Serialize)]
pub struct PolicyFlagsResponse {
    pub sensitive: bool,
    pub curated: bool,
    pub slow_mode: bool,
}

#[derive(Serialize)]
pub struct JoinRoomResponse {
    pub session_mask: String,
    pub session_id: String,
}

#[derive(Deserialize)]
pub struct JoinRoomRequest {
    pub ttl_hours: Option<i64>,
}

pub async fn list_rooms(State(pool): State<Arc<SqlitePool>>) -> impl IntoResponse {
    match RoomRepository::list_rooms(&pool).await {
        Ok(rooms) => {
            let room_responses: Vec<RoomResponse> = rooms
                .into_iter()
                .map(|room| RoomResponse {
                    id: room.id,
                    title: room.title,
                    language: room.language,
                    policy_flags: PolicyFlagsResponse {
                        sensitive: room.policy_flags.sensitive,
                        curated: room.policy_flags.curated,
                        slow_mode: room.policy_flags.slow_mode,
                    },
                    created_at: room.created_at.to_rfc3339(),
                    updated_at: room.updated_at.to_rfc3339(),
                })
                .collect();
            
            (StatusCode::OK, Json(serde_json::json!({
                "items": room_responses
            }))).into_response()
        }
        Err(e) => {
            tracing::error!("Failed to list rooms: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch rooms. Please try again."
                })),
            ).into_response()
        }
    }
}

pub async fn join_room(
    State(pool): State<Arc<SqlitePool>>,
    State(event_bus): State<Arc<EventBus>>,
    Path(room_id): Path<String>,
    Json(req): Json<JoinRoomRequest>,
) -> impl IntoResponse {
    // Validate room_id
    if room_id.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Room ID cannot be empty"
            })),
        ).into_response();
    }

    // Validate TTL if provided
    if let Some(ttl) = req.ttl_hours {
        if ttl <= 0 || ttl > 168 { // Max 1 week
            return (
                StatusCode::BAD_REQUEST,
                Json(serde_json::json!({
                    "code": "VALIDATION_ERROR",
                    "message": "TTL must be between 1 and 168 hours (1 week)"
                })),
            ).into_response();
        }
    }

    // Check if room exists first
    match RoomRepository::get_room(&pool, &room_id).await {
        Ok(Some(_)) => {
            // Room exists, continue with join process
        }
        Ok(None) => {
            return (
                StatusCode::NOT_FOUND,
                Json(serde_json::json!({
                    "code": "ROOM_NOT_FOUND",
                    "message": "Room not found"
                })),
            ).into_response();
        }
        Err(e) => {
            tracing::error!("Failed to get room: {}", e);
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch room. Please try again."
                })),
            ).into_response();
        }
    }

    // Check rate limit for join action
    // For join, we use room_id as a simple identifier (MVP approach)
    // Future: Use IP hash or temporary session identifier
    // Increased limit: 3 joins per 60 seconds (more lenient for re-joining)
    let rate_limit_key = format!("join:{}", room_id);
    match RateLimitRepository::check_rate_limit(&pool, &rate_limit_key, "join", 60, 3).await {
        Ok(true) => {
            // Rate limit check passed
        }
        Ok(false) => {
            return (
                StatusCode::TOO_MANY_REQUESTS,
                Json(serde_json::json!({
                    "code": "RATE_LIMITED",
                    "message": "Too many join attempts for this room. Please wait a moment before trying again."
                })),
            ).into_response();
        }
        Err(e) => {
            tracing::error!("Rate limit check failed: {}", e);
            // Continue on rate limit check error (fail open for MVP)
        }
    }

    // Record the join action for rate limiting (before creating session)
    if let Err(e) = RateLimitRepository::record_action(&pool, &rate_limit_key, "join", &format!("room:{}", room_id)).await {
        tracing::warn!("Failed to record join action for rate limiting: {}", e);
    }

    // Room exists, create a session
    let ttl_hours = req.ttl_hours.unwrap_or(24);
    let session = UserSession::new(room_id.clone(), ttl_hours);
    
    match SessionRepository::create_session(&pool, session.clone()).await {
        Ok(_) => {
            // Publish member.joined event
            event_bus.publish(bus::Event {
                event_type: "member.joined".to_string(),
                room_id: Some(room_id.clone()),
                whisper_id: None,
                payload: serde_json::json!({
                    "mask": session.session_mask,
                }),
            });
            
            (StatusCode::OK, Json(JoinRoomResponse {
                session_mask: session.session_mask,
                session_id: session.id,
            })).into_response()
        }
        Err(e) => {
            // Check if it's a constraint violation (duplicate session ID - very rare but possible)
            let error_msg = e.to_string();
            let is_constraint_error = error_msg.contains("UNIQUE constraint") || 
                                      error_msg.contains("duplicate") ||
                                      error_msg.contains("constraint");
            
            tracing::error!("Failed to create session: {} (error: {})", error_msg, e);
            
            let user_message = if is_constraint_error {
                "Session creation failed due to conflict. Please try again in a moment.".to_string()
            } else {
                format!("Failed to join room: {}", error_msg)
            };
            
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": user_message
                })),
            ).into_response()
        }
    }
}
