// Pure chain detection logic - no Phaser dependencies

import { Tile, TileType, Chain } from '../../types/puzzle';
import { Position, ChainValidity } from '../types';
import { GAME_CONFIG } from '../../../config';

export class ChainDetector {
  
  /**
   * Check if a tile type can be part of a chain
   */
  private isChainableTile(tile: Tile | null): boolean {
    if (!tile) return false;
    return tile.type === 'evidence' || tile.type === 'testimony' || tile.type === 'document';
  }
  
  /**
   * Get orthogonal neighbors (no diagonals for clarity)
   */
  private getNeighbors(grid: Tile[][], row: number, col: number): Array<{ row: number; col: number }> {
    const neighbors: Array<{ row: number; col: number }> = [];
    const directions = [
      { row: -1, col: 0 },  // up
      { row: 1, col: 0 },   // down
      { row: 0, col: -1 },  // left
      { row: 0, col: 1 }    // right
    ];
    
    for (const dir of directions) {
      const newRow = row + dir.row;
      const newCol = col + dir.col;
      
      if (newRow >= 0 && newRow < grid.length && 
          newCol >= 0 && newCol < grid[0].length) {
        neighbors.push({ row: newRow, col: newCol });
      }
    }
    
    return neighbors;
  }
  
  /**
   * Flood fill to find all connected chainable tiles
   */
  private floodFillChain(
    grid: Tile[][],
    startRow: number,
    startCol: number,
    visited: Set<string>
  ): Chain {
    const chainId = `chain-${Date.now()}-${Math.random()}`;
    const tiles: Position[] = [];
    const composition = new Map<TileType, number>();
    let isContested = false;
    
    const queue: Position[] = [{ row: startRow, col: startCol }];
    
    while (queue.length > 0) {
      const pos = queue.shift()!;
      const key = `${pos.row},${pos.col}`;
      
      if (visited.has(key)) continue;
      
      const tile = grid[pos.row][pos.col];
      if (!this.isChainableTile(tile)) continue;
      
      visited.add(key);
      tiles.push(pos);
      
      // Update composition
      const count = composition.get(tile.type) || 0;
      composition.set(tile.type, count + 1);
      
      // Check if contested
      if (tile.contested || tile.taintLevel > 0) {
        isContested = true;
      }
      
      // Mark tile with chain ID
      tile.chainId = chainId;
      
      // Add neighbors
      const neighbors = this.getNeighbors(grid, pos.row, pos.col);
      for (const neighbor of neighbors) {
        const neighborKey = `${neighbor.row},${neighbor.col}`;
        if (!visited.has(neighborKey)) {
          const neighborTile = grid[neighbor.row][neighbor.col];
          if (this.isChainableTile(neighborTile)) {
            queue.push(neighbor);
          }
        }
      }
    }
    
    return {
      id: chainId,
      tiles,
      length: tiles.length,
      isComplete: false, // Will be checked separately
      isContested,
      value: 0, // Will be calculated separately
      composition
    };
  }
  
  /**
   * Find all chains in the grid
   */
  findAllChains(grid: Tile[][]): Chain[] {
    const visited = new Set<string>();
    const chains: Chain[] = [];
    
    for (let row = 0; row < grid.length; row++) {
      for (let col = 0; col < grid[row].length; col++) {
        const key = `${row},${col}`;
        const tile = grid[row][col];
        
        if (this.isChainableTile(tile) && !visited.has(key)) {
          const chain = this.floodFillChain(grid, row, col, visited);
          if (chain.tiles.length >= GAME_CONFIG.CHAIN_MIN_LENGTH) {
            chains.push(chain);
          }
        }
      }
    }
    
    return chains;
  }
  
  /**
   * Check if a chain reaches any target position
   */
  checkChainCompletion(chain: Chain, targetPositions: Position[]): boolean {
    // Targets are not chainable tiles, so completion is defined as:
    // any chain tile is orthogonally adjacent to any target position.
    return chain.tiles.some(tile =>
      targetPositions.some(target => {
        const manhattan = Math.abs(target.row - tile.row) + Math.abs(target.col - tile.col);
        return manhattan === 1;
      })
    );
  }
  
  /**
   * Calculate chain value based on composition and contamination
   */
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
  
  /**
   * Validate a chain
   */
  validateChain(chain: Chain, targetPositions: Position[]): ChainValidity {
    const isComplete = this.checkChainCompletion(chain, targetPositions);
    
    return {
      isValid: chain.length >= GAME_CONFIG.CHAIN_MIN_LENGTH,
      isComplete,
      isContested: chain.isContested,
      reason: !isComplete ? 'Chain does not reach a target (adjacent)' : undefined
    };
  }
}

