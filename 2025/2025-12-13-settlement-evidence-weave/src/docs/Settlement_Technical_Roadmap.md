# Settlement — Technical Implementation Roadmap

**Engine:** Custom (Phaser 3 + Matter.js)  
**Solo Dev Build**  
**Core Mechanic:** Evidence Weave puzzle system  

---

## Document Purpose

This roadmap sequences every major system from foundation to vertical slice. Each phase includes goals, success criteria, implementation details, and dependencies. Follow phases in order—later systems assume earlier ones exist.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         GAME SHELL                              │
│  (Phaser bootstrap, scene management, global state container)   │
└─────────────────────────────────────────────────────────────────┘
        │
        ├──────────────────┬──────────────────┬──────────────────┐
        ▼                  ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  PUZZLE       │  │  NARRATIVE    │  │  BOARD/UI     │  │  META         │
│  ENGINE       │  │  ENGINE       │  │  SYSTEM       │  │  PROGRESSION  │
│               │  │               │  │               │  │               │
│ - Grid logic  │  │ - Scene graph │  │ - Indicators  │  │ - Unlocks     │
│ - Tiles       │  │ - Dialogue    │  │ - Resources   │  │ - Templates   │
│ - Chains      │  │ - Choices     │  │ - Tooltips    │  │ - Persistence │
│ - Taint       │  │ - State flags │  │ - Actions     │  │ - Run history │
│ - Hazards     │  │ - Characters  │  │ - Heat meter  │  │               │
└───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘
        │                  │                  │                  │
        └──────────────────┴──────────────────┴──────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │       DAY/NIGHT LOOP          │
                    │  (Orchestrates all systems)   │
                    └───────────────────────────────┘
```

---

## Phase 0: Project Scaffolding ✅ COMPLETE

**Goal:** Establish the development environment and project structure before writing game logic.

**Status:** ✅ Completed

### Success Criteria
- [x] `npm run dev` launches Phaser in browser with hot reload
- [x] TypeScript compiles without errors
- [x] Folder structure supports modular system development
- [x] Basic scene transitions work

### Implementation Notes

**Completed:**
- All required directory structure created (systems/, data/, ui/, types/, tools/, docs/)
- `src/config.ts` created with GAME_CONFIG constants (1280x720 resolution, grid settings, resources, tuning)
- `src/config/gameConfig.ts` updated to use constants from config.ts
- `src/systems/core/GameState.ts` implemented with GameStateManager class using Phaser EventEmitter
- Type definitions created in `src/types/puzzle.ts` and `src/types/game.ts`
- `src/scenes/TransitionScene.ts` placeholder created
- Roadmap moved to `docs/` directory
- All TypeScript compilation errors resolved
- Build system verified working

**Note:** Existing scenes (`DayVNScene.ts`, `NightPuzzleScene.ts`) are retained. These align with roadmap expectations and can be refactored to `DayScene.ts`/`NightScene.ts` later if needed.

### Implementation

#### 0.1 Project Setup
```bash
settlement/
├── src/
│   ├── main.ts                 # Phaser bootstrap
│   ├── config.ts               # Game constants, tuning values
│   ├── scenes/
│   │   ├── BootScene.ts        # Asset preloading
│   │   ├── MainMenuScene.ts
│   │   ├── DayScene.ts
│   │   ├── NightScene.ts       # Puzzle container
│   │   └── TransitionScene.ts
│   ├── systems/
│   │   ├── puzzle/             # Evidence Weave
│   │   ├── narrative/          # VN engine
│   │   ├── board/              # Markets/indicators
│   │   ├── meta/               # Progression/unlocks
│   │   └── core/               # Shared utilities
│   ├── data/
│   │   ├── scenes/             # Narrative JSON/YAML
│   │   ├── puzzles/            # Level definitions
│   │   ├── characters/
│   │   └── config/
│   ├── ui/
│   │   ├── components/         # Reusable UI elements
│   │   └── styles/
│   └── types/                  # TypeScript interfaces
├── assets/
│   ├── sprites/
│   ├── audio/
│   ├── fonts/
│   └── ui/
├── tools/                      # Content authoring scripts
└── docs/                       # Design docs (your existing PDFs live here)
```

#### 0.2 Core Configuration
```typescript
// src/config.ts
export const GAME_CONFIG = {
  // Display
  WIDTH: 1280,
  HEIGHT: 720,
  
  // Puzzle grid
  GRID_COLS: 8,
  GRID_ROWS: 10,
  TILE_SIZE: 48,
  
  // Resources (the three core numbers)
  STARTING_CAPACITY: 10,
  STARTING_STANDING: 5,
  STARTING_MOMENTUM: 0,
  
  // Tuning
  TAINT_SPREAD_INTERVAL: 2,  // turns between taint spread
  CHAIN_MIN_LENGTH: 3,
  
  // Day structure
  ACTIONS_PER_DAY: 2,
};
```

#### 0.3 State Container Pattern
```typescript
// src/systems/core/GameState.ts
export interface GameState {
  // Run state
  currentDay: number;
  phase: 'morning' | 'day' | 'night' | 'resolution';
  
  // Resources
  capacity: number;
  standing: number;
  momentum: number;
  
  // Puzzle state (isolated for easy reset)
  puzzle: PuzzleState | null;
  
  // Narrative state
  flags: Map<string, boolean | number | string>;
  relationships: Map<string, number>;
  
  // Meta (persists across runs)
  unlocks: Set<string>;
  templates: string[];
  precedents: string[];
  
  // Board indicators
  indicators: Indicator[];
}
```

Use a simple pub/sub pattern for state changes—Phaser's EventEmitter works fine for this scale.

---

## Phase 1: Evidence Weave — Core Puzzle Engine ✅ COMPLETE

**Goal:** Build the puzzle as a standalone system. This is your highest-risk item and must be fun before anything else gets built.

**Why first:** Your design docs say "If the night puzzle alone is compelling, the rest of the game can be built around it." Validate this immediately.

**Status:** ✅ Completed - MVP implementation ready for playtesting

### Success Criteria
- [x] Grid renders with placeholder tiles
- [x] Player can place tiles via click/drag
- [x] Chain detection highlights valid proof chains
- [x] Taint spreads on a timer or turn count
- [x] Completing a chain to target triggers reward state
- [ ] Playtesters find the core loop engaging for 10+ minutes without any story context (pending playtest)

### Puzzle Strategy & How to Play

**Goal:** Collect enough evidence points by connecting proof tiles to target tiles before running out of turns or the board gets overwhelmed by corruption.

**Core Mechanics:**
1. **Placement:** Click a tile in your hand (bottom of screen), then click an empty grid cell to place it
   - **Evidence (Blue):** Base proof tiles, most common
   - **Testimony (Purple):** Connector tiles, common
   - **Document (Gold):** High-value tiles, rarer but worth more points

2. **Chains:** Connect 3+ tiles orthogonally (up/down/left/right) to form chains
   - Chains that reach a **Target (Green)** tile at the top are completed
   - Completed chains award evidence points and are cleared from the board
   - Longer chains = more points
   - Document tiles add bonus value (+25 each)
   - Contested chains (touched by taint) are worth 60% less

3. **Taint Pressure:** Red corruption spreads every 2 turns
   - Spreads orthogonally from taint sources
   - Empty cells become new taint sources
   - Evidence tiles become "contested" (reduced value)
   - After 3 taint hits, tiles are consumed/destroyed
   - If 50%+ of board is tainted, you lose

4. **Win/Loss:**
   - **Win:** Collect required evidence (shown in top-left)
   - **Loss:** Run out of turns OR board overwhelmed by taint

**Strategy Tips:**
- Build chains toward the green target tiles at the top
- Place tiles efficiently to create multiple chain opportunities
- Watch taint spread patterns - it spreads every 2 turns
- Complete chains quickly before taint corrupts them
- Use documents strategically for bonus points
- Keep chains away from taint sources when possible

### Implementation Notes

**Completed Systems:**
- Pure logic modules (ChainDetector, TaintSystem, PlacementRules, HandManager, PuzzleRunner)
- Phaser rendering (GridRenderer, PuzzleHud)
- Input handling (PlacementController)
- Scene integration (NightPuzzleScene replaces old tower scene)
- Light GameState integration (rewards → momentum/standing)
- Unit tests (Vitest setup with tests for core logic)
- Debug mode (M key toggles debug overlay)

**File Structure:**
```
src/systems/puzzle/
├── types.ts                    # Internal puzzle types
├── logic/
│   ├── ChainDetector.ts        # Flood-fill chain detection
│   ├── TaintSystem.ts          # Taint spread logic
│   ├── PlacementRules.ts       # Placement validation
│   ├── HandManager.ts          # Hand refill with weighted RNG
│   ├── PuzzleRunner.ts         # Turn orchestration
│   └── __tests__/              # Unit tests
├── state/
│   └── createPuzzleState.ts    # Deterministic state initialization
├── view/
│   ├── GridRenderer.ts         # Phaser grid rendering
│   └── PuzzleHud.ts            # UI overlay
└── input/
    └── PlacementController.ts  # Pointer input handling
```

**Configuration (src/config.ts):**
- Grid: 8x10 tiles
- Taint spread: Every 2 turns
- Chain minimum: 3 tiles
- Taint consume threshold: 3 hits
- Overwhelm threshold: 50% of board
- Default level: Evidence required scales with day (80 + day*15), turns (25 + day*3)

**Testing:**
- Vitest configured with unit tests for pure logic
- Debug overlay (M key) shows chain count, taint sources, hand contents
- Run tests: `npm test`

### 1.1 Grid Foundation

#### Data Structures
```typescript
// src/systems/puzzle/types.ts

export type TileType = 
  | 'empty'
  | 'evidence'      // Base proof tile
  | 'testimony'     // Connects evidence
  | 'document'      // High-value, harder to place
  | 'tainted'       // Corrupted, spreads
  | 'blocked'       // Impassable (fee gate, throttle)
  | 'target';       // Chain destination

export interface Tile {
  type: TileType;
  x: number;
  y: number;
  
  // Chain membership
  chainId: string | null;
  
  // Corruption tracking
  taintLevel: number;        // 0 = clean, 3 = fully tainted
  taintSource: boolean;      // Does this spread taint?
  
  // Validity
  contested: boolean;        // Touched by taint but not consumed
  
  // Visual state
  highlighted: boolean;
  animating: boolean;
}

export interface PuzzleState {
  grid: Tile[][];
  targetPositions: {x: number, y: number}[];
  
  turnsElapsed: number;
  tilesPlaced: number;
  chainsCompleted: number;
  
  // Queue of tiles player can place
  hand: TileType[];
  handSize: number;
  
  // Hazard state
  activeTaintSources: {x: number, y: number}[];
  throttleZones: {x: number, y: number, radius: number}[];
  
  // Win/loss
  evidenceCollected: number;
  evidenceRequired: number;
  maxTurns: number;
}
```

#### Grid Manager
```typescript
// src/systems/puzzle/GridManager.ts

export class GridManager {
  private grid: Tile[][];
  private scene: Phaser.Scene;
  private tileSprites: Map<string, Phaser.GameObjects.Sprite>;
  
  constructor(scene: Phaser.Scene, cols: number, rows: number) {
    this.scene = scene;
    this.grid = this.createEmptyGrid(cols, rows);
    this.tileSprites = new Map();
  }
  
  // Core operations
  placeTile(x: number, y: number, type: TileType): boolean;
  removeTile(x: number, y: number): Tile | null;
  getTile(x: number, y: number): Tile | null;
  getNeighbors(x: number, y: number): Tile[];
  
  // Chain detection (see 1.2)
  findChains(): Chain[];
  validateChain(chain: Chain): ChainValidity;
  
  // Taint system (see 1.3)
  spreadTaint(): TaintEvent[];
  getTaintedTiles(): Tile[];
  
  // Rendering
  renderGrid(): void;
  highlightTiles(positions: {x: number, y: number}[]): void;
  animateChainCompletion(chain: Chain): Promise<void>;
}
```

### 1.2 Chain Detection Algorithm

The core puzzle verb is "connect proof to target." This requires pathfinding with validation.

```typescript
// src/systems/puzzle/ChainDetector.ts

export interface Chain {
  id: string;
  tiles: Tile[];
  isComplete: boolean;      // Reaches a target
  isContested: boolean;     // Any tile has taint contact
  value: number;            // Score/reward value
  composition: Map<TileType, number>;  // For reward calculation
}

export class ChainDetector {
  
  // Find all connected components of evidence tiles
  findAllChains(grid: Tile[][]): Chain[] {
    const visited = new Set<string>();
    const chains: Chain[] = [];
    
    for (let y = 0; y < grid.length; y++) {
      for (let x = 0; x < grid[y].length; x++) {
        const tile = grid[y][x];
        const key = `${x},${y}`;
        
        if (this.isChainableTile(tile) && !visited.has(key)) {
          const chain = this.floodFillChain(grid, x, y, visited);
          if (chain.tiles.length >= GAME_CONFIG.CHAIN_MIN_LENGTH) {
            chains.push(chain);
          }
        }
      }
    }
    
    return chains;
  }
  
  // Check if chain reaches any target
  private checkChainCompletion(chain: Chain, targets: Position[]): boolean {
    return chain.tiles.some(tile => 
      targets.some(t => t.x === tile.x && t.y === tile.y)
    );
  }
  
  // Calculate chain value based on composition and contamination
  calculateChainValue(chain: Chain): number {
    let base = chain.tiles.length * 10;
    
    // Bonus for document tiles (harder to place)
    base += (chain.composition.get('document') || 0) * 25;
    
    // Penalty for contested chains
    if (chain.isContested) {
      base = Math.floor(base * 0.6);
    }
    
    return base;
  }
}
```

### 1.3 Taint System

Taint is your primary pressure mechanic. It embodies "misinformation" and "corrupted records."

```typescript
// src/systems/puzzle/TaintSystem.ts

export interface TaintEvent {
  type: 'spread' | 'consume' | 'contest';
  position: {x: number, y: number};
  affectedTiles: Tile[];
}

export class TaintSystem {
  
  spreadTaint(grid: Tile[][], sources: Position[]): TaintEvent[] {
    const events: TaintEvent[] = [];
    
    for (const source of sources) {
      const neighbors = this.getSpreadTargets(grid, source);
      
      for (const neighbor of neighbors) {
        if (neighbor.type === 'empty') {
          // Empty cells can become taint sources
          neighbor.taintLevel = 1;
          events.push({
            type: 'spread',
            position: {x: neighbor.x, y: neighbor.y},
            affectedTiles: [neighbor]
          });
        } else if (this.isChainableTile(neighbor)) {
          // Evidence tiles become contested
          neighbor.taintLevel++;
          neighbor.contested = true;
          
          if (neighbor.taintLevel >= 3) {
            // Fully consumed - tile is destroyed
            events.push({
              type: 'consume',
              position: {x: neighbor.x, y: neighbor.y},
              affectedTiles: [neighbor]
            });
          } else {
            events.push({
              type: 'contest',
              position: {x: neighbor.x, y: neighbor.y},
              affectedTiles: [neighbor]
            });
          }
        }
      }
    }
    
    return events;
  }
  
  // Taint spreads orthogonally, not diagonally (clearer to read)
  private getSpreadTargets(grid: Tile[][], source: Position): Tile[] {
    const directions = [{x: 0, y: -1}, {x: 0, y: 1}, {x: -1, y: 0}, {x: 1, y: 0}];
    return directions
      .map(d => grid[source.y + d.y]?.[source.x + d.x])
      .filter(t => t && t.type !== 'blocked' && !t.taintSource);
  }
}
```

### 1.4 Input & Placement

```typescript
// src/systems/puzzle/PlacementController.ts

export class PlacementController {
  private selectedTile: TileType | null = null;
  private previewSprite: Phaser.GameObjects.Sprite | null = null;
  
  setupInput(scene: Phaser.Scene, gridManager: GridManager) {
    // Hand selection
    scene.input.on('pointerdown', (pointer: Phaser.Input.Pointer) => {
      const handTile = this.getHandTileAtPointer(pointer);
      if (handTile) {
        this.selectTile(handTile);
        return;
      }
      
      // Grid placement
      const gridPos = this.pointerToGrid(pointer);
      if (gridPos && this.selectedTile) {
        this.attemptPlacement(gridPos);
      }
    });
    
    // Hover preview
    scene.input.on('pointermove', (pointer: Phaser.Input.Pointer) => {
      if (this.selectedTile) {
        this.updatePreview(pointer);
      }
    });
  }
  
  private attemptPlacement(pos: Position): boolean {
    // Validate placement
    if (!this.canPlaceAt(pos)) {
      this.showInvalidFeedback(pos);
      return false;
    }
    
    // Place tile
    this.gridManager.placeTile(pos.x, pos.y, this.selectedTile);
    this.removeFromHand(this.selectedTile);
    this.selectedTile = null;
    
    // Trigger turn advancement
    this.events.emit('tilePlaced', pos);
    
    return true;
  }
  
  private canPlaceAt(pos: Position): boolean {
    const tile = this.gridManager.getTile(pos.x, pos.y);
    
    // Basic checks
    if (!tile || tile.type !== 'empty') return false;
    if (tile.taintSource) return false;
    
    // Throttle zone check (costs capacity)
    if (this.isInThrottleZone(pos) && this.gameState.capacity < 1) {
      return false;
    }
    
    return true;
  }
}
```

### 1.5 Turn Structure & Win/Loss

```typescript
// src/systems/puzzle/PuzzleRunner.ts

export class PuzzleRunner {
  private state: PuzzleState;
  private gridManager: GridManager;
  private chainDetector: ChainDetector;
  private taintSystem: TaintSystem;
  
  async runTurn(): Promise<TurnResult> {
    // 1. Player places tile (handled by PlacementController)
    // This method is called AFTER placement
    
    this.state.turnsElapsed++;
    this.state.tilesPlaced++;
    
    // 2. Check for completed chains
    const chains = this.chainDetector.findAllChains(this.gridManager.grid);
    const completedChains = chains.filter(c => c.isComplete);
    
    for (const chain of completedChains) {
      await this.resolveChain(chain);
    }
    
    // 3. Spread taint (every N turns)
    if (this.state.turnsElapsed % GAME_CONFIG.TAINT_SPREAD_INTERVAL === 0) {
      const taintEvents = this.taintSystem.spreadTaint(
        this.gridManager.grid,
        this.state.activeTaintSources
      );
      await this.animateTaintEvents(taintEvents);
    }
    
    // 4. Refill hand
    this.refillHand();
    
    // 5. Check win/loss
    return this.evaluateGameState();
  }
  
  private evaluateGameState(): TurnResult {
    // Win: collected enough evidence
    if (this.state.evidenceCollected >= this.state.evidenceRequired) {
      return { status: 'victory', reward: this.calculateReward() };
    }
    
    // Loss: out of turns
    if (this.state.turnsElapsed >= this.state.maxTurns) {
      return { status: 'timeout', reward: this.calculatePartialReward() };
    }
    
    // Loss: grid overwhelmed by taint
    if (this.isBoardLost()) {
      return { status: 'corrupted', reward: this.calculatePartialReward() };
    }
    
    return { status: 'continue' };
  }
  
  private async resolveChain(chain: Chain): Promise<void> {
    const value = this.chainDetector.calculateChainValue(chain);
    this.state.evidenceCollected += value;
    
    // Visual feedback
    await this.gridManager.animateChainCompletion(chain);
    
    // Clear chain tiles
    for (const tile of chain.tiles) {
      this.gridManager.removeTile(tile.x, tile.y);
    }
    
    this.state.chainsCompleted++;
  }
}
```

### 1.6 Puzzle Scene Integration

```typescript
// src/scenes/NightScene.ts

export class NightScene extends Phaser.Scene {
  private puzzleRunner: PuzzleRunner;
  private uiLayer: PuzzleUI;
  
  create(data: { level: LevelDefinition, gameState: GameState }) {
    // Initialize puzzle systems
    this.puzzleRunner = new PuzzleRunner(this, data.level);
    
    // Setup UI
    this.uiLayer = new PuzzleUI(this);
    this.uiLayer.bindToState(this.puzzleRunner.state);
    
    // Input
    const controller = new PlacementController();
    controller.setupInput(this, this.puzzleRunner.gridManager);
    controller.events.on('tilePlaced', () => this.onTilePlaced());
  }
  
  private async onTilePlaced() {
    const result = await this.puzzleRunner.runTurn();
    
    if (result.status !== 'continue') {
      this.endPuzzle(result);
    }
  }
  
  private endPuzzle(result: TurnResult) {
    // Transition to resolution
    this.scene.start('TransitionScene', {
      from: 'night',
      result: result,
      nextPhase: 'resolution'
    });
  }
}
```

### 1.7 Prototype Testing Checklist

Before moving to Phase 2, validate with these tests:

**Mechanical Tests:**
- [x] Chain detection correctly identifies all connected paths (unit tested)
- [x] Taint spreads predictably (players can anticipate) (orthogonal spread, every 2 turns)
- [x] Blocked tiles and throttle zones work as obstacles (PlacementRules implemented)
- [x] Turn counter and win/loss conditions trigger correctly (PuzzleRunner.evaluateGameState)
- [x] Hand refill maintains puzzle flow (HandManager with weighted RNG)

**Feel Tests (5 playtesters, no story context):**
- [ ] Players understand goal within 2 minutes (pending playtest)
- [ ] Players feel tension from taint spread (pending playtest)
- [ ] Completing chains feels satisfying (pending playtest)
- [ ] Players want to retry after losing (pending playtest)
- [ ] Average session length > 10 minutes voluntarily (pending playtest)

**Next Steps:**
- Run playtests with 5+ players
- Tune difficulty (evidence required, turn limits, taint spread rate)
- Adjust hand weights if needed
- Polish animations and feedback based on playtest feedback

---

## Phase 2: Board & Resource UI

**Goal:** Build the "Board" that shows markets, indicators, and player resources. This is how players understand the game state at a glance.

**Dependency:** None (can be developed in parallel with Phase 1)

### Success Criteria
- [ ] Board displays 5-7 indicators with clear labels
- [ ] Hovering indicator shows tooltip explaining what it affects
- [ ] Three resources (Capacity, Standing, Momentum) displayed prominently
- [ ] Changes animate so players see cause → effect
- [ ] Playtesters can explain what resources do after one loop

### 2.1 Indicator System

```typescript
// src/systems/board/types.ts

export interface Indicator {
  id: string;
  name: string;
  
  // Display
  displayMode: 'level' | 'percentage' | 'binary';
  currentValue: number;
  maxValue: number;
  
  // Categorization
  category: 'threat' | 'opportunity' | 'neutral';
  
  // What this indicator affects (for tooltips)
  effects: IndicatorEffect[];
  
  // What changes this indicator
  drivers: string[];
  
  // Visual
  icon: string;
  color: string;
}

export interface IndicatorEffect {
  target: 'capacity' | 'standing' | 'momentum' | 'puzzle' | 'narrative';
  description: string;
  threshold?: number;  // At what value does this kick in
}

// Example indicators for v1
export const BASE_INDICATORS: Partial<Indicator>[] = [
  {
    id: 'resolver_scrutiny',
    name: 'Resolver Scrutiny',
    category: 'threat',
    effects: [
      { target: 'puzzle', description: 'More taint sources in puzzles' },
      { target: 'standing', description: 'Disputes cost more Standing' }
    ],
    drivers: ['Failed arbitrations', 'High-profile cases', 'Pattern of disputes']
  },
  {
    id: 'community_trust',
    name: 'Community Trust',
    category: 'opportunity',
    effects: [
      { target: 'capacity', description: 'More volunteers available' },
      { target: 'narrative', description: 'Unlocks witness cooperation' }
    ],
    drivers: ['Successful cases', 'Mutual aid actions', 'Time spent organizing']
  },
  {
    id: 'heat',
    name: 'Heat',
    category: 'threat',
    effects: [
      { target: 'narrative', description: 'More hostile random encounters' },
      { target: 'puzzle', description: 'Throttle zones expand' }
    ],
    drivers: ['Visible opposition', 'Media attention', 'Corporate complaints']
  },
  {
    id: 'liquidity_access',
    name: 'Liquidity Access',
    category: 'neutral',
    effects: [
      { target: 'capacity', description: 'Determines available actions' },
      { target: 'narrative', description: 'Affects NPC attitudes' }
    ],
    drivers: ['Standing changes', 'Market conditions', 'Zone restrictions']
  },
  {
    id: 'media_narrative',
    name: 'Media Narrative',
    category: 'neutral',
    effects: [
      { target: 'momentum', description: 'Positive coverage boosts momentum' },
      { target: 'narrative', description: 'Shapes NPC initial attitudes' }
    ],
    drivers: ['Your public actions', 'Corporate PR', 'News events']
  }
];
```

### 2.2 Board UI Component

```typescript
// src/ui/components/BoardUI.ts

export class BoardUI extends Phaser.GameObjects.Container {
  private indicators: Map<string, IndicatorDisplay>;
  private resourceBar: ResourceBar;
  private tooltipPanel: TooltipPanel;
  
  constructor(scene: Phaser.Scene, x: number, y: number) {
    super(scene, x, y);
    
    this.resourceBar = new ResourceBar(scene, 0, 0);
    this.add(this.resourceBar);
    
    this.tooltipPanel = new TooltipPanel(scene);
    this.tooltipPanel.setVisible(false);
    this.add(this.tooltipPanel);
    
    this.indicators = new Map();
  }
  
  setupIndicators(indicatorData: Indicator[]) {
    const startY = 80;
    const spacing = 60;
    
    indicatorData.forEach((indicator, index) => {
      const display = new IndicatorDisplay(
        this.scene,
        0,
        startY + (index * spacing),
        indicator
      );
      
      // Hover for tooltip
      display.on('pointerover', () => this.showTooltip(indicator));
      display.on('pointerout', () => this.hideTooltip());
      
      this.indicators.set(indicator.id, display);
      this.add(display);
    });
  }
  
  // Animate value change with "why it changed" callout
  updateIndicator(id: string, newValue: number, reason: string) {
    const display = this.indicators.get(id);
    if (!display) return;
    
    const oldValue = display.getValue();
    const delta = newValue - oldValue;
    
    // Show change reason
    this.showChangeCallout(display, delta, reason);
    
    // Animate bar
    display.animateToValue(newValue);
  }
  
  private showChangeCallout(display: IndicatorDisplay, delta: number, reason: string) {
    const callout = this.scene.add.text(
      display.x + 150,
      display.y,
      `${delta > 0 ? '+' : ''}${delta} (${reason})`,
      { fontSize: '14px', color: delta > 0 ? '#4ade80' : '#f87171' }
    );
    
    this.scene.tweens.add({
      targets: callout,
      y: callout.y - 30,
      alpha: 0,
      duration: 2000,
      onComplete: () => callout.destroy()
    });
  }
}

// Lite/Full toggle for odds display
export class IndicatorDisplay extends Phaser.GameObjects.Container {
  private displayMode: 'lite' | 'full' = 'lite';
  
  // Lite: LOW / MID / HIGH
  // Full: Actual percentage
  
  setDisplayMode(mode: 'lite' | 'full') {
    this.displayMode = mode;
    this.updateDisplay();
  }
  
  private getDisplayText(): string {
    if (this.displayMode === 'lite') {
      if (this.value < 33) return 'LOW';
      if (this.value < 66) return 'MID';
      return 'HIGH';
    }
    return `${Math.round(this.value)}%`;
  }
}
```

### 2.3 Resource Bar

```typescript
// src/ui/components/ResourceBar.ts

export class ResourceBar extends Phaser.GameObjects.Container {
  private capacity: ResourceDisplay;
  private standing: ResourceDisplay;
  private momentum: ResourceDisplay;
  
  constructor(scene: Phaser.Scene, x: number, y: number) {
    super(scene, x, y);
    
    // Three resources, horizontally arranged
    this.capacity = new ResourceDisplay(scene, 0, 0, {
      name: 'Capacity',
      icon: 'icon_capacity',
      color: 0x60a5fa,  // Blue
      tooltip: 'Volunteers, safe spaces, and logistics. Spend to take actions.'
    });
    
    this.standing = new ResourceDisplay(scene, 120, 0, {
      name: 'Standing',
      icon: 'icon_standing',
      color: 0xfbbf24,  // Yellow
      tooltip: 'Your tier in wallet systems. Affects fees, speed, and access.'
    });
    
    this.momentum = new ResourceDisplay(scene, 240, 0, {
      name: 'Momentum',
      icon: 'icon_momentum',
      color: 0x34d399,  // Green
      tooltip: 'Public trust. Enables mass actions and protects against retaliation.'
    });
    
    this.add([this.capacity, this.standing, this.momentum]);
  }
  
  updateResources(state: GameState) {
    this.capacity.setValue(state.capacity);
    this.standing.setValue(state.standing);
    this.momentum.setValue(state.momentum);
  }
}
```

### 2.4 Tooltip System

```typescript
// src/ui/components/TooltipPanel.ts

export class TooltipPanel extends Phaser.GameObjects.Container {
  private background: Phaser.GameObjects.Rectangle;
  private titleText: Phaser.GameObjects.Text;
  private descriptionText: Phaser.GameObjects.Text;
  private effectsList: Phaser.GameObjects.Text;
  
  showIndicatorTooltip(indicator: Indicator) {
    this.titleText.setText(indicator.name);
    
    // Build effects description
    const effectsText = indicator.effects
      .map(e => `• ${e.description}`)
      .join('\n');
    this.effectsList.setText(effectsText);
    
    // Build drivers description
    const driversText = `Changes from: ${indicator.drivers.join(', ')}`;
    this.descriptionText.setText(driversText);
    
    this.resize();
    this.setVisible(true);
  }
}
```

---

## Phase 3: Narrative Engine

**Goal:** Build a lightweight visual novel system that supports branching dialogue, choices, state flags, and character relationships.

**Dependency:** Phase 0 (state management)

### Success Criteria
- [ ] Scenes load from JSON/YAML data files
- [ ] Dialogue displays with character portraits
- [ ] Choices branch to different scenes
- [ ] State flags persist and affect available choices
- [ ] Character relationships track numerically
- [ ] Scene system supports conditional content

### 3.1 Scene Data Format

```typescript
// src/data/scenes/schema.ts

export interface NarrativeScene {
  id: string;
  
  // Display
  background: string;
  music?: string;
  ambience?: string;
  
  // Content
  beats: DialogueBeat[];
  
  // Conditions to enter this scene
  conditions?: Condition[];
  
  // Where to go after
  nextScene?: string;
  choices?: SceneChoice[];
}

export interface DialogueBeat {
  type: 'dialogue' | 'narration' | 'action' | 'choice';
  
  // For dialogue
  speaker?: string;
  portrait?: string;
  text: string;
  
  // Optional effects that trigger when this beat plays
  effects?: Effect[];
  
  // Optional condition to show this beat
  condition?: Condition;
}

export interface SceneChoice {
  text: string;
  
  // What happens
  nextScene?: string;
  effects?: Effect[];
  
  // When is this available
  condition?: Condition;
  
  // Cost to select
  cost?: { resource: 'capacity' | 'standing' | 'momentum', amount: number };
}

export interface Condition {
  type: 'flag' | 'resource' | 'relationship' | 'indicator';
  key: string;
  operator: '==' | '!=' | '>' | '<' | '>=' | '<=';
  value: any;
}

export interface Effect {
  type: 'setFlag' | 'modifyResource' | 'modifyRelationship' | 'modifyIndicator' | 'unlock';
  key: string;
  value: any;
  operation?: 'set' | 'add' | 'subtract';
}
```

### 3.2 Example Scene Data

```yaml
# src/data/scenes/day1_morning.yaml

id: day1_morning
background: bg_apartment
music: ambient_morning

beats:
  - type: narration
    text: "The morning light filters through cheap blinds. Your terminal hums—the Board is already updating."
    
  - type: dialogue
    speaker: protagonist
    portrait: protag_tired
    text: "Another day of making the system work for people it wasn't designed to help."
    
  - type: narration
    text: "A message blinks. It's Maya—the organizer from the community hub."
    
  - type: dialogue
    speaker: maya
    portrait: maya_concerned
    text: "We've got a situation. The Delgados are getting eviction notices again. Same 'algorithmic adjustment' excuse."
    effects:
      - type: setFlag
        key: delgado_case_active
        value: true

choices:
  - text: "I'll look into it. Meet me at the hub."
    nextScene: day1_hub_intro
    effects:
      - type: modifyRelationship
        key: maya
        value: 1
        operation: add
        
  - text: "Can't today. I need to deal with my own Standing issue first."
    nextScene: day1_standing_office
    effects:
      - type: modifyRelationship
        key: maya
        value: -1
        operation: add
    condition:
      type: resource
      key: standing
      operator: '<'
      value: 3
      
  - text: "I'll help, but I need something first."
    nextScene: day1_negotiate
    condition:
      type: flag
      key: hardball_unlocked
      operator: '=='
      value: true
```

### 3.3 Narrative Runner

```typescript
// src/systems/narrative/NarrativeRunner.ts

export class NarrativeRunner {
  private scene: Phaser.Scene;
  private currentSceneData: NarrativeScene;
  private beatIndex: number = 0;
  private ui: DialogueUI;
  
  async loadScene(sceneId: string) {
    const sceneData = await this.loadSceneData(sceneId);
    
    // Check conditions
    if (sceneData.conditions && !this.evaluateConditions(sceneData.conditions)) {
      throw new Error(`Cannot enter scene ${sceneId}: conditions not met`);
    }
    
    this.currentSceneData = sceneData;
    this.beatIndex = 0;
    
    // Set up visuals
    await this.setBackground(sceneData.background);
    if (sceneData.music) this.playMusic(sceneData.music);
    
    // Start first beat
    this.advanceBeat();
  }
  
  advanceBeat() {
    // Find next valid beat (skip beats whose conditions aren't met)
    while (this.beatIndex < this.currentSceneData.beats.length) {
      const beat = this.currentSceneData.beats[this.beatIndex];
      
      if (!beat.condition || this.evaluateCondition(beat.condition)) {
        this.displayBeat(beat);
        return;
      }
      
      this.beatIndex++;
    }
    
    // No more beats—show choices or transition
    this.handleSceneEnd();
  }
  
  private displayBeat(beat: DialogueBeat) {
    // Apply effects
    if (beat.effects) {
      this.applyEffects(beat.effects);
    }
    
    // Display based on type
    switch (beat.type) {
      case 'dialogue':
        this.ui.showDialogue(beat.speaker, beat.portrait, beat.text);
        break;
      case 'narration':
        this.ui.showNarration(beat.text);
        break;
      case 'choice':
        // Choices are handled at scene end
        break;
    }
    
    this.beatIndex++;
  }
  
  private handleSceneEnd() {
    const scene = this.currentSceneData;
    
    if (scene.choices && scene.choices.length > 0) {
      // Filter to available choices
      const availableChoices = scene.choices.filter(c => 
        !c.condition || this.evaluateCondition(c.condition)
      );
      
      this.ui.showChoices(availableChoices, (choice) => this.selectChoice(choice));
    } else if (scene.nextScene) {
      this.loadScene(scene.nextScene);
    } else {
      // End of narrative segment
      this.events.emit('narrativeComplete');
    }
  }
  
  private selectChoice(choice: SceneChoice) {
    // Pay cost if any
    if (choice.cost) {
      this.gameState.modifyResource(choice.cost.resource, -choice.cost.amount);
    }
    
    // Apply effects
    if (choice.effects) {
      this.applyEffects(choice.effects);
    }
    
    // Go to next scene
    if (choice.nextScene) {
      this.loadScene(choice.nextScene);
    }
  }
  
  private evaluateCondition(condition: Condition): boolean {
    let currentValue: any;
    
    switch (condition.type) {
      case 'flag':
        currentValue = this.gameState.flags.get(condition.key);
        break;
      case 'resource':
        currentValue = this.gameState[condition.key as keyof GameState];
        break;
      case 'relationship':
        currentValue = this.gameState.relationships.get(condition.key) || 0;
        break;
      case 'indicator':
        currentValue = this.gameState.indicators
          .find(i => i.id === condition.key)?.currentValue || 0;
        break;
    }
    
    switch (condition.operator) {
      case '==': return currentValue === condition.value;
      case '!=': return currentValue !== condition.value;
      case '>': return currentValue > condition.value;
      case '<': return currentValue < condition.value;
      case '>=': return currentValue >= condition.value;
      case '<=': return currentValue <= condition.value;
    }
  }
}
```

### 3.4 Dialogue UI

```typescript
// src/ui/components/DialogueUI.ts

export class DialogueUI extends Phaser.GameObjects.Container {
  private dialogueBox: Phaser.GameObjects.NineSlice;
  private speakerName: Phaser.GameObjects.Text;
  private dialogueText: Phaser.GameObjects.Text;
  private portrait: Phaser.GameObjects.Sprite;
  private choiceContainer: Phaser.GameObjects.Container;
  
  private typewriterTween: Phaser.Tweens.Tween | null = null;
  private fullText: string = '';
  private isTyping: boolean = false;
  
  showDialogue(speaker: string, portraitKey: string, text: string) {
    this.speakerName.setText(speaker);
    this.portrait.setTexture(portraitKey);
    this.portrait.setVisible(true);
    
    this.startTypewriter(text);
  }
  
  showNarration(text: string) {
    this.speakerName.setText('');
    this.portrait.setVisible(false);
    
    this.startTypewriter(text);
  }
  
  showChoices(choices: SceneChoice[], onSelect: (choice: SceneChoice) => void) {
    this.choiceContainer.removeAll(true);
    
    choices.forEach((choice, index) => {
      const button = new ChoiceButton(
        this.scene,
        0,
        index * 50,
        choice,
        () => onSelect(choice)
      );
      
      // Show cost if any
      if (choice.cost) {
        button.showCost(choice.cost);
      }
      
      this.choiceContainer.add(button);
    });
    
    this.choiceContainer.setVisible(true);
  }
  
  private startTypewriter(text: string) {
    this.fullText = text;
    this.dialogueText.setText('');
    this.isTyping = true;
    
    let charIndex = 0;
    
    this.typewriterTween = this.scene.time.addEvent({
      delay: 30,
      callback: () => {
        charIndex++;
        this.dialogueText.setText(this.fullText.substring(0, charIndex));
        
        if (charIndex >= this.fullText.length) {
          this.isTyping = false;
          this.typewriterTween?.destroy();
        }
      },
      repeat: this.fullText.length - 1
    });
  }
  
  // Skip to end of current text
  skipTypewriter() {
    if (this.isTyping) {
      this.typewriterTween?.destroy();
      this.dialogueText.setText(this.fullText);
      this.isTyping = false;
    }
  }
}
```

### 3.5 Character Data

```typescript
// src/data/characters/types.ts

export interface Character {
  id: string;
  name: string;
  role: string;  // For UI display
  
  // Portraits
  portraits: {
    [key: string]: string;  // 'neutral', 'happy', 'angry', etc.
  };
  
  // Relationship tracking
  initialRelationship: number;
  relationshipThresholds: {
    hostile: number;     // Below this
    neutral: number;     // Between hostile and friendly
    friendly: number;    // Above this
    allied: number;      // Way above
  };
  
  // Narrative hooks
  personalQuest?: string;  // Scene ID for their arc
  unlockCondition?: Condition;
}

// src/data/characters/maya.yaml
id: maya
name: "Maya Reyes"
role: "Community Organizer"

portraits:
  neutral: maya_neutral
  concerned: maya_concerned
  determined: maya_determined
  angry: maya_angry
  hopeful: maya_hopeful

initialRelationship: 2

relationshipThresholds:
  hostile: -5
  neutral: 0
  friendly: 5
  allied: 10
```

---

## Phase 4: Day/Night Loop Integration

**Goal:** Wire together the puzzle, narrative, and board systems into the core gameplay loop.

**Dependencies:** Phases 1, 2, 3

### Success Criteria
- [ ] Morning phase shows Board briefing and sets up day context
- [ ] Day phase allows 2 actions with clear costs and effects
- [ ] Night transitions into puzzle with appropriate modifiers
- [ ] Resolution phase shows consequences and indicator changes
- [ ] Loop repeats cleanly with state persistence
- [ ] Players can describe the loop after one complete cycle

### 4.1 Loop Orchestrator

```typescript
// src/systems/core/LoopOrchestrator.ts

export type GamePhase = 'morning' | 'day' | 'night' | 'resolution';

export interface DayState {
  dayNumber: number;
  actionsRemaining: number;
  actionsTaken: Action[];
  nightModifiers: NightModifier[];
}

export class LoopOrchestrator {
  private gameState: GameState;
  private dayState: DayState;
  private sceneManager: Phaser.Scenes.SceneManager;
  
  startNewDay() {
    this.dayState = {
      dayNumber: this.gameState.currentDay,
      actionsRemaining: GAME_CONFIG.ACTIONS_PER_DAY,
      actionsTaken: [],
      nightModifiers: []
    };
    
    this.transitionToPhase('morning');
  }
  
  transitionToPhase(phase: GamePhase) {
    this.gameState.phase = phase;
    
    switch (phase) {
      case 'morning':
        this.startMorning();
        break;
      case 'day':
        this.startDay();
        break;
      case 'night':
        this.startNight();
        break;
      case 'resolution':
        this.startResolution();
        break;
    }
  }
  
  private startMorning() {
    // Show Board with any overnight changes
    const boardChanges = this.calculateOvernightChanges();
    
    this.sceneManager.start('DayScene', {
      phase: 'morning',
      boardChanges: boardChanges,
      briefingScene: this.getMorningBriefingScene()
    });
  }
  
  private startDay() {
    // Day scene with action selection
    this.sceneManager.start('DayScene', {
      phase: 'day',
      actionsRemaining: this.dayState.actionsRemaining,
      availableActions: this.getAvailableActions()
    });
  }
  
  private startNight() {
    // Calculate puzzle modifiers based on day actions and state
    const modifiers = this.calculateNightModifiers();
    
    // Select puzzle level
    const level = this.selectPuzzleLevel();
    
    this.sceneManager.start('NightScene', {
      level: level,
      modifiers: modifiers,
      gameState: this.gameState
    });
  }
  
  private startResolution() {
    // Calculate consequences
    const consequences = this.calculateConsequences();
    
    this.sceneManager.start('TransitionScene', {
      type: 'resolution',
      consequences: consequences,
      unlocksEarned: this.checkUnlocks()
    });
  }
  
  // Called from DayScene when player takes an action
  onActionTaken(action: Action) {
    this.dayState.actionsRemaining--;
    this.dayState.actionsTaken.push(action);
    
    // Apply immediate effects
    this.applyActionEffects(action);
    
    // Check for night modifiers this action adds
    if (action.nightModifier) {
      this.dayState.nightModifiers.push(action.nightModifier);
    }
    
    // Check if day is over
    if (this.dayState.actionsRemaining <= 0) {
      this.transitionToPhase('night');
    }
  }
  
  // Called from NightScene when puzzle ends
  onPuzzleComplete(result: TurnResult) {
    // Store puzzle results for resolution
    this.dayState.puzzleResult = result;
    
    this.transitionToPhase('resolution');
  }
  
  // Called from resolution scene when player continues
  onResolutionComplete() {
    this.gameState.currentDay++;
    
    // Check for arc progression
    if (this.shouldTriggerBoss()) {
      this.startBossEncounter();
    } else {
      this.startNewDay();
    }
  }
}
```

### 4.2 Action System

```typescript
// src/systems/day/ActionSystem.ts

export interface Action {
  id: string;
  name: string;
  description: string;
  
  // Costs
  capacityCost: number;
  timeCost: number;  // Usually 1 (one action slot)
  
  // Requirements
  conditions?: Condition[];
  
  // Effects
  effects: Effect[];
  
  // Puzzle modifier if any
  nightModifier?: NightModifier;
  
  // Narrative hook
  sceneId?: string;  // Optional scene that plays when selected
  
  // Category for UI
  category: 'investigate' | 'organize' | 'operate' | 'recover';
}

export const BASE_ACTIONS: Action[] = [
  // INVESTIGATE
  {
    id: 'gather_evidence',
    name: 'Gather Evidence',
    description: 'Search records and interview witnesses.',
    category: 'investigate',
    capacityCost: 1,
    timeCost: 1,
    effects: [
      { type: 'modifyIndicator', key: 'resolver_scrutiny', value: 5, operation: 'add' }
    ],
    nightModifier: {
      type: 'extra_evidence_tiles',
      value: 2
    }
  },
  {
    id: 'audit_trail',
    name: 'Request Audit Trail',
    description: 'Force disclosure through official channels. Slow but legitimate.',
    category: 'investigate',
    capacityCost: 0,
    timeCost: 1,
    conditions: [
      { type: 'resource', key: 'standing', operator: '>=', value: 3 }
    ],
    effects: [
      { type: 'setFlag', key: 'audit_pending', value: true }
    ],
    sceneId: 'audit_request_scene'
  },
  
  // ORGANIZE
  {
    id: 'community_meeting',
    name: 'Hold Community Meeting',
    description: 'Build support and recruit volunteers.',
    category: 'organize',
    capacityCost: 2,
    timeCost: 1,
    effects: [
      { type: 'modifyResource', key: 'capacity', value: 2, operation: 'add' },
      { type: 'modifyResource', key: 'momentum', value: 1, operation: 'add' },
      { type: 'modifyIndicator', key: 'community_trust', value: 10, operation: 'add' }
    ]
  },
  {
    id: 'witness_outreach',
    name: 'Witness Outreach',
    description: 'Convince someone to stake their credibility.',
    category: 'organize',
    capacityCost: 1,
    timeCost: 1,
    sceneId: 'witness_outreach_scene',
    nightModifier: {
      type: 'testimony_tile_available',
      value: true
    }
  },
  
  // OPERATE
  {
    id: 'file_dispute',
    name: 'File Dispute',
    description: 'Submit a formal challenge. Consumes evidence, triggers hearing.',
    category: 'operate',
    capacityCost: 1,
    timeCost: 1,
    conditions: [
      { type: 'flag', key: 'evidence_collected', operator: '>=', value: 50 }
    ],
    effects: [
      { type: 'setFlag', key: 'hearing_scheduled', value: true },
      { type: 'modifyIndicator', key: 'resolver_scrutiny', value: 15, operation: 'add' }
    ]
  },
  {
    id: 'mutual_aid_run',
    name: 'Mutual Aid Run',
    description: 'Distribute resources. Builds trust, costs capacity.',
    category: 'operate',
    capacityCost: 3,
    timeCost: 1,
    effects: [
      { type: 'modifyIndicator', key: 'community_trust', value: 15, operation: 'add' },
      { type: 'modifyResource', key: 'momentum', value: 2, operation: 'add' }
    ]
  },
  
  // RECOVER
  {
    id: 'lay_low',
    name: 'Lay Low',
    description: 'Reduce heat. Skip a day of action.',
    category: 'recover',
    capacityCost: 0,
    timeCost: 1,
    effects: [
      { type: 'modifyIndicator', key: 'heat', value: -20, operation: 'add' }
    ]
  },
  {
    id: 'standing_repair',
    name: 'Standing Maintenance',
    description: 'Jump through hoops to restore wallet access.',
    category: 'recover',
    capacityCost: 1,
    timeCost: 1,
    effects: [
      { type: 'modifyResource', key: 'standing', value: 1, operation: 'add' }
    ],
    sceneId: 'standing_office_scene'
  }
];
```

### 4.3 Night Modifiers

```typescript
// src/systems/puzzle/NightModifiers.ts

export interface NightModifier {
  type: string;
  value: any;
}

export class NightModifierApplicator {
  
  applyModifiers(basePuzzle: PuzzleState, modifiers: NightModifier[]): PuzzleState {
    let modified = { ...basePuzzle };
    
    for (const mod of modifiers) {
      modified = this.applyModifier(modified, mod);
    }
    
    return modified;
  }
  
  private applyModifier(state: PuzzleState, mod: NightModifier): PuzzleState {
    switch (mod.type) {
      case 'extra_evidence_tiles':
        // Add more evidence tiles to starting hand
        for (let i = 0; i < mod.value; i++) {
          state.hand.push('evidence');
        }
        break;
        
      case 'testimony_tile_available':
        // Add testimony tile (high-value connector)
        state.hand.push('testimony');
        break;
        
      case 'extra_taint_sources':
        // Add more taint sources (from high heat)
        for (let i = 0; i < mod.value; i++) {
          const pos = this.findEmptyPosition(state.grid);
          if (pos) {
            state.activeTaintSources.push(pos);
            state.grid[pos.y][pos.x].taintSource = true;
            state.grid[pos.y][pos.x].type = 'tainted';
          }
        }
        break;
        
      case 'throttle_zone':
        // Add throttle zone (costs capacity to place in)
        state.throttleZones.push({
          x: mod.value.x,
          y: mod.value.y,
          radius: mod.value.radius
        });
        break;
        
      case 'reduced_turns':
        // Time pressure
        state.maxTurns -= mod.value;
        break;
        
      case 'bonus_target':
        // Extra objective for more reward
        state.targetPositions.push(mod.value);
        state.evidenceRequired += 25;
        break;
    }
    
    return state;
  }
}
```

### 4.4 Consequence Calculator

```typescript
// src/systems/core/ConsequenceCalculator.ts

export interface Consequence {
  type: 'resource' | 'indicator' | 'flag' | 'unlock' | 'narrative';
  key: string;
  change: number | string | boolean;
  reason: string;
}

export class ConsequenceCalculator {
  
  calculate(dayState: DayState, gameState: GameState): Consequence[] {
    const consequences: Consequence[] = [];
    
    // From puzzle result
    if (dayState.puzzleResult) {
      consequences.push(...this.calculatePuzzleConsequences(dayState.puzzleResult));
    }
    
    // From indicator thresholds
    consequences.push(...this.calculateIndicatorTriggers(gameState));
    
    // From narrative flags
    consequences.push(...this.calculateNarrativeConsequences(gameState));
    
    // Retaliation check (based on heat)
    if (this.shouldTriggerRetaliation(gameState)) {
      consequences.push(...this.calculateRetaliation(gameState));
    }
    
    return consequences;
  }
  
  private calculatePuzzleConsequences(result: TurnResult): Consequence[] {
    const consequences: Consequence[] = [];
    
    // Base rewards
    if (result.status === 'victory') {
      consequences.push({
        type: 'flag',
        key: 'evidence_collected',
        change: result.reward.evidence,
        reason: 'Evidence gathered from investigation'
      });
    }
    
    // Failure-forward
    if (result.status === 'timeout' || result.status === 'corrupted') {
      consequences.push({
        type: 'flag',
        key: 'intel_fragment',
        change: true,
        reason: 'Partial intel recovered despite setback'
      });
      
      consequences.push({
        type: 'narrative',
        key: 'failure_scene',
        change: this.selectFailureScene(result.status),
        reason: 'Story continues despite loss'
      });
    }
    
    return consequences;
  }
  
  private shouldTriggerRetaliation(state: GameState): boolean {
    const heat = state.indicators.find(i => i.id === 'heat');
    if (!heat) return false;
    
    // Higher heat = higher chance
    const threshold = 50;
    return heat.currentValue > threshold && Math.random() < (heat.currentValue - threshold) / 100;
  }
  
  private calculateRetaliation(state: GameState): Consequence[] {
    // Pick a retaliation type based on what hurts most
    const retaliations = [
      { 
        condition: () => state.capacity > 3,
        consequence: {
          type: 'resource' as const,
          key: 'capacity',
          change: -2,
          reason: 'Volunteer doxxed—capacity reduced'
        }
      },
      {
        condition: () => state.standing > 2,
        consequence: {
          type: 'resource' as const,
          key: 'standing',
          change: -1,
          reason: 'Algorithmic downgrade to wallet tier'
        }
      },
      {
        condition: () => true,
        consequence: {
          type: 'indicator' as const,
          key: 'resolver_scrutiny',
          change: 20,
          reason: 'Audit triggered by anonymous complaint'
        }
      }
    ];
    
    const valid = retaliations.filter(r => r.condition());
    return [valid[Math.floor(Math.random() * valid.length)].consequence];
  }
}
```

---

## Phase 5: Meta Progression System

**Goal:** Implement unlocks, templates, and precedents that persist across runs. This is what makes "failure forward" work.

**Dependencies:** Phases 1-4

### Success Criteria
- [ ] Unlocks persist in localStorage/save file
- [ ] Templates modify starting resources or available actions
- [ ] Precedents weaken specific enemy mechanics
- [ ] Losing a run still grants at least one unlock
- [ ] Players feel invested in long-term progress

### 5.1 Unlock System

```typescript
// src/systems/meta/UnlockSystem.ts

export interface Unlock {
  id: string;
  name: string;
  description: string;
  
  // What grants this unlock
  condition: UnlockCondition;
  
  // What it does
  effect: UnlockEffect;
  
  // Flavor
  icon: string;
  unlockMessage: string;
}

export interface UnlockCondition {
  type: 'flag' | 'stat' | 'ending' | 'action';
  requirement: any;
}

export interface UnlockEffect {
  type: 'template' | 'precedent' | 'character' | 'action' | 'puzzle_modifier';
  data: any;
}

export const UNLOCKS: Unlock[] = [
  // TEMPLATES (modify starting conditions)
  {
    id: 'organized_start',
    name: 'Community Network',
    description: 'Start with +3 Capacity',
    condition: { type: 'stat', requirement: { key: 'community_meetings_held', value: 5 } },
    effect: { type: 'template', data: { startingCapacity: 3 } },
    icon: 'icon_network',
    unlockMessage: 'Your organizing work has built lasting infrastructure.'
  },
  {
    id: 'media_savvy',
    name: 'Media Training',
    description: 'Start with Momentum 2 instead of 0',
    condition: { type: 'stat', requirement: { key: 'media_mentions', value: 3 } },
    effect: { type: 'template', data: { startingMomentum: 2 } },
    icon: 'icon_media',
    unlockMessage: 'You\'ve learned how to shape the narrative.'
  },
  
  // PRECEDENTS (weaken enemy mechanics)
  {
    id: 'disclosure_precedent',
    name: 'Disclosure Precedent',
    description: 'Audit trails now take 1 day instead of 2',
    condition: { type: 'ending', requirement: { endingId: 'win_audit_case' } },
    effect: { type: 'precedent', data: { auditDays: 1 } },
    icon: 'icon_gavel',
    unlockMessage: 'Your case set a precedent. The system must now respond faster.'
  },
  {
    id: 'standing_floor',
    name: 'Tier Protection',
    description: 'Standing cannot drop below 1',
    condition: { type: 'stat', requirement: { key: 'standing_zero_survivals', value: 2 } },
    effect: { type: 'precedent', data: { standingFloor: 1 } },
    icon: 'icon_shield',
    unlockMessage: 'You\'ve proven that exile can be reversed.'
  },
  
  // CHARACTERS
  {
    id: 'unlock_verifier',
    name: 'The Verifier',
    description: 'A new ally who can authenticate evidence',
    condition: { type: 'flag', requirement: { key: 'met_verifier', value: true } },
    effect: { type: 'character', data: { characterId: 'verifier' } },
    icon: 'icon_verify',
    unlockMessage: 'Someone on the inside wants to help.'
  },
  
  // FAILURE-FORWARD UNLOCKS
  {
    id: 'learn_from_loss',
    name: 'Hard Lessons',
    description: 'Gain +1 starting Evidence after any loss',
    condition: { type: 'stat', requirement: { key: 'runs_lost', value: 1 } },
    effect: { type: 'template', data: { startingEvidence: 10 } },
    icon: 'icon_lesson',
    unlockMessage: 'Every failure teaches something.'
  }
];

export class UnlockSystem {
  private unlockedIds: Set<string>;
  
  constructor() {
    this.unlockedIds = new Set(this.loadUnlocks());
  }
  
  checkForNewUnlocks(gameState: GameState, runStats: RunStats): Unlock[] {
    const newUnlocks: Unlock[] = [];
    
    for (const unlock of UNLOCKS) {
      if (this.unlockedIds.has(unlock.id)) continue;
      
      if (this.evaluateCondition(unlock.condition, gameState, runStats)) {
        this.unlockedIds.add(unlock.id);
        newUnlocks.push(unlock);
      }
    }
    
    if (newUnlocks.length > 0) {
      this.saveUnlocks();
    }
    
    return newUnlocks;
  }
  
  getActiveEffects(): UnlockEffect[] {
    return Array.from(this.unlockedIds)
      .map(id => UNLOCKS.find(u => u.id === id))
      .filter(Boolean)
      .map(u => u!.effect);
  }
  
  applyTemplates(baseState: GameState): GameState {
    const templates = this.getActiveEffects()
      .filter(e => e.type === 'template');
    
    let modified = { ...baseState };
    
    for (const template of templates) {
      if (template.data.startingCapacity) {
        modified.capacity += template.data.startingCapacity;
      }
      if (template.data.startingMomentum) {
        modified.momentum = template.data.startingMomentum;
      }
      if (template.data.startingEvidence) {
        modified.flags.set('evidence_collected', template.data.startingEvidence);
      }
    }
    
    return modified;
  }
  
  private loadUnlocks(): string[] {
    const saved = localStorage.getItem('settlement_unlocks');
    return saved ? JSON.parse(saved) : [];
  }
  
  private saveUnlocks() {
    localStorage.setItem('settlement_unlocks', JSON.stringify(Array.from(this.unlockedIds)));
  }
}
```

### 5.2 Run Statistics Tracking

```typescript
// src/systems/meta/RunStats.ts

export interface RunStats {
  // Identifiers
  runId: string;
  startedAt: Date;
  endedAt: Date;
  
  // Outcome
  outcome: 'victory' | 'defeat' | 'abandoned';
  endingId?: string;
  daysCompleted: number;
  
  // Cumulative stats
  totalEvidenceCollected: number;
  totalChainsCompleted: number;
  puzzlesWon: number;
  puzzlesLost: number;
  actionsTotal: number;
  actionsByCategory: Map<string, number>;
  
  // Peak values
  peakCapacity: number;
  peakMomentum: number;
  lowestStanding: number;
  
  // Flags for unlock conditions
  standingZeroSurvivals: number;
  communityMeetingsHeld: number;
  mediaMentions: number;
  
  // Choices made (for narrative tracking)
  majorChoices: { sceneId: string, choiceId: string }[];
}

export class RunStatsTracker {
  private stats: RunStats;
  
  constructor() {
    this.stats = this.createNewRun();
  }
  
  recordAction(action: Action) {
    this.stats.actionsTotal++;
    const count = this.stats.actionsByCategory.get(action.category) || 0;
    this.stats.actionsByCategory.set(action.category, count + 1);
    
    // Special tracking
    if (action.id === 'community_meeting') {
      this.stats.communityMeetingsHeld++;
    }
  }
  
  recordPuzzleResult(result: TurnResult) {
    if (result.status === 'victory') {
      this.stats.puzzlesWon++;
    } else {
      this.stats.puzzlesLost++;
    }
    
    this.stats.totalEvidenceCollected += result.reward?.evidence || 0;
    this.stats.totalChainsCompleted += result.chainsCompleted || 0;
  }
  
  recordResourceChange(resource: string, oldValue: number, newValue: number) {
    if (resource === 'capacity' && newValue > this.stats.peakCapacity) {
      this.stats.peakCapacity = newValue;
    }
    if (resource === 'momentum' && newValue > this.stats.peakMomentum) {
      this.stats.peakMomentum = newValue;
    }
    if (resource === 'standing') {
      if (newValue < this.stats.lowestStanding) {
        this.stats.lowestStanding = newValue;
      }
      if (oldValue === 0 && newValue > 0) {
        this.stats.standingZeroSurvivals++;
      }
    }
  }
  
  recordChoice(sceneId: string, choiceId: string) {
    this.stats.majorChoices.push({ sceneId, choiceId });
  }
  
  finalizeRun(outcome: 'victory' | 'defeat' | 'abandoned', endingId?: string) {
    this.stats.outcome = outcome;
    this.stats.endingId = endingId;
    this.stats.endedAt = new Date();
    
    // Save to history
    this.saveRunToHistory(this.stats);
    
    return this.stats;
  }
  
  private saveRunToHistory(stats: RunStats) {
    const history = JSON.parse(localStorage.getItem('settlement_run_history') || '[]');
    history.push(stats);
    
    // Keep last 50 runs
    if (history.length > 50) {
      history.shift();
    }
    
    localStorage.setItem('settlement_run_history', JSON.stringify(history));
  }
}
```

---

## Phase 6: Boss Encounter — Resolver Hearing

**Goal:** Implement the slice's boss encounter as a template for future bosses. This demonstrates capture/retaliation and provides a climactic test of player progress.

**Dependencies:** Phases 1-5

### Success Criteria
- [ ] Hearing has clear evidence/threshold requirement
- [ ] Time pressure creates tension
- [ ] Multiple outcomes (win clean, win dirty, lose-forward)
- [ ] Boss modifies puzzle rules in meaningful ways
- [ ] Beating the boss feels earned

### 6.1 Boss Definition

```typescript
// src/systems/boss/types.ts

export interface BossEncounter {
  id: string;
  name: string;
  description: string;
  
  // Entry conditions
  triggerConditions: Condition[];
  
  // Narrative wrapper
  introScene: string;
  victoryScene: string;
  defeatScene: string;
  dirtyVictoryScene?: string;
  
  // Puzzle modifications
  puzzleModifiers: NightModifier[];
  
  // Win conditions (beyond base puzzle)
  specialConditions: BossCondition[];
  
  // Time limit
  turnLimit: number;
  
  // Rewards by outcome
  rewards: {
    clean: UnlockEffect[];
    dirty: UnlockEffect[];
    loss: UnlockEffect[];
  };
}

export interface BossCondition {
  type: 'evidence_threshold' | 'no_contested_chains' | 'min_chain_length' | 'no_taint_spread';
  value: any;
  description: string;
  failureConsequence: string;
}

// The Resolver Hearing
export const RESOLVER_HEARING: BossEncounter = {
  id: 'resolver_hearing_1',
  name: 'Resolver Hearing',
  description: 'Present your evidence before the algorithmic arbiter. Contradictions will be exploited.',
  
  triggerConditions: [
    { type: 'flag', key: 'hearing_scheduled', operator: '==', value: true }
  ],
  
  introScene: 'boss_hearing_intro',
  victoryScene: 'boss_hearing_victory',
  defeatScene: 'boss_hearing_defeat',
  dirtyVictoryScene: 'boss_hearing_dirty',
  
  puzzleModifiers: [
    { type: 'extra_taint_sources', value: 2 },
    { type: 'reduced_turns', value: 5 },
    { type: 'new_hazard', value: 'contradiction_detector' }
  ],
  
  specialConditions: [
    {
      type: 'evidence_threshold',
      value: 100,
      description: 'Collect at least 100 evidence to make your case',
      failureConsequence: 'Case dismissed for insufficient evidence'
    },
    {
      type: 'no_contested_chains',
      value: true,
      description: 'Win with no contested chains for a clean victory',
      failureConsequence: 'Opposing counsel exploits contested evidence'
    }
  ],
  
  turnLimit: 15,
  
  rewards: {
    clean: [
      { type: 'precedent', data: { id: 'disclosure_precedent' } },
      { type: 'template', data: { startingStanding: 1 } }
    ],
    dirty: [
      { type: 'template', data: { startingEvidence: 25 } }
    ],
    loss: [
      { type: 'character', data: { characterId: 'insider_contact' } }
    ]
  }
};
```

### 6.2 Boss Puzzle Runner

```typescript
// src/systems/boss/BossPuzzleRunner.ts

export class BossPuzzleRunner extends PuzzleRunner {
  private boss: BossEncounter;
  private conditionResults: Map<string, boolean>;
  
  constructor(scene: Phaser.Scene, level: LevelDefinition, boss: BossEncounter) {
    super(scene, level);
    this.boss = boss;
    this.conditionResults = new Map();
    
    // Apply boss modifiers
    this.applyBossModifiers();
  }
  
  private applyBossModifiers() {
    const applicator = new NightModifierApplicator();
    this.state = applicator.applyModifiers(this.state, this.boss.puzzleModifiers);
    
    // Override turn limit
    this.state.maxTurns = this.boss.turnLimit;
  }
  
  protected evaluateGameState(): TurnResult {
    const baseResult = super.evaluateGameState();
    
    if (baseResult.status === 'continue') {
      return baseResult;
    }
    
    // Evaluate special conditions
    for (const condition of this.boss.specialConditions) {
      this.conditionResults.set(condition.type, this.evaluateBossCondition(condition));
    }
    
    // Determine outcome type
    const outcome = this.determineBossOutcome(baseResult);
    
    return {
      ...baseResult,
      bossOutcome: outcome,
      conditionResults: this.conditionResults
    };
  }
  
  private evaluateBossCondition(condition: BossCondition): boolean {
    switch (condition.type) {
      case 'evidence_threshold':
        return this.state.evidenceCollected >= condition.value;
        
      case 'no_contested_chains':
        const chains = this.chainDetector.findAllChains(this.gridManager.grid);
        return !chains.some(c => c.isContested);
        
      case 'min_chain_length':
        const allChains = this.chainDetector.findAllChains(this.gridManager.grid);
        return allChains.some(c => c.tiles.length >= condition.value);
        
      default:
        return true;
    }
  }
  
  private determineBossOutcome(baseResult: TurnResult): BossOutcome {
    // Lost the puzzle entirely
    if (baseResult.status === 'timeout' || baseResult.status === 'corrupted') {
      return 'loss';
    }
    
    // Check required conditions
    const evidenceMet = this.conditionResults.get('evidence_threshold') ?? true;
    if (!evidenceMet) {
      return 'loss';
    }
    
    // Check clean victory conditions
    const cleanConditions = this.boss.specialConditions
      .filter(c => c.type !== 'evidence_threshold');
    const allCleanMet = cleanConditions.every(c => this.conditionResults.get(c.type));
    
    if (allCleanMet) {
      return 'clean';
    }
    
    return 'dirty';
  }
}
```

### 6.3 Boss UI Additions

```typescript
// src/ui/components/BossUI.ts

export class BossUI extends Phaser.GameObjects.Container {
  private conditionDisplays: Map<string, ConditionDisplay>;
  private turnCounter: TurnCounterUI;
  private bossPortrait: Phaser.GameObjects.Sprite;
  
  constructor(scene: Phaser.Scene, boss: BossEncounter) {
    super(scene, 0, 0);
    
    // Boss portrait and name
    this.bossPortrait = scene.add.sprite(100, 100, 'boss_resolver');
    this.add(this.bossPortrait);
    
    // Turn counter with emphasis
    this.turnCounter = new TurnCounterUI(scene, boss.turnLimit);
    this.turnCounter.setPosition(640, 50);
    this.add(this.turnCounter);
    
    // Special conditions display
    this.conditionDisplays = new Map();
    boss.specialConditions.forEach((condition, index) => {
      const display = new ConditionDisplay(scene, condition);
      display.setPosition(50, 200 + index * 60);
      this.conditionDisplays.set(condition.type, display);
      this.add(display);
    });
  }
  
  updateCondition(type: string, met: boolean, current?: number, required?: number) {
    const display = this.conditionDisplays.get(type);
    if (display) {
      display.update(met, current, required);
    }
  }
  
  updateTurns(remaining: number) {
    this.turnCounter.setRemaining(remaining);
    
    // Urgency feedback
    if (remaining <= 3) {
      this.turnCounter.setPanic(true);
    }
  }
}

export class ConditionDisplay extends Phaser.GameObjects.Container {
  private icon: Phaser.GameObjects.Sprite;
  private text: Phaser.GameObjects.Text;
  private progressBar: Phaser.GameObjects.Graphics;
  
  update(met: boolean, current?: number, required?: number) {
    if (met) {
      this.icon.setTint(0x4ade80);  // Green
      this.text.setColor('#4ade80');
    } else {
      this.icon.setTint(0xfbbf24);  // Yellow
    }
    
    if (current !== undefined && required !== undefined) {
      this.drawProgress(current / required);
    }
  }
}
```

---

## Phase 7: Vertical Slice Assembly

**Goal:** Combine all systems into the 30-minute playable slice defined in your design docs.

**Dependencies:** All previous phases

### Success Criteria
- [ ] Complete playthrough takes 25-35 minutes
- [ ] All three endings are reachable
- [ ] Players can explain resources after one loop
- [ ] Playtesters replay voluntarily
- [ ] Critique lands without exposition dumps
- [ ] Board is readable at a glance

### 7.1 Slice Content Checklist

```
SETTING
├── Neighborhood: Eastside District
├── Wallet-state: "StandardAccess" tier system
└── Corporate presence: "Clarity Utilities" (data/power/water)

CHARACTERS
├── Protagonist: [player-defined name]
├── Maya Reyes: Organizer (ally)
├── The Verifier: Data auditor (unlockable)
└── Skeptic Friend: "Jordan" (grounding voice)

NARRATIVE SCENES (10-14 total)
├── Day 1
│   ├── [01] Morning briefing + Board tutorial
│   ├── [02] Hub intro + meet Maya
│   ├── [03] First case briefing (Delgados)
│   └── [04] Night 1 setup
├── Day 2
│   ├── [05] Morning consequences
│   ├── [06] Action scene A (investigate)
│   ├── [07] Action scene B (organize)
│   └── [08] Night 2 setup / hearing prep
├── Resolution
│   ├── [09] Hearing intro
│   ├── [10] Victory clean
│   ├── [11] Victory dirty
│   └── [12] Defeat forward

PUZZLE FLOORS
├── Tutorial floor (Night 1): 2 hazards, generous turns
├── Standard floor (Night 1 late): 3 hazards, normal turns
└── Pressure floor (Night 2 / Hearing): Timed, boss conditions

BACKGROUNDS (3)
├── bg_street: Eastside main drag
├── bg_hub: Community center interior
└── bg_hearing: Resolver arbitration room

UI SCREENS
├── Board screen
├── Action select
├── Puzzle play
└── Reward/resolution
```

### 7.2 Scene Flow Diagram

```
                    ┌─────────────────┐
                    │   BOOT/MENU     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  DAY 1 MORNING  │
                    │  - Board intro  │
                    │  - 3 indicators │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   DAY 1 DAY     │
                    │  - 2 actions    │
                    │  - Meet NPCs    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   NIGHT 1       │
                    │  - Tutorial     │
                    │  - Standard     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  DAY 2 MORNING  │
                    │  - Consequences │
                    │  - 5 indicators │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   DAY 2 DAY     │
                    │  - 2 actions    │
                    │  - Hearing prep │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   NIGHT 2       │
                    │  - Boss prep    │
                    │  - Hearing      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │  WIN CLEAN   │ │  WIN DIRTY   │ │ LOSE FORWARD │
      │  - Precedent │ │  - Partial   │ │  - Unlock    │
      │  - Tease Arc2│ │  - Costs     │ │  - New ally  │
      └──────────────┘ └──────────────┘ └──────────────┘
```

### 7.3 Tutorial Implementation

```typescript
// src/systems/tutorial/TutorialSystem.ts

export interface TutorialStep {
  id: string;
  trigger: TutorialTrigger;
  content: TutorialContent;
  completion: TutorialCompletion;
}

export interface TutorialTrigger {
  type: 'scene_enter' | 'action' | 'state_change' | 'time';
  data: any;
}

export interface TutorialContent {
  type: 'highlight' | 'popup' | 'forced_action' | 'narrative';
  target?: string;
  text: string;
  position?: { x: number, y: number };
}

export interface TutorialCompletion {
  type: 'click_target' | 'any_click' | 'action_complete' | 'auto';
  data?: any;
}

export const SLICE_TUTORIAL: TutorialStep[] = [
  // Board Tutorial
  {
    id: 'board_intro',
    trigger: { type: 'scene_enter', data: { sceneId: 'day1_morning' } },
    content: {
      type: 'highlight',
      target: 'board_panel',
      text: 'This is the Board. It shows the forces working for and against you.'
    },
    completion: { type: 'any_click' }
  },
  {
    id: 'indicator_explain',
    trigger: { type: 'action', data: { afterStep: 'board_intro' } },
    content: {
      type: 'highlight',
      target: 'indicator_0',
      text: 'Each indicator affects your options. Hover to see what it does.'
    },
    completion: { type: 'click_target', data: { target: 'indicator_0' } }
  },
  {
    id: 'resources_intro',
    trigger: { type: 'action', data: { afterStep: 'indicator_explain' } },
    content: {
      type: 'highlight',
      target: 'resource_bar',
      text: 'Capacity, Standing, Momentum. These are your fuel. Spend them wisely.'
    },
    completion: { type: 'any_click' }
  },
  
  // Puzzle Tutorial
  {
    id: 'puzzle_goal',
    trigger: { type: 'scene_enter', data: { sceneId: 'night_1' } },
    content: {
      type: 'popup',
      text: 'Connect evidence tiles to the target. Complete chains to collect proof.',
      position: { x: 640, y: 360 }
    },
    completion: { type: 'any_click' }
  },
  {
    id: 'puzzle_hand',
    trigger: { type: 'action', data: { afterStep: 'puzzle_goal' } },
    content: {
      type: 'highlight',
      target: 'hand_display',
      text: 'Your hand. Click a tile, then click the grid to place it.'
    },
    completion: { type: 'action_complete', data: { action: 'place_tile' } }
  },
  {
    id: 'puzzle_taint',
    trigger: { type: 'state_change', data: { event: 'taint_spread' } },
    content: {
      type: 'highlight',
      target: 'taint_source',
      text: 'Corruption spreads. Tiles it touches become contested—worth less and vulnerable.'
    },
    completion: { type: 'any_click' }
  },
  {
    id: 'puzzle_chain',
    trigger: { type: 'state_change', data: { event: 'chain_complete' } },
    content: {
      type: 'popup',
      text: 'Chain complete! Evidence collected. Clear the grid before corruption wins.',
      position: { x: 640, y: 360 }
    },
    completion: { type: 'auto', data: { delay: 2000 } }
  }
];

export class TutorialSystem {
  private steps: TutorialStep[];
  private completedSteps: Set<string>;
  private currentStep: TutorialStep | null = null;
  
  constructor(steps: TutorialStep[]) {
    this.steps = steps;
    this.completedSteps = new Set();
  }
  
  checkTriggers(event: { type: string, data: any }) {
    for (const step of this.steps) {
      if (this.completedSteps.has(step.id)) continue;
      if (this.currentStep) continue;
      
      if (this.matchesTrigger(step.trigger, event)) {
        this.startStep(step);
        break;
      }
    }
  }
  
  private startStep(step: TutorialStep) {
    this.currentStep = step;
    this.displayContent(step.content);
    
    if (step.completion.type === 'auto') {
      setTimeout(() => this.completeStep(), step.completion.data?.delay || 1000);
    }
  }
  
  completeStep() {
    if (!this.currentStep) return;
    
    this.completedSteps.add(this.currentStep.id);
    this.hideContent();
    this.currentStep = null;
  }
}
```

### 7.4 Playtest Protocol

```markdown
## Slice Playtest Protocol

### Pre-Session
- Fresh browser (clear localStorage)
- Screen recording on
- Note-taking ready

### During Session (observe, don't help)
- Note confusion points
- Note delight moments
- Note skip/impatience moments
- Track time at each phase

### Post-Session Questions

**Comprehension (target: all correct after one loop)**
1. What are the three resources? What do they do?
2. What was your goal in the puzzle?
3. How did you win/lose?
4. What would you do differently next run?

**Engagement**
5. Would you play again right now? Why/why not?
6. What was the most interesting decision you made?
7. What was confusing?
8. What was frustrating?

**Theme (target: felt, not explained)**
9. What is this game about?
10. Did anything feel unfair? Was that intentional?
11. Did you feel like you could make a difference?

### Success Metrics
- Time to complete: 25-35 minutes ✓
- Can name 3 resources: 100% ✓
- Can describe loop: 100% ✓
- Would replay: >60% ✓
- Understood theme without exposition: >80% ✓
- Found puzzle fun standalone: >70% ✓
```

---

## Phase 8: Content Pipeline & Tooling

**Goal:** Build tools to efficiently author and test narrative content, puzzle levels, and balancing.

**Dependencies:** Phases 1-5 (tooling supports content creation for Phase 7)

### Success Criteria
- [ ] Scenes can be written in YAML and hot-reloaded
- [ ] Puzzle levels can be designed in a visual tool or simple format
- [ ] Balance values are centralized and tweakable
- [ ] Playtest mode allows jumping to any scene/puzzle

### 8.1 Content Hot Reload

```typescript
// src/tools/dev/HotReload.ts

export class ContentHotReload {
  private watcher: FileWatcher;
  private sceneManager: Phaser.Scenes.SceneManager;
  
  constructor(sceneManager: Phaser.Scenes.SceneManager) {
    this.sceneManager = sceneManager;
    
    if (process.env.NODE_ENV === 'development') {
      this.setupWatcher();
    }
  }
  
  private setupWatcher() {
    // Watch scene files
    this.watchDirectory('src/data/scenes', (file) => {
      console.log(`Scene changed: ${file}`);
      this.reloadScene(file);
    });
    
    // Watch puzzle definitions
    this.watchDirectory('src/data/puzzles', (file) => {
      console.log(`Puzzle changed: ${file}`);
      this.reloadPuzzle(file);
    });
    
    // Watch config
    this.watchFile('src/config.ts', () => {
      console.log('Config changed—refresh required');
    });
  }
  
  private async reloadScene(file: string) {
    const sceneId = this.fileToSceneId(file);
    const newData = await this.loadYAML(file);
    
    // Update cache
    SceneCache.set(sceneId, newData);
    
    // If currently viewing this scene, soft-reload
    const currentScene = this.sceneManager.getScene('DayScene') as DayScene;
    if (currentScene?.currentSceneId === sceneId) {
      currentScene.reloadDialogue();
    }
  }
}
```

### 8.2 Debug Panel

```typescript
// src/tools/dev/DebugPanel.ts

export class DebugPanel extends Phaser.GameObjects.Container {
  private visible: boolean = false;
  
  constructor(scene: Phaser.Scene) {
    super(scene, 0, 0);
    
    // Toggle with backtick
    scene.input.keyboard.on('keydown-BACKQUOTE', () => this.toggle());
    
    this.createPanel();
  }
  
  private createPanel() {
    // Background
    const bg = this.scene.add.rectangle(10, 10, 300, 400, 0x000000, 0.8);
    bg.setOrigin(0, 0);
    this.add(bg);
    
    // Jump to scene
    this.addButton(20, 50, 'Jump to Scene...', () => this.showSceneSelector());
    
    // Resource controls
    this.addSlider(20, 100, 'Capacity', 0, 20, (v) => this.setResource('capacity', v));
    this.addSlider(20, 140, 'Standing', 0, 10, (v) => this.setResource('standing', v));
    this.addSlider(20, 180, 'Momentum', 0, 20, (v) => this.setResource('momentum', v));
    
    // Indicator controls
    this.addButton(20, 230, 'Max All Indicators', () => this.maxIndicators());
    this.addButton(20, 270, 'Min All Indicators', () => this.minIndicators());
    
    // Puzzle controls
    this.addButton(20, 320, 'Skip to Night', () => this.skipToNight());
    this.addButton(20, 360, 'Win Puzzle', () => this.winPuzzle());
    
    // Unlock controls
    this.addButton(20, 400, 'Unlock All', () => this.unlockAll());
    this.addButton(20, 440, 'Reset Unlocks', () => this.resetUnlocks());
    
    this.setVisible(false);
  }
  
  private showSceneSelector() {
    const scenes = SceneCache.getAllIds();
    // Show dropdown or list for selection
    // On select: this.jumpToScene(sceneId)
  }
  
  private jumpToScene(sceneId: string) {
    const narrativeRunner = this.scene.registry.get('narrativeRunner') as NarrativeRunner;
    narrativeRunner.loadScene(sceneId);
  }
}
```

### 8.3 Puzzle Level Editor (Simple Format)

```yaml
# src/data/puzzles/night1_tutorial.yaml

id: night1_tutorial
name: "First Night"
description: "Learn the basics"

# Grid setup
grid:
  cols: 8
  rows: 10
  
# Pre-placed elements
initial:
  targets:
    - { x: 7, y: 0 }
  taint_sources:
    - { x: 0, y: 9 }
  blocked:
    - { x: 3, y: 5 }
    - { x: 4, y: 5 }

# Win conditions
conditions:
  evidence_required: 50
  max_turns: 25

# Starting hand
hand:
  - evidence
  - evidence
  - evidence
  - testimony

# Hazards (unlocked gradually)
hazards:
  - type: taint_spread
    interval: 3
  # No fee gates in tutorial

# Modifiers from game state
state_modifiers:
  - condition: { type: 'indicator', key: 'heat', operator: '>', value: 50 }
    effect: { type: 'extra_taint_sources', value: 1 }
```

### 8.4 Balance Configuration

```typescript
// src/data/config/balance.ts

export const BALANCE = {
  // Resources
  resources: {
    capacity: {
      starting: 10,
      max: 25,
      perVolunteer: 2,
      actionCosts: {
        investigate: 1,
        organize: 2,
        operate: 1,
        recover: 0
      }
    },
    standing: {
      starting: 5,
      max: 10,
      min: 0,  // Can hit zero (exile state)
      recoveryRate: 1,  // Per "standing maintenance" action
      degradeThreshold: 30  // Heat level that causes standing loss
    },
    momentum: {
      starting: 0,
      max: 20,
      massActionThreshold: 10,
      decayRate: 1,  // Per day without momentum-building action
      retaliationProtection: 15  // Above this, reduced retaliation chance
    }
  },
  
  // Puzzle
  puzzle: {
    baseEvidence: 10,
    chainBonus: 1.5,  // Multiplier for longer chains
    contestedPenalty: 0.6,  // Multiplier for contested chains
    taintSpreadInterval: 2,
    minChainLength: 3,
    handSize: 4,
    handRefillRate: 2  // Tiles per turn
  },
  
  // Indicators
  indicators: {
    heat: {
      baseDecay: 5,  // Per day laying low
      actionIncrease: {
        investigate: 5,
        organize: 3,
        operate: 10,
        recover: -10
      },
      retaliationThreshold: 50
    },
    community_trust: {
      meetingBonus: 15,
      caseWinBonus: 10,
      caseLossPenalty: -5,
      decayRate: 2  // Per day of inaction
    }
  },
  
  // Boss
  boss: {
    resolver_hearing: {
      turnLimit: 15,
      evidenceThreshold: 100,
      extraTaintSources: 2,
      dirtyVictoryPenalty: { standing: -1 }
    }
  }
};

// Hot-reloadable in dev mode
if (process.env.NODE_ENV === 'development') {
  (window as any).BALANCE = BALANCE;
}
```

---

## Phase 9: Audio & Polish

**Goal:** Add audio feedback and visual polish to make the game feel responsive and atmospheric.

**Dependencies:** Phase 7 (after slice is playable)

### Success Criteria
- [ ] UI interactions have audio feedback
- [ ] Puzzle has satisfying sound design
- [ ] Music supports mood without overwhelming
- [ ] Transitions feel smooth
- [ ] Visual feedback is clear and immediate

### 9.1 Audio System

```typescript
// src/systems/audio/AudioManager.ts

export class AudioManager {
  private scene: Phaser.Scene;
  private musicTrack: Phaser.Sound.BaseSound | null = null;
  private ambienceTrack: Phaser.Sound.BaseSound | null = null;
  
  private sfxVolume: number = 0.7;
  private musicVolume: number = 0.4;
  
  // SFX categories
  private sfx = {
    ui: {
      click: 'sfx_click',
      hover: 'sfx_hover',
      confirm: 'sfx_confirm',
      cancel: 'sfx_cancel',
      error: 'sfx_error'
    },
    puzzle: {
      place: 'sfx_place',
      chain_start: 'sfx_chain_start',
      chain_complete: 'sfx_chain_complete',
      taint_spread: 'sfx_taint',
      contested: 'sfx_contested',
      victory: 'sfx_victory',
      defeat: 'sfx_defeat'
    },
    narrative: {
      choice_appear: 'sfx_choice',
      choice_select: 'sfx_select',
      character_enter: 'sfx_enter',
      notification: 'sfx_notify'
    },
    board: {
      indicator_up: 'sfx_up',
      indicator_down: 'sfx_down',
      resource_spend: 'sfx_spend',
      resource_gain: 'sfx_gain',
      retaliation: 'sfx_alarm'
    }
  };
  
  playSFX(category: keyof typeof this.sfx, sound: string) {
    const key = this.sfx[category]?.[sound];
    if (key) {
      this.scene.sound.play(key, { volume: this.sfxVolume });
    }
  }
  
  playMusic(key: string, fadeIn: boolean = true) {
    if (this.musicTrack) {
      if (fadeIn) {
        this.scene.tweens.add({
          targets: this.musicTrack,
          volume: 0,
          duration: 1000,
          onComplete: () => {
            this.musicTrack?.stop();
            this.startNewMusic(key, fadeIn);
          }
        });
      } else {
        this.musicTrack.stop();
        this.startNewMusic(key, false);
      }
    } else {
      this.startNewMusic(key, fadeIn);
    }
  }
  
  private startNewMusic(key: string, fadeIn: boolean) {
    this.musicTrack = this.scene.sound.add(key, {
      loop: true,
      volume: fadeIn ? 0 : this.musicVolume
    });
    this.musicTrack.play();
    
    if (fadeIn) {
      this.scene.tweens.add({
        targets: this.musicTrack,
        volume: this.musicVolume,
        duration: 2000
      });
    }
  }
  
  // "Market hum" - ambient layer that reflects game state
  updateAmbience(intensity: number) {
    // intensity 0-1 maps to ambience variations
    // Could be multiple layered tracks that crossfade
  }
}
```

### 9.2 Juice & Feedback

```typescript
// src/ui/effects/Juice.ts

export class Juice {
  private scene: Phaser.Scene;
  
  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }
  
  // Button press
  buttonPress(target: Phaser.GameObjects.GameObject) {
    this.scene.tweens.add({
      targets: target,
      scaleX: 0.95,
      scaleY: 0.95,
      duration: 50,
      yoyo: true
    });
  }
  
  // Resource change
  resourcePop(target: Phaser.GameObjects.Text, positive: boolean) {
    const color = positive ? 0x4ade80 : 0xf87171;
    target.setTint(color);
    
    this.scene.tweens.add({
      targets: target,
      scale: 1.2,
      duration: 100,
      yoyo: true,
      onComplete: () => target.clearTint()
    });
  }
  
  // Chain completion
  chainClear(tiles: Phaser.GameObjects.Sprite[]) {
    // Cascade effect
    tiles.forEach((tile, i) => {
      this.scene.time.delayedCall(i * 50, () => {
        this.scene.tweens.add({
          targets: tile,
          scale: 1.3,
          alpha: 0,
          duration: 200,
          ease: 'Back.easeIn'
        });
        
        // Particles
        this.sparkle(tile.x, tile.y);
      });
    });
  }
  
  // Taint spread
  taintPulse(tile: Phaser.GameObjects.Sprite) {
    tile.setTint(0x9333ea);
    
    this.scene.tweens.add({
      targets: tile,
      scale: 1.1,
      duration: 200,
      yoyo: true,
      repeat: 1,
      onComplete: () => tile.clearTint()
    });
  }
  
  // Screen shake (for retaliation, boss moments)
  shake(intensity: number = 0.01, duration: number = 200) {
    this.scene.cameras.main.shake(duration, intensity);
  }
  
  // Particles
  private sparkle(x: number, y: number) {
    const particles = this.scene.add.particles(x, y, 'particle', {
      speed: { min: 50, max: 150 },
      scale: { start: 0.5, end: 0 },
      lifespan: 500,
      quantity: 8,
      emitting: false
    });
    particles.explode();
    
    this.scene.time.delayedCall(600, () => particles.destroy());
  }
}
```

---

## Phase 10: Ship Preparation

**Goal:** Prepare the vertical slice for external playtesting and potential release.

### Success Criteria
- [ ] No crashes in 10 consecutive playthroughs
- [ ] Save/load works correctly
- [ ] Settings menu functional
- [ ] Build deploys cleanly
- [ ] Placeholder art is consistent in style

### 10.1 Save System

```typescript
// src/systems/core/SaveSystem.ts

export interface SaveData {
  version: string;
  timestamp: number;
  
  // Run state
  gameState: GameState;
  dayState: DayState;
  
  // Meta state
  unlocks: string[];
  runHistory: RunStats[];
  
  // Settings
  settings: GameSettings;
}

export class SaveSystem {
  private readonly SAVE_KEY = 'settlement_save';
  private readonly VERSION = '0.1.0';
  
  save(gameState: GameState, dayState: DayState): boolean {
    try {
      const data: SaveData = {
        version: this.VERSION,
        timestamp: Date.now(),
        gameState: this.serializeGameState(gameState),
        dayState: dayState,
        unlocks: Array.from(gameState.unlocks),
        runHistory: this.loadRunHistory(),
        settings: this.loadSettings()
      };
      
      localStorage.setItem(this.SAVE_KEY, JSON.stringify(data));
      return true;
    } catch (e) {
      console.error('Save failed:', e);
      return false;
    }
  }
  
  load(): SaveData | null {
    try {
      const raw = localStorage.getItem(this.SAVE_KEY);
      if (!raw) return null;
      
      const data = JSON.parse(raw) as SaveData;
      
      // Version migration if needed
      if (data.version !== this.VERSION) {
        return this.migrate(data);
      }
      
      return data;
    } catch (e) {
      console.error('Load failed:', e);
      return null;
    }
  }
  
  hasSave(): boolean {
    return localStorage.getItem(this.SAVE_KEY) !== null;
  }
  
  deleteSave() {
    localStorage.removeItem(this.SAVE_KEY);
  }
  
  private serializeGameState(state: GameState): any {
    return {
      ...state,
      flags: Array.from(state.flags.entries()),
      relationships: Array.from(state.relationships.entries()),
      unlocks: Array.from(state.unlocks)
    };
  }
  
  private deserializeGameState(data: any): GameState {
    return {
      ...data,
      flags: new Map(data.flags),
      relationships: new Map(data.relationships),
      unlocks: new Set(data.unlocks)
    };
  }
}
```

### 10.2 Settings

```typescript
// src/systems/core/Settings.ts

export interface GameSettings {
  // Audio
  masterVolume: number;
  musicVolume: number;
  sfxVolume: number;
  
  // Display
  uiScale: number;
  indicatorMode: 'lite' | 'full';
  
  // Accessibility
  textSpeed: 'slow' | 'normal' | 'fast' | 'instant';
  screenShake: boolean;
  highContrast: boolean;
  dyslexiaFont: boolean;
  
  // Gameplay
  confirmActions: boolean;
  showTutorials: boolean;
}

export const DEFAULT_SETTINGS: GameSettings = {
  masterVolume: 1.0,
  musicVolume: 0.5,
  sfxVolume: 0.7,
  
  uiScale: 1.0,
  indicatorMode: 'lite',
  
  textSpeed: 'normal',
  screenShake: true,
  highContrast: false,
  dyslexiaFont: false,
  
  confirmActions: true,
  showTutorials: true
};
```

### 10.3 Build Configuration

```typescript
// vite.config.ts

import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          phaser: ['phaser'],
          game: ['./src/main.ts']
        }
      }
    }
  },
  server: {
    port: 3000,
    open: true
  }
});
```

---

## Appendix A: File Naming Conventions

```
Scenes:       {act}_{day}_{event}.yaml       → act1_day1_morning.yaml
Puzzles:      {context}_{difficulty}.yaml    → night1_tutorial.yaml
Characters:   {name}.yaml                    → maya.yaml
Sprites:      {character}_{expression}.png   → maya_concerned.png
Backgrounds:  bg_{location}.png              → bg_hub.png
Audio:        {type}_{name}.{ext}            → sfx_chain_complete.ogg
```

---

## Appendix B: Development Milestones

| Milestone | Description | Validation |
|-----------|-------------|------------|
| M1: Puzzle Core | Grid, chains, taint—playable standalone | 5 players find it fun for 10+ min |
| M2: Board UI | Resources + indicators readable | 3 players explain correctly |
| M3: Narrative Shell | Dialogue + choices work | Can play through test scene |
| M4: Loop Integration | Day→Night→Resolution flows | Complete one full day |
| M5: Boss | Resolver hearing playable | All 3 outcomes reachable |
| M6: Vertical Slice | Full 30-min experience | Playtest protocol passes |
| M7: Polish | Audio, juice, save/load | No crashes in 10 runs |

---

## Appendix C: Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Puzzle isn't fun | Prototype in isolation first (Phase 1); iterate before story |
| Scope creep | MoSCoW list is law; features must justify against pillars |
| Solo dev burnout | Milestone-based progress; playable slice is always the goal |
| Balance issues | Centralized config; debug panel for rapid testing |
| Content bottleneck | Modular scenes; procedural elements where possible |

---

*Document generated for Settlement development. Update as design evolves.*
