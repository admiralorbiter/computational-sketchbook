# WebSocket Events & API

## Namespaces
- `/control` — Operator UI → Server
- `/show` — Server ↔ Show View

## Server → Show View
- `SHOW_LOAD_TIMELINE { timeline }`
- `SHOW_PLAY { index?:number }`
- `SHOW_PAUSE {}`
- `SHOW_JUMP { index:number }`
- `SHOW_SKIP { delta:+1|-1 }`
- `SHOW_HOLD { on:boolean }`
- `SHOW_BLACKOUT { on:boolean }`
- `SHOW_SET_VOLUME { value:0..1 }`
- `SHOW_SET_THEME { id:string }`
- `SHOW_CUE { type:string, payload:any }`
  - Types: `COUNTDOWN_START`, `CONFETTI`, `SHOW_TEXT`, `SET_PARAM`

## Show View → Server (telemetry)
- `SHOW_STATUS { fps, sceneId, itemIndex, timecodeMs, nextId }`
- `ASSET_PRELOAD_DONE { sceneId }`
- `ERROR { code, message, context }`

## Operator UI → Server
- Mirrors server→show commands with operator identity.
- `TIMELINE_SAVE { timeline }`
- `ASSET_INDEX_REQUEST {}` → server responds with asset list.
