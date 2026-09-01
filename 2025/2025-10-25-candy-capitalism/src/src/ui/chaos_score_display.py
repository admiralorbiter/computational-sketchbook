"""
Chaos score display HUD element.

Shows total chaos points earned with floating gain indicators
and recent activity tracking.
"""

import pygame
from typing import List, Tuple, Optional
from .ui_element import UIElement
from ..core.constants import COLORS


class ChaosScoreDisplay(UIElement):
    """
    Chaos score display showing total points and recent gains.
    
    Displays large score text with floating "+X" indicators
    when points are earned.
    """
    
    def __init__(self, screen_width: int, y: int = 20):
        """
        Initialize chaos score display.
        
        Args:
            screen_width: Width of the screen for centering
            y: Y position on screen
        """
        # Calculate centered position
        width = 200
        x = (screen_width - width) // 2
        
        super().__init__(pygame.Rect(x, y, width, 60))
        
        # Visual properties
        self.text_color = COLORS['WHITE']
        self.gain_color = COLORS['GREEN']
        self.loss_color = COLORS['RED']
        
        # Fonts
        self.score_font = pygame.font.Font(None, 36)
        self.gain_font = pygame.font.Font(None, 24)
        
        # Score tracking
        self.current_score = 0
        self.target_score = 0  # For smooth counting animation
        
        # Floating gain indicators
        self.floating_gains: List[Tuple[str, float, float, float, float]] = []
        # Format: (text, x, y, timer, duration)
        
        # Animation
        self.count_up_speed = 50.0  # Points per second when counting up
        
    def update(self, dt: float):
        """Update chaos score display."""
        super().update(dt)
        
        # Animate score counting up
        if self.target_score > self.current_score:
            points_to_add = self.count_up_speed * dt
            self.current_score = min(self.target_score, self.current_score + points_to_add)
        
        # Update floating gains
        for i in range(len(self.floating_gains) - 1, -1, -1):
            text, x, y, timer, duration = self.floating_gains[i]
            timer += dt
            
            if timer >= duration:
                self.floating_gains.pop(i)
            else:
                # Update position (float upward)
                new_y = y - 30 * dt
                self.floating_gains[i] = (text, x, new_y, timer, duration)
    
    def render(self, screen: pygame.Surface):
        """Render the chaos score display."""
        if not self.visible:
            return
        
        # Draw main score
        self._render_main_score(screen)
        
        # Draw floating gains
        self._render_floating_gains(screen)
    
    def _render_main_score(self, screen: pygame.Surface):
        """Render the main chaos score."""
        score_text = f"Chaos: {int(self.current_score):,} pts"
        score_surface = self.score_font.render(score_text, True, self.text_color)
        
        # Center the text
        score_rect = score_surface.get_rect(center=self.rect.center)
        screen.blit(score_surface, score_rect)
    
    def _render_floating_gains(self, screen: pygame.Surface):
        """Render floating gain indicators."""
        for text, x, y, timer, duration in self.floating_gains:
            # Calculate alpha based on remaining time
            alpha = int(255 * (1.0 - timer / duration))
            alpha = max(0, min(255, alpha))
            
            # Create surface with alpha
            gain_surface = self.gain_font.render(text, True, self.gain_color)
            
            # Apply alpha (simplified - in a real implementation you'd use proper alpha blending)
            if alpha < 255:
                # Create a temporary surface for alpha blending
                temp_surface = pygame.Surface(gain_surface.get_size(), pygame.SRCALPHA)
                temp_surface.blit(gain_surface, (0, 0))
                temp_surface.set_alpha(alpha)
                screen.blit(temp_surface, (int(x), int(y)))
            else:
                screen.blit(gain_surface, (int(x), int(y)))
    
    def add_chaos_points(self, points: int, source: str = ""):
        """
        Add chaos points with floating indicator.
        
        Args:
            points: Points to add (can be negative)
            source: Source of the points (for debugging)
        """
        self.target_score += points
        
        # Create floating gain indicator
        if points > 0:
            text = f"+{points}"
            color = self.gain_color
        else:
            text = str(points)  # Will show as negative
            color = self.loss_color
        
        # Position near the score display
        gain_x = self.rect.centerx + 20
        gain_y = self.rect.centery
        
        # Add to floating gains list
        duration = 2.0  # 2 seconds
        self.floating_gains.append((text, gain_x, gain_y, 0.0, duration))
        
        print(f"Chaos points: {points} (source: {source}) - Total: {self.target_score}")
    
    def set_chaos_score(self, score: int):
        """Set the chaos score directly."""
        self.current_score = score
        self.target_score = score
    
    def get_chaos_score(self) -> int:
        """Get current chaos score."""
        return int(self.current_score)
    
    def reset_score(self):
        """Reset chaos score to zero."""
        self.current_score = 0
        self.target_score = 0
        self.floating_gains.clear()
    
    def on_chaos_event(self, event_type: str, points: int, details: str = ""):
        """
        Handle chaos events from the game.
        
        Args:
            event_type: Type of chaos event (e.g., "bad_trade", "house_curse")
            points: Points earned/lost
            details: Additional details about the event
        """
        self.add_chaos_points(points, f"{event_type}: {details}")
    
    def get_score_summary(self) -> dict:
        """Get a summary of the current score state."""
        return {
            'current_score': int(self.current_score),
            'target_score': self.target_score,
            'floating_gains_count': len(self.floating_gains),
            'is_counting_up': self.target_score > self.current_score
        }
