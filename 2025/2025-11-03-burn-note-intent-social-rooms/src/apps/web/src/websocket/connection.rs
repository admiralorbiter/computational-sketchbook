use crate::websocket::events::ServerMessage;
use serde_json;
use std::collections::{HashMap, HashSet};
use std::sync::Arc;
use tokio::sync::{mpsc, RwLock};
use uuid::Uuid;

pub type ConnectionId = String;

/// Represents a WebSocket connection
pub struct Connection {
    pub id: ConnectionId,
    pub session_mask: String,
    pub room_id: Option<String>,
    pub subscriptions: HashSet<String>,
    pub sender: mpsc::UnboundedSender<String>,
}

impl Connection {
    pub fn new(session_mask: String, sender: mpsc::UnboundedSender<String>) -> Self {
        Self {
            id: Uuid::new_v4().to_string(),
            session_mask,
            room_id: None,
            subscriptions: HashSet::new(),
            sender,
        }
    }

    /// Send a message to this connection
    pub fn send(&self, message: &ServerMessage) -> Result<(), mpsc::error::SendError<String>> {
        match serde_json::to_string(message) {
            Ok(json) => self.sender.send(json),
            Err(e) => {
                tracing::error!("Failed to serialize message: {}", e);
                Err(mpsc::error::SendError("".to_string()))
            }
        }
    }

    /// Subscribe to a room
    pub fn subscribe_room(&mut self, room_id: String) {
        self.room_id = Some(room_id);
    }

    /// Unsubscribe from room
    pub fn unsubscribe_room(&mut self) {
        self.room_id = None;
    }

    /// Add subscription type
    pub fn add_subscription(&mut self, subscription: String) {
        self.subscriptions.insert(subscription);
    }

    /// Remove subscription type
    pub fn remove_subscription(&mut self, subscription: &str) {
        self.subscriptions.remove(subscription);
    }
}

/// Manages WebSocket connections
#[derive(Clone)]
pub struct ConnectionManager {
    connections: Arc<RwLock<HashMap<ConnectionId, Arc<RwLock<Connection>>>>>,
    room_subscriptions: Arc<RwLock<HashMap<String, HashSet<ConnectionId>>>>,
    whisper_subscriptions: Arc<RwLock<HashMap<String, HashSet<ConnectionId>>>>,
}

impl ConnectionManager {
    pub fn new() -> Self {
        Self {
            connections: Arc::new(RwLock::new(HashMap::new())),
            room_subscriptions: Arc::new(RwLock::new(HashMap::new())),
            whisper_subscriptions: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Add a new connection
    pub async fn add_connection(&self, connection: Connection) -> ConnectionId {
        let id = connection.id.clone();
        let connection = Arc::new(RwLock::new(connection));
        
        let mut connections = self.connections.write().await;
        connections.insert(id.clone(), connection);
        
        tracing::debug!("Added connection: {}", id);
        id
    }

    /// Remove a connection and clean up subscriptions
    pub async fn remove_connection(&self, connection_id: &ConnectionId) {
        // Get connection to check room/whisper subscriptions
        let room_id = {
            let connections = self.connections.read().await;
            connections.get(connection_id).and_then(|conn| {
                conn.try_read().ok().and_then(|c| c.room_id.clone())
            })
        };

        // Remove from connections
        {
            let mut connections = self.connections.write().await;
            connections.remove(connection_id);
        }

        // Remove from room subscriptions
        if let Some(room_id) = room_id {
            let mut room_subs = self.room_subscriptions.write().await;
            if let Some(subs) = room_subs.get_mut(&room_id) {
                subs.remove(connection_id);
                if subs.is_empty() {
                    room_subs.remove(&room_id);
                }
            }
        }

        // Remove from whisper subscriptions (check all whispers)
        {
            let mut whisper_subs = self.whisper_subscriptions.write().await;
            whisper_subs.retain(|_whisper_id, subs| {
                subs.remove(connection_id);
                !subs.is_empty()
            });
        }

        tracing::debug!("Removed connection: {}", connection_id);
    }

    /// Subscribe connection to a room
    pub async fn subscribe_room(&self, connection_id: &ConnectionId, room_id: String) -> Result<(), String> {
        // Update connection
        {
            let connections = self.connections.read().await;
            if let Some(conn) = connections.get(connection_id) {
                let mut conn = conn.write().await;
                conn.subscribe_room(room_id.clone());
            } else {
                return Err("Connection not found".to_string());
            }
        }

        // Add to room subscriptions
        {
            let mut room_subs = self.room_subscriptions.write().await;
            room_subs.entry(room_id.clone()).or_insert_with(HashSet::new).insert(connection_id.clone());
        }

        tracing::debug!("Connection {} subscribed to room {}", connection_id, room_id);
        Ok(())
    }

    /// Unsubscribe connection from a room
    pub async fn unsubscribe_room(&self, connection_id: &ConnectionId) -> Result<(), String> {
        let room_id = {
            let connections = self.connections.read().await;
            connections.get(connection_id)
                .and_then(|conn| conn.try_read().ok())
                .and_then(|c| c.room_id.clone())
        };

        if let Some(room_id) = room_id {
            // Update connection
            {
                let connections = self.connections.read().await;
                if let Some(conn) = connections.get(connection_id) {
                    let mut conn = conn.write().await;
                    conn.unsubscribe_room();
                }
            }

            // Remove from room subscriptions
            {
                let mut room_subs = self.room_subscriptions.write().await;
                if let Some(subs) = room_subs.get_mut(&room_id) {
                    subs.remove(connection_id);
                    if subs.is_empty() {
                        room_subs.remove(&room_id);
                    }
                }
            }
        }

        Ok(())
    }

    /// Subscribe connection to a whisper
    pub async fn subscribe_whisper(&self, connection_id: &ConnectionId, whisper_id: String) -> Result<(), String> {
        {
            let mut whisper_subs = self.whisper_subscriptions.write().await;
            whisper_subs.entry(whisper_id.clone()).or_insert_with(HashSet::new).insert(connection_id.clone());
        }

        tracing::debug!("Connection {} subscribed to whisper {}", connection_id, whisper_id);
        Ok(())
    }

    /// Unsubscribe connection from a whisper
    pub async fn unsubscribe_whisper(&self, connection_id: &ConnectionId, whisper_id: &str) -> Result<(), String> {
        {
            let mut whisper_subs = self.whisper_subscriptions.write().await;
            if let Some(subs) = whisper_subs.get_mut(whisper_id) {
                subs.remove(connection_id);
                if subs.is_empty() {
                    whisper_subs.remove(whisper_id);
                }
            }
        }

        Ok(())
    }

    /// Broadcast a message to all connections in a room
    pub async fn broadcast_to_room(&self, room_id: &str, message: &ServerMessage) {
        let connection_ids = {
            let room_subs = self.room_subscriptions.read().await;
            room_subs.get(room_id)
                .map(|subs| subs.iter().cloned().collect::<Vec<_>>())
                .unwrap_or_default()
        };

        let connections = self.connections.read().await;
        for connection_id in connection_ids {
            if let Some(conn) = connections.get(&connection_id) {
                let conn = conn.read().await;
                if let Err(e) = conn.send(message) {
                    tracing::warn!("Failed to send message to connection {}: {}", connection_id, e);
                }
            }
        }
    }

    /// Send a message to specific connections (e.g., whisper participants)
    pub async fn send_to_connections(&self, connection_ids: &[ConnectionId], message: &ServerMessage) {
        let connections = self.connections.read().await;
        for connection_id in connection_ids {
            if let Some(conn) = connections.get(connection_id) {
                let conn = conn.read().await;
                if let Err(e) = conn.send(message) {
                    tracing::warn!("Failed to send message to connection {}: {}", connection_id, e);
                }
            }
        }
    }

    /// Send a message to all connections subscribed to a whisper
    pub async fn broadcast_to_whisper(&self, whisper_id: &str, message: &ServerMessage) {
        let connection_ids = {
            let whisper_subs = self.whisper_subscriptions.read().await;
            whisper_subs.get(whisper_id)
                .map(|subs| subs.iter().cloned().collect::<Vec<_>>())
                .unwrap_or_default()
        };

        self.send_to_connections(&connection_ids, message).await;
    }

    /// Get connection by ID
    pub async fn get_connection(&self, connection_id: &ConnectionId) -> Option<Arc<RwLock<Connection>>> {
        let connections = self.connections.read().await;
        connections.get(connection_id).cloned()
    }

    /// Get all connection IDs for a room
    pub async fn get_room_connections(&self, room_id: &str) -> Vec<ConnectionId> {
        let room_subs = self.room_subscriptions.read().await;
        room_subs.get(room_id)
            .map(|subs| subs.iter().cloned().collect())
            .unwrap_or_default()
    }
}

impl Default for ConnectionManager {
    fn default() -> Self {
        Self::new()
    }
}

