"""
Unit tests for AI house selection logic.

Tests AI behavior for cursed/blessed house avoidance and preference.
"""

import pytest
from src.ai.basic_behaviors import BasicBehaviors
from src.entities.kid import Kid
from src.entities.house import House
from src.systems.game_world import GameWorld
from src.utils.vector2 import Vector2


class TestAIHouseSelection:
    """Test AI house selection behavior."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.world = GameWorld()
        self.kid = Kid("test_kid", Vector2(100, 100))
        self.world.add_kid(self.kid)
        
        # Add multiple houses
        self.house1 = House("house1", Vector2(200, 200))
        self.house2 = House("house2", Vector2(300, 300))
        self.house3 = House("house3", Vector2(400, 400))
        
        self.world.add_house(self.house1)
        self.world.add_house(self.house2)
        self.world.add_house(self.house3)
    
    def test_avoids_cursed_houses(self):
        """Test that AI avoids cursed houses when possible."""
        # Curse one house
        self.house1.curse(duration=60.0)
        
        # Select house multiple times and ensure cursed house is avoided
        selections = []
        for _ in range(10):
            selected = BasicBehaviors.select_house(self.kid, self.world)
            if selected:
                selections.append(selected.id)
        
        # Should not select cursed house when others available
        assert "house1" not in selections
        assert "house2" in selections or "house3" in selections
    
    def test_prefers_blessed_houses(self):
        """Test that AI prefers blessed houses."""
        # Bless one house
        self.house2.bless(duration=30.0)
        
        # Select house many times
        blessed_count = 0
        total_selections = 50
        
        for _ in range(total_selections):
            selected = BasicBehaviors.select_house(self.kid, self.world)
            if selected and selected.id == "house2":
                blessed_count += 1
        
        # Should prefer blessed house (70% chance)
        # With 50 trials, expect at least 60% to account for randomness
        assert blessed_count >= total_selections * 0.6
    
    def test_selects_cursed_if_no_choice(self):
        """Test that AI selects cursed house if all houses are cursed."""
        # Curse all houses
        self.house1.curse(duration=60.0)
        self.house2.curse(duration=60.0)
        self.house3.curse(duration=60.0)
        
        # Should still select a house
        selected = BasicBehaviors.select_house(self.kid, self.world)
        assert selected is not None
        assert selected.id in ["house1", "house2", "house3"]
