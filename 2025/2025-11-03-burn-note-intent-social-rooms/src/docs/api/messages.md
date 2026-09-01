# API — Messages (MVP)

## POST /v1/messages
Create a message (room or whisper).

### Body
- roomId, type, body, whisperId?

### Response
- 201: { id, createdAt }
- Errors: 400/401/413/429/422

## GET /v1/messages
Pull messages for a room.

### Query
- roomId, after (cursor), limit

### Response
- 200: { items: [...], next: cursor? }


