# Matching v2: Scalable & Sophisticated

## Problem
With 2,000+ rooms per topic category:
- Keyword matching returns too many similar results
- No way to differentiate "Tech Talk #1" from "Tech Talk #2000"
- Users can't discover the "right" niche within broad topics
- Current MVP keyword approach doesn't scale beyond ~100 rooms

## Proposed Solutions

### 1. Hierarchical Embeddings
- Coarse-grained: "technology" → "programming" → "rust"
- Fine-grained: "rust async" vs "rust game dev" vs "rust embedded"
- Use HNSW (Hierarchical Navigable Small World) for fast ANN search
- Enable sub-topic discovery within broad categories

### 2. Multi-Signal Scoring
Combine multiple signals with weighted importance:
- **Semantic similarity** (embeddings): 40% weight
  - Cosine similarity between intent embedding and room centroid
  - Computed on-device (privacy-preserving) or via edge function
- **Activity recency** (last message timestamp): 20% weight
  - Prefer recently active rooms (decay function: e^(-days/7))
- **Member engagement** (messages per member): 15% weight
  - Higher ratio = more engaged community
  - Prefer rooms with >0.5 messages/member/day
- **Churn rate** (low = healthier): 10% weight
  - Rooms with high join/leave ratio are less stable
- **Personal fit** (privacy-preserving collaborative signal): 15% weight
  - "Users who matched with X also liked Y"
  - Computed via differential privacy to protect individual preferences

### 3. Room Clustering & Auto-Archival
- When 5+ rooms have >0.95 similarity, suggest merge or archive low-activity ones
- Archive rooms with <3 messages in 7 days (auto-archive after 30 days inactive)
- Automatically create "Part 2" rooms when one hits 500 members
- Cluster similar rooms and show "Related rooms" sidebar

### 4. On-Device Matching (Privacy-First)
- Download Room Atlas (compressed embeddings + metadata)
  - Atlas size: ~50KB per 1000 rooms (quantized int8 vectors)
  - Updates hourly via signed diffs
- Compute matching client-side
- Only send `room_id` to server, never raw intent
- Use WebAssembly for fast vector operations
- Client can rank 2000+ rooms in <100ms

### 5. Temporal/Contextual Signals
- "Morning coffee chat" rooms vs "late night deep dives"
  - Time-of-day preferences learned implicitly
- Trending topics (computed via privacy-preserving aggregation)
  - Spike detection: 3x normal message rate = trending
- Event-based rooms (auto-expire after event)
  - Conference rooms, watch parties, etc.

### 6. Intent Refinement
When no good match exists:
- Show "Related intents" based on partial matches
- "Did you mean: rust async programming?" (for "rust async")
- Allow users to refine intent with suggested keywords

## Implementation Phases

### Phase 1 (MVP - Current)
- Keyword matching + room creation
- Basic score thresholds (35% minimum, 60% good match)
- Qualitative match reasons (no technical details)
- Room creation for unique intents

### Phase 2: Add Embeddings
- Migrate to `crates/matching` with strategy pattern
- Implement `EmbeddingMatcher` using sentence-transformers
- Download Room Atlas client-side
- Client-side vector search using WASM
- A/B test: embeddings vs keywords

### Phase 3: Multi-Signal Scoring
- Add activity recency scoring
- Add member engagement scoring
- Combine signals with weighted average
- Tune weights via user feedback

### Phase 4: Collaborative Signals
- Privacy-preserving preference learning
- Differential privacy for "users also liked"
- Client-side collaborative filtering
- No server-side user profiling

### Phase 5: Auto-Clustering and Lifecycle
- Room similarity detection
- Auto-archive inactive rooms
- Auto-create "Part 2" when room full
- Merge suggestions for near-duplicate rooms

## Technical Considerations

### Atlas Compression
- Use int8 quantization (vs float32) → 4x size reduction
- Sparse vectors for rooms with limited metadata
- Delta compression for hourly updates (only changed rooms)

### Performance Targets
- Atlas download: <2s on LTE
- Client-side ranking: <100ms for 2000 rooms
- Server-side room creation: <500ms

### Privacy Guarantees
- Intent never leaves device (except as part of room creation)
- Only room_id sent to server
- Atlas is public (signed, verifiable)
- No user profiling or tracking

## Migration Path

1. **Gradual rollout**: Feature flag to switch between keyword/embedding
2. **Hybrid approach**: Use embeddings for top-K, then refine with keywords
3. **Backward compatibility**: All existing rooms work with new matching
4. **Testing**: A/B test with small user cohort before full rollout

## Future Enhancements

1. **Federated learning**: Room owners can improve matching via feedback
2. **Multi-language**: Cross-language matching for international topics
3. **Visual similarity**: For rooms about art/design, use image embeddings
4. **Voice input**: Speech-to-intent for accessibility
