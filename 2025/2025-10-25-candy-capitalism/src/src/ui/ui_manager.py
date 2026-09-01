"""
UI management system for layered rendering and event handling.

Manages UI elements in layers and handles input events
with proper event consumption and propagation.
"""

import pygame
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from .ui_element import UIElement
from ..core.constants import COLORS


class UILayer(Enum):
    """UI rendering layers."""
    BACKGROUND = 0
    WORLD = 1
    HUD = 2
    POPUPS = 3
    OVERLAY = 4


class UIManager:
    """
    Manages UI elements and event handling.
    
    Provides layered rendering system and handles input events
    with proper event consumption and propagation.
    """
    
    def __init__(self):
        """Initialize the UI manager."""
        self.layers: Dict[UILayer, List[UIElement]] = {
            layer: [] for layer in UILayer
        }
        self.active_popup: Optional[UIElement] = None
        self.hovered_element: Optional[UIElement] = None
        
        # Event handling
        self.event_handlers: List[Callable] = []
        
    def add_element(self, element: UIElement, layer: UILayer):
        """
        Add a UI element to a layer.
        
        Args:
            element: UI element to add
            layer: Layer to add element to
        """
        if element not in self.layers[layer]:
            self.layers[layer].append(element)
    
    def remove_element(self, element: UIElement):
        """
        Remove a UI element from all layers.
        
        Args:
            element: UI element to remove
        """
        for layer in self.layers.values():
            if element in layer:
                layer.remove(element)
        
        if self.active_popup == element:
            self.active_popup = None
        if self.hovered_element == element:
            self.hovered_element = None
    
    def show_popup(self, popup: UIElement):
        """
        Show a popup element.
        
        Args:
            popup: Popup element to show
        """
        self.active_popup = popup
        self.add_element(popup, UILayer.POPUPS)
    
    def hide_popup(self, popup: UIElement = None):
        """
        Hide a popup element.
        
        Args:
            popup: Popup to hide (if None, hides active popup)
        """
        if popup is None:
            popup = self.active_popup
        
        if popup:
            self.remove_element(popup)
            if self.active_popup == popup:
                self.active_popup = None
    
    def clear_layer(self, layer: UILayer):
        """
        Clear all elements from a layer.
        
        Args:
            layer: Layer to clear
        """
        self.layers[layer].clear()
    
    def clear_all(self):
        """Clear all UI elements."""
        for layer in self.layers.values():
            layer.clear()
        self.active_popup = None
        self.hovered_element = None
    
    def update(self, dt: float):
        """
        Update all UI elements.
        
        Args:
            dt: Delta time in seconds
        """
        for layer in UILayer:
            for element in self.layers[layer]:
                if element.enabled:
                    element.update(dt)
    
    def render(self, screen: pygame.Surface):
        """
        Render all UI elements.
        
        Args:
            screen: Pygame screen surface
        """
        for layer in UILayer:
            for element in self.layers[layer]:
                if element.visible:
                    element.render(screen)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.
        
        Args:
            event: Pygame event to handle
            
        Returns:
            True if event was consumed, False otherwise
        """
        # Handle popup events first
        if self.active_popup and self.active_popup.enabled:
            if self.active_popup.handle_event(event):
                return True
        
        # Handle hover events
        if event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event)
        
        # Process events in reverse layer order (top to bottom)
        for layer in reversed(list(UILayer)):
            for element in self.layers[layer]:
                if element.enabled and element.handle_event(event):
                    return True
        
        # Call custom event handlers
        for handler in self.event_handlers:
            if handler(event):
                return True
        
        return False
    
    def _handle_mouse_motion(self, event: pygame.event.Event):
        """Handle mouse motion for hover detection."""
        mouse_pos = event.pos
        
        # Check for hovered elements
        hovered = None
        for layer in reversed(list(UILayer)):
            for element in self.layers[layer]:
                if element.enabled and element.visible:
                    if hasattr(element, 'rect') and element.rect.collidepoint(mouse_pos):
                        hovered = element
                        break
            if hovered:
                break
        
        # Update hover state
        if self.hovered_element != hovered:
            if self.hovered_element:
                self.hovered_element.on_mouse_leave()
            if hovered:
                hovered.on_mouse_enter()
            self.hovered_element = hovered
    
    def add_event_handler(self, handler: Callable):
        """
        Add a custom event handler.
        
        Args:
            handler: Function to call for events
        """
        if handler not in self.event_handlers:
            self.event_handlers.append(handler)
    
    def remove_event_handler(self, handler: Callable):
        """
        Remove a custom event handler.
        
        Args:
            handler: Handler to remove
        """
        if handler in self.event_handlers:
            self.event_handlers.remove(handler)
    
    def get_elements_in_layer(self, layer: UILayer) -> List[UIElement]:
        """
        Get all elements in a specific layer.
        
        Args:
            layer: Layer to get elements from
            
        Returns:
            List of elements in the layer
        """
        return self.layers[layer].copy()
    
    def get_element_at_position(self, position: tuple, layer: UILayer = None) -> Optional[UIElement]:
        """
        Get the topmost element at a position.
        
        Args:
            position: (x, y) position to check
            layer: Specific layer to check (if None, checks all layers)
            
        Returns:
            Element at position, or None if none found
        """
        if layer is not None:
            layers_to_check = [layer]
        else:
            layers_to_check = reversed(list(UILayer))
        
        for layer in layers_to_check:
            for element in reversed(self.layers[layer]):
                if element.enabled and element.visible:
                    if hasattr(element, 'rect') and element.rect.collidepoint(position):
                        return element
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get UI manager statistics."""
        stats = {
            'total_elements': sum(len(layer) for layer in self.layers.values()),
            'elements_by_layer': {layer.name: len(elements) for layer, elements in self.layers.items()},
            'active_popup': self.active_popup is not None,
            'hovered_element': self.hovered_element is not None,
            'event_handlers': len(self.event_handlers)
        }
        return stats
