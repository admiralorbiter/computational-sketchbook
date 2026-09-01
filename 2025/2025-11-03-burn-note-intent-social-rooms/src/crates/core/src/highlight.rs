use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::error::ValidationError;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum HighlightReferenceType {
    Message,
    Post,
    Standalone,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Highlight {
    pub id: String,
    pub room_id: String,
    pub title: String,
    pub reference_type: HighlightReferenceType,
    pub reference_id: Option<String>,
    pub curator_mask: String,
    pub created_at: DateTime<Utc>,
    pub is_auto: bool,
}

impl Highlight {
    pub const MAX_TITLE_LENGTH: usize = 200;

    pub fn new(
        room_id: String,
        title: String,
        reference_type: HighlightReferenceType,
        reference_id: Option<String>,
        curator_mask: String,
    ) -> Result<Self, ValidationError> {
        Self::validate(&room_id, &title, &reference_type, &reference_id)?;

        Ok(Self {
            id: Uuid::new_v4().to_string(),
            room_id,
            title,
            reference_type,
            reference_id,
            curator_mask,
            created_at: Utc::now(),
            is_auto: false,
        })
    }

    pub fn new_auto(
        room_id: String,
        title: String,
        reference_type: HighlightReferenceType,
        reference_id: Option<String>,
    ) -> Result<Self, ValidationError> {
        Self::validate(&room_id, &title, &reference_type, &reference_id)?;

        Ok(Self {
            id: Uuid::new_v4().to_string(),
            room_id,
            title,
            reference_type,
            reference_id,
            curator_mask: "system".to_string(),
            created_at: Utc::now(),
            is_auto: true,
        })
    }

    pub fn validate(
        room_id: &str,
        title: &str,
        reference_type: &HighlightReferenceType,
        reference_id: &Option<String>,
    ) -> Result<(), ValidationError> {
        if room_id.is_empty() {
            return Err(ValidationError::Failed("Room ID cannot be empty".to_string()));
        }

        if title.trim().is_empty() {
            return Err(ValidationError::Failed("Title cannot be empty".to_string()));
        }

        if title.len() > Self::MAX_TITLE_LENGTH {
            return Err(ValidationError::Failed(format!(
                "Title too long (maximum {} characters)",
                Self::MAX_TITLE_LENGTH
            )));
        }

        // If reference_type is not Standalone, reference_id must be provided
        if *reference_type != HighlightReferenceType::Standalone && reference_id.is_none() {
            return Err(ValidationError::Failed(
                "Reference ID is required when reference type is not Standalone".to_string(),
            ));
        }

        // If reference_type is Standalone, reference_id should be None
        if *reference_type == HighlightReferenceType::Standalone && reference_id.is_some() {
            return Err(ValidationError::Failed(
                "Reference ID must be empty for Standalone highlights".to_string(),
            ));
        }

        Ok(())
    }
}


