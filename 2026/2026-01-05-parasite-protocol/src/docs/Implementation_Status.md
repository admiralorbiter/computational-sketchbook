# Implementation Status — Parasite Protocol

Last Updated: 2026-01-06

## Phase 0 — Skeleton (Foundation)

### ✅ Completed
- [x] **Time step / pause / speed control** (`core_time.rs`)
  - TimeScale resource with pause (Space) and speed controls (1/2/3 keys)
  - Basic pause/speed infrastructure ready
  
- [x] **Map renderer (basic)** (`arena_map.rs`)
  - Membrane ring rendered as a circle
  - CellRadius resource configured (75.0 units - increased for better gameplay space)
  - Basic visual foundation in place
  
- [x] **Organelles** (`arena_map.rs`)
  - Nucleus rendered at center (purple, 9 units radius scaled)
  - ER/Golgi rendered offset from center (yellow/orange, 7 units radius scaled)
  - 3 Mitochondria rendered in annulus band (red/orange, 6 units radius scaled)
  - Organelles scale proportionally with cell size
  - Proper z-ordering (membrane z=0, organelles z=1) to prevent flickering
  - Organelle components and types exported for other systems

- [x] **Basic UI framework (pan/zoom)** (`core_camera.rs`)
  - Keyboard panning (WASD/Arrow keys)
  - Mouse drag panning (middle mouse button)
  - Mouse wheel zoom (with min/max bounds)
  - Camera bounds clamping
  - MainCamera component and CameraBounds resource

- [x] **Project structure**
  - Plugin-based architecture established
  - AppState and RunState enums defined
  - Window configuration (1280x720, "Parasite Protocol")

### ❌ In Progress / Missing
- [ ] **Entity/component base**
  - Basic ECS patterns established, but no game-specific entities yet
  - Need to define core components (HP, Position, etc.)

- [ ] **Collision / navigation primitives**
  - No navigation grid implemented
  - No collision detection system
  - No flow field for enemy pathfinding

- [ ] **Selection system** (`core_selection` plugin - not created)
  - Mouse picking
  - Hover tooltips
  - Placement previews

- [ ] **Arena map features** (from Arena_Map.md)
  - ✅ Organelles (nucleus, ER/Golgi, mitochondria) rendered
  - [ ] Membrane segments (currently just visual circle)
  - [ ] Breach mechanics not implemented
  - [ ] Navigation grid/flow field missing

## Phase 1 — Combat Basics
- [ ] Enemy spawner + movement
- [ ] Damage + HP + death
- [ ] Basic "membrane breach" mechanic
- [ ] Nucleus HP and lose condition

## Phase 2+ — Future Phases
All future phases are not yet started.

---

## Recommended Next Steps

### Priority 1: Complete Phase 0 Foundation
1. ✅ **Add organelles to arena** (`arena_map.rs`) - COMPLETED
   - Nucleus, ER/Golgi, and mitochondria rendered with proper z-ordering
   - Organelles scale proportionally with cell size

2. **Create core_selection plugin**
   - Mouse picking system
   - Hover detection
   - Basic tooltip framework
   - Needed before placement systems

3. **Add navigation grid** (in `arena_map.rs` or new plugin)
   - Simple grid-based navigation
   - Mark organelle positions as blocked
   - Prepare for enemy pathfinding
   - Can be simple initially (128x128 grid)

### Priority 2: Begin Phase 1 (Combat Basics)
Once Phase 0 is solid:
1. Enemy spawner system
2. Basic enemy movement (toward nucleus)
3. HP/damage system
4. Nucleus as target with HP

### Why This Order?
- **Organelles first**: Everything else depends on knowing where organelles are (manufacturing, ATP zones, navigation)
- **Selection second**: Needed for all placement/interaction systems
- **Navigation third**: Needed for enemy movement, vesicle routing
- **Combat fourth**: Makes the game playable and testable

---

## Current Code Status

### Plugins Implemented
- ✅ `core_time` - Time control (pause/speed)
- ✅ `core_camera` - Camera controls (pan/zoom/bounds, updated for 75 unit cell radius)
- ✅ `arena_map` - Membrane rendering + organelles (nucleus, ER/Golgi, mitochondria)

### Plugins Missing (from Technical_Architecture.md)
- ❌ `core_selection` - Mouse picking, tooltips
- ❌ `core_save_seed` - Deterministic runs (optional for MVP)
- ❌ `enemy` - Enemy systems
- ❌ `combat` - Combat systems
- ❌ `manufacturing` - Manufacturing queue
- ❌ `shipping` - Vesicle delivery
- ❌ `tracks` - Track placement/routing
- ❌ `circuits` - Circuit wiring
- ❌ `infection` - Infection overlay
- ❌ `economy` - ATP/stress/membrane integrity
- ❌ `waves` - Wave generation
- ❌ `adaptation` - Strategy adaptation
- ❌ `render_entities` - Entity rendering
- ❌ `render_overlays` - Overlay rendering
- ❌ `ui_hud` - HUD/UI
- ❌ `audio` - Audio (optional)
- ❌ `debug_panel` - Debug tools

---

## Notes
- Project compiles and runs successfully ✅
- Window opens and displays cell with membrane and organelles ✅
- Organelles render without flickering (proper z-ordering) ✅
- Cell size increased to 75 units radius for better gameplay space ✅
- Camera controls work (pan/zoom) ✅
- Time controls work (pause/speed) ✅
- Organelles are queryable by other systems ✅
- Ready to build on this foundation

