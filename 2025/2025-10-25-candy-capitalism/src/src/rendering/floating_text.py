"""
Floating text system for trade notifications and other UI feedback.

Displays temporary text that floats upward and fades out.
"""

import pygame
from typing import List, Tuple
from ..utils.vector2 import Vector2


class FloatingText:
    """Individual floating text element."""
    
    def __init__(self, text: str, position: Vector2, color: Tuple[int, int, int] = (255, 255, 255),
                 lifetime: float = 2.0, velocity: Vector2 = None, font_size: int = 20):
        self.text = text
        self.position = position.copy()
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.active = True
        
        # Default upward velocity
        if velocity is None:
            velocity = Vector2(0, -30)  # Float upward
        self.velocity = velocity
        
        # Font setup
        self.font_size = font_size
        self.font = pygame.font.Font(None, font_size)
    
    def update(self, dt: float) -> bool:
        """
        Update text position and lifetime.
        
        Args:
            dt: Delta time in seconds
            
        Returns:
            True if text is still active, False if expired
        """
        if not self.active:
            return False
        
        # Update position
        self.position += self.velocity * dt
        
        # Update lifetime
        self.lifetime -= dt
        
        # Check if expired
        if self.lifetime <= 0:
            self.active = False
            return False
        
        return True
    
    def get_alpha(self) -> int:
        """Get alpha value based on lifetime (fade out)."""
        if self.max_lifetime <= 0:
            return 255
        
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        return max(0, min(255, alpha))
    
    def render(self, screen, camera):
        """Render the floating text."""
        if not self.active:
            return
        
        # Convert world position to screen position
        screen_pos = camera.world_to_screen(self.position)
        
        # Skip if off-screen
        if (screen_pos.x < -50 or screen_pos.x > screen.get_width() + 50 or
            screen_pos.y < -50 or screen_pos.y > screen.get_height() + 50):
            return
        
        # Get alpha for fading
        alpha = self.get_alpha()
        
        # Create text surface with alpha
        text_surface = self.font.render(self.text, True, self.color)
        
        # Create a surface with alpha
        alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        alpha_surface.blit(text_surface, (0, 0))
        
        # Apply alpha
        alpha_surface.set_alpha(alpha)
        
        # Blit to screen
        screen.blit(alpha_surface, (screen_pos.x - text_surface.get_width() // 2, 
                                   screen_pos.y - text_surface.get_height() // 2))


class FloatingTextSystem:
    """Manages all floating text in the game."""
    
    def __init__(self):
        self.texts: List[FloatingText] = []
        self.max_texts = 50  # Limit for performance
    
    def add_text(self, text: str, position: Vector2, color: Tuple[int, int, int] = (255, 255, 255),
                 lifetime: float = 2.0, velocity: Vector2 = None, font_size: int = 20):
        """Add floating text to the system."""
        floating_text = FloatingText(text, position, color, lifetime, velocity, font_size)
        self.texts.append(floating_text)
        
        # Limit total texts
        if len(self.texts) > self.max_texts:
            # Remove oldest texts
            self.texts = self.texts[-self.max_texts:]
    
    def add_trade_text(self, position: Vector2, offer: dict, request: dict):
        """Add floating text for a trade."""
        # Create trade description
        offer_str = ", ".join([f"{qty}x {candy}" for candy, qty in offer.items()])
        request_str = ", ".join([f"{qty}x {candy}" for candy, qty in request.items()])
        
        # Add text for each part of the trade
        self.add_text(f"Trading: {offer_str}", position, (100, 255, 100), 2.0, Vector2(0, -40))
        self.add_text(f"For: {request_str}", position, (255, 255, 100), 2.0, Vector2(0, -20))
    
    def add_price_change_text(self, position: Vector2, candy_type: str, old_price: float, new_price: float):
        """Add floating text for price changes."""
        if new_price > old_price:
            color = (100, 255, 100)  # Green for increase
            symbol = "↑"
        else:
            color = (255, 100, 100)  # Red for decrease
            symbol = "↓"
        
        change = abs(new_price - old_price)
        text = f"{candy_type} {symbol} {change:.1f}"
        
        self.add_text(text, position, color, 3.0, Vector2(0, -30), 18)
    
    def update(self, dt: float):
        """Update all floating texts."""
        # Update texts and remove inactive ones
        self.texts = [t for t in self.texts if t.update(dt)]
    
    def render(self, screen, camera):
        """Render all floating texts."""
        for text in self.texts:
            text.render(screen, camera)
    
    def clear(self):
        """Clear all floating texts."""
        self.texts.clear()
    
    def get_text_count(self) -> int:
        """Get current text count."""
        return len(self.texts)
