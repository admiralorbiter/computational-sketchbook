#!/usr/bin/env python3
"""
Debug script to see what markets are actually available on Kalshi.
"""

import requests
import json

def get_all_markets():
    """Get all open markets from Kalshi to see what's available."""
    url = "https://api.elections.kalshi.com/trade-api/v2/markets"
    params = {"status": "open"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            markets = data.get('markets', [])
            print(f"📊 Total open markets: {len(markets)}")
            
            # Show first 10 markets
            print("\n🔍 First 10 markets:")
            for i, market in enumerate(markets[:10]):
                print(f"  {i+1}. {market.get('ticker', 'N/A')}: {market.get('title', 'N/A')}")
            
            # Look for any crypto-related markets
            crypto_keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency']
            crypto_markets = []
            
            for market in markets:
                title = market.get('title', '').lower()
                if any(keyword in title for keyword in crypto_keywords):
                    crypto_markets.append(market)
            
            print(f"\n💰 Crypto-related markets found: {len(crypto_markets)}")
            for market in crypto_markets:
                print(f"  - {market.get('ticker', 'N/A')}: {market.get('title', 'N/A')}")
                print(f"    Status: {market.get('status', 'N/A')}")
                print(f"    Yes Price: {market.get('yes_price', 'N/A')}¢")
                print(f"    Volume: {market.get('volume', 'N/A')}")
                print(f"    Close Time: {market.get('close_time', 'N/A')}")
                print()
            
            return markets
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def main():
    print("🔍 Debugging Kalshi API - What markets are available?")
    print("=" * 60)
    
    markets = get_all_markets()
    
    if markets:
        print(f"\n✅ Successfully retrieved {len(markets)} markets")
        print("\n💡 This will help us understand what markets are actually available.")
    else:
        print("\n❌ No markets retrieved. Check API connection.")

if __name__ == "__main__":
    main()
