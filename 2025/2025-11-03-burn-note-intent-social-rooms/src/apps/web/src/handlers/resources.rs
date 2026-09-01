use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use std::sync::Arc;

use storage::{ResourceRepository, RateLimitRepository};
use core::Resource;

#[derive(Deserialize)]
pub struct GetResourcesQuery {
    pub after: Option<String>,
    pub limit: Option<u32>,
    pub category: Option<String>,
}

#[derive(Serialize)]
pub struct ResourceResponse {
    pub id: String,
    pub room_id: String,
    pub title: String,
    pub url: String,
    pub description: Option<String>,
    pub category: Option<String>,
    pub curator_mask: String,
    pub created_at: String,
    pub updated_at: String,
    pub is_verified: bool,
}

#[derive(Deserialize)]
pub struct CreateResourceRequest {
    pub title: String,
    pub url: String,
    pub description: Option<String>,
    pub category: Option<String>,
}

#[derive(Serialize)]
pub struct CreateResourceResponse {
    pub id: String,
    pub created_at: String,
}

#[derive(Deserialize)]
pub struct UpdateResourceRequest {
    pub title: Option<String>,
    pub url: Option<String>,
    pub description: Option<String>,
    pub category: Option<String>,
}

#[derive(Serialize)]
pub struct UpdateResourceResponse {
    pub id: String,
    pub updated_at: String,
}

pub async fn get_resources(
    State(pool): State<Arc<SqlitePool>>,
    Path(room_id): Path<String>,
    Query(params): Query<GetResourcesQuery>,
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

    match ResourceRepository::get_resources(
        &pool,
        &room_id,
        params.after.as_deref(),
        params.limit,
        params.category.as_deref(),
    )
    .await
    {
        Ok(resources) => {
            let resource_responses: Vec<ResourceResponse> = resources
                .into_iter()
                .map(|r| ResourceResponse {
                    id: r.id,
                    room_id: r.room_id,
                    title: r.title,
                    url: r.url,
                    description: r.description,
                    category: r.category,
                    curator_mask: r.curator_mask,
                    created_at: r.created_at.to_rfc3339(),
                    updated_at: r.updated_at.to_rfc3339(),
                    is_verified: r.is_verified,
                })
                .collect();

            // Determine if there are more resources
            let next = if resource_responses.len() == params.limit.unwrap_or(50) as usize {
                resource_responses.last().map(|r| r.id.clone())
            } else {
                None
            };

            let mut response = serde_json::json!({
                "items": resource_responses
            });
            
            if let Some(next_cursor) = next {
                response["next"] = serde_json::json!(next_cursor);
            }

            (StatusCode::OK, Json(response)).into_response()
        }
        Err(e) => {
            tracing::error!("Failed to get resources: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch resources. Please try again."
                })),
            )
                .into_response()
        }
    }
}

pub async fn create_resource(
    State(pool): State<Arc<SqlitePool>>,
    Path(room_id): Path<String>,
    Json(req): Json<CreateResourceRequest>,
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

    if req.url.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "URL cannot be empty"
            })),
        )
            .into_response();
    }

    // For MVP, we'll use a placeholder curator_mask from a header or default
    // In a real implementation, this would come from session middleware
    // For now, we'll use a default "anonymous" curator
    let curator_mask = "anonymous".to_string(); // TODO: Get from session when middleware is added

    // Check rate limit - 10 resources per 60s per room
    let rate_limit_key = format!("resource:{}:{}", room_id, curator_mask);
    match RateLimitRepository::check_rate_limit(&pool, &rate_limit_key, "resource", 60, 10).await {
        Ok(true) => {
            // Rate limit check passed
        }
        Ok(false) => {
            return (
                StatusCode::TOO_MANY_REQUESTS,
                Json(serde_json::json!({
                    "code": "RATE_LIMITED",
                    "message": "Too many resources. Please wait before creating another resource."
                })),
            )
                .into_response();
        }
        Err(e) => {
            tracing::error!("Rate limit check failed: {}", e);
            // Continue on rate limit check error (fail open for MVP)
        }
    }

    // Record the resource action for rate limiting
    if let Err(e) = RateLimitRepository::record_action(
        &pool,
        &rate_limit_key,
        "resource",
        &format!("room:{}", room_id),
    )
    .await
    {
        tracing::warn!("Failed to record resource action for rate limiting: {}", e);
    }

    // Create resource
    match Resource::new(
        room_id,
        req.title,
        req.url,
        req.description,
        req.category,
        curator_mask,
    ) {
        Ok(resource) => {
            match ResourceRepository::create_resource(&pool, resource.clone()).await {
                Ok(_) => {
                    (
                        StatusCode::CREATED,
                        Json(CreateResourceResponse {
                            id: resource.id,
                            created_at: resource.created_at.to_rfc3339(),
                        }),
                    )
                        .into_response()
                }
                Err(e) => {
                    tracing::error!("Failed to create resource: {}", e);
                    (
                        StatusCode::INTERNAL_SERVER_ERROR,
                        Json(serde_json::json!({
                            "code": "INTERNAL_ERROR",
                            "message": "Failed to create resource. Please try again."
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

pub async fn update_resource(
    State(pool): State<Arc<SqlitePool>>,
    Path(resource_id): Path<String>,
    Json(req): Json<UpdateResourceRequest>,
) -> impl IntoResponse {
    // Get resource to check curator and get current values
    let resource_opt = match ResourceRepository::get_resource_by_id(&pool, &resource_id).await {
        Ok(Some(resource)) => resource,
        Ok(None) => {
            return (
                StatusCode::NOT_FOUND,
                Json(serde_json::json!({
                    "code": "RESOURCE_NOT_FOUND",
                    "message": "Resource not found"
                })),
            )
                .into_response();
        }
        Err(e) => {
            tracing::error!("Failed to get resource: {}", e);
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to check resource. Please try again."
                })),
            )
                .into_response();
        }
    };

    // For MVP, allow update if curator is "system" or "anonymous"
    // In a real implementation, this would check session match
    if resource_opt.curator_mask != "system" && resource_opt.curator_mask != "anonymous" {
        return (
            StatusCode::FORBIDDEN,
            Json(serde_json::json!({
                "code": "FORBIDDEN",
                "message": "Only the curator can update this resource"
            })),
        )
            .into_response();
    }

    // Create updated resource
    let mut updated_resource = resource_opt.clone();
    
    // Update fields if provided
    match updated_resource.update(
        req.title,
        req.url,
        req.description,
        req.category,
    ) {
        Ok(_) => {
            match ResourceRepository::update_resource(&pool, &updated_resource).await {
                Ok(_) => {
                    (
                        StatusCode::OK,
                        Json(UpdateResourceResponse {
                            id: updated_resource.id,
                            updated_at: updated_resource.updated_at.to_rfc3339(),
                        }),
                    )
                        .into_response()
                }
                Err(e) => {
                    tracing::error!("Failed to update resource: {}", e);
                    (
                        StatusCode::INTERNAL_SERVER_ERROR,
                        Json(serde_json::json!({
                            "code": "INTERNAL_ERROR",
                            "message": "Failed to update resource. Please try again."
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

pub async fn delete_resource(
    State(pool): State<Arc<SqlitePool>>,
    Path(resource_id): Path<String>,
) -> impl IntoResponse {
    // Get resource to check curator
    match ResourceRepository::get_resource_by_id(&pool, &resource_id).await {
        Ok(Some(resource)) => {
            // For MVP, allow deletion if curator is "system" or "anonymous"
            // In a real implementation, this would check session match
            if resource.curator_mask == "system" || resource.curator_mask == "anonymous" {
                match ResourceRepository::delete_resource(&pool, &resource_id).await {
                    Ok(true) => StatusCode::NO_CONTENT.into_response(),
                    Ok(false) => {
                        (
                            StatusCode::NOT_FOUND,
                            Json(serde_json::json!({
                                "code": "RESOURCE_NOT_FOUND",
                                "message": "Resource not found"
                            })),
                        )
                            .into_response()
                    }
                    Err(e) => {
                        tracing::error!("Failed to delete resource: {}", e);
                        (
                            StatusCode::INTERNAL_SERVER_ERROR,
                            Json(serde_json::json!({
                                "code": "INTERNAL_ERROR",
                                "message": "Failed to delete resource. Please try again."
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
                        "message": "Only the curator can delete this resource"
                    })),
                )
                    .into_response()
            }
        }
        Ok(None) => {
            (
                StatusCode::NOT_FOUND,
                Json(serde_json::json!({
                    "code": "RESOURCE_NOT_FOUND",
                    "message": "Resource not found"
                })),
            )
                .into_response()
        }
        Err(e) => {
            tracing::error!("Failed to get resource: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to check resource. Please try again."
                })),
            )
                .into_response()
        }
    }
}

