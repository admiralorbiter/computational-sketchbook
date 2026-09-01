//! bus: in-process pub/sub for event distribution

use serde::{Deserialize, Serialize};
use tokio::sync::broadcast;

/// Event that can be published and subscribed to
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Event {
    pub event_type: String,
    pub room_id: Option<String>,
    pub whisper_id: Option<String>,
    pub payload: serde_json::Value,
}

/// Filter for subscribing to events
#[derive(Debug, Clone)]
pub struct EventFilter {
    pub event_types: Option<Vec<String>>,
    pub room_id: Option<String>,
    pub whisper_id: Option<String>,
}

impl EventFilter {
    pub fn matches(&self, event: &Event) -> bool {
        // Check event type filter
        if let Some(ref event_types) = self.event_types {
            if !event_types.contains(&event.event_type) {
                return false;
            }
        }

        // Check room_id filter
        if let Some(ref filter_room_id) = self.room_id {
            if event.room_id.as_ref() != Some(filter_room_id) {
                return false;
            }
        }

        // Check whisper_id filter
        if let Some(ref filter_whisper_id) = self.whisper_id {
            if event.whisper_id.as_ref() != Some(filter_whisper_id) {
                return false;
            }
        }

        true
    }
}

/// Event bus for pub/sub event distribution
#[derive(Clone)]
pub struct EventBus {
    sender: broadcast::Sender<Event>,
}

impl EventBus {
    /// Create a new event bus with the specified channel capacity
    pub fn new(capacity: usize) -> Self {
        let (sender, _) = broadcast::channel(capacity);
        Self { sender }
    }

    /// Publish an event to all subscribers
    pub fn publish(&self, event: Event) {
        let _ = self.sender.send(event);
    }

    /// Subscribe to events matching the filter
    pub fn subscribe(&self, filter: EventFilter) -> EventStream {
        EventStream {
            receiver: self.sender.subscribe(),
            filter,
        }
    }

    /// Get the number of active subscribers
    pub fn subscriber_count(&self) -> usize {
        self.sender.receiver_count()
    }
}

/// Stream of events matching a filter
pub struct EventStream {
    receiver: broadcast::Receiver<Event>,
    filter: EventFilter,
}

impl EventStream {
    /// Get the next event matching the filter
    pub async fn next(&mut self) -> Option<Event> {
        loop {
            match self.receiver.recv().await {
                Ok(event) => {
                    if self.filter.matches(&event) {
                        return Some(event);
                    }
                    // Continue loop to find matching event
                }
                Err(broadcast::error::RecvError::Closed) => {
                    // Channel closed, return None
                    return None;
                }
                Err(broadcast::error::RecvError::Lagged(_)) => {
                    // Lagged, skip and continue
                    continue;
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_event_bus_pub_sub() {
        let bus = EventBus::new(100);
        
        let filter = EventFilter {
            event_types: Some(vec!["test".to_string()]),
            room_id: None,
            whisper_id: None,
        };
        
        let mut stream = bus.subscribe(filter);
        
        let event = Event {
            event_type: "test".to_string(),
            room_id: None,
            whisper_id: None,
            payload: serde_json::json!({"test": "data"}),
        };
        
        bus.publish(event.clone());
        
        let received = stream.next().await;
        assert!(received.is_some());
        assert_eq!(received.unwrap().event_type, "test");
    }

    #[tokio::test]
    async fn test_event_filter() {
        let bus = EventBus::new(100);
        
        let filter = EventFilter {
            event_types: Some(vec!["message.created".to_string()]),
            room_id: Some("room1".to_string()),
            whisper_id: None,
        };
        
        let mut stream = bus.subscribe(filter);
        
        // Publish event that matches
        bus.publish(Event {
            event_type: "message.created".to_string(),
            room_id: Some("room1".to_string()),
            whisper_id: None,
            payload: serde_json::json!({}),
        });
        
        // Publish event that doesn't match (wrong room)
        bus.publish(Event {
            event_type: "message.created".to_string(),
            room_id: Some("room2".to_string()),
            whisper_id: None,
            payload: serde_json::json!({}),
        });
        
        let received = stream.next().await;
        assert!(received.is_some());
        assert_eq!(received.unwrap().room_id, Some("room1".to_string()));
    }
}