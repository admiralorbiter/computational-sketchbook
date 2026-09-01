use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use serde::{Deserialize, Serialize};
use sqlx::{SqlitePool, Row};
use std::sync::Arc;

use storage::{MessageRepository, RateLimitRepository, HighlightRepository};
use core::{Message, MessageType};
use bus::EventBus;

#[derive(Deserialize)]
pub struct GetPostsQuery {
    pub room_id: String,
    pub after: Option<String>,
    pub limit: Option<u32>,
}

#[derive(Deserialize)]
pub struct GetRepliesQuery {
    pub after: Option<String>,
    pub limit: Option<u32>,
}

#[derive(Serialize)]
pub struct PostResponse {
    pub id: String,
    pub room_id: String,
    pub sender_mask: String,
    pub body: String,
    pub created_at: String,
    pub reply_count: i64,
}

#[derive(Deserialize)]
pub struct CreatePostRequest {
    pub room_id: String,
    pub sender_mask: String,
    pub body: String,
    pub parent_post_id: Option<String>,
}

#[derive(Serialize)]
pub struct CreatePostResponse {
    pub id: String,
    pub created_at: String,
}

pub async fn get_posts(
    State(pool): State<Arc<SqlitePool>>,
    Query(params): Query<GetPostsQuery>,
) -> impl IntoResponse {
    // Validate input
    if params.room_id.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Room ID is required"
            })),
        )
            .into_response();
    }

    // Validate limit if provided
    if let Some(limit) = params.limit {
        if limit > 50 {
            return (
                StatusCode::BAD_REQUEST,
                Json(serde_json::json!({
                    "code": "VALIDATION_ERROR",
                    "message": "Limit cannot exceed 50"
                })),
            )
                .into_response();
        }
    }

    match MessageRepository::get_posts(
        &pool,
        &params.room_id,
        params.after.as_deref(),
        params.limit,
    )
    .await
    {
        Ok(posts) => {
            // Get reply counts for each post
            let mut post_responses = Vec::new();
            for post in posts {
                let reply_count = MessageRepository::get_reply_count(&pool, &post.id)
                    .await
                    .unwrap_or(0);

                post_responses.push(PostResponse {
                    id: post.id,
                    room_id: post.room_id,
                    sender_mask: post.sender_mask,
                    body: post.body,
                    created_at: post.created_at.to_rfc3339(),
                    reply_count,
                });
            }

            // Determine if there are more posts
            let next = if post_responses.len() == params.limit.unwrap_or(50) as usize {
                post_responses.last().map(|p| p.id.clone())
            } else {
                None
            };

            let mut response = serde_json::json!({
                "items": post_responses
            });
            
            if let Some(next_cursor) = next {
                response["next"] = serde_json::json!(next_cursor);
            }

            (StatusCode::OK, Json(response)).into_response()
        }
        Err(e) => {
            tracing::error!("Failed to get posts: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch posts. Please try again."
                })),
            )
                .into_response()
        }
    }
}

pub async fn get_post_replies(
    State(pool): State<Arc<SqlitePool>>,
    Path(post_id): Path<String>,
    Query(params): Query<GetRepliesQuery>,
) -> impl IntoResponse {
    // Validate limit if provided
    if let Some(limit) = params.limit {
        if limit > 50 {
            return (
                StatusCode::BAD_REQUEST,
                Json(serde_json::json!({
                    "code": "VALIDATION_ERROR",
                    "message": "Limit cannot exceed 50"
                })),
            )
                .into_response();
        }
    }

    match MessageRepository::get_post_replies(
        &pool,
        &post_id,
        params.after.as_deref(),
        params.limit,
    )
    .await
    {
        Ok(replies) => {
            let reply_responses: Vec<PostResponse> = replies
                .into_iter()
                .map(|reply| PostResponse {
                    id: reply.id,
                    room_id: reply.room_id,
                    sender_mask: reply.sender_mask,
                    body: reply.body,
                    created_at: reply.created_at.to_rfc3339(),
                    reply_count: 0, // Replies don't have replies in MVP
                })
                .collect();

            // Determine if there are more replies
            let next = if reply_responses.len() == params.limit.unwrap_or(50) as usize {
                reply_responses.last().map(|r| r.id.clone())
            } else {
                None
            };

            let mut response = serde_json::json!({
                "items": reply_responses
            });
            
            if let Some(next_cursor) = next {
                response["next"] = serde_json::json!(next_cursor);
            }

            (StatusCode::OK, Json(response)).into_response()
        }
        Err(e) => {
            tracing::error!("Failed to get post replies: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch replies. Please try again."
                })),
            )
                .into_response()
        }
    }
}

pub async fn create_post(
    State(pool): State<Arc<SqlitePool>>,
    State(event_bus): State<Arc<EventBus>>,
    Json(req): Json<CreatePostRequest>,
) -> impl IntoResponse {
    // Validate input
    if req.room_id.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Room ID cannot be empty"
            })),
        )
            .into_response();
    }

    if req.sender_mask.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Sender mask cannot be empty"
            })),
        )
            .into_response();
    }

    if req.body.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Post body cannot be empty"
            })),
        )
            .into_response();
    }

    if req.body.len() > 4096 {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Post body too large (maximum 4096 characters)"
            })),
        )
            .into_response();
    }

    // If parent_post_id is provided, validate it exists and is in the same room
    if let Some(ref parent_id) = req.parent_post_id {
        // Verify parent post exists and is in the same room
        let post_type_str = serde_json::to_string(&MessageType::Post).unwrap_or_else(|_| "\"post\"".to_string());
        let parent_room_check = sqlx::query("SELECT room_id FROM messages WHERE id = ?1 AND message_type = ?2")
            .bind(parent_id)
            .bind(&post_type_str)
            .fetch_optional(&*pool)
            .await;

        match parent_room_check {
            Ok(Some(row)) => {
                let parent_room_id: String = row.get("room_id");
                if parent_room_id != req.room_id {
                    return (
                        StatusCode::BAD_REQUEST,
                        Json(serde_json::json!({
                            "code": "VALIDATION_ERROR",
                            "message": "Parent post must be in the same room"
                        })),
                    )
                        .into_response();
                }
            }
            Ok(None) => {
                return (
                    StatusCode::NOT_FOUND,
                    Json(serde_json::json!({
                        "code": "POST_NOT_FOUND",
                        "message": "Parent post not found"
                    })),
                )
                    .into_response();
            }
            Err(e) => {
                tracing::error!("Failed to validate parent post: {}", e);
                return (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(serde_json::json!({
                        "code": "INTERNAL_ERROR",
                        "message": "Failed to validate parent post"
                    })),
                )
                    .into_response();
            }
        }
    }

    // Check rate limit - same as messages: 10 per 60s
    let rate_limit_key = format!("post:{}:{}", req.room_id, req.sender_mask);
    match RateLimitRepository::check_rate_limit(&pool, &rate_limit_key, "post", 60, 10).await {
        Ok(true) => {
            // Rate limit check passed
        }
        Ok(false) => {
            return (
                StatusCode::TOO_MANY_REQUESTS,
                Json(serde_json::json!({
                    "code": "RATE_LIMITED",
                    "message": "Too many posts. Please wait before creating another post."
                })),
            )
                .into_response();
        }
        Err(e) => {
            tracing::error!("Rate limit check failed: {}", e);
            // Continue on rate limit check error (fail open for MVP)
        }
    }

    // Record the post action for rate limiting
    if let Err(e) = RateLimitRepository::record_action(
        &pool,
        &rate_limit_key,
        "post",
        &format!("room:{}", req.room_id),
    )
    .await
    {
        tracing::warn!("Failed to record post action for rate limiting: {}", e);
    }

    // Store parent_post_id before moving req
    let parent_post_id_clone = req.parent_post_id.clone();
    
    // Create post
    match Message::new(
        req.room_id.clone(),
        req.sender_mask,
        MessageType::Post,
        req.body,
        None, // whisper_id - not used for posts
        parent_post_id_clone.clone(),
    ) {
        Ok(post) => {
            match MessageRepository::create_message(&pool, post.clone()).await {
                Ok(_) => {
                    // Check for auto-highlighting
                    let post_id_to_check = if let Some(ref parent_id) = parent_post_id_clone {
                        // This is a reply - check if parent post should be auto-highlighted
                        parent_id.clone()
                    } else {
                        // This is a top-level post - check if it should be auto-highlighted
                        post.id.clone()
                    };
                    
                    // Check the post (or parent post if this is a reply) for auto-highlighting
                    if let Ok(Some(auto_highlight)) = HighlightRepository::maybe_auto_highlight_post(
                        &pool,
                        &post_id_to_check,
                        &req.room_id,
                    )
                    .await
                    {
                        if let Err(e) = HighlightRepository::create_highlight(&pool, auto_highlight).await {
                            tracing::warn!("Failed to create auto-highlight: {}", e);
                            // Don't fail the post creation if auto-highlight fails
                        }
                    }
                    
                    // Publish event
                    if parent_post_id_clone.is_some() {
                        // This is a reply
                        event_bus.publish(bus::Event {
                            event_type: "post.replied".to_string(),
                            room_id: Some(post.room_id.clone()),
                            whisper_id: None,
                            payload: serde_json::json!({
                                "id": post.id,
                                "room_id": post.room_id,
                                "sender_mask": post.sender_mask,
                                "body": post.body,
                                "created_at": post.created_at.to_rfc3339(),
                                "parent_post_id": parent_post_id_clone,
                            }),
                        });
                    } else {
                        // This is a top-level post
                        event_bus.publish(bus::Event {
                            event_type: "post.created".to_string(),
                            room_id: Some(post.room_id.clone()),
                            whisper_id: None,
                            payload: serde_json::to_value(&post).unwrap_or_default(),
                        });
                    }
                    
                    (
                        StatusCode::CREATED,
                        Json(CreatePostResponse {
                            id: post.id,
                            created_at: post.created_at.to_rfc3339(),
                        }),
                    )
                        .into_response()
                }
                Err(e) => {
                    tracing::error!("Failed to create post: {}", e);
                    (
                        StatusCode::INTERNAL_SERVER_ERROR,
                        Json(serde_json::json!({
                            "code": "INTERNAL_ERROR",
                            "message": "Failed to create post. Please try again."
                        })),
                    )
                        .into_response()
                }
            }
        }
        Err(e) => {
            tracing::warn!("Validation error: {:?}", e);
            let error_message = e.to_string();
            (
                StatusCode::BAD_REQUEST,
                Json(serde_json::json!({
                    "code": "VALIDATION_ERROR",
                    "message": error_message
                })),
            )
                .into_response()
        }
    }
}

