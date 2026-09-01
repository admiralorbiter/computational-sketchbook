"""
Game state management system.

Handles transitions between different game states (menu, playing, paused, etc.)
using a state machine pattern.
"""

from enum import Enum
from typing import Dict, Any


class GameState(Enum):
    """Enumeration of all possible game states."""
    MAIN_MENU = 0
    SCENARIO_SELECT = 1
    PLAYING = 2
    PAUSED = 3
    VICTORY = 4
    DEFEAT = 5


class GameStateMachine:
    """
    Manages game state transitions and updates.
    
    Uses the State pattern to handle different game modes cleanly.
    """
    
    def __init__(self):
        self.current_state = GameState.MAIN_MENU
        self.states: Dict[GameState, Any] = {}
        self.state_data = {}  # Data passed between states
        
    def register_state(self, state: GameState, state_handler):
        """Register a state handler for a given state."""
        self.states[state] = state_handler
        
    def transition(self, new_state: GameState, data: Dict[str, Any] = None):
        """
        Transition to a new game state.
        
        Args:
            new_state: The state to transition to
            data: Optional data to pass to the new state
        """
        if self.current_state in self.states:
            self.states[self.current_state].on_exit()
            
        self.current_state = new_state
        self.state_data = data or {}
        
        if self.current_state in self.states:
            self.states[self.current_state].on_enter(self.state_data)
    
    def update(self, dt: float):
        """Update the current state."""
        if self.current_state in self.states:
            self.states[self.current_state].update(dt)
    
    def handle_event(self, event):
        """Pass events to the current state."""
        if self.current_state in self.states:
            return self.states[self.current_state].handle_event(event)
        return False


class BaseState:
    """Base class for all game states."""
    
    def on_enter(self, data: Dict[str, Any] = None):
        """Called when entering this state."""
        pass
    
    def on_exit(self):
        """Called when exiting this state."""
        pass
    
    def update(self, dt: float):
        """Update this state."""
        pass
    
    def handle_event(self, event):
        """Handle input events for this state."""
        return False
