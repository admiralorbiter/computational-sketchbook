#!/usr/bin/env python3
"""
Example script showing how to use the Kalshi API directly for BTC/ETH hourly markets.
Based on the official Kalshi documentation: https://docs.kalshi.com/getting_started/quick_start_market_data
"""

import requests
import json
from datetime import datetime

def search_kalshi_markets(search_term, status="open"):
    """Search for markets using the Kalshi API."""
    url = "https://api.elections.kalshi.com/trade-api/v2/markets"
    params = {
        "status": status,
        "search": search_term
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def get_market_orderbook(ticker):
    """Get orderbook for a specific market."""
    url = f"https://api.elections.kalshi.com/trade-api/v2/markets/{ticker}/orderbook"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Orderbook API Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching orderbook: {e}")
        return None

def find_hourly_markets(crypto_name):
    """Find hourly markets for a specific crypto."""
    print(f"\n🔍 Searching for {crypto_name} hourly markets...")
    
    # Search terms to try
    search_terms = [
        crypto_name,
        f"hourly {crypto_name}",
        f"per hour {crypto_name}",
        f"each hour {crypto_name}"
    ]
    
    all_markets = []
    for term in search_terms:
        print(f"  Searching: '{term}'")
        data = search_kalshi_markets(term)
        if data and 'markets' in data:
            markets = data['markets']
            # Filter for hourly markets
            hourly_markets = [
                m for m in markets 
                if any(keyword in m.get('title', '').lower() 
                      for keyword in ['hourly', 'per hour', 'each hour', 'every hour'])
            ]
            all_markets.extend(hourly_markets)
            print(f"    Found {len(hourly_markets)} hourly markets")
    
    # Remove duplicates
    seen_tickers = set()
    unique_markets = []
    for market in all_markets:
        ticker = market.get('ticker', '')
        if ticker not in seen_tickers:
            seen_tickers.add(ticker)
            unique_markets.append(market)
    
    return unique_markets

def display_market_info(market):
    """Display information about a market."""
    print(f"\n📊 Market: {market.get('ticker', 'N/A')}")
    print(f"   Title: {market.get('title', 'N/A')}")
    print(f"   Status: {market.get('status', 'N/A')}")
    print(f"   Yes Price: {market.get('yes_price', 'N/A')}¢")
    print(f"   Volume: {market.get('volume', 'N/A')}")
    print(f"   Open Interest: {market.get('open_interest', 'N/A')}")
    
    # Get orderbook data
    ticker = market.get('ticker', '')
    if ticker:
        orderbook = get_market_orderbook(ticker)
        if orderbook and 'orderbook' in orderbook:
            ob = orderbook['orderbook']
            print(f"   Orderbook:")
            if 'yes' in ob and ob['yes']:
                print(f"     Yes Bids: {ob['yes'][:3]}")  # Top 3 bids
            if 'no' in ob and ob['no']:
                print(f"     No Bids: {ob['no'][:3]}")    # Top 3 bids

def main():
    """Main function to demonstrate Kalshi API usage."""
    print("🚀 Kalshi API Example - BTC/ETH Hourly Markets")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Search for BTC hourly markets
    btc_markets = find_hourly_markets("bitcoin")
    print(f"\n✅ Found {len(btc_markets)} BTC hourly markets")
    
    # Search for ETH hourly markets  
    eth_markets = find_hourly_markets("ethereum")
    print(f"\n✅ Found {len(eth_markets)} ETH hourly markets")
    
    # Display first few markets
    print(f"\n📈 BTC Hourly Markets:")
    for i, market in enumerate(btc_markets[:3]):  # Show first 3
        display_market_info(market)
        if i < len(btc_markets) - 1:
            print("-" * 30)
    
    print(f"\n📈 ETH Hourly Markets:")
    for i, market in enumerate(eth_markets[:3]):  # Show first 3
        display_market_info(market)
        if i < len(eth_markets) - 1:
            print("-" * 30)
    
    print(f"\n🎯 Summary:")
    print(f"   Total BTC hourly markets: {len(btc_markets)}")
    print(f"   Total ETH hourly markets: {len(eth_markets)}")
    print(f"\n💡 Use these market tickers in the Flask app for real-time data!")

if __name__ == "__main__":
    main()
