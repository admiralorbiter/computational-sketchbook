# UX — Whispers (MVP)

## Flows
- Ask to Whisper → pending state on recipient
- Accept/Decline → active session or dismissed
- Send messages → expiry countdown visible
- End whisper → confirm and close; optional redact last N messages

## Defaults
- Expiry: 24h (both can extend)
- Media: disabled or small images only (MVP)

## Safety
- Private safety meter shows both have rate-limit headroom
- Block/Mute available; reporting flow mirrors room messages

## Error States
- Recipient offline → show pending; retry sending
- Session expired → prompt to restart


