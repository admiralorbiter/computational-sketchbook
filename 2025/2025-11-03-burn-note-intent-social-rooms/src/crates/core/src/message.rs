use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::error::MessageError;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Message {
    pub id: String,
    pub room_id: String,
    pub sender_mask: String,
    pub message_type: MessageType,
    pub body: String,
    pub media: Option<MediaInfo>,
    pub created_at: DateTime<Utc>,
    pub tombstoned: bool,
    pub whisper_id: Option<String>,
    pub parent_post_id: Option<String>,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum MessageType {
    Text,
    Media,
    Whisper,
    Post,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MediaInfo {
    pub url: String,
    #[serde(rename = "type")]
    pub media_type: String,
    pub size: u64,
}

impl Message {
    pub const MAX_BODY_SIZE: usize = 4 * 1024; // 4 KB

    pub fn new(
        room_id: String,
        sender_mask: String,
        message_type: MessageType,
        body: String,
        whisper_id: Option<String>,
        parent_post_id: Option<String>,
    ) -> Result<Self, MessageError> {
        Self::validate(&room_id, &body)?;
        
        // If parent_post_id is set, message_type must be Post
        if parent_post_id.is_some() && message_type != MessageType::Post {
            return Err(MessageError::InvalidType);
        }
        
        Ok(Self {
            id: Uuid::new_v4().to_string(),
            room_id,
            sender_mask,
            message_type,
            body,
            media: None,
            created_at: Utc::now(),
            tombstoned: false,
            whisper_id,
            parent_post_id,
        })
    }

    pub fn new_with_media(
        room_id: String,
        sender_mask: String,
        body: String,
        media: MediaInfo,
    ) -> Result<Self, MessageError> {
        Self::validate(&room_id, &body)?;
        
        Ok(Self {
            id: Uuid::new_v4().to_string(),
            room_id,
            sender_mask,
            message_type: MessageType::Media,
            body,
            media: Some(media),
            created_at: Utc::now(),
            tombstoned: false,
            whisper_id: None,
            parent_post_id: None,
        })
    }

    pub fn validate(room_id: &str, body: &str) -> Result<(), MessageError> {
        if room_id.is_empty() {
            return Err(MessageError::MissingRoomId);
        }
        
        if body.is_empty() {
            return Err(MessageError::EmptyBody);
        }
        
        if body.len() > Self::MAX_BODY_SIZE {
            return Err(MessageError::BodyTooLarge);
        }
        
        Ok(())
    }

    pub fn tombstone(&mut self) {
        self.tombstoned = true;
    }
}
