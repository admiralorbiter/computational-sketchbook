// Puzzle-related type definitions

export interface PuzzleState {
  // Grid state
  grid: Tile[][];
  
  // Current turn/phase
  turn: number;
  turnsElapsed: number;
  tilesPlaced: number;
  chainsCompleted: number;
  
  // Target positions (where chains must reach)
  targetPositions: Array<{ row: number; col: number }>;
  
  // Hand (tiles player can place)
  hand: TileType[];
  handSize: number;
  
  // Taint state
  activeTaintSources: Array<{ row: number; col: number }>;
  throttleZones: Array<{ row: number; col: number; radius: number }>;
  
  // Win/lose conditions
  evidenceCollected: number;
  evidenceRequired: number;
  maxTurns: number;
  isComplete: boolean;
  isFailed: boolean;
}

export interface Tile {
  row: number;
  col: number;
  type: TileType;
  
  // Chain membership
  chainId: string | null;
  
  // Corruption tracking
  taintLevel: number;        // 0 = clean, 3 = fully tainted
  taintSource: boolean;      // Does this spread taint?
  
  // Validity
  contested: boolean;        // Touched by taint but not consumed
  
  // Visual state (for rendering)
  highlighted: boolean;
  animating: boolean;
}

export type TileType = 
  | 'empty'
  | 'evidence'      // Base proof tile
  | 'testimony'     // Connects evidence
  | 'document'      // High-value, harder to place
  | 'tainted'       // Corrupted, spreads
  | 'blocked'       // Impassable (fee gate, throttle)
  | 'target';       // Chain destination

export interface Chain {
  id: string;
  tiles: Array<{ row: number; col: number }>;
  length: number;
  isComplete: boolean;      // Reaches a target
  isContested: boolean;     // Any tile has taint contact
  value: number;            // Score/reward value
  composition: Map<TileType, number>;  // For reward calculation
}

export interface Hazard {
  id: string;
  type: HazardType;
  position: { row: number; col: number };
  effect: string;
}

export type HazardType = 
  | 'taint'
  | 'block'
  | 'decay'
  | 'pressure';

export interface Indicator {
  id: string;
  name: string;
  value: number;
  trend: 'up' | 'down' | 'stable';
  description: string;
}

