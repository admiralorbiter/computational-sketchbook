// Pure taint spread logic - no Phaser dependencies

import { Tile } from '../../types/puzzle';
import { Position, TaintEvent } from '../types';

import { GAME_CONFIG } from '../../../config';

export class TaintSystem {
  private readonly TAINT_CONSUME_THRESHOLD = GAME_CONFIG.TAINT_CONSUME_THRESHOLD || 3;
  
  /**
   * Check if a tile type can be part of a chain (for contested logic)
   */
  private isChainableTile(tile: Tile | null): boolean {
    if (!tile) return false;
    return tile.type === 'evidence' || tile.type === 'testimony' || tile.type === 'document';
  }
  
  /**
   * Get orthogonal neighbors for taint spread
   */
  private getSpreadTargets(grid: Tile[][], source: Position): Tile[] {
    const directions = [
      { row: -1, col: 0 },  // up
      { row: 1, col: 0 },   // down
      { row: 0, col: -1 },  // left
      { row: 0, col: 1 }    // right
    ];
    
    const targets: Tile[] = [];
    
    for (const dir of directions) {
      const newRow = source.row + dir.row;
      const newCol = source.col + dir.col;
      
      if (newRow >= 0 && newRow < grid.length && 
          newCol >= 0 && newCol < grid[0].length) {
        const tile = grid[newRow][newCol];
        
        // Don't spread to blocked tiles or existing taint sources
        if (tile && tile.type !== 'blocked' && !tile.taintSource) {
          targets.push(tile);
        }
      }
    }
    
    return targets;
  }
  
  /**
   * Spread taint from active sources
   */
  spreadTaint(grid: Tile[][], sources: Position[]): TaintEvent[] {
    const events: TaintEvent[] = [];
    
    for (const source of sources) {
      const tile = grid[source.row]?.[source.col];
      if (!tile || !tile.taintSource) continue;
      
      const neighbors = this.getSpreadTargets(grid, source);
      
      for (const neighbor of neighbors) {
        if (neighbor.type === 'empty') {
          // Empty cells become tainted, but do NOT automatically become sources.
          // This avoids exponential flood-fill and makes taint readable/strategic.
          neighbor.type = 'tainted';
          neighbor.taintLevel = 1;
          neighbor.taintSource = false;
          events.push({
            type: 'spread',
            position: { row: neighbor.row, col: neighbor.col },
            affectedTiles: [neighbor]
          });
        } else if (this.isChainableTile(neighbor)) {
          // Evidence tiles become contested
          neighbor.taintLevel++;
          neighbor.contested = true;
          
          if (neighbor.taintLevel >= this.TAINT_CONSUME_THRESHOLD) {
            // Fully consumed - tile is destroyed
            neighbor.type = 'tainted';
            // Consumed evidence becomes a new source (pressure increases over time)
            neighbor.taintSource = true;
            events.push({
              type: 'consume',
              position: { row: neighbor.row, col: neighbor.col },
              affectedTiles: [neighbor]
            });
          } else {
            events.push({
              type: 'contest',
              position: { row: neighbor.row, col: neighbor.col },
              affectedTiles: [neighbor]
            });
          }
        }
      }
    }
    
    return events;
  }
  
  /**
   * Get all tainted tiles
   */
  getTaintedTiles(grid: Tile[][]): Tile[] {
    const tainted: Tile[] = [];
    
    for (let row = 0; row < grid.length; row++) {
      for (let col = 0; col < grid[row].length; col++) {
        const tile = grid[row][col];
        if (tile.taintSource || tile.type === 'tainted' || tile.taintLevel > 0) {
          tainted.push(tile);
        }
      }
    }
    
    return tainted;
  }
  
  /**
   * Check if board is overwhelmed by taint
   * Returns true if taint coverage exceeds threshold
   */
  isBoardOverwhelmed(grid: Tile[][], threshold?: number): boolean {
    const overwhelmThreshold = threshold ?? GAME_CONFIG.TAINT_OVERWHELM_THRESHOLD ?? 0.5;
    const totalCells = grid.length * grid[0].length;
    const taintedCount = this.getTaintedTiles(grid).length;
    return taintedCount / totalCells >= overwhelmThreshold;
  }
}

