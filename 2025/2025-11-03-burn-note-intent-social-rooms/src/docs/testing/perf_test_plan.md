# Performance Test Plan (MVP)

## Targets
- 100k concurrent members across 2k rooms (design upper bound)
- Join latency P50/P95 as SLOs

## Scenarios
- Fan-out messaging bursts
- Alternating active/idle rooms
- Slow-mode engaged under load

## Tooling
- Load generator simulating join/send/pull (CLI or k6)


