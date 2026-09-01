use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use serde::{Deserialize, Serialize};
use sqlx::{SqlitePool, Row};
use std::sync::Arc;

use storage::{HighlightRepository, RateLimitRepository};
use core::{Highlight, HighlightReferenceType};

#[derive(Deserialize)]
pub struct GetHighlightsQuery {
    pub after: Option<String>,
    pub limit: Option<u32>,
    #[serde(rename = "last_24h")]
    pub last_24h: Option<bool>,
}

#[derive(Serialize)]
pub struct HighlightResponse {
    pub id: String,
    pub room_id: String,
    pub title: String,
    pub reference_type: String,
    pub reference_id: Option<String>,
    pub curator_mask: String,
    pub created_at: String,
    pub is_auto: bool,
}

#[derive(Deserialize)]
pub struct CreateHighlightRequest {
    pub title: String,
    pub reference_type: Option<String>,
    pub reference_id: Option<String>,
}

#[derive(Serialize)]
pub struct CreateHighlightResponse {
    pub id: String,
    pub created_at: String,
}

pub async fn get_highlights(
    State(pool): State<Arc<SqlitePool>>,
    Path(room_id): Path<String>,
    Query(params): Query<GetHighlightsQuery>,
) -> impl IntoResponse {
    // Validate input
    if room_id.trim().is_empty() {
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

    let last_24h = params.last_24h.unwrap_or(false);

    match HighlightRepository::get_highlights(
        &pool,
        &room_id,
        params.after.as_deref(),
        params.limit,
        last_24h,
    )
    .await
    {
        Ok(highlights) => {
            let highlight_responses: Vec<HighlightResponse> = highlights
                .into_iter()
                .map(|h| HighlightResponse {
                    id: h.id,
                    room_id: h.room_id,
                    title: h.title,
                    reference_type: serde_json::to_string(&h.reference_type)
                        .unwrap_or_else(|_| "standalone".to_string())
                        .trim_matches('"')
                        .to_string(),
                    reference_id: h.reference_id,
                    curator_mask: h.curator_mask,
                    created_at: h.created_at.to_rfc3339(),
                    is_auto: h.is_auto,
                })
                .collect();

            // Determine if there are more highlights
            let next = if highlight_responses.len() == params.limit.unwrap_or(50) as usize {
                highlight_responses.last().map(|h| h.id.clone())
            } else {
                None
            };

            let mut response = serde_json::json!({
                "items": highlight_responses
            });
            
            if let Some(next_cursor) = next {
                response["next"] = serde_json::json!(next_cursor);
            }

            (StatusCode::OK, Json(response)).into_response()
        }
        Err(e) => {
            tracing::error!("Failed to get highlights: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch highlights. Please try again."
                })),
            )
                .into_response()
        }
    }
}

pub async fn create_highlight(
    State(pool): State<Arc<SqlitePool>>,
    Path(room_id): Path<String>,
    Json(req): Json<CreateHighlightRequest>,
) -> impl IntoResponse {
    // Validate input
    if room_id.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Room ID cannot be empty"
            })),
        )
            .into_response();
    }

    if req.title.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Title cannot be empty"
            })),
        )
            .into_response();
    }

    // Parse reference type
    let reference_type = if let Some(ref_type_str) = &req.reference_type {
        match ref_type_str.as_str() {
            "message" => HighlightReferenceType::Message,
            "post" => HighlightReferenceType::Post,
            "standalone" | "" => HighlightReferenceType::Standalone,
            _ => {
                return (
                    StatusCode::BAD_REQUEST,
                    Json(serde_json::json!({
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid reference type. Must be 'message', 'post', or 'standalone'"
                    })),
                )
                    .into_response();
            }
        }
    } else {
        HighlightReferenceType::Standalone
    };

    // If reference_id is provided, validate it exists
    if let Some(ref ref_id) = req.reference_id {
        if reference_type == HighlightReferenceType::Standalone {
            return (
                StatusCode::BAD_REQUEST,
                Json(serde_json::json!({
                    "code": "VALIDATION_ERROR",
                    "message": "Reference ID cannot be provided for standalone highlights"
                })),
            )
                .into_response();
        }

        // Verify reference exists
        let reference_check = match reference_type {
            HighlightReferenceType::Message | HighlightReferenceType::Post => {
                sqlx::query("SELECT room_id FROM messages WHERE id = ?1")
                    .bind(ref_id)
                    .fetch_optional(&*pool)
                    .await
            }
            HighlightReferenceType::Standalone => unreachable!(),
        };

        match reference_check {
            Ok(Some(row)) => {
                let ref_room_id: String = row.get("room_id");
                if ref_room_id != room_id {
                    return (
                        StatusCode::BAD_REQUEST,
                        Json(serde_json::json!({
                            "code": "VALIDATION_ERROR",
                            "message": "Reference must be in the same room"
                        })),
                    )
                        .into_response();
                }
            }
            Ok(None) => {
                return (
                    StatusCode::NOT_FOUND,
                    Json(serde_json::json!({
                        "code": "REFERENCE_NOT_FOUND",
                        "message": "Referenced message or post not found"
                    })),
                )
                    .into_response();
            }
            Err(e) => {
                tracing::error!("Failed to validate reference: {}", e);
                return (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(serde_json::json!({
                        "code": "INTERNAL_ERROR",
                        "message": "Failed to validate reference"
                    })),
                )
                    .into_response();
            }
        }
    }

    // For MVP, we'll use a placeholder curator_mask from a header or default
    // In a real implementation, this would come from session middleware
    // For now, we'll use a default "anonymous" curator
    let curator_mask = "anonymous".to_string(); // TODO: Get from session when middleware is added

    // Check rate limit - 5 highlights per 60s per room
    let rate_limit_key = format!("highlight:{}:{}", room_id, curator_mask);
    match RateLimitRepository::check_rate_limit(&pool, &rate_limit_key, "highlight", 60, 5).await {
        Ok(true) => {
            // Rate limit check passed
        }
        Ok(false) => {
            return (
                StatusCode::TOO_MANY_REQUESTS,
                Json(serde_json::json!({
                    "code": "RATE_LIMITED",
                    "message": "Too many highlights. Please wait before creating another highlight."
                })),
            )
                .into_response();
        }
        Err(e) => {
            tracing::error!("Rate limit check failed: {}", e);
            // Continue on rate limit check error (fail open for MVP)
        }
    }

    // Record the highlight action for rate limiting
    if let Err(e) = RateLimitRepository::record_action(
        &pool,
        &rate_limit_key,
        "highlight",
        &format!("room:{}", room_id),
    )
    .await
    {
        tracing::warn!("Failed to record highlight action for rate limiting: {}", e);
    }

    // Create highlight
    match Highlight::new(
        room_id,
        req.title,
        reference_type,
        req.reference_id,
        curator_mask,
    ) {
        Ok(highlight) => {
            match HighlightRepository::create_highlight(&pool, highlight.clone()).await {
                Ok(_) => {
                    (
                        StatusCode::CREATED,
                        Json(CreateHighlightResponse {
                            id: highlight.id,
                            created_at: highlight.created_at.to_rfc3339(),
                        }),
                    )
                        .into_response()
                }
                Err(e) => {
                    tracing::error!("Failed to create highlight: {}", e);
                    (
                        StatusCode::INTERNAL_SERVER_ERROR,
                        Json(serde_json::json!({
                            "code": "INTERNAL_ERROR",
                            "message": "Failed to create highlight. Please try again."
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

pub async fn delete_highlight(
    State(pool): State<Arc<SqlitePool>>,
    Path(highlight_id): Path<String>,
) -> impl IntoResponse {
    // Get highlight to check curator
    match HighlightRepository::get_highlight_by_id(&pool, &highlight_id).await {
        Ok(Some(highlight)) => {
            // For MVP, allow deletion if curator is "system" or "anonymous"
            // In a real implementation, this would check session match
            if highlight.curator_mask == "system" || highlight.curator_mask == "anonymous" {
                match HighlightRepository::delete_highlight(&pool, &highlight_id).await {
                    Ok(true) => StatusCode::NO_CONTENT.into_response(),
                    Ok(false) => {
                        (
                            StatusCode::NOT_FOUND,
                            Json(serde_json::json!({
                                "code": "HIGHLIGHT_NOT_FOUND",
                                "message": "Highlight not found"
                            })),
                        )
                            .into_response()
                    }
                    Err(e) => {
                        tracing::error!("Failed to delete highlight: {}", e);
                        (
                            StatusCode::INTERNAL_SERVER_ERROR,
                            Json(serde_json::json!({
                                "code": "INTERNAL_ERROR",
                                "message": "Failed to delete highlight. Please try again."
                            })),
                        )
                            .into_response()
                    }
                }
            } else {
                (
                    StatusCode::FORBIDDEN,
                    Json(serde_json::json!({
                        "code": "FORBIDDEN",
                        "message": "Only the curator can delete this highlight"
                    })),
                )
                    .into_response()
            }
        }
        Ok(None) => {
            (
                StatusCode::NOT_FOUND,
                Json(serde_json::json!({
                    "code": "HIGHLIGHT_NOT_FOUND",
                    "message": "Highlight not found"
                })),
            )
                .into_response()
        }
        Err(e) => {
            tracing::error!("Failed to get highlight: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to check highlight. Please try again."
                })),
            )
                .into_response()
        }
    }
}

