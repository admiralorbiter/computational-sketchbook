"""
Unit tests for the economy system.

Tests core economy calculations, price discovery, and market dynamics.
"""

import pytest
from src.systems.economy import Economy


class TestEconomy:
    """Test cases for the Economy class."""
    
    def test_initialization(self, sample_economy):
        """Test economy initialization."""
        economy = sample_economy
        
        assert economy.discovery_active is True
        assert economy.discovery_progress == 0.0
        assert economy.volatility == 1.0
        assert economy.trend_strength == 0.0
        assert len(economy.real_values) == 6
        assert economy.real_values["CHOCOLATE"] == 8.0
        assert economy.real_values["TRASH"] == 1.0
    
    def test_get_real_value(self, sample_economy):
        """Test getting real values for candy types."""
        economy = sample_economy
        
        assert economy.get_real_value("CHOCOLATE") == 8.0
        assert economy.get_real_value("FRUITY") == 5.0
        assert economy.get_real_value("UNKNOWN") == 1.0  # Default value
    
    def test_record_trade(self, sample_economy):
        """Test recording trades."""
        economy = sample_economy
        
        # Record a trade
        economy.record_trade("CHOCOLATE", 7.5, "kid1", "kid2")
        
        # Check trade was recorded
        assert len(economy.trade_history) == 1
        trade = economy.trade_history[0]
        assert trade.candy_type == "CHOCOLATE"
        assert trade.price == 7.5
        assert trade.kid_a_id == "kid1"
        assert trade.kid_b_id == "kid2"
    
    def test_market_price_calculation(self, sample_economy):
        """Test market price calculation from trades."""
        economy = sample_economy
        
        # Record several trades
        economy.record_trade("CHOCOLATE", 8.0, "kid1", "kid2")
        economy.record_trade("CHOCOLATE", 7.5, "kid2", "kid3")
        economy.record_trade("CHOCOLATE", 8.5, "kid3", "kid1")
        
        # Update economy to calculate market prices
        economy.update(0.1)
        
        # Check market price was calculated
        assert "CHOCOLATE" in economy.market_prices
        # Price should be close to average of trades
        assert 7.5 <= economy.market_prices["CHOCOLATE"] <= 8.5
    
    def test_get_market_price(self, sample_economy):
        """Test getting market prices."""
        economy = sample_economy
        
        # No trades yet, should return real value
        price = economy.get_market_price("CHOCOLATE")
        assert price == 8.0
        
        # Record a trade and update
        economy.record_trade("CHOCOLATE", 7.0, "kid1", "kid2")
        economy.update(0.1)
        
        # Should return market price
        price = economy.get_market_price("CHOCOLATE")
        assert price == 7.0
    
    def test_price_trend_calculation(self, sample_economy):
        """Test price trend calculation."""
        economy = sample_economy
        
        # Record trades with increasing prices
        economy.record_trade("CHOCOLATE", 7.0, "kid1", "kid2")
        economy.record_trade("CHOCOLATE", 8.0, "kid2", "kid3")
        economy.record_trade("CHOCOLATE", 9.0, "kid3", "kid1")
        
        economy.update(0.1)
        
        # Should show positive trend
        trend = economy.get_price_trend("CHOCOLATE")
        assert trend > 0
    
    def test_discovery_progress(self, sample_economy):
        """Test price discovery progress."""
        economy = sample_economy
        
        assert economy.is_discovery_active() is True
        assert economy.get_discovery_progress() == 0.0
        
        # Update several times
        for _ in range(100):
            economy.update(0.1)
        
        # Discovery should have progressed
        assert economy.get_discovery_progress() > 0.0
    
    def test_force_discovery_complete(self, sample_economy):
        """Test forcing discovery to complete."""
        economy = sample_economy
        
        economy.force_discovery_complete()
        
        assert economy.is_discovery_active() is False
        assert economy.get_discovery_progress() == 1.0
    
    def test_reset_discovery(self, sample_economy):
        """Test resetting discovery."""
        economy = sample_economy
        
        # Force complete, then reset
        economy.force_discovery_complete()
        economy.reset_discovery()
        
        assert economy.is_discovery_active() is True
        assert economy.get_discovery_progress() == 0.0
    
    def test_get_trade_history(self, sample_economy):
        """Test getting trade history."""
        economy = sample_economy
        
        # Record some trades
        economy.record_trade("CHOCOLATE", 8.0, "kid1", "kid2")
        economy.record_trade("FRUITY", 5.0, "kid2", "kid3")
        economy.record_trade("CHOCOLATE", 7.5, "kid3", "kid1")
        
        # Get all trades
        all_trades = economy.get_trade_history()
        assert len(all_trades) == 3
        
        # Get chocolate trades only
        chocolate_trades = economy.get_trade_history("CHOCOLATE")
        assert len(chocolate_trades) == 2
        
        # Get limited trades
        limited_trades = economy.get_trade_history(limit=2)
        assert len(limited_trades) == 2
    
    def test_market_stats(self, sample_economy):
        """Test getting market statistics."""
        economy = sample_economy
        
        # Record some trades
        economy.record_trade("CHOCOLATE", 8.0, "kid1", "kid2")
        economy.update(0.1)
        
        stats = economy.get_market_stats()
        
        assert "total_trades" in stats
        assert "discovery_active" in stats
        assert "market_prices" in stats
        assert "real_values" in stats
        assert stats["total_trades"] == 1
