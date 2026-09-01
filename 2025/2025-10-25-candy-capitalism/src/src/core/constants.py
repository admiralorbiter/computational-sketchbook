"""
Game constants and configuration values.

Centralized location for all game constants to make tuning easier.
"""

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Performance targets
FPS_TARGET = 60
AI_TICK_RATE = 2.0  # AI updates every 2 seconds

# Spatial partitioning
SPATIAL_GRID_CELL_SIZE = 100

# Game timing
GAME_TIME_STEP = 1.0 / FPS_TARGET
AI_TICK_INTERVAL = 1.0 / AI_TICK_RATE

# Colors (RGB)
COLORS = {
    'BACKGROUND': (20, 20, 30),
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'RED': (255, 100, 100),
    'GREEN': (100, 255, 100),
    'BLUE': (100, 100, 255),
    'YELLOW': (255, 255, 100),
    'ORANGE': (255, 165, 0),
    'PURPLE': (128, 0, 128),
    'GRAY': (128, 128, 128),
    'DARK_GRAY': (64, 64, 64),
}

# Candy types (will be loaded from config)
CANDY_TYPES = [
    'CHOCOLATE',
    'FRUITY', 
    'SOUR',
    'NOVELTY',
    'HEALTH',
    'TRASH'
]

# Kid personality types
PERSONALITY_TYPES = [
    'VALUE_INVESTOR',
    'MOMENTUM_TRADER', 
    'HOARDER',
    'SOCIAL_TRADER',
    'PANIC_SELLER'
]

# Kid states
KID_STATES = [
    'IDLE',
    'MOVING_TO_HOUSE',
    'TRICK_OR_TREATING',
    'SEEKING_TRADE',
    'IN_TRADE',
    'FLEEING'
]

# Mood types
MOODS = [
    'HAPPY',
    'NEUTRAL',
    'ANXIOUS',
    'GREEDY',
    'PANIC'
]

# Game states
GAME_STATES = [
    'MAIN_MENU',
    'SCENARIO_SELECT',
    'PLAYING',
    'PAUSED',
    'VICTORY',
    'DEFEAT'
]

# Event types
EVENT_TYPES = [
    'TRADE_COMPLETED',
    'RUMOR_SPREAD',
    'DEBT_DEFAULTED',
    'COMBO_TRIGGERED',
    'CARTEL_FORMED',
    'RANDOM_EVENT'
]

# UI layers
UI_LAYERS = [
    'BACKGROUND',
    'WORLD',
    'HUD',
    'POPUPS',
    'OVERLAY'
]
