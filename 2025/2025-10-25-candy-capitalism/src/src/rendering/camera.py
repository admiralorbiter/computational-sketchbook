"""
Camera system for world-to-screen coordinate conversion.

Handles camera positioning, zoom, and coordinate transformations
for rendering the game world.
"""

from typing import Tuple
from ..utils.vector2 import Vector2
from ..core.constants import SCREEN_SIZE


class Camera:
    """
    Camera system for world-to-screen coordinate conversion.
    
    Handles camera positioning, zoom, and smooth transitions
    for rendering the game world.
    """
    
    def __init__(self, position: Vector2 = None, zoom: float = 1.0):
        """
        Initialize the camera.
        
        Args:
            position: Initial camera position in world space
            zoom: Initial zoom level
        """
        self.position = position or Vector2(0, 0)
        self.zoom = zoom
        self.target_position = self.position
        self.target_zoom = self.zoom
        
        # Camera bounds
        self.bounds = None  # (min_x, min_y, max_x, max_y)
        
        # Smooth movement
        self.move_speed = 5.0
        self.zoom_speed = 2.0
        
    def update(self, dt: float):
        """
        Update camera position and zoom.
        
        Args:
            dt: Delta time in seconds
        """
        # Smooth movement to target
        if self.position != self.target_position:
            direction = self.target_position - self.position
            distance = direction.length()
            
            if distance > 1.0:  # Don't jitter
                move_distance = self.move_speed * dt
                if move_distance >= distance:
                    self.position = self.target_position
                else:
                    self.position += direction.normalize() * move_distance
        
        # Smooth zoom to target
        if abs(self.zoom - self.target_zoom) > 0.01:
            zoom_diff = self.target_zoom - self.zoom
            zoom_change = self.zoom_speed * dt
            
            if abs(zoom_diff) <= zoom_change:
                self.zoom = self.target_zoom
            else:
                self.zoom += zoom_diff * zoom_change
        
        # Apply bounds
        if self.bounds:
            self.position.x = max(self.bounds[0], min(self.bounds[2], self.position.x))
            self.position.y = max(self.bounds[1], min(self.bounds[3], self.position.y))
    
    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_pos: Position in world space
            
        Returns:
            Position in screen space
        """
        # Translate to camera-relative position
        relative_pos = world_pos - self.position
        
        # Apply zoom
        screen_pos = relative_pos * self.zoom
        
        # Translate to screen center
        screen_pos += Vector2(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
        
        return screen_pos
    
    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_pos: Position in screen space
            
        Returns:
            Position in world space
        """
        # Translate from screen center
        relative_pos = screen_pos - Vector2(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
        
        # Apply inverse zoom
        world_pos = relative_pos / self.zoom
        
        # Translate to world position
        world_pos += self.position
        
        return world_pos
    
    def set_position(self, position: Vector2, smooth: bool = True):
        """
        Set camera position.
        
        Args:
            position: New camera position
            smooth: Whether to smoothly move to position
        """
        if smooth:
            self.target_position = position
        else:
            self.position = position
            self.target_position = position
    
    def set_zoom(self, zoom: float, smooth: bool = True):
        """
        Set camera zoom level.
        
        Args:
            zoom: New zoom level
            smooth: Whether to smoothly zoom to level
        """
        zoom = max(0.1, min(5.0, zoom))  # Clamp zoom
        
        if smooth:
            self.target_zoom = zoom
        else:
            self.zoom = zoom
            self.target_zoom = zoom
    
    def zoom_in(self, factor: float = 1.2):
        """Zoom in by a factor."""
        self.set_zoom(self.target_zoom * factor, smooth=False)
    
    def zoom_out(self, factor: float = 1.2):
        """Zoom out by a factor."""
        self.set_zoom(self.target_zoom / factor, smooth=False)
    
    def move_to(self, position: Vector2, smooth: bool = True):
        """Move camera to a specific position."""
        self.set_position(position, smooth)
    
    def follow(self, target: Vector2, smooth: bool = True):
        """Follow a target position."""
        self.set_position(target, smooth)
    
    def set_bounds(self, min_x: float, min_y: float, max_x: float, max_y: float):
        """
        Set camera bounds.
        
        Args:
            min_x: Minimum x position
            min_y: Minimum y position
            max_x: Maximum x position
            max_y: Maximum y position
        """
        self.bounds = (min_x, min_y, max_x, max_y)
    
    def clear_bounds(self):
        """Clear camera bounds."""
        self.bounds = None
    
    def is_position_visible(self, world_pos: Vector2) -> bool:
        """
        Check if a world position is visible on screen.
        
        Args:
            world_pos: Position in world space
            
        Returns:
            True if position is visible
        """
        screen_pos = self.world_to_screen(world_pos)
        
        return (0 <= screen_pos.x <= SCREEN_SIZE[0] and 
                0 <= screen_pos.y <= SCREEN_SIZE[1])
    
    def get_visible_bounds(self) -> Tuple[float, float, float, float]:
        """
        Get the visible world bounds.
        
        Returns:
            Tuple of (min_x, min_y, max_x, max_y) in world space
        """
        # Convert screen corners to world space
        top_left = self.screen_to_world(Vector2(0, 0))
        bottom_right = self.screen_to_world(Vector2(SCREEN_SIZE[0], SCREEN_SIZE[1]))
        
        return (top_left.x, top_left.y, bottom_right.x, bottom_right.y)
    
    def get_zoom_level(self) -> float:
        """Get current zoom level."""
        return self.zoom
    
    def get_position(self) -> Vector2:
        """Get current camera position."""
        return self.position
    
    def is_moving(self) -> bool:
        """Check if camera is currently moving."""
        return (self.position != self.target_position or 
                abs(self.zoom - self.target_zoom) > 0.01)
