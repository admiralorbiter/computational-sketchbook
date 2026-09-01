"""
Possessed kid info panel HUD element.

Shows information about the currently possessed kid including
inventory, personality, mood, and personal goal.
"""

import pygame
from typing import Optional, Dict, Any
from .ui_element import UIElement
from ..core.constants import COLORS


class KidInfoPanel(UIElement):
    """
    Info panel showing details about the currently possessed kid.
    
    Only visible when possessing a kid, shows inventory, personality,
    mood, and other relevant information.
    """
    
    def __init__(self, x: int = 20, y: int = 60, width: int = 250, height: int = 120):
        """
        Initialize kid info panel.
        
        Args:
            x: X position on screen
            y: Y position on screen
            width: Width of the panel
            height: Height of the panel
        """
        super().__init__(pygame.Rect(x, y, width, height))
        
        # Visual properties
        self.background_color = (30, 30, 40)
        self.border_color = COLORS['WHITE']
        self.border_width = 2
        self.text_color = COLORS['WHITE']
        self.title_color = COLORS['YELLOW']
        
        # Fonts
        self.title_font = pygame.font.Font(None, 18)
        self.text_font = pygame.font.Font(None, 14)
        self.small_font = pygame.font.Font(None, 12)
        
        # Layout
        self.padding = 8
        self.line_height = 16
        
        # Possession system reference
        self.possession_system = None
        
    def update(self, dt: float):
        """Update kid info panel."""
        super().update(dt)
        
        # Only visible when possessing a kid
        if self.possession_system and self.possession_system.is_possessing():
            self.visible = True
        else:
            self.visible = False
    
    def render(self, screen: pygame.Surface):
        """Render the kid info panel."""
        if not self.visible or not self.possession_system:
            return
        
        possessed_kid = self.possession_system.get_possessed_kid()
        if not possessed_kid:
            return
        
        # Draw background
        pygame.draw.rect(screen, self.background_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)
        
        # Draw content
        self._render_title(screen, possessed_kid)
        self._render_personality(screen, possessed_kid)
        self._render_mood(screen, possessed_kid)
        self._render_inventory(screen, possessed_kid)
        self._render_personal_goal(screen, possessed_kid)
        self._render_release_instruction(screen)
    
    def _render_title(self, screen: pygame.Surface, kid):
        """Render kid name and ID."""
        title_text = f"Possessed: {kid.id}"
        title_surface = self.title_font.render(title_text, True, self.title_color)
        
        title_x = self.rect.x + self.padding
        title_y = self.rect.y + self.padding
        
        screen.blit(title_surface, (title_x, title_y))
    
    def _render_personality(self, screen: pygame.Surface, kid):
        """Render personality type."""
        personality_text = f"Personality: {kid.personality.name if hasattr(kid, 'personality') else 'Unknown'}"
        personality_surface = self.text_font.render(personality_text, True, self.text_color)
        
        personality_x = self.rect.x + self.padding
        personality_y = self.rect.y + self.padding + self.line_height
        
        screen.blit(personality_surface, (personality_x, personality_y))
    
    def _render_mood(self, screen: pygame.Surface, kid):
        """Render current mood."""
        mood_text = f"Mood: {kid.mood.name if hasattr(kid, 'mood') else 'Unknown'}"
        mood_surface = self.text_font.render(mood_text, True, self.text_color)
        
        mood_x = self.rect.x + self.padding
        mood_y = self.rect.y + self.padding + self.line_height * 2
        
        screen.blit(mood_surface, (mood_x, mood_y))
    
    def _render_inventory(self, screen: pygame.Surface, kid):
        """Render inventory summary."""
        if not hasattr(kid, 'inventory') or not kid.inventory:
            return
        
        # Count total candy
        total_candy = sum(kid.inventory.values())
        
        # Show top 3 candy types by quantity
        sorted_candy = sorted(kid.inventory.items(), key=lambda x: x[1], reverse=True)
        top_candy = sorted_candy[:3]
        
        inventory_text = f"Inventory ({total_candy} total):"
        inventory_surface = self.text_font.render(inventory_text, True, self.text_color)
        
        inventory_x = self.rect.x + self.padding
        inventory_y = self.rect.y + self.padding + self.line_height * 3
        
        screen.blit(inventory_surface, (inventory_x, inventory_y))
        
        # Show top candy types
        for i, (candy_type, quantity) in enumerate(top_candy):
            if quantity > 0:
                candy_text = f"  {candy_type}: {quantity}"
                candy_surface = self.small_font.render(candy_text, True, self.text_color)
                
                candy_x = self.rect.x + self.padding
                candy_y = inventory_y + self.line_height + (i * 12)
                
                screen.blit(candy_surface, (candy_x, candy_y))
    
    def _render_personal_goal(self, screen: pygame.Surface, kid):
        """Render personal goal (if implemented)."""
        if hasattr(kid, 'personal_goal') and kid.personal_goal:
            goal_text = f"Goal: {kid.personal_goal.type if hasattr(kid.personal_goal, 'type') else 'Unknown'}"
            goal_surface = self.small_font.render(goal_text, True, COLORS['CYAN'])
            
            goal_x = self.rect.x + self.padding
            goal_y = self.rect.bottom - self.padding - self.line_height
            
            screen.blit(goal_surface, (goal_x, goal_y))
    
    def _render_release_instruction(self, screen: pygame.Surface):
        """Render instruction on how to release possession."""
        instruction_text = "Press ESC or Right-Click to release"
        instruction_surface = self.small_font.render(instruction_text, True, COLORS['YELLOW'])
        
        instruction_x = self.rect.x + self.padding
        instruction_y = self.rect.bottom - self.padding - 12
        
        screen.blit(instruction_surface, (instruction_x, instruction_y))
    
    def set_possession_system(self, possession_system):
        """Set the possession system to monitor."""
        self.possession_system = possession_system
    
    def get_kid_summary(self) -> Dict[str, Any]:
        """Get a summary of the possessed kid's information."""
        if not self.possession_system or not self.possession_system.is_possessing():
            return {}
        
        kid = self.possession_system.get_possessed_kid()
        if not kid:
            return {}
        
        return {
            'id': kid.id,
            'personality': kid.personality.name if hasattr(kid, 'personality') else 'Unknown',
            'mood': kid.mood.name if hasattr(kid, 'mood') else 'Unknown',
            'inventory': kid.inventory.copy() if hasattr(kid, 'inventory') else {},
            'total_candy': sum(kid.inventory.values()) if hasattr(kid, 'inventory') else 0,
            'personal_goal': kid.personal_goal.type if hasattr(kid, 'personal_goal') and kid.personal_goal else None
        }
