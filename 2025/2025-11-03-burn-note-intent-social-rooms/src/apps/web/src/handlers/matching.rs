use axum::{
    extract::State,
    http::StatusCode,
    response::{IntoResponse, Json},
};
use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use std::sync::Arc;

use storage::RoomRepository;
use core::{Room, PolicyFlags, ValidationError};

// Matching thresholds
const MIN_MATCH_SCORE: f64 = 0.35; // 35% minimum to show a room
const GOOD_MATCH_THRESHOLD: f64 = 0.60; // 60% for "good" matches

#[derive(Deserialize)]
pub struct MatchIntentRequest {
    pub intent: String,
    pub include_sensitive: Option<bool>,
}

#[derive(Serialize)]
pub struct MatchIntentResponse {
    pub rooms: Vec<MatchedRoom>,
    pub alternatives: Vec<MatchedRoom>,
}

#[derive(Serialize)]
pub struct MatchedRoom {
    pub room: RoomInfo,
    pub score: f64,
    pub reason: String,
}

#[derive(Serialize)]
pub struct RoomInfo {
    pub id: String,
    pub title: String,
    pub language: String,
    pub tags: String,
    pub description: String,
    pub activity_score: f64,
    pub member_count: i32,
}

pub async fn match_intent(
    State(pool): State<Arc<SqlitePool>>,
    Json(req): Json<MatchIntentRequest>,
) -> impl IntoResponse {
    // Validate input
    if req.intent.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Intent cannot be empty"
            })),
        ).into_response();
    }

    // Normalize intent: lowercase and split into keywords
    let normalized_intent = req.intent.to_lowercase();
    let keywords: Vec<&str> = normalized_intent
        .split_whitespace()
        .filter(|w| w.len() > 2) // Filter out very short words
        .collect();

    if keywords.is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({
                "code": "VALIDATION_ERROR",
                "message": "Intent must contain meaningful words"
            })),
        ).into_response();
    }

    // Get all rooms
    let rooms = match RoomRepository::list_rooms(&pool).await {
        Ok(rooms) => rooms,
        Err(e) => {
            tracing::error!("Failed to list rooms for matching: {}", e);
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch rooms for matching"
                })),
            ).into_response();
        }
    };

    // Score each room based on keyword matching
    let include_sensitive = req.include_sensitive.unwrap_or(false);
    let mut scored_rooms: Vec<(Room, f64, String)> = rooms
        .into_iter()
        .filter_map(|room| {
            // Filter out sensitive rooms if not included
            if !include_sensitive && room.policy_flags.sensitive {
                return None;
            }

            let score_result = score_room(&room, &keywords);
            let score = score_result.0;
            
            // Filter out rooms below minimum threshold
            if score < MIN_MATCH_SCORE {
                return None;
            }
            
            Some((room, score, score_result.1))
        })
        .collect();

    // Sort by score (highest first)
    scored_rooms.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));

    // Check if we need to create a new room (no good matches)
    if scored_rooms.is_empty() || scored_rooms[0].1 < GOOD_MATCH_THRESHOLD {
        // Create a new room based on the intent
        match create_room_from_intent(&req.intent, &pool).await {
            Ok(new_room) => {
                return (
                    StatusCode::OK,
                    Json(MatchIntentResponse {
                        rooms: vec![MatchedRoom {
                            room: RoomInfo {
                                id: new_room.id.clone(),
                                title: new_room.title.clone(),
                                language: new_room.language.clone(),
                                tags: new_room.tags.clone(),
                                description: new_room.description.clone(),
                                activity_score: new_room.activity_score,
                                member_count: new_room.member_count,
                            },
                            score: 1.0,
                            reason: "New room created just for your interest".to_string(),
                        }],
                        alternatives: vec![],
                    }),
                )
                    .into_response();
            }
            Err(e) => {
                tracing::error!("Failed to create room from intent: {}", e);
                // Fall through to return empty results or whatever we have
            }
        }
    }

    // Take top 3 for main results
    let top_rooms: Vec<MatchedRoom> = scored_rooms
        .iter()
        .take(3)
        .map(|(room, score, reason)| MatchedRoom {
            room: RoomInfo {
                id: room.id.clone(),
                title: room.title.clone(),
                language: room.language.clone(),
                tags: room.tags.clone(),
                description: room.description.clone(),
                activity_score: room.activity_score,
                member_count: room.member_count,
            },
            score: *score,
            reason: reason.clone(),
        })
        .collect();

    // For alternatives, use MMR diversification to avoid near-duplicates
    let alternatives = if scored_rooms.len() > 3 {
        diversify_rooms_matched(&scored_rooms[3..], &top_rooms, 3)
            .iter()
            .map(|(room, score, reason)| MatchedRoom {
                room: RoomInfo {
                    id: room.id.clone(),
                    title: room.title.clone(),
                    language: room.language.clone(),
                    tags: room.tags.clone(),
                    description: room.description.clone(),
                    activity_score: room.activity_score,
                    member_count: room.member_count,
                },
                score: *score,
                reason: reason.clone(),
            })
            .collect()
    } else {
        Vec::new()
    };

    (
        StatusCode::OK,
        Json(MatchIntentResponse {
            rooms: top_rooms,
            alternatives,
        }),
    )
        .into_response()
}

fn score_room(room: &Room, keywords: &[&str]) -> (f64, String) {
    let mut score = 0.0;
    let mut matched_keywords = Vec::new();

    // Combine room text fields for matching
    let room_text = format!("{} {} {}", room.title, room.tags, room.description).to_lowercase();
    let room_words: Vec<&str> = room_text.split_whitespace().collect();

    // Score based on keyword overlap (weighted)
    for keyword in keywords {
        // Check title matches (highest weight)
        if room.title.to_lowercase().contains(keyword) {
            score += 0.6;
            matched_keywords.push(format!("title:{}", keyword));
        }
        // Check tags matches (medium weight)
        if room.tags.to_lowercase().contains(keyword) {
            score += 0.3;
            matched_keywords.push(format!("tag:{}", keyword));
        }
        // Check description matches (lower weight)
        if room.description.to_lowercase().contains(keyword) {
            score += 0.2;
            matched_keywords.push(format!("desc:{}", keyword));
        }
        // Check general word overlap
        if room_words.contains(keyword) {
            score += 0.1;
        }
    }

    // Boost by activity score (0.0 to 1.0) - weight 0.2
    score += room.activity_score * 0.2;

    // Boost by member count (normalized, max 100) - weight 0.1
    let member_boost = (room.member_count.min(100) as f64 / 100.0) * 0.1;
    score += member_boost;

    // Generate qualitative reason string
    let reason = generate_match_reason(score, matched_keywords, room);
    
    (score, reason)
}

fn generate_match_reason(score: f64, matched_keywords: Vec<String>, room: &Room) -> String {
    if matched_keywords.is_empty() {
        if score >= 0.40 {
            "Community exploring related topics".to_string()
        } else {
            format!("General match (activity: {:.2}, members: {})", room.activity_score, room.member_count)
        }
    } else {
        let topics = summarize_topics(&matched_keywords);
        if score >= 0.80 {
            format!("Highly relevant community discussing {}", topics)
        } else if score >= 0.60 {
            format!("Active discussions about {}", topics)
        } else {
            format!("Community exploring related topics: {}", topics)
        }
    }
}

fn summarize_topics(matches: &[String]) -> String {
    // Extract keywords from matches like "title:tech", "tag:programming", etc.
    let mut keywords: Vec<String> = Vec::new();
    for m in matches {
        if let Some((_, keyword)) = m.split_once(':') {
            keywords.push(keyword.to_string());
        }
    }
    
    // Remove duplicates and take top 3
    keywords.sort();
    keywords.dedup();
    keywords.truncate(3);
    
    if keywords.is_empty() {
        "various topics".to_string()
    } else if keywords.len() == 1 {
        keywords[0].clone()
    } else if keywords.len() == 2 {
        format!("{} and {}", keywords[0], keywords[1])
    } else {
        format!("{}, {}, and {}", keywords[0], keywords[1], keywords[2])
    }
}

async fn create_room_from_intent(
    intent: &str,
    pool: &SqlitePool,
) -> Result<Room, ValidationError> {
    // Extract key concepts from intent (simple version for MVP)
    let title = generate_room_title(intent);
    let tags = extract_tags(intent);
    let description = format!("Room for discussing: {}", intent);
    
    // Create room with metadata
    let room = Room::new_with_metadata(
        title,
        "en".to_string(),
        PolicyFlags::default(),
        tags,
        description,
        0.5, // Start with medium activity score
        0,   // Zero members initially
    )?;
    
    // Insert room directly into database (similar to RoomRepository::create_room but with metadata)
    sqlx::query(
        r#"
        INSERT INTO rooms (id, title, language, policy_flags, created_at, updated_at, tags, description, activity_score, member_count)
        VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)
        "#,
    )
    .bind(&room.id)
    .bind(&room.title)
    .bind(&room.language)
    .bind(room.policy_flags.bitset() as i64)
    .bind(room.created_at.to_rfc3339())
    .bind(room.updated_at.to_rfc3339())
    .bind(&room.tags)
    .bind(&room.description)
    .bind(room.activity_score)
    .bind(room.member_count)
    .execute(pool)
    .await
    .map_err(|e| ValidationError::Failed(format!("Failed to create room: {}", e)))?;
    
    tracing::info!("Created new room '{}' from intent: {}", room.title, intent);
    Ok(room)
}

fn generate_room_title(intent: &str) -> String {
    // MVP: Simple title generation
    // Take first 3-5 keywords, capitalize
    // Future: Use LLM to generate creative titles
    let words: Vec<&str> = intent
        .split_whitespace()
        .filter(|w| w.len() > 3)
        .take(4)
        .collect();
    
    if words.is_empty() {
        // Fallback: take first few words regardless of length
        let fallback_words: Vec<&str> = intent
            .split_whitespace()
            .take(3)
            .collect();
        
        if fallback_words.is_empty() {
            "Discussion Room".to_string()
        } else {
            fallback_words.iter()
                .map(|w| capitalize_first(w))
                .collect::<Vec<_>>()
                .join(" ")
        }
    } else {
        words.iter()
            .map(|w| capitalize_first(w))
            .collect::<Vec<_>>()
            .join(" ")
    }
}

fn capitalize_first(s: &str) -> String {
    let mut chars = s.chars();
    match chars.next() {
        None => String::new(),
        Some(first) => first.to_uppercase().collect::<String>() + chars.as_str(),
    }
}

fn extract_tags(intent: &str) -> String {
    // MVP: Extract nouns/keywords as tags
    // Future: Use NLP/embeddings
    intent
        .to_lowercase()
        .split_whitespace()
        .filter(|w| w.len() > 3)
        .take(5)
        .collect::<Vec<_>>()
        .join(",")
}

fn diversify_rooms_matched(
    candidates: &[(Room, f64, String)],
    selected: &[MatchedRoom],
    max_count: usize,
) -> Vec<(Room, f64, String)> {
    if candidates.is_empty() || max_count == 0 {
        return Vec::new();
    }

    let mut result: Vec<(Room, f64, String)> = Vec::new();
    let mut remaining: Vec<&(Room, f64, String)> = candidates.iter().collect();

    // Lambda for MMR diversity (0.3 = moderate diversity)
    let lambda = 0.3;

    while result.len() < max_count && !remaining.is_empty() {
        let best = remaining
            .iter()
            .enumerate()
            .max_by(|(_, a), (_, b)| {
                let a_score = a.1 - lambda * similarity_to_selected_matched(&a.0, selected);
                let b_score = b.1 - lambda * similarity_to_selected_matched(&b.0, selected);
                a_score.partial_cmp(&b_score).unwrap_or(std::cmp::Ordering::Equal)
            })
            .map(|(idx, item)| (idx, (**item).clone()));

        if let Some((idx, item)) = best {
            result.push((item.0.clone(), item.1, item.2.clone()));
            remaining.remove(idx);
        } else {
            break;
        }
    }

    result
}

// Overload for MatchedRoom (used in diversify_rooms with top_rooms)
fn similarity_to_selected_matched(room: &Room, selected: &[MatchedRoom]) -> f64 {
    if selected.is_empty() {
        return 0.0;
    }

    let mut max_similarity: f64 = 0.0;
    let room_text = format!("{} {}", room.tags, room.description).to_lowercase();
    let room_words: std::collections::HashSet<&str> = room_text.split_whitespace().collect();

    for matched in selected {
        let selected_text = format!("{} {}", matched.room.tags, matched.room.description).to_lowercase();
        let selected_words: std::collections::HashSet<&str> = selected_text.split_whitespace().collect();
        
        // Jaccard similarity
        let intersection = room_words.intersection(&selected_words).count();
        let union = room_words.union(&selected_words).count();
        let similarity = if union > 0 {
            intersection as f64 / union as f64
        } else {
            0.0
        };
        
        max_similarity = max_similarity.max(similarity);
    }

    max_similarity
}
