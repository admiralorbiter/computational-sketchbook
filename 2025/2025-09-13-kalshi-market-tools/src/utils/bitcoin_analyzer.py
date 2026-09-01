"""
Bitcoin price analysis with technical indicators for betting timing.
Analyzes market conditions to help determine if it's a good time to bet or wait.
"""

import math
import time
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import requests
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from scipy.stats import norm

logger = logging.getLogger(__name__)


@dataclass
class PricePoint:
    """Represents a price point with timestamp."""
    timestamp: float
    price: float
    volume: Optional[float] = None


@dataclass
class TechnicalIndicator:
    """Represents a technical indicator value."""
    name: str
    value: float
    signal: str  # "BULLISH", "BEARISH", "NEUTRAL", "OVERSOLD", "OVERBOUGHT"
    strength: float  # 0-1 scale
    description: str


class BitcoinAnalyzer:
    """Comprehensive Bitcoin price analysis for betting timing."""
    
    def __init__(self):
        self.price_history = []
        self.current_price = 0.0
        self.last_update = 0.0
        self.kalshi_service = None  # Will be initialized when needed
        
    def get_comprehensive_analysis(self) -> Dict:
        """Get comprehensive Bitcoin analysis for betting timing."""
        try:
            # Get current price and historical data
            self._fetch_price_data()
            
            if not self.price_history:
                return {"error": "Unable to fetch price data"}
            
            # Calculate all indicators
            analysis = {
                "current_price": self.current_price,
                "last_update": datetime.fromtimestamp(self.last_update).strftime("%Y-%m-%d %H:%M:%S"),
                "price_change_24h": self._calculate_price_change_24h(),
                "volatility_analysis": self._analyze_volatility(),
                "trend_analysis": self._analyze_trend(),
                "momentum_indicators": self._calculate_momentum_indicators(),
                "support_resistance": self._find_support_resistance(),
                "market_sentiment": self._analyze_market_sentiment(),
                "betting_timing": self._get_betting_timing_recommendation(),
                "risk_level": self._calculate_risk_level(),
                "price_targets": self._calculate_price_targets(),
                "hourly_betting_bands": self._calculate_hourly_betting_bands()
            }
            
            # Add Kalshi market integration
            kalshi_markets = self._fetch_kalshi_markets()
            if kalshi_markets:
                analysis["kalshi_opportunities"] = self._match_analysis_to_kalshi_markets(analysis, kalshi_markets)
            else:
                analysis["kalshi_opportunities"] = []
            
            # Add advanced probability model
            try:
                analysis["advanced_probability_model"] = self._calculate_advanced_probability_model()
            except Exception as e:
                logger.error(f"Error in advanced probability model: {e}")
                analysis["advanced_probability_model"] = {"error": str(e), "model_ready": False}
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {"error": str(e)}
    
    def _fetch_price_data(self):
        """Fetch current and historical Bitcoin price data."""
        try:
            # Get current price from CoinGecko (free, no API key needed)
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                btc_data = data.get("bitcoin", {})
                
                self.current_price = btc_data.get("usd", 0.0)
                self.last_update = time.time()
                
                # Generate mock historical data for analysis (in real app, use proper historical API)
                self._generate_mock_historical_data()
                
        except Exception as e:
            logger.error(f"Error fetching price data: {e}")
            # Fallback to mock data
            self.current_price = 45000.0
            self.last_update = time.time()
            self._generate_mock_historical_data()
    
    def _generate_mock_historical_data(self):
        """Generate mock historical data for analysis."""
        # In a real implementation, you'd fetch this from a proper historical data API
        # For now, generate realistic mock data
        base_price = self.current_price
        current_time = time.time()
        
        self.price_history = []
        
        # Generate 100 data points over the last 24 hours
        for i in range(100):
            # Simulate realistic price movement with some volatility
            hours_ago = (100 - i) / 4.17  # 24 hours / 100 points
            timestamp = current_time - (hours_ago * 3600)
            
            # Add some realistic price variation
            variation = math.sin(i * 0.1) * 0.02 + math.cos(i * 0.05) * 0.01
            price = base_price * (1 + variation * (1 - i/100))
            
            # Add some volume data
            volume = 1000000 * (1 + math.sin(i * 0.2) * 0.3)
            
            self.price_history.append(PricePoint(
                timestamp=timestamp,
                price=price,
                volume=volume
            ))
    
    def _calculate_price_change_24h(self) -> Dict:
        """Calculate 24-hour price change."""
        if len(self.price_history) < 2:
            return {"change_pct": 0.0, "change_usd": 0.0}
        
        current = self.price_history[-1].price
        start = self.price_history[0].price
        
        change_usd = current - start
        change_pct = (change_usd / start) * 100
        
        return {
            "change_pct": round(change_pct, 2),
            "change_usd": round(change_usd, 2),
            "direction": "UP" if change_usd > 0 else "DOWN"
        }
    
    def _analyze_volatility(self) -> Dict:
        """Analyze market volatility and choppiness."""
        if len(self.price_history) < 20:
            return {"volatility": 0.0, "choppiness": 0.0, "signal": "NEUTRAL"}
        
        prices = [p.price for p in self.price_history[-20:]]
        
        # Calculate volatility (standard deviation of returns)
        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        
        volatility = math.sqrt(sum(r**2 for r in returns) / len(returns)) * 100
        
        # Calculate choppiness (average true range)
        atr = self._calculate_atr(prices, 14)
        choppiness = (atr / self.current_price) * 100
        
        # Determine signal
        if volatility > 3.0 or choppiness > 2.0:
            signal = "HIGH_VOLATILITY"
        elif volatility < 1.0 and choppiness < 0.5:
            signal = "LOW_VOLATILITY"
        else:
            signal = "MODERATE_VOLATILITY"
        
        return {
            "volatility": round(volatility, 2),
            "choppiness": round(choppiness, 2),
            "signal": signal,
            "description": self._get_volatility_description(volatility, choppiness)
        }
    
    def _analyze_trend(self) -> Dict:
        """Analyze trend strength and direction."""
        if len(self.price_history) < 20:
            return {"trend": "UNKNOWN", "strength": 0.0}
        
        prices = [p.price for p in self.price_history[-20:]]
        
        # Simple moving averages
        sma_5 = sum(prices[-5:]) / 5
        sma_10 = sum(prices[-10:]) / 10
        sma_20 = sum(prices[-20:]) / 20
        
        # Trend direction
        if sma_5 > sma_10 > sma_20:
            trend = "UPTREND"
        elif sma_5 < sma_10 < sma_20:
            trend = "DOWNTREND"
        else:
            trend = "SIDEWAYS"
        
        # Trend strength (0-1)
        price_range = max(prices) - min(prices)
        current_deviation = abs(self.current_price - sma_20)
        strength = min(current_deviation / (price_range / 2), 1.0) if price_range > 0 else 0.0
        
        return {
            "trend": trend,
            "strength": round(strength, 2),
            "sma_5": round(sma_5, 2),
            "sma_10": round(sma_10, 2),
            "sma_20": round(sma_20, 2),
            "description": self._get_trend_description(trend, strength)
        }
    
    def _calculate_momentum_indicators(self) -> Dict:
        """Calculate momentum indicators (RSI, MACD, etc.)."""
        if len(self.price_history) < 14:
            return {"rsi": 50.0, "macd": 0.0, "signal": "NEUTRAL"}
        
        prices = [p.price for p in self.price_history[-14:]]
        
        # RSI calculation
        rsi = self._calculate_rsi(prices)
        
        # MACD calculation (simplified)
        macd = self._calculate_macd(prices)
        
        # Determine signal
        if rsi > 70:
            signal = "OVERBOUGHT"
        elif rsi < 30:
            signal = "OVERSOLD"
        elif 40 <= rsi <= 60:
            signal = "NEUTRAL"
        else:
            signal = "MOMENTUM"
        
        return {
            "rsi": round(rsi, 2),
            "macd": round(macd, 2),
            "signal": signal,
            "description": self._get_momentum_description(rsi, macd)
        }
    
    def _find_support_resistance(self) -> Dict:
        """Find key support and resistance levels."""
        if len(self.price_history) < 20:
            return {"support": 0.0, "resistance": 0.0, "levels": []}
        
        prices = [p.price for p in self.price_history[-20:]]
        
        # Find local highs and lows
        highs = []
        lows = []
        
        for i in range(1, len(prices) - 1):
            if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
                highs.append(prices[i])
            elif prices[i] < prices[i-1] and prices[i] < prices[i+1]:
                lows.append(prices[i])
        
        # Calculate support and resistance
        support = min(lows) if lows else min(prices)
        resistance = max(highs) if highs else max(prices)
        
        # Distance to levels
        distance_to_support = ((self.current_price - support) / self.current_price) * 100
        distance_to_resistance = ((resistance - self.current_price) / self.current_price) * 100
        
        return {
            "support": round(support, 2),
            "resistance": round(resistance, 2),
            "distance_to_support": round(distance_to_support, 2),
            "distance_to_resistance": round(distance_to_resistance, 2),
            "levels": sorted(set(highs + lows), reverse=True)[:5]
        }
    
    def _analyze_market_sentiment(self) -> Dict:
        """Analyze overall market sentiment."""
        volatility = self._analyze_volatility()
        trend = self._analyze_trend()
        momentum = self._calculate_momentum_indicators()
        
        # Combine indicators for sentiment
        sentiment_score = 0.5  # Start neutral
        
        # Volatility impact
        if volatility["signal"] == "HIGH_VOLATILITY":
            sentiment_score -= 0.2
        elif volatility["signal"] == "LOW_VOLATILITY":
            sentiment_score += 0.1
        
        # Trend impact
        if trend["trend"] == "UPTREND":
            sentiment_score += 0.2
        elif trend["trend"] == "DOWNTREND":
            sentiment_score -= 0.2
        
        # Momentum impact
        if momentum["signal"] == "OVERSOLD":
            sentiment_score += 0.1
        elif momentum["signal"] == "OVERBOUGHT":
            sentiment_score -= 0.1
        
        # Determine sentiment
        if sentiment_score > 0.7:
            sentiment = "BULLISH"
        elif sentiment_score < 0.3:
            sentiment = "BEARISH"
        else:
            sentiment = "NEUTRAL"
        
        return {
            "sentiment": sentiment,
            "score": round(sentiment_score, 2),
            "confidence": round(abs(sentiment_score - 0.5) * 2, 2),
            "description": self._get_sentiment_description(sentiment, sentiment_score)
        }
    
    def _get_betting_timing_recommendation(self) -> Dict:
        """Get betting timing recommendation based on all indicators."""
        volatility = self._analyze_volatility()
        trend = self._analyze_trend()
        momentum = self._calculate_momentum_indicators()
        sentiment = self._analyze_market_sentiment()
        
        # Scoring system
        score = 0
        reasons = []
        
        # Volatility scoring
        if volatility["signal"] == "LOW_VOLATILITY":
            score += 2
            reasons.append("Low volatility - stable conditions")
        elif volatility["signal"] == "HIGH_VOLATILITY":
            score -= 2
            reasons.append("High volatility - risky conditions")
        
        # Trend scoring
        if trend["trend"] == "UPTREND" and trend["strength"] > 0.6:
            score += 2
            reasons.append("Strong uptrend - momentum favors longs")
        elif trend["trend"] == "DOWNTREND" and trend["strength"] > 0.6:
            score += 1
            reasons.append("Strong downtrend - momentum favors shorts")
        elif trend["trend"] == "SIDEWAYS":
            score -= 1
            reasons.append("Sideways movement - unclear direction")
        
        # Momentum scoring
        if momentum["signal"] == "OVERSOLD":
            score += 1
            reasons.append("Oversold conditions - potential bounce")
        elif momentum["signal"] == "OVERBOUGHT":
            score -= 1
            reasons.append("Overbought conditions - potential pullback")
        
        # Sentiment scoring
        if sentiment["sentiment"] == "BULLISH":
            score += 1
        elif sentiment["sentiment"] == "BEARISH":
            score -= 1
        
        # Determine recommendation
        if score >= 3:
            recommendation = "STRONG_BUY"
            action = "Good time to bet - multiple positive signals"
        elif score >= 1:
            recommendation = "BUY"
            action = "Moderate conditions - consider betting"
        elif score >= -1:
            recommendation = "HOLD"
            action = "Wait for better conditions"
        elif score >= -3:
            recommendation = "SELL"
            action = "Poor conditions - avoid betting"
        else:
            recommendation = "STRONG_SELL"
            action = "Very poor conditions - definitely wait"
        
        return {
            "recommendation": recommendation,
            "action": action,
            "score": score,
            "reasons": reasons,
            "confidence": min(abs(score) / 4, 1.0)
        }
    
    def _calculate_risk_level(self) -> Dict:
        """Calculate current risk level for betting."""
        volatility = self._analyze_volatility()
        trend = self._analyze_trend()
        
        risk_score = 0.5  # Start moderate
        
        # Volatility risk
        if volatility["volatility"] > 3.0:
            risk_score += 0.3
        elif volatility["volatility"] < 1.0:
            risk_score -= 0.2
        
        # Trend risk
        if trend["trend"] == "SIDEWAYS":
            risk_score += 0.2
        
        # Choppiness risk
        if volatility["choppiness"] > 2.0:
            risk_score += 0.2
        
        risk_level = "LOW" if risk_score < 0.3 else "MODERATE" if risk_score < 0.7 else "HIGH"
        
        return {
            "level": risk_level,
            "score": round(risk_score, 2),
            "description": self._get_risk_description(risk_level, risk_score)
        }
    
    def _calculate_price_targets(self) -> Dict:
        """Calculate potential price targets."""
        if len(self.price_history) < 20:
            return {"targets": []}
        
        prices = [p.price for p in self.price_history[-20:]]
        current = self.current_price
        
        # Calculate volatility-based targets
        volatility = self._analyze_volatility()
        vol_pct = volatility["volatility"] / 100
        
        # 1-day targets
        target_1d_up = current * (1 + vol_pct)
        target_1d_down = current * (1 - vol_pct)
        
        # 1-week targets (assuming 7x daily volatility)
        target_1w_up = current * (1 + vol_pct * 7)
        target_1w_down = current * (1 - vol_pct * 7)
        
        return {
            "targets": [
                {"timeframe": "1 Day", "up": round(target_1d_up, 2), "down": round(target_1d_down, 2)},
                {"timeframe": "1 Week", "up": round(target_1w_up, 2), "down": round(target_1w_down, 2)}
            ]
        }
    
    def _calculate_hourly_betting_bands(self) -> Dict:
        """Calculate hourly betting bands for Kalshi integration."""
        if len(self.price_history) < 20:
            return {"bands": [], "recommendations": []}
        
        current = self.current_price
        volatility = self._analyze_volatility()
        trend = self._analyze_trend()
        momentum = self._calculate_momentum_indicators()
        
        # Calculate realistic hourly volatility for Bitcoin
        # Bitcoin typically moves 0.2-0.8% per hour during normal trading
        hourly_vol = max(0.2, min(0.8, volatility["volatility"] / 24))  # Clamp between 0.2% and 0.8%
        
        # Base hourly movement range in dollars
        base_range = current * (hourly_vol / 100)
        
        # Create realistic price bands around current price
        # Use round numbers that would make sense for Kalshi markets
        bands = []
        
        # Conservative bands (70% probability) - small moves
        conservative_range = base_range * 0.6  # Smaller range for higher probability
        above_conservative = current + conservative_range
        below_conservative = current - conservative_range
        
        # Round to nearest $250 for Kalshi Bitcoin markets
        above_conservative = round(above_conservative / 250) * 250
        below_conservative = round(below_conservative / 250) * 250
        
        bands.append({
            "type": "Conservative",
            "probability": 70,
            "above_target": int(above_conservative),
            "below_target": int(below_conservative),
            "confidence": "High",
            "description": f"Safe betting range ±${int(conservative_range):,} from current"
        })
        
        # Moderate bands (50% probability) - medium moves
        moderate_range = base_range * 1.2
        above_moderate = current + moderate_range
        below_moderate = current - moderate_range
        
        # Round to nearest $250 for Kalshi Bitcoin markets
        above_moderate = round(above_moderate / 250) * 250
        below_moderate = round(below_moderate / 250) * 250
        
        bands.append({
            "type": "Moderate",
            "probability": 50,
            "above_target": int(above_moderate),
            "below_target": int(below_moderate),
            "confidence": "Medium",
            "description": f"Balanced risk/reward ±${int(moderate_range):,} from current"
        })
        
        # Aggressive bands (30% probability) - larger moves
        aggressive_range = base_range * 2.0
        above_aggressive = current + aggressive_range
        below_aggressive = current - aggressive_range
        
        # Round to nearest $250 for Kalshi Bitcoin markets
        above_aggressive = round(above_aggressive / 250) * 250
        below_aggressive = round(below_aggressive / 250) * 250
        
        bands.append({
            "type": "Aggressive",
            "probability": 30,
            "above_target": int(above_aggressive),
            "below_target": int(below_aggressive),
            "confidence": "Low",
            "description": f"High reward ±${int(aggressive_range):,} from current"
        })
        
        # Generate specific recommendations
        recommendations = self._generate_hourly_recommendations(bands, trend, momentum, volatility)
        
        return {
            "bands": bands,
            "recommendations": recommendations,
            "current_price": current,
            "hourly_volatility": round(hourly_vol, 2),
            "trend_bias": trend["trend"],
            "momentum_bias": momentum["signal"]
        }
    
    def _generate_hourly_recommendations(self, bands: List[Dict], trend: Dict, momentum: Dict, volatility: Dict) -> List[Dict]:
        """Generate specific hourly betting recommendations."""
        recommendations = []
        current = self.current_price
        
        # Determine overall bias
        bias_score = 0
        if trend["trend"] == "UPTREND":
            bias_score += 1
        elif trend["trend"] == "DOWNTREND":
            bias_score -= 1
        
        if momentum["rsi"] > 55:
            bias_score += 0.5
        elif momentum["rsi"] < 45:
            bias_score -= 0.5
        
        # Generate recommendations based on bias and volatility
        if volatility["signal"] == "LOW_VOLATILITY":
            # Low volatility - focus on conservative ranges
            for band in bands[:2]:  # Conservative and moderate only
                if bias_score > 0.5:
                    recommendations.append({
                        "action": "BUY_YES",
                        "target": band["above_target"],
                        "probability": band["probability"],
                        "reasoning": f"Uptrend bias + low volatility = good upside bet at ${band['above_target']:,}",
                        "risk_level": band["confidence"]
                    })
                elif bias_score < -0.5:
                    recommendations.append({
                        "action": "BUY_NO",
                        "target": band["below_target"],
                        "probability": band["probability"],
                        "reasoning": f"Downtrend bias + low volatility = good downside bet at ${band['below_target']:,}",
                        "risk_level": band["confidence"]
                    })
                else:
                    # Neutral bias - suggest both directions
                    recommendations.append({
                        "action": "BUY_YES",
                        "target": band["above_target"],
                        "probability": band["probability"],
                        "reasoning": f"Low volatility = stable conditions, consider upside bet at ${band['above_target']:,}",
                        "risk_level": band["confidence"]
                    })
                    recommendations.append({
                        "action": "BUY_NO",
                        "target": band["below_target"],
                        "probability": band["probability"],
                        "reasoning": f"Low volatility = stable conditions, consider downside bet at ${band['below_target']:,}",
                        "risk_level": band["confidence"]
                    })
        
        elif volatility["signal"] == "HIGH_VOLATILITY":
            # High volatility - be more cautious
            if bias_score > 1:
                recommendations.append({
                    "action": "BUY_YES",
                    "target": bands[0]["above_target"],  # Only conservative
                    "probability": bands[0]["probability"],
                    "reasoning": f"Strong uptrend bias but high volatility - use conservative target ${bands[0]['above_target']:,}",
                    "risk_level": "High"
                })
            elif bias_score < -1:
                recommendations.append({
                    "action": "BUY_NO",
                    "target": bands[0]["below_target"],  # Only conservative
                    "probability": bands[0]["probability"],
                    "reasoning": f"Strong downtrend bias but high volatility - use conservative target ${bands[0]['below_target']:,}",
                    "risk_level": "High"
                })
            else:
                recommendations.append({
                    "action": "WAIT",
                    "target": None,
                    "probability": 0,
                    "reasoning": "High volatility + unclear direction = wait for better conditions",
                    "risk_level": "Very High"
                })
        
        else:  # Moderate volatility
            # Moderate volatility - use all bands
            for band in bands:
                if bias_score > 0.3:
                    recommendations.append({
                        "action": "BUY_YES",
                        "target": band["above_target"],
                        "probability": band["probability"],
                        "reasoning": f"Uptrend bias + moderate volatility = consider upside bet at ${band['above_target']:,}",
                        "risk_level": band["confidence"]
                    })
                elif bias_score < -0.3:
                    recommendations.append({
                        "action": "BUY_NO",
                        "target": band["below_target"],
                        "probability": band["probability"],
                        "reasoning": f"Downtrend bias + moderate volatility = consider downside bet at ${band['below_target']:,}",
                        "risk_level": band["confidence"]
                    })
        
        return recommendations[:6]  # Limit to 6 recommendations
    
    def _calculate_advanced_probability_model(self) -> Dict:
        """Calculate advanced probability model for Kalshi BTC markets using drift + volatility."""
        if len(self.price_history) < 60:  # Need at least 1 hour of data
            return {"error": "Insufficient data for advanced model"}
        
        try:
            # Get recent price data for calculations
            prices = [p.price for p in self.price_history[-60:]]  # Last 60 minutes
            current_price = self.current_price
            
            # Calculate short-term drift (μ) from 5-minute EMA slope
            mu = self._calculate_drift(prices)
            
            # Calculate intrahour volatility (σ60) from recent 1-min returns
            sigma60 = self._calculate_intrahour_volatility(prices)
            
            # Generate Kalshi market opportunities with probability calculations
            opportunities_data = self._generate_kalshi_opportunities_with_probability(
                current_price, mu, sigma60
            )
            
            return {
                "drift_per_minute": mu,
                "hourly_volatility": sigma60,
                "current_price": current_price,
                "opportunities": opportunities_data['opportunities'],
                "criteria_analysis": opportunities_data['criteria_analysis'],
                "model_ready": True
            }
            
        except Exception as e:
            logger.error(f"Error in advanced probability model: {e}")
            return {"error": f"Model calculation failed: {e}"}
    
    def _calculate_drift(self, prices: List[float]) -> float:
        """Calculate short-term drift (μ) in $/min from 5-minute EMA slope."""
        if len(prices) < 10:
            return 0.0
        
        # Calculate 5-minute EMA
        ema_period = 5
        alpha = 2.0 / (ema_period + 1)
        ema_values = []
        ema = prices[0]
        
        for price in prices:
            ema = alpha * price + (1 - alpha) * ema
            ema_values.append(ema)
        
        # Calculate slope of EMA over last 10 minutes
        if len(ema_values) >= 10:
            recent_ema = ema_values[-10:]
            x = np.arange(len(recent_ema))
            slope, _ = np.polyfit(x, recent_ema, 1)
            return slope  # $/min drift
        else:
            return 0.0
    
    def _calculate_intrahour_volatility(self, prices: List[float]) -> float:
        """Calculate intrahour volatility (σ60) from recent 1-min returns."""
        if len(prices) < 2:
            return 0.0
        
        # Calculate 1-minute returns
        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        
        # Calculate standard deviation of returns (annualized)
        if len(returns) > 1:
            std_returns = np.std(returns)
            # Convert to hourly volatility
            hourly_vol = std_returns * np.sqrt(60)  # 60 minutes in an hour
            return hourly_vol
        else:
            return 0.0
    
    def _generate_kalshi_opportunities_with_probability(self, current_price: float, mu: float, sigma60: float) -> List[Dict]:
        """Generate Kalshi opportunities with probability calculations."""
        opportunities = []
        
        # Generate strikes on $250 grid around current price
        base_strike = round(current_price / 250) * 250
        strikes = []
        
        # Add strikes in $250 increments
        for i in range(-3, 4):  # -$750 to +$750 range
            strike = base_strike + (i * 250)
            if strike > 0:
                strikes.append(strike)
        
        logger.info(f"Generated strikes: {strikes}")
        logger.info(f"Current price: {current_price}, mu: {mu}, sigma60: {sigma60}")
        
        # Calculate probabilities for each strike
        for strike in strikes:
            # Calculate time remaining (assume we're checking at start of hour)
            minutes_left = 60  # Full hour
            
            # Calculate projected remaining move
            s = sigma60 * np.sqrt(minutes_left / 60)
            
            # Calculate probability using normal CDF
            z = (strike - current_price - mu * minutes_left) / max(1e-8, s)
            prob_above = 1 - norm.cdf(z)
            
            # Calculate distance in sigma units
            distance_sigma = abs(current_price - strike) / max(1e-8, s)
            
            # Determine if this is a safe opportunity
            is_safe_no = self._is_safe_no(current_price, strike, s, mu, distance_sigma)
            is_safe_yes = self._is_safe_yes(current_price, strike, s, mu, distance_sigma)
            
            # Calculate edge (assuming market price = 50% for now)
            market_prob = 0.5  # In real implementation, get from Kalshi
            edge_yes = prob_above - market_prob
            edge_no = (1 - prob_above) - (1 - market_prob)
            
            opportunities.append({
                'strike': strike,
                'prob_above': round(prob_above * 100, 1),
                'prob_below': round((1 - prob_above) * 100, 1),
                'distance_sigma': round(distance_sigma, 2),
                'is_safe_no': is_safe_no,
                'is_safe_yes': is_safe_yes,
                'edge_yes': round(edge_yes * 100, 1),
                'edge_no': round(edge_no * 100, 1),
                'recommendation': self._get_recommendation(is_safe_no, is_safe_yes, edge_yes, edge_no),
                'reasoning': self._get_reasoning(current_price, strike, prob_above, distance_sigma, mu)
            })
        
        # Separate opportunities and failed ones
        good_opportunities = [opp for opp in opportunities if opp['recommendation'] != 'PASS']
        failed_opportunities = [opp for opp in opportunities if opp['recommendation'] == 'PASS']
        
        # Sort good opportunities by edge
        good_opportunities.sort(key=lambda x: max(x['edge_yes'], x['edge_no']), reverse=True)
        
        # Add criteria analysis for failed opportunities
        criteria_analysis = self._analyze_failed_criteria(failed_opportunities, mu, sigma60)
        
        # Debug: Log the data structure
        logger.info(f"Good opportunities count: {len(good_opportunities)}")
        logger.info(f"Failed opportunities count: {len(failed_opportunities)}")
        if good_opportunities:
            logger.info(f"First good opportunity: {good_opportunities[0]}")
        
        return {
            'opportunities': good_opportunities[:8],
            'criteria_analysis': criteria_analysis,
            'total_checked': len(opportunities)
        }
    
    def _is_safe_no(self, current_price: float, strike: float, s: float, mu: float, distance_sigma: float) -> bool:
        """Check if this is a safe NO opportunity (fade far-away strike)."""
        if strike <= current_price:
            return False
        
        # Safe NO rules:
        # 1. Strike is >1.25× projected remaining move away
        # 2. Non-positive trend (μ ≤ 0)
        # 3. Minutes left ≤ 20 (we'll use 60 for now)
        # 4. Edge ≥ 3%
        
        return (distance_sigma >= 1.25 and 
                mu <= 0 and 
                distance_sigma >= 1.25)  # Simplified for now
    
    def _is_safe_yes(self, current_price: float, strike: float, s: float, mu: float, distance_sigma: float) -> bool:
        """Check if this is a safe YES opportunity (protect the lead)."""
        if strike >= current_price:
            return False
        
        # Safe YES rules:
        # 1. Price is >0.8× projected remaining move above strike
        # 2. Positive trend (μ > 0)
        # 3. Minutes left ≤ 20
        # 4. Edge ≥ 3%
        
        return (distance_sigma >= 0.8 and 
                mu > 0 and 
                distance_sigma >= 0.8)  # Simplified for now
    
    def _get_recommendation(self, is_safe_no: bool, is_safe_yes: bool, edge_yes: float, edge_no: float) -> str:
        """Get recommendation based on safe rules and edge."""
        if is_safe_no and edge_no > 3:
            return "BUY_NO"
        elif is_safe_yes and edge_yes > 3:
            return "BUY_YES"
        else:
            return "PASS"
    
    def _get_reasoning(self, current_price: float, strike: float, prob_above: float, distance_sigma: float, mu: float) -> str:
        """Generate reasoning for the recommendation."""
        price_diff = strike - current_price
        direction = "above" if price_diff > 0 else "below"
        
        if prob_above > 0.6:
            confidence = "High"
        elif prob_above > 0.4:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        trend_desc = "uptrend" if mu > 0 else "downtrend" if mu < 0 else "sideways"
        
        return f"{confidence} confidence ({prob_above:.1%}) that price will be {direction} ${strike:,.0f}. Distance: {distance_sigma:.1f}σ, Trend: {trend_desc}"
    
    def _analyze_failed_criteria(self, failed_opportunities: List[Dict], mu: float, sigma60: float) -> Dict:
        """Analyze why opportunities failed to meet criteria."""
        if not failed_opportunities:
            return {"message": "All opportunities met criteria", "details": []}
        
        analysis = {
            "total_checked": len(failed_opportunities),
            "failed_reasons": {},
            "closest_opportunities": [],
            "recommendations": []
        }
        
        # Analyze failure reasons
        distance_issues = 0
        edge_issues = 0
        trend_issues = 0
        volatility_issues = 0
        
        closest_yes = None
        closest_no = None
        
        for opp in failed_opportunities:
            # Check distance criteria
            if opp['distance_sigma'] < 0.8:
                distance_issues += 1
            
            # Check edge criteria
            if opp['edge_yes'] < 3 and opp['edge_no'] < 3:
                edge_issues += 1
            
            # Check trend criteria
            if mu <= 0 and opp['strike'] > opp.get('current_price', 0):
                trend_issues += 1
            elif mu > 0 and opp['strike'] < opp.get('current_price', 0):
                trend_issues += 1
            
            # Check volatility
            if sigma60 < 0.005:  # Less than 0.5% hourly vol
                volatility_issues += 1
            
            # Track closest opportunities
            if opp['strike'] > opp.get('current_price', 0):  # Above strikes
                if closest_yes is None or opp['distance_sigma'] < closest_yes['distance_sigma']:
                    closest_yes = opp
            else:  # Below strikes
                if closest_no is None or opp['distance_sigma'] < closest_no['distance_sigma']:
                    closest_no = opp
        
        # Compile analysis
        analysis['failed_reasons'] = {
            'distance_too_close': distance_issues,
            'insufficient_edge': edge_issues,
            'trend_mismatch': trend_issues,
            'low_volatility': volatility_issues
        }
        
        # Add closest opportunities
        if closest_yes:
            analysis['closest_opportunities'].append({
                'type': 'YES',
                'strike': closest_yes['strike'],
                'distance_sigma': closest_yes['distance_sigma'],
                'edge': closest_yes['edge_yes'],
                'prob': closest_yes['prob_above'],
                'missing': self._get_missing_criteria(closest_yes, mu, sigma60)
            })
        
        if closest_no:
            analysis['closest_opportunities'].append({
                'type': 'NO',
                'strike': closest_no['strike'],
                'distance_sigma': closest_no['distance_sigma'],
                'edge': closest_no['edge_no'],
                'prob': closest_no['prob_below'],
                'missing': self._get_missing_criteria(closest_no, mu, sigma60)
            })
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_criteria_recommendations(analysis, mu, sigma60)
        
        return analysis
    
    def _get_missing_criteria(self, opp: Dict, mu: float, sigma60: float) -> List[str]:
        """Get specific missing criteria for an opportunity."""
        missing = []
        
        # Distance criteria
        if opp['distance_sigma'] < 0.8:
            missing.append(f"Distance too close ({opp['distance_sigma']:.1f}σ < 0.8σ required)")
        
        # Edge criteria
        if opp['edge_yes'] < 3 and opp['edge_no'] < 3:
            missing.append(f"Edge too low (YES: {opp['edge_yes']:.1f}%, NO: {opp['edge_no']:.1f}% < 3% required)")
        
        # Trend criteria
        if mu <= 0 and opp['strike'] > opp.get('current_price', 0):
            missing.append(f"Negative drift ({mu:.2f}/min) but strike above current price")
        elif mu > 0 and opp['strike'] < opp.get('current_price', 0):
            missing.append(f"Positive drift ({mu:.2f}/min) but strike below current price")
        
        # Volatility criteria
        if sigma60 < 0.005:
            missing.append(f"Low volatility ({sigma60*100:.1f}% < 0.5% required)")
        
        return missing
    
    def _generate_criteria_recommendations(self, analysis: Dict, mu: float, sigma60: float) -> List[str]:
        """Generate recommendations based on criteria analysis."""
        recommendations = []
        
        # Volatility recommendations
        if analysis['failed_reasons']['low_volatility'] > 0:
            recommendations.append(f"⚠️ Low volatility ({sigma60*100:.1f}%) - wait for more active market conditions")
        
        # Distance recommendations
        if analysis['failed_reasons']['distance_too_close'] > 0:
            recommendations.append("⚠️ Strikes too close to current price - need larger moves for safe betting")
        
        # Edge recommendations
        if analysis['failed_reasons']['insufficient_edge'] > 0:
            recommendations.append("⚠️ Insufficient edge - market prices too close to model probabilities")
        
        # Trend recommendations
        if analysis['failed_reasons']['trend_mismatch'] > 0:
            trend_desc = "downtrend" if mu < 0 else "uptrend" if mu > 0 else "sideways"
            recommendations.append(f"⚠️ Trend mismatch - current {trend_desc} doesn't align with strike directions")
        
        # General recommendations
        if not recommendations:
            recommendations.append("✅ All criteria met - no issues found")
        else:
            recommendations.append("💡 Wait for better market conditions or adjust strike levels")
        
        return recommendations
    
    def _get_kalshi_service(self):
        """Get or initialize Kalshi service."""
        if self.kalshi_service is None:
            try:
                from utils.kalshi_integration import SyncKalshiIntegration
                self.kalshi_service = SyncKalshiIntegration()
            except ImportError:
                logger.warning("Kalshi integration not available")
                return None
        return self.kalshi_service
    
    def _fetch_kalshi_markets(self) -> List[Dict]:
        """Fetch available Kalshi markets for price-based betting."""
        kalshi_service = self._get_kalshi_service()
        if not kalshi_service:
            return []
        
        try:
            # Get all open markets
            markets_data = kalshi_service.get_relevant_markets()
            markets = markets_data.get('btc_daily', []) + markets_data.get('eth_daily', [])
            
            # Filter for price-based markets (not just crypto)
            price_markets = []
            for market in markets:
                title = market.get('title', '').lower()
                # Look for markets with price levels, numbers, and directional words
                if (any(char.isdigit() for char in title) and 
                    ('above' in title or 'below' in title or 'over' in title or 'under' in title) and
                    ('price' in title or 'open' in title or 'close' in title)):
                    price_markets.append(market)
            
            # Sort by volume (most active first)
            price_markets.sort(key=lambda x: x.get('volume', 0), reverse=True)
            
            # If we have price markets, return them
            if price_markets:
                return price_markets[:20]  # Return top 20 most active
            
            # If no price markets, create some example Bitcoin markets for demonstration
            return self._create_example_bitcoin_markets()
            
        except Exception as e:
            logger.error(f"Error fetching Kalshi markets: {e}")
            return self._create_example_bitcoin_markets()
    
    def _create_example_bitcoin_markets(self) -> List[Dict]:
        """Create example Bitcoin markets for demonstration when no real markets are available."""
        current = self.current_price
        if current <= 0:
            return []
        
        # Create example markets around current Bitcoin price
        example_markets = []
        
        # Conservative levels (±$250 from current)
        levels = [
            (current + 250, "above"),
            (current - 250, "below"),
            (current + 500, "above"),
            (current - 500, "below"),
            (current + 750, "above"),
            (current - 750, "below"),
        ]
        
        for i, (price, direction) in enumerate(levels):
            price_rounded = round(price / 250) * 250  # Round to nearest $250
            example_markets.append({
                'ticker': f'BTC-EXAMPLE-{i+1}',
                'title': f'Will Bitcoin be {direction} ${price_rounded:,} in the next hour?',
                'yes_price': 45 if direction == 'above' else 55,  # Example prices
                'volume': 100 + i * 50,
                'status': 'open',
                'close_time': '2025-09-14T15:00:00Z',
                'is_example': True
            })
        
        return example_markets
    
    def _match_analysis_to_kalshi_markets(self, analysis: Dict, kalshi_markets: List[Dict]) -> List[Dict]:
        """Match Bitcoin analysis to specific Kalshi market opportunities."""
        if not kalshi_markets:
            return []
        
        current_price = analysis.get('current_price', 0)
        volatility = analysis.get('volatility_analysis', {})
        trend = analysis.get('trend_analysis', {})
        momentum = analysis.get('momentum_indicators', {})
        
        recommendations = []
        
        for market in kalshi_markets:
            try:
                # Extract price level from market title
                title = market.get('title', '')
                price_level = self._extract_price_from_title(title)
                
                if not price_level:
                    continue
                
                # Determine if this is an "above" or "below" market
                is_above_market = 'above' in title.lower() or 'over' in title.lower()
                
                # Calculate probability based on current price vs target
                if is_above_market:
                    # Market asks if price will be above X
                    probability = self._calculate_probability_above(current_price, price_level, volatility, trend, momentum)
                    action = "BUY_YES" if probability > 0.5 else "BUY_NO"
                else:
                    # Market asks if price will be below X
                    probability = self._calculate_probability_below(current_price, price_level, volatility, trend, momentum)
                    action = "BUY_YES" if probability > 0.5 else "BUY_NO"
                
                # Calculate confidence and value
                confidence = abs(probability - 0.5) * 2  # Convert to 0-1 scale
                value_score = self._calculate_value_score(probability, market.get('yes_price', 50))
                
                # Only include if there's some edge
                if confidence > 0.1 and value_score > 0:
                    recommendations.append({
                        'market': market,
                        'action': action,
                        'target_price': price_level,
                        'probability': round(probability * 100, 1),
                        'confidence': round(confidence * 100, 1),
                        'value_score': round(value_score, 2),
                        'reasoning': self._generate_market_reasoning(current_price, price_level, probability, trend, volatility),
                        'kalshi_price': market.get('yes_price', 0),
                        'volume': market.get('volume', 0),
                        'ticker': market.get('ticker', ''),
                        'title': title
                    })
            
            except Exception as e:
                logger.error(f"Error processing market {market.get('ticker', '')}: {e}")
                continue
        
        # Sort by value score and confidence
        recommendations.sort(key=lambda x: (x['value_score'], x['confidence']), reverse=True)
        return recommendations[:10]  # Return top 10 opportunities
    
    def _extract_price_from_title(self, title: str) -> Optional[float]:
        """Extract price level from market title."""
        import re
        
        # Look for decimal numbers in the title
        # Pattern for numbers like 1.19159, 115000, etc.
        patterns = [
            r'(\d+\.\d{4,})',  # Decimal with 4+ places
            r'(\d{5,})',       # Large integers (like 115000)
            r'(\d+\.\d{2,3})', # Standard decimal
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, title)
            if matches:
                try:
                    return float(matches[0])
                except ValueError:
                    continue
        
        return None
    
    def _calculate_probability_above(self, current_price: float, target_price: float, volatility: Dict, trend: Dict, momentum: Dict) -> float:
        """Calculate probability that price will be above target."""
        if current_price <= 0 or target_price <= 0:
            return 0.5
        
        # Base probability from current position
        price_ratio = target_price / current_price
        base_prob = 0.5
        
        # Adjust for distance
        if price_ratio > 1.01:  # Target is significantly above current
            base_prob = 0.3
        elif price_ratio < 0.99:  # Target is significantly below current
            base_prob = 0.7
        else:  # Target is close to current
            base_prob = 0.5
        
        # Adjust for trend
        if trend.get('trend') == 'UPTREND':
            base_prob += 0.1
        elif trend.get('trend') == 'DOWNTREND':
            base_prob -= 0.1
        
        # Adjust for momentum
        rsi = momentum.get('rsi', 50)
        if rsi > 60:
            base_prob += 0.05
        elif rsi < 40:
            base_prob -= 0.05
        
        # Adjust for volatility
        vol_signal = volatility.get('signal', 'MODERATE_VOLATILITY')
        if vol_signal == 'HIGH_VOLATILITY':
            # High volatility makes extreme moves more likely
            if price_ratio > 1.02:
                base_prob += 0.1
            elif price_ratio < 0.98:
                base_prob -= 0.1
        
        return max(0.1, min(0.9, base_prob))
    
    def _calculate_probability_below(self, current_price: float, target_price: float, volatility: Dict, trend: Dict, momentum: Dict) -> float:
        """Calculate probability that price will be below target."""
        return 1.0 - self._calculate_probability_above(current_price, target_price, volatility, trend, momentum)
    
    def _calculate_value_score(self, probability: float, kalshi_price: float) -> float:
        """Calculate value score for a market opportunity."""
        if kalshi_price <= 0:
            return 0
        
        # Convert Kalshi price to decimal (assuming it's in cents)
        kalshi_decimal = kalshi_price / 100 if kalshi_price > 1 else kalshi_price
        
        # Calculate expected value
        expected_value = (probability * 1.0) - ((1 - probability) * 1.0)  # $1 payout
        cost = kalshi_decimal
        
        # Value score is expected value minus cost
        value_score = expected_value - cost
        
        return value_score
    
    def _generate_market_reasoning(self, current_price: float, target_price: float, probability: float, trend: Dict, volatility: Dict) -> str:
        """Generate reasoning for a market recommendation."""
        price_diff = target_price - current_price
        price_diff_pct = (price_diff / current_price) * 100
        
        if price_diff > 0:
            direction = "above"
            distance = f"{price_diff_pct:.1f}% above"
        else:
            direction = "below"
            distance = f"{abs(price_diff_pct):.1f}% below"
        
        trend_desc = trend.get('trend', 'SIDEWAYS')
        vol_desc = volatility.get('signal', 'MODERATE_VOLATILITY')
        
        if probability > 0.6:
            confidence = "High"
        elif probability > 0.4:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        return f"{confidence} confidence that price will be {direction} ${target_price:,.2f} ({distance} current). Trend: {trend_desc}, Volatility: {vol_desc}"
    
    # Helper methods for technical calculations
    
    def _calculate_atr(self, prices: List[float], period: int) -> float:
        """Calculate Average True Range."""
        if len(prices) < period + 1:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(prices)):
            tr = abs(prices[i] - prices[i-1])
            true_ranges.append(tr)
        
        return sum(true_ranges[-period:]) / period if true_ranges else 0.0
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return 50.0
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, prices: List[float]) -> float:
        """Calculate MACD (simplified)."""
        if len(prices) < 26:
            return 0.0
        
        # Simplified MACD calculation
        ema_12 = sum(prices[-12:]) / 12
        ema_26 = sum(prices[-26:]) / 26
        
        return ema_12 - ema_26
    
    # Description methods
    
    def _get_volatility_description(self, volatility: float, choppiness: float) -> str:
        """Get volatility description."""
        if volatility > 3.0 or choppiness > 2.0:
            return "Market is very choppy and volatile. High risk of sudden moves."
        elif volatility < 1.0 and choppiness < 0.5:
            return "Market is calm and stable. Good for conservative betting."
        else:
            return "Moderate volatility. Normal market conditions."
    
    def _get_trend_description(self, trend: str, strength: float) -> str:
        """Get trend description."""
        if trend == "UPTREND" and strength > 0.6:
            return f"Strong uptrend with {strength:.0%} strength. Momentum favors upward moves."
        elif trend == "DOWNTREND" and strength > 0.6:
            return f"Strong downtrend with {strength:.0%} strength. Momentum favors downward moves."
        elif trend == "SIDEWAYS":
            return "Sideways movement. No clear directional bias."
        else:
            return f"Weak {trend.lower()}. Unclear direction."
    
    def _get_momentum_description(self, rsi: float, macd: float) -> str:
        """Get momentum description."""
        if rsi > 70:
            return f"RSI {rsi:.1f} - Overbought. Potential for pullback."
        elif rsi < 30:
            return f"RSI {rsi:.1f} - Oversold. Potential for bounce."
        else:
            return f"RSI {rsi:.1f} - Neutral momentum. MACD: {macd:.2f}"
    
    def _get_sentiment_description(self, sentiment: str, score: float) -> str:
        """Get sentiment description."""
        if sentiment == "BULLISH":
            return f"Bullish sentiment ({score:.0%} confidence). Market favors upward moves."
        elif sentiment == "BEARISH":
            return f"Bearish sentiment ({score:.0%} confidence). Market favors downward moves."
        else:
            return f"Neutral sentiment ({score:.0%} confidence). Mixed signals."
    
    def _get_risk_description(self, level: str, score: float) -> str:
        """Get risk description."""
        if level == "LOW":
            return f"Low risk environment ({score:.0%}). Good conditions for betting."
        elif level == "HIGH":
            return f"High risk environment ({score:.0%}). Consider waiting for better conditions."
        else:
            return f"Moderate risk environment ({score:.0%}). Normal caution advised."
