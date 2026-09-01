# Evaluation Plan — Matching v1

## Offline
- Curate ~500 intents with target rooms (seeded by team)
- Metrics: Recall@1/3, NDCG@3, unsafe-room rate

## Internal Online (MVP)
- Collect thumbs (good fit) and alternates pick rate (aggregated)
- Compare weight variants A/B; guardrail unsafe-room rate

## Success Criteria
- Recall@1 ≥ 0.6; unsafe-room rate ≤ 2%
- Internal thumbs ≥ 60% good fit


