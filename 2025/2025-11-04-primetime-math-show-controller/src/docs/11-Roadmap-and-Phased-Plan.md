# Roadmap & Phased Plan

## Overview
Phase 1 follows a rendering-first approach, starting with math visualizations to establish the core engine, then layering music, text, photos, and video. Each phase is a vertical slice delivering independently testable functionality with UI controls, error handling, and acceptance tests.

## Development Order Rationale
1. **Math Visuals First** - Proves Canvas/WebGL rendering without asset dependencies
2. **Music Next** - Adds audio layer, independent of complex media
3. **Text Cards** - Simple Canvas rendering with animations
4. **Photos** - Introduces asset pipeline incrementally
5. **Video Last** - Most complex, builds on all previous work

## Phase 1A: Lean Foundation

**Goal**: Minimal infrastructure to support real-time rendering and operator control.

### Deliverables
1. **Flask server scaffold** - `/show` and `/operator` routes, static serving
2. **Minimal SQLite schema** - settings table only (defer asset tables)
3. **WebSocket plumbing** - SocketIO namespaces (`/control`, `/show`)
4. **Show View shell** - Canvas element, FPS counter, SocketIO connection
5. **Operator UI shell** - Connection status indicator, simple cue button

### What's Deferred
- Asset watcher and file system monitoring
- Complex database schema (assets, timelines, thumbnails)
- Asset validation and preprocessing
- Timeline editor

### Acceptance Criteria
- Two browser windows connect to server successfully
- FPS counter displays in Show View (even if just empty canvas)
- Operator UI sends ping, Show View responds with pong via WebSocket
- Connection status updates in real-time (connected/disconnected)

---

## Phase 1B: Math Visuals Core (First Vertical Slice) ✅ COMPLETE

**Goal**: First math preset rendering at 60fps with live parameter control.

### Deliverables
1. **Rendering engine choice** ✅ - Canvas 2D API implemented (`static/show/utils/renderer.js`)
2. **Lissajous curves preset** ✅ - Parametric curve rendering with trail effect (`static/show/scenes/Lissajous.js`)
3. **Scene lifecycle** ✅ - Start, render loop, stop, cleanup (`static/show/utils/scene-manager.js`, `MathVisuals.js`)
4. **Operator UI controls** ✅ - "Start Lissajous" button, parameter sliders with debouncing (`static/operator/components/scene-controls.js`)
5. **WebSocket events** ✅ - `SHOW_START_SCENE`, `SHOW_UPDATE_PARAMS`, `SHOW_STOP_SCENE` fully implemented
6. **Performance monitoring** ✅ - FPS calculation and display in operator UI (`static/show/utils/renderer.js`)
7. **Error handling** ✅ - Canvas initialization failures, graceful degradation with user feedback

### Testing
- ✅ Unit test: Lissajous parameter validation (`tests/unit/test_lissajous_params.py`)
- ✅ Integration test: WebSocket event flow (`tests/integration/test_websocket_scene_control.py`)
- ✅ Performance test: FPS monitoring (`tests/integration/test_performance.py`)
- ✅ Manual test checklist: FPS sustains 60fps for 60 seconds (`tests/MANUAL_TEST_CHECKLIST.md`)

### Acceptance Criteria
- ✅ Lissajous curves render smoothly at 60fps (validated via FPS counter)
- ✅ Parameter sliders update visualization in real-time with debouncing
- ⏳ No memory leaks during 5-minute continuous run (requires manual testing)
- ✅ FPS reported to operator UI every second (implemented and tested)

### Implementation Notes
- **Error Handling**: Added comprehensive error handling for canvas initialization failures, context loss, and scene errors
- **Parameter Validation**: Implemented client-side validation with range clamping and fallback to defaults
- **UI Feedback**: Added toast notifications, loading states, and parameter update indicators
- **Performance**: FPS tracking implemented with 60-frame rolling average
- **Testing**: Unit tests for parameter validation, integration tests for WebSocket flow, manual test checklist for performance validation

---

## Phase 1C: Math Visuals Library (Expand Preset Collection) ✅ COMPLETE

**Goal**: Multiple math presets with smooth switching and consistent performance.

### Deliverables
1. **Preset architecture** ✅ - Base class/interface enhanced (`MathVisuals.js`)
2. **Additional presets** ✅ (grouped by complexity):
   - **Simple**: Polar Roses (`PolarRoses.js`), Spirograph (`Spirograph.js`)
   - **Medium**: Digits Rain (`DigitsRain.js`), Ulam Prime Spiral (`UlamSpiral.js`)
   - **Complex**: Conway's Game of Life (`ConwayLife.js`), Mandelbrot Set (`Mandelbrot.js`)
3. **Preset selector UI** ✅ - Grid of preset cards (`preset-selector.js` component)
4. **Scene switching** ✅ - Transitions between presets (`transitions.js`, integrated in `SceneManager`)
5. **Duration control** ✅ - Auto-advance after N seconds (implemented in `SceneManager`)
6. **Theme colors** ✅ - Theme system (`theme.js`) applied to all presets via `MathVisuals` base class
7. **Performance guardrails** ✅ - Automatic complexity reduction when FPS < 55 for 3 seconds

### Testing
- ✅ Unit test: Parameter validation for all presets (`tests/unit/test_math_visuals_params.py`)
- ✅ Integration test: Preset switching functionality (`tests/integration/test_preset_switching.py`)
- ✅ Manual test checklist: Performance and visual validation (`tests/MANUAL_TEST_CHECKLIST_PHASE1C.md`)

### Acceptance Criteria
- ✅ All 7 presets available and working (Lissajous, Polar Roses, Spirograph, Digits Rain, Ulam Spiral, Conway's Life, Mandelbrot)
- ⏳ Each preset sustains minimum 55 fps (requires manual testing)
- ⏳ Switching between presets completes in < 500ms (requires manual testing)
- ✅ Theme colors consistent across all presets (theme system implemented)
- ✅ Operator can trigger any preset on-demand (preset selector UI implemented)
- ✅ Performance guardrails activate when FPS < 55 (implemented with automatic complexity reduction)

### Implementation Notes
- **Theme System**: Centralized theme management with JSON file support, accessible to all scenes
- **Transitions**: Cut, fade, and crossfade transitions implemented with easing functions
- **Duration Control**: Supports finite durations (auto-advance) and infinite (0 = manual stop only)
- **Performance Guardrails**: Monitors FPS every 3 seconds, reduces complexity automatically when FPS < 55
- **Prime Utilities**: Shared prime number generation utilities for Ulam Spiral and Digits Rain
- **Parameter Validation**: All presets have comprehensive parameter validation with range clamping

---

## Phase 1D: Music Playback (Audio Layer)

**Goal**: Background music plays independently of visuals with operator control.

### Deliverables
1. **Web Audio API integration** - AudioContext, buffer loading, playback
2. **Music library** - Scan `/assets/music/` folder, list MP3 files
3. **Playback controls** - Play, pause, stop, loop
4. **Volume control** - Master volume slider (0-100%)
5. **Audio meters** - Visual feedback (peak levels, waveform optional)
6. **Track selection** - Dropdown or list in operator UI
7. **Crossfade** - Smooth transition between tracks (3-5 second fade)
8. **Error handling** - File not found, decode failures, autoplay policy

### Testing
- Unit test: Audio buffer loading and decoding
- Integration test: Volume control accuracy
- Manual test: Music plays for 10+ minutes without glitches

### Acceptance Criteria
- Music plays under math visuals without affecting FPS
- Volume adjustable live (0-100%)
- Crossfade between tracks smooth and seamless
- Audio meters display accurate levels
- Show View reconnection resumes music from correct position

---

## Phase 1E: Text Cards (Simple Scene Type)

**Goal**: Display text overlays with animations on top of visuals.

### Deliverables
1. **Canvas text rendering** - Multi-line text, theme fonts (Bebas Neue, Inter)
2. **Animation presets** - Slide in/out, fade in/out, zoom in/out
3. **Layout options** - Center, lower-third, upper-left
4. **Operator UI** - Text input field, animation picker, layout picker
5. **Live cue** - "Show Text" button for ad-hoc messages
6. **Timing control** - Duration slider or auto-dismiss
7. **Text formatting** - Line breaks, basic styling (bold optional)

### Testing
- Unit test: Text layout calculations
- Integration test: Animation timing accuracy
- Visual test: Text readable on various backgrounds

### Acceptance Criteria
- Text card appears over math visual without stopping rendering
- Animations smooth (fade/slide complete in specified duration)
- Text stays on screen for configured duration
- Live cue works instantly (< 200ms latency)
- Text clears properly without artifacts

---

## Phase 1F: Photo Slideshow (Asset Pipeline Introduction)

**Goal**: Display photos with Ken Burns effect and basic asset management.

### Deliverables
1. **Image loading** - Canvas drawImage, handle EXIF rotation
2. **Ken Burns effect** - Slow zoom and pan with easing
3. **Crossfade transitions** - Blend between photos smoothly
4. **Basic asset indexing** - Scan `/assets/photos/`, list files
5. **Photo bin UI** - Thumbnail grid in operator UI
6. **Asset metadata** - Store file paths, dimensions in memory (no DB yet)
7. **Drag-and-drop** - Add photos to active slideshow
8. **Error handling** - Missing files, corrupted images, unsupported formats

### What's Still Deferred
- Asset watcher (file system monitoring)
- Image preprocessing and scaling
- Thumbnail generation
- Database persistence of assets

### Testing
- Unit test: Image load error handling
- Integration test: Ken Burns timing and smoothness
- Manual test: 50+ photos cycle without memory issues

### Acceptance Criteria
- Photos display with smooth Ken Burns effect
- Crossfade between photos seamless (< 1 second)
- New photo added via UI appears in slideshow within 5 seconds
- No memory leaks over 100+ photo cycle
- Operator can see photo thumbnails and select

---

## Phase 1G: Video Playback (Complex Media Integration)

**Goal**: Play MP4 videos with proper sync and transitions.

### Deliverables
1. **HTML5 video element** - Position off-screen or overlay on canvas
2. **Video validation** - Check codec (H.264/AAC only via ffprobe or browser)
3. **Playback controls** - Play, pause, seek
4. **Video/scene transitions** - Fade in/out, crossfade to other scenes
5. **Video library UI** - List videos from `/assets/videos/`
6. **Sync with timeline** - Video duration drives scene duration
7. **End behavior** - Hold last frame, loop, or advance to next scene
8. **Error handling** - Codec unsupported, file not found, playback stalled

### Testing
- Unit test: Video validation logic
- Integration test: Video start/stop via WebSocket
- Manual test: Video plays without audio/video desync

### Acceptance Criteria
- MP4 H.264 video plays smoothly
- Video transitions to/from other scenes cleanly
- Audio in video plays in sync with visuals
- Operator can see video thumbnails (first frame)
- Video ends gracefully (hold or advance as configured)

---

## Phase 1H: Countdown & Polish (Signature Feature)

**Goal**: Countdown feature and overall theme consistency.

### Deliverables
1. **Countdown scene** - Large numerals counting down (10→0 or custom start)
2. **Timing precision** - Each number displays for exactly 1 second
3. **Sound effects** - Tick sound each second, air horn at zero (optional)
4. **Confetti trigger** - Particle system fires at 0
5. **Live cue button** - Countdown 10/5/3 from operator UI
6. **Theme system** - Load Neon Chalkboard theme JSON, apply colors globally
7. **Transition refinements** - Ensure all scenes transition smoothly
8. **Error UI polish** - Toast notifications for errors, connection status

### Testing
- Unit test: Countdown timing accuracy
- Integration test: Confetti triggers correctly
- Manual test: Theme applied consistently across all scenes

### Acceptance Criteria
- Countdown runs 10→0 in exactly 10.0 seconds
- Confetti fires at zero with visual impact
- Operator can trigger countdown mid-show instantly
- Theme colors consistent across math, text, photos, video
- All transitions feel polished (< 300ms, smooth)

---

## Phase 1I: Timeline & Integration Testing

**Goal**: Build, save, and replay complex multi-scene timelines.

### Deliverables
1. **Timeline editor UI** - Visual track with scene cards
2. **Timeline data structure** - JSON format with scene sequence
3. **Save/load timelines** - Persist to SQLite database
4. **Timeline playback** - Auto-advance through scenes
5. **Transport controls** - Play, pause, next, previous, jump
6. **Inspector panel** - Edit scene parameters (duration, transitions)
7. **Validation** - Warn on missing assets, invalid parameters
8. **20-minute test timeline** - All scene types, realistic show flow
9. **Full test suite** - Pytest unit + integration + E2E tests
10. **Performance benchmarks** - Sustained 60fps for full timeline

### Testing
- E2E test: Build 5-item timeline, save, reload, playback
- Performance test: 20-minute timeline without FPS drops
- Integration test: All WebSocket events in timeline flow

### Acceptance Criteria
- Build timeline with 10+ items via UI
- Save and reload timeline preserves all settings
- Playback advances through scenes automatically
- Timeline runs for 20+ minutes without errors
- All pytest tests pass with 80%+ coverage
- Production ready for first event deployment

---

## Phase 2 — Live Enhancements (Future)

- Beat-aware visual swaps (BPM grid analysis)
- Sponsor ticker and school roll-call animations
- Advanced confetti with physics
- Stream Deck integration and hotkey mapping UI
- Asset watcher and hot-reload

---

## Phase 3 — Advanced Features (Future)

- External scoreboard integration (Google Sheets)
- Face blur and content moderation
- NDI output for OBS/vMix
- DMX/Art-Net lighting bridge
- Highlight auto-export and analytics
- Multi-operator collaboration

---

## Notes on Vertical Slices

Each phase delivers:
- **Core functionality** working end-to-end
- **Operator UI** to control the feature
- **Error handling** and validation
- **Tests** (unit + integration at minimum)
- **Documentation** updates as we go

This approach allows for:
- Early demo-ability (show progress after each phase)
- Risk mitigation (prove hardest parts early)
- Flexibility (reprioritize phases based on feedback)
- Incremental complexity (build on solid foundation)
