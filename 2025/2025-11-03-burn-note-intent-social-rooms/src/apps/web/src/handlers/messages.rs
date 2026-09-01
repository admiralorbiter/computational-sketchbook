use axum::{
    extract::{Query, State},
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use std::sync::Arc;

use storage::{MessageRepository, RateLimitRepository, WhisperRepository};
use core::{Message, MessageType};
use bus::EventBus;

#[derive(Deserialize)]
pub struct GetMessagesQuery {
    pub room_id: String,
    pub after: Option<String>,
    pub limit: Option<u32>,
}

#[derive(Serialize)]
pub struct MessageResponse {
    pub id: String,
    pub room_id: String,
    pub sender_mask: String,
    #[serde(rename = "type")]
    pub message_type: String,
    pub body: String,
    pub created_at: String,
    pub tombstoned: bool,
    pub whisper_id: Option<String>,
}

#[derive(Deserialize)]
pub struct CreateMessageRequest {
    pub room_id: String,
    pub sender_mask: String,
    #[serde(rename = "type")]
    pub message_type: String,
    pub body: String,
    pub whisper_id: Option<String>,
}

#[derive(Serialize)]
pub struct CreateMessageResponse {
    pub id: String,
    pub created_at: String,
}

pub async fn get_messages(
    State(pool): State<Arc<SqlitePool>>,
    Query(params): Query<GetMessagesQuery>,
) -> impl IntoResponse {
    // Validate input
    if params.room_id.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Room ID is required"
            })),
        ).into_response();
    }

    // Validate limit if provided
    if let Some(limit) = params.limit {
        if limit > 100 {
            return (
                StatusCode::BAD_REQUEST,
                Json(serde_json::json!({
                    "code": "VALIDATION_ERROR",
                    "message": "Limit cannot exceed 100"
                })),
            ).into_response();
        }
    }

    match MessageRepository::get_messages(
        &pool,
        &params.room_id,
        params.after.as_deref(),
        params.limit,
    )
    .await
    {
        Ok(messages) => {
            let message_responses: Vec<MessageResponse> = messages
                .into_iter()
                .map(|msg| MessageResponse {
                    id: msg.id,
                    room_id: msg.room_id,
                    sender_mask: msg.sender_mask,
                    message_type: serde_json::to_string(&msg.message_type)
                        .unwrap_or_else(|_| "text".to_string())
                        .trim_matches('"')
                        .to_string(),
                    body: msg.body,
                    created_at: msg.created_at.to_rfc3339(),
                    tombstoned: msg.tombstoned,
                    whisper_id: msg.whisper_id,
                })
                .collect();

            (StatusCode::OK, Json(serde_json::json!({
                "items": message_responses
            }))).into_response()
        }
        Err(e) => {
            tracing::error!("Failed to get messages: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch messages. Please try again."
                })),
            ).into_response()
        }
    }
}

pub async fn create_message(
    State(pool): State<Arc<SqlitePool>>,
    State(event_bus): State<Arc<EventBus>>,
    Json(req): Json<CreateMessageRequest>,
) -> impl IntoResponse {
    // Validate input
    if req.room_id.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Room ID cannot be empty"
            })),
        ).into_response();
    }

    if req.sender_mask.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Sender mask cannot be empty"
            })),
        ).into_response();
    }

    if req.body.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Message body cannot be empty"
            })),
        ).into_response();
    }

    if req.body.len() > 4096 {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Message body too large (maximum 4096 characters)"
            })),
        ).into_response();
    }

    // Parse message type
    let message_type = match req.message_type.as_str() {
        "text" => MessageType::Text,
        "media" => MessageType::Media,
        "whisper" => MessageType::Whisper,
        _ => {
            return (
                StatusCode::BAD_REQUEST,
                Json(serde_json::json!({
                    "code": "INVALID_MESSAGE_TYPE",
                    "message": "Invalid message type. Must be 'text', 'media', or 'whisper'"
                })),
            ).into_response();
        }
    };

    // Validate whisper if type is whisper
    if message_type == MessageType::Whisper {
        if let Some(ref whisper_id) = req.whisper_id {
            // Validate whisper exists and is Active
            match WhisperRepository::get_whisper(&pool, whisper_id).await {
                Ok(Some(whisper)) => {
                    // Check if whisper is expired
                    if whisper.is_expired() {
                        return (
                            StatusCode::GONE,
                            Json(serde_json::json!({
                                "code": "EXPIRED",
                                "message": "Whisper has expired"
                            })),
                        ).into_response();
                    }
                    
                    // Check if whisper is in Active state
                    if whisper.state != core::WhisperState::Active {
                        return (
                            StatusCode::BAD_REQUEST,
                            Json(serde_json::json!({
                                "code": "INVALID_STATE",
                                "message": format!("Cannot send message to whisper in {:?} state", whisper.state)
                            })),
                        ).into_response();
                    }
                    
                    // Update last activity
                    if let Err(e) = WhisperRepository::update_activity(&pool, whisper_id).await {
                        tracing::warn!("Failed to update whisper activity: {}", e);
                        // Continue anyway - not critical
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
                    tracing::error!("Failed to validate whisper: {}", e);
                    return (
                        StatusCode::INTERNAL_SERVER_ERROR,
                        Json(serde_json::json!({
                            "code": "INTERNAL_ERROR",
                            "message": "Failed to validate whisper"
                        })),
                    ).into_response();
                }
            }
        } else {
            return (
                StatusCode::BAD_REQUEST,
                Json(serde_json::json!({
                    "code": "VALIDATION_ERROR",
                    "message": "whisper_id is required for whisper messages"
                })),
            ).into_response();
        }
    }

    // Check rate limit
    let rate_limit_key = if message_type == MessageType::Whisper {
        // For whispers, use whisper-specific rate limiting
        if let Some(ref whisper_id) = req.whisper_id {
            format!("whisper:{}:{}", whisper_id, req.sender_mask)
        } else {
            format!("post:{}:{}", req.room_id, req.sender_mask)
        }
    } else {
        // MVP approach: Use sender_mask+room_id as identifier
        // Future: Require X-Session-Id header and use session middleware
        format!("post:{}:{}", req.room_id, req.sender_mask)
    };
    
    let (window_seconds, max_actions) = if message_type == MessageType::Whisper {
        (60, 10) // 10 messages per 60 seconds per whisper
    } else {
        (60, 10) // 10 messages per 60 seconds per room
    };
    
    match RateLimitRepository::check_rate_limit(&pool, &rate_limit_key, "post", window_seconds, max_actions).await {
        Ok(true) => {
            // Rate limit check passed
        }
        Ok(false) => {
            return (
                StatusCode::TOO_MANY_REQUESTS,
                Json(serde_json::json!({
                    "code": "RATE_LIMITED",
                    "message": "Too many messages. Please wait before sending another message."
                })),
            ).into_response();
        }
        Err(e) => {
            tracing::error!("Rate limit check failed: {}", e);
            // Continue on rate limit check error (fail open for MVP)
        }
    }

    // Record the post action for rate limiting
    if let Err(e) = RateLimitRepository::record_action(&pool, &rate_limit_key, "post", &format!("room:{}", req.room_id)).await {
        tracing::warn!("Failed to record post action for rate limiting: {}", e);
    }

    // Create message
    match Message::new(
        req.room_id.clone(),
        req.sender_mask,
        message_type,
        req.body,
        req.whisper_id.clone(),
        None, // parent_post_id - only used for posts
    ) {
        Ok(message) => {
            match MessageRepository::create_message(&pool, message.clone()).await {
                Ok(_) => {
                    // Publish event
                    event_bus.publish(bus::Event {
                        event_type: "message.created".to_string(),
                        room_id: Some(message.room_id.clone()),
                        whisper_id: message.whisper_id.clone(),
                        payload: serde_json::to_value(&message).unwrap_or_default(),
                    });
                    
                    (
                        StatusCode::CREATED,
                        Json(CreateMessageResponse {
                            id: message.id,
                            created_at: message.created_at.to_rfc3339(),
                        }),
                    ).into_response()
                }
                Err(e) => {
                    tracing::error!("Failed to create message: {}", e);
                    (
                        StatusCode::INTERNAL_SERVER_ERROR,
                        Json(serde_json::json!({
                            "code": "INTERNAL_ERROR",
                            "message": "Failed to create message. Please try again."
                        })),
                    ).into_response()
                }
            }
        }
        Err(e) => {
            tracing::warn!("Validation error: {:?}", e);
            // Use the error's Display implementation for user-friendly message
            let error_message = e.to_string();
            (
                StatusCode::BAD_REQUEST,
                Json(serde_json::json!({
                    "code": "VALIDATION_ERROR",
                    "message": error_message
                })),
            ).into_response()
        }
    }
}
