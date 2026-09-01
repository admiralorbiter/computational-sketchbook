"""
Unit tests for house cooldown functionality.

Tests the cooldown system that prevents houses from dispensing candy too frequently.
"""

import pytest
from src.entities.house import House
from src.utils.vector2 import Vector2


class TestHouseCooldown:
    """Test house cooldown functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.house = House("test_house", Vector2(100, 100), quality=2)
    
    def test_initial_cooldown_state(self):
        """Test initial cooldown state."""
        assert self.house.dispense_cooldown == 0.0
        assert self.house.is_available() == True
        assert self.house.get_cooldown_progress() == 1.0
        assert self.house.get_next_available_time() == 0.0
    
    def test_cooldown_after_dispensing(self):
        """Test cooldown is set after dispensing candy."""
        # Initially available
        assert self.house.is_available() == True
        
        # Dispense candy
        candy = self.house.dispense_candy()
        assert len(candy) > 0
        
        # Should now be on cooldown
        assert self.house.dispense_cooldown > 0
        assert self.house.is_available() == False
        assert self.house.get_cooldown_progress() < 1.0
        assert self.house.get_next_available_time() > 0.0
    
    def test_cooldown_progress_calculation(self):
        """Test cooldown progress calculation."""
        # Dispense candy to start cooldown
        self.house.dispense_candy()
        initial_cooldown = self.house.dispense_cooldown
        
        # Progress should be less than 1.0
        progress = self.house.get_cooldown_progress()
        assert 0.0 <= progress < 1.0
        
        # Simulate time passing
        self.house.update(2.0)  # 2 seconds
        
        # Progress should be higher
        new_progress = self.house.get_cooldown_progress()
        assert new_progress > progress
    
    def test_cooldown_expiration(self):
        """Test cooldown expires after time."""
        # Dispense candy to start cooldown
        self.house.dispense_candy()
        assert not self.house.is_available()
        
        # Wait for cooldown to expire
        self.house.update(6.0)  # 6 seconds (cooldown is 5 seconds)
        
        # Should be available again
        assert self.house.is_available()
        assert self.house.get_cooldown_progress() == 1.0
        assert self.house.get_next_available_time() == 0.0
    
    def test_cannot_dispense_during_cooldown(self):
        """Test cannot dispense candy during cooldown."""
        # Dispense candy to start cooldown
        self.house.dispense_candy()
        
        # Try to dispense again immediately
        candy = self.house.dispense_candy()
        assert len(candy) == 0  # Should get no candy
    
    def test_can_dispense_after_cooldown(self):
        """Test can dispense candy after cooldown expires."""
        # Dispense candy to start cooldown
        self.house.dispense_candy()
        
        # Wait for cooldown to expire
        self.house.update(6.0)
        
        # Should be able to dispense again
        candy = self.house.dispense_candy()
        assert len(candy) > 0
    
    def test_cooldown_update(self):
        """Test cooldown timer updates correctly."""
        # Dispense candy to start cooldown
        self.house.dispense_candy()
        initial_cooldown = self.house.dispense_cooldown
        
        # Update with small time step
        self.house.update(0.5)
        
        # Cooldown should be reduced
        assert self.house.dispense_cooldown < initial_cooldown
        assert self.house.dispense_cooldown > 0
    
    def test_cooldown_never_goes_negative(self):
        """Test cooldown never goes below zero."""
        # Dispense candy to start cooldown
        self.house.dispense_candy()
        
        # Update with large time step
        self.house.update(10.0)
        
        # Cooldown should be exactly 0
        assert self.house.dispense_cooldown == 0.0
        assert self.house.is_available() == True
    
    def test_multiple_dispenses_respect_cooldown(self):
        """Test multiple dispense attempts respect cooldown."""
        # First dispense
        candy1 = self.house.dispense_candy()
        assert len(candy1) > 0
        
        # Try to dispense again immediately
        candy2 = self.house.dispense_candy()
        assert len(candy2) == 0
        
        # Wait a bit
        self.house.update(2.0)
        
        # Still on cooldown
        candy3 = self.house.dispense_candy()
        assert len(candy3) == 0
        
        # Wait for full cooldown
        self.house.update(4.0)
        
        # Now should work
        candy4 = self.house.dispense_candy()
        assert len(candy4) > 0
