use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::error::WhisperError;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum WhisperState {
    Pending,
    Active,
    Declined,
    Ended,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WhisperSession {
    pub id: String,
    pub sender_mask: String,
    pub recipient_mask: String,
    pub room_id: String,
    pub state: WhisperState,
    pub created_at: DateTime<Utc>,
    pub expires_at: DateTime<Utc>,
    pub last_activity_at: DateTime<Utc>,
}

impl WhisperSession {
    /// Create a new whisper session with default 24h expiry
    pub fn new(
        sender_mask: String,
        recipient_mask: String,
        room_id: String,
    ) -> Result<Self, WhisperError> {
        if sender_mask.trim().is_empty() {
            return Err(WhisperError::InvalidState("Sender mask cannot be empty".to_string()));
        }
        if recipient_mask.trim().is_empty() {
            return Err(WhisperError::InvalidState("Recipient mask cannot be empty".to_string()));
        }
        if sender_mask == recipient_mask {
            return Err(WhisperError::InvalidState("Cannot whisper to yourself".to_string()));
        }
        if room_id.trim().is_empty() {
            return Err(WhisperError::InvalidState("Room ID cannot be empty".to_string()));
        }

        let now = Utc::now();
        Ok(Self {
            id: Uuid::new_v4().to_string(),
            sender_mask,
            recipient_mask,
            room_id,
            state: WhisperState::Pending,
            created_at: now,
            expires_at: now + chrono::Duration::hours(24),
            last_activity_at: now,
        })
    }

    /// Check if the whisper session has expired
    pub fn is_expired(&self) -> bool {
        Utc::now() > self.expires_at
    }

    /// Check if a message can be sent in this whisper
    pub fn can_send_message(&self) -> Result<(), WhisperError> {
        if self.is_expired() {
            return Err(WhisperError::Expired);
        }
        if self.state != WhisperState::Active {
            return Err(WhisperError::InvalidState(
                format!("Cannot send message in {:?} state", self.state)
            ));
        }
        Ok(())
    }

    /// Extend the expiry by N hours
    pub fn extend_expiry(&mut self, hours: i64) -> Result<(), WhisperError> {
        if self.state != WhisperState::Active && self.state != WhisperState::Pending {
            return Err(WhisperError::InvalidState(
                format!("Cannot extend expiry in {:?} state", self.state)
            ));
        }
        if hours <= 0 {
            return Err(WhisperError::InvalidState("Hours must be positive".to_string()));
        }
        self.expires_at = self.expires_at + chrono::Duration::hours(hours);
        Ok(())
    }

    /// Update the last activity timestamp
    pub fn update_activity(&mut self) {
        self.last_activity_at = Utc::now();
    }
}

