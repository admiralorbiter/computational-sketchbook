"""
Integration tests for Sprint 1 polish features.

Tests the integration of particle effects, cooldown visualization, 
inventory display, personality indicators, and collision detection.
"""

import pytest
import pygame
from unittest.mock import Mock, patch
from src.core.game import Game
from src.systems.game_world import GameWorld
from src.rendering.renderer import Renderer
from src.entities.kid import Kid, PersonalityType, Mood, KidState
from src.entities.house import House
from src.utils.vector2 import Vector2


class TestSprint1PolishIntegration:
    """Test integration of Sprint 1 polish features."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Initialize pygame for testing
        pygame.init()
        
        # Create game world
        self.world = GameWorld()
        self.world.generate_map("test_small")
        self.world.spawn_kids(5)
        
        # Create renderer
        screen = pygame.display.set_mode((800, 600))
        self.renderer = Renderer(screen)
        self.renderer.camera.position = Vector2(1000, 1000)
        self.renderer.camera.zoom = 0.5
    
    def teardown_method(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_particle_effects_integration(self):
        """Test particle effects are emitted when candy is dispensed."""
        # Get a house and kid
        house = self.world.houses[0]
        kid = self.world.kids[0]
        
        # Position kid at house
        kid.position = house.position
        kid.target_house = house
        kid.state = KidState.TRICK_OR_TREATING
        
        # Get initial particle count
        initial_particle_count = self.renderer.particle_system.get_particle_count()
        
        # Update kid to trigger candy dispensing
        kid.update(0.1, self.renderer)
        
        # Should have more particles now
        new_particle_count = self.renderer.particle_system.get_particle_count()
        assert new_particle_count > initial_particle_count
    
    def test_house_cooldown_integration(self):
        """Test house cooldown prevents multiple dispenses."""
        house = self.world.houses[0]
        
        # First dispense
        candy1 = house.dispense_candy()
        assert len(candy1) > 0
        assert not house.is_available()
        
        # Try to dispense again immediately
        candy2 = house.dispense_candy()
        assert len(candy2) == 0  # Should be blocked by cooldown
        
        # Wait for cooldown to expire
        house.update(6.0)
        assert house.is_available()
        
        # Should be able to dispense again
        candy3 = house.dispense_candy()
        assert len(candy3) > 0
    
    def test_inventory_display_integration(self):
        """Test inventory display shows correct data."""
        kid = self.world.kids[0]
        kid.inventory = {"chocolate": 5, "fruity": 3, "sour": 1}
        
        # Select kid for inventory display
        self.renderer.select_kid_for_inventory(kid)
        
        # Get inventory data
        data = self.renderer.inventory_manager.get_selected_kid_data()
        
        assert data["kid_id"] == kid.id
        assert data["total_candy"] == 9
        assert data["candy_breakdown"]["chocolate"] == 5
        assert data["candy_breakdown"]["fruity"] == 3
        assert data["candy_breakdown"]["sour"] == 1
    
    def test_personality_indicators_integration(self):
        """Test personality indicators are visible on kids."""
        kid = self.world.kids[0]
        kid.personality = PersonalityType.VALUE_INVESTOR
        
        # Render the kid
        self.renderer._render_kid(kid)
        
        # The personality indicator should be rendered
        # (This is tested by ensuring the method doesn't crash)
        assert kid.personality.name == "VALUE_INVESTOR"
    
    def test_collision_detection_integration(self):
        """Test collision detection works in game world."""
        # Position two kids close together
        kid1 = self.world.kids[0]
        kid2 = self.world.kids[1]
        
        kid1.position = Vector2(100, 100)
        kid2.position = Vector2(110, 100)  # Close together
        
        # Update world to trigger collision detection
        self.world.update(0.1, self.renderer)
        
        # Kids should have moved apart due to separation force
        distance = kid1.position.distance_to(kid2.position)
        assert distance > 10  # Should be more than initial 10 units
    
    def test_debug_overlay_integration(self):
        """Test debug overlay shows enhanced information."""
        # Enable debug overlay
        self.renderer.toggle_debug()
        assert self.renderer.debug_enabled == True
        
        # Render debug overlay
        self.renderer._render_debug_overlay(self.world)
        
        # Should show particle count, house cooldowns, personality distribution
        # (This is tested by ensuring the method doesn't crash)
        assert self.renderer.particle_system.get_particle_count() >= 0
    
    def test_help_overlay_integration(self):
        """Test help overlay shows new controls."""
        # Enable help overlay
        self.renderer.toggle_help()
        assert self.renderer.help_enabled == True
        
        # Render help overlay
        self.renderer._render_help_overlay()
        
        # Should include inventory display control
        # (This is tested by ensuring the method doesn't crash)
        assert True  # If we get here, no exceptions were raised
    
    def test_inventory_toggle_integration(self):
        """Test inventory display can be toggled."""
        # Initially disabled
        assert not self.renderer.inventory_display_enabled
        
        # Toggle on
        self.renderer.toggle_inventory_display()
        assert self.renderer.inventory_display_enabled
        
        # Toggle off
        self.renderer.toggle_inventory_display()
        assert not self.renderer.inventory_display_enabled
    
    def test_candy_types_integration(self):
        """Test candy types are properly defined and used."""
        from src.core.candy_types import CandyTypes
        
        # Test candy type colors
        chocolate_color = CandyTypes.get_color("CHOCOLATE")
        assert chocolate_color == (139, 69, 19)
        
        # Test candy type icons
        chocolate_icon = CandyTypes.get_icon("CHOCOLATE")
        assert chocolate_icon == "C"
        
        # Test unknown candy type fallback
        unknown_color = CandyTypes.get_color("unknown")
        assert unknown_color == (255, 255, 255)  # Default white
    
    def test_house_cooldown_visualization_integration(self):
        """Test house cooldown visualization is rendered."""
        house = self.world.houses[0]
        
        # Dispense candy to start cooldown
        house.dispense_candy()
        assert house.dispense_cooldown > 0
        
        # Render house with cooldown
        self.renderer._render_house(house)
        
        # Should render cooldown indicator
        # (This is tested by ensuring the method doesn't crash)
        assert house.get_cooldown_progress() < 1.0
    
    def test_complete_game_loop_integration(self):
        """Test complete game loop with all polish features."""
        # Update world multiple times
        for _ in range(10):
            self.world.update(0.1, self.renderer)
        
        # Render world
        self.renderer.render_world(self.world, 0.1)
        
        # All systems should be working
        assert len(self.world.kids) > 0
        assert len(self.world.houses) > 0
        assert self.renderer.particle_system is not None
        assert self.renderer.inventory_manager is not None
    
    def test_performance_with_polish_features(self):
        """Test performance is maintained with polish features."""
        import time
        
        # Time the update and render cycle
        start_time = time.time()
        
        for _ in range(100):  # 100 update cycles
            self.world.update(0.016, self.renderer)  # ~60 FPS
            self.renderer.render_world(self.world, 0.016)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 100 cycles in reasonable time (< 5 seconds)
        assert total_time < 5.0
        
        # Average time per cycle should be reasonable (< 50ms)
        avg_time_per_cycle = total_time / 100
        assert avg_time_per_cycle < 0.05
