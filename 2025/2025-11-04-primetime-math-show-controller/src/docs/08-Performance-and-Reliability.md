# Performance & Reliability

## Targets
- 1080p @ 60 fps in Show View.
- Scene switch ≤ 300 ms perceived latency (preload next).

## Techniques
- Pre-scale images to protect VRAM.
- Mipmaps / texture atlases for text and icons.
- Lazy-load video elements; call `play()` early muted to warm decoder.
- Use a single monotonic clock; step animations off `requestAnimationFrame` delta.
- Backoff logic: if FPS < 55 for 2s, reduce particle count / visual density.

## Reliability
- Server is source of truth; show view may reconnect and resume last state.
- Atomic writes for timeline/config; rolling logs.
- Graceful failure: if a scene fails to load, skip and toast the operator.
