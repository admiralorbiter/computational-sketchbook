// Game state and related type definitions
import { PuzzleState, Indicator } from './puzzle';

export interface GameState {
  // Run state
  currentDay: number;
  phase: 'morning' | 'day' | 'night' | 'resolution';
  
  // Resources
  capacity: number;
  standing: number;
  momentum: number;
  
  // Puzzle state (isolated for easy reset)
  puzzle: PuzzleState | null;
  
  // Narrative state
  flags: Map<string, boolean | number | string>;
  relationships: Map<string, number>;
  
  // Meta (persists across runs)
  unlocks: Set<string>;
  templates: string[];
  precedents: string[];
  
  // Board indicators
  indicators: Indicator[];
}

// Re-export commonly used types
export type { PuzzleState, Indicator } from './puzzle';

