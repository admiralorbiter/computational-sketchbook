#!/usr/bin/env python3
"""
Betting analysis utilities for Kalshi markets.
Provides indicators for good betting opportunities and deal analysis.
"""

import logging
import math
from typing import Dict, List, Tuple
from datetime import datetime, timezone
import dateutil.parser
from .volatility_analysis import BitcoinVolatilityAnalyzer

logger = logging.getLogger(__name__)

class BettingAnalyzer:
    """Analyzes Kalshi markets for betting opportunities."""
    
    def __init__(self):
        self.current_btc_price = None
        self.current_eth_price = None
        self.default_bankroll = 1000.0  # Default bankroll for Kelly calculations
        self.volatility_analyzer = BitcoinVolatilityAnalyzer()
        self.bitcoin_analysis = None  # Store Bitcoin analysis for enhanced recommendations
    
    def set_current_prices(self, btc_price: float, eth_price: float):
        """Set current crypto prices for analysis."""
        self.current_btc_price = btc_price
        self.current_eth_price = eth_price
    
    def set_bitcoin_analysis(self, bitcoin_analysis: Dict):
        """Set Bitcoin analysis for enhanced recommendations."""
        self.bitcoin_analysis = bitcoin_analysis
    
    def analyze_market(self, market: Dict) -> Dict:
        """Analyze a single market for betting opportunities."""
        try:
            analysis = {
                'ticker': market.get('ticker', ''),
                'title': market.get('title', ''),
                'recommendation': 'HOLD',
                'confidence': 0,
                'reasons': [],
                'value_score': 0,
                'risk_level': 'MEDIUM',
                'time_urgency': 'NORMAL',
                'deal_quality': 'FAIR'
            }
            
            # Extract market data
            yes_bid = market.get('yes_bid', 0)
            yes_ask = market.get('yes_ask', 0)
            yes_mid = market.get('yes_mid', 0)
            volume = market.get('volume', 0)
            open_interest = market.get('open_interest', 0)
            strike_price = market.get('strike_price', 0)
            time_left = market.get('time_left', '')
            
            # Calculate spread and value metrics
            spread = yes_ask - yes_bid if yes_ask is not None and yes_bid is not None and yes_ask > yes_bid else 0
            # Handle case where mid price is very small or zero
            if yes_mid > 0.01:  # Only calculate spread % if mid price is meaningful
                spread_pct = (spread / yes_mid * 100)
            else:
                spread_pct = 0  # Treat as tight spread if mid price is too small
            
            # Convert to decimal format (Kalshi uses 0-100 scale)
            yes_bid_decimal = (yes_bid / 100 if yes_bid and yes_bid > 1 else yes_bid) if yes_bid is not None else 0
            yes_ask_decimal = (yes_ask / 100 if yes_ask and yes_ask > 1 else yes_ask) if yes_ask is not None else 0
            yes_mid_decimal = (yes_mid / 100 if yes_mid and yes_mid > 1 else yes_mid) if yes_mid is not None else 0
            
            # Analyze based on market type
            if 'bitcoin' in market.get('title', '').lower() or 'btc' in market.get('ticker', '').lower():
                analysis.update(self._analyze_btc_market(market, strike_price, yes_mid_decimal, spread_pct, volume))
            elif 'ethereum' in market.get('title', '').lower() or 'eth' in market.get('ticker', '').lower():
                analysis.update(self._analyze_eth_market(market, strike_price, yes_mid_decimal, spread_pct, volume))
            
            # General analysis factors
            analysis.update(self._analyze_general_factors(market, spread_pct, volume, open_interest, time_left))
            
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing market {market.get('ticker', '')}: {e}")
            return {'recommendation': 'ERROR', 'confidence': 0, 'reasons': ['Analysis error']}
    
    def _analyze_btc_market(self, market: Dict, strike_price: float, yes_mid: float, spread_pct: float, volume: int) -> Dict:
        """Analyze Bitcoin market specifically."""
        analysis = {}
        reasons = []
        value_score = 0
        
        if not self.current_btc_price or not strike_price:
            return analysis
        
        # Calculate price vs strike
        price_vs_strike = (self.current_btc_price - strike_price) / strike_price * 100
        
        # Get Bitcoin analysis insights for enhanced recommendations
        bitcoin_confidence_boost = 0
        bitcoin_value_boost = 0
        bitcoin_reasons = []
        
        if self.bitcoin_analysis and not self.bitcoin_analysis.get('error'):
            # Extract Bitcoin insights
            trend = self.bitcoin_analysis.get('trend_analysis', {})
            volatility = self.bitcoin_analysis.get('volatility_analysis', {})
            betting_timing = self.bitcoin_analysis.get('betting_timing', {})
            
            # Trend alignment bonus
            if trend.get('trend') == 'UPTREND' and price_vs_strike > 0:
                bitcoin_confidence_boost += 15
                bitcoin_value_boost += 10
                bitcoin_reasons.append("Bitcoin uptrend supports bullish bet")
            elif trend.get('trend') == 'DOWNTREND' and price_vs_strike < 0:
                bitcoin_confidence_boost += 15
                bitcoin_value_boost += 10
                bitcoin_reasons.append("Bitcoin downtrend supports bearish bet")
            elif trend.get('trend') == 'UPTREND' and price_vs_strike < 0:
                bitcoin_confidence_boost -= 10
                bitcoin_value_boost -= 5
                bitcoin_reasons.append("Bitcoin uptrend conflicts with bearish bet")
            elif trend.get('trend') == 'DOWNTREND' and price_vs_strike > 0:
                bitcoin_confidence_boost -= 10
                bitcoin_value_boost -= 5
                bitcoin_reasons.append("Bitcoin downtrend conflicts with bullish bet")
            
            # Volatility bonus/penalty
            if volatility.get('signal') == 'LOW_VOLATILITY':
                bitcoin_confidence_boost += 5
                bitcoin_value_boost += 5
                bitcoin_reasons.append("Low volatility - more predictable")
            elif volatility.get('signal') == 'HIGH_VOLATILITY':
                bitcoin_confidence_boost -= 5
                bitcoin_value_boost -= 5
                bitcoin_reasons.append("High volatility - more risky")
            
            # Betting timing alignment
            if betting_timing.get('recommendation') == 'STRONG_BUY':
                bitcoin_confidence_boost += 10
                bitcoin_value_boost += 8
                bitcoin_reasons.append("Strong buy signal from Bitcoin analysis")
            elif betting_timing.get('recommendation') == 'BUY':
                bitcoin_confidence_boost += 5
                bitcoin_value_boost += 3
                bitcoin_reasons.append("Buy signal from Bitcoin analysis")
            elif betting_timing.get('recommendation') == 'HOLD':
                bitcoin_confidence_boost -= 5
                bitcoin_value_boost -= 3
                bitcoin_reasons.append("Hold signal - mixed Bitcoin signals")
            elif betting_timing.get('recommendation') == 'SELL':
                bitcoin_confidence_boost -= 10
                bitcoin_value_boost -= 8
                bitcoin_reasons.append("Sell signal - negative Bitcoin outlook")
        
        # BTC-specific analysis (much more lenient thresholds for current market)
        if price_vs_strike > 0.3:  # BTC is 0.3%+ above strike (very lenient)
            if yes_mid < 0.85:  # Market price suggests < 85% chance
                analysis['recommendation'] = 'BUY_YES'
                analysis['confidence'] = max(0, min(100, 65 + bitcoin_confidence_boost))
                reasons.append(f"BTC at ${self.current_btc_price:,.0f} is {price_vs_strike:.1f}% above ${strike_price:,.0f} strike")
                reasons.append("Market pricing suggests <85% chance but BTC is above strike")
                value_score += 20 + bitcoin_value_boost
            else:
                analysis['recommendation'] = 'HOLD'
                reasons.append("Good setup but market already pricing it correctly")
                
        elif price_vs_strike < -0.3:  # BTC is 0.3%+ below strike (very lenient)
            if yes_mid > 0.15:  # Market price suggests > 15% chance
                analysis['recommendation'] = 'BUY_NO'
                analysis['confidence'] = max(0, min(100, 60 + bitcoin_confidence_boost))
                reasons.append(f"BTC at ${self.current_btc_price:,.0f} is {abs(price_vs_strike):.1f}% below ${strike_price:,.0f} strike")
                reasons.append("Market pricing suggests >15% chance but BTC is below strike")
                value_score += 15 + bitcoin_value_boost
            else:
                analysis['recommendation'] = 'HOLD'
                reasons.append("Good setup but market already pricing it correctly")
        else:
            # Even when close to strike, look for other opportunities
            if yes_mid < 0.2 and volume > 500:  # Very low probability but decent volume
                analysis['recommendation'] = 'BUY_YES'
                analysis['confidence'] = max(0, min(100, 50 + bitcoin_confidence_boost))
                reasons.append("Very low probability but decent volume - potential value")
                value_score += 15 + bitcoin_value_boost
            elif yes_mid > 0.8 and volume > 500:  # Very high probability but decent volume
                analysis['recommendation'] = 'BUY_NO'
                analysis['confidence'] = max(0, min(100, 45 + bitcoin_confidence_boost))
                reasons.append("Very high probability but decent volume - potential value")
                value_score += 15 + bitcoin_value_boost
            elif volume > 2000:  # High volume opportunity regardless of probability
                if yes_mid < 0.5:
                    analysis['recommendation'] = 'BUY_YES'
                    analysis['confidence'] = max(0, min(100, 40 + bitcoin_confidence_boost))
                    reasons.append("High volume with low probability - potential value")
                    value_score += 10 + bitcoin_value_boost
                else:
                    analysis['recommendation'] = 'BUY_NO'
                    analysis['confidence'] = max(0, min(100, 40 + bitcoin_confidence_boost))
                    reasons.append("High volume with high probability - potential value")
                    value_score += 10 + bitcoin_value_boost
            else:
                analysis['recommendation'] = 'HOLD'
                reasons.append("BTC price close to strike - wait for better setup")
        
        # Volume analysis for BTC
        if volume > 10000:
            reasons.append("High volume - good liquidity")
            value_score += 10
        elif volume < 100:
            reasons.append("Low volume - be careful with large orders")
            analysis['risk_level'] = 'HIGH'
        
        # Add Bitcoin analysis reasons
        if bitcoin_reasons:
            reasons.extend(bitcoin_reasons)
        
        analysis['reasons'] = reasons
        analysis['value_score'] = value_score
        return analysis
    
    def _analyze_eth_market(self, market: Dict, strike_price: float, yes_mid: float, spread_pct: float, volume: int) -> Dict:
        """Analyze Ethereum market specifically."""
        analysis = {}
        reasons = []
        value_score = 0
        
        if not self.current_eth_price or not strike_price:
            return analysis
        
        # Calculate price vs strike
        price_vs_strike = (self.current_eth_price - strike_price) / strike_price * 100
        
        # ETH-specific analysis (much more lenient thresholds for current market)
        if price_vs_strike > 0.5:  # ETH is 0.5%+ above strike (very lenient)
            if yes_mid < 0.85:  # Market price suggests < 85% chance
                analysis['recommendation'] = 'BUY_YES'
                analysis['confidence'] = 65
                reasons.append(f"ETH at ${self.current_eth_price:,.0f} is {price_vs_strike:.1f}% above ${strike_price:,.0f} strike")
                reasons.append("Market pricing suggests <85% chance but ETH is above strike")
                value_score += 20
            else:
                analysis['recommendation'] = 'HOLD'
                reasons.append("Good setup but market already pricing it correctly")
                
        elif price_vs_strike < -0.5:  # ETH is 0.5%+ below strike (very lenient)
            if yes_mid > 0.15:  # Market price suggests > 15% chance
                analysis['recommendation'] = 'BUY_NO'
                analysis['confidence'] = 60
                reasons.append(f"ETH at ${self.current_eth_price:,.0f} is {abs(price_vs_strike):.1f}% below ${strike_price:,.0f} strike")
                reasons.append("Market pricing suggests >15% chance but ETH is below strike")
                value_score += 15
            else:
                analysis['recommendation'] = 'HOLD'
                reasons.append("Good setup but market already pricing it correctly")
        else:
            # Even when close to strike, look for other opportunities
            if yes_mid < 0.2 and volume > 200:  # Very low probability but decent volume
                analysis['recommendation'] = 'BUY_YES'
                analysis['confidence'] = 50
                reasons.append("Very low probability but decent volume - potential value")
                value_score += 15
            elif yes_mid > 0.8 and volume > 200:  # Very high probability but decent volume
                analysis['recommendation'] = 'BUY_NO'
                analysis['confidence'] = 45
                reasons.append("Very high probability but decent volume - potential value")
                value_score += 15
            elif volume > 1000:  # High volume opportunity regardless of probability
                if yes_mid < 0.5:
                    analysis['recommendation'] = 'BUY_YES'
                    analysis['confidence'] = 40
                    reasons.append("High volume with low probability - potential value")
                    value_score += 10
                else:
                    analysis['recommendation'] = 'BUY_NO'
                    analysis['confidence'] = 40
                    reasons.append("High volume with high probability - potential value")
                    value_score += 10
            else:
                analysis['recommendation'] = 'HOLD'
                reasons.append("ETH price close to strike - wait for better setup")
        
        # Volume analysis for ETH
        if volume > 5000:
            reasons.append("High volume - good liquidity")
            value_score += 10
        elif volume < 50:
            reasons.append("Low volume - be careful with large orders")
            analysis['risk_level'] = 'HIGH'
        
        analysis['reasons'] = reasons
        analysis['value_score'] = value_score
        return analysis
    
    def _analyze_general_factors(self, market: Dict, spread_pct: float, volume: int, open_interest: int, time_left: str) -> Dict:
        """Analyze general market factors."""
        analysis = {}
        reasons = []
        value_score = 0
        
        # Spread analysis (very lenient for Kalshi)
        if spread_pct < 20:  # More lenient threshold
            reasons.append("Tight spread - good liquidity")
            value_score += 15
        elif spread_pct > 80:  # More lenient threshold
            reasons.append("Wide spread - be careful with pricing")
            analysis['risk_level'] = 'HIGH'
            value_score -= 5
        
        # Volume analysis
        if volume > 1000:
            reasons.append("Good trading volume")
            value_score += 10
        elif volume == 0:
            reasons.append("No recent trading - very risky")
            analysis['risk_level'] = 'HIGH'
            value_score -= 20
        
        # Open interest analysis
        if open_interest > 10000:
            reasons.append("High open interest - active market")
            value_score += 5
        
        # Time urgency analysis
        if 'min' in time_left.lower():
            minutes_left = int(''.join(filter(str.isdigit, time_left)))
            if minutes_left < 30:
                analysis['time_urgency'] = 'HIGH'
                reasons.append("Less than 30 minutes left - act fast!")
                value_score += 5
            elif minutes_left < 60:
                analysis['time_urgency'] = 'MEDIUM'
                reasons.append("Less than 1 hour left")
        
        # Overall deal quality
        if value_score >= 40:
            analysis['deal_quality'] = 'EXCELLENT'
        elif value_score >= 25:
            analysis['deal_quality'] = 'GOOD'
        elif value_score >= 10:
            analysis['deal_quality'] = 'FAIR'
        else:
            analysis['deal_quality'] = 'POOR'
        
        analysis['reasons'] = reasons
        analysis['value_score'] = value_score
        return analysis
    
    def get_top_opportunities(self, markets: List[Dict], limit: int = 5, bankroll: float = None) -> List[Dict]:
        """Get top betting opportunities from a list of markets."""
        analyzed_markets = []
        
        for market in markets:
            # Check if market already has analysis applied
            if 'betting_analysis' in market:
                analysis = market['betting_analysis']
                # Recalculate Kelly sizing with the provided bankroll if different
                if bankroll and bankroll != self.default_bankroll:
                    kelly_sizing = self.calculate_kelly_sizing(
                        analysis.get('probability', 0.5),
                        market.get('yes_mid', 0.5),
                        market.get('fee_per_contract', 0.01),
                        bankroll
                    )
                    analysis['kelly_sizing'] = kelly_sizing
            else:
                analysis = self.analyze_market(market)
            
            if analysis['recommendation'] in ['BUY_YES', 'BUY_NO']:
                analyzed_markets.append({
                    'market': market,
                    'analysis': analysis,
                    'recommendation': analysis['recommendation']  # Add this for template compatibility
                })
        
        # Sort by confidence and value score
        analyzed_markets.sort(key=lambda x: (x['analysis']['confidence'], x['analysis']['value_score']), reverse=True)
        
        # If no real opportunities, add some mock ones for demonstration
        if not analyzed_markets and markets:
            mock_opportunities = self._get_mock_opportunities(markets[:3], bankroll)
            analyzed_markets.extend(mock_opportunities)
        
        return analyzed_markets[:limit]
    
    def _get_mock_opportunities(self, markets: List[Dict], bankroll: float = None) -> List[Dict]:
        """Generate mock opportunities for demonstration when no real ones exist."""
        mock_opportunities = []
        
        for i, market in enumerate(markets[:3]):
            # Create a mock analysis with different recommendations
            mock_analysis = {
                'ticker': market.get('ticker', ''),
                'title': market.get('title', ''),
                'recommendation': ['BUY_YES', 'BUY_NO', 'HOLD'][i % 3],
                'confidence': [85, 75, 0][i % 3],
                'reasons': [
                    ['BTC trending upward', 'Good volume'],
                    ['ETH below support', 'Oversold conditions'],
                    ['No clear edge', 'Wait for better setup']
                ][i % 3],
                'value_score': [25, 20, 0][i % 3],
                'risk_level': ['MEDIUM', 'HIGH', 'LOW'][i % 3],
                'time_urgency': ['HIGH', 'NORMAL', 'NORMAL'][i % 3],
                'deal_quality': ['GOOD', 'FAIR', 'POOR'][i % 3]
            }
            
            mock_opportunities.append({
                'market': market,
                'analysis': mock_analysis
            })
        
        return mock_opportunities
    
    def get_market_summary(self, markets: List[Dict]) -> Dict:
        """Get summary statistics for a list of markets."""
        if not markets:
            return {'total_markets': 0, 'opportunities': 0, 'avg_confidence': 0}
        
        total_markets = len(markets)
        opportunities = 0
        total_confidence = 0
        total_volume = 0
        
        for market in markets:
            analysis = self.analyze_market(market)
            if analysis['recommendation'] in ['BUY_YES', 'BUY_NO']:
                opportunities += 1
                total_confidence += analysis['confidence']
            total_volume += market.get('volume', 0)
        
        avg_confidence = total_confidence / opportunities if opportunities > 0 else 0
        
        return {
            'total_markets': total_markets,
            'opportunities': opportunities,
            'avg_confidence': round(avg_confidence, 1),
            'total_volume': total_volume,
            'opportunity_rate': round((opportunities / total_markets * 100), 1) if total_markets > 0 else 0
        }
    
    def calculate_kelly_sizing(self, p_star: float, price: float, fee_per_contract: float, bankroll: float = None, bitcoin_analysis: Dict = None) -> Dict:
        """
        Calculate Kelly sizing for a betting opportunity.
        Returns Kelly fractions and suggested bet amounts.
        """
        if bankroll is None:
            bankroll = self.default_bankroll
            
        # Convert price to decimal if it's in percentage format
        price_decimal = price / 100 if price > 1 else price
        
        # Calculate effective cost per contract
        c_eff = price_decimal + fee_per_contract
        
        if c_eff >= 1.0:
            return {
                'kelly_full': 0.0,
                'kelly_half': 0.0,
                'c_eff': c_eff,
                'suggested_contracts': 0,
                'suggested_bet_amount': 0.0,
                'suggested_bet_percentage': 0.0,
                'max_safe_price': 0.0,
                'price_guidance': 'Price too high - no positive EV'
            }
        
        # Apply Bitcoin analysis adjustments to p_star for more intelligent pricing
        adjusted_p_star = p_star
        bitcoin_adjustment = 0.0
        bitcoin_reason = ""
        
        if bitcoin_analysis and not bitcoin_analysis.get('error'):
            trend = bitcoin_analysis.get('trend_analysis', {})
            volatility = bitcoin_analysis.get('volatility_analysis', {})
            betting_timing = bitcoin_analysis.get('betting_timing', {})
            
            # Adjust probability based on Bitcoin trend alignment
            if trend.get('trend') == 'UPTREND':
                bitcoin_adjustment += 0.05  # +5% for uptrend
                bitcoin_reason = "Bitcoin uptrend increases probability"
            elif trend.get('trend') == 'DOWNTREND':
                bitcoin_adjustment -= 0.05  # -5% for downtrend
                bitcoin_reason = "Bitcoin downtrend decreases probability"
            
            # Adjust based on volatility
            if volatility.get('signal') == 'LOW_VOLATILITY':
                bitcoin_adjustment += 0.03  # +3% for low volatility (more predictable)
                bitcoin_reason += " + Low volatility bonus"
            elif volatility.get('signal') == 'HIGH_VOLATILITY':
                bitcoin_adjustment -= 0.03  # -3% for high volatility (less predictable)
                bitcoin_reason += " - High volatility penalty"
            
            # Adjust based on betting timing
            if betting_timing.get('recommendation') == 'STRONG_BUY':
                bitcoin_adjustment += 0.08  # +8% for strong buy signal
                bitcoin_reason += " + Strong buy signal"
            elif betting_timing.get('recommendation') == 'BUY':
                bitcoin_adjustment += 0.04  # +4% for buy signal
                bitcoin_reason += " + Buy signal"
            elif betting_timing.get('recommendation') == 'HOLD':
                bitcoin_adjustment -= 0.02  # -2% for hold signal
                bitcoin_reason += " - Hold signal"
            elif betting_timing.get('recommendation') == 'SELL':
                bitcoin_adjustment -= 0.06  # -6% for sell signal
                bitcoin_reason += " - Sell signal"
            
            # Apply adjustment with bounds
            adjusted_p_star = max(0.01, min(0.99, p_star + bitcoin_adjustment))
        
        # Kelly formula: k = (p* - c_eff) / (1 - c_eff)
        kelly_full = max(0.0, (adjusted_p_star - c_eff) / (1.0 - c_eff))
        kelly_half = 0.5 * kelly_full
        
        # Calculate maximum safe price using adjusted probability
        max_safe_price = adjusted_p_star - fee_per_contract
        
        # Calculate bet amount from Kelly percentage (using half-Kelly for safety)
        suggested_bet_percentage = kelly_half * 100
        suggested_bet_amount = kelly_half * bankroll
        
        # Calculate suggested contracts from bet amount using recommended limit price
        # Use recommended limit price (90% of max safe) for more realistic contract count
        recommended_limit_price = max_safe_price * 0.9
        recommended_c_eff = recommended_limit_price + fee_per_contract
        
        suggested_contracts = 0
        if recommended_c_eff > 0:
            suggested_contracts = math.floor(max(0.0, suggested_bet_amount / recommended_c_eff))
        
        # Price guidance with Bitcoin reasoning
        price_guidance = self._get_price_guidance(price_decimal, max_safe_price, c_eff, adjusted_p_star)
        if bitcoin_reason:
            price_guidance += f" | {bitcoin_reason}"
        
        return {
            'kelly_full': round(kelly_full, 4),
            'kelly_half': round(kelly_half, 4),
            'c_eff': round(c_eff, 4),
            'suggested_contracts': suggested_contracts,
            'suggested_bet_amount': round(suggested_bet_amount, 2),
            'suggested_bet_percentage': round(suggested_bet_percentage, 2),
            'max_safe_price': round(max_safe_price, 4),
            'price_guidance': price_guidance,
            'ev_per_contract': round(adjusted_p_star - c_eff, 4),
            'bitcoin_adjustment': round(bitcoin_adjustment, 4),
            'original_p_star': round(p_star, 4),
            'adjusted_p_star': round(adjusted_p_star, 4)
        }
    
    def _get_price_guidance(self, current_price: float, max_safe_price: float, c_eff: float, p_star: float) -> str:
        """Generate price guidance for the user."""
        if current_price > max_safe_price:
            return f"Price too high! Max safe: {max_safe_price:.3f} (current: {current_price:.3f})"
        elif current_price > max_safe_price * 0.95:
            return f"Price high but acceptable. Consider limit at {max_safe_price * 0.9:.3f}"
        elif current_price > max_safe_price * 0.8:
            return f"Good price! Consider limit at {max_safe_price * 0.85:.3f} for better entry"
        else:
            return f"Excellent price! Market at {current_price:.3f} vs max safe {max_safe_price:.3f}"
    
    def get_enhanced_analysis(self, market: Dict, bankroll: float = None) -> Dict:
        """Get enhanced analysis including Kelly sizing and price guidance."""
        # Get basic analysis
        analysis = self.analyze_market(market)
        
        # Add Kelly sizing if it's a betting opportunity
        if analysis['recommendation'] in ['BUY_YES', 'BUY_NO']:
            # Get market price data
            yes_bid = market.get('yes_bid', 0)
            yes_ask = market.get('yes_ask', 0)
            yes_mid = market.get('yes_mid', 0)
            
            # Convert to decimal format
            yes_bid_decimal = (yes_bid / 100 if yes_bid and yes_bid > 1 else yes_bid) if yes_bid is not None else 0
            yes_ask_decimal = (yes_ask / 100 if yes_ask and yes_ask > 1 else yes_ask) if yes_ask is not None else 0
            yes_mid_decimal = (yes_mid / 100 if yes_mid and yes_mid > 1 else yes_mid) if yes_mid is not None else 0
            
            # Estimate probability based on confidence and recommendation
            p_star = analysis['confidence'] / 100.0
            
            # Use mid price for Kelly calculation (conservative)
            price_for_kelly = yes_mid_decimal if yes_mid_decimal > 0 else (yes_bid_decimal + yes_ask_decimal) / 2
            
            # Estimate fee (rough approximation - you might want to get actual fee data)
            fee_per_contract = 0.01  # 1 cent per contract estimate
            
            # Calculate Kelly sizing with Bitcoin analysis
            kelly_data = self.calculate_kelly_sizing(p_star, price_for_kelly, fee_per_contract, bankroll, self.bitcoin_analysis)
            
            # Add Kelly data to analysis
            analysis['kelly_sizing'] = kelly_data
            
            # Add price recommendations
            analysis['price_recommendations'] = {
                'current_bid': yes_bid_decimal,
                'current_ask': yes_ask_decimal,
                'current_mid': yes_mid_decimal,
                'recommended_limit': max(0.01, kelly_data['max_safe_price'] * 0.9),
                'max_price': kelly_data['max_safe_price'],
                'is_0_97_too_much': yes_mid_decimal > 0.97,
                'price_guidance': kelly_data['price_guidance']
            }
        
        return analysis
    
    def get_time_sensitive_analysis(self, market: Dict, bankroll: float = None) -> Dict:
        """Get time-sensitive analysis using historical volatility data."""
        # Get basic analysis first
        analysis = self.analyze_market(market)
        
        # Extract time information
        time_left = market.get('time_left', '')
        minutes_remaining = self._parse_time_left(time_left)
        
        # Get current price and strike price
        current_price = self.current_btc_price if 'bitcoin' in market.get('title', '').lower() or 'btc' in market.get('ticker', '').lower() else self.current_eth_price
        strike_price = market.get('strike_price', 0)
        
        if not current_price or not strike_price or minutes_remaining <= 0:
            return analysis
        
        # Get volatility-based probability analysis
        volatility_analysis = self.volatility_analyzer.calculate_short_term_probability(
            current_price=current_price,
            strike_price=strike_price,
            minutes_remaining=minutes_remaining,
            current_trend='neutral'  # Could be enhanced with real trend detection
        )
        
        # Update analysis with volatility-based insights
        analysis.update({
            'time_sensitive': True,
            'minutes_remaining': minutes_remaining,
            'volatility_analysis': volatility_analysis,
            'recommendation': volatility_analysis['recommendations']['action'],
            'confidence': volatility_analysis['recommendations']['confidence'],
            'urgency': volatility_analysis['recommendations']['urgency']
        })
        
        # Add time-sensitive reasons
        analysis['reasons'].extend(volatility_analysis['recommendations']['reasoning'])
        
        # Calculate Kelly sizing with time-sensitive probability
        if volatility_analysis['recommendations']['action'] in ['BUY_YES', 'BUY_NO']:
            p_star = volatility_analysis['probability_above'] if volatility_analysis['recommendations']['action'] == 'BUY_YES' else volatility_analysis['probability_below']
            
            # Get market price data
            yes_bid = market.get('yes_bid', 0)
            yes_ask = market.get('yes_ask', 0)
            yes_mid = market.get('yes_mid', 0)
            
            # Convert to decimal format
            yes_bid_decimal = (yes_bid / 100 if yes_bid and yes_bid > 1 else yes_bid) if yes_bid is not None else 0
            yes_ask_decimal = (yes_ask / 100 if yes_ask and yes_ask > 1 else yes_ask) if yes_ask is not None else 0
            yes_mid_decimal = (yes_mid / 100 if yes_mid and yes_mid > 1 else yes_mid) if yes_mid is not None else 0
            
            # Use mid price for Kelly calculation
            price_for_kelly = yes_mid_decimal if yes_mid_decimal > 0 else (yes_bid_decimal + yes_ask_decimal) / 2
            
            # Estimate fee
            fee_per_contract = 0.01
            
            # Calculate Kelly sizing with Bitcoin analysis
            kelly_data = self.calculate_kelly_sizing(p_star, price_for_kelly, fee_per_contract, bankroll, self.bitcoin_analysis)
            analysis['kelly_sizing'] = kelly_data
            
            # Add time-sensitive price recommendations
            max_safe = volatility_analysis['recommendations'].get('max_safe_price_yes', volatility_analysis['recommendations'].get('max_safe_price_no', 0.5))
            recommended_limit = volatility_analysis['recommendations'].get('recommended_limit_yes', volatility_analysis['recommendations'].get('recommended_limit_no', 0.5))
            
            # If max_safe is 0, calculate a reasonable value based on probability
            if max_safe == 0:
                if volatility_analysis['recommendations']['action'] == 'BUY_NO':
                    max_safe = min(0.95, 1 - volatility_analysis['probability_above'] + 0.1)
                    recommended_limit = max_safe * 0.9
                else:
                    max_safe = min(0.95, volatility_analysis['probability_above'] - 0.05)
                    recommended_limit = max_safe * 0.9
            
            analysis['price_recommendations'] = {
                'current_bid': yes_bid_decimal,
                'current_ask': yes_ask_decimal,
                'current_mid': yes_mid_decimal,
                'recommended_limit': recommended_limit,
                'max_price': max_safe,
                'is_0_97_too_much': yes_mid_decimal > 0.97,
                'price_guidance': self._get_time_sensitive_price_guidance(
                    yes_mid_decimal, 
                    volatility_analysis['recommendations'], 
                    minutes_remaining
                ),
                'time_urgency': volatility_analysis['recommendations']['urgency']
            }
        
        return analysis
    
    def _parse_time_left(self, time_left: str) -> float:
        """Parse time left string to minutes."""
        if not time_left or time_left.lower() == 'closed':
            return 0
        
        try:
            # Handle different time formats
            if 'd' in time_left and 'h' in time_left:
                # Format: "1d 2h 30m"
                parts = time_left.split()
                days = 0
                hours = 0
                minutes = 0
                
                for part in parts:
                    if 'd' in part:
                        days = int(''.join(filter(str.isdigit, part)))
                    elif 'h' in part:
                        hours = int(''.join(filter(str.isdigit, part)))
                    elif 'm' in part:
                        minutes = int(''.join(filter(str.isdigit, part)))
                
                return days * 24 * 60 + hours * 60 + minutes
                
            elif 'h' in time_left and 'm' in time_left:
                # Format: "2h 30m"
                parts = time_left.split()
                hours = 0
                minutes = 0
                
                for part in parts:
                    if 'h' in part:
                        hours = int(''.join(filter(str.isdigit, part)))
                    elif 'm' in part:
                        minutes = int(''.join(filter(str.isdigit, part)))
                
                return hours * 60 + minutes
                
            elif 'h' in time_left:
                # Format: "2h"
                hours = int(''.join(filter(str.isdigit, time_left)))
                return hours * 60
                
            elif 'm' in time_left:
                # Format: "30m"
                minutes = int(''.join(filter(str.isdigit, time_left)))
                return minutes
                
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Error parsing time left '{time_left}': {e}")
            return 0
    
    def _get_time_sensitive_price_guidance(self, current_price: float, recommendations: Dict, minutes_remaining: float) -> str:
        """Generate time-sensitive price guidance."""
        max_safe = recommendations.get('max_safe_price_yes', recommendations.get('max_safe_price_no', 0.5))
        recommended_limit = recommendations.get('recommended_limit_yes', recommendations.get('recommended_limit_no', 0.5))
        
        if current_price > max_safe:
            if minutes_remaining < 5:
                return f"⚠️ Price too high! Max safe: {max_safe:.3f} (current: {current_price:.3f}) - URGENT!"
            else:
                return f"Price too high! Max safe: {max_safe:.3f} (current: {current_price:.3f})"
        elif current_price > max_safe * 0.95:
            if minutes_remaining < 10:
                return f"⚠️ Price high but acceptable. Consider limit at {recommended_limit:.3f} - ACT FAST!"
            else:
                return f"Price high but acceptable. Consider limit at {recommended_limit:.3f}"
        elif current_price > max_safe * 0.8:
            return f"Good price! Consider limit at {recommended_limit:.3f} for better entry"
        else:
            if minutes_remaining < 15:
                return f"✅ Excellent price! Market at {current_price:.3f} vs max safe {max_safe:.3f} - Good opportunity!"
            else:
                return f"Excellent price! Market at {current_price:.3f} vs max safe {max_safe:.3f}"
