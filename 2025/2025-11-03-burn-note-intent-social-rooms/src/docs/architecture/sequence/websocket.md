# WebSocket Real-time Event Flow

## Context
Real-time updates are delivered via WebSocket connections. Clients connect to the WebSocket endpoint, subscribe to rooms and whispers, and receive events as they occur.

## Sequence: Message Created (Real-time)

```
Client                    Server                    Event Bus
  |                          |                          |
  |-- Connect WebSocket ---->|                          |
  |                          |<-- Authenticate Session  |
  |<-- Connection Established|                          |
  |                          |                          |
  |-- Subscribe to Room ---->|                          |
  |                          |-- Register Subscription->|
  |<-- Subscription Confirmed|                          |
  |                          |                          |
  |                          |                          |
  |                          |                          |
  |-- POST /messages ------->|                          |
  |                          |-- Create Message ------->|
  |                          |                          |
  |                          |-- Publish Event --------->|
  |                          |    (message.created)      |
  |                          |                          |
  |                          |<-- Event Received --------|
  |                          |-- Convert to ServerMsg    |
  |                          |-- Broadcast to Room ----->|
  |                          |                          |
  |<-- message event --------|                          |
  |                          |                          |
  |-- Update UI (add msg)    |                          |
```

## Sequence: Whisper Created (Real-time)

```
Client A                   Server                    Client B
  |                          |                          |
  |-- POST /whispers ------->|                          |
  |                          |-- Create Whisper         |
  |                          |-- Publish whisper.created |
  |                          |                          |
  |<-- whisper_created ------|                          |
  |                          |-- Broadcast to Room ----->|
  |                          |                          |
  |                          |<-- whisper_created -------|
  |                          |                          |
  |-- Update Whisper List    |                          |-- Update Whisper List
```

## Sequence: Whisper Message (Real-time)

```
Client A                   Server                    Client B
  |                          |                          |
  |-- Open Whisper Chat      |                          |
  |-- Subscribe to Whisper -->|                          |
  |                          |                          |
  |                          |                          |
  |-- POST /messages ------->|                          |
  |    (whisper_id)          |-- Create Message         |
  |                          |-- Publish message.created |
  |                          |                          |
  |                          |-- Broadcast to Whisper -->|
  |                          |                          |
  |                          |                          |
  |<-- whisper_message -------|                          |<-- whisper_message -------
  |                          |                          |
  |-- Update Whisper Chat    |                          |-- Update Whisper Chat
```

## Key Components

### Connection Flow
1. Client connects to `GET /v1/ws?session_id={id}`
2. Server authenticates session via `X-Session-Id` header
3. Server creates WebSocket connection and assigns connection ID
4. Connection added to ConnectionManager
5. Client receives connection confirmation

### Subscription Flow
1. Client sends `{ type: "subscribe", payload: { room_id, whisper_id, subscriptions } }`
2. Server registers subscription in ConnectionManager
3. Server sends `{ type: "subscription_confirmed", payload: { ... } }`

### Event Forwarding Flow
1. Handler publishes event to EventBus (e.g., `message.created`)
2. Global event forwarding task receives event
3. Event converted to `ServerMessage` via `convert_event_to_message()`
4. ConnectionManager broadcasts to subscribed connections:
   - If event has `room_id`: broadcast to room subscribers
   - If event has `whisper_id`: broadcast to whisper subscribers
5. Clients receive events and update UI

### Client Auto-reconnect
1. On connection close (not manual), client waits with exponential backoff
2. Reconnects up to 10 times
3. Resubscribes to current room on reconnect
4. Heartbeat ping every 30 seconds to keep connection alive

## Event Types

### Server → Client
- `message` - Room message created
- `whisper_message` - Whisper message created
- `member_joined` - Member joined room
- `member_left` - Member left room
- `whisper_created` - Whisper request created
- `whisper_accepted` - Whisper accepted
- `whisper_declined` - Whisper declined
- `whisper_ended` - Whisper ended
- `post_created` - Post created
- `post_replied` - Reply to post created
- `subscription_confirmed` - Subscription registered
- `error` - Error message
- `pong` - Heartbeat response

### Client → Server
- `subscribe` - Subscribe to room/whisper events
- `unsubscribe` - Unsubscribe from room/whisper events
- `ping` - Heartbeat ping

## Implementation Files

- **Server**: `apps/web/src/handlers/websocket.rs` - WebSocket handler
- **Connection Manager**: `apps/web/src/websocket/connection.rs` - Connection and subscription tracking
- **Events**: `apps/web/src/websocket/events.rs` - Message type definitions and conversion
- **Event Forwarding**: `apps/web/src/main.rs` - Global event forwarding task
- **Client**: `apps/web/static/app.js` - WebSocketClient class

## Notes

- **Session-based Auth**: WebSocket connections authenticated via session ID in query parameter and `X-Session-Id` header
- **Subscription Model**: Clients explicitly subscribe to receive events (filtered at server for efficiency)
- **Auto-cleanup**: Disconnected connections automatically removed from ConnectionManager
- **Event Bus**: Uses in-process pub/sub (`crates/bus`) - events are published from handlers and forwarded to WebSocket clients
- **No Polling**: Real-time updates eliminate need for polling in most cases

