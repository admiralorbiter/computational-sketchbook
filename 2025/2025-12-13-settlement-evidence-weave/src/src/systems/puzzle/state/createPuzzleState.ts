// Deterministic puzzle state initialization

import { PuzzleState, Tile, TileType } from '../../types/puzzle';
import { LevelDefinition } from '../types';
import { GAME_CONFIG } from '../../../config';
import { HandManager } from '../logic/HandManager';

export function createPuzzleState(
  level: LevelDefinition,
  rng: () => number
): PuzzleState {
  const handManager = new HandManager();
  
  // Create empty grid
  const grid: Tile[][] = [];
  for (let row = 0; row < level.gridRows; row++) {
    grid[row] = [];
    for (let col = 0; col < level.gridCols; col++) {
      grid[row][col] = {
        row,
        col,
        type: 'empty',
        chainId: null,
        taintLevel: 0,
        taintSource: false,
        contested: false,
        highlighted: false,
        animating: false
      };
    }
  }
  
  // Place target tiles
  for (const target of level.targetPositions) {
    if (target.row >= 0 && target.row < level.gridRows &&
        target.col >= 0 && target.col < level.gridCols) {
      grid[target.row][target.col].type = 'target';
    }
  }
  
  // Place initial taint sources
  for (const taintSource of level.initialTaintSources) {
    if (taintSource.row >= 0 && taintSource.row < level.gridRows &&
        taintSource.col >= 0 && taintSource.col < level.gridCols) {
      const tile = grid[taintSource.row][taintSource.col];
      tile.type = 'tainted';
      tile.taintSource = true;
      tile.taintLevel = 1;
    }
  }
  
  // Generate initial hand
  const initialHand: TileType[] = [];
  for (let i = 0; i < level.handSize; i++) {
    const tileType = handManager.refillHand(initialHand, 1, rng)[0];
    initialHand.push(tileType);
  }
  
  return {
    grid,
    turn: 0,
    turnsElapsed: 0,
    tilesPlaced: 0,
    chainsCompleted: 0,
    targetPositions: level.targetPositions,
    hand: initialHand,
    handSize: level.handSize,
    activeTaintSources: level.initialTaintSources,
    throttleZones: level.throttleZones.map(z => ({
      row: z.position.row,
      col: z.position.col,
      radius: z.radius
    })),
    evidenceCollected: 0,
    evidenceRequired: level.evidenceRequired,
    maxTurns: level.maxTurns,
    isComplete: false,
    isFailed: false
  };
}

/**
 * Create a default level definition for MVP testing
 */
export function createDefaultLevel(dayIndex: number = 1): LevelDefinition {
  return {
    gridCols: GAME_CONFIG.GRID_COLS,
    gridRows: GAME_CONFIG.GRID_ROWS,
    targetPositions: [
      { row: 0, col: Math.floor(GAME_CONFIG.GRID_COLS / 2) },
      { row: 0, col: Math.floor(GAME_CONFIG.GRID_COLS / 2) + 1 }
    ],
    initialTaintSources: [
      { row: GAME_CONFIG.GRID_ROWS - 1, col: 0 },
      { row: GAME_CONFIG.GRID_ROWS - 1, col: GAME_CONFIG.GRID_COLS - 1 }
    ],
    throttleZones: [], // MVP: no throttle zones initially
    evidenceRequired: 80 + (dayIndex * 15), // Scales with day (tuned for 10+ min play)
    maxTurns: 25 + (dayIndex * 3), // Reasonable turn limit
    handSize: 4
  };
}

