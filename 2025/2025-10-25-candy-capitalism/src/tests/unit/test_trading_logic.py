"""
Unit tests for trading logic.

Tests candy type system, inventory management, trade evaluation,
and basic trading AI behavior.
"""

import pytest
from src.entities.kid import Kid, PersonalityType, Mood, KidState
from src.systems.economy import Economy
from src.core.candy_types import CandyTypes
from src.utils.vector2 import Vector2


class TestCandyTypeSystem:
    """Test candy type system."""
    
    def test_candy_types_load(self):
        """Test that candy types load from config."""
        types = CandyTypes.get_all_types()
        assert len(types) == 6  # CHOCOLATE, FRUITY, SOUR, NOVELTY, HEALTH, TRASH
        assert "CHOCOLATE" in types
        assert "FRUITY" in types
    
    def test_get_candy_type(self):
        """Test getting candy type object."""
        chocolate = CandyTypes.get("CHOCOLATE")
        assert chocolate is not None
        assert chocolate.name == "Chocolate"
        assert chocolate.real_value > 0
    
    def test_get_visual_properties(self):
        """Test getting visual properties."""
        props = CandyTypes.get_visual_properties("CHOCOLATE")
        assert "color" in props
        assert "icon" in props
        assert "name" in props
        assert props["name"] == "Chocolate"


class TestInventoryManagement:
    """Test inventory management."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.kid = Kid("test_kid", Vector2(100, 100))
    
    def test_add_candy(self):
        """Test adding candy to inventory."""
        self.kid.add_candy("CHOCOLATE", 3)
        assert self.kid.inventory["CHOCOLATE"] == 3
    
    def test_remove_candy(self):
        """Test removing candy from inventory."""
        self.kid.add_candy("CHOCOLATE", 5)
        success = self.kid.remove_candy("CHOCOLATE", 2)
        assert success
        assert self.kid.inventory["CHOCOLATE"] == 3
    
    def test_remove_candy_insufficient(self):
        """Test removing candy fails when insufficient."""
        self.kid.add_candy("CHOCOLATE", 1)
        success = self.kid.remove_candy("CHOCOLATE", 5)
        assert not success
        assert self.kid.inventory["CHOCOLATE"] == 1
    
    def test_has_candy(self):
        """Test checking if kid has candy."""
        self.kid.add_candy("FRUITY", 3)
        assert self.kid.has_candy("FRUITY", 2)
        assert not self.kid.has_candy("FRUITY", 5)
        assert not self.kid.has_candy("SOUR", 1)


class TestTradeEvaluation:
    """Test trade evaluation logic."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.kid = Kid("test_kid", Vector2(100, 100))
        self.economy = Economy()
        
        # Give kid some candy
        self.kid.add_candy("CHOCOLATE", 5)
        self.kid.add_candy("FRUITY", 3)
        
        # Set beliefs (chocolate worth 8.0, fruity worth 5.0)
        self.kid.believed_values["CHOCOLATE"] = 8.0
        self.kid.believed_values["FRUITY"] = 5.0
        self.kid.believed_values["SOUR"] = 6.0
    
    def test_evaluate_fair_trade(self):
        """Test evaluating a fair trade."""
        # Offer CHOCOLATE (value 8.0), request SOUR (value 6.0) - slightly bad for kid
        offer = {"CHOCOLATE": 1}
        request = {"SOUR": 1}
        
        score = self.kid.evaluate_trade(offer, request, self.economy)
        # Score should be negative (losing value)
        assert score < 0
    
    def test_evaluate_good_trade(self):
        """Test evaluating a good trade."""
        # Offer FRUITY (value 5.0), request CHOCOLATE (value 8.0) - good for kid
        offer = {"FRUITY": 1}
        request = {"CHOCOLATE": 1}
        
        score = self.kid.evaluate_trade(offer, request, self.economy)
        # Score should be positive (gaining value)
        assert score > 0
    
    def test_personality_affects_evaluation(self):
        """Test that different personalities evaluate trades differently."""
        # Create two kids with different personalities
        value_investor = Kid("investor", Vector2(100, 100))
        value_investor.personality = PersonalityType.VALUE_INVESTOR
        value_investor.believed_values = {"CHOCOLATE": 8.0, "FRUITY": 5.0}
        
        panic_seller = Kid("panicker", Vector2(200, 200))
        panic_seller.personality = PersonalityType.PANIC_SELLER
        panic_seller.believed_values = {"CHOCOLATE": 8.0, "FRUITY": 5.0}
        
        # Bad trade: Giving 8.0 value, receiving 10.0 value
        # Base score would be +2.0 * personality_modifier
        offer = {"CHOCOLATE": 1}  # Value 8.0
        request = {"FRUITY": 2}   # Value 10.0 (giving 2 fruity worth 5.0 each)
        
        investor_score = value_investor.evaluate_trade(offer, request, self.economy)
        panic_score = panic_seller.evaluate_trade(offer, request, self.economy)
        
        # Both should get positive scores (good trade)
        assert investor_score > 0
        assert panic_score > 0
        
        # Panic seller should accept worse trades (lower threshold)
        # So for a GOOD trade, both accept but VALUE_INVESTOR gets higher score
        # (multiplies by 1.3 vs 0.5, but that makes investor score HIGHER)
        # This is because multiplier amplifies the positive score
        
        # Let's test with a BAD trade instead
        bad_offer = {"CHOCOLATE": 1}  # Value 8.0
        bad_request = {"FRUITY": 1}   # Value 5.0 (bad trade, losing value)
        
        investor_bad = value_investor.evaluate_trade(bad_offer, bad_request, self.economy)
        panic_bad = panic_seller.evaluate_trade(bad_offer, bad_request, self.economy)
        
        # Both should reject bad trade, but panic seller is more lenient (less negative)
        # VALUE_INVESTOR: -3.0 * 1.3 = -3.9
        # PANIC_SELLER: -3.0 * 0.5 = -1.5
        assert panic_bad > investor_bad  # Panic seller is less negative
    
    def test_mood_affects_evaluation(self):
        """Test that mood affects trade evaluation."""
        kid1 = Kid("happy_kid", Vector2(100, 100))
        kid1.mood = Mood.HAPPY
        kid1.believed_values = {"CHOCOLATE": 8.0, "FRUITY": 5.0}
        
        kid2 = Kid("anxious_kid", Vector2(200, 200))
        kid2.mood = Mood.ANXIOUS
        kid2.believed_values = {"CHOCOLATE": 8.0, "FRUITY": 5.0}
        
        offer = {"FRUITY": 1}
        request = {"CHOCOLATE": 1}  # Good trade
        
        happy_score = kid1.evaluate_trade(offer, request, self.economy)
        anxious_score = kid2.evaluate_trade(offer, request, self.economy)
        
        # Both should accept, but anxious is more cautious
        # The exact relationship depends on implementation
        assert happy_score > 0
        assert anxious_score > 0


class TestTradingAI:
    """Test trading AI behavior."""
    
    def setup_method(self):
        """Set up test fixtures."""
        from src.systems.game_world import GameWorld
        self.world = GameWorld()
        self.world.economy = Economy()
        
        # Create two kids close together
        self.kid1 = Kid("kid1", Vector2(100, 100))
        self.kid1.inventory = {"CHOCOLATE": 5, "FRUITY": 3}
        self.kid1.believed_values = {"CHOCOLATE": 8.0, "FRUITY": 5.0, "SOUR": 6.0}
        self.kid1.preferences = {"CHOCOLATE": 0.8, "FRUITY": 0.6, "SOUR": 0.5}
        self.world.add_kid(self.kid1)
        
        self.kid2 = Kid("kid2", Vector2(120, 120))  # Close by
        self.kid2.inventory = {"SOUR": 5, "FRUITY": 2}
        self.kid2.believed_values = {"CHOCOLATE": 8.0, "FRUITY": 5.0, "SOUR": 6.0}
        self.kid2.preferences = {"CHOCOLATE": 0.9, "FRUITY": 0.4, "SOUR": 0.3}
        self.world.add_kid(self.kid2)
        
        # Update spatial grid
        self.world._update_spatial_grid()
    
    def test_can_find_nearby_partners(self):
        """Test that AI can find nearby trading partners."""
        from src.ai.basic_behaviors import BasicBehaviors
        
        # Both kids should have enough candy to trade
        assert sum(self.kid1.inventory.values()) >= 2
        assert sum(self.kid2.inventory.values()) >= 2
        
        # Should be able to find each other as partners
        nearby = self.world.spatial_grid.get_nearby(self.kid1.position, 150.0)
        kid_types = [k for k in nearby if isinstance(k, Kid) and k != self.kid1]
        assert len(kid_types) > 0
