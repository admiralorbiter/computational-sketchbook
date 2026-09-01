"""
Base entity class for all game entities.

Provides common functionality for position, velocity, update/render hooks,
and basic entity management.
"""

from typing import Optional, Any
from ..utils.vector2 import Vector2


class BaseEntity:
    """
    Base class for all game entities.
    
    Provides common functionality that all entities need:
    - Position and velocity
    - Update and render hooks
    - Basic entity identification
    """
    
    def __init__(self, entity_id: str, position: Vector2 = None):
        """
        Initialize base entity.
        
        Args:
            entity_id: Unique identifier for this entity
            position: Initial position (defaults to origin)
        """
        self.id = entity_id
        self.position = position or Vector2(0, 0)
        self.velocity = Vector2(0, 0)
        self.rotation = 0.0  # In radians
        self.scale = 1.0
        
        # Entity state
        self.active = True
        self.visible = True
        
        # Update timing
        self.last_update_time = 0.0
        
    def update(self, dt: float):
        """
        Update entity state.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.active:
            return
            
        # Update position based on velocity
        self.position += self.velocity * dt
        
        # Update timing
        self.last_update_time += dt
    
    def render(self, screen, camera=None):
        """
        Render the entity.
        
        Args:
            screen: Pygame screen surface
            camera: Camera for coordinate conversion (optional)
        """
        if not self.visible or not self.active:
            return
            
        # Base implementation does nothing
        # Subclasses should override this method
        pass
    
    def set_position(self, position: Vector2):
        """Set entity position."""
        self.position = position
    
    def set_velocity(self, velocity: Vector2):
        """Set entity velocity."""
        self.velocity = velocity
    
    def add_velocity(self, velocity: Vector2):
        """Add to current velocity."""
        self.velocity += velocity
    
    def set_rotation(self, rotation: float):
        """Set entity rotation in radians."""
        self.rotation = rotation
    
    def set_scale(self, scale: float):
        """Set entity scale."""
        self.scale = scale
    
    def activate(self):
        """Activate the entity."""
        self.active = True
    
    def deactivate(self):
        """Deactivate the entity."""
        self.active = False
    
    def show(self):
        """Make entity visible."""
        self.visible = True
    
    def hide(self):
        """Hide entity."""
        self.visible = False
    
    def get_distance_to(self, other: 'BaseEntity') -> float:
        """Get distance to another entity."""
        return self.position.distance_to(other.position)
    
    def get_angle_to(self, other: 'BaseEntity') -> float:
        """Get angle to another entity in radians."""
        return self.position.angle_to(other.position)
    
    def move_toward(self, target: Vector2, speed: float, dt: float) -> bool:
        """
        Move toward a target position.
        
        Args:
            target: Target position
            speed: Movement speed in units per second
            dt: Delta time
            
        Returns:
            True if reached target, False otherwise
        """
        direction = target - self.position
        distance = direction.length()
        
        if distance < speed * dt:
            # Close enough to target
            self.position = target
            self.velocity = Vector2(0, 0)
            return True
        
        # Move toward target
        direction = direction.normalize()
        self.velocity = direction * speed
        return False
    
    def look_at(self, target: Vector2):
        """Rotate entity to look at target position."""
        self.rotation = self.position.angle_to(target)
    
    def get_forward_direction(self) -> Vector2:
        """Get forward direction vector based on rotation."""
        from math import cos, sin
        return Vector2(cos(self.rotation), sin(self.rotation))
    
    def get_right_direction(self) -> Vector2:
        """Get right direction vector based on rotation."""
        from math import cos, sin
        return Vector2(-sin(self.rotation), cos(self.rotation))
    
    def __repr__(self) -> str:
        """String representation of entity."""
        return f"{self.__class__.__name__}(id={self.id}, pos={self.position})"
