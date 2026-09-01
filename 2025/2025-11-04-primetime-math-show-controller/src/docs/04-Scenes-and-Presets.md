# Scenes & Presets

## Scene Implementation Order

Scenes are built incrementally by complexity and dependencies:

1. **MathVisuals** (Phase 1B-1C) - No external assets, pure rendering
2. **TextCards** (Phase 1E) - Simple Canvas text rendering
3. **PhotoSlideshow** (Phase 1F) - Image loading, basic asset management
4. **VideoScene** (Phase 1G) - Complex media integration
5. **Countdown** (Phase 1H) - Specialized feature with timing precision

---

## Common Parameters

All scenes support these optional parameters:
- `transitionIn/Out`: `cut | fade:ms | cross:ms`
- `overlayTitle`: optional string; rendered as an upper-left bug
- `brightness`, `gamma`, `saturation`: global tweak per scene (optional)

---

## MathVisuals (Presets)

**Implementation**: Canvas 2D API or PixiJS WebGL  
**Dependencies**: None  
**Complexity**: Low to Medium

All GPU/Canvas friendly with performance guardrails. Math visuals are parametric and generate in real-time without external assets.

### Phase 1B: Core Preset

**1. Lissajous Lab** (Simplest, first implementation)
- **Params**: `{a:int=3, b:int=2, delta:float=1.57, trail:int=100, speed:float=1.0, glow:float=0.5}`
- **Complexity**: Low - Simple parametric curve `x = sin(a*t + delta), y = sin(b*t)`
- **Notes**: Perfect first preset, no transformations needed, immediate visual feedback

### Phase 1C: Expanded Library

**2. Polar Roses**
- **Params**: `{k:float=3.0, rotation:float=0.0, petalGlow:float=0.7, speed:float=1.0}`
- **Complexity**: Low - Polar equation `r = sin(k*θ)`
- **Notes**: Beautiful patterns with simple k values (try k=2,3,5,7)

**3. Spirograph/Epicycles**
- **Params**: `{radii:[int]=3, speed:float=1.0, trace:boolean=true}`
- **Complexity**: Medium - Multiple circles, compound rotation
- **Notes**: Classic mathematical drawing toy, mesmerizing

**4. Digits Rain (π/e/primes)**
- **Params**: `{charset:"pi|e|primes", density:float=0.5, speed:float=1.0, fontSize:int=16}`
- **Complexity**: Low - Matrix-style falling text
- **Notes**: Text rain with mathematical constants, good typography showcase

**5. Ulam Prime Spiral**
- **Params**: `{grid:int=50, pulse:float=1.0, highlightPrimes:boolean=true}`
- **Complexity**: Medium - Requires prime number generation, spiral layout
- **Notes**: Visually reveals patterns in prime numbers

**6. Conway's Game of Life**
- **Params**: `{seed:"gosper|random", stepMs:int=100, cellSize:int=10}`
- **Complexity**: Medium - Cellular automaton, grid state tracking
- **Notes**: Classic, fascinating emergent behavior

**7. Platonic Solids** (WebGL recommended)
- **Params**: `{type:"tetra|cube|octa|dodeca|icosa", wire:boolean=false, spinSpeed:float=1.0}`
- **Complexity**: High - 3D geometry, requires WebGL or perspective projection
- **Notes**: Best with PixiJS or Three.js, impressive visual

**8. Voronoi Flow**
- **Params**: `{sites:int=20, flowSpeed:float=1.0, colorShift:float=0.5}`
- **Complexity**: Medium - Voronoi diagram computation, animation
- **Notes**: Organic flowing patterns, performance-sensitive

**9. Vector Field Swirls**
- **Params**: `{noiseScale:float=0.01, particleCount:int=500, speed:float=1.0}`
- **Complexity**: High - Perlin noise, particle simulation
- **Notes**: Requires noise function library, CPU/GPU intensive

**10. Mandelbrot/Julia Set**
- **Params**: `{zoom:float=1.0, centerX:float=-0.5, centerY:float=0.0, maxIter:int=100, hueCycle:float=1.0}`
- **Complexity**: High - Fractal computation, zoom navigation
- **Notes**: Beautiful but computationally expensive, best with WebGL shaders

### Default Rotation (good show mix)
- Lissajous (60s) → Polar Roses (60s) → Spirograph (60s) → Digits Rain (45s) → Ulam Spiral (60s) → Conway's Life (90s)

### Performance Guardrails
- Target: 60fps minimum, acceptable: 55fps
- If FPS < 55 for 3 consecutive seconds:
  - Reduce particle count by 50%
  - Disable glow effects
  - Lower resolution
  - Report to operator UI

---

## TextCards

**Implementation**: Canvas 2D API  
**Dependencies**: Web fonts (loaded via CSS)  
**Complexity**: Low

### Parameters
- `lines:[string]` - Array of text lines to display
- `layout:"center|lower-third|upper-left"` - Screen position
- `enter:"slide|fade|zoom"` - Entry animation
- `exit:"slide|fade|zoom"` - Exit animation
- `duration:int=5000` - Display time in milliseconds
- `fontSize:int=72` - Font size in pixels
- `fontWeight:"normal|bold"` - Text weight

### Use Cases
- Slogans and motivational quotes
- School roll-call announcements
- Sponsor thank-you messages
- Live ad-hoc announcements

### Notes
- Text renders on top of any background scene (overlay mode)
- Supports line breaks, basic formatting
- Theme fonts applied automatically (Bebas Neue for headings, Inter for body)

---

## PhotoSlideshow

**Implementation**: Canvas 2D API with Image objects  
**Dependencies**: Image files in `/assets/photos/`, basic file scanning  
**Complexity**: Medium

### Parameters
- `folder:string="/assets/photos"` - Source folder for images
- `kenBurns:boolean=true` - Enable slow zoom/pan effect
- `holdEachMs:int=3500` - Time per photo
- `randomize:boolean=false` - Shuffle order
- `avoidRepeatMinutes:int=10` - Don't repeat photos within N minutes
- `transition:"fade|cross"` - Transition style between photos
- `transitionMs:int=800` - Transition duration

### Notes
- Images are scaled to fit 1920x1080 canvas (aspect ratio preserved)
- EXIF rotation applied if present (Phase 1F+ with Pillow)
- Ken Burns effect: slow zoom from 100% to 110% with random pan direction
- Supports JPG, PNG formats
- **Phase 1F**: Basic file listing, no preprocessing
- **Future phases**: Thumbnail generation, EXIF data, duplicate detection

### Ken Burns Implementation
```javascript
// Zoom from 1.0 to 1.1 over holdEachMs duration
// Pan direction randomized: top-left to bottom-right or top-right to bottom-left
// Easing function: easeInOutQuad for smooth motion
```

---

## VideoScene

**Implementation**: HTML5 `<video>` element positioned over/behind canvas  
**Dependencies**: Video files (H.264/AAC), optional ffprobe validation  
**Complexity**: High

### Parameters
- `src:string` - Path to video file (e.g., `/assets/videos/intro.mp4`)
- `loop:boolean=false` - Loop video playback
- `holdLastFrame:boolean=false` - Pause on last frame instead of advancing
- `volume:float=1.0` - Video audio volume (0.0-1.0)
- `playbackRate:float=1.0` - Speed multiplier (0.5-2.0)

### Controls
- Play/pause/seek via WebSocket events
- End behavior: hold frame, loop, or auto-advance to next scene
- Sync with scene duration (override timeline duration if `duration:"auto"`)

### Notes
- **Codec requirement**: H.264 video, AAC audio (MP4 container)
- Video element layered behind canvas or overlaid based on scene composition
- First frame preloaded for smooth start
- **Phase 1G**: Basic playback only
- **Future phases**: Thumbnail extraction, metadata validation with ffprobe

### Video Sync Strategy
- Use `video.currentTime` for seeking
- Monitor `timeupdate` event for progress
- Handle `ended` event for auto-advance or loop
- Report playback status to operator UI

---

## Countdown

**Implementation**: Canvas 2D API with large typography  
**Dependencies**: Audio files for tick/horn sounds (optional)  
**Complexity**: Medium

### Parameters
- `from:int=10` - Starting number (countdown from N to 0)
- `style:"big-flash|neon|minimal"` - Visual style
- `sound:boolean=true` - Enable tick sounds
- `confetti:boolean=true` - Trigger confetti at zero

### Behavior
- Displays each number for exactly 1 second
- Visual flash or pulse on each number
- Optional tick sound each second (short beep)
- Air horn sound at zero (if enabled)
- Confetti particle effect fires at zero
- Can be triggered as overlay (transparent background) or standalone scene

### Timing Precision
```javascript
// Use performance.now() for accurate timing
// Each number displays for exactly 1000ms
// Compensate for rendering time to maintain sync
```

### Confetti Trigger
- Particle system with physics simulation
- 150+ particles, random colors from theme palette
- Spread: 65 degrees, decay: 0.92
- Duration: ~3 seconds until particles settle

### Use Cases
- Awards ceremony countdown
- Break timer
- Event start countdown
- Dramatic scene transitions

---

## Scene Development Checklist

For each new scene type:
- [ ] Scene class with `init()`, `render()`, `cleanup()` methods
- [ ] Parameter validation and defaults
- [ ] Error handling (missing assets, rendering failures)
- [ ] Performance monitoring (FPS tracking)
- [ ] Operator UI controls (buttons, sliders, inputs)
- [ ] WebSocket events (start, stop, update params)
- [ ] Unit tests (parameter validation, lifecycle)
- [ ] Integration tests (WebSocket flow)
- [ ] Manual acceptance tests (visual quality, performance)
- [ ] Documentation updates
