"""
Energy bar HUD element for displaying chaos energy.

Shows current energy level with visual feedback and recharge rate indicator.
"""

import pygame
from typing import Optional
from .ui_element import UIElement
from ..core.constants import COLORS


class EnergyBar(UIElement):
    """
    Energy bar UI element showing chaos energy level.
    
    Displays current energy as a horizontal bar with color gradient
    and text overlay showing exact values.
    """
    
    def __init__(self, x: int = 20, y: int = 20, width: int = 200, height: int = 30):
        """
        Initialize energy bar.
        
        Args:
            x: X position on screen
            y: Y position on screen
            width: Width of the bar
            height: Height of the bar
        """
        super().__init__(pygame.Rect(x, y, width, height))
        
        # Visual properties
        self.border_width = 2
        self.text_color = COLORS['WHITE']
        self.border_color = COLORS['WHITE']
        
        # Energy colors (gradient from low to high)
        self.low_energy_color = (100, 0, 0)      # Dark red
        self.medium_energy_color = (255, 100, 0)  # Orange
        self.high_energy_color = (255, 255, 0)    # Yellow
        self.max_energy_color = (0, 255, 0)       # Green
        
        # Font
        self.font = pygame.font.Font(None, 20)
        
        # Animation
        self.pulse_timer = 0.0
        self.pulse_speed = 2.0
        
    def update(self, dt: float):
        """Update energy bar animation."""
        super().update(dt)
        
        # Update pulse animation
        self.pulse_timer += dt * self.pulse_speed
        
    def render(self, screen: pygame.Surface):
        """Render the energy bar."""
        if not self.visible:
            return
        
        # Draw background
        pygame.draw.rect(screen, (50, 50, 50), self.rect)
        
        # Calculate fill width based on energy percentage
        possession_system = self.get_possession_system()
        if not possession_system:
            return
        
        energy_percentage = possession_system.get_energy_percentage()
        fill_width = int(self.rect.width * energy_percentage)
        
        if fill_width > 0:
            # Create fill rectangle
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            
            # Calculate color based on energy level
            color = self._get_energy_color(energy_percentage)
            
            # Add pulse effect when energy is low
            if energy_percentage < 0.2:
                pulse_intensity = (1.0 + 0.3 * abs(pygame.math.Vector2(self.pulse_timer).x % 2 - 1))
                color = tuple(int(c * pulse_intensity) for c in color)
            
            # Draw fill
            pygame.draw.rect(screen, color, fill_rect)
        
        # Draw border
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)
        
        # Draw text overlay
        self._render_text(screen, possession_system)
        
        # Draw recharge indicator
        self._render_recharge_indicator(screen, possession_system)
    
    def _get_energy_color(self, percentage: float) -> tuple:
        """Get color based on energy percentage."""
        if percentage <= 0.25:
            # Low energy - red gradient
            t = percentage / 0.25
            return self._lerp_color(self.low_energy_color, self.medium_energy_color, t)
        elif percentage <= 0.5:
            # Medium energy - orange gradient
            t = (percentage - 0.25) / 0.25
            return self._lerp_color(self.medium_energy_color, self.high_energy_color, t)
        elif percentage <= 0.75:
            # High energy - yellow gradient
            t = (percentage - 0.5) / 0.25
            return self._lerp_color(self.high_energy_color, self.max_energy_color, t)
        else:
            # Max energy - green
            return self.max_energy_color
    
    def _lerp_color(self, color1: tuple, color2: tuple, t: float) -> tuple:
        """Linear interpolation between two colors."""
        return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))
    
    def _render_text(self, screen: pygame.Surface, possession_system):
        """Render energy text overlay."""
        current_energy = int(possession_system.current_energy)
        max_energy = int(possession_system.max_energy)
        
        text = f"{current_energy} / {max_energy} Energy"
        text_surface = self.font.render(text, True, self.text_color)
        
        # Center text in bar
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def _render_recharge_indicator(self, screen: pygame.Surface, possession_system):
        """Render recharge rate indicator."""
        if possession_system.current_energy >= possession_system.max_energy:
            return  # No recharge needed
        
        # Draw small arrow indicating recharge
        arrow_size = 8
        arrow_x = self.rect.right + 5
        arrow_y = self.rect.centery
        
        # Arrow pointing right (recharge direction)
        points = [
            (arrow_x, arrow_y - arrow_size // 2),
            (arrow_x + arrow_size, arrow_y),
            (arrow_x, arrow_y + arrow_size // 2)
        ]
        
        pygame.draw.polygon(screen, COLORS['GREEN'], points)
    
    def get_possession_system(self):
        """Get possession system from game world."""
        # Return the possession system that was set via set_possession_system
        return getattr(self, 'possession_system', None)
    
    def set_possession_system(self, possession_system):
        """Set the possession system to monitor."""
        self.possession_system = possession_system
    
    def on_energy_changed(self, old_energy: float, new_energy: float):
        """Called when energy level changes."""
        # Could add visual effects here like flashing or particles
        pass
    
    def on_energy_depleted(self):
        """Called when energy is completely depleted."""
        # Could add warning effects here
        pass
