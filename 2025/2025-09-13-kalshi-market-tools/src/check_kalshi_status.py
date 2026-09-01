#!/usr/bin/env python3
"""
Check what markets are actually available on Kalshi right now.
"""

import requests
import json

def check_kalshi_markets():
    """Check what markets are available on Kalshi."""
    print("🔍 Checking Kalshi API status...")
    
    try:
        # Get all open markets
        url = "https://api.elections.kalshi.com/trade-api/v2/markets"
        params = {"status": "open"}
        
        response = requests.get(url, params=params, timeout=10)
        print(f"✅ API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('markets', [])
            print(f"📊 Total open markets: {len(markets)}")
            
            # Look for crypto-related markets
            crypto_keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto']
            crypto_markets = []
            
            for market in markets:
                title = market.get('title', '').lower()
                if any(keyword in title for keyword in crypto_keywords):
                    crypto_markets.append(market)
            
            print(f"💰 Crypto markets found: {len(crypto_markets)}")
            
            if crypto_markets:
                print("\n📈 Available crypto markets:")
                for market in crypto_markets:
                    print(f"  - {market.get('ticker')}: {market.get('title')}")
            else:
                print("\n❌ No crypto markets currently available on Kalshi")
                print("💡 This means:")
                print("   • No Bitcoin/Ethereum prediction markets are active right now")
                print("   • They might be temporarily unavailable")
                print("   • They might use different naming conventions")
            
            # Show what types of markets ARE available
            print(f"\n📋 Sample of available markets:")
            for i, market in enumerate(markets[:5]):
                print(f"  {i+1}. {market.get('ticker')}: {market.get('title')}")
            
            return len(crypto_markets) > 0
            
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Kalshi Market Status Check")
    print("=" * 40)
    
    has_crypto = check_kalshi_markets()
    
    if not has_crypto:
        print("\n🔧 Solutions:")
        print("1. The app will show mock Kalshi data for demonstration")
        print("2. Real-time crypto prices still work from other APIs")
        print("3. You can still use the probability calculator with real prices")
        print("4. Check back later - crypto markets may become available")

if __name__ == "__main__":
    main()
