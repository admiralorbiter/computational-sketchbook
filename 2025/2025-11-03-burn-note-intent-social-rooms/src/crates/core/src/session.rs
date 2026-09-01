use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::error::SessionError;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserSession {
    pub id: String,
    pub room_id: String,
    pub session_mask: String,
    pub created_at: DateTime<Utc>,
    pub expires_at: DateTime<Utc>,
}

impl UserSession {
    pub fn new(room_id: String, ttl_hours: i64) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4().to_string(),
            room_id,
            session_mask: SessionMask::generate(),
            created_at: now,
            expires_at: now + chrono::Duration::hours(ttl_hours),
        }
    }

    pub fn is_expired(&self) -> bool {
        Utc::now() > self.expires_at
    }

    pub fn validate(&self) -> Result<(), SessionError> {
        if self.is_expired() {
            return Err(SessionError::Expired);
        }
        
        if !SessionMask::is_valid(&self.session_mask) {
            return Err(SessionError::InvalidMask);
        }
        
        Ok(())
    }
}

pub struct SessionMask;

impl SessionMask {
    /// Generate a random session mask in format "Word-####" (e.g., "Fox-7291")
    pub fn generate() -> String {
        let adjectives = [
            "Fox", "Owl", "Bear", "Wolf", "Eagle", "Hawk", "Lynx", "Puma",
            "Raven", "Swan", "Deer", "Elk", "Falcon", "Jaguar", "Tiger", "Lion",
            "Otter", "Seal", "Whale", "Dolphin", "Shark", "Stag", "Horse", "Elk",
        ];
        
        let numbers = fastrand::u32(1000..=9999);
        let adjective = fastrand::choice(adjectives).unwrap();
        
        format!("{}-{}", adjective, numbers)
    }

    /// Validate that a string matches the session mask format
    pub fn is_valid(mask: &str) -> bool {
        let parts: Vec<&str> = mask.split('-').collect();
        if parts.len() != 2 {
            return false;
        }
        
        // First part should be alphabetic
        if !parts[0].chars().all(|c| c.is_alphabetic()) || parts[0].is_empty() {
            return false;
        }
        
        // Second part should be 4 digits
        parts[1].len() == 4 && parts[1].chars().all(|c| c.is_ascii_digit())
    }
}
