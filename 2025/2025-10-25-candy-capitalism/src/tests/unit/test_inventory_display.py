"""
Unit tests for inventory display UI.

Tests the inventory display system for showing kid candy breakdown.
"""

import pytest
from unittest.mock import Mock
from src.ui.inventory_display import InventoryDisplay, InventoryManager
from src.entities.kid import Kid, PersonalityType, Mood, KidState
from src.utils.vector2 import Vector2


class TestInventoryDisplay:
    """Test inventory display functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.display = InventoryDisplay()
        self.kid = Kid("test_kid", Vector2(100, 100))
        self.kid.personality = PersonalityType.VALUE_INVESTOR
        self.kid.inventory = {"chocolate": 5, "fruity": 3, "sour": 1}
    
    def test_initial_state(self):
        """Test initial display state."""
        assert self.display.selected_kid is None
        assert self.display.visible == False
        assert self.display.position == Vector2(10, 10)
        assert self.display.width == 400
        assert self.display.height == 300
    
    def test_set_selected_kid(self):
        """Test setting selected kid."""
        self.display.set_selected_kid(self.kid)
        assert self.display.selected_kid == self.kid
    
    def test_toggle_visibility(self):
        """Test toggling display visibility."""
        assert self.display.visible == False
        
        self.display.toggle_visibility()
        assert self.display.visible == True
        
        self.display.toggle_visibility()
        assert self.display.visible == False
    
    def test_show_hide(self):
        """Test show and hide methods."""
        self.display.show()
        assert self.display.visible == True
        
        self.display.hide()
        assert self.display.visible == False
    
    def test_get_display_data(self):
        """Test getting display data for selected kid."""
        self.display.set_selected_kid(self.kid)
        
        data = self.display.get_display_data()
        
        assert data["kid_id"] == "test_kid"
        assert data["personality"] == "VALUE_INVESTOR"
        assert data["total_candy"] == 9
        assert data["candy_breakdown"] == {"chocolate": 5, "fruity": 3, "sour": 1}
        assert "candy_details" in data
    
    def test_get_display_data_no_kid(self):
        """Test getting display data with no selected kid."""
        data = self.display.get_display_data()
        assert data == {}


class TestInventoryManager:
    """Test inventory manager functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = InventoryManager()
        self.kid = Kid("test_kid", Vector2(100, 100))
        self.kid.personality = PersonalityType.VALUE_INVESTOR
        self.kid.inventory = {"chocolate": 5, "fruity": 3}
    
    def test_initial_state(self):
        """Test initial manager state."""
        assert self.manager.selected_kid_id is None
        assert self.manager.main_display is not None
        assert self.manager.main_display.visible == False
    
    def test_select_kid(self):
        """Test selecting a kid."""
        self.manager.select_kid(self.kid)
        
        assert self.manager.selected_kid_id == "test_kid"
        assert self.manager.main_display.selected_kid == self.kid
    
    def test_select_none_kid(self):
        """Test selecting None kid."""
        self.manager.select_kid(None)
        
        assert self.manager.selected_kid_id is None
        assert self.manager.main_display.selected_kid is None
    
    def test_toggle_main_display(self):
        """Test toggling main display."""
        assert self.manager.main_display.visible == False
        
        self.manager.toggle_main_display()
        assert self.manager.main_display.visible == True
        
        self.manager.toggle_main_display()
        assert self.manager.main_display.visible == False
    
    def test_show_hide_main_display(self):
        """Test showing and hiding main display."""
        self.manager.show_main_display()
        assert self.manager.main_display.visible == True
        
        self.manager.hide_main_display()
        assert self.manager.main_display.visible == False
    
    def test_get_selected_kid_data(self):
        """Test getting selected kid data."""
        self.manager.select_kid(self.kid)
        
        data = self.manager.get_selected_kid_data()
        
        assert data["kid_id"] == "test_kid"
        assert data["personality"] == "VALUE_INVESTOR"
        assert data["total_candy"] == 8
        assert data["candy_breakdown"] == {"chocolate": 5, "fruity": 3}
    
    def test_get_selected_kid_data_no_kid(self):
        """Test getting selected kid data with no kid selected."""
        data = self.manager.get_selected_kid_data()
        assert data == {}


class TestInventoryDisplayIntegration:
    """Test inventory display integration with kid data."""
    
    def test_empty_inventory_display(self):
        """Test display with empty inventory."""
        display = InventoryDisplay()
        kid = Kid("empty_kid", Vector2(100, 100))
        kid.personality = PersonalityType.HOARDER
        kid.inventory = {}
        
        display.set_selected_kid(kid)
        data = display.get_display_data()
        
        assert data["kid_id"] == "empty_kid"
        assert data["personality"] == "HOARDER"
        assert data["total_candy"] == 0
        assert data["candy_breakdown"] == {}
    
    def test_full_inventory_display(self):
        """Test display with full inventory."""
        display = InventoryDisplay()
        kid = Kid("rich_kid", Vector2(100, 100))
        kid.personality = PersonalityType.MOMENTUM_TRADER
        kid.inventory = {
            "chocolate": 10,
            "fruity": 8,
            "sour": 5,
            "mint": 3,
            "caramel": 7
        }
        
        display.set_selected_kid(kid)
        data = display.get_display_data()
        
        assert data["kid_id"] == "rich_kid"
        assert data["personality"] == "MOMENTUM_TRADER"
        assert data["total_candy"] == 33
        assert len(data["candy_breakdown"]) == 5
        assert data["candy_breakdown"]["chocolate"] == 10
        assert data["candy_breakdown"]["fruity"] == 8
    
    def test_different_personalities(self):
        """Test display with different kid personalities."""
        personalities = [
            PersonalityType.VALUE_INVESTOR,
            PersonalityType.MOMENTUM_TRADER,
            PersonalityType.HOARDER,
            PersonalityType.SOCIAL_TRADER,
            PersonalityType.PANIC_SELLER
        ]
        
        for personality in personalities:
            display = InventoryDisplay()
            kid = Kid(f"kid_{personality.name}", Vector2(100, 100))
            kid.personality = personality
            kid.inventory = {"chocolate": 2}
            
            display.set_selected_kid(kid)
            data = display.get_display_data()
            
            assert data["personality"] == personality.name
            assert data["total_candy"] == 2
