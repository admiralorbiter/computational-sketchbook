use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::error::ValidationError;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Resource {
    pub id: String,
    pub room_id: String,
    pub title: String,
    pub url: String,
    pub description: Option<String>,
    pub category: Option<String>,
    pub curator_mask: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub is_verified: bool,
}

impl Resource {
    pub const MAX_TITLE_LENGTH: usize = 200;
    pub const MAX_DESCRIPTION_LENGTH: usize = 500;
    pub const MAX_CATEGORY_LENGTH: usize = 50;

    pub fn new(
        room_id: String,
        title: String,
        url: String,
        description: Option<String>,
        category: Option<String>,
        curator_mask: String,
    ) -> Result<Self, ValidationError> {
        Self::validate(&room_id, &title, &url, &description, &category)?;

        Ok(Self {
            id: Uuid::new_v4().to_string(),
            room_id,
            title,
            url,
            description,
            category,
            curator_mask,
            created_at: Utc::now(),
            updated_at: Utc::now(),
            is_verified: false,
        })
    }

    pub fn new_verified(
        room_id: String,
        title: String,
        url: String,
        description: Option<String>,
        category: Option<String>,
    ) -> Result<Self, ValidationError> {
        Self::validate(&room_id, &title, &url, &description, &category)?;

        Ok(Self {
            id: Uuid::new_v4().to_string(),
            room_id,
            title,
            url,
            description,
            category,
            curator_mask: "system".to_string(),
            created_at: Utc::now(),
            updated_at: Utc::now(),
            is_verified: true,
        })
    }

    pub fn update(
        &mut self,
        title: Option<String>,
        url: Option<String>,
        description: Option<String>,
        category: Option<String>,
    ) -> Result<(), ValidationError> {
        let new_title = title.as_ref().unwrap_or(&self.title);
        let new_url = url.as_ref().unwrap_or(&self.url);
        let new_description = description.as_ref().or(self.description.as_ref());
        let new_category = category.as_ref().or(self.category.as_ref());

        Self::validate(&self.room_id, new_title, new_url, &new_description.cloned(), &new_category.cloned())?;

        if let Some(t) = title {
            self.title = t;
        }
        if let Some(u) = url {
            self.url = u;
        }
        if let Some(d) = description {
            self.description = Some(d);
        } else if description.is_some() {
            // Explicitly set to None
            self.description = None;
        }
        if let Some(c) = category {
            self.category = Some(c);
        } else if category.is_some() {
            // Explicitly set to None
            self.category = None;
        }

        self.updated_at = Utc::now();
        Ok(())
    }

    pub fn validate(
        room_id: &str,
        title: &str,
        url: &str,
        description: &Option<String>,
        category: &Option<String>,
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

        // Validate URL format
        if !url.starts_with("http://") && !url.starts_with("https://") {
            return Err(ValidationError::Failed(
                "URL must start with http:// or https://".to_string(),
            ));
        }

        // Basic URL validation - check for at least a domain
        if url.len() < 10 {
            return Err(ValidationError::Failed("URL is too short".to_string()));
        }

        // Check for basic URL structure (at least protocol://domain)
        let url_parts: Vec<&str> = url.split("://").collect();
        if url_parts.len() != 2 || url_parts[1].is_empty() {
            return Err(ValidationError::Failed("Invalid URL format".to_string()));
        }

        if let Some(ref desc) = description {
            if desc.len() > Self::MAX_DESCRIPTION_LENGTH {
                return Err(ValidationError::Failed(format!(
                    "Description too long (maximum {} characters)",
                    Self::MAX_DESCRIPTION_LENGTH
                )));
            }
        }

        if let Some(ref cat) = category {
            if cat.trim().is_empty() {
                return Err(ValidationError::Failed(
                    "Category cannot be empty if provided".to_string(),
                ));
            }
            if cat.len() > Self::MAX_CATEGORY_LENGTH {
                return Err(ValidationError::Failed(format!(
                    "Category too long (maximum {} characters)",
                    Self::MAX_CATEGORY_LENGTH
                )));
            }
        }

        Ok(())
    }
}

