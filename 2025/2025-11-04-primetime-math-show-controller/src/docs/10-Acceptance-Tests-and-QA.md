# Acceptance Tests & QA

## Functional
- **Video playback**: MP4 1080p plays/pauses/seeks; end-action respected.
- **Photos ingest**: New photo appears in slideshow within 10s of copy.
- **Math visuals**: Default presets sustain ≥ 60 fps.
- **Text cards**: Legible from back row (font ≥ 64px at 1080p).
- **Countdown**: 10→0 lasts exactly 10s; confetti at 0.

## Operator UX
- Build 20-minute timeline without editing JSON.
- Hotkeys work: Space, ←/→, C, B, F.
- Recovery: refresh show view—state resumes within 2s.

## Performance
- Average FPS ≥ 60; 95th percentile frame time ≤ 18ms.
- Scene swap time ≤ 300ms.

## Negative/Edge
- Missing asset → skip with clear UI warning; app continues.
- Corrupt image/video → logged; not blocking.
