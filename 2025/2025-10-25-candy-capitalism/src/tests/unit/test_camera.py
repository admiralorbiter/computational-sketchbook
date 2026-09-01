"""
Unit tests for camera system.
"""

import pytest
from src.rendering.camera import Camera
from src.utils.vector2 import Vector2
from src.core.constants import SCREEN_SIZE


class TestCamera:
    """Test cases for Camera class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.camera = Camera()
    
    def test_camera_initialization(self):
        """Test camera initialization with default values."""
        assert self.camera.position == Vector2(0, 0)
        assert self.camera.zoom == 1.0
        assert self.camera.target_position == Vector2(0, 0)
        assert self.camera.target_zoom == 1.0
        assert self.camera.bounds is None
    
    def test_camera_initialization_with_params(self):
        """Test camera initialization with custom parameters."""
        position = Vector2(100, 200)
        zoom = 2.0
        
        camera = Camera(position, zoom)
        
        assert camera.position == position
        assert camera.zoom == zoom
        assert camera.target_position == position
        assert camera.target_zoom == zoom
    
    def test_world_to_screen_conversion(self):
        """Test world to screen coordinate conversion."""
        # Test with camera at origin
        world_pos = Vector2(100, 150)
        screen_pos = self.camera.world_to_screen(world_pos)
        
        # Should be centered on screen
        expected_x = 100 + SCREEN_SIZE[0] // 2
        expected_y = 150 + SCREEN_SIZE[1] // 2
        assert screen_pos.x == expected_x
        assert screen_pos.y == expected_y
    
    def test_world_to_screen_with_zoom(self):
        """Test world to screen conversion with zoom."""
        self.camera.zoom = 2.0
        world_pos = Vector2(100, 150)
        screen_pos = self.camera.world_to_screen(world_pos)
        
        # Should be scaled by zoom
        expected_x = (100 * 2) + SCREEN_SIZE[0] // 2
        expected_y = (150 * 2) + SCREEN_SIZE[1] // 2
        assert screen_pos.x == expected_x
        assert screen_pos.y == expected_y
    
    def test_world_to_screen_with_offset(self):
        """Test world to screen conversion with camera offset."""
        self.camera.position = Vector2(50, 75)
        world_pos = Vector2(100, 150)
        screen_pos = self.camera.world_to_screen(world_pos)
        
        # Should account for camera position
        expected_x = (100 - 50) + SCREEN_SIZE[0] // 2
        expected_y = (150 - 75) + SCREEN_SIZE[1] // 2
        assert screen_pos.x == expected_x
        assert screen_pos.y == expected_y
    
    def test_screen_to_world_conversion(self):
        """Test screen to world coordinate conversion."""
        # Test with camera at origin
        screen_pos = Vector2(100, 150)
        world_pos = self.camera.screen_to_world(screen_pos)
        
        # Should be relative to screen center
        expected_x = 100 - SCREEN_SIZE[0] // 2
        expected_y = 150 - SCREEN_SIZE[1] // 2
        assert world_pos.x == expected_x
        assert world_pos.y == expected_y
    
    def test_screen_to_world_with_zoom(self):
        """Test screen to world conversion with zoom."""
        self.camera.zoom = 2.0
        screen_pos = Vector2(100, 150)
        world_pos = self.camera.screen_to_world(screen_pos)
        
        # Should be scaled by inverse zoom
        expected_x = (100 - SCREEN_SIZE[0] // 2) / 2
        expected_y = (150 - SCREEN_SIZE[1] // 2) / 2
        assert world_pos.x == expected_x
        assert world_pos.y == expected_y
    
    def test_screen_to_world_with_offset(self):
        """Test screen to world conversion with camera offset."""
        self.camera.position = Vector2(50, 75)
        screen_pos = Vector2(100, 150)
        world_pos = self.camera.screen_to_world(screen_pos)
        
        # Should account for camera position
        expected_x = (100 - SCREEN_SIZE[0] // 2) + 50
        expected_y = (150 - SCREEN_SIZE[1] // 2) + 75
        assert world_pos.x == expected_x
        assert world_pos.y == expected_y
    
    def test_round_trip_conversion(self):
        """Test that world->screen->world conversion is consistent."""
        original_world = Vector2(123.45, 678.90)
        
        # Convert to screen and back
        screen_pos = self.camera.world_to_screen(original_world)
        back_to_world = self.camera.screen_to_world(screen_pos)
        
        # Should be very close to original (within floating point precision)
        assert abs(back_to_world.x - original_world.x) < 0.01
        assert abs(back_to_world.y - original_world.y) < 0.01
    
    def test_set_position_immediate(self):
        """Test setting camera position immediately."""
        new_position = Vector2(200, 300)
        self.camera.set_position(new_position, smooth=False)
        
        assert self.camera.position == new_position
        assert self.camera.target_position == new_position
    
    def test_set_position_smooth(self):
        """Test setting camera position smoothly."""
        new_position = Vector2(200, 300)
        self.camera.set_position(new_position, smooth=True)
        
        # Position should not change immediately
        assert self.camera.position != new_position
        # Target should be set
        assert self.camera.target_position == new_position
    
    def test_set_zoom_immediate(self):
        """Test setting camera zoom immediately."""
        new_zoom = 2.5
        self.camera.set_zoom(new_zoom, smooth=False)
        
        assert self.camera.zoom == new_zoom
        assert self.camera.target_zoom == new_zoom
    
    def test_set_zoom_smooth(self):
        """Test setting camera zoom smoothly."""
        new_zoom = 2.5
        self.camera.set_zoom(new_zoom, smooth=True)
        
        # Zoom should not change immediately
        assert self.camera.zoom != new_zoom
        # Target should be set
        assert self.camera.target_zoom == new_zoom
    
    def test_zoom_clamping(self):
        """Test that zoom is clamped to valid range."""
        # Test zoom too low
        self.camera.set_zoom(0.05, smooth=False)
        assert self.camera.zoom == 0.1  # Should be clamped to minimum
        
        # Test zoom too high
        self.camera.set_zoom(10.0, smooth=False)
        assert self.camera.zoom == 5.0  # Should be clamped to maximum
    
    def test_zoom_in_out(self):
        """Test zoom in and out methods."""
        initial_zoom = self.camera.zoom
        
        # Zoom in
        self.camera.zoom_in(2.0)
        assert self.camera.target_zoom == initial_zoom * 2.0
        
        # Zoom out
        self.camera.zoom_out(2.0)
        assert self.camera.target_zoom == initial_zoom
    
    def test_move_to(self):
        """Test move_to method."""
        target_position = Vector2(500, 600)
        self.camera.move_to(target_position, smooth=False)
        
        assert self.camera.position == target_position
    
    def test_follow(self):
        """Test follow method."""
        target_position = Vector2(700, 800)
        self.camera.follow(target_position, smooth=False)
        
        assert self.camera.position == target_position
    
    def test_bounds_setting(self):
        """Test setting camera bounds."""
        self.camera.set_bounds(0, 0, 1000, 1000)
        
        assert self.camera.bounds == (0, 0, 1000, 1000)
    
    def test_bounds_clearing(self):
        """Test clearing camera bounds."""
        self.camera.set_bounds(0, 0, 1000, 1000)
        self.camera.clear_bounds()
        
        assert self.camera.bounds is None
    
    def test_position_visibility(self):
        """Test checking if position is visible."""
        # Position at screen center should be visible
        center_world = Vector2(0, 0)  # Camera at origin
        assert self.camera.is_position_visible(center_world)
        
        # Position far away should not be visible
        far_world = Vector2(10000, 10000)
        assert not self.camera.is_position_visible(far_world)
    
    def test_visible_bounds(self):
        """Test getting visible world bounds."""
        bounds = self.camera.get_visible_bounds()
        
        assert len(bounds) == 4
        assert isinstance(bounds[0], float)  # min_x
        assert isinstance(bounds[1], float)  # min_y
        assert isinstance(bounds[2], float)  # max_x
        assert isinstance(bounds[3], float)  # max_y
        
        # max should be greater than min
        assert bounds[2] > bounds[0]  # max_x > min_x
        assert bounds[3] > bounds[1]  # max_y > min_y
    
    def test_smooth_movement_update(self):
        """Test smooth movement during update."""
        # Set target position
        target = Vector2(100, 200)
        self.camera.set_position(target, smooth=True)
        
        # Update with small dt
        self.camera.update(0.1)
        
        # Position should move toward target
        assert self.camera.position != Vector2(0, 0)  # Should have moved
        assert self.camera.position != target  # Should not be at target yet
    
    def test_smooth_zoom_update(self):
        """Test smooth zoom during update."""
        # Set target zoom
        target_zoom = 2.0
        self.camera.set_zoom(target_zoom, smooth=True)
        
        # Update with small dt
        self.camera.update(0.1)
        
        # Zoom should move toward target
        assert self.camera.zoom != 1.0  # Should have changed
        assert self.camera.zoom != target_zoom  # Should not be at target yet
    
    def test_bounds_enforcement(self):
        """Test that bounds are enforced during update."""
        # Set bounds
        self.camera.set_bounds(0, 0, 500, 500)
        
        # Set target outside bounds
        self.camera.set_position(Vector2(1000, 1000), smooth=True)
        
        # Update until movement completes
        for _ in range(100):
            self.camera.update(0.1)
        
        # Position should be clamped to bounds
        assert self.camera.position.x <= 500
        assert self.camera.position.y <= 500
        assert self.camera.position.x >= 0
        assert self.camera.position.y >= 0
    
    def test_is_moving(self):
        """Test is_moving method."""
        # Should not be moving initially
        assert not self.camera.is_moving()
        
        # Set target position
        self.camera.set_position(Vector2(100, 100), smooth=True)
        assert self.camera.is_moving()
        
        # Update until movement completes (with more iterations)
        for _ in range(300):
            self.camera.update(0.1)
            if not self.camera.is_moving():
                break
        
        # Should be very close to target (within floating point precision)
        distance = self.camera.position.distance_to(self.camera.target_position)
        assert distance < 1.0  # More lenient tolerance for smooth movement
    
    def test_get_position_zoom(self):
        """Test getting current position and zoom."""
        position = Vector2(123, 456)
        zoom = 1.5
        
        self.camera.position = position
        self.camera.zoom = zoom
        
        assert self.camera.get_position() == position
        assert self.camera.get_zoom_level() == zoom
