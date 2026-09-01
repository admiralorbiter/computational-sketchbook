# PrimeTime — PREP-KC Math Relays Live Show Controller (November 2025)

> **Category:** `[SKETCHBOOK EXPERIMENT / LIVE EVENT CONTROL & MATHEMATICAL VISUALS]`  
> **Date:** November 4–5, 2025  
> **Stack:** Python 3, Flask, Flask-SocketIO, SQLite, HTML5 Canvas, Vanilla JavaScript  
> **Original Origin:** `admiralorbiter/PrimeTime` (HEAD: `f824720`)  

---

## 1. Project Purpose & Scope

*PrimeTime* was designed as a single-operator broadcast/control-room system for the PREP-KC Math Relays, replacing manual multi-application alt-tabbing with an integrated, programmable live show controller running interactive mathematical visuals, countdowns, and cues:

```text
               ┌────────────────────────────────────────────────────────┐
               │           OPERATOR VIEW (Desk Interface)               │
               │   Preset Picker, Param Sliders, Transition Triggers    │
               └──────────────────────────┬─────────────────────────────┘
                                          │
                        WebSocket Control Bus (Flask-SocketIO)
                        - CONTROL_START_SCENE / CONTROL_UPDATE_PARAMS
                        - SHOW_FRAME_TELEMETRY (FPS feedback)
                                          │
               ┌──────────────────────────▼─────────────────────────────┐
               │           SHOW VIEW (Fullscreen Projection)            │
               │  HTML5 Canvas Renderer, Dynamic Math Scenes, Auto-FPS  │
               └────────────────────────────────────────────────────────┘
```

---

## 2. Implemented Capabilities: The Phase 1C Math Visuals Engine

Development reached **Phase 1C (Math Visuals Library)**, producing seven interactive mathematical visualization presets:

1. **Lissajous Curves:** Harmonic oscillation curves with live phase and frequency controls.
2. **Polar Roses:** Modulated harmonic sinusoidal blooms ($r = a \cos(k	heta)$).
3. **Spirographs:** Epitrochoid and hypotrochoid rolling circle curves.
4. **Digits Rain:** Matrix-style streaming numeric columns.
5. **Ulam Prime Spiral:** Square spiral highlighting prime distributions in real-time.
6. **Conway's Game of Life:** Cellular automata with seed presets and mutation rate sliders.
7. **Mandelbrot Fractal:** Interactive complex plane rendering with continuous zoom and iteration tuning.

### Orchestration Infrastructure:
- **Scene Manager & Transitions:** Cut, Fade, and Crossfade transitions between mathematical presets.
- **Adaptive Performance:** Dynamic complexity throttling when client frame rate drops below 45 FPS.

---

## 3. Preserved Artifacts

- **Server & WebSocket Handlers (`src/app.py`, `src/routes/`):** Real-time SocketIO control bus and REST telemetry endpoints.
- **Operator Desk (`src/static/operator/`):** Preset selection UI, parameter manipulation sliders, and live transition triggers.
- **Show View & Visual Engines (`src/static/show/`):** Fullscreen Canvas scene manager and 7 mathematical visual generators.
