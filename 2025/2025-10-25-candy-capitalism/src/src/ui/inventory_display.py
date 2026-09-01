"""
Inventory display UI for showing kid candy breakdown.

Displays detailed inventory information for selected kids.
"""

import pygame
from typing import Dict, List, Optional, Tuple
from ..utils.vector2 import Vector2
from ..core.candy_types import CandyTypes


class InventoryDisplay:
    """Displays detailed inventory breakdown for kids."""
    
    def __init__(self):
        self.selected_kid = None
        self.visible = False
        self.position = Vector2(10, 10)  # Top-left corner
        self.width = 400
        self.height = 300
        self.font_size = 16
        self.line_height = 20
    
    def set_selected_kid(self, kid):
        """Set the kid to display inventory for."""
        self.selected_kid = kid
    
    def toggle_visibility(self):
        """Toggle display visibility."""
        self.visible = not self.visible
    
    def show(self):
        """Show the inventory display."""
        self.visible = True
    
    def hide(self):
        """Hide the inventory display."""
        self.visible = False
    
    def render(self, screen: pygame.Surface, font: pygame.font.Font):
        """Render the inventory display."""
        if not self.visible or not self.selected_kid:
            return
        
        # Create background surface
        background = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        background.fill((0, 0, 0, 180))  # Semi-transparent black
        
        # Draw border
        pygame.draw.rect(background, (255, 255, 255), 
                        (0, 0, self.width, self.height), 2)
        
        # Blit background to screen
        screen.blit(background, self.position.to_int_tuple())
        
        # Render inventory content
        self._render_inventory_content(screen, font)
    
    def _render_inventory_content(self, screen: pygame.Surface, font: pygame.font.Font):
        """Render the inventory content."""
        if not self.selected_kid:
            return
        
        y_offset = self.position.y + 10
        x_offset = self.position.x + 10
        
        # Kid ID header
        kid_text = f"Kid: {self.selected_kid.id}"
        text_surface = font.render(kid_text, True, (255, 255, 255))
        screen.blit(text_surface, (x_offset, y_offset))
        y_offset += self.line_height
        
        # Personality
        personality_text = f"Personality: {self.selected_kid.personality.name}"
        text_surface = font.render(personality_text, True, (200, 200, 200))
        screen.blit(text_surface, (x_offset, y_offset))
        y_offset += self.line_height
        
        # Total candy count
        total_candy = sum(self.selected_kid.inventory.values())
        total_text = f"Total Candy: {total_candy}"
        text_surface = font.render(total_text, True, (255, 255, 0))
        screen.blit(text_surface, (x_offset, y_offset))
        y_offset += self.line_height + 5
        
        # Candy breakdown
        if self.selected_kid.inventory:
            breakdown_text = "Candy Breakdown:"
            text_surface = font.render(breakdown_text, True, (255, 255, 255))
            screen.blit(text_surface, (x_offset, y_offset))
            y_offset += self.line_height
            
            for candy_type, count in self.selected_kid.inventory.items():
                if count > 0:
                    # Get candy color and icon
                    color = CandyTypes.get_color(candy_type)
                    icon = CandyTypes.get_icon(candy_type)
                    
                    # Render candy line
                    candy_text = f"  {icon} {candy_type.title()}: {count}"
                    text_surface = font.render(candy_text, True, color)
                    screen.blit(text_surface, (x_offset, y_offset))
                    y_offset += self.line_height
        else:
            no_candy_text = "No candy yet"
            text_surface = font.render(no_candy_text, True, (150, 150, 150))
            screen.blit(text_surface, (x_offset, y_offset))
    
    def get_display_data(self) -> Dict[str, any]:
        """Get formatted inventory data for the selected kid."""
        if not self.selected_kid:
            return {}
        
        return {
            "kid_id": self.selected_kid.id,
            "personality": self.selected_kid.personality.name,
            "total_candy": sum(self.selected_kid.inventory.values()),
            "candy_breakdown": dict(self.selected_kid.inventory),
            "candy_details": {
                candy_type: {
                    "count": count,
                    "color": CandyTypes.get_color(candy_type),
                    "icon": CandyTypes.get_icon(candy_type)
                }
                for candy_type, count in self.selected_kid.inventory.items()
                if count > 0
            }
        }


class InventoryManager:
    """Manages inventory displays for multiple kids."""
    
    def __init__(self):
        self.displays: Dict[str, InventoryDisplay] = {}
        self.selected_kid_id = None
        self.main_display = InventoryDisplay()
    
    def select_kid(self, kid):
        """Select a kid to show inventory for."""
        self.selected_kid_id = kid.id if kid else None
        self.main_display.set_selected_kid(kid)
    
    def toggle_main_display(self):
        """Toggle the main inventory display."""
        self.main_display.toggle_visibility()
    
    def show_main_display(self):
        """Show the main inventory display."""
        self.main_display.show()
    
    def hide_main_display(self):
        """Hide the main inventory display."""
        self.main_display.hide()
    
    def render(self, screen: pygame.Surface, font: pygame.font.Font):
        """Render all inventory displays."""
        self.main_display.render(screen, font)
    
    def get_selected_kid_data(self) -> Dict[str, any]:
        """Get data for the currently selected kid."""
        return self.main_display.get_display_data()
