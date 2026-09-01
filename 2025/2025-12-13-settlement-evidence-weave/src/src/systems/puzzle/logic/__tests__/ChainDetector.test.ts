import { describe, it, expect, beforeEach } from 'vitest';
import { ChainDetector } from '../ChainDetector';
import { Tile } from '../../../../types/puzzle';
import { GAME_CONFIG } from '../../../../config';

describe('ChainDetector', () => {
  let detector: ChainDetector;
  let grid: Tile[][];
  
  beforeEach(() => {
    detector = new ChainDetector();
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
  
  it('should find no chains in empty grid', () => {
    const chains = detector.findAllChains(grid);
    expect(chains).toHaveLength(0);
  });
  
  it('should find single chain of evidence tiles', () => {
    // Create a horizontal chain
    grid[2][1].type = 'evidence';
    grid[2][2].type = 'evidence';
    grid[2][3].type = 'evidence';
    
    const chains = detector.findAllChains(grid);
    expect(chains).toHaveLength(1);
    expect(chains[0].tiles).toHaveLength(3);
  });
  
  it('should find multiple separate chains', () => {
    // Chain 1: horizontal
    grid[1][1].type = 'evidence';
    grid[1][2].type = 'evidence';
    
    // Chain 2: vertical
    grid[3][3].type = 'testimony';
    grid[4][3].type = 'testimony';
    
    const chains = detector.findAllChains(grid);
    expect(chains).toHaveLength(2);
  });
  
  it('should not include chains below minimum length', () => {
    grid[2][2].type = 'evidence';
    grid[2][3].type = 'evidence';
    // Only 2 tiles, below CHAIN_MIN_LENGTH (3)
    
    const chains = detector.findAllChains(grid);
    expect(chains).toHaveLength(0);
  });
  
  it('should detect chain completion at target', () => {
    // Create chain reaching target
    grid[0][2].type = 'target';
    // Chain is complete when adjacent to target (targets are not chainable)
    grid[1][2].type = 'evidence'; // adjacent to target
    grid[2][2].type = 'evidence';
    grid[3][2].type = 'evidence';
    
    const chains = detector.findAllChains(grid);
    expect(chains).toHaveLength(1);
    
    const isComplete = detector.checkChainCompletion(chains[0], [{ row: 0, col: 2 }]);
    expect(isComplete).toBe(true);
  });
  
  it('should calculate chain value correctly', () => {
    const chain = {
      id: 'test',
      tiles: [
        { row: 0, col: 0 },
        { row: 0, col: 1 },
        { row: 0, col: 2 }
      ],
      length: 3,
      isComplete: false,
      isContested: false,
      value: 0,
      composition: new Map([
        ['evidence', 3]
      ])
    };
    
    const value = detector.calculateChainValue(chain);
    expect(value).toBe(30); // 3 tiles * 10
  });
  
  it('should apply document bonus', () => {
    const chain = {
      id: 'test',
      tiles: [
        { row: 0, col: 0 },
        { row: 0, col: 1 }
      ],
      length: 2,
      isComplete: false,
      isContested: false,
      value: 0,
      composition: new Map([
        ['document', 2]
      ])
    };
    
    const value = detector.calculateChainValue(chain);
    expect(value).toBe(70); // (2 * 10) + (2 * 25)
  });
  
  it('should apply contested penalty', () => {
    const chain = {
      id: 'test',
      tiles: [
        { row: 0, col: 0 },
        { row: 0, col: 1 },
        { row: 0, col: 2 }
      ],
      length: 3,
      isComplete: false,
      isContested: true,
      value: 0,
      composition: new Map([
        ['evidence', 3]
      ])
    };
    
    const value = detector.calculateChainValue(chain);
    expect(value).toBe(18); // 30 * 0.6
  });
});

