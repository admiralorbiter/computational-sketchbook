"""
House entity class.

Represents houses that dispense candy to kids during trick-or-treating.
Houses can be cursed or blessed to affect the quality of candy they give out.
"""

from typing import List, Dict, Any, Optional
from ..utils.vector2 import Vector2
from .base_entity import BaseEntity


class House(BaseEntity):
    """
    Represents a house that dispenses candy to trick-or-treaters.
    
    Houses have different quality levels and can be affected by player powers
    (curse/bless) to manipulate the candy economy.
    """
    
    def __init__(self, house_id: str, position: Vector2 = None, quality: int = 1):
        """
        Initialize a house entity.
        
        Args:
            house_id: Unique identifier for this house
            position: Position of the house
            quality: House quality level (1=low, 2=mid, 3=high)
        """
        super().__init__(house_id, position)
        
        # House properties
        self.quality = quality  # Quality level (1, 2, or 3)
        self.candy_quality = self._get_quality_multiplier(quality)  # Multiplier for candy quality
        self.candy_types: List[str] = self._get_default_candy_types(quality)  # Types of candy this house gives
        self.dispense_rate = 0.0  # How often it dispenses candy (seconds) - 0 means can dispense immediately
        self.dispense_timer = 1.0  # Start ready to dispense
        self.dispense_cooldown = 0.0  # Cooldown after dispensing candy
        self.last_dispense_time = 0.0  # Time when candy was last dispensed
        
        # Power effects
        self.curse_timer = 0.0  # Time remaining for curse effect
        self.bless_timer = 0.0  # Time remaining for bless effect
        self.quality_multiplier = 1.0  # Current quality multiplier
        
        # Visual properties
        self.house_type = "normal"  # normal, spooky, mansion, etc.
        self.attraction_radius = self._get_attraction_radius(quality)  # How far kids are attracted to this house
    
    def _get_quality_multiplier(self, quality: int) -> float:
        """Get candy quality multiplier based on house quality level."""
        quality_multipliers = {1: 0.5, 2: 1.0, 3: 1.5}
        return quality_multipliers.get(quality, 1.0)
    
    def _get_default_candy_types(self, quality: int) -> List[str]:
        """Get default candy types based on house quality level."""
        if quality == 1:  # Low quality
            return ["trash", "health"]
        elif quality == 2:  # Mid quality
            return ["fruity", "novelty"]
        else:  # High quality
            return ["chocolate", "sour", "fruity"]
    
    def _get_attraction_radius(self, quality: int) -> float:
        """Get attraction radius based on house quality level."""
        attraction_radii = {1: 80.0, 2: 100.0, 3: 120.0}
        return attraction_radii.get(quality, 100.0)
        
    def update(self, dt: float):
        """Update house state."""
        super().update(dt)
        
        if not self.active:
            return
        
        # Update power effect timers
        self._update_power_effects(dt)
        
        # Update dispense timer
        self.dispense_timer += dt
        
        # Update cooldown timer
        if self.dispense_cooldown > 0:
            self.dispense_cooldown -= dt
            if self.dispense_cooldown < 0:
                self.dispense_cooldown = 0
    
    def _update_power_effects(self, dt: float):
        """Update curse and bless effect timers."""
        if self.curse_timer > 0:
            self.curse_timer -= dt
            if self.curse_timer <= 0:
                self._remove_curse()
        
        if self.bless_timer > 0:
            self.bless_timer -= dt
            if self.bless_timer <= 0:
                self._remove_bless()
    
    def curse(self, duration: float = 60.0, quality_multiplier: float = 0.3):
        """
        Apply curse effect to the house.
        
        Args:
            duration: How long the curse lasts (seconds)
            quality_multiplier: Quality multiplier during curse (0.1 to 1.0)
        """
        self.curse_timer = duration
        self.quality_multiplier = quality_multiplier
        print(f"House {self.id} cursed for {duration} seconds")
    
    def bless(self, duration: float = 30.0, quality_multiplier: float = 2.5):
        """
        Apply bless effect to the house.
        
        Args:
            duration: How long the blessing lasts (seconds)
            quality_multiplier: Quality multiplier during blessing (1.0 to 3.0)
        """
        self.bless_timer = duration
        self.quality_multiplier = quality_multiplier
        print(f"House {self.id} blessed for {duration} seconds")
    
    def _remove_curse(self):
        """Remove curse effect."""
        self.curse_timer = 0.0
        self.quality_multiplier = 1.0
        print(f"House {self.id} curse removed")
    
    def _remove_bless(self):
        """Remove bless effect."""
        self.bless_timer = 0.0
        self.quality_multiplier = 1.0
        print(f"House {self.id} blessing removed")
    
    def is_cursed(self) -> bool:
        """Check if house is currently cursed."""
        return self.curse_timer > 0
    
    def is_blessed(self) -> bool:
        """Check if house is currently blessed."""
        return self.bless_timer > 0
    
    def can_dispense_candy(self) -> bool:
        """Check if house can dispense candy now."""
        return self.dispense_timer >= self.dispense_rate and self.dispense_cooldown <= 0
    
    def dispense_candy(self) -> Dict[str, int]:
        """
        Dispense candy to a kid.
        
        Returns:
            Dictionary of candy types and quantities given
        """
        if not self.can_dispense_candy():
            return {}
        
        # Reset dispense timer and set cooldown
        self.dispense_timer = 0.0
        self.dispense_cooldown = 5.0  # 5 second cooldown after dispensing
        self.last_dispense_time = self.dispense_timer
        
        # Calculate candy based on quality
        candy_given = {}
        
        for candy_type in self.candy_types:
            # Base quantity (1-3 pieces)
            import random
            base_quantity = random.randint(1, 3)
            
            # Apply quality multiplier
            final_quantity = int(base_quantity * self.quality_multiplier)
            final_quantity = max(1, final_quantity)  # Always give at least 1
            
            candy_given[candy_type] = final_quantity
        
        return candy_given
    
    def get_attraction_strength(self, kid_position: Vector2) -> float:
        """
        Calculate how attractive this house is to a kid.
        
        Args:
            kid_position: Position of the kid
            
        Returns:
            Attraction strength (0.0 to 1.0)
        """
        distance = self.position.distance_to(kid_position)
        
        if distance > self.attraction_radius:
            return 0.0
        
        # Closer houses are more attractive
        attraction = 1.0 - (distance / self.attraction_radius)
        
        # Blessed houses are more attractive
        if self.is_blessed():
            attraction *= 1.5
        
        # Cursed houses are less attractive
        if self.is_cursed():
            attraction *= 0.3
        
        return min(1.0, attraction)
    
    def set_candy_types(self, candy_types: List[str]):
        """Set the types of candy this house dispenses."""
        self.candy_types = candy_types
    
    def add_candy_type(self, candy_type: str):
        """Add a candy type to this house."""
        if candy_type not in self.candy_types:
            self.candy_types.append(candy_type)
    
    def set_house_type(self, house_type: str):
        """Set the type of house (affects visual appearance)."""
        self.house_type = house_type
        
        # Adjust properties based on house type
        if house_type == "mansion":
            self.candy_quality = 1.5
            self.attraction_radius = 150.0
        elif house_type == "spooky":
            self.candy_quality = 0.8
            self.attraction_radius = 80.0
        elif house_type == "normal":
            self.candy_quality = 1.0
            self.attraction_radius = 100.0
    
    def render(self, screen, camera=None):
        """Render the house."""
        super().render(screen, camera)
        
        if not self.visible or not self.active:
            return
        
        import pygame
        
        # Convert world position to screen position
        if camera:
            screen_pos = camera.world_to_screen(self.position)
        else:
            screen_pos = self.position
        
        # Draw house as a rectangle
        house_rect = pygame.Rect(
            screen_pos.x - 20, screen_pos.y - 15,
            40, 30
        )
        
        # Choose color based on house state and quality
        if self.is_blessed():
            color = (100, 255, 100)  # Green for blessed
        elif self.is_cursed():
            color = (255, 100, 100)  # Red for cursed
        else:
            # Color based on quality level
            if self.quality == 1:  # Low quality
                color = (150, 150, 150)  # Gray
            elif self.quality == 2:  # Mid quality
                color = (139, 69, 19)  # Brown
            else:  # High quality
                color = (255, 215, 0)  # Gold
        
        pygame.draw.rect(screen, color, house_rect)
        pygame.draw.rect(screen, (0, 0, 0), house_rect, 2)
        
        # Draw power effect indicators
        if self.is_blessed() or self.is_cursed():
            effect_color = (255, 255, 0) if self.is_blessed() else (255, 0, 0)
            pygame.draw.circle(screen, effect_color, 
                             screen_pos.to_int_tuple(), 25, 2)
    
    def get_cooldown_progress(self) -> float:
        """Get cooldown progress as 0.0-1.0 (1.0 = ready, 0.0 = just dispensed)."""
        if self.dispense_cooldown <= 0:
            return 1.0
        
        # Calculate progress (1.0 when cooldown is 0, 0.0 when cooldown is at max)
        max_cooldown = 5.0  # Default cooldown time
        progress = max(0.0, 1.0 - (self.dispense_cooldown / max_cooldown))
        return progress
    
    def is_available(self) -> bool:
        """Check if house is available to dispense candy."""
        return self.dispense_cooldown <= 0
    
    def get_next_available_time(self) -> float:
        """Get time until house is available again."""
        return max(0.0, self.dispense_cooldown)
