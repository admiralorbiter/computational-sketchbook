# System Architecture

## High-Level
- **Flask Control Server**: Serves Operator UI + Show View; manages state and communication; WebSocket hub.
- **Show View (Projector)**: Fullscreen browser page at `/show`. Renders scenes with Canvas/WebGL (math visuals primary), then Canvas 2D (text/photos), then `<video>` + WebAudio; listens to SocketIO events.
- **Operator View (Laptop)**: Web UI at `/operator`. Controls live scenes, triggers cues, adjusts parameters, monitors status.
- **Asset Pipeline** *(Phase 1F+)*: File scanning and validation introduced incrementally; starts simple (list files), adds preprocessing later.

## Components

### Backend (Incremental Build)
**Phase 1A (Foundation):**
  - Flask
  - Flask-SocketIO (WebSocket)
  - SQLite (minimal schema: settings only)

**Phase 1D+ (Added Later):**
  - Flask-SQLAlchemy (ORM for SQLite database)
  - Flask-Migrate (database migrations)

**Phase 1F+ (Asset Pipeline):**
  - watchdog (filesystem events) - optional, deferred
  - Pillow (image scale/EXIF)
  - mutagen/ffprobe (media metadata validation)

### Frontend / Renderer (Rendering-First Priority)
**Show View Rendering Order:**
  1. **Canvas 2D API** - Math visuals, text cards, photo slideshow (Phases 1B-1F)
  2. **PixiJS v7 (WebGL)** - Advanced math visuals if needed for performance (Phase 1C)
  3. **Web Audio API** - Music playback (Phase 1D)
  4. **HTML5 `<video>`** - Video playback (Phase 1G)

**Operator UI:**
  - Vanilla JavaScript (ES2020+), Web Components (Custom Elements), CSS Grid/Flexbox
  - Socket.io-client (vanilla JS) for both operator and show view
  - No build tools required for development (Flask serves static files directly)

## Process & Communication
- SocketIO namespaces:
  - `/control` (operator → server)
  - `/show` (server → show view, bidirectional)
- **Early phases**: Server relays operator commands to show view; minimal state tracking
- **Later phases**: Server becomes source of truth for timeline and current index; show view streams back telemetry (fps, scene, timecode)

## Displays
- Dual-window launch: Projector at `/show` in kiosk/fullscreen; Operator UI at `/operator`.

## Folder Structure

```
primetime/
  app.py                    # Flask application entry
  database.py               # SQLite DB operations (minimal initially)
  routes/                   # Flask route handlers
    api.py                  # REST API endpoints (minimal initially)
    operator.py             # Operator UI route
    show.py                 # Show View route
  static/
    show/                   # Show View frontend
      index.html
      show.js               # Main controller
      scenes/               # Scene renderers (build incrementally)
        MathVisuals.js      # Phase 1B: Base math scene class
        Lissajous.js        # Phase 1B: First preset
        PolarRoses.js       # Phase 1C: Additional presets
        Spirograph.js       # Phase 1C
        DigitsRain.js       # Phase 1C
        TextCards.js        # Phase 1E
        PhotoSlideshow.js   # Phase 1F
        VideoScene.js       # Phase 1G
        Countdown.js        # Phase 1H
      utils/
        audio.js            # Phase 1D: Web Audio wrapper
        transitions.js      # Phase 1H: Transition effects
    operator/               # Operator UI frontend
      index.html
      operator.js           # Main controller
      components/           # Web Components (build incrementally)
        status-bar.js       # Phase 1A: Connection status
        preset-selector.js  # Phase 1B-1C: Math presets
        audio-controls.js   # Phase 1D: Music controls
        text-input.js       # Phase 1E: Text card input
        asset-bin.js        # Phase 1F: Photo bin
        timeline-track.js   # Phase 1I: Timeline editor
      styles/
      utils/
    shared/                 # Shared utilities
      api.js
      websocket.js
  assets/                   # Media assets (scanned, not watched initially)
    photos/
    videos/
    music/
    logos/
  themes/                   # Theme JSON files (Phase 1H)
  config/                   # Configuration files
  logs/                     # Application logs
  data/                     # SQLite database
    primetime.db
  tests/                    # Test suite (build incrementally per phase)
    unit/
    integration/
    e2e/
    fixtures/

# Deferred to Later Phases:
  asset_pipeline.py         # Phase 1F+: File watching, preprocessing
  asset_validator.py        # Phase 1G: Media validation logic
  playback.py               # Phase 1I: State machine, timeline management
```
