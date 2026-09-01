import { describe, it, expect, beforeEach } from 'vitest';
import { PlacementRules } from '../PlacementRules';
import { Tile } from '../../../../types/puzzle';

describe('PlacementRules', () => {
  let rules: PlacementRules;
  let grid: Tile[][];
  
  beforeEach(() => {
    rules = new PlacementRules();
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
  
  it('should allow placement on empty tile', () => {
    const result = rules.canPlaceAt(
      grid,
      { row: 2, col: 2 },
      'evidence',
      { capacity: 10, throttleZones: [] }
    );
    
    expect(result.valid).toBe(true);
  });
  
  it('should reject placement on non-empty tile', () => {
    grid[2][2].type = 'evidence';
    
    const result = rules.canPlaceAt(
      grid,
      { row: 2, col: 2 },
      'testimony',
      { capacity: 10, throttleZones: [] }
    );
    
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('not empty');
  });
  
  it('should reject placement on tainted tile', () => {
    grid[2][2].type = 'tainted';
    grid[2][2].taintSource = true;
    
    const result = rules.canPlaceAt(
      grid,
      { row: 2, col: 2 },
      'evidence',
      { capacity: 10, throttleZones: [] }
    );
    
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('tainted');
  });
  
  it('should reject placement on target tile', () => {
    grid[2][2].type = 'target';
    
    const result = rules.canPlaceAt(
      grid,
      { row: 2, col: 2 },
      'evidence',
      { capacity: 10, throttleZones: [] }
    );
    
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('target');
  });
  
  it('should reject placement out of bounds', () => {
    const result = rules.canPlaceAt(
      grid,
      { row: 10, col: 10 },
      'evidence',
      { capacity: 10, throttleZones: [] }
    );
    
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('bounds');
  });
  
  it('should reject system tile types', () => {
    const result = rules.canPlaceAt(
      grid,
      { row: 2, col: 2 },
      'tainted',
      { capacity: 10, throttleZones: [] }
    );
    
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('system tile');
  });
  
  it('should require capacity in throttle zones', () => {
    const result = rules.canPlaceAt(
      grid,
      { row: 2, col: 2 },
      'evidence',
      {
        capacity: 0,
        throttleZones: [{ position: { row: 2, col: 2 }, radius: 1 }]
      }
    );
    
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('capacity');
  });
  
  it('should calculate placement cost in throttle zone', () => {
    const cost = rules.getPlacementCost(
      { row: 2, col: 2 },
      {
        capacity: 10,
        throttleZones: [{ position: { row: 2, col: 2 }, radius: 1 }]
      }
    );
    
    expect(cost).toBe(1);
  });
  
  it('should return zero cost outside throttle zones', () => {
    const cost = rules.getPlacementCost(
      { row: 0, col: 0 },
      {
        capacity: 10,
        throttleZones: [{ position: { row: 2, col: 2 }, radius: 1 }]
      }
    );
    
    expect(cost).toBe(0);
  });
});

