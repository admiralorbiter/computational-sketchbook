"""
Base UI element classes for the game interface.

Provides base classes for UI elements with common functionality
like event handling, rendering, and state management.
"""

import pygame
from typing import Optional, Callable, Any
from ..core.constants import COLORS


class UIElement:
    """
    Base class for all UI elements.
    
    Provides common functionality for position, visibility,
    event handling, and rendering.
    """
    
    def __init__(self, rect: pygame.Rect):
        """
        Initialize UI element.
        
        Args:
            rect: Rectangle defining position and size
        """
        self.rect = pygame.Rect(rect)
        self.visible = True
        self.enabled = True
        self.active = False
        
        # Event callbacks
        self.on_click: Optional[Callable] = None
        self.on_hover: Optional[Callable] = None
        self.on_leave: Optional[Callable] = None
        
        # Visual state
        self.hovered = False
        self.pressed = False
        
    def update(self, dt: float):
        """
        Update element state.
        
        Args:
            dt: Delta time in seconds
        """
        # Override in subclasses
        pass
    
    def render(self, screen: pygame.Surface):
        """
        Render the element.
        
        Args:
            screen: Pygame screen surface
        """
        if not self.visible:
            return
        
        # Override in subclasses
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.
        
        Args:
            event: Pygame event to handle
            
        Returns:
            True if event was consumed, False otherwise
        """
        if not self.enabled or not self.visible:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.rect.collidepoint(event.pos):
                    self.pressed = True
                    if self.on_click:
                        self.on_click()
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click
                if self.pressed:
                    self.pressed = False
                    return True
        
        elif event.type == pygame.MOUSEMOTION:
            was_hovered = self.hovered
            self.hovered = self.rect.collidepoint(event.pos)
            
            if self.hovered and not was_hovered:
                self.on_mouse_enter()
            elif not self.hovered and was_hovered:
                self.on_mouse_leave()
        
        return False
    
    def on_mouse_enter(self):
        """Called when mouse enters element."""
        if self.on_hover:
            self.on_hover()
    
    def on_mouse_leave(self):
        """Called when mouse leaves element."""
        if self.on_leave:
            self.on_leave()
    
    def set_position(self, x: int, y: int):
        """Set element position."""
        self.rect.x = x
        self.rect.y = y
    
    def set_size(self, width: int, height: int):
        """Set element size."""
        self.rect.width = width
        self.rect.height = height
    
    def set_visible(self, visible: bool):
        """Set element visibility."""
        self.visible = visible
    
    def set_enabled(self, enabled: bool):
        """Set element enabled state."""
        self.enabled = enabled
    
    def is_point_inside(self, point: tuple) -> bool:
        """Check if point is inside element."""
        return self.rect.collidepoint(point)


class Button(UIElement):
    """Button UI element."""
    
    def __init__(self, rect: pygame.Rect, text: str, callback: Callable = None):
        """
        Initialize button.
        
        Args:
            rect: Button rectangle
            text: Button text
            callback: Function to call when clicked
        """
        super().__init__(rect)
        self.text = text
        self.on_click = callback
        
        # Button colors
        self.normal_color = COLORS['BLUE']
        self.hover_color = COLORS['GREEN']
        self.pressed_color = COLORS['RED']
        self.text_color = COLORS['WHITE']
        
        # Font
        self.font = pygame.font.Font(None, 24)
    
    def render(self, screen: pygame.Surface):
        """Render the button."""
        super().render(screen)
        
        if not self.visible:
            return
        
        # Choose color based on state
        if self.pressed:
            color = self.pressed_color
        elif self.hovered:
            color = self.hover_color
        else:
            color = self.normal_color
        
        # Draw button background
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLORS['WHITE'], self.rect, 2)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class Label(UIElement):
    """Label UI element for displaying text."""
    
    def __init__(self, rect: pygame.Rect, text: str, font_size: int = 24):
        """
        Initialize label.
        
        Args:
            rect: Label rectangle
            text: Text to display
            font_size: Font size
        """
        super().__init__(rect)
        self.text = text
        self.font_size = font_size
        self.text_color = COLORS['WHITE']
        self.font = pygame.font.Font(None, font_size)
    
    def set_text(self, text: str):
        """Set label text."""
        self.text = text
    
    def render(self, screen: pygame.Surface):
        """Render the label."""
        super().render(screen)
        
        if not self.visible:
            return
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class Panel(UIElement):
    """Panel UI element for grouping other elements."""
    
    def __init__(self, rect: pygame.Rect, background_color: tuple = None):
        """
        Initialize panel.
        
        Args:
            rect: Panel rectangle
            background_color: Background color
        """
        super().__init__(rect)
        self.background_color = background_color or COLORS['DARK_GRAY']
        self.border_color = COLORS['WHITE']
        self.border_width = 2
    
    def render(self, screen: pygame.Surface):
        """Render the panel."""
        super().render(screen)
        
        if not self.visible:
            return
        
        # Draw background
        pygame.draw.rect(screen, self.background_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)


class ProgressBar(UIElement):
    """Progress bar UI element."""
    
    def __init__(self, rect: pygame.Rect, max_value: float = 100.0, current_value: float = 0.0):
        """
        Initialize progress bar.
        
        Args:
            rect: Progress bar rectangle
            max_value: Maximum value
            current_value: Current value
        """
        super().__init__(rect)
        self.max_value = max_value
        self.current_value = current_value
        self.fill_color = COLORS['GREEN']
        self.background_color = COLORS['DARK_GRAY']
        self.border_color = COLORS['WHITE']
    
    def set_value(self, value: float):
        """Set current value."""
        self.current_value = max(0, min(self.max_value, value))
    
    def set_max_value(self, max_value: float):
        """Set maximum value."""
        self.max_value = max_value
        self.current_value = max(0, min(self.max_value, self.current_value))
    
    def get_percentage(self) -> float:
        """Get progress as percentage."""
        if self.max_value == 0:
            return 0.0
        return self.current_value / self.max_value
    
    def render(self, screen: pygame.Surface):
        """Render the progress bar."""
        super().render(screen)
        
        if not self.visible:
            return
        
        # Draw background
        pygame.draw.rect(screen, self.background_color, self.rect)
        
        # Draw fill
        if self.current_value > 0:
            fill_width = int(self.rect.width * self.get_percentage())
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            pygame.draw.rect(screen, self.fill_color, fill_rect)
        
        # Draw border
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
