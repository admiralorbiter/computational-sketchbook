# API — Whispers (MVP)

## GET /v1/whispers
List whispers for a user.

### Query Parameters
- `mask` (required): Session mask of the user
- `room_id` (optional): Filter whispers by room ID

### Response
- 200: `{ items: WhisperResponse[] }`

### WhisperResponse
```json
{
  "id": "string",
  "sender_mask": "string",
  "recipient_mask": "string",
  "room_id": "string",
  "state": "pending" | "active" | "declined" | "ended",
  "created_at": "RFC3339 timestamp",
  "expires_at": "RFC3339 timestamp",
  "last_activity_at": "RFC3339 timestamp"
}
```

## POST /v1/whispers
Create a whisper request.

### Body
```json
{
  "sender_mask": "string",
  "recipient_mask": "string",
  "room_id": "string"
}
```

### Response
- 201: `WhisperResponse` (full whisper object with state "pending")

### Errors
- 400: Validation error (empty masks, same sender/recipient, etc.)
- 400: Sender doesn't have active session
- 400: Recipient not found in room (no messages or active session)
- 409: Already active whisper exists between participants

## POST /v1/whispers/:id/accept
Accept a whisper request.

### Response
- 200: `WhisperResponse` (full whisper object with state "active")

### Errors
- 404: Whisper not found
- 410: Whisper has expired
- 400: Cannot accept whisper in current state (not pending)

## POST /v1/whispers/:id/decline
Decline a whisper request.

### Response
- 200: `WhisperResponse` (full whisper object with state "declined")

### Errors
- 404: Whisper not found
- 400: Cannot decline whisper in current state

## DELETE /v1/whispers/:id
End a whisper session.

### Response
- 204: No content (success)

### Errors
- 404: Whisper not found
- 400: Cannot end whisper in current state (already ended or declined)

## POST /v1/whispers/:id/extend
Extend a whisper's expiry time.

### Body
```json
{
  "hours": 24  // optional, defaults to 24
}
```

### Response
- 200: `WhisperResponse` (updated whisper object)

### Errors
- 404: Whisper not found
- 400: Cannot extend whisper in current state (must be pending or active)
- 400: Extension hours must be positive

## Notes
- Whispers expire after 24 hours by default (can be extended)
- Whisper messages are sent via `POST /v1/messages` with `type: "whisper"` and `whisper_id`
- Only one active whisper can exist between two participants in a room
- Background task expires whispers every 5 minutes


