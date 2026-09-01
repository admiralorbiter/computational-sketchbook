# Logging Policy (MVP)

## Principles
- Minimize; never log message bodies or intents
- Use structured logs; redact sensitive fields

## Levels
- info: request/response summaries
- warn: user-visible errors
- error: server failures with correlation ids

## Retention
- ≤ 7 days in dev/internal; rotation enabled


