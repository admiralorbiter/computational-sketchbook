# Timeline & Data Contracts

## Timeline JSON (authoritative)

**Note**: Timeline structure is introduced in Phase 1I. Early phases use direct scene triggering via WebSocket events.

### Full Timeline Example (Phase 1I)
```json
{
  "name": "Math Relays 2025",
  "theme": "neon-chalkboard",
  "items": [
    {
      "id": "math-intro",
      "sceneType": "MathVisuals",
      "params": { "preset": "lissajous", "a": 3, "b": 2, "speed": 1.0 },
      "duration": 60000,
      "transitionIn": "fade:800",
      "transitionOut": "fade:500",
      "notes": "Opening visual - simple Lissajous"
    },
    {
      "id": "welcome-text",
      "sceneType": "TextCards",
      "params": { 
        "lines": ["Welcome to", "Math Relays 2025"], 
        "layout": "center",
        "enter": "fade",
        "exit": "fade"
      },
      "duration": 5000,
      "transitionIn": "fade:600",
      "transitionOut": "fade:600"
    },
    {
      "id": "math-roses",
      "sceneType": "MathVisuals",
      "params": { "preset": "polar_roses", "k": 5, "speed": 0.8 },
      "duration": 90000,
      "transitionIn": "fade:600",
      "transitionOut": "fade:300"
    },
    {
      "id": "photo-loop",
      "sceneType": "PhotoSlideshow",
      "params": { "folder": "/assets/photos", "kenBurns": true, "holdEachMs": 3500 },
      "duration": 180000,
      "transitionIn": "cross:700",
      "transitionOut": "cross:700"
    },
    {
      "id": "intro-video",
      "sceneType": "VideoScene",
      "params": { "src": "/assets/videos/intro.mp4", "volume": 1.0 },
      "duration": "auto",
      "transitionIn": "fade:800",
      "transitionOut": "fade:500",
      "notes": "Welcome video"
    },
    {
      "id": "awards-countdown",
      "sceneType": "Countdown",
      "params": { "from": 10, "style": "big-flash", "sound": true },
      "duration": "auto",
      "transitionIn": "cut",
      "transitionOut": "cut"
    }
  ]
}
```

### Simple Scene Triggering (Phase 1B-1H)

Before timeline implementation, scenes are triggered directly via WebSocket:

```javascript
// Operator sends to server
socket.emit('SHOW_START_SCENE', {
  sceneType: 'MathVisuals',
  params: { preset: 'lissajous', a: 3, b: 2, speed: 1.0 }
});

// Server relays to Show View
socket.emit('SHOW_START_SCENE', { /* same payload */ });

// Show View responds
socket.emit('SHOW_STATUS', {
  sceneType: 'MathVisuals',
  preset: 'lissajous',
  fps: 60,
  state: 'RENDERING'
});
```

### Field Notes
- `duration`: `"auto"` means **VideoScene** uses media duration; **Countdown** uses computed duration; others in ms.
- `transitionIn`/`Out`: `"fade:ms"`, `"cross:ms"`, `"cut"`.
- `params` are scene-specific. See `04-Scenes-and-Presets.md`.

## Asset Metadata (cached in DB)
```json
{
  "id": "a_01he9j...",
  "type": "photo|video|music|logo",
  "path": "/assets/photos/IMG_1234.jpg",
  "width": 1920,
  "height": 1280,
  "hash": "phash-...",
  "addedAt": 1730745600
}
```

## Theme JSON
```json
{
  "id": "neon-chalkboard",
  "palette": { "bg": "#0f1115", "fg": "#F4F4F4", "accent": ["#39FF14","#00E5FF","#FF3AF2","#FFE600"] },
  "fonts": { "heading": "Bebas Neue", "body": "Inter" },
  "motion": { "easing": "easeOutQuad", "defaultMs": 350 },
  "gammaLift": 0.1,
  "confetti": { "particleCount": 150, "spread": 65, "decay": 0.92 }
}
```
