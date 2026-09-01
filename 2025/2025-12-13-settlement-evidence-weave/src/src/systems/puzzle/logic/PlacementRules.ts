// Pure placement validation logic - no Phaser dependencies

import { Tile, TileType } from '../../types/puzzle';
import { Position } from '../types';

export interface PlacementContext {
  capacity: number;
  throttleZones: Array<{ position: Position; radius: number }>;
}

export class PlacementRules {
  
  /**
   * Check if a tile can be placed at the given position
   */
  canPlaceAt(
    grid: Tile[][],
    position: Position,
    tileType: TileType,
    context: PlacementContext
  ): { valid: boolean; reason?: string } {
    const { row, col } = position;
    
    // Bounds check
    if (row < 0 || row >= grid.length || col < 0 || col >= grid[0].length) {
      return { valid: false, reason: 'Out of bounds' };
    }
    
    const tile = grid[row][col];
    
    // Can't place on non-empty tiles (except we're replacing, but MVP doesn't allow that)
    if (tile.type !== 'empty') {
      return { valid: false, reason: 'Cell is not empty' };
    }
    
    // Can't place on taint sources
    if (tile.taintSource) {
      return { valid: false, reason: 'Cell is tainted' };
    }
    
    // Can't place on target tiles
    if (tile.type === 'target') {
      return { valid: false, reason: 'Cannot place on target' };
    }
    
    // Check throttle zones (costs capacity)
    if (this.isInThrottleZone(position, context.throttleZones)) {
      if (context.capacity < 1) {
        return { valid: false, reason: 'Insufficient capacity for throttle zone' };
      }
    }
    
    // Can't place tainted/blocked types directly (these are system-generated)
    if (tileType === 'tainted' || tileType === 'blocked' || tileType === 'target') {
      return { valid: false, reason: 'Cannot place system tile types' };
    }
    
    return { valid: true };
  }
  
  /**
   * Check if position is in a throttle zone
   */
  private isInThrottleZone(
    position: Position,
    throttleZones: Array<{ position: Position; radius: number }>
  ): boolean {
    for (const zone of throttleZones) {
      const distance = Math.abs(position.row - zone.position.row) + 
                       Math.abs(position.col - zone.position.col);
      if (distance <= zone.radius) {
        return true;
      }
    }
    return false;
  }
  
  /**
   * Calculate capacity cost for placement
   */
  getPlacementCost(
    position: Position,
    context: PlacementContext
  ): number {
    if (this.isInThrottleZone(position, context.throttleZones)) {
      return 1;
    }
    return 0;
  }
}

