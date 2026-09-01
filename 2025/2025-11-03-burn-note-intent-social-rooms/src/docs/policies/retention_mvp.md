# Retention Policy — MVP

## Content
- Room messages: default 30 days (configurable up to 90 days)
- Whispers: default 24h expiry
- Highlights: until room is archived or curator removes

## Logs
- Application logs: ≤ 7 days, no message bodies

## Deletion
- Tombstone on delete; redact body for UI; retain minimal audit for abuse investigations (internal only)


