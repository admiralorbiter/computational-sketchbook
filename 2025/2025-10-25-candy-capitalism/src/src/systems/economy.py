"""
Economy system for managing candy values and market dynamics.

Handles real values, market prices, trade history, and price discovery
mechanisms that drive the economic simulation.
"""

from typing import Dict, List, Any, Optional, Deque
from collections import deque
import time
from ..entities.kid import Kid
from ..core.config_manager import config_manager


class Trade:
    """Represents a completed trade."""
    
    def __init__(self, candy_type: str, price: float, kid_a_id: str, 
                 kid_b_id: str, timestamp: float):
        self.candy_type = candy_type
        self.price = price
        self.kid_a_id = kid_a_id
        self.kid_b_id = kid_b_id
        self.timestamp = timestamp


class Economy:
    """
    Manages the candy economy and market dynamics.
    
    Tracks real values, market prices, trade history, and implements
    price discovery mechanisms that create emergent market behavior.
    """
    
    def __init__(self):
        """Initialize the economy system."""
        # Load real values from config
        self.real_values = self._load_real_values()
        
        # Load economy settings
        self.settings = self._load_economy_settings()
        
        # Market history (for price calculations)
        history_window = self.settings.get('market_history_window', 20)
        self.trade_history: Deque[Trade] = deque(maxlen=history_window)
        self.market_prices: Dict[str, float] = {}
        
        # Price discovery
        self.discovery_active = True
        self.discovery_progress = 0.0
        self.discovery_rate = self.settings.get('convergence_rate', 0.1)
        
        # Market state
        self.volatility = 1.0  # Market volatility multiplier
        self.trend_strength = 0.0  # Current trend strength
    
    def _load_real_values(self) -> Dict[str, float]:
        """Load real values from candy types config."""
        try:
            if not config_manager.configs:
                config_manager.load_all()
            
            candy_config = config_manager.get('candy_types')
            if candy_config:
                real_values = {}
                for candy_key, properties in candy_config.items():
                    real_values[candy_key] = properties.get('real_value', 5.0)
                return real_values
        except Exception as e:
            print(f"Warning: Could not load real values from config: {e}")
        
        # Fallback values
        return {
            'CHOCOLATE': 8.0,
            'FRUITY': 5.0,
            'SOUR': 6.0,
            'NOVELTY': 4.0,
            'HEALTH': 2.0,
            'TRASH': 1.0,
        }
    
    def _load_economy_settings(self) -> Dict[str, Any]:
        """Load economy settings from game settings config."""
        try:
            if not config_manager.configs:
                config_manager.load_all()
            
            game_settings = config_manager.get('game_settings')
            if game_settings and 'economy' in game_settings:
                return game_settings['economy']
        except Exception as e:
            print(f"Warning: Could not load economy settings: {e}")
        
        # Default settings
        return {
            'price_discovery_mode': 'fixed',
            'convergence_rate': 0.1,
            'market_history_window': 20,
            'enable_multi_item_trades': True
        }
        
    def update(self, dt: float):
        """
        Update economy state.
        
        Args:
            dt: Delta time in seconds
        """
        # Update market prices from recent trades
        self._calculate_market_prices()
        
        # Price discovery convergence
        if self.discovery_active:
            self._update_discovery(dt)
        
        # Update market trends
        self._update_trends()
    
    def _calculate_market_prices(self):
        """Calculate market price as weighted average of recent trades."""
        trades_by_candy = {}
        
        for trade in self.trade_history:
            candy_type = trade.candy_type
            if candy_type not in trades_by_candy:
                trades_by_candy[candy_type] = []
            trades_by_candy[candy_type].append(trade.price)
        
        for candy_type, prices in trades_by_candy.items():
            if not prices:
                continue
            
            # Weighted average, more recent trades have higher weight
            weights = [1.0 + i * 0.1 for i in range(len(prices))]
            try:
                import numpy as np
                self.market_prices[candy_type] = np.average(prices, weights=weights)
            except ImportError:
                # Fallback if numpy not available
                weighted_sum = sum(p * w for p, w in zip(prices, weights))
                weight_sum = sum(weights)
                self.market_prices[candy_type] = weighted_sum / weight_sum
    
    def _update_discovery(self, dt: float):
        """Gradually converge believed values toward real values."""
        self.discovery_progress += self.discovery_rate * dt
        
        if self.discovery_progress >= 1.0:
            self.discovery_active = False
            return
    
    def _update_trends(self):
        """Update market trends and volatility."""
        if len(self.trade_history) < 10:
            return
        
        # Calculate recent price changes
        recent_trades = list(self.trade_history)[-10:]
        price_changes = []
        
        for i in range(1, len(recent_trades)):
            if recent_trades[i].candy_type == recent_trades[i-1].candy_type:
                change = recent_trades[i].price - recent_trades[i-1].price
                price_changes.append(change)
        
        if price_changes:
            # Calculate trend strength
            avg_change = sum(price_changes) / len(price_changes)
            self.trend_strength = min(1.0, abs(avg_change) / 2.0)
            
            # Calculate volatility
            variance = sum((change - avg_change) ** 2 for change in price_changes) / len(price_changes)
            self.volatility = min(2.0, 1.0 + variance)
    
    def record_trade(self, candy_type: str, price: float, kid_a_id: str, kid_b_id: str):
        """
        Record a completed trade.
        
        Args:
            candy_type: Type of candy traded
            price: Price of the trade
            kid_a_id: ID of first kid
            kid_b_id: ID of second kid
        """
        trade = Trade(candy_type, price, kid_a_id, kid_b_id, time.time())
        self.trade_history.append(trade)
    
    def get_market_price(self, candy_type: str) -> float:
        """
        Get current market price for a candy type.
        
        Args:
            candy_type: Type of candy
            
        Returns:
            Current market price, or real value if no trades
        """
        if candy_type in self.market_prices:
            return self.market_prices[candy_type]
        return self.real_values.get(candy_type, 1.0)
    
    def get_real_value(self, candy_type: str) -> float:
        """
        Get real value for a candy type.
        
        Args:
            candy_type: Type of candy
            
        Returns:
            Real value of the candy
        """
        return self.real_values.get(candy_type, 1.0)
    
    def get_price_trend(self, candy_type: str) -> float:
        """
        Get price trend for a candy type.
        
        Args:
            candy_type: Type of candy
            
        Returns:
            Price trend (-1.0 to 1.0, negative = falling, positive = rising)
        """
        candy_trades = [t for t in self.trade_history if t.candy_type == candy_type]
        
        if len(candy_trades) < 2:
            return 0.0
        
        recent_trades = candy_trades[-5:]  # Last 5 trades
        if len(recent_trades) < 2:
            return 0.0
        
        # Calculate trend
        first_price = recent_trades[0].price
        last_price = recent_trades[-1].price
        
        if first_price == 0:
            return 0.0
        
        trend = (last_price - first_price) / first_price
        return max(-1.0, min(1.0, trend))
    
    def get_market_volatility(self) -> float:
        """Get current market volatility."""
        return self.volatility
    
    def get_trend_strength(self) -> float:
        """Get current trend strength."""
        return self.trend_strength
    
    def is_discovery_active(self) -> bool:
        """Check if price discovery is still active."""
        return self.discovery_active
    
    def get_discovery_progress(self) -> float:
        """Get price discovery progress (0.0 to 1.0)."""
        return self.discovery_progress
    
    def force_discovery_complete(self):
        """Force price discovery to complete immediately."""
        self.discovery_active = False
        self.discovery_progress = 1.0
    
    def reset_discovery(self):
        """Reset price discovery to initial state."""
        self.discovery_active = True
        self.discovery_progress = 0.0
    
    def get_trade_history(self, candy_type: str = None, limit: int = None) -> List[Trade]:
        """
        Get trade history.
        
        Args:
            candy_type: Filter by candy type (optional)
            limit: Maximum number of trades to return (optional)
            
        Returns:
            List of trades
        """
        trades = list(self.trade_history)
        
        if candy_type:
            trades = [t for t in trades if t.candy_type == candy_type]
        
        if limit:
            trades = trades[-limit:]
        
        return trades
    
    def get_market_stats(self) -> Dict[str, Any]:
        """Get market statistics."""
        return {
            'total_trades': len(self.trade_history),
            'discovery_active': self.discovery_active,
            'discovery_progress': self.discovery_progress,
            'volatility': self.volatility,
            'trend_strength': self.trend_strength,
            'market_prices': self.market_prices.copy(),
            'real_values': self.real_values.copy()
        }
