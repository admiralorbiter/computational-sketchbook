// Puzzle turn orchestration - mostly pure, emits events for rendering

import { PuzzleState, Tile } from '../../types/puzzle';
import { TurnResult, TaintEvent } from '../types';
import { ChainDetector } from './ChainDetector';
import { TaintSystem } from './TaintSystem';
import { PlacementRules, PlacementContext } from './PlacementRules';
import { HandManager } from './HandManager';
import { GAME_CONFIG } from '../../../config';

export class PuzzleRunner {
  private state: PuzzleState;
  private chainDetector: ChainDetector;
  private taintSystem: TaintSystem;
  private placementRules: PlacementRules;
  private handManager: HandManager;
  private rng: () => number;
  
  constructor(initialState: PuzzleState, rng: () => number) {
    this.state = { ...initialState };
    this.chainDetector = new ChainDetector();
    this.taintSystem = new TaintSystem();
    this.placementRules = new PlacementRules();
    this.handManager = new HandManager();
    this.rng = rng;
  }
  
  /**
   * Get current state (read-only)
   */
  getState(): Readonly<PuzzleState> {
    return { ...this.state };
  }
  
  /**
   * Attempt to place a tile
   */
  attemptPlacement(
    row: number,
    col: number,
    tileType: Tile['type'],
    capacity: number
  ): { success: boolean; reason?: string } {
    const context: PlacementContext = {
      capacity,
      throttleZones: this.state.throttleZones.map(z => ({
        position: { row: z.row, col: z.col },
        radius: z.radius
      }))
    };
    
    const validation = this.placementRules.canPlaceAt(
      this.state.grid,
      { row, col },
      tileType,
      context
    );
    
    if (!validation.valid) {
      return { success: false, reason: validation.reason };
    }
    
    // Place the tile
    const tile = this.state.grid[row][col];
    tile.type = tileType;
    tile.chainId = null; // Will be assigned by chain detection
    
    // Remove from hand
    this.state.hand = this.handManager.removeFromHand(this.state.hand, tileType);
    
    // Consume capacity if in throttle zone
    const cost = this.placementRules.getPlacementCost({ row, col }, context);
    // Note: capacity is managed externally, we just validate here
    
    this.state.tilesPlaced++;
    
    return { success: true };
  }
  
  /**
   * Run a turn (called after placement)
   * Returns turn result and taint events for animation
   * Note: Chain resolution should happen AFTER animation, so this method
   * expects chains to be resolved externally via resolveCompletedChains()
   */
  async runTurn(): Promise<{ result: TurnResult; taintEvents: TaintEvent[] }> {
    this.state.turnsElapsed++;
    this.state.turn++;
    
    // 1. Resolve any completed chains (should be called after animation)
    // This is now handled externally, but we keep the check here for safety
    const chains = this.chainDetector.findAllChains(this.state.grid);
    const completedChains = chains.filter(chain => 
      this.chainDetector.checkChainCompletion(chain, this.state.targetPositions)
    );
    
    // Resolve completed chains (if not already resolved)
    for (const chain of completedChains) {
      await this.resolveChain(chain);
    }
    
    // 2. Spread taint (every N turns)
    let taintEvents: TaintEvent[] = [];
    if (this.state.turnsElapsed % GAME_CONFIG.TAINT_SPREAD_INTERVAL === 0) {
      taintEvents = this.taintSystem.spreadTaint(
        this.state.grid,
        this.state.activeTaintSources.map(s => ({ row: s.row, col: s.col }))
      );
      
      // Update active taint sources (any tile that became a taint source)
      this.updateActiveTaintSources();
    }
    
    // 3. Refill hand
    this.state.hand = this.handManager.refillHand(
      this.state.hand,
      this.state.handSize,
      this.rng
    );
    
    // 4. Check win/loss
    return {
      result: this.evaluateGameState(),
      taintEvents
    };
  }
  
  /**
   * Get completed chains for this turn (for animation)
   */
  getCompletedChains(): import('../types').Chain[] {
    const chains = this.chainDetector.findAllChains(this.state.grid);
    return chains.filter(chain => 
      this.chainDetector.checkChainCompletion(chain, this.state.targetPositions)
    );
  }
  
  /**
   * Resolve completed chains (call after animation)
   */
  async resolveCompletedChains(): Promise<void> {
    const chains = this.chainDetector.findAllChains(this.state.grid);
    const completedChains = chains.filter(chain => 
      this.chainDetector.checkChainCompletion(chain, this.state.targetPositions)
    );
    
    for (const chain of completedChains) {
      await this.resolveChain(chain);
    }
  }
  
  /**
   * Resolve a completed chain
   */
  private async resolveChain(chain: import('../types').Chain): Promise<void> {
    const value = this.chainDetector.calculateChainValue(chain);
    this.state.evidenceCollected += value;
    
    // Clear chain tiles (set to empty)
    for (const tilePos of chain.tiles) {
      const tile = this.state.grid[tilePos.row][tilePos.col];
      tile.type = 'empty';
      tile.chainId = null;
      tile.contested = false;
      tile.taintLevel = 0;
    }
    
    this.state.chainsCompleted++;
  }
  
  /**
   * Update active taint sources list
   */
  private updateActiveTaintSources(): void {
    this.state.activeTaintSources = [];
    
    for (let row = 0; row < this.state.grid.length; row++) {
      for (let col = 0; col < this.state.grid[row].length; col++) {
        const tile = this.state.grid[row][col];
        if (tile.taintSource) {
          this.state.activeTaintSources.push({ row, col });
        }
      }
    }
  }
  
  /**
   * Evaluate current game state and return result
   */
  private evaluateGameState(): TurnResult {
    // Win: collected enough evidence
    if (this.state.evidenceCollected >= this.state.evidenceRequired) {
      this.state.isComplete = true;
      return {
        status: 'victory',
        reward: this.calculateReward(),
        evidenceCollected: this.state.evidenceCollected
      };
    }
    
    // Loss: out of turns
    if (this.state.turnsElapsed >= this.state.maxTurns) {
      this.state.isFailed = true;
      return {
        status: 'timeout',
        reward: this.calculatePartialReward(),
        evidenceCollected: this.state.evidenceCollected
      };
    }
    
    // Loss: grid overwhelmed by taint
    if (this.taintSystem.isBoardOverwhelmed(this.state.grid, 0.5)) {
      this.state.isFailed = true;
      return {
        status: 'corrupted',
        reward: this.calculatePartialReward(),
        evidenceCollected: this.state.evidenceCollected
      };
    }
    
    return { status: 'continue' };
  }
  
  /**
   * Calculate reward for victory
   */
  private calculateReward(): number {
    // Base reward + bonus for efficiency
    const baseReward = this.state.evidenceCollected;
    const efficiencyBonus = Math.max(0, (this.state.maxTurns - this.state.turnsElapsed) * 2);
    return baseReward + efficiencyBonus;
  }
  
  /**
   * Calculate partial reward for loss
   */
  private calculatePartialReward(): number {
    // Partial credit based on evidence collected
    return Math.floor(this.state.evidenceCollected * 0.5);
  }
}

