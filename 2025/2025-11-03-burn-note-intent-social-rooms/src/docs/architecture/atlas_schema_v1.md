# Room Atlas — Schema v1 (Design)

## Purpose
Enable on-device matching via compact, signed data about rooms.

## Fields per Room
- centroid: quantized vector (int8, length 384–768)
- activity: decayed msgs/sec (float32)
- civility: 0–1 score (float32)
- language: ISO 639-1
- freshness: last-active bucket (uint32)
- id: opaque string
- flags: bitset (sensitive, curated, etc.)

## Packaging
- Sharded files (by language or hash)
- Signed manifest with content hashes
- Hourly deltas (binary diff or JSON patch + gzip)

## Integrity
- Manifest signed with server key; client verifies before use


