"""
Market ticker UI element.

Displays current market prices with trend indicators in the bottom-right corner.
"""

import pygame
from typing import Dict, List, Tuple, Optional
from ..systems.economy import Economy
from ..core.candy_types import CandyTypes


class MarketTicker:
    """Market ticker showing current prices and trends."""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Position and size
        self.width = 300
        self.height = 150
        self.x = screen_width - self.width - 20
        self.y = screen_height - self.height - 20
        
        # Font setup
        self.font_large = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 14)
        
        # Colors
        self.bg_color = (20, 20, 20, 200)  # Semi-transparent dark
        self.text_color = (255, 255, 255)
        self.up_color = (100, 255, 100)    # Green
        self.down_color = (255, 100, 100)  # Red
        self.neutral_color = (200, 200, 200)  # Gray
        
        # Animation
        self.animation_timer = 0.0
        self.update_interval = 1.0  # Update every second
        
        # Cached data
        self.last_prices: Dict[str, float] = {}
        self.current_prices: Dict[str, float] = {}
        self.trends: Dict[str, float] = {}
    
    def update(self, dt: float, economy: Economy):
        """Update ticker data."""
        self.animation_timer += dt
        
        if self.animation_timer >= self.update_interval:
            self.animation_timer = 0.0
            self._update_prices(economy)
    
    def _update_prices(self, economy: Economy):
        """Update price data from economy."""
        # Store previous prices for trend calculation
        self.last_prices = self.current_prices.copy()
        
        # Get current market prices
        self.current_prices = {}
        candy_types = CandyTypes.get_all_types()
        
        for candy_type in candy_types:
            market_price = economy.get_market_price(candy_type)
            self.current_prices[candy_type] = market_price
            
            # Calculate trend
            if candy_type in self.last_prices:
                old_price = self.last_prices[candy_type]
                if old_price > 0:
                    trend = (market_price - old_price) / old_price
                    self.trends[candy_type] = trend
                else:
                    self.trends[candy_type] = 0.0
            else:
                self.trends[candy_type] = 0.0
    
    def render(self, screen: pygame.Surface):
        """Render the market ticker."""
        # Create background surface
        bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_surface.fill(self.bg_color)
        
        # Draw border
        pygame.draw.rect(bg_surface, (100, 100, 100), (0, 0, self.width, self.height), 2)
        
        # Draw title
        title_text = self.font_large.render("Market Prices", True, self.text_color)
        bg_surface.blit(title_text, (10, 10))
        
        # Draw prices
        y_offset = 40
        candy_types = CandyTypes.get_all_types()
        
        for i, candy_type in enumerate(candy_types[:6]):  # Show first 6 candy types
            if candy_type not in self.current_prices:
                continue
            
            price = self.current_prices[candy_type]
            trend = self.trends.get(candy_type, 0.0)
            
            # Candy name
            candy_name = CandyTypes.get_visual_properties(candy_type).get('name', candy_type)
            name_text = self.font_medium.render(candy_name, True, self.text_color)
            bg_surface.blit(name_text, (10, y_offset))
            
            # Price
            price_text = f"${price:.1f}"
            price_surface = self.font_medium.render(price_text, True, self.text_color)
            bg_surface.blit(price_surface, (150, y_offset))
            
            # Trend indicator
            if abs(trend) > 0.01:  # Only show if significant change
                if trend > 0:
                    symbol = "↑"
                    color = self.up_color
                else:
                    symbol = "↓"
                    color = self.down_color
                
                trend_text = f"{symbol} {abs(trend)*100:.1f}%"
                trend_surface = self.font_small.render(trend_text, True, color)
                bg_surface.blit(trend_surface, (220, y_offset))
            else:
                # Neutral indicator
                neutral_text = "—"
                neutral_surface = self.font_small.render(neutral_text, True, self.neutral_color)
                bg_surface.blit(neutral_surface, (220, y_offset))
            
            y_offset += 18
        
        # Draw trade count
        trade_count = len(getattr(self, 'economy', {}).get('trade_history', []))
        count_text = f"Trades: {trade_count}"
        count_surface = self.font_small.render(count_text, True, self.text_color)
        bg_surface.blit(count_surface, (10, y_offset + 5))
        
        # Blit to screen
        screen.blit(bg_surface, (self.x, self.y))
    
    def set_economy(self, economy: Economy):
        """Set the economy reference for trade count."""
        self.economy = economy


class PriceIndicator:
    """Individual price indicator that can be shown above kids."""
    
    def __init__(self, candy_type: str, price: float, position: Tuple[int, int]):
        self.candy_type = candy_type
        self.price = price
        self.position = position
        self.lifetime = 3.0
        self.max_lifetime = 3.0
        self.active = True
        
        # Font setup
        self.font = pygame.font.Font(None, 16)
        
        # Get candy color
        candy_props = CandyTypes.get_visual_properties(candy_type)
        self.color = candy_props.get('color', (255, 255, 255))
    
    def update(self, dt: float) -> bool:
        """Update indicator lifetime."""
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            return False
        return True
    
    def render(self, screen: pygame.Surface):
        """Render the price indicator."""
        if not self.active:
            return
        
        # Calculate alpha based on lifetime
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        # Create text
        text = f"{self.candy_type}: ${self.price:.1f}"
        text_surface = self.font.render(text, True, self.color)
        
        # Create surface with alpha
        alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        alpha_surface.blit(text_surface, (0, 0))
        alpha_surface.set_alpha(alpha)
        
        # Blit to screen
        screen.blit(alpha_surface, self.position)
