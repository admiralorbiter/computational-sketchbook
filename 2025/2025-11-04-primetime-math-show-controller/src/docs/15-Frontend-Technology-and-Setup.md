# Frontend Technology & Setup

## Overview
PrimeTime uses vanilla JavaScript with Web Components for the Operator UI and Canvas/WebGL for the Show View. No build tools required for development—Flask serves static files directly.

## Technology Stack

### Show View (Projector Display)

**Core Technologies (Build Order):**

**Phase 1B-1C: Math Visuals Foundation**
- **Canvas 2D API** - Primary renderer for math visuals (start here, simplest)
- **PixiJS v7** (optional) - WebGL renderer if Canvas 2D performance insufficient for complex presets
- **Vanilla JavaScript (ES2020+)** - No frameworks, direct DOM/Canvas access

**Phase 1D: Audio Layer**
- **Web Audio API** - Music playback, volume control, audio meters

**Phase 1E: Text Rendering**
- **Canvas 2D API** - Text cards with animations (already loaded)

**Phase 1F: Image Rendering**
- **Canvas 2D API** - Photo slideshow, Ken Burns effects (already loaded)

**Phase 1G: Video Integration**
- **Native HTML5 `<video>`** - Video playback (better performance than Canvas video)

**Why Start with Canvas 2D API:**
- No external dependencies, built into browser
- Sufficient performance for most math visuals
- Simpler API than WebGL
- Faster to prototype and iterate
- Can always upgrade to PixiJS/WebGL for specific presets if needed

**Why PixiJS (if needed for Phase 1C):**
- Mature WebGL abstraction, excellent performance for complex visuals
- Built-in sprite batching, texture caching
- Shader support for custom math visuals (Mandelbrot, Platonic Solids)
- Active maintenance, good documentation

**File Structure (Build Incrementally):**
```
static/
  show/
    index.html          # Fullscreen Show View page
    show.js             # Main Show View controller
    scenes/
      # Phase 1B: Start here
      MathVisuals.js    # Base class for math presets
      Lissajous.js      # First preset (Phase 1B)
      
      # Phase 1C: Add more math presets
      PolarRoses.js
      Spirograph.js
      DigitsRain.js
      UlamSpiral.js
      ConwayLife.js
      Mandelbrot.js
      # ... more presets
      
      # Phase 1E: Text rendering
      TextCards.js      # Text card scene
      
      # Phase 1F: Image rendering
      PhotoSlideshow.js # Photo slideshow scene
      
      # Phase 1G: Video playback
      VideoScene.js     # Video playback scene
      
      # Phase 1H: Polish
      Countdown.js      # Countdown scene
      
    utils/
      # Phase 1D: Audio
      audio.js          # Web Audio API wrapper
      
      # Phase 1H: Transitions
      transitions.js    # Fade/cross/cut transition functions
```

### Operator UI (Control Interface)

**Core Technologies:**
- **Vanilla JavaScript (ES2020+)** - Modern JS features (classes, async/await, modules)
- **Web Components (Custom Elements)** - Reusable UI components
- **CSS Grid & Flexbox** - Layout (no CSS framework required)
- **Socket.io-client** - WebSocket communication
- **Native Drag & Drop API** - Timeline item reordering

**Why Web Components:**
- Native browser standard, no framework overhead
- Encapsulation with Shadow DOM (optional, for complex components)
- Works seamlessly with vanilla JS
- No build step required

**Example Component Structure:**
```javascript
// static/operator/components/asset-bin.js
class AssetBin extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <div class="asset-bin">
                <h3>${this.getAttribute('title')}</h3>
                <div class="asset-grid"></div>
            </div>
        `;
        this.loadAssets();
    }
    
    async loadAssets() {
        // Fetch assets from API, render thumbnails
    }
}

customElements.define('asset-bin', AssetBin);
```

**File Structure:**
```
static/
  operator/
    index.html              # Operator UI page
    operator.js             # Main Operator UI controller
    components/
      asset-bin.js          # Asset thumbnail grid
      timeline-track.js     # Timeline item cards
      inspector-panel.js    # Scene parameter editor
      transport-controls.js # Play/pause/skip buttons
      status-bar.js         # FPS, timecode, connection status
    styles/
      main.css              # Global styles
      components.css        # Component styles
    utils/
      websocket.js          # Socket.io wrapper
      drag-drop.js          # Drag & drop helpers
      toast.js              # Toast notification system
```

### Shared Utilities

```
static/
  shared/
    api.js                  # REST API client functions
    timeline-validator.js   # Timeline JSON validation
    timecode-formatter.js   # Format timecode (MM:SS)
```

## Development Setup

### No Build Tools Required

**Development Mode:**
- Flask serves static files via `app.static_folder`
- ES6 modules work natively in modern browsers
- Use `type="module"` in script tags
- Browser refresh on file save (Flask debug mode)

**HTML Example:**
```html
<!-- static/show/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>PrimeTime Show View</title>
    <style>/* CSS here or link external */</style>
</head>
<body>
    <canvas id="show-canvas"></canvas>
    <video id="show-video" style="display: none;"></video>
    
    <script type="module" src="/static/show/show.js"></script>
</body>
</html>
```

**JavaScript Module:**
```javascript
// static/show/show.js
import { VideoScene } from './scenes/VideoScene.js';
import { socket } from './utils/websocket.js';

class ShowView {
    constructor() {
        this.canvas = document.getElementById('show-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.setupWebSocket();
    }
    // ...
}
```

### Flask Static File Serving

```python
# app.py
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/show')
def show_view():
    return send_from_directory('static/show', 'index.html')

@app.route('/operator')
def operator_ui():
    return send_from_directory('static/operator', 'index.html')

# Static files automatically served from /static/*
```

### Optional Production Build

**If minification desired:**
- Use `esbuild` in simple mode: `esbuild static/**/*.js --outdir=static/dist --minify`
- Only needed for production deployment
- Development can use unminified source

**esbuild command:**
```bash
# package.json scripts (optional)
{
  "scripts": {
    "build": "esbuild static/**/*.js --outdir=static/dist --minify --bundle --format=esm"
  }
}
```

## WebSocket Communication

### Socket.io Client Setup

**Operator UI:**
```javascript
// static/operator/utils/websocket.js
import { io } from 'https://cdn.socket.io/4.5.4/socket.io.esm.min.js';

export const socket = io('/control', {
    autoConnect: true,
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000
});

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('disconnect', () => {
    console.log('Disconnected');
});
```

**Show View:**
```javascript
// static/show/utils/websocket.js
export const socket = io('/show', {
    autoConnect: true,
    reconnection: true
});

socket.on('SHOW_LOAD_TIMELINE', (data) => {
    // Load timeline and start playback
});

socket.on('SHOW_PLAY', (data) => {
    // Start/resume playback
});
```

**CDN Usage:**
- Use Socket.io from CDN (no npm required)
- Or include `socket.io-client` via `<script>` tag if preferred

## CSS Approach

### Minimal CSS Framework (Optional)

**Option 1: Pure CSS**
- Custom CSS Grid/Flexbox layouts
- CSS variables for theme colors
- Utility classes as needed (`.flex`, `.grid`, `.hidden`)

**Option 2: Tailwind CDN (Optional)**
- Use Tailwind Play CDN for rapid prototyping
- Not recommended for production (large file size)
- Better to write custom CSS for final version

**CSS Variables for Theme:**
```css
:root {
    --bg-color: #0f1115;
    --fg-color: #F4F4F4;
    --accent-green: #39FF14;
    --accent-cyan: #00E5FF;
    --font-heading: 'Bebas Neue', sans-serif;
    --font-body: 'Inter', sans-serif;
}

body {
    background: var(--bg-color);
    color: var(--fg-color);
    font-family: var(--font-body);
}
```

## Audio Implementation

### Web Audio API

**Music Playback:**
```javascript
// static/show/utils/audio.js
export class AudioPlayer {
    constructor() {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.source = null;
        this.gainNode = this.audioContext.createGain();
        this.gainNode.connect(this.audioContext.destination);
    }
    
    async loadAudio(url) {
        const response = await fetch(url);
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
        return audioBuffer;
    }
    
    play(buffer, volume = 1.0, loop = false) {
        if (this.source) this.source.stop();
        this.source = this.audioContext.createBufferSource();
        this.source.buffer = buffer;
        this.source.loop = loop;
        this.source.connect(this.gainNode);
        this.gainNode.gain.value = volume;
        this.source.start();
    }
    
    setVolume(volume) {
        this.gainNode.gain.value = volume;
    }
}
```

**Audio Meter (Visual Feedback):**
- Use `AnalyserNode` to get frequency data
- Draw bar chart in Operator UI canvas
- Update every frame via `requestAnimationFrame`

## Performance Considerations

### Show View Optimization (By Phase)

**Phase 1B-1C (Math Visuals):**
1. **RequestAnimationFrame**: Use single RAF loop for all rendering (critical from day 1)
2. **Object Pooling**: Reuse arrays/objects in render loop, avoid allocations
3. **Canvas Optimization**: Use `clearRect()` only on changed regions if possible
4. **FPS Monitoring**: Track frame times, warn if < 55fps

**Phase 1D (Audio):**
1. **Audio Buffer Caching**: Decode audio files once, reuse buffers
2. **No Rendering in Audio Callbacks**: Keep audio thread separate

**Phase 1F (Photos):**
1. **Image Caching**: Cache decoded Image objects, don't reload
2. **Lazy Decoding**: Only decode next 2-3 images

**Phase 1G (Video):**
1. **Video Element Reuse**: Reuse `<video>` elements, don't create new ones per scene
2. **First Frame Ready**: Wait for `canplay` event before displaying

**Phase 1I (Timeline):**
1. **Preload Next Scene**: Start loading when current scene 75% complete
2. **Memory Management**: Release resources when scenes no longer needed

### Operator UI Optimization

1. **Debounce**: Throttle WebSocket sends while dragging sliders (100ms)
2. **Virtual Scrolling** (Phase 1F+): For large asset lists (100+ items), only render visible thumbnails
3. **Lazy Loading** (Phase 1F+): Load asset thumbnails on scroll

## Browser Compatibility

**Target Browsers:**
- Chrome/Edge 90+ (primary - for Show View, most reliable WebGL/WebAudio)
- Firefox 88+ (secondary)
- Safari 14+ (if needed, may have WebGL quirks)

**Show View**: Chrome recommended for best WebGL/WebAudio performance
**Operator UI**: Any modern browser acceptable

## Development Workflow

### Phase-by-Phase Development

**Phase 1A (Foundation Setup):**
1. Create minimal Flask server with `/show` and `/operator` routes
2. Set up SocketIO namespaces
3. Create basic HTML pages with canvas elements
4. Verify WebSocket connection (ping/pong test)

**Phase 1B (First Math Visual):**
1. Implement `MathVisuals.js` base class with `init()`, `render()`, `cleanup()`
2. Implement `Lissajous.js` preset extending base class
3. Add operator UI button to trigger Lissajous
4. Test FPS counter updates every second

**Phase 1C (More Visuals):**
1. Add 3-4 more preset files (PolarRoses, Spirograph, etc.)
2. Add preset selector UI component
3. Test switching between presets smoothly

**Phase 1D (Music):**
1. Add `audio.js` utility with Web Audio API
2. Add music controls in operator UI
3. Test music plays independently of visuals

**Continue this pattern for each phase...**

### Daily Development Flow

1. **Start Flask**: `flask run` (debug mode enabled)
2. **Open Show View**: Navigate to `http://localhost:5000/show`, press F11 for fullscreen
3. **Open Operator UI**: Navigate to `http://localhost:5000/operator` in separate window
4. **Edit Code**: Save files, refresh browser (Flask auto-reloads on Python changes)
5. **Debug**: Use browser DevTools for JavaScript debugging, Network tab for WebSocket

**Hot Reload (Optional):**
- Browser extension: "Live Server" or "Auto Refresh"
- Or manual refresh (Cmd/Ctrl+R)

## Module Import Strategy

**ES6 Modules:**
- Use `import/export` syntax
- Browser resolves paths relative to HTML file
- No bundler needed for development

**Example:**
```javascript
// static/show/scenes/VideoScene.js
export class VideoScene {
    // ...
}

// static/show/show.js
import { VideoScene } from './scenes/VideoScene.js';
```

**CDN Libraries:**
- PixiJS: `<script src="https://pixijs.download/release/pixi.min.js"></script>`
- Socket.io: Use ESM CDN version for modules
- Or download and serve locally from `/static/vendor/`
