"""
Data fetching utilities for real-time market data integration.
Provides easy access to current prices and market data for the Flask app.
"""

import logging
import time
from typing import Dict, Optional, Tuple
from .market_data import SyncMarketDataService, MarketPrice
from .kalshi_integration import SyncKalshiIntegration

logger = logging.getLogger(__name__)


class DataFetcher:
    """Main data fetcher for the Flask app."""
    
    def __init__(self):
        self.market_service = SyncMarketDataService(enable_binance=False)  # Disable Binance by default
        self.kalshi_service = SyncKalshiIntegration()
    
    def get_crypto_prices(self) -> Dict[str, Optional[MarketPrice]]:
        """Get current prices for BTC and ETH from multiple sources."""
        prices = {}
        
        # Try to get BTC price
        try:
            btc_price = self.market_service.get_price("BTC-USD")
            if btc_price is None:
                # Fallback to mock data
                btc_price = MarketPrice(
                    symbol="BTC-USD",
                    price=45000.0,  # Mock price
                    timestamp=time.time(),
                    source="Mock (API failed)",
                    volume_24h=None,
                    change_24h=None
                )
            prices["BTC"] = btc_price
        except Exception as e:
            logger.error(f"Error fetching BTC price: {e}")
            # Fallback to mock data
            prices["BTC"] = MarketPrice(
                symbol="BTC-USD",
                price=45000.0,
                timestamp=time.time(),
                source="Mock (Error)",
                volume_24h=None,
                change_24h=None
            )
        
        # Try to get ETH price
        try:
            eth_price = self.market_service.get_price("ETH-USD")
            if eth_price is None:
                # Fallback to mock data
                eth_price = MarketPrice(
                    symbol="ETH-USD",
                    price=3000.0,  # Mock price
                    timestamp=time.time(),
                    source="Mock (API failed)",
                    volume_24h=None,
                    change_24h=None
                )
            prices["ETH"] = eth_price
        except Exception as e:
            logger.error(f"Error fetching ETH price: {e}")
            # Fallback to mock data
            prices["ETH"] = MarketPrice(
                symbol="ETH-USD",
                price=3000.0,
                timestamp=time.time(),
                source="Mock (Error)",
                volume_24h=None,
                change_24h=None
            )
        
        return prices
    
    def get_nasdaq_price(self) -> Optional[MarketPrice]:
        """Get current NASDAQ-100 price."""
        try:
            # For now, return a mock price - you'd implement real NASDAQ data fetching here
            return self.market_service.get_nasdaq_price()
        except Exception as e:
            logger.error(f"Error fetching NASDAQ price: {e}")
            return None
    
    def get_kalshi_markets(self) -> list:
        """Get relevant Kalshi markets for BTC/ETH/NASDAQ."""
        try:
            return self.market_service.get_kalshi_markets()
        except Exception as e:
            logger.error(f"Error fetching Kalshi markets: {e}")
            return []
    
    def get_market_summary(self) -> Dict:
        """Get a summary of all market data."""
        crypto_prices = self.get_crypto_prices()
        nasdaq_price = self.get_nasdaq_price()
        kalshi_markets = self.get_kalshi_markets()
        kalshi_relevant = self.kalshi_service.get_relevant_markets()
        
        return {
            "crypto_prices": crypto_prices,
            "nasdaq_price": nasdaq_price,
            "kalshi_markets": kalshi_markets,
            "kalshi_relevant": kalshi_relevant,
            "timestamp": self._get_current_timestamp()
        }
    
    def get_kalshi_markets_with_analysis(self, bankroll: float = 1000.0, bitcoin_analysis: Dict = None) -> Dict:
        """Get Kalshi markets with betting analysis and recommendations."""
        try:
            # Get current crypto prices for analysis
            crypto_prices = self.get_crypto_prices()
            btc_price = crypto_prices.get("BTC").price if crypto_prices.get("BTC") else None
            eth_price = crypto_prices.get("ETH").price if crypto_prices.get("ETH") else None
            
            # Get markets with analysis using the provided bankroll and Bitcoin analysis
            kalshi_data = self.kalshi_service.get_markets_with_analysis(btc_price, eth_price, bankroll, bitcoin_analysis)
            return kalshi_data
        except Exception as e:
            logger.error(f"Error fetching Kalshi markets with analysis: {e}")
            return self.kalshi_service.get_relevant_markets()
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    def get_price_for_symbol(self, symbol: str) -> Optional[float]:
        """Get current price for a specific symbol."""
        if symbol.upper() in ["BTC", "BITCOIN"]:
            btc_price = self.get_crypto_prices().get("BTC")
            return btc_price.price if btc_price else None
        elif symbol.upper() in ["ETH", "ETHEREUM"]:
            eth_price = self.get_crypto_prices().get("ETH")
            return eth_price.price if eth_price else None
        elif symbol.upper() in ["NDX", "NASDAQ", "NASDAQ-100"]:
            nasdaq_price = self.get_nasdaq_price()
            return nasdaq_price.price if nasdaq_price else None
        else:
            logger.warning(f"Unknown symbol: {symbol}")
            return None


# Global instance for the Flask app
data_fetcher = DataFetcher()
