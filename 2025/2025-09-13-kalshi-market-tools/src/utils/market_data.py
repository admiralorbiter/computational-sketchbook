"""
Market data service for real-time price feeds from various exchanges.
Supports Kalshi, Coinbase, Kraken, and Binance APIs.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import aiohttp
import requests
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MarketPrice:
    """Represents a market price with metadata."""
    symbol: str
    price: float
    timestamp: float
    source: str
    volume_24h: Optional[float] = None
    change_24h: Optional[float] = None


class MarketDataService:
    """Service for fetching real-time market data from multiple sources."""
    
    def __init__(self, enable_binance: bool = False):
        self.session = None
        self.cache = {}
        self.cache_ttl = 30  # 30 seconds cache
        self.enable_binance = enable_binance
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self.cache:
            return False
        return time.time() - self.cache[key]['timestamp'] < self.cache_ttl
    
    def _get_cached(self, key: str) -> Optional[MarketPrice]:
        """Get cached data if valid."""
        if self._is_cache_valid(key):
            return self.cache[key]['data']
        return None
    
    def _set_cache(self, key: str, data: MarketPrice):
        """Cache data with timestamp."""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    async def get_coinbase_price(self, symbol: str) -> Optional[MarketPrice]:
        """Get price from Coinbase Advanced Trade API."""
        try:
            cache_key = f"coinbase_{symbol}"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
                
            # Try the simpler public API first
            url = f"https://api.coinbase.com/v2/exchange-rates?currency={symbol.split('-')[0]}"
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data and 'rates' in data['data'] and 'USD' in data['data']['rates']:
                        price = float(data['data']['rates']['USD'])
                        
                        market_price = MarketPrice(
                            symbol=symbol,
                            price=price,
                            timestamp=time.time(),
                            source="Coinbase",
                            volume_24h=None,
                            change_24h=None
                        )
                        
                        self._set_cache(cache_key, market_price)
                        return market_price
                else:
                    logger.warning(f"Coinbase API error for {symbol}: {response.status}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Coinbase API timeout for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Error fetching Coinbase data for {symbol}: {e}")
            return None
    
    async def get_kraken_price(self, symbol: str) -> Optional[MarketPrice]:
        """Get price from Kraken API."""
        try:
            cache_key = f"kraken_{symbol}"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
                
            # Kraken uses different symbol format
            kraken_symbol = self._convert_to_kraken_symbol(symbol)
            url = f"https://api.kraken.com/0/public/Ticker?pair={kraken_symbol}"
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'result' in data and kraken_symbol in data['result']:
                        ticker = data['result'][kraken_symbol]
                        price = float(ticker['c'][0])  # Last trade closed price
                        volume = float(ticker['v'][1])  # Volume today
                        
                        market_price = MarketPrice(
                            symbol=symbol,
                            price=price,
                            timestamp=time.time(),
                            source="Kraken",
                            volume_24h=volume,
                            change_24h=None  # Would need additional calculation
                        )
                        
                        self._set_cache(cache_key, market_price)
                        return market_price
                else:
                    logger.warning(f"Kraken API error for {symbol}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching Kraken data for {symbol}: {e}")
            return None
    
    async def get_binance_price(self, symbol: str) -> Optional[MarketPrice]:
        """Get price from Binance API."""
        try:
            cache_key = f"binance_{symbol}"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
                
            # Use the simpler price endpoint
            symbol_clean = symbol.replace('-', '')
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol_clean}"
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'price' in data:
                        price = float(data['price'])
                        
                        market_price = MarketPrice(
                            symbol=symbol,
                            price=price,
                            timestamp=time.time(),
                            source="Binance",
                            volume_24h=None,
                            change_24h=None
                        )
                        
                        self._set_cache(cache_key, market_price)
                        return market_price
                else:
                    logger.warning(f"Binance API error for {symbol}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching Binance data for {symbol}: {e}")
            return None
    
    def _convert_to_kraken_symbol(self, symbol: str) -> str:
        """Convert standard symbol to Kraken format."""
        symbol_map = {
            'BTC-USD': 'XXBTZUSD',
            'ETH-USD': 'XETHZUSD',
            'BTCUSDT': 'XXBTZUSD',
            'ETHUSDT': 'XETHZUSD'
        }
        return symbol_map.get(symbol, symbol)
    
    async def get_kalshi_markets(self) -> List[Dict]:
        """Get Kalshi market data for BTC/ETH/NASDAQ markets."""
        try:
            cache_key = "kalshi_markets"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]['data']
                
            url = "https://api.elections.kalshi.com/trade-api/v2/markets"
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    markets = data.get('markets', [])
                    
                    # Filter for BTC/ETH/NASDAQ markets
                    relevant_markets = [
                        m for m in markets 
                        if any(keyword in m.get('title', '').lower() 
                              for keyword in ['bitcoin', 'btc', 'ethereum', 'eth', 'nasdaq', 'ndx'])
                    ]
                    
                    self.cache[cache_key] = {
                        'data': relevant_markets,
                        'timestamp': time.time()
                    }
                    return relevant_markets
                else:
                    logger.warning(f"Kalshi API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching Kalshi markets: {e}")
            return []
    
    async def get_best_price(self, symbol: str) -> Optional[MarketPrice]:
        """Get the best available price from multiple sources."""
        sources = [
            self.get_coinbase_price(symbol),
            self.get_kraken_price(symbol)
        ]
        
        # Only include Binance if enabled
        if self.enable_binance:
            sources.append(self.get_binance_price(symbol))
        
        results = await asyncio.gather(*sources, return_exceptions=True)
        
        # Filter out exceptions and None values
        valid_prices = [r for r in results if isinstance(r, MarketPrice)]
        
        if not valid_prices:
            return None
            
        # Return the first valid price (could implement logic to choose best)
        return valid_prices[0]
    
    def get_nasdaq_price(self) -> Optional[MarketPrice]:
        """Get NASDAQ-100 price using a simple approach (would need real implementation)."""
        # This is a placeholder - you'd need to implement actual NASDAQ data fetching
        # For now, return a mock price
        return MarketPrice(
            symbol="NDX",
            price=15000.0,  # Mock price
            timestamp=time.time(),
            source="Mock",
            volume_24h=None,
            change_24h=None
        )


# Synchronous wrapper for Flask app
class SyncMarketDataService:
    """Synchronous wrapper for the async market data service."""
    
    def __init__(self, enable_binance: bool = False):
        self.service = MarketDataService(enable_binance=enable_binance)
    
    def get_price(self, symbol: str) -> Optional[MarketPrice]:
        """Get price synchronously."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._get_price_async(symbol))
        finally:
            loop.close()
    
    async def _get_price_async(self, symbol: str) -> Optional[MarketPrice]:
        async with self.service as service:
            return await service.get_best_price(symbol)
    
    def get_kalshi_markets(self) -> List[Dict]:
        """Get Kalshi markets synchronously."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._get_kalshi_markets_async())
        finally:
            loop.close()
    
    async def _get_kalshi_markets_async(self) -> List[Dict]:
        async with self.service as service:
            return await service.get_kalshi_markets()
    
    def get_nasdaq_price(self) -> Optional[MarketPrice]:
        """Get NASDAQ-100 price synchronously."""
        return self.service.get_nasdaq_price()
