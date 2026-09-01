"""
Kalshi API integration for market data and order book information.
Provides access to real Kalshi markets and pricing data.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
import aiohttp
import requests
from datetime import datetime, timezone
from .betting_analysis import BettingAnalyzer

logger = logging.getLogger(__name__)


class KalshiIntegration:
    """Integration with Kalshi API for market data."""
    
    def __init__(self):
        self.base_url = "https://api.elections.kalshi.com/trade-api/v2"
        self.session = None
        self.cache = {}
        self.cache_ttl = 60  # 1 minute cache for market data
        self.betting_analyzer = BettingAnalyzer()
    
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
        return (datetime.now().timestamp() - self.cache[key]['timestamp']) < self.cache_ttl
    
    def _get_cached(self, key: str):
        """Get cached data if valid."""
        if self._is_cache_valid(key):
            return self.cache[key]['data']
        return None
    
    def _set_cache(self, key: str, data):
        """Cache data with timestamp."""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now().timestamp()
        }
    
    async def get_markets(self, status: str = "open") -> List[Dict]:
        """Get all markets from Kalshi."""
        try:
            cache_key = f"markets_{status}"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
                
            url = f"{self.base_url}/markets"
            params = {"status": status}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    markets = data.get('markets', [])
                    self._set_cache(cache_key, markets)
                    return markets
                else:
                    logger.warning(f"Kalshi API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching Kalshi markets: {e}")
            return []
    
    async def get_market_by_ticker(self, ticker: str) -> Optional[Dict]:
        """Get a specific market by ticker."""
        try:
            cache_key = f"market_{ticker}"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
                
            url = f"{self.base_url}/markets/{ticker}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    market = data.get('market')
                    if market:
                        self._set_cache(cache_key, market)
                    return market
                else:
                    logger.warning(f"Kalshi API error for ticker {ticker}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching Kalshi market {ticker}: {e}")
            return None
    
    async def get_market_orderbook(self, ticker: str) -> Optional[Dict]:
        """Get order book for a specific market."""
        try:
            cache_key = f"orderbook_{ticker}"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
                
            url = f"{self.base_url}/markets/{ticker}/orderbook"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    orderbook = data.get('orderbook')
                    if orderbook:
                        self._set_cache(cache_key, orderbook)
                    return orderbook
                else:
                    logger.warning(f"Kalshi API error for orderbook {ticker}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching Kalshi orderbook {ticker}: {e}")
            return None
    
    async def get_crypto_markets(self) -> List[Dict]:
        """Get BTC and ETH hourly markets from Kalshi."""
        try:
            cache_key = "crypto_hourly_markets"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
                
            # Search for BTC and ETH hourly markets
            btc_markets = await self._search_crypto_markets('bitcoin', 'btc')
            eth_markets = await self._search_crypto_markets('ethereum', 'eth')
            
            all_crypto_markets = btc_markets + eth_markets
            self._set_cache(cache_key, all_crypto_markets)
            return all_crypto_markets
            
        except Exception as e:
            logger.error(f"Error fetching crypto markets: {e}")
            return []
    
    async def _search_crypto_markets(self, crypto_name: str, crypto_ticker: str) -> List[Dict]:
        """Search for specific crypto markets using the real series."""
        # Use the actual crypto series we found
        series_mapping = {
            'bitcoin': 'KXBTCD',  # Bitcoin price Above/below daily
            'btc': 'KXBTCD',
            'ethereum': 'KXETHD',  # Ethereum price Above/below daily  
            'eth': 'KXETHD'
        }
        
        series_ticker = series_mapping.get(crypto_name.lower())
        if not series_ticker:
            logger.warning(f"No series mapping found for {crypto_name}")
            return []
        
        try:
            # Get markets from the specific crypto series
            url = f"{self.base_url}/markets"
            params = {
                "status": "open",
                "series_ticker": series_ticker
            }
            
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    markets = data.get('markets', [])
                    
                    # Filter for markets with volume > 0 (active trading)
                    active_markets = [m for m in markets if m.get('volume', 0) > 0]
                    
                    # If no active markets, take the first 10 markets
                    if not active_markets:
                        active_markets = markets[:10]
                    
                    logger.info(f"Found {len(active_markets)} {crypto_name} markets in series {series_ticker}")
                    return active_markets
                else:
                    logger.warning(f"Kalshi API error for {series_ticker}: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching for {crypto_name} in series {series_ticker}: {e}")
            return []
    
    async def get_nasdaq_markets(self) -> List[Dict]:
        """Get NASDAQ-related markets from Kalshi."""
        markets = await self.get_markets()
        nasdaq_keywords = ['nasdaq', 'ndx', 'nasdaq-100', 'nasdaq100']
        
        nasdaq_markets = []
        for market in markets:
            title = market.get('title', '').lower()
            if any(keyword in title for keyword in nasdaq_keywords):
                nasdaq_markets.append(market)
        
        return nasdaq_markets
    
    def get_market_price_info(self, market: Dict) -> Dict:
        """Extract price information from a market."""
        try:
            # Kalshi API uses different field names
            yes_bid = market.get('yes_bid', 0)
            yes_ask = market.get('yes_ask', 0)
            yes_price = market.get('yes_price', 0)  # Mid price from API
            
            # Calculate mid price if not provided
            if yes_price == 0 and yes_ask > 0:
                yes_mid = (yes_bid + yes_ask) / 2
            else:
                yes_mid = yes_price
            
            # Extract time information
            close_time = market.get('close_time', '')
            time_left = self._calculate_time_left(close_time)
            
            # Extract strike price from title or ticker if possible
            strike_price = self._extract_strike_price(market.get('title', ''), market.get('ticker', ''))
            
            return {
                'ticker': market.get('ticker', ''),
                'title': market.get('title', ''),
                'status': market.get('status', ''),
                'yes_bid': yes_bid,
                'yes_ask': yes_ask,
                'yes_mid': yes_mid,
                'yes_price': yes_price,
                'volume': market.get('volume', 0),
                'open_interest': market.get('open_interest', 0),
                'close_time': close_time,
                'time_left': time_left,
                'strike_price': strike_price,
                'last_trade_price': market.get('last_trade_price', 0),
                'last_trade_yes_price': market.get('last_trade_yes_price', 0),
                'event_ticker': market.get('event_ticker', ''),
                'series_ticker': market.get('series_ticker', ''),
                'min_tick_size': market.get('min_tick_size', 0.01),
                'can_close_early': market.get('can_close_early', False)
            }
        except Exception as e:
            logger.error(f"Error extracting price info from market: {e}")
            return {}
    
    def _calculate_time_left(self, close_time: str) -> str:
        """Calculate time left until market closes."""
        if not close_time:
            return "Unknown"
        
        try:
            from datetime import datetime, timezone
            import dateutil.parser
            
            # Parse the close time
            close_dt = dateutil.parser.parse(close_time)
            now = datetime.now(timezone.utc)
            
            # Calculate time difference
            time_diff = close_dt - now
            
            if time_diff.total_seconds() <= 0:
                return "Closed"
            
            # Format time left
            days = time_diff.days
            hours, remainder = divmod(time_diff.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
                
        except Exception as e:
            logger.error(f"Error calculating time left: {e}")
            return "Unknown"
    
    def _extract_strike_price(self, title: str, ticker: str = None) -> Optional[float]:
        """Extract strike price from market title or ticker."""
        import re
        
        # First try to extract from ticker (more reliable)
        if ticker:
            # Pattern: KXBTCD-25SEP1417-T116999.99 -> 116999.99
            ticker_match = re.search(r'-T([0-9]+(?:\.[0-9]+)?)$', ticker)
            if ticker_match:
                try:
                    return float(ticker_match.group(1))
                except ValueError:
                    pass
        
        # Fallback to title patterns
        patterns = [
            r'\$([0-9,]+(?:\.\d+)?)k',  # $50k
            r'\$([0-9,]+(?:\.\d+)?)',   # $50,000
            r'([0-9,]+(?:\.\d+)?)k',    # 50k
            r'above\s+([0-9,]+(?:\.\d+)?)',  # above 50000
            r'below\s+([0-9,]+(?:\.\d+)?)',  # below 50000
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                try:
                    price_str = match.group(1).replace(',', '')
                    price = float(price_str)
                    
                    # If it's in thousands (k), multiply by 1000
                    if 'k' in pattern and 'k' in match.group(0).lower():
                        price *= 1000
                    
                    return price
                except ValueError:
                    continue
        
        return None
    
    async def get_btc_daily_markets(self) -> List[Dict]:
        """Get specifically BTC daily markets."""
        try:
            cache_key = "btc_daily_markets"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
                
            # Search for BTC daily markets
            btc_markets = await self._search_crypto_markets('bitcoin', 'btc')
            self._set_cache(cache_key, btc_markets)
            return btc_markets
            
        except Exception as e:
            logger.error(f"Error fetching BTC daily markets: {e}")
            return []
    
    async def get_eth_daily_markets(self) -> List[Dict]:
        """Get specifically ETH daily markets."""
        try:
            cache_key = "eth_daily_markets"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
                
            # Search for ETH daily markets
            eth_markets = await self._search_crypto_markets('ethereum', 'eth')
            self._set_cache(cache_key, eth_markets)
            return eth_markets
            
        except Exception as e:
            logger.error(f"Error fetching ETH daily markets: {e}")
            return []
    
    async def get_relevant_markets(self) -> Dict[str, List[Dict]]:
        """Get BTC and ETH daily markets from Kalshi."""
        try:
            btc_markets = await self.get_btc_daily_markets()
            eth_markets = await self.get_eth_daily_markets()
            
            # Process market data
            processed_btc = [self.get_market_price_info(m) for m in btc_markets]
            processed_eth = [self.get_market_price_info(m) for m in eth_markets]
            
            # If no real markets found, provide mock data for demonstration
            if not processed_btc and not processed_eth:
                logger.info("No crypto markets found on Kalshi, providing mock data for demonstration")
                processed_btc = self._get_mock_btc_markets()
                processed_eth = self._get_mock_eth_markets()
            
            return {
                'btc_daily': processed_btc,
                'eth_daily': processed_eth,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                'is_mock_data': len(processed_btc) > 0 and processed_btc[0].get('ticker', '').startswith('MOCK')
            }
        except Exception as e:
            logger.error(f"Error getting relevant markets: {e}")
            return {'btc_daily': [], 'eth_daily': [], 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
    
    async def get_markets_with_analysis(self, btc_price: float = None, eth_price: float = None, bankroll: float = 1000.0, bitcoin_analysis: Dict = None) -> Dict[str, List[Dict]]:
        """Get markets with betting analysis and recommendations."""
        try:
            # Get basic market data
            markets_data = await self.get_relevant_markets()
            
            # Set current prices for analysis
            if btc_price and eth_price:
                self.betting_analyzer.set_current_prices(btc_price, eth_price)
            
            # Set Bitcoin analysis for enhanced recommendations
            if bitcoin_analysis:
                self.betting_analyzer.set_bitcoin_analysis(bitcoin_analysis)
            
            # Add time-sensitive betting analysis to each market with bankroll
            for market in markets_data['btc_daily']:
                analysis = self.betting_analyzer.get_time_sensitive_analysis(market, bankroll)
                market['betting_analysis'] = analysis
            
            for market in markets_data['eth_daily']:
                analysis = self.betting_analyzer.get_time_sensitive_analysis(market, bankroll)
                market['betting_analysis'] = analysis
            
            # Get top opportunities
            all_markets = markets_data['btc_daily'] + markets_data['eth_daily']
            top_opportunities = self.betting_analyzer.get_top_opportunities(all_markets, limit=10, bankroll=bankroll)
            
            # Get market summary
            btc_summary = self.betting_analyzer.get_market_summary(markets_data['btc_daily'])
            eth_summary = self.betting_analyzer.get_market_summary(markets_data['eth_daily'])
            
            markets_data.update({
                'top_opportunities': top_opportunities,
                'btc_summary': btc_summary,
                'eth_summary': eth_summary,
                'analysis_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            })
            
            return markets_data
            
        except Exception as e:
            logger.error(f"Error getting markets with analysis: {e}")
            return await self.get_relevant_markets()
    
    def _get_mock_btc_markets(self) -> List[Dict]:
        """Generate mock BTC markets for demonstration."""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        
        mock_markets = [
            {
                'ticker': 'MOCK-BTC-45000-1H',
                'title': 'Bitcoin above $45,000 at end of next hour?',
                'status': 'open',
                'yes_bid': 0.45,
                'yes_ask': 0.52,
                'yes_mid': 0.485,
                'yes_price': 0.485,
                'volume': 1250,
                'open_interest': 8900,
                'close_time': (now + timedelta(hours=1)).isoformat(),
                'time_left': '45m',
                'strike_price': 45000.0,
                'last_trade_price': 0.48,
                'last_trade_yes_price': 0.48,
                'event_ticker': 'MOCK-BTC-EVENT',
                'series_ticker': 'MOCK-BTC-SERIES',
                'min_tick_size': 0.01,
                'can_close_early': True
            },
            {
                'ticker': 'MOCK-BTC-46000-1H',
                'title': 'Bitcoin above $46,000 at end of next hour?',
                'status': 'open',
                'yes_bid': 0.32,
                'yes_ask': 0.38,
                'yes_mid': 0.35,
                'yes_price': 0.35,
                'volume': 890,
                'open_interest': 5600,
                'close_time': (now + timedelta(hours=1)).isoformat(),
                'time_left': '45m',
                'strike_price': 46000.0,
                'last_trade_price': 0.34,
                'last_trade_yes_price': 0.34,
                'event_ticker': 'MOCK-BTC-EVENT',
                'series_ticker': 'MOCK-BTC-SERIES',
                'min_tick_size': 0.01,
                'can_close_early': True
            }
        ]
        
        return mock_markets
    
    def _get_mock_eth_markets(self) -> List[Dict]:
        """Generate mock ETH markets for demonstration."""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        
        mock_markets = [
            {
                'ticker': 'MOCK-ETH-3000-1H',
                'title': 'Ethereum above $3,000 at end of next hour?',
                'status': 'open',
                'yes_bid': 0.42,
                'yes_ask': 0.48,
                'yes_mid': 0.45,
                'yes_price': 0.45,
                'volume': 980,
                'open_interest': 7200,
                'close_time': (now + timedelta(hours=1)).isoformat(),
                'time_left': '45m',
                'strike_price': 3000.0,
                'last_trade_price': 0.44,
                'last_trade_yes_price': 0.44,
                'event_ticker': 'MOCK-ETH-EVENT',
                'series_ticker': 'MOCK-ETH-SERIES',
                'min_tick_size': 0.01,
                'can_close_early': True
            },
            {
                'ticker': 'MOCK-ETH-3100-1H',
                'title': 'Ethereum above $3,100 at end of next hour?',
                'status': 'open',
                'yes_bid': 0.28,
                'yes_ask': 0.34,
                'yes_mid': 0.31,
                'yes_price': 0.31,
                'volume': 650,
                'open_interest': 4200,
                'close_time': (now + timedelta(hours=1)).isoformat(),
                'time_left': '45m',
                'strike_price': 3100.0,
                'last_trade_price': 0.30,
                'last_trade_yes_price': 0.30,
                'event_ticker': 'MOCK-ETH-EVENT',
                'series_ticker': 'MOCK-ETH-SERIES',
                'min_tick_size': 0.01,
                'can_close_early': True
            }
        ]
        
        return mock_markets


# Synchronous wrapper for Flask app
class SyncKalshiIntegration:
    """Synchronous wrapper for the async Kalshi integration."""
    
    def __init__(self):
        self.integration = KalshiIntegration()
    
    def get_relevant_markets(self) -> Dict[str, List[Dict]]:
        """Get relevant markets synchronously."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._get_relevant_markets_async())
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error in get_relevant_markets: {e}")
            return {'btc_hourly': [], 'eth_hourly': [], 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
    
    async def _get_relevant_markets_async(self) -> Dict[str, List[Dict]]:
        async with self.integration as integration:
            return await integration.get_relevant_markets()
    
    def get_market_by_ticker(self, ticker: str) -> Optional[Dict]:
        """Get market by ticker synchronously."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._get_market_by_ticker_async(ticker))
        finally:
            loop.close()
    
    def get_markets_with_analysis(self, btc_price: float = None, eth_price: float = None, bankroll: float = 1000.0, bitcoin_analysis: Dict = None) -> Dict[str, List[Dict]]:
        """Get markets with betting analysis synchronously."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._get_markets_with_analysis_async(btc_price, eth_price, bankroll, bitcoin_analysis))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error in get_markets_with_analysis: {e}")
            return self.get_relevant_markets()
    
    async def _get_markets_with_analysis_async(self, btc_price: float = None, eth_price: float = None, bankroll: float = 1000.0, bitcoin_analysis: Dict = None) -> Dict[str, List[Dict]]:
        async with self.integration as integration:
            return await integration.get_markets_with_analysis(btc_price, eth_price, bankroll, bitcoin_analysis)
    
    async def _get_market_by_ticker_async(self, ticker: str) -> Optional[Dict]:
        async with self.integration as integration:
            return await integration.get_market_by_ticker(ticker)
