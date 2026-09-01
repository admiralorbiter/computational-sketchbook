//! core: domain types & logic

pub mod error;
pub mod highlight;
pub mod message;
pub mod resource;
pub mod room;
pub mod session;
pub mod whisper;

pub use error::{MessageError, RoomError, SessionError, ValidationError, WhisperError};
pub use highlight::{Highlight, HighlightReferenceType};
pub use message::{MediaInfo, Message, MessageType};
pub use resource::Resource;
pub use room::{PolicyFlags, Room};
pub use session::{SessionMask, UserSession};
pub use whisper::{WhisperSession, WhisperState};