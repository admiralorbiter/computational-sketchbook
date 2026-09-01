// Game constants and tuning values
export const GAME_CONFIG = {
  // Display
  WIDTH: 1280,
  HEIGHT: 720,
  
  // Puzzle grid
  GRID_COLS: 8,
  GRID_ROWS: 10,
  TILE_SIZE: 48,
  
  // Resources (the three core numbers)
  STARTING_CAPACITY: 10,
  STARTING_STANDING: 5,
  STARTING_MOMENTUM: 0,
  
  // Puzzle tuning
  TAINT_SPREAD_INTERVAL: 2,  // turns between taint spread
  CHAIN_MIN_LENGTH: 3,
  TAINT_CONSUME_THRESHOLD: 3, // taint level at which tiles are consumed
  TAINT_OVERWHELM_THRESHOLD: 0.5, // fraction of board that must be tainted to lose
  
  // Day structure
  ACTIONS_PER_DAY: 2,
};

