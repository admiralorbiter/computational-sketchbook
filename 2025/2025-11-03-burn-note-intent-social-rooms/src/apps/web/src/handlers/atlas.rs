use axum::{
    extract::State,
    http::StatusCode,
    response::{IntoResponse, Json},
};
use serde::Serialize;
use sqlx::SqlitePool;
use std::sync::Arc;

use storage::RoomRepository;

#[derive(Serialize)]
pub struct AtlasResponse {
    pub rooms: Vec<AtlasRoomInfo>,
    pub updated_at: String,
}

#[derive(Serialize)]
pub struct AtlasRoomInfo {
    pub id: String,
    pub title: String,
    pub tags: String,
    pub activity_score: f64,
    pub language: String,
    pub policy_flags: PolicyFlagsInfo,
}

#[derive(Serialize)]
pub struct PolicyFlagsInfo {
    pub sensitive: bool,
    pub curated: bool,
    pub slow_mode: bool,
}

pub async fn get_atlas(State(pool): State<Arc<SqlitePool>>) -> impl IntoResponse {
    match RoomRepository::list_rooms(&pool).await {
        Ok(rooms) => {
            let atlas_rooms: Vec<AtlasRoomInfo> = rooms
                .into_iter()
                .map(|room| AtlasRoomInfo {
                    id: room.id,
                    title: room.title,
                    tags: room.tags,
                    activity_score: room.activity_score,
                    language: room.language,
                    policy_flags: PolicyFlagsInfo {
                        sensitive: room.policy_flags.sensitive,
                        curated: room.policy_flags.curated,
                        slow_mode: room.policy_flags.slow_mode,
                    },
                })
                .collect();

            let response = AtlasResponse {
                rooms: atlas_rooms,
                updated_at: chrono::Utc::now().to_rfc3339(),
            };

            (StatusCode::OK, Json(response)).into_response()
        }
        Err(e) => {
            tracing::error!("Failed to fetch rooms for atlas: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch room atlas"
                })),
            )
                .into_response()
        }
    }
}
