use serde::{Deserialize, Serialize};
use anyhow;

/// Client → Server message types
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum ClientMessage {
    #[serde(rename = "subscribe")]
    Subscribe {
        payload: SubscribePayload,
    },
    #[serde(rename = "unsubscribe")]
    Unsubscribe {
        payload: UnsubscribePayload,
    },
    #[serde(rename = "ping")]
    Ping {
        payload: PingPayload,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SubscribePayload {
    pub room_id: Option<String>,
    pub whisper_id: Option<String>,
    pub subscriptions: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UnsubscribePayload {
    pub room_id: Option<String>,
    pub whisper_id: Option<String>,
    pub subscriptions: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PingPayload {
    pub timestamp: String,
}

/// Server → Client message types
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum ServerMessage {
    #[serde(rename = "message")]
    Message {
        id: String,
        timestamp: String,
        payload: MessagePayload,
    },
    #[serde(rename = "whisper_message")]
    WhisperMessage {
        id: String,
        timestamp: String,
        payload: WhisperMessagePayload,
    },
    #[serde(rename = "member_joined")]
    MemberJoined {
        id: String,
        timestamp: String,
        payload: MemberJoinedPayload,
    },
    #[serde(rename = "member_left")]
    MemberLeft {
        id: String,
        timestamp: String,
        payload: MemberLeftPayload,
    },
    #[serde(rename = "whisper_created")]
    WhisperCreated {
        id: String,
        timestamp: String,
        payload: WhisperCreatedPayload,
    },
    #[serde(rename = "whisper_accepted")]
    WhisperAccepted {
        id: String,
        timestamp: String,
        payload: WhisperAcceptedPayload,
    },
    #[serde(rename = "whisper_declined")]
    WhisperDeclined {
        id: String,
        timestamp: String,
        payload: WhisperDeclinedPayload,
    },
    #[serde(rename = "whisper_ended")]
    WhisperEnded {
        id: String,
        timestamp: String,
        payload: WhisperEndedPayload,
    },
    #[serde(rename = "post_created")]
    PostCreated {
        id: String,
        timestamp: String,
        payload: PostCreatedPayload,
    },
    #[serde(rename = "post_replied")]
    PostReplied {
        id: String,
        timestamp: String,
        payload: PostRepliedPayload,
    },
    #[serde(rename = "subscription_confirmed")]
    SubscriptionConfirmed {
        id: String,
        timestamp: String,
        payload: SubscriptionConfirmedPayload,
    },
    #[serde(rename = "pong")]
    Pong {
        id: String,
        timestamp: String,
        payload: PongPayload,
    },
    #[serde(rename = "error")]
    Error {
        id: String,
        timestamp: String,
        payload: ErrorPayload,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MessagePayload {
    pub id: String,
    pub room_id: String,
    pub sender_mask: String,
    #[serde(rename = "type")]
    pub message_type: String,
    pub body: String,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WhisperMessagePayload {
    pub id: String,
    pub whisper_id: String,
    pub sender_mask: String,
    pub body: String,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemberJoinedPayload {
    pub room_id: String,
    pub mask: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemberLeftPayload {
    pub room_id: String,
    pub mask: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WhisperCreatedPayload {
    pub whisper: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WhisperAcceptedPayload {
    pub whisper: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WhisperDeclinedPayload {
    pub whisper_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WhisperEndedPayload {
    pub whisper_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PostCreatedPayload {
    pub post: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PostRepliedPayload {
    pub reply: serde_json::Value,
    pub parent_post_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SubscriptionConfirmedPayload {
    pub room_id: Option<String>,
    pub whisper_id: Option<String>,
    pub subscriptions: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PongPayload {
    pub timestamp: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ErrorPayload {
    pub code: String,
    pub message: String,
}

/// Convert bus::Event to ServerMessage
pub fn convert_event_to_message(event: &bus::Event) -> anyhow::Result<ServerMessage> {
    use uuid::Uuid;
    use chrono::Utc;
    
    let id = Uuid::new_v4().to_string();
    let timestamp = Utc::now().to_rfc3339();
    
    match event.event_type.as_str() {
        "message.created" => {
            let message: core::Message = serde_json::from_value(event.payload.clone())?;
            let message_type_str = serde_json::to_string(&message.message_type)?
                .trim_matches('"')
                .to_string();
            
            if message.message_type == core::MessageType::Whisper {
                // Whisper message
                Ok(ServerMessage::WhisperMessage {
                    id,
                    timestamp,
                    payload: WhisperMessagePayload {
                        id: message.id,
                        whisper_id: message.whisper_id.clone().unwrap_or_default(),
                        sender_mask: message.sender_mask,
                        body: message.body,
                        created_at: message.created_at.to_rfc3339(),
                    },
                })
            } else {
                // Regular room message
                Ok(ServerMessage::Message {
                    id,
                    timestamp,
                    payload: MessagePayload {
                        id: message.id,
                        room_id: message.room_id,
                        sender_mask: message.sender_mask,
                        message_type: message_type_str,
                        body: message.body,
                        created_at: message.created_at.to_rfc3339(),
                    },
                })
            }
        }
        "whisper.created" => {
            Ok(ServerMessage::WhisperCreated {
                id,
                timestamp,
                payload: WhisperCreatedPayload {
                    whisper: event.payload.clone(),
                },
            })
        }
        "whisper.accepted" => {
            Ok(ServerMessage::WhisperAccepted {
                id,
                timestamp,
                payload: WhisperAcceptedPayload {
                    whisper: event.payload.clone(),
                },
            })
        }
        "whisper.declined" => {
            let whisper_id = event.payload.get("id")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            Ok(ServerMessage::WhisperDeclined {
                id,
                timestamp,
                payload: WhisperDeclinedPayload {
                    whisper_id,
                },
            })
        }
        "whisper.ended" => {
            let whisper_id = event.payload.get("id")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            Ok(ServerMessage::WhisperEnded {
                id,
                timestamp,
                payload: WhisperEndedPayload {
                    whisper_id,
                },
            })
        }
        "post.created" => {
            Ok(ServerMessage::PostCreated {
                id,
                timestamp,
                payload: PostCreatedPayload {
                    post: event.payload.clone(),
                },
            })
        }
        "post.replied" => {
            let parent_post_id = event.payload.get("parent_post_id")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            Ok(ServerMessage::PostReplied {
                id,
                timestamp,
                payload: PostRepliedPayload {
                    reply: event.payload.clone(),
                    parent_post_id,
                },
            })
        }
        "member.joined" => {
            let room_id = event.room_id.clone().unwrap_or_default();
            let mask = event.payload.get("mask")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            Ok(ServerMessage::MemberJoined {
                id,
                timestamp,
                payload: MemberJoinedPayload {
                    room_id,
                    mask,
                },
            })
        }
        "member.left" => {
            let room_id = event.room_id.clone().unwrap_or_default();
            let mask = event.payload.get("mask")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            Ok(ServerMessage::MemberLeft {
                id,
                timestamp,
                payload: MemberLeftPayload {
                    room_id,
                    mask,
                },
            })
        }
        _ => {
            tracing::warn!("Unknown event type: {}", event.event_type);
            Err(anyhow::anyhow!("Unknown event type: {}", event.event_type))
        }
    }
}

