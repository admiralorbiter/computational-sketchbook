use axum::extract::{
    ws::{Message, WebSocket, WebSocketUpgrade},
    Query, State,
};
use axum::response::Response;
use serde::Deserialize;
use std::sync::Arc;
use sqlx::SqlitePool;
use tokio::sync::mpsc;
use tracing::{debug, error, info, warn};
use futures_util::{StreamExt, SinkExt};

use crate::websocket::{ClientMessage, ConnectionManager, ServerMessage};
use bus::EventBus;
use storage::SessionRepository;

#[derive(Deserialize)]
pub struct WebSocketQuery {
    session_id: Option<String>,
}

/// WebSocket handler - upgrades HTTP connection to WebSocket
pub async fn websocket_handler(
    ws: WebSocketUpgrade,
    Query(params): Query<WebSocketQuery>,
    State(pool): State<Arc<SqlitePool>>,
    State(connection_manager): State<Arc<ConnectionManager>>,
    State(event_bus): State<Arc<EventBus>>,
) -> Response {
    let session_id = params.session_id;

    ws.on_upgrade(move |socket| {
        handle_socket(
            socket,
            session_id,
            pool,
            connection_manager,
            event_bus,
        )
    })
}

/// Handle WebSocket connection lifecycle
async fn handle_socket(
    socket: WebSocket,
    session_id: Option<String>,
    pool: Arc<SqlitePool>,
    connection_manager: Arc<ConnectionManager>,
    _event_bus: Arc<EventBus>,
) {
    // Authenticate session
    let (session_mask, room_id) = match authenticate_session(&pool, &session_id).await {
        Ok(Some((mask, room))) => (mask, room),
        Ok(None) => {
            error!("WebSocket connection rejected: invalid session");
            return;
        }
        Err(e) => {
            error!("WebSocket connection rejected: {}", e);
            return;
        }
    };

    info!("WebSocket connection established for session mask: {}", session_mask);

    // Split socket into sender and receiver
    let (mut sender, mut receiver) = socket.split();

    // Create channel for sending messages to client
    let (tx, mut rx) = mpsc::unbounded_channel::<String>();

    // Create connection and add to manager
    let mut connection = crate::websocket::connection::Connection::new(session_mask.clone(), tx);
    // Subscribe to room if we have room_id from session
    if !room_id.is_empty() {
        connection.subscribe_room(room_id.clone());
    }
    let connection_id = connection.id.clone();
    connection_manager.add_connection(connection).await;
    
    // Subscribe to room in connection manager if we have room_id
    if !room_id.is_empty() {
        if let Err(e) = connection_manager.subscribe_room(&connection_id, room_id).await {
            warn!("Failed to subscribe connection to room: {}", e);
        }
    }

    // Spawn task to forward messages from channel to WebSocket
    let mut send_task = tokio::spawn(async move {
        while let Some(msg) = rx.recv().await {
            if let Err(e) = sender.send(Message::Text(msg)).await {
                warn!("Failed to send WebSocket message: {}", e);
                break;
            }
        }
    });

    // Spawn task to handle incoming messages from client
    let connection_manager_clone = connection_manager.clone();
    let pool_clone = pool.clone();
    let session_mask_clone = session_mask.clone();
    let connection_id_clone = connection_id.clone();

    let mut recv_task = tokio::spawn(async move {
        while let Some(msg) = receiver.next().await {
            match msg {
                Ok(Message::Text(text)) => {
                    if let Err(e) = handle_client_message(
                        &text,
                        &connection_id_clone,
                        &session_mask_clone,
                        &connection_manager_clone,
                        &pool_clone,
                    ).await {
                        error!("Error handling client message: {}", e);
                    }
                }
                Ok(Message::Close(_)) => {
                    debug!("WebSocket closed by client");
                    break;
                }
                Ok(Message::Ping(_data)) => {
                    // Axum handles pong automatically
                    debug!("Received ping");
                }
                Ok(Message::Pong(_)) => {
                    debug!("Received pong");
                }
                Err(e) => {
                    error!("WebSocket error: {}", e);
                    break;
                }
                _ => {}
            }
        }
    });

    // Note: Event forwarding is handled by a global task in main.rs
    // that listens to all events and broadcasts them via connection_manager

    // Wait for either task to complete (connection closed)
    tokio::select! {
        _ = &mut send_task => {
            recv_task.abort();
        }
        _ = &mut recv_task => {
            send_task.abort();
        }
    }

    // Cleanup: remove connection
    connection_manager.remove_connection(&connection_id).await;
    info!("WebSocket connection closed for session mask: {}", session_mask);
}

/// Authenticate WebSocket connection using session
async fn authenticate_session(
    pool: &SqlitePool,
    session_id: &Option<String>,
) -> Result<Option<(String, String)>, Box<dyn std::error::Error>> {
    let session_id = match session_id {
        Some(id) => id,
        None => return Ok(None),
    };

    // Get session from database - we need to query by session_id
    // For WebSocket, we'll validate that session exists and is not expired
    // We'll get the session_mask and room_id from the session
    
    // Note: SessionRepository::get_session takes session_id
    match SessionRepository::get_session(pool, session_id).await {
        Ok(Some(session)) => {
            if session.is_expired() {
                return Ok(None);
            }
            Ok(Some((session.session_mask, session.room_id)))
        }
        Ok(None) => Ok(None),
        Err(e) => {
            error!("Failed to get session: {}", e);
            Err(format!("Failed to get session: {}", e).into())
        }
    }
}

/// Handle incoming client message
async fn handle_client_message(
    text: &str,
    connection_id: &str,
    _session_mask: &str,
    connection_manager: &Arc<ConnectionManager>,
    _pool: &SqlitePool,
) -> Result<(), Box<dyn std::error::Error>> {
    let message: ClientMessage = serde_json::from_str(text)?;
    let connection_id_string = connection_id.to_string();

    match message {
        ClientMessage::Subscribe { payload } => {
            debug!("Subscribe request from connection {}: {:?}", connection_id, payload);

            // Subscribe to room if provided
            if let Some(room_id) = &payload.room_id {
                connection_manager.subscribe_room(&connection_id_string, room_id.clone()).await?;
            }

            // Subscribe to whisper if provided
            if let Some(whisper_id) = &payload.whisper_id {
                connection_manager.subscribe_whisper(&connection_id_string, whisper_id.clone()).await?;
            }

            // Update connection subscriptions
            let subscriptions_clone = payload.subscriptions.clone();
            if let Some(conn) = connection_manager.get_connection(&connection_id_string).await {
                let mut conn = conn.write().await;
                for sub in payload.subscriptions {
                    conn.add_subscription(sub);
                }
            }

            // Send confirmation
            let confirmation = ServerMessage::SubscriptionConfirmed {
                id: uuid::Uuid::new_v4().to_string(),
                timestamp: chrono::Utc::now().to_rfc3339(),
                payload: crate::websocket::events::SubscriptionConfirmedPayload {
                    room_id: payload.room_id.clone(),
                    whisper_id: payload.whisper_id.clone(),
                    subscriptions: subscriptions_clone,
                },
            };

            if let Some(conn) = connection_manager.get_connection(&connection_id_string).await {
                let conn = conn.read().await;
                let _ = conn.send(&confirmation);
            }
        }
        ClientMessage::Unsubscribe { payload } => {
            debug!("Unsubscribe request from connection {}: {:?}", connection_id, payload);

            if payload.room_id.is_some() {
                connection_manager.unsubscribe_room(&connection_id_string).await?;
            }

            if let Some(whisper_id) = &payload.whisper_id {
                connection_manager.unsubscribe_whisper(&connection_id_string, whisper_id).await?;
            }

            // Update connection subscriptions
            if let Some(conn) = connection_manager.get_connection(&connection_id_string).await {
                let mut conn = conn.write().await;
                for sub in payload.subscriptions {
                    conn.remove_subscription(&sub);
                }
            }
        }
        ClientMessage::Ping { payload } => {
            debug!("Ping from connection {}", connection_id);

            // Send pong
            let pong = ServerMessage::Pong {
                id: uuid::Uuid::new_v4().to_string(),
                timestamp: chrono::Utc::now().to_rfc3339(),
                payload: crate::websocket::events::PongPayload {
                    timestamp: payload.timestamp,
                },
            };

            if let Some(conn) = connection_manager.get_connection(&connection_id_string).await {
                let conn = conn.read().await;
                let _ = conn.send(&pong);
            }
        }
    }

    Ok(())
}



