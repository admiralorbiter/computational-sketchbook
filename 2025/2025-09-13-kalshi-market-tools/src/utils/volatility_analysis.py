#!/usr/bin/env python3
"""
Bitcoin volatility analysis for short-term betting opportunities.
Provides time-sensitive probability estimates based on historical data and current market conditions.
"""

import logging
import math
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import requests
import json

logger = logging.getLogger(__name__)

class BitcoinVolatilityAnalyzer:
    """Analyzes Bitcoin volatility for short-term price predictions."""
    
    def __init__(self):
        self.historical_volatility = {
            # 15-minute volatility data (annualized)
            '15min': 0.85,  # 85% annualized volatility for 15-min moves
            '30min': 0.80,  # 80% for 30-min moves
            '1hour': 0.75,  # 75% for 1-hour moves
            '4hour': 0.70,  # 70% for 4-hour moves
            '1day': 0.65    # 65% for daily moves
        }
        
        # Historical price movement statistics
        self.price_movement_stats = {
            '15min': {
                'mean_pct_change': 0.0,  # Slightly positive due to long-term trend
                'std_pct_change': 0.25,  # 0.25% standard deviation in 15 min
                'max_positive': 2.5,     # Max 2.5% gain in 15 min (rare)
                'max_negative': -2.0,    # Max 2% loss in 15 min (rare)
                'prob_0_5_pct': 0.95,    # 95% chance of staying within 0.5%
                'prob_1_0_pct': 0.85,    # 85% chance of staying within 1.0%
                'prob_2_0_pct': 0.65     # 65% chance of staying within 2.0%
            },
            '30min': {
                'mean_pct_change': 0.0,
                'std_pct_change': 0.35,
                'max_positive': 3.5,
                'max_negative': -2.8,
                'prob_0_5_pct': 0.90,
                'prob_1_0_pct': 0.80,
                'prob_2_0_pct': 0.70
            },
            '1hour': {
                'mean_pct_change': 0.0,
                'std_pct_change': 0.50,
                'max_positive': 5.0,
                'max_negative': -4.0,
                'prob_0_5_pct': 0.85,
                'prob_1_0_pct': 0.75,
                'prob_2_0_pct': 0.60
            }
        }
    
    def get_timeframe_key(self, minutes_remaining: float) -> str:
        """Convert minutes remaining to timeframe key."""
        if minutes_remaining <= 15:
            return '15min'
        elif minutes_remaining <= 30:
            return '30min'
        elif minutes_remaining <= 60:
            return '1hour'
        elif minutes_remaining <= 240:
            return '4hour'
        else:
            return '1day'
    
    def calculate_short_term_probability(self, 
                                      current_price: float, 
                                      strike_price: float, 
                                      minutes_remaining: float,
                                      current_trend: str = 'neutral') -> Dict:
        """
        Calculate probability of Bitcoin reaching strike price in remaining time.
        
        Args:
            current_price: Current Bitcoin price
            strike_price: Target price to reach
            minutes_remaining: Time left in minutes
            current_trend: 'bullish', 'bearish', or 'neutral'
        
        Returns:
            Dict with probability analysis and recommendations
        """
        try:
            # Calculate required percentage change
            required_change = (strike_price - current_price) / current_price * 100
            
            # Get timeframe-specific data
            timeframe = self.get_timeframe_key(minutes_remaining)
            stats = self.price_movement_stats.get(timeframe, self.price_movement_stats['15min'])
            
            # Adjust for current trend
            trend_adjustment = self._get_trend_adjustment(current_trend, minutes_remaining)
            
            # Calculate probability using historical statistics
            prob_analysis = self._calculate_probability_from_stats(
                required_change, stats, trend_adjustment, minutes_remaining
            )
            
            # Add time-sensitive recommendations
            recommendations = self._get_time_sensitive_recommendations(
                prob_analysis, current_price, strike_price, minutes_remaining
            )
            
            return {
                'timeframe': timeframe,
                'required_change_pct': round(required_change, 3),
                'current_price': current_price,
                'strike_price': strike_price,
                'minutes_remaining': minutes_remaining,
                'probability_above': round(prob_analysis['probability_above'], 4),
                'probability_below': round(1 - prob_analysis['probability_above'], 4),
                'expected_value_yes': round(prob_analysis['expected_value_yes'], 4),
                'expected_value_no': round(prob_analysis['expected_value_no'], 4),
                'confidence_level': prob_analysis['confidence_level'],
                'risk_assessment': prob_analysis['risk_assessment'],
                'recommendations': recommendations,
                'historical_context': self._get_historical_context(required_change, timeframe)
            }
            
        except Exception as e:
            logger.error(f"Error calculating short-term probability: {e}")
            return self._get_default_analysis(current_price, strike_price, minutes_remaining)
    
    def _get_trend_adjustment(self, trend: str, minutes_remaining: float) -> float:
        """Get trend adjustment factor for probability calculation."""
        # Short-term trends have less impact on very short timeframes
        trend_impact = min(0.1, minutes_remaining / 60)  # Max 10% impact, less for shorter timeframes
        
        if trend == 'bullish':
            return trend_impact
        elif trend == 'bearish':
            return -trend_impact
        else:
            return 0.0
    
    def _calculate_probability_from_stats(self, required_change: float, stats: Dict, 
                                        trend_adjustment: float, minutes_remaining: float) -> Dict:
        """Calculate probability using historical statistics."""
        
        # Adjust required change for trend
        adjusted_required_change = required_change - (trend_adjustment * 100)
        
        # Use normal distribution approximation
        mean_change = stats['mean_pct_change'] + trend_adjustment
        std_change = stats['std_pct_change']
        
        # Calculate probability using cumulative normal distribution
        z_score = (adjusted_required_change - mean_change) / std_change
        probability_above = 1 - self._normal_cdf(z_score)
        
        # Clamp probability to realistic bounds
        probability_above = max(0.001, min(0.999, probability_above))
        
        # Calculate expected values
        expected_value_yes = probability_above - 0.5  # Assuming 50¢ market price
        expected_value_no = (1 - probability_above) - 0.5
        
        # Determine confidence level
        if abs(required_change) < 0.1:  # Very small move needed
            confidence_level = 'VERY_HIGH'
        elif abs(required_change) < 0.5:  # Small move needed
            confidence_level = 'HIGH'
        elif abs(required_change) < 1.0:  # Moderate move needed
            confidence_level = 'MEDIUM'
        else:  # Large move needed
            confidence_level = 'LOW'
        
        # Risk assessment
        if minutes_remaining < 5:
            risk_assessment = 'EXTREME'
        elif minutes_remaining < 15:
            risk_assessment = 'HIGH'
        elif minutes_remaining < 30:
            risk_assessment = 'MEDIUM'
        else:
            risk_assessment = 'LOW'
        
        return {
            'probability_above': probability_above,
            'expected_value_yes': expected_value_yes,
            'expected_value_no': expected_value_no,
            'confidence_level': confidence_level,
            'risk_assessment': risk_assessment
        }
    
    def _normal_cdf(self, x: float) -> float:
        """Cumulative distribution function for standard normal distribution."""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    def _get_time_sensitive_recommendations(self, prob_analysis: Dict, 
                                          current_price: float, strike_price: float, 
                                          minutes_remaining: float) -> Dict:
        """Get time-sensitive betting recommendations."""
        
        prob_above = prob_analysis['probability_above']
        confidence = prob_analysis['confidence_level']
        risk = prob_analysis['risk_assessment']
        
        recommendations = {
            'action': 'HOLD',
            'confidence': 0,
            'max_safe_price_yes': 0.0,
            'max_safe_price_no': 0.0,
            'recommended_limit_yes': 0.0,
            'recommended_limit_no': 0.0,
            'urgency': 'NORMAL',
            'reasoning': []
        }
        
        # Determine action based on probability and time remaining
        if prob_above < 0.1:  # Very low probability of reaching strike
            recommendations['action'] = 'BUY_NO'
            recommendations['confidence'] = min(95, 100 - (prob_above * 100))
            # For BUY_NO, max safe price should be higher than current market price
            recommendations['max_safe_price_no'] = min(0.95, 1 - prob_above + 0.1)  # Add buffer
            recommendations['recommended_limit_no'] = recommendations['max_safe_price_no'] * 0.9
            recommendations['reasoning'].append(f"Only {prob_above*100:.1f}% chance of reaching ${strike_price:,.0f}")
            
        elif prob_above > 0.9:  # Very high probability of reaching strike
            recommendations['action'] = 'BUY_YES'
            recommendations['confidence'] = min(95, prob_above * 100)
            recommendations['max_safe_price_yes'] = min(0.95, prob_above - 0.05)
            recommendations['recommended_limit_yes'] = recommendations['max_safe_price_yes'] * 0.9
            recommendations['reasoning'].append(f"{prob_above*100:.1f}% chance of reaching ${strike_price:,.0f}")
            
        else:  # Moderate probability
            if minutes_remaining < 10:
                recommendations['action'] = 'HOLD'
                recommendations['reasoning'].append("Too close to call with high time pressure")
            else:
                if prob_above < 0.5:
                    recommendations['action'] = 'BUY_NO'
                    recommendations['confidence'] = 60
                    recommendations['max_safe_price_no'] = 0.8
                    recommendations['recommended_limit_no'] = 0.75
                else:
                    recommendations['action'] = 'BUY_YES'
                    recommendations['confidence'] = 60
                    recommendations['max_safe_price_yes'] = 0.8
                    recommendations['recommended_limit_yes'] = 0.75
        
        # Adjust for time urgency
        if minutes_remaining < 5:
            recommendations['urgency'] = 'EXTREME'
            recommendations['reasoning'].append("Less than 5 minutes remaining - act fast!")
        elif minutes_remaining < 15:
            recommendations['urgency'] = 'HIGH'
            recommendations['reasoning'].append("Less than 15 minutes remaining")
        elif minutes_remaining < 30:
            recommendations['urgency'] = 'MEDIUM'
        
        # Add specific reasoning based on required change
        required_change = (strike_price - current_price) / current_price * 100
        if abs(required_change) < 0.1:
            recommendations['reasoning'].append("Very small price movement needed")
        elif abs(required_change) < 0.5:
            recommendations['reasoning'].append("Small price movement needed")
        elif abs(required_change) < 1.0:
            recommendations['reasoning'].append("Moderate price movement needed")
        else:
            recommendations['reasoning'].append("Large price movement needed - high risk")
        
        return recommendations
    
    def _get_historical_context(self, required_change: float, timeframe: str) -> Dict:
        """Get historical context for the required price change."""
        stats = self.price_movement_stats.get(timeframe, self.price_movement_stats['15min'])
        
        context = {
            'typical_range': f"±{stats['std_pct_change']:.1f}%",
            'max_observed': f"+{stats['max_positive']:.1f}% / {stats['max_negative']:.1f}%",
            'required_change': f"{required_change:+.2f}%",
            'difficulty': 'EASY' if abs(required_change) < stats['std_pct_change'] else 'HARD'
        }
        
        if abs(required_change) > stats['max_positive']:
            context['difficulty'] = 'EXTREME'
            context['note'] = 'Required change exceeds historical maximum'
        elif abs(required_change) > stats['std_pct_change'] * 2:
            context['difficulty'] = 'VERY_HARD'
            context['note'] = 'Required change is 2+ standard deviations'
        
        return context
    
    def _get_default_analysis(self, current_price: float, strike_price: float, 
                            minutes_remaining: float) -> Dict:
        """Get default analysis when calculation fails."""
        return {
            'timeframe': '15min',
            'required_change_pct': round((strike_price - current_price) / current_price * 100, 3),
            'current_price': current_price,
            'strike_price': strike_price,
            'minutes_remaining': minutes_remaining,
            'probability_above': 0.5,
            'probability_below': 0.5,
            'expected_value_yes': 0.0,
            'expected_value_no': 0.0,
            'confidence_level': 'LOW',
            'risk_assessment': 'HIGH',
            'recommendations': {
                'action': 'HOLD',
                'confidence': 0,
                'reasoning': ['Analysis failed - use caution']
            },
            'historical_context': {'difficulty': 'UNKNOWN'}
        }
    
    def analyze_current_market_conditions(self, current_price: float, 
                                        recent_prices: List[float] = None) -> Dict:
        """Analyze current market conditions for trend detection."""
        if not recent_prices or len(recent_prices) < 3:
            return {'trend': 'neutral', 'volatility': 'normal', 'momentum': 'none'}
        
        # Calculate short-term trend
        price_change = (current_price - recent_prices[0]) / recent_prices[0] * 100
        
        if price_change > 0.5:
            trend = 'bullish'
        elif price_change < -0.5:
            trend = 'bearish'
        else:
            trend = 'neutral'
        
        # Calculate volatility
        if len(recent_prices) >= 5:
            returns = [(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] 
                      for i in range(1, len(recent_prices))]
            volatility = np.std(returns) * 100
            
            if volatility > 1.0:
                vol_level = 'high'
            elif volatility > 0.5:
                vol_level = 'normal'
            else:
                vol_level = 'low'
        else:
            vol_level = 'normal'
        
        return {
            'trend': trend,
            'volatility': vol_level,
            'momentum': 'positive' if price_change > 0 else 'negative' if price_change < 0 else 'none',
            'price_change_pct': round(price_change, 2)
        }
