use axum::{
    routing::{get, post},
    Router,
    response::{Html, IntoResponse},
    Json,
};
use serde::Serialize;
use std::sync::Arc;
use tokio::net::TcpListener;
use tower_http::services::ServeDir;
use tracing::info;

mod handlers;
mod middleware;
mod websocket;

use handlers::rooms;
use handlers::messages;
use handlers::matching;
use handlers::atlas;
use handlers::sessions;
use handlers::posts;
use handlers::highlights;
use handlers::resources;
use handlers::whispers;
use handlers::members;
use handlers::websocket as ws_handler;
use storage::StorageClient;
use websocket::ConnectionManager;
use axum::extract::FromRef;

#[derive(Clone)]
pub struct AppState {
    pub pool: Arc<sqlx::SqlitePool>,
    pub connection_manager: Arc<ConnectionManager>,
    pub event_bus: Arc<bus::EventBus>,
}

impl FromRef<AppState> for Arc<sqlx::SqlitePool> {
    fn from_ref(state: &AppState) -> Self {
        state.pool.clone()
    }
}

impl FromRef<AppState> for Arc<ConnectionManager> {
    fn from_ref(state: &AppState) -> Self {
        state.connection_manager.clone()
    }
}

impl FromRef<AppState> for Arc<bus::EventBus> {
    fn from_ref(state: &AppState) -> Self {
        state.event_bus.clone()
    }
}

#[derive(Serialize)]
struct Pong { msg: &'static str }

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt::init();

    // Initialize database - use relative path from current working directory
    let db_path = "burn_note.db";
    info!("Database path: {}", db_path);
    let storage = StorageClient::new(db_path).await?;
    storage.init().await?;
    storage.seed_rooms().await?;
    
    let pool = Arc::new(storage.pool().clone());
    info!("Database initialized and seeded");

    // Initialize WebSocket infrastructure
    let connection_manager = Arc::new(ConnectionManager::new());
    let event_bus = Arc::new(bus::EventBus::new(1000)); // 1000 event capacity
    info!("WebSocket infrastructure initialized");

    // Create app state
    let app_state = AppState {
        pool: pool.clone(),
        connection_manager: connection_manager.clone(),
        event_bus: event_bus.clone(),
    };

    // Start global event forwarding task
    let connection_manager_for_events = connection_manager.clone();
    let event_bus_for_events = event_bus.clone();
    tokio::spawn(async move {
        let filter = bus::EventFilter {
            event_types: Some(vec![
                "message.created".to_string(),
                "whisper.created".to_string(),
                "whisper.accepted".to_string(),
                "whisper.declined".to_string(),
                "whisper.ended".to_string(),
                "post.created".to_string(),
                "post.replied".to_string(),
                "member.joined".to_string(),
                "member.left".to_string(),
            ]),
            room_id: None, // Don't filter by room - we'll route based on event.room_id
            whisper_id: None, // Don't filter by whisper - we'll route based on event.whisper_id
        };
        
        let mut event_stream = event_bus_for_events.subscribe(filter);
        
        loop {
            match event_stream.next().await {
                Some(event) => {
                    // Convert event to ServerMessage
                    match websocket::events::convert_event_to_message(&event) {
                        Ok(server_msg) => {
                            // Route to appropriate connections based on event's room_id/whisper_id
                            if let Some(ref event_room_id) = event.room_id {
                                // Broadcast to all connections subscribed to this room
                                connection_manager_for_events.broadcast_to_room(
                                    event_room_id,
                                    &server_msg,
                                ).await;
                            }
                            
                            // If it's a whisper event, also broadcast to whisper subscribers
                            if let Some(ref event_whisper_id) = event.whisper_id {
                                connection_manager_for_events.broadcast_to_whisper(
                                    event_whisper_id,
                                    &server_msg,
                                ).await;
                            }
                        }
                        Err(e) => {
                            tracing::warn!("Failed to convert event to message: {}", e);
                        }
                    }
                }
                None => {
                    // Event stream closed (shouldn't happen in normal operation)
                    tracing::error!("Event stream closed unexpectedly");
                    break;
                }
            }
        }
    });

    // Start background task for session cleanup (runs every 5 minutes)
    let pool_for_cleanup = pool.clone();
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(300)); // 5 minutes
        loop {
            interval.tick().await;
            match storage::SessionRepository::expire_sessions(&pool_for_cleanup).await {
                Ok(count) => {
                    if count > 0 {
                        tracing::info!("Expired {} sessions", count);
                        // Note: We could publish member.left events here, but we'd need to track which sessions expired
                        // For now, we'll only publish member.left when sessions are explicitly deleted
                    }
                }
                Err(e) => {
                    tracing::error!("Failed to expire sessions: {}", e);
                }
            }
        }
    });

    // Start background task for whisper expiry (runs every 5 minutes)
    let pool_for_whisper_cleanup = pool.clone();
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(300)); // 5 minutes
        loop {
            interval.tick().await;
            match storage::WhisperRepository::expire_whispers(&pool_for_whisper_cleanup).await {
                Ok(count) => {
                    if count > 0 {
                        tracing::info!("Expired {} whispers", count);
                    }
                }
                Err(e) => {
                    tracing::error!("Failed to expire whispers: {}", e);
                }
            }
        }
    });

    // build the router and add the route here
    let app = Router::new()
        .route("/", get(root))
        .route("/healthz", get(healthz))
        .route("/api/ping", get(ping))
        .route("/v1/rooms", get(rooms::list_rooms))
        .route("/v1/rooms/:id/join", post(rooms::join_room))
        .route("/v1/messages", get(messages::get_messages).post(messages::create_message))
        .route("/v1/posts", get(posts::get_posts).post(posts::create_post))
        .route("/v1/posts/:post_id/replies", get(posts::get_post_replies))
        .route("/v1/rooms/:room_id/highlights", get(highlights::get_highlights).post(highlights::create_highlight))
        .route("/v1/highlights/:id", axum::routing::delete(highlights::delete_highlight))
        .route("/v1/rooms/:room_id/resources", get(resources::get_resources).post(resources::create_resource))
        .route("/v1/resources/:id", axum::routing::put(resources::update_resource).delete(resources::delete_resource))
        .route("/v1/intent/match", post(matching::match_intent))
        .route("/v1/atlas", get(atlas::get_atlas))
        .route("/v1/whispers", get(whispers::list_whispers).post(whispers::create_whisper))
        .route("/v1/whispers/:id/accept", axum::routing::post(whispers::accept_whisper))
        .route("/v1/whispers/:id/decline", axum::routing::post(whispers::decline_whisper))
        .route("/v1/whispers/:id", axum::routing::delete(whispers::end_whisper))
        .route("/v1/whispers/:id/extend", axum::routing::post(whispers::extend_whisper))
        .route("/v1/rooms/:room_id/members", get(members::get_active_members))
        .route("/v1/ws", axum::routing::get(ws_handler::websocket_handler))
        .route(
            "/v1/sessions/:id",
            axum::routing::delete(sessions::burn_session)
                .route_layer(axum::middleware::from_fn_with_state(
                    app_state.clone(),
                    middleware::session::session_middleware,
                )),
        )
        .nest_service("/static", ServeDir::new("apps/web/static"))
        .with_state(app_state);

    let listener = TcpListener::bind(("127.0.0.1", 8080)).await?;
    info!("listening on http://localhost:8080");
    axum::serve(listener, app).await?;
    
    Ok(())
}

async fn root() -> impl IntoResponse {
    Html(include_str!("../static/index.html"))
}
async fn healthz() -> impl IntoResponse { "ok" }
async fn ping() -> Json<Pong> {
    Json(Pong { msg: "pong" })
}
