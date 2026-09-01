#!/usr/bin/env python3
"""
Comprehensive search for Bitcoin and Ethereum markets on Kalshi.
Based on the fact that Kalshi has been offering BTC/ETH markets since March 2024.
"""

import requests
import json
import re
from datetime import datetime

def search_all_markets_comprehensive():
    """Search comprehensively for crypto markets on Kalshi."""
    print("🔍 Comprehensive search for Bitcoin/Ethereum markets on Kalshi...")
    print("=" * 70)
    
    try:
        # Get all open markets
        url = "https://api.elections.kalshi.com/trade-api/v2/markets"
        params = {"status": "open"}
        
        response = requests.get(url, params=params, timeout=15)
        print(f"✅ API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('markets', [])
            print(f"📊 Total open markets: {len(markets)}")
            
            # Comprehensive search terms for crypto
            crypto_patterns = [
                # Bitcoin patterns
                r'bitcoin', r'btc', r'bit coin',
                # Ethereum patterns  
                r'ethereum', r'eth', r'ether',
                # General crypto patterns
                r'crypto', r'cryptocurrency', r'digital currency',
                # Price-related patterns
                r'price.*above', r'price.*below', r'above.*price', r'below.*price',
                # Time patterns
                r'hourly', r'daily', r'weekly', r'end.*hour', r'end.*day',
                # Dollar amount patterns
                r'\$[0-9,]+', r'[0-9,]+k', r'[0-9,]+ thousand'
            ]
            
            found_markets = []
            
            print("\n🔍 Searching through all markets...")
            for i, market in enumerate(markets):
                title = market.get('title', '').lower()
                ticker = market.get('ticker', '').lower()
                series = market.get('series_ticker', '').lower()
                
                # Check all patterns
                for pattern in crypto_patterns:
                    if re.search(pattern, title) or re.search(pattern, ticker) or re.search(pattern, series):
                        found_markets.append((market, pattern))
                        break
                
                # Progress indicator
                if (i + 1) % 20 == 0:
                    print(f"  Processed {i + 1}/{len(markets)} markets...")
            
            print(f"\n💰 Found {len(found_markets)} potential crypto-related markets:")
            
            if found_markets:
                for market, matched_pattern in found_markets:
                    print(f"\n📈 Market: {market.get('ticker', 'N/A')}")
                    print(f"   Title: {market.get('title', 'N/A')}")
                    print(f"   Series: {market.get('series_ticker', 'N/A')}")
                    print(f"   Matched: '{matched_pattern}'")
                    print(f"   Status: {market.get('status', 'N/A')}")
                    print(f"   Yes Price: {market.get('yes_price', 'N/A')}¢")
                    print(f"   Volume: {market.get('volume', 'N/A')}")
                    print(f"   Close Time: {market.get('close_time', 'N/A')}")
                    print(f"   Open Interest: {market.get('open_interest', 'N/A')}")
            else:
                print("\n❌ No crypto markets found with current search patterns")
                
                # Let's look at what types of markets ARE available
                print("\n📋 Sample of available market titles:")
                for i, market in enumerate(markets[:10]):
                    print(f"  {i+1}. {market.get('title', 'N/A')}")
                
                # Check for any markets with numbers (potential price markets)
                number_markets = []
                for market in markets:
                    title = market.get('title', '')
                    if re.search(r'\$[0-9]', title) or re.search(r'[0-9]+k', title):
                        number_markets.append(market)
                        if len(number_markets) >= 5:
                            break
                
                if number_markets:
                    print(f"\n💰 Markets with price-like numbers:")
                    for market in number_markets:
                        print(f"  - {market.get('ticker')}: {market.get('title')}")
            
            return found_markets
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def check_series_endpoints():
    """Check if there are specific series endpoints for crypto."""
    print("\n🔍 Checking for crypto-specific series...")
    
    try:
        # Try to get series information
        series_url = "https://api.elections.kalshi.com/trade-api/v2/series"
        response = requests.get(series_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            series_list = data.get('series', [])
            print(f"📊 Found {len(series_list)} series")
            
            # Look for crypto-related series
            crypto_series = []
            for series in series_list:
                title = series.get('title', '').lower()
                ticker = series.get('ticker', '').lower()
                
                if any(term in title or term in ticker for term in ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto']):
                    crypto_series.append(series)
            
            if crypto_series:
                print(f"\n💰 Crypto-related series found:")
                for series in crypto_series:
                    print(f"  - {series.get('ticker')}: {series.get('title')}")
            else:
                print("\n❌ No crypto-related series found")
                
                # Show some sample series
                print(f"\n📋 Sample series (first 10):")
                for i, series in enumerate(series_list[:10]):
                    print(f"  {i+1}. {series.get('ticker')}: {series.get('title')}")
        else:
            print(f"❌ Series API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Series check error: {e}")

def main():
    print("🚀 Comprehensive Kalshi Crypto Market Search")
    print("Based on: Kalshi has offered BTC/ETH markets since March 2024")
    print("=" * 70)
    
    # Search all markets
    markets = search_all_markets_comprehensive()
    
    # Check series endpoints
    check_series_endpoints()
    
    if not markets:
        print("\n🤔 Possible reasons no crypto markets found:")
        print("1. Markets might be in 'closed' status instead of 'open'")
        print("2. Different naming conventions than expected")
        print("3. Markets might be in different categories")
        print("4. API might require different parameters")
        
        print("\n🔄 Let's try searching closed markets too...")
        try:
            closed_url = "https://api.elections.kalshi.com/trade-api/v2/markets"
            closed_params = {"status": "closed"}
            closed_response = requests.get(closed_url, params=closed_params, timeout=10)
            
            if closed_response.status_code == 200:
                closed_data = closed_response.json()
                closed_markets = closed_data.get('markets', [])
                print(f"📊 Found {len(closed_markets)} closed markets")
                
                # Quick search in closed markets
                crypto_closed = []
                for market in closed_markets[:50]:  # Check first 50
                    title = market.get('title', '').lower()
                    if any(term in title for term in ['bitcoin', 'btc', 'ethereum', 'eth']):
                        crypto_closed.append(market)
                
                if crypto_closed:
                    print(f"💰 Found {len(crypto_closed)} crypto markets in closed status:")
                    for market in crypto_closed:
                        print(f"  - {market.get('ticker')}: {market.get('title')}")
                else:
                    print("❌ No crypto markets in closed status either")
        except Exception as e:
            print(f"❌ Closed markets check error: {e}")

if __name__ == "__main__":
    main()
