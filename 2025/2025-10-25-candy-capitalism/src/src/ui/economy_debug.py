"""
Economy debug overlay.

Shows detailed economy information including kid beliefs, market prices,
and price discovery progress when enabled.
"""

import pygame
from typing import Dict, List, Tuple, Optional
from ..systems.economy import Economy
from ..entities.kid import Kid
from ..core.candy_types import CandyTypes


class EconomyDebugOverlay:
    """Debug overlay for economy information."""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.visible = False
        
        # Font setup
        self.font_large = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 14)
        
        # Colors
        self.bg_color = (0, 0, 0, 180)  # Semi-transparent black
        self.text_color = (255, 255, 255)
        self.header_color = (100, 255, 100)
        self.warning_color = (255, 255, 100)
        self.error_color = (255, 100, 100)
        
        # Layout
        self.padding = 20
        self.line_height = 20
        self.section_spacing = 30
    
    def toggle(self):
        """Toggle debug overlay visibility."""
        self.visible = not self.visible
    
    def render(self, screen: pygame.Surface, economy: Economy, kids: List[Kid], camera=None):
        """Render the debug overlay."""
        if not self.visible:
            return
        
        # Create background
        bg_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        bg_surface.fill(self.bg_color)
        
        y_offset = self.padding
        
        # Economy overview
        y_offset = self._render_economy_overview(bg_surface, economy, y_offset)
        y_offset += self.section_spacing
        
        # Price discovery progress
        y_offset = self._render_price_discovery(bg_surface, economy, y_offset)
        y_offset += self.section_spacing
        
        # Market prices vs real values
        y_offset = self._render_price_comparison(bg_surface, economy, y_offset)
        y_offset += self.section_spacing
        
        # Kid beliefs (first 5 kids)
        y_offset = self._render_kid_beliefs(bg_surface, kids[:5], economy, y_offset)
        y_offset += self.section_spacing
        
        # Recent trades
        y_offset = self._render_recent_trades(bg_surface, economy, y_offset)
        
        # Blit to screen
        screen.blit(bg_surface, (0, 0))
    
    def _render_economy_overview(self, surface: pygame.Surface, economy: Economy, y_offset: int) -> int:
        """Render economy overview section."""
        # Header
        header_text = self.font_large.render("Economy Overview", True, self.header_color)
        surface.blit(header_text, (self.padding, y_offset))
        y_offset += self.line_height + 5
        
        # Total trades
        trade_count = len(economy.trade_history)
        trades_text = f"Total Trades: {trade_count}"
        surface.blit(self.font_medium.render(trades_text, True, self.text_color), 
                    (self.padding, y_offset))
        y_offset += self.line_height
        
        # Discovery status
        discovery_status = "Active" if economy.discovery_active else "Complete"
        discovery_color = self.warning_color if economy.discovery_active else self.text_color
        discovery_text = f"Price Discovery: {discovery_status} ({economy.discovery_progress*100:.1f}%)"
        surface.blit(self.font_medium.render(discovery_text, True, discovery_color), 
                    (self.padding, y_offset))
        y_offset += self.line_height
        
        # Market volatility
        volatility_text = f"Market Volatility: {economy.volatility:.2f}"
        surface.blit(self.font_medium.render(volatility_text, True, self.text_color), 
                    (self.padding, y_offset))
        y_offset += self.line_height
        
        # Trend strength
        trend_text = f"Trend Strength: {economy.trend_strength:.2f}"
        surface.blit(self.font_medium.render(trend_text, True, self.text_color), 
                    (self.padding, y_offset))
        y_offset += self.line_height
        
        return y_offset
    
    def _render_price_discovery(self, surface: pygame.Surface, economy: Economy, y_offset: int) -> int:
        """Render price discovery section."""
        # Header
        header_text = self.font_large.render("Price Discovery", True, self.header_color)
        surface.blit(header_text, (self.padding, y_offset))
        y_offset += self.line_height + 5
        
        # Discovery mode
        mode = economy.settings.get('price_discovery_mode', 'fixed')
        mode_text = f"Mode: {mode}"
        surface.blit(self.font_medium.render(mode_text, True, self.text_color), 
                    (self.padding, y_offset))
        y_offset += self.line_height
        
        # Convergence rate
        rate = economy.settings.get('convergence_rate', 0.1)
        rate_text = f"Convergence Rate: {rate:.2f}"
        surface.blit(self.font_medium.render(rate_text, True, self.text_color), 
                    (self.padding, y_offset))
        y_offset += self.line_height
        
        return y_offset
    
    def _render_price_comparison(self, surface: pygame.Surface, economy: Economy, y_offset: int) -> int:
        """Render price comparison section."""
        # Header
        header_text = self.font_large.render("Market vs Real Prices", True, self.header_color)
        surface.blit(header_text, (self.padding, y_offset))
        y_offset += self.line_height + 5
        
        # Price comparison table
        candy_types = CandyTypes.get_all_types()
        
        for candy_type in candy_types:
            real_price = economy.get_real_value(candy_type)
            market_price = economy.get_market_price(candy_type)
            
            # Calculate difference
            if real_price > 0:
                diff = ((market_price - real_price) / real_price) * 100
                diff_color = self.warning_color if abs(diff) > 10 else self.text_color
            else:
                diff = 0
                diff_color = self.text_color
            
            # Candy name
            candy_name = CandyTypes.get_visual_properties(candy_type).get('name', candy_type)
            name_text = f"{candy_name}:"
            surface.blit(self.font_small.render(name_text, True, self.text_color), 
                        (self.padding, y_offset))
            
            # Prices
            price_text = f"Real: ${real_price:.1f} | Market: ${market_price:.1f} | Diff: {diff:+.1f}%"
            surface.blit(self.font_small.render(price_text, True, diff_color), 
                        (self.padding + 120, y_offset))
            
            y_offset += self.line_height - 2
        
        return y_offset
    
    def _render_kid_beliefs(self, surface: pygame.Surface, kids: List[Kid], economy: Economy, y_offset: int) -> int:
        """Render kid beliefs section."""
        # Header
        header_text = self.font_large.render("Kid Beliefs (First 5)", True, self.header_color)
        surface.blit(header_text, (self.padding, y_offset))
        y_offset += self.line_height + 5
        
        for kid in kids:
            # Kid ID and personality
            kid_text = f"{kid.id} ({kid.personality.name})"
            surface.blit(self.font_medium.render(kid_text, True, self.text_color), 
                        (self.padding, y_offset))
            y_offset += self.line_height - 2
            
            # Beliefs for each candy type
            candy_types = CandyTypes.get_all_types()
            for candy_type in candy_types[:3]:  # Show first 3 candy types
                if candy_type in kid.believed_values:
                    belief = kid.believed_values[candy_type]
                    real_value = economy.get_real_value(candy_type)
                    
                    # Calculate accuracy
                    if real_value > 0:
                        accuracy = (1 - abs(belief - real_value) / real_value) * 100
                        accuracy_color = self.text_color if accuracy > 80 else self.warning_color
                    else:
                        accuracy = 0
                        accuracy_color = self.text_color
                    
                    candy_name = CandyTypes.get_visual_properties(candy_type).get('name', candy_type)
                    belief_text = f"  {candy_name}: ${belief:.1f} (acc: {accuracy:.0f}%)"
                    surface.blit(self.font_small.render(belief_text, True, accuracy_color), 
                                (self.padding + 20, y_offset))
                    y_offset += self.line_height - 4
            
            y_offset += 5
        
        return y_offset
    
    def _render_recent_trades(self, surface: pygame.Surface, economy: Economy, y_offset: int) -> int:
        """Render recent trades section."""
        # Header
        header_text = self.font_large.render("Recent Trades", True, self.header_color)
        surface.blit(header_text, (self.padding, y_offset))
        y_offset += self.line_height + 5
        
        # Get recent trades
        recent_trades = economy.get_trade_history(limit=5)
        
        if not recent_trades:
            no_trades_text = "No trades yet"
            surface.blit(self.font_medium.render(no_trades_text, True, self.text_color), 
                        (self.padding, y_offset))
            y_offset += self.line_height
        else:
            for trade in recent_trades[-5:]:  # Last 5 trades
                trade_text = f"{trade.candy_type}: ${trade.price:.1f} ({trade.kid_a_id} <-> {trade.kid_b_id})"
                surface.blit(self.font_small.render(trade_text, True, self.text_color), 
                            (self.padding, y_offset))
                y_offset += self.line_height - 2
        
        return y_offset
