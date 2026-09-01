// Internal puzzle system types
// These align with the implementation details and may be more detailed than the public types

import { Tile, TileType, Chain } from '../../types/puzzle';

export type { Tile, TileType, Chain };

export interface Position {
  row: number;
  col: number;
}

export interface ChainValidity {
  isValid: boolean;
  isComplete: boolean;
  isContested: boolean;
  reason?: string;
}

export interface TaintEvent {
  type: 'spread' | 'consume' | 'contest';
  position: Position;
  affectedTiles: Tile[];
}

export interface TurnResult {
  status: 'continue' | 'victory' | 'timeout' | 'corrupted';
  reward?: number;
  evidenceCollected?: number;
}

export interface LevelDefinition {
  gridCols: number;
  gridRows: number;
  targetPositions: Position[];
  initialTaintSources: Position[];
  throttleZones: Array<{ position: Position; radius: number }>;
  evidenceRequired: number;
  maxTurns: number;
  handSize: number;
}

