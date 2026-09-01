"""
House power selection context menu.

Appears when clicking on houses to allow selection of curse/bless powers
with energy cost display and confirmation.
"""

import pygame
from typing import Optional, Callable, List, Tuple
from .ui_element import UIElement
from ..core.constants import COLORS


class PowerMenu(UIElement):
    """
    Context menu for selecting house powers (curse/bless).
    
    Appears when clicking on houses and shows available powers
    with energy costs and confirmation buttons.
    """
    
    def __init__(self, x: int, y: int, house_id: str, curse_cost: int = 15, bless_cost: int = 25):
        """
        Initialize power menu.
        
        Args:
            x: X position on screen
            y: Y position on screen
            house_id: ID of the house this menu is for
            curse_cost: Energy cost for curse power
            bless_cost: Energy cost for bless power
        """
        width = 200
        height = 120
        
        super().__init__(pygame.Rect(x, y, width, height))
        
        # Properties
        self.house_id = house_id
        self.curse_cost = curse_cost
        self.bless_cost = bless_cost
        
        # Visual properties
        self.background_color = (40, 40, 50)
        self.border_color = COLORS['WHITE']
        self.border_width = 2
        self.text_color = COLORS['WHITE']
        self.title_color = COLORS['YELLOW']
        self.button_color = (70, 70, 80)
        self.button_hover_color = (90, 90, 100)
        self.disabled_color = (50, 50, 50)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 18)
        self.button_font = pygame.font.Font(None, 16)
        self.cost_font = pygame.font.Font(None, 14)
        
        # Button layout
        self.button_height = 30
        self.button_padding = 5
        
        # State
        self.hovered_button = None
        self.current_energy = 100  # Will be updated from possession system
        
        # Callbacks
        self.on_curse_callback: Optional[Callable] = None
        self.on_bless_callback: Optional[Callable] = None
        self.on_close_callback: Optional[Callable] = None
        
    def update(self, dt: float):
        """Update power menu."""
        super().update(dt)
        
        # Auto-close after a few seconds if no interaction
        if hasattr(self, 'auto_close_timer'):
            self.auto_close_timer -= dt
            if self.auto_close_timer <= 0:
                self.close()
    
    def render(self, screen: pygame.Surface):
        """Render the power menu."""
        if not self.visible:
            return
        
        # Draw background
        pygame.draw.rect(screen, self.background_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)
        
        # Draw title
        self._render_title(screen)
        
        # Draw buttons
        self._render_buttons(screen)
    
    def _render_title(self, screen: pygame.Surface):
        """Render menu title."""
        title_text = f"House Powers: {self.house_id}"
        title_surface = self.title_font.render(title_text, True, self.title_color)
        
        title_x = self.rect.x + 10
        title_y = self.rect.y + 10
        
        screen.blit(title_surface, (title_x, title_y))
    
    def _render_buttons(self, screen: pygame.Surface):
        """Render power buttons."""
        button_y = self.rect.y + 35
        
        # Curse button
        curse_rect = pygame.Rect(self.rect.x + 10, button_y, self.rect.width - 20, self.button_height)
        curse_enabled = self.current_energy >= self.curse_cost
        
        self._render_button(screen, curse_rect, "Curse House", self.curse_cost, 
                           curse_enabled, self.hovered_button == "curse")
        
        # Bless button
        bless_y = button_y + self.button_height + self.button_padding
        bless_rect = pygame.Rect(self.rect.x + 10, bless_y, self.rect.width - 20, self.button_height)
        bless_enabled = self.current_energy >= self.bless_cost
        
        self._render_button(screen, bless_rect, "Bless House", self.bless_cost, 
                           bless_enabled, self.hovered_button == "bless")
    
    def _render_button(self, screen: pygame.Surface, rect: pygame.Rect, text: str, 
                      cost: int, enabled: bool, hovered: bool):
        """Render a single button."""
        # Choose button color
        if enabled:
            color = self.button_hover_color if hovered else self.button_color
        else:
            color = self.disabled_color
        
        # Draw button background
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, self.border_color, rect, 1)
        
        # Draw button text
        text_color = self.text_color if enabled else (100, 100, 100)
        text_surface = self.button_font.render(text, True, text_color)
        
        # Center text in button
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)
        
        # Draw cost
        cost_text = f"({cost} energy)"
        cost_surface = self.cost_font.render(cost_text, True, text_color)
        
        cost_x = rect.right - cost_surface.get_width() - 5
        cost_y = rect.centery - cost_surface.get_height() // 2
        
        screen.blit(cost_surface, (cost_x, cost_y))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events for the power menu."""
        if not self.enabled or not self.visible:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            # Check for button hover
            mouse_pos = event.pos
            self.hovered_button = self._get_hovered_button(mouse_pos)
            return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                clicked_button = self._get_hovered_button(mouse_pos)
                
                if clicked_button == "curse" and self.current_energy >= self.curse_cost:
                    self._on_curse_clicked()
                    return True
                elif clicked_button == "bless" and self.current_energy >= self.bless_cost:
                    self._on_bless_clicked()
                    return True
                else:
                    # Clicked outside buttons - close menu
                    self.close()
                    return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return True
        
        return False
    
    def _get_hovered_button(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """Get which button is being hovered."""
        button_y = self.rect.y + 35
        
        # Check curse button
        curse_rect = pygame.Rect(self.rect.x + 10, button_y, self.rect.width - 20, self.button_height)
        if curse_rect.collidepoint(mouse_pos):
            return "curse"
        
        # Check bless button
        bless_y = button_y + self.button_height + self.button_padding
        bless_rect = pygame.Rect(self.rect.x + 10, bless_y, self.rect.width - 20, self.button_height)
        if bless_rect.collidepoint(mouse_pos):
            return "bless"
        
        return None
    
    def _on_curse_clicked(self):
        """Handle curse button click."""
        if self.on_curse_callback:
            self.on_curse_callback(self.house_id)
        self.close()
    
    def _on_bless_clicked(self):
        """Handle bless button click."""
        if self.on_bless_callback:
            self.on_bless_callback(self.house_id)
        self.close()
    
    def close(self):
        """Close the power menu."""
        self.visible = False
        if self.on_close_callback:
            self.on_close_callback()
    
    def set_energy(self, energy: int):
        """Set current energy level."""
        self.current_energy = energy
    
    def set_callbacks(self, curse_callback: Optional[Callable] = None, 
                     bless_callback: Optional[Callable] = None,
                     close_callback: Optional[Callable] = None):
        """Set callback functions."""
        self.on_curse_callback = curse_callback
        self.on_bless_callback = bless_callback
        self.on_close_callback = close_callback
    
    def show(self, x: int, y: int, energy: int):
        """Show the power menu at specified position."""
        self.rect.x = x
        self.rect.y = y
        self.current_energy = energy
        self.visible = True
        self.enabled = True
        self.hovered_button = None
        
        # Set auto-close timer
        self.auto_close_timer = 5.0  # Close after 5 seconds
    
    def get_menu_info(self) -> dict:
        """Get information about the menu state."""
        return {
            'house_id': self.house_id,
            'curse_cost': self.curse_cost,
            'bless_cost': self.bless_cost,
            'current_energy': self.current_energy,
            'curse_enabled': self.current_energy >= self.curse_cost,
            'bless_enabled': self.current_energy >= self.bless_cost,
            'hovered_button': self.hovered_button
        }
