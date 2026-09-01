import Phaser from 'phaser';
import { GameState } from '../../types/game';
import { GAME_CONFIG } from '../../config';

/**
 * Central game state container with pub/sub pattern for state changes.
 * Uses Phaser's EventEmitter for reactive updates across systems.
 */
export class GameStateManager extends Phaser.Events.EventEmitter {
  private state: GameState;

  constructor() {
    super();
    this.state = this.createInitialState();
  }

  /**
   * Create a fresh initial game state
   */
  private createInitialState(): GameState {
    return {
      currentDay: 1,
      phase: 'morning',
      capacity: GAME_CONFIG.STARTING_CAPACITY,
      standing: GAME_CONFIG.STARTING_STANDING,
      momentum: GAME_CONFIG.STARTING_MOMENTUM,
      puzzle: null,
      flags: new Map(),
      relationships: new Map(),
      unlocks: new Set(),
      templates: [],
      precedents: [],
      indicators: [],
    };
  }

  /**
   * Get the current game state (read-only access)
   */
  getState(): Readonly<GameState> {
    return { ...this.state };
  }

  /**
   * Update a specific field in the state and emit change event
   */
  updateState<K extends keyof GameState>(key: K, value: GameState[K]): void {
    const oldValue = this.state[key];
    this.state[key] = value;
    
    this.emit('state:change', { key, oldValue, newValue: value });
    this.emit(`state:change:${key}`, { oldValue, newValue: value });
  }

  /**
   * Update multiple fields at once
   */
  updateStateBatch(updates: Partial<GameState>): void {
    const changes: Array<{ key: keyof GameState; oldValue: unknown; newValue: unknown }> = [];
    
    for (const key in updates) {
      if (Object.prototype.hasOwnProperty.call(updates, key)) {
        const typedKey = key as keyof GameState;
        const value = updates[typedKey];
        if (value !== undefined) {
          const oldValue = this.state[typedKey];
          (this.state as any)[typedKey] = value;
          changes.push({ key: typedKey, oldValue, newValue: value });
        }
      }
    }
    
    this.emit('state:change:batch', { changes });
    for (const change of changes) {
      this.emit(`state:change:${change.key}`, { oldValue: change.oldValue, newValue: change.newValue });
    }
  }

  /**
   * Reset state to initial values (for new run)
   */
  reset(): void {
    const oldState = { ...this.state };
    this.state = this.createInitialState();
    this.emit('state:reset', { oldState, newState: this.state });
  }

  /**
   * Initialize state for a new day
   */
  startNewDay(dayNumber: number): void {
    this.updateState('currentDay', dayNumber);
    this.updateState('phase', 'morning');
    this.updateState('puzzle', null);
  }

  /**
   * Transition to next phase
   */
  transitionPhase(phase: GameState['phase']): void {
    this.updateState('phase', phase);
  }

  /**
   * Update resources
   */
  updateResources(updates: { capacity?: number; standing?: number; momentum?: number }): void {
    if (updates.capacity !== undefined) {
      this.updateState('capacity', updates.capacity);
    }
    if (updates.standing !== undefined) {
      this.updateState('standing', updates.standing);
    }
    if (updates.momentum !== undefined) {
      this.updateState('momentum', updates.momentum);
    }
  }

  /**
   * Set a narrative flag
   */
  setFlag(key: string, value: boolean | number | string): void {
    this.state.flags.set(key, value);
    this.emit('flag:set', { key, value });
  }

  /**
   * Get a narrative flag
   */
  getFlag(key: string): boolean | number | string | undefined {
    return this.state.flags.get(key);
  }

  /**
   * Update a relationship value
   */
  updateRelationship(characterId: string, delta: number): void {
    const current = this.state.relationships.get(characterId) ?? 0;
    const newValue = current + delta;
    this.state.relationships.set(characterId, newValue);
    this.emit('relationship:update', { characterId, oldValue: current, newValue });
  }

  /**
   * Add an unlock
   */
  addUnlock(unlockId: string): void {
    if (!this.state.unlocks.has(unlockId)) {
      this.state.unlocks.add(unlockId);
      this.emit('unlock:added', { unlockId });
    }
  }

  /**
   * Check if an unlock exists
   */
  hasUnlock(unlockId: string): boolean {
    return this.state.unlocks.has(unlockId);
  }
}

// Singleton instance (can be accessed globally or passed via dependency injection)
let gameStateInstance: GameStateManager | null = null;

/**
 * Get or create the global game state manager instance
 */
export function getGameState(): GameStateManager {
  if (!gameStateInstance) {
    gameStateInstance = new GameStateManager();
  }
  return gameStateInstance;
}

/**
 * Reset the global instance (useful for testing or full game reset)
 */
export function resetGameState(): void {
  if (gameStateInstance) {
    gameStateInstance.reset();
  } else {
    gameStateInstance = new GameStateManager();
  }
}

