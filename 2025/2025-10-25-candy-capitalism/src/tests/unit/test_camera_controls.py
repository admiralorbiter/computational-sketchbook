"""
Unit tests for camera controls functionality.
"""

import pytest
import pygame
from src.core.game import PlayingState
from src.systems.game_world import GameWorld
from src.rendering.renderer import Renderer
from src.utils.vector2 import Vector2


class TestCameraControls:
    """Test camera controls functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Initialize pygame for testing
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        
        # Create game state
        self.playing_state = PlayingState()
        self.playing_state.world = GameWorld()
        self.playing_state.renderer = Renderer(self.screen)
        
        # Generate map
        self.playing_state.world.generate_map("default", seed=42)
        self.playing_state.world.spawn_kids(5)
    
    def teardown_method(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_arrow_key_movement(self):
        """Test arrow key camera movement."""
        initial_pos = self.playing_state.renderer.camera.position
        
        # Test right arrow
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        result = self.playing_state.handle_event(event)
        
        assert result == True
        new_pos = self.playing_state.renderer.camera.position
        assert new_pos.x > initial_pos.x
        assert new_pos.y == initial_pos.y
    
    def test_zoom_controls(self):
        """Test zoom controls."""
        initial_zoom = self.playing_state.renderer.camera.zoom
        
        # Test zoom in
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_EQUALS)
        result = self.playing_state.handle_event(event)
        
        assert result == True
        new_zoom = self.playing_state.renderer.camera.zoom
        assert new_zoom > initial_zoom
    
    def test_mouse_wheel_zoom(self):
        """Test mouse wheel zoom."""
        initial_zoom = self.playing_state.renderer.camera.zoom
        
        # Test zoom in (scroll up)
        event = pygame.event.Event(pygame.MOUSEWHEEL, y=1)
        result = self.playing_state.handle_event(event)
        
        assert result == True
        new_zoom = self.playing_state.renderer.camera.zoom
        assert new_zoom > initial_zoom
    
    def test_reset_camera(self):
        """Test camera reset functionality."""
        # Move camera away from center
        self.playing_state.renderer.camera.set_position(Vector2(500, 500))
        self.playing_state.renderer.camera.set_zoom(2.0)
        
        # Reset camera
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)
        result = self.playing_state.handle_event(event)
        
        assert result == True
        assert self.playing_state.renderer.camera.position == Vector2(1000, 1000)
        assert self.playing_state.renderer.camera.zoom == 0.5
    
    def test_help_toggle(self):
        """Test help overlay toggle."""
        initial_help = self.playing_state.renderer.help_enabled
        
        # Toggle help
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h)
        result = self.playing_state.handle_event(event)
        
        assert result == True
        assert self.playing_state.renderer.help_enabled != initial_help
    
    def test_debug_toggle(self):
        """Test debug overlay toggle."""
        initial_debug = self.playing_state.renderer.debug_enabled
        
        # Toggle debug
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F3)
        result = self.playing_state.handle_event(event)
        
        assert result == True
        assert self.playing_state.renderer.debug_enabled != initial_debug
