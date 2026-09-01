# Matching v1 — Scoring & Diversification (Design)

## Embedding & Candidates
- Local embed intent (384–768d); normalize text; strip PII (design)
- Top-K by cosine similarity against Atlas centroids

## Score Function
- score = α·cosine + β·activity + γ·civility + δ·freshness − dupPenalty
- Start: α=0.6, β=0.2, γ=0.15, δ=0.05; tune via eval

## Diversification (MMR)
- Select top room, then iteratively choose next maximizing relevance − λ·similarityToSelected
- λ ~ 0.3 for alternates panel

## Safety Gating
- If sensitive intent (local heuristic), require rooms with vetted resources & higher civility

## Evaluation
- Offline: labeled pairs from seed dataset
- Online (internal): thumbs + dwell (aggregated)


