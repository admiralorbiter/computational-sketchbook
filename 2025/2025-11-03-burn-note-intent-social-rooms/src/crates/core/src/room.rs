use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::error::ValidationError;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Room {
    pub id: String,
    pub title: String,
    pub language: String, // ISO 639-1
    pub policy_flags: PolicyFlags,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    // Matching metadata
    pub tags: String, // Comma-separated tags for keyword matching
    pub description: String, // Description for matching
    pub activity_score: f64, // 0.0 to 1.0 based on recent message frequency
    pub member_count: i32, // Current member count
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, Default)]
pub struct PolicyFlags {
    pub sensitive: bool,
    pub curated: bool,
    pub slow_mode: bool,
}

impl PolicyFlags {
    pub fn bitset(&self) -> u8 {
        let mut bits = 0u8;
        if self.sensitive {
            bits |= 1 << 0;
        }
        if self.curated {
            bits |= 1 << 1;
        }
        if self.slow_mode {
            bits |= 1 << 2;
        }
        bits
    }

    pub fn from_bitset(bits: u8) -> Self {
        Self {
            sensitive: (bits & (1 << 0)) != 0,
            curated: (bits & (1 << 1)) != 0,
            slow_mode: (bits & (1 << 2)) != 0,
        }
    }
}

impl Room {
    pub fn new(title: String, language: String, policy_flags: PolicyFlags) -> Result<Self, ValidationError> {
        Self::new_with_metadata(title, language, policy_flags, String::new(), String::new(), 0.0, 0)
    }

    pub fn new_with_metadata(
        title: String,
        language: String,
        policy_flags: PolicyFlags,
        tags: String,
        description: String,
        activity_score: f64,
        member_count: i32,
    ) -> Result<Self, ValidationError> {
        Self::validate(&title, &language)?;
        
        // Validate activity_score is in range [0.0, 1.0]
        let activity_score = activity_score.max(0.0).min(1.0);
        // Validate member_count is non-negative
        let member_count = member_count.max(0);
        
        let now = Utc::now();
        Ok(Self {
            id: Uuid::new_v4().to_string(),
            title,
            language,
            policy_flags,
            created_at: now,
            updated_at: now,
            tags,
            description,
            activity_score,
            member_count,
        })
    }

    pub fn validate(title: &str, language: &str) -> Result<(), ValidationError> {
        if title.trim().is_empty() {
            return Err(ValidationError::EmptyTitle);
        }
        
        // Basic ISO 639-1 validation (2 characters)
        if language.len() != 2 || !language.chars().all(|c| c.is_ascii_lowercase()) {
            return Err(ValidationError::InvalidLanguage);
        }
        
        Ok(())
    }

    pub fn update(&mut self, title: Option<String>, language: Option<String>) -> Result<(), ValidationError> {
        if let Some(ref t) = title {
            if t.trim().is_empty() {
                return Err(ValidationError::EmptyTitle);
            }
            self.title = t.clone();
        }
        
        if let Some(ref l) = language {
            if l.len() != 2 || !l.chars().all(|c| c.is_ascii_lowercase()) {
                return Err(ValidationError::InvalidLanguage);
            }
            self.language = l.clone();
        }
        
        self.updated_at = Utc::now();
        Ok(())
    }

    // Methods to update matching metadata
    pub fn update_activity_score(&mut self, score: f64) {
        self.activity_score = score.max(0.0).min(1.0);
        self.updated_at = Utc::now();
    }

    pub fn update_member_count(&mut self, count: i32) {
        self.member_count = count.max(0);
        self.updated_at = Utc::now();
    }

    pub fn update_metadata(&mut self, tags: Option<String>, description: Option<String>) {
        if let Some(t) = tags {
            self.tags = t;
        }
        if let Some(d) = description {
            self.description = d;
        }
        self.updated_at = Utc::now();
    }
}
