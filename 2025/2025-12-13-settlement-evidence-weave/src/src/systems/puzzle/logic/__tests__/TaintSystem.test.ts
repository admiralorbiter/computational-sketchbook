import { describe, it, expect, beforeEach } from 'vitest';
import { TaintSystem } from '../TaintSystem';
import { Tile } from '../../../../types/puzzle';

describe('TaintSystem', () => {
  let taintSystem: TaintSystem;
  let grid: Tile[][];
  
  beforeEach(() => {
    taintSystem = new TaintSystem();
    grid = [];
    
    // Create empty grid
    for (let row = 0; row < 5; row++) {
      grid[row] = [];
      for (let col = 0; col < 5; col++) {
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
  });
  
  it('should spread taint to empty neighbors', () => {
    // Set up taint source
    grid[2][2].type = 'tainted';
    grid[2][2].taintSource = true;
    grid[2][2].taintLevel = 1;
    
    const events = taintSystem.spreadTaint(grid, [{ row: 2, col: 2 }]);
    
    // Should spread to 4 orthogonal neighbors
    expect(events.length).toBeGreaterThan(0);
    
    // Check that neighbors became tainted
    const up = grid[1][2];
    const down = grid[3][2];
    const left = grid[2][1];
    const right = grid[2][3];
    
    // At least one should be tainted
    const taintedCount = [up, down, left, right].filter(t => t.type === 'tainted').length;
    expect(taintedCount).toBeGreaterThan(0);
  });
  
  it('should contest chainable tiles', () => {
    // Set up evidence tile
    grid[2][2].type = 'evidence';
    
    // Set up taint source nearby
    grid[2][1].type = 'tainted';
    grid[2][1].taintSource = true;
    grid[2][1].taintLevel = 1;
    
    const events = taintSystem.spreadTaint(grid, [{ row: 2, col: 1 }]);
    
    // Should contest the evidence tile
    expect(events.some(e => e.type === 'contest')).toBe(true);
    expect(grid[2][2].contested).toBe(true);
    expect(grid[2][2].taintLevel).toBeGreaterThan(0);
  });
  
  it('should consume tiles at threshold', () => {
    // Set up evidence tile with high taint level
    grid[2][2].type = 'evidence';
    grid[2][2].taintLevel = 2; // One away from threshold
    
    // Set up taint source
    grid[2][1].type = 'tainted';
    grid[2][1].taintSource = true;
    grid[2][1].taintLevel = 1;
    
    const events = taintSystem.spreadTaint(grid, [{ row: 2, col: 1 }]);
    
    // Should consume the tile
    const consumeEvent = events.find(e => e.type === 'consume');
    expect(consumeEvent).toBeDefined();
    expect(grid[2][2].type).toBe('tainted');
    expect(grid[2][2].taintSource).toBe(true);
  });
  
  it('should not spread to blocked tiles', () => {
    grid[2][2].type = 'tainted';
    grid[2][2].taintSource = true;
    grid[2][2].taintLevel = 1;
    
    // Block a neighbor
    grid[2][1].type = 'blocked';
    
    const events = taintSystem.spreadTaint(grid, [{ row: 2, col: 2 }]);
    
    // Should not spread to blocked tile
    expect(grid[2][1].type).toBe('blocked');
  });
  
  it('should detect overwhelmed board', () => {
    // Fill most of grid with taint
    for (let row = 0; row < 5; row++) {
      for (let col = 0; col < 5; col++) {
        if (row < 3) {
          grid[row][col].type = 'tainted';
          grid[row][col].taintSource = true;
        }
      }
    }
    
    const isOverwhelmed = taintSystem.isBoardOverwhelmed(grid, 0.5);
    expect(isOverwhelmed).toBe(true);
  });
});

