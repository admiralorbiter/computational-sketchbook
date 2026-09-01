# Prime Time — Design Docs
**Date:** 2025-11-04  
**Owner:** Jonathan Lane  
**Scope:** Single-operator, preplanned show with music, videos, photo slideshow, math visuals, big-text interstitials, and a triggerable awards countdown.

## Contents
- `01-Product-Vision-and-Scope.md`
- `02-System-Architecture.md`
- `03-Timeline-and-Data-Contracts.md`
- `04-Scenes-and-Presets.md`
- `05-Operator-UI-Design.md`
- `06-WebSocket-Events-and-API.md`
- `07-Asset-Pipeline-and-Ingest.md`
- `08-Performance-and-Reliability.md`
- `09-Setup-Runbook-and-Deployment.md`
- `10-Acceptance-Tests-and-QA.md`
- `11-Roadmap-and-Phased-Plan.md`
- `12-Database-Schema-and-Persistence.md`
- `13-State-Machine-and-Playback-Logic.md`
- `14-Error-Handling-and-Validation.md`
- `15-Frontend-Technology-and-Setup.md`
- `16-Testing-Strategy.md`

## TL;DR
- **Renderer:** Fullscreen browser Show View (Canvas 2D for math visuals, then WebAudio, then HTML5 `<video>`).
- **Backend:** Flask + Flask-SocketIO; minimal SQLite initially; build incrementally.
- **Operator UI:** Vanilla JS + Web Components; live cues, scene controls, parameter adjustments.
- **Build Order:** Math visuals first → music → text → photos → video → timeline.
- **Signature:** Neon Chalkboard theme; parametric math presets; 10→0 countdown macro.
- **Philosophy:** Rendering-first approach; prove core visuals work before adding asset complexity.
