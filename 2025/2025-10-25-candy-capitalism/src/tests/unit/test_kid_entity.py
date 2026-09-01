"""
Unit tests for Kid entity.
"""

import pytest
from src.entities.kid import Kid, KidState, PersonalityType, Mood
from src.utils.vector2 import Vector2


class TestKidEntity:
    """Test cases for Kid entity."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.kid = Kid("test_kid", Vector2(100, 100))
    
    def test_kid_initialization(self):
        """Test kid initialization with default values."""
        assert self.kid.id == "test_kid"
        assert self.kid.position == Vector2(100, 100)
        assert self.kid.state == KidState.IDLE
        assert self.kid.personality == PersonalityType.VALUE_INVESTOR
        assert self.kid.mood == Mood.NEUTRAL
        assert self.kid.max_speed == 50.0
        assert self.kid.active == True
        assert self.kid.visible == True
    
    def test_movement_toward_target(self):
        """Test movement toward target position."""
        target = Vector2(200, 200)
        
        # Move toward target
        reached = self.kid.move_toward(target, 100.0, 0.1)  # High speed, small dt
        
        # Should not reach target in one step
        assert not reached
        assert self.kid.position != Vector2(100, 100)  # Should have moved
        
        # Continue moving until reached
        for _ in range(20):  # Max 20 iterations
            reached = self.kid.move_toward(target, 100.0, 0.1)
            if reached:
                break
        
        # Should eventually reach target
        assert reached
        assert self.kid.position.distance_to(target) <= 10.0  # Arrival distance
    
    def test_reached_target(self):
        """Test reached_target detection."""
        # Set target far away
        self.kid.target_position = Vector2(1000, 1000)
        assert not self.kid.reached_target()
        
        # Set target close
        self.kid.target_position = Vector2(105, 105)  # 5 units away
        assert self.kid.reached_target()
        
        # Set target very close
        self.kid.target_position = Vector2(100.1, 100.1)  # 0.14 units away
        assert self.kid.reached_target()
    
    def test_candy_inventory(self):
        """Test candy inventory management."""
        # Add candy
        self.kid.add_candy("chocolate", 3)
        self.kid.add_candy("fruity", 2)
        
        # Check inventory
        assert self.kid.inventory["chocolate"] == 3
        assert self.kid.inventory["fruity"] == 2
        assert self.kid.has_candy("chocolate", 3)
        assert self.kid.has_candy("fruity", 1)
        assert not self.kid.has_candy("sour", 1)
        
        # Remove candy
        success = self.kid.remove_candy("chocolate", 2)
        assert success
        assert self.kid.inventory["chocolate"] == 1
        
        # Try to remove more than available
        success = self.kid.remove_candy("chocolate", 5)
        assert not success
        assert self.kid.inventory["chocolate"] == 1  # Should not change
    
    def test_state_transitions(self):
        """Test kid state transitions."""
        # Start in IDLE
        assert self.kid.state == KidState.IDLE
        
        # Set target and move to MOVING_TO_HOUSE
        self.kid.target_position = Vector2(200, 200)
        self.kid.state = KidState.MOVING_TO_HOUSE
        assert self.kid.state == KidState.MOVING_TO_HOUSE
        
        # Simulate reaching target
        self.kid.position = Vector2(200, 200)
        self.kid.state = KidState.TRICK_OR_TREATING
        self.kid.trick_or_treat_timer = 2.0
        assert self.kid.state == KidState.TRICK_OR_TREATING
    
    def test_pathfinding_properties(self):
        """Test pathfinding-related properties."""
        # Test path setting
        path = [Vector2(100, 100), Vector2(150, 150), Vector2(200, 200)]
        self.kid.set_path(path)
        
        assert self.kid.current_path == path
        assert self.kid.path_index == 0
        
        # Test path clearing
        self.kid.clear_path()
        assert self.kid.current_path == []
        assert self.kid.path_index == 0
    
    def test_mood_color_mapping(self):
        """Test mood to color mapping."""
        # Test different moods
        self.kid.mood = Mood.HAPPY
        color = self.kid._get_mood_color()
        assert color == (100, 255, 100)  # Green
        
        self.kid.mood = Mood.PANIC
        color = self.kid._get_mood_color()
        assert color == (255, 100, 100)  # Red
        
        self.kid.mood = Mood.NEUTRAL
        color = self.kid._get_mood_color()
        assert color == (255, 255, 255)  # White
    
    def test_candy_value_calculation(self):
        """Test candy value calculation."""
        # Add some candy
        self.kid.add_candy("chocolate", 2)
        self.kid.add_candy("fruity", 3)
        
        # Define real values
        real_values = {
            "chocolate": 8.0,
            "fruity": 5.0,
            "sour": 6.0
        }
        
        # Calculate total value
        total_value = self.kid.get_total_candy_value(real_values)
        expected = (2 * 8.0) + (3 * 5.0)  # 16 + 15 = 31
        assert total_value == expected
    
    def test_update_timers(self):
        """Test that timers update correctly."""
        # Set initial timers
        self.kid.trade_cooldown = 5.0
        self.kid.trick_or_treat_timer = 3.0
        
        # Update with small dt
        self.kid.update(0.1)
        
        # Timers should decrease
        assert self.kid.trade_cooldown < 5.0
        assert self.kid.trick_or_treat_timer < 3.0
        
        # Update until cooldown reaches 0
        while self.kid.trade_cooldown > 0:
            self.kid.update(0.1)
        
        # Cooldown should not go below 0
        assert self.kid.trade_cooldown == 0.0
    
    def test_movement_with_pathfinding(self):
        """Test movement with pathfinding."""
        # Set up path
        path = [Vector2(150, 150), Vector2(200, 200)]
        self.kid.set_path(path)
        self.kid.target_position = Vector2(200, 200)
        
        # Move with pathfinding
        reached = self.kid._move_with_pathfinding(Vector2(200, 200), 100.0, 0.1)
        
        # Should not reach immediately
        assert not reached
        assert self.kid.path_index == 0  # Should be at first waypoint
        
        # Continue moving
        for _ in range(20):
            reached = self.kid._move_with_pathfinding(Vector2(200, 200), 100.0, 0.1)
            if reached:
                break
        
        # Should eventually reach target
        assert reached
    
    def test_inactive_kid_behavior(self):
        """Test that inactive kids don't update."""
        self.kid.active = False
        self.kid.trade_cooldown = 5.0
        
        # Update inactive kid
        self.kid.update(1.0)
        
        # Timer should not change
        assert self.kid.trade_cooldown == 5.0


class TestKidStateMachine:
    """Test kid state machine behavior."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.kid = Kid("test_kid", Vector2(100, 100))
    
    def test_idle_to_moving_transition(self):
        """Test transition from IDLE to MOVING_TO_HOUSE."""
        # Start in IDLE
        assert self.kid.state == KidState.IDLE
        
        # Set target and change state
        self.kid.target_position = Vector2(200, 200)
        self.kid.state = KidState.MOVING_TO_HOUSE
        
        assert self.kid.state == KidState.MOVING_TO_HOUSE
    
    def test_moving_to_trick_or_treating(self):
        """Test transition from MOVING to TRICK_OR_TREATING."""
        self.kid.state = KidState.MOVING_TO_HOUSE
        self.kid.target_position = Vector2(200, 200)
        
        # Simulate reaching target
        self.kid.position = Vector2(200, 200)
        
        # Update state behavior
        self.kid._update_state_behavior(0.1)
        
        # Should transition to trick-or-treating
        assert self.kid.state == KidState.TRICK_OR_TREATING
        assert self.kid.trick_or_treat_timer > 0
    
    def test_trick_or_treating_to_idle(self):
        """Test transition from TRICK_OR_TREATING to IDLE."""
        self.kid.state = KidState.TRICK_OR_TREATING
        self.kid.trick_or_treat_timer = 0.1  # Almost done
        
        # Update the kid (which calls _update_state_behavior)
        self.kid.update(0.2)  # More than timer
        
        # Should transition to IDLE
        assert self.kid.state == KidState.IDLE
