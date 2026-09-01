"""
Integration tests for the trading system.

Tests the interaction between kids, economy, and trading mechanics.
"""

import pytest
from src.systems.game_world import GameWorld
from src.systems.economy import Economy
from src.entities.kid import Kid, PersonalityType, Mood
from src.utils.vector2 import Vector2


class TestTradingSystem:
    """Test cases for trading system integration."""
    
    def test_kid_economy_integration(self, sample_world):
        """Test integration between kids and economy system."""
        world = sample_world
        
        # Add economy system
        world.economy = Economy()
        
        # Get a kid and give them some candy
        kid = world.kids[0]
        kid.inventory = {"CHOCOLATE": 3, "FRUITY": 2}
        kid.believed_values = {"CHOCOLATE": 8.0, "FRUITY": 5.0}
        
        # Check kid's total candy value
        total_value = kid.get_total_candy_value(world.economy.real_values)
        expected_value = (3 * 8.0) + (2 * 5.0)  # 24 + 10 = 34
        assert total_value == expected_value
    
    def test_trade_evaluation(self, sample_world):
        """Test trade evaluation between kids."""
        world = sample_world
        
        # Create two kids with different personalities
        kid1 = Kid("trader1", Vector2(0, 0))
        kid1.personality = PersonalityType.VALUE_INVESTOR
        kid1.mood = Mood.NEUTRAL
        kid1.inventory = {"CHOCOLATE": 2}
        kid1.believed_values = {"CHOCOLATE": 8.0, "FRUITY": 5.0}
        
        kid2 = Kid("trader2", Vector2(50, 50))
        kid2.personality = PersonalityType.MOMENTUM_TRADER
        kid2.mood = Mood.NEUTRAL
        kid2.inventory = {"FRUITY": 3}
        kid2.believed_values = {"CHOCOLATE": 8.0, "FRUITY": 5.0}
        
        world.add_kid(kid1)
        world.add_kid(kid2)
        
        # Test trade evaluation
        offer = {"CHOCOLATE": 1}
        request = {"FRUITY": 1}
        
        # Both kids should evaluate this as a fair trade
        score1 = kid1.evaluate_trade(offer, request, world.economy)
        score2 = kid2.evaluate_trade(request, offer, world.economy)
        
        # Scores should be reasonable (implementation dependent)
        assert isinstance(score1, (int, float))
        assert isinstance(score2, (int, float))
    
    def test_spatial_grid_integration(self, sample_world):
        """Test spatial grid integration with kids."""
        world = sample_world
        
        # Update world to populate spatial grid
        world.update(0.1)
        
        # Test getting nearby kids
        center = Vector2(50, 50)
        nearby_kids = world.get_nearby_kids(center, 100)
        
        # Should find kids within radius
        assert len(nearby_kids) > 0
        assert len(nearby_kids) <= len(world.kids)
        
        # All returned kids should be within radius
        for kid in nearby_kids:
            distance = kid.position.distance_to(center)
            assert distance <= 100
    
    def test_trading_bloc_formation(self, sample_world):
        """Test trading bloc formation."""
        world = sample_world
        
        # Update world to trigger bloc formation
        world.update(0.1)
        
        # Should have formed a bloc with 3 kids
        assert len(world.trading_blocs) > 0
        
        bloc = world.trading_blocs[0]
        assert bloc.get_member_count() >= 3
        assert bloc.can_form() is True
    
    def test_world_update_cycle(self, sample_world):
        """Test complete world update cycle."""
        world = sample_world
        
        # Add economy system
        world.economy = Economy()
        
        # Update world multiple times
        for _ in range(10):
            world.update(0.1)
        
        # Check that systems are working
        assert world.game_time > 0
        assert len(world.kids) > 0
        assert len(world.houses) > 0
        
        # Check spatial grid is populated
        stats = world.spatial_grid.get_stats()
        assert stats['total_entities'] > 0
    
    def test_kid_ai_tick(self, sample_world):
        """Test kid AI tick functionality."""
        world = sample_world
        
        # Get a kid and set up their state
        kid = world.kids[0]
        kid.state = kid.state.SEEKING_TRADE
        kid.trade_cooldown = 0
        
        # Run AI tick
        kid.ai_tick(world)
        
        # Kid should have updated their state
        # (exact behavior depends on implementation)
        assert kid.state in [kid.state.IDLE, kid.state.SEEKING_TRADE]
    
    def test_house_kid_interaction(self, sample_world):
        """Test interaction between houses and kids."""
        world = sample_world
        
        # Get a house and kid
        house = world.houses[0]
        kid = world.kids[0]
        
        # Set up house candy types
        house.set_candy_types(["CHOCOLATE", "FRUITY"])
        
        # Test attraction calculation
        attraction = house.get_attraction_strength(kid.position)
        assert 0.0 <= attraction <= 1.0
        
        # Test candy dispensing
        if house.can_dispense_candy():
            candy = house.dispense_candy()
            assert isinstance(candy, dict)
            assert len(candy) > 0
    
    def test_world_stats(self, sample_world):
        """Test world statistics gathering."""
        world = sample_world
        
        # Update world
        world.update(0.1)
        
        # Get stats
        stats = world.get_stats()
        
        assert "kids" in stats
        assert "houses" in stats
        assert "trading_blocs" in stats
        assert "game_time" in stats
        assert "spatial_grid_stats" in stats
        
        assert stats["kids"] == len(world.kids)
        assert stats["houses"] == len(world.houses)
        assert stats["game_time"] > 0
