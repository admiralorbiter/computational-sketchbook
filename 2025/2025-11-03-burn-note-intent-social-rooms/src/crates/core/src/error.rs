use thiserror::Error;

#[derive(Debug, Error)]
pub enum RoomError {
    #[error("Room not found")]
    NotFound,
    
    #[error("Room is full")]
    Full,
    
    #[error("Invalid room ID")]
    InvalidId,
}

#[derive(Debug, Error)]
pub enum MessageError {
    #[error("Message body too large (max 4KB)")]
    BodyTooLarge,
    
    #[error("Message body cannot be empty")]
    EmptyBody,
    
    #[error("Invalid message type")]
    InvalidType,
    
    #[error("Message not found")]
    NotFound,
    
    #[error("Room ID is required")]
    MissingRoomId,
}

#[derive(Debug, Error)]
pub enum ValidationError {
    #[error("Validation failed: {0}")]
    Failed(String),
    
    #[error("Invalid ISO 639-1 language code")]
    InvalidLanguage,
    
    #[error("Title cannot be empty")]
    EmptyTitle,
}

#[derive(Debug, Error)]
pub enum SessionError {
    #[error("Session not found")]
    NotFound,
    
    #[error("Session expired")]
    Expired,
    
    #[error("Invalid session mask")]
    InvalidMask,
}

#[derive(Debug, Error)]
pub enum WhisperError {
    #[error("Whisper not found")]
    NotFound,
    
    #[error("Whisper expired")]
    Expired,
    
    #[error("Invalid state: {0}")]
    InvalidState(String),
    
    #[error("Already active whisper exists")]
    AlreadyActive,
    
    #[error("Recipient has blocked sender")]
    Blocked,
}