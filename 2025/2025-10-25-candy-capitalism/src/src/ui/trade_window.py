"""
Trade window UI for manual trade creation.

Provides a drag-and-drop interface for creating trades between
the possessed kid and other kids in the neighborhood.
"""

import pygame
from typing import Optional, Dict, Any, Callable, List, Tuple
from .ui_element import UIElement
from ..core.constants import COLORS
from ..entities.kid import Kid


class TradeWindow(UIElement):
    """
    Main trade window with drag-and-drop functionality.
    
    Shows inventories of both kids and allows dragging candy
    to create trade offers.
    """
    
    def __init__(self, x: int = 200, y: int = 100, width: int = 600, height: int = 400):
        """
        Initialize trade window.
        
        Args:
            x: X position on screen
            y: Y position on screen
            width: Width of the window
            height: Height of the window
        """
        super().__init__(pygame.Rect(x, y, width, height))
        
        # Visual properties
        self.background_color = (40, 40, 50)
        self.border_color = COLORS['WHITE']
        self.border_width = 3
        self.title_color = COLORS['YELLOW']
        self.text_color = COLORS['WHITE']
        
        # Fonts
        self.title_font = pygame.font.Font(None, 24)
        self.text_font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 14)
        
        # Layout
        self.padding = 15
        self.section_spacing = 20
        self.slot_size = 60
        self.slots_per_row = 4
        
        # Trade state
        self.player_kid: Optional[Kid] = None
        self.target_kid: Optional[Kid] = None
        self.player_offer: Dict[str, int] = {}
        self.target_offer: Dict[str, int] = {}
        
        # Drag state
        self.dragging_item: Optional[Tuple[str, int]] = None  # (candy_type, quantity)
        self.drag_offset: Tuple[int, int] = (0, 0)
        self.drag_start_pos: Tuple[int, int] = (0, 0)
        
        # Callbacks
        self.on_close: Optional[Callable] = None
        self.on_propose_trade: Optional[Callable] = None
        
        # UI sections
        self._calculate_sections()
        
    def _calculate_sections(self):
        """Calculate positions of UI sections."""
        # Title area
        self.title_rect = pygame.Rect(
            self.rect.x + self.padding,
            self.rect.y + self.padding,
            self.rect.width - self.padding * 2,
            30
        )
        
        # Close button
        self.close_rect = pygame.Rect(
            self.rect.right - 30,
            self.rect.y + self.padding,
            20,
            20
        )
        
        # Inventory sections
        inv_width = (self.rect.width - self.padding * 3) // 2
        inv_height = 120
        
        self.player_inv_rect = pygame.Rect(
            self.rect.x + self.padding,
            self.title_rect.bottom + self.section_spacing,
            inv_width,
            inv_height
        )
        
        self.target_inv_rect = pygame.Rect(
            self.player_inv_rect.right + self.padding,
            self.player_inv_rect.y,
            inv_width,
            inv_height
        )
        
        # Offer sections
        self.player_offer_rect = pygame.Rect(
            self.rect.x + self.padding,
            self.player_inv_rect.bottom + self.section_spacing,
            inv_width,
            inv_height
        )
        
        self.target_offer_rect = pygame.Rect(
            self.player_offer_rect.right + self.padding,
            self.player_offer_rect.y,
            inv_width,
            inv_height
        )
        
        # Bottom section
        self.bottom_rect = pygame.Rect(
            self.rect.x + self.padding,
            self.player_offer_rect.bottom + self.section_spacing,
            self.rect.width - self.padding * 2,
            60
        )
        
        # Propose button
        self.propose_rect = pygame.Rect(
            self.bottom_rect.right - 100,
            self.bottom_rect.y + 10,
            90,
            40
        )
    
    def set_kids(self, player_kid: Kid, target_kid: Kid):
        """Set the kids involved in the trade."""
        self.player_kid = player_kid
        self.target_kid = target_kid
        self.player_offer = {}
        self.target_offer = {}
    
    def update(self, dt: float):
        """Update trade window."""
        super().update(dt)
        
        # Update drag state
        if self.dragging_item:
            mouse_pos = pygame.mouse.get_pos()
            # Keep drag item following mouse
            pass
    
    def render(self, screen: pygame.Surface):
        """Render the trade window."""
        if not self.visible:
            return
        
        # Draw background
        pygame.draw.rect(screen, self.background_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)
        
        # Draw title
        self._render_title(screen)
        
        # Draw inventories
        self._render_inventory_sections(screen)
        
        # Draw offer areas
        self._render_offer_sections(screen)
        
        # Draw bottom section
        self._render_bottom_section(screen)
        
        # Draw dragging item
        if self.dragging_item:
            self._render_dragging_item(screen)
    
    def _render_title(self, screen: pygame.Surface):
        """Render window title."""
        if self.target_kid:
            title_text = f"Trade with {self.target_kid.id}"
        else:
            title_text = "Trade Window"
        
        title_surface = self.title_font.render(title_text, True, self.title_color)
        screen.blit(title_surface, (self.title_rect.x, self.title_rect.y))
        
        # Close button
        pygame.draw.rect(screen, COLORS['RED'], self.close_rect)
        close_text = self.small_font.render("X", True, COLORS['WHITE'])
        close_text_rect = close_text.get_rect(center=self.close_rect.center)
        screen.blit(close_text, close_text_rect)
    
    def _render_inventory_sections(self, screen: pygame.Surface):
        """Render inventory sections."""
        # Player inventory
        pygame.draw.rect(screen, (50, 50, 60), self.player_inv_rect)
        pygame.draw.rect(screen, COLORS['WHITE'], self.player_inv_rect, 2)
        
        player_text = self.text_font.render("Your Inventory", True, self.text_color)
        screen.blit(player_text, (self.player_inv_rect.x + 5, self.player_inv_rect.y + 5))
        
        if self.player_kid and hasattr(self.player_kid, 'inventory'):
            self._render_inventory_grid(screen, self.player_inv_rect, self.player_kid.inventory, True)
        
        # Target inventory
        pygame.draw.rect(screen, (50, 50, 60), self.target_inv_rect)
        pygame.draw.rect(screen, COLORS['WHITE'], self.target_inv_rect, 2)
        
        target_text = self.text_font.render("Their Inventory", True, self.text_color)
        screen.blit(target_text, (self.target_inv_rect.x + 5, self.target_inv_rect.y + 5))
        
        if self.target_kid and hasattr(self.target_kid, 'inventory'):
            self._render_inventory_grid(screen, self.target_inv_rect, self.target_kid.inventory, False)
    
    def _render_inventory_grid(self, screen: pygame.Surface, rect: pygame.Rect, inventory: Dict[str, int], is_player: bool):
        """Render inventory as a grid of candy slots."""
        if not inventory:
            return
        
        # Calculate grid position
        grid_x = rect.x + 5
        grid_y = rect.y + 25
        grid_width = rect.width - 10
        grid_height = rect.height - 30
        
        # Render candy slots
        slot_x = grid_x
        slot_y = grid_y
        slot_count = 0
        
        for candy_type, quantity in inventory.items():
            if quantity > 0:
                slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
                
                # Draw slot background
                pygame.draw.rect(screen, (70, 70, 80), slot_rect)
                pygame.draw.rect(screen, COLORS['WHITE'], slot_rect, 1)
                
                # Draw candy type
                candy_text = self.small_font.render(candy_type[:4], True, self.text_color)
                candy_rect = candy_text.get_rect(center=(slot_rect.centerx, slot_rect.centery - 8))
                screen.blit(candy_text, candy_rect)
                
                # Draw quantity
                qty_text = self.small_font.render(f"x{quantity}", True, COLORS['YELLOW'])
                qty_rect = qty_text.get_rect(center=(slot_rect.centerx, slot_rect.centery + 8))
                screen.blit(qty_text, qty_rect)
                
                # Move to next slot
                slot_x += self.slot_size + 5
                slot_count += 1
                
                if slot_count >= self.slots_per_row:
                    slot_x = grid_x
                    slot_y += self.slot_size + 5
                    slot_count = 0
    
    def _render_offer_sections(self, screen: pygame.Surface):
        """Render trade offer sections."""
        # Player offer area
        pygame.draw.rect(screen, (60, 40, 40), self.player_offer_rect)
        pygame.draw.rect(screen, COLORS['GREEN'], self.player_offer_rect, 2)
        
        player_offer_text = self.text_font.render("Your Offer", True, COLORS['GREEN'])
        screen.blit(player_offer_text, (self.player_offer_rect.x + 5, self.player_offer_rect.y + 5))
        
        # Target offer area
        pygame.draw.rect(screen, (40, 40, 60), self.target_offer_rect)
        pygame.draw.rect(screen, COLORS['BLUE'], self.target_offer_rect, 2)
        
        target_offer_text = self.text_font.render("Their Offer", True, COLORS['BLUE'])
        screen.blit(target_offer_text, (self.target_offer_rect.x + 5, self.target_offer_rect.y + 5))
        
        # Render offer items
        self._render_offer_items(screen, self.player_offer_rect, self.player_offer, COLORS['GREEN'])
        self._render_offer_items(screen, self.target_offer_rect, self.target_offer, COLORS['BLUE'])
    
    def _render_offer_items(self, screen: pygame.Surface, rect: pygame.Rect, offer: Dict[str, int], color: Tuple[int, int, int]):
        """Render items in offer area."""
        if not offer:
            # Show "Drop here" text
            drop_text = self.small_font.render("Drop candy here", True, (100, 100, 100))
            drop_rect = drop_text.get_rect(center=rect.center)
            screen.blit(drop_text, drop_rect)
            return
        
        # Render offer items
        slot_x = rect.x + 5
        slot_y = rect.y + 25
        
        for candy_type, quantity in offer.items():
            if quantity > 0:
                slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
                
                # Draw slot with offer color
                pygame.draw.rect(screen, color, slot_rect)
                pygame.draw.rect(screen, COLORS['WHITE'], slot_rect, 2)
                
                # Draw candy type
                candy_text = self.small_font.render(candy_type[:4], True, COLORS['WHITE'])
                candy_rect = candy_text.get_rect(center=(slot_rect.centerx, slot_rect.centery - 8))
                screen.blit(candy_text, candy_rect)
                
                # Draw quantity
                qty_text = self.small_font.render(f"x{quantity}", True, COLORS['WHITE'])
                qty_rect = qty_text.get_rect(center=(slot_rect.centerx, slot_rect.centery + 8))
                screen.blit(qty_text, qty_rect)
                
                slot_x += self.slot_size + 5
    
    def _render_bottom_section(self, screen: pygame.Surface):
        """Render bottom section with trade value and propose button."""
        pygame.draw.rect(screen, (30, 30, 40), self.bottom_rect)
        
        # Calculate trade value
        trade_value = self._calculate_trade_value()
        
        # Trade value text
        if trade_value > 0:
            value_text = f"Value: +{trade_value} (Good for you)"
            value_color = COLORS['GREEN']
        elif trade_value < 0:
            value_text = f"Value: {trade_value} (Bad for you)"
            value_color = COLORS['RED']
        else:
            value_text = "Value: 0 (Fair)"
            value_color = COLORS['WHITE']
        
        value_surface = self.text_font.render(value_text, True, value_color)
        screen.blit(value_surface, (self.bottom_rect.x + 5, self.bottom_rect.y + 10))
        
        # Show chaos gain for bad trades
        if trade_value < 0:
            chaos_gain = abs(trade_value) * 2
            chaos_text = f"Chaos Gain: +{chaos_gain}"
            chaos_surface = self.text_font.render(chaos_text, True, COLORS['GREEN'])
            chaos_rect = chaos_surface.get_rect(center=(self.bottom_rect.centerx, 
                                                         self.bottom_rect.centery - 20))
            screen.blit(chaos_surface, chaos_rect)
        
        # Propose button
        button_color = COLORS['GREEN'] if trade_value < 0 else COLORS['GRAY']
        pygame.draw.rect(screen, button_color, self.propose_rect)
        pygame.draw.rect(screen, COLORS['WHITE'], self.propose_rect, 2)
        
        propose_text = self.text_font.render("Propose", True, COLORS['WHITE'])
        propose_rect = propose_text.get_rect(center=self.propose_rect.center)
        screen.blit(propose_text, propose_rect)
    
    def _render_dragging_item(self, screen: pygame.Surface):
        """Render item being dragged."""
        if not self.dragging_item:
            return
        
        candy_type, quantity = self.dragging_item
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw dragging item at mouse position
        drag_rect = pygame.Rect(
            mouse_pos[0] - self.slot_size // 2,
            mouse_pos[1] - self.slot_size // 2,
            self.slot_size,
            self.slot_size
        )
        
        pygame.draw.rect(screen, COLORS['YELLOW'], drag_rect)
        pygame.draw.rect(screen, COLORS['WHITE'], drag_rect, 2)
        
        # Draw candy type
        candy_text = self.small_font.render(candy_type[:4], True, COLORS['BLACK'])
        candy_rect = candy_text.get_rect(center=(drag_rect.centerx, drag_rect.centery - 8))
        screen.blit(candy_text, candy_rect)
        
        # Draw quantity
        qty_text = self.small_font.render(f"x{quantity}", True, COLORS['BLACK'])
        qty_rect = qty_text.get_rect(center=(drag_rect.centerx, drag_rect.centery + 8))
        screen.blit(qty_text, qty_rect)
    
    def _calculate_trade_value(self) -> int:
        """Calculate trade value (positive = good for player, negative = bad for player)."""
        # Simple calculation: sum of player offer - sum of target offer
        # In a real implementation, this would use the TradeEvaluator
        player_value = sum(self.player_offer.values())
        target_value = sum(self.target_offer.values())
        return target_value - player_value
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if not self.enabled or not self.visible:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self._handle_left_click(event.pos)
            elif event.button == 3:  # Right click
                return self._handle_right_click(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                return self._handle_left_release(event.pos)
        
        elif event.type == pygame.MOUSEMOTION:
            return self._handle_mouse_motion(event.pos)
        
        return False
    
    def _handle_left_click(self, pos: Tuple[int, int]) -> bool:
        """Handle left mouse click."""
        # Check close button
        if self.close_rect.collidepoint(pos):
            if self.on_close:
                self.on_close()
            return True
        
        # Check propose button
        if self.propose_rect.collidepoint(pos):
            if self.on_propose_trade:
                self.on_propose_trade(self.player_offer, self.target_offer)
            return True
        
        # Check inventory slots for drag start
        if self.player_kid and hasattr(self.player_kid, 'inventory'):
            candy_item = self._get_candy_at_position(pos, self.player_inv_rect, self.player_kid.inventory)
            if candy_item:
                self._start_drag(candy_item, pos)
                return True
        
        if self.target_kid and hasattr(self.target_kid, 'inventory'):
            candy_item = self._get_candy_at_position(pos, self.target_inv_rect, self.target_kid.inventory)
            if candy_item:
                self._start_drag(candy_item, pos)
                return True
        
        return False
    
    def _handle_left_release(self, pos: Tuple[int, int]) -> bool:
        """Handle left mouse release."""
        if self.dragging_item:
            self._handle_drop(pos)
            return True
        return False
    
    def _handle_right_click(self, pos: Tuple[int, int]) -> bool:
        """Handle right mouse click."""
        # Could be used for quantity adjustment
        return False
    
    def _handle_mouse_motion(self, pos: Tuple[int, int]) -> bool:
        """Handle mouse motion."""
        # Update drag position
        return False
    
    def _get_candy_at_position(self, pos: Tuple[int, int], rect: pygame.Rect, inventory: Dict[str, int]) -> Optional[Tuple[str, int]]:
        """Get candy item at mouse position."""
        if not rect.collidepoint(pos):
            return None
        
        # Calculate which slot was clicked
        relative_x = pos[0] - rect.x - 5
        relative_y = pos[1] - rect.y - 25
        
        slot_x = relative_x // (self.slot_size + 5)
        slot_y = relative_y // (self.slot_size + 5)
        
        # Find candy at this slot position
        slot_count = 0
        for candy_type, quantity in inventory.items():
            if quantity > 0:
                if slot_count == slot_x + slot_y * self.slots_per_row:
                    return (candy_type, quantity)
                slot_count += 1
        
        return None
    
    def _start_drag(self, candy_item: Tuple[str, int], pos: Tuple[int, int]):
        """Start dragging a candy item."""
        self.dragging_item = candy_item
        self.drag_start_pos = pos
        self.drag_offset = (pos[0] - pos[0], pos[1] - pos[1])  # Will be updated during drag
    
    def _handle_drop(self, pos: Tuple[int, int]):
        """Handle dropping dragged item."""
        if not self.dragging_item:
            return
        
        candy_type, quantity = self.dragging_item
        
        # Check if dropped in player offer area
        if self.player_offer_rect.collidepoint(pos):
            if candy_type not in self.player_offer:
                self.player_offer[candy_type] = 0
            self.player_offer[candy_type] += quantity
        
        # Check if dropped in target offer area
        elif self.target_offer_rect.collidepoint(pos):
            if candy_type not in self.target_offer:
                self.target_offer[candy_type] = 0
            self.target_offer[candy_type] += quantity
        
        # Stop dragging
        self.dragging_item = None
    
    def close(self):
        """Close the trade window."""
        self.visible = False
        if self.on_close:
            self.on_close()
    
    def set_callbacks(self, close_callback: Callable = None, propose_callback: Callable = None):
        """Set callback functions."""
        self.on_close = close_callback
        self.on_propose_trade = propose_callback
