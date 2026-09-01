use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use std::sync::Arc;

use storage::{WhisperRepository, SessionRepository};
use core::{WhisperSession, WhisperState};
use bus::EventBus;

#[derive(Deserialize)]
pub struct CreateWhisperRequest {
    pub sender_mask: String,
    pub recipient_mask: String,
    pub room_id: String,
}

#[derive(Serialize)]
pub struct WhisperResponse {
    pub id: String,
    pub sender_mask: String,
    pub recipient_mask: String,
    pub room_id: String,
    pub state: String,
    pub created_at: String,
    pub expires_at: String,
    pub last_activity_at: String,
}

#[derive(Deserialize)]
pub struct GetWhispersQuery {
    pub mask: String,
    pub room_id: Option<String>,
}

#[derive(Deserialize)]
pub struct ExtendWhisperRequest {
    pub hours: Option<i64>,
}

pub async fn create_whisper(
    State(pool): State<Arc<SqlitePool>>,
    State(event_bus): State<Arc<EventBus>>,
    Json(req): Json<CreateWhisperRequest>,
) -> impl IntoResponse {
    // Validate input
    if req.sender_mask.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Sender mask cannot be empty"
            })),
        ).into_response();
    }

    if req.recipient_mask.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Recipient mask cannot be empty"
            })),
        ).into_response();
    }

    if req.sender_mask == req.recipient_mask {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Cannot whisper to yourself"
            })),
        ).into_response();
    }

    if req.room_id.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Room ID cannot be empty"
            })),
        ).into_response();
    }

    // Validate sender has active session (required)
    let sender_session = SessionRepository::get_session_by_mask(&pool, &req.room_id, &req.sender_mask).await;
    
    match sender_session {
        Ok(Some(_)) => {
            // Sender has active session, continue
        }
        Ok(None) => {
            return (
                StatusCode::BAD_REQUEST,
                Json(serde_json::json!({
                    "code": "VALIDATION_ERROR",
                    "message": "You must have an active session to send whispers"
                })),
            ).into_response();
        }
        Err(e) => {
            tracing::error!("Failed to validate sender session: {}", e);
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to validate sender session"
                })),
            ).into_response();
        }
    }
    
    // Check if recipient has sent messages in this room (more lenient - allows whispers to past participants)
    // This is optional - if they have a session, great, but we'll also allow if they've sent messages
    let recipient_has_messages = {
        use storage::MessageRepository;
        // Check if recipient has sent any messages in this room
        let messages = MessageRepository::get_messages(&pool, &req.room_id, None, Some(100)).await.unwrap_or_default();
        messages.iter().any(|msg| msg.sender_mask == req.recipient_mask && msg.message_type != core::MessageType::Whisper)
    };
    
    if !recipient_has_messages {
        // Also check if they have an active session as fallback
        let recipient_session = SessionRepository::get_session_by_mask(&pool, &req.room_id, &req.recipient_mask).await;
        match recipient_session {
            Ok(None) => {
                return (
                    StatusCode::BAD_REQUEST,
                    Json(serde_json::json!({
                        "code": "VALIDATION_ERROR",
                        "message": "Recipient not found in room"
                    })),
                ).into_response();
            }
            Err(e) => {
                tracing::warn!("Failed to check recipient session (allowing anyway): {}", e);
                // Continue - we'll allow it if they have messages
            }
            Ok(Some(_)) => {
                // Recipient has active session, all good
            }
        }
    }

    // Check if active whisper already exists
    match WhisperRepository::get_active_whisper(&pool, &req.sender_mask, &req.recipient_mask, &req.room_id).await {
        Ok(Some(_)) => {
            return (
                StatusCode::CONFLICT,
                Json(serde_json::json!({
                    "code": "ALREADY_ACTIVE",
                    "message": "An active whisper already exists between these users"
                })),
            ).into_response();
        }
        Ok(None) => {
            // No active whisper, continue
        }
        Err(e) => {
            tracing::error!("Failed to check for active whisper: {}", e);
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to check for existing whisper"
                })),
            ).into_response();
        }
    }

    // Create whisper session
    match WhisperSession::new(req.sender_mask, req.recipient_mask, req.room_id.clone()) {
        Ok(whisper) => {
            match WhisperRepository::create_whisper(&pool, whisper.clone()).await {
                Ok(_) => {
                    // Publish event
                    event_bus.publish(bus::Event {
                        event_type: "whisper.created".to_string(),
                        room_id: Some(whisper.room_id.clone()),
                        whisper_id: Some(whisper.id.clone()),
                        payload: serde_json::to_value(&whisper).unwrap_or_default(),
                    });
                    
                    (
                        StatusCode::CREATED,
                        Json(serde_json::json!({
                            "id": whisper.id,
                            "state": serde_json::to_string(&whisper.state).unwrap_or_else(|_| "pending".to_string()).trim_matches('"'),
                            "expires_at": whisper.expires_at.to_rfc3339()
                        })),
                    ).into_response()
                }
                Err(e) => {
                    tracing::error!("Failed to create whisper: {}", e);
                    (
                        StatusCode::INTERNAL_SERVER_ERROR,
                        Json(serde_json::json!({
                            "code": "INTERNAL_ERROR",
                            "message": "Failed to create whisper"
                        })),
                    ).into_response()
                }
            }
        }
        Err(e) => {
            tracing::warn!("Validation error: {:?}", e);
            (
                StatusCode::BAD_REQUEST,
                Json(serde_json::json!({
                    "code": "VALIDATION_ERROR",
                    "message": e.to_string()
                })),
            ).into_response()
        }
    }
}

pub async fn accept_whisper(
    State(pool): State<Arc<SqlitePool>>,
    State(event_bus): State<Arc<EventBus>>,
    Path(whisper_id): Path<String>,
) -> impl IntoResponse {
    // Get whisper
    let _whisper_room_id = match WhisperRepository::get_whisper(&pool, &whisper_id).await {
        Ok(Some(w)) => {
            // Check if expired
            if w.is_expired() {
                return (
                    StatusCode::GONE,
                    Json(serde_json::json!({
                        "code": "EXPIRED",
                        "message": "Whisper has expired"
                    })),
                ).into_response();
            }

            // Check if state is Pending
            if w.state != WhisperState::Pending {
                return (
                    StatusCode::BAD_REQUEST,
                    Json(serde_json::json!({
                        "code": "INVALID_STATE",
                        "message": format!("Cannot accept whisper in {:?} state", w.state)
                    })),
                ).into_response();
            }
            
            Some(w.room_id)
        },
        Ok(None) => {
            return (
                StatusCode::NOT_FOUND,
                Json(serde_json::json!({
                    "code": "NOT_FOUND",
                    "message": "Whisper not found"
                })),
            ).into_response();
        }
        Err(e) => {
            tracing::error!("Failed to get whisper: {}", e);
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch whisper"
                })),
            ).into_response();
        }
    };

    // Accept whisper (whisper_room_id was used for validation, now we get room_id from updated whisper)
    match WhisperRepository::accept_whisper(&pool, &whisper_id).await {
        Ok(updated) => {
            // Publish event
            event_bus.publish(bus::Event {
                event_type: "whisper.accepted".to_string(),
                room_id: Some(updated.room_id.clone()),
                whisper_id: Some(updated.id.clone()),
                payload: serde_json::to_value(&updated).unwrap_or_default(),
            });
            
            // Return full whisper object for frontend
            let response = WhisperResponse {
                id: updated.id,
                sender_mask: updated.sender_mask,
                recipient_mask: updated.recipient_mask,
                room_id: updated.room_id,
                state: serde_json::to_string(&updated.state).unwrap_or_else(|_| "active".to_string()).trim_matches('"').to_string(),
                created_at: updated.created_at.to_rfc3339(),
                expires_at: updated.expires_at.to_rfc3339(),
                last_activity_at: updated.last_activity_at.to_rfc3339(),
            };
            (
                StatusCode::OK,
                Json(response),
            ).into_response()
        }
        Err(e) => {
            tracing::error!("Failed to accept whisper: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to accept whisper"
                })),
            ).into_response()
        }
    }
}

pub async fn decline_whisper(
    State(pool): State<Arc<SqlitePool>>,
    State(event_bus): State<Arc<EventBus>>,
    Path(whisper_id): Path<String>,
) -> impl IntoResponse {
    // Get whisper to get room_id
    let whisper_room_id = match WhisperRepository::get_whisper(&pool, &whisper_id).await {
        Ok(Some(w)) => Some(w.room_id),
        Ok(None) => {
            return (
                StatusCode::NOT_FOUND,
                Json(serde_json::json!({
                    "code": "NOT_FOUND",
                    "message": "Whisper not found"
                })),
            ).into_response();
        }
        Err(e) => {
            tracing::error!("Failed to get whisper: {}", e);
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch whisper"
                })),
            ).into_response();
        }
    };

    // Decline whisper
    match WhisperRepository::decline_whisper(&pool, &whisper_id).await {
        Ok(updated) => {
            // Publish event
            if let Some(room_id) = whisper_room_id {
                event_bus.publish(bus::Event {
                    event_type: "whisper.declined".to_string(),
                    room_id: Some(room_id),
                    whisper_id: Some(whisper_id.clone()),
                    payload: serde_json::json!({
                        "id": whisper_id,
                    }),
                });
            }
            
            (
                StatusCode::OK,
                Json(serde_json::json!({
                    "id": updated.id,
                    "state": serde_json::to_string(&updated.state).unwrap_or_else(|_| "declined".to_string()).trim_matches('"')
                })),
            ).into_response()
        }
        Err(e) => {
            tracing::error!("Failed to decline whisper: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to decline whisper"
                })),
            ).into_response()
        }
    }
}

pub async fn list_whispers(
    State(pool): State<Arc<SqlitePool>>,
    Query(params): Query<GetWhispersQuery>,
) -> impl IntoResponse {
    if params.mask.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Mask parameter is required"
            })),
        ).into_response();
    }

    tracing::debug!("Listing whispers for mask: {}, room_id: {:?}", params.mask, params.room_id);
    
    match WhisperRepository::get_whispers_for_mask(&pool, &params.mask, params.room_id.as_deref()).await {
        Ok(whispers) => {
            tracing::debug!("Found {} whispers for mask {}", whispers.len(), params.mask);
            let whisper_responses: Vec<WhisperResponse> = whispers
                .into_iter()
                .map(|w| WhisperResponse {
                    id: w.id,
                    sender_mask: w.sender_mask,
                    recipient_mask: w.recipient_mask,
                    room_id: w.room_id,
                    state: match w.state {
                        core::WhisperState::Pending => "pending".to_string(),
                        core::WhisperState::Active => "active".to_string(),
                        core::WhisperState::Declined => "declined".to_string(),
                        core::WhisperState::Ended => "ended".to_string(),
                    },
                    created_at: w.created_at.to_rfc3339(),
                    expires_at: w.expires_at.to_rfc3339(),
                    last_activity_at: w.last_activity_at.to_rfc3339(),
                })
                .collect();

            (
                StatusCode::OK,
                Json(serde_json::json!({
                    "items": whisper_responses
                })),
            ).into_response()
        }
        Err(e) => {
            tracing::error!("Failed to list whispers: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch whispers"
                })),
            ).into_response()
        }
    }
}

pub async fn end_whisper(
    State(pool): State<Arc<SqlitePool>>,
    State(event_bus): State<Arc<EventBus>>,
    Path(whisper_id): Path<String>,
) -> impl IntoResponse {
    // Check if whisper exists and get it for room_id
    let whisper_room_id = match WhisperRepository::get_whisper(&pool, &whisper_id).await {
        Ok(Some(whisper)) => {
            Some(whisper.room_id)
        }
        Ok(None) => {
            return (
                StatusCode::NOT_FOUND,
                Json(serde_json::json!({
                    "code": "NOT_FOUND",
                    "message": "Whisper not found"
                })),
            ).into_response();
        }
        Err(e) => {
            tracing::error!("Failed to get whisper: {}", e);
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch whisper"
                })),
            ).into_response();
        }
    };

    match WhisperRepository::end_whisper(&pool, &whisper_id).await {
        Ok(_) => {
            // Publish event
            if let Some(room_id) = whisper_room_id {
                event_bus.publish(bus::Event {
                    event_type: "whisper.ended".to_string(),
                    room_id: Some(room_id),
                    whisper_id: Some(whisper_id.clone()),
                    payload: serde_json::json!({
                        "id": whisper_id,
                    }),
                });
            }
            
            StatusCode::NO_CONTENT.into_response()
        }
        Err(e) => {
            tracing::error!("Failed to end whisper: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to end whisper"
                })),
            ).into_response()
        }
    }
}

pub async fn extend_whisper(
    State(pool): State<Arc<SqlitePool>>,
    Path(whisper_id): Path<String>,
    Json(req): Json<ExtendWhisperRequest>,
) -> impl IntoResponse {
    let hours = req.hours.unwrap_or(24);
    
    if hours <= 0 {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Hours must be positive"
            })),
        ).into_response();
    }

    // Get whisper to check state
    match WhisperRepository::get_whisper(&pool, &whisper_id).await {
        Ok(Some(whisper)) => {
            // Check if state allows extension
            if whisper.state != WhisperState::Active && whisper.state != WhisperState::Pending {
                return (
                    StatusCode::BAD_REQUEST,
                    Json(serde_json::json!({
                        "code": "INVALID_STATE",
                        "message": format!("Cannot extend whisper in {:?} state", whisper.state)
                    })),
                ).into_response();
            }
        }
        Ok(None) => {
            return (
                StatusCode::NOT_FOUND,
                Json(serde_json::json!({
                    "code": "NOT_FOUND",
                    "message": "Whisper not found"
                })),
            ).into_response();
        }
        Err(e) => {
            tracing::error!("Failed to get whisper: {}", e);
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch whisper"
                })),
            ).into_response();
        }
    }

    match WhisperRepository::extend_whisper(&pool, &whisper_id, hours).await {
        Ok(updated) => {
            (
                StatusCode::OK,
                Json(serde_json::json!({
                    "id": updated.id,
                    "expires_at": updated.expires_at.to_rfc3339()
                })),
            ).into_response()
        }
        Err(e) => {
            tracing::error!("Failed to extend whisper: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to extend whisper"
                })),
            ).into_response()
        }
    }
}

