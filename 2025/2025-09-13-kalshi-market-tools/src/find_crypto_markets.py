#!/usr/bin/env python3
"""
Find any crypto-related markets on Kalshi.
"""

import requests
import json

def search_all_markets():
    """Search through all markets to find crypto-related ones."""
    url = "https://api.elections.kalshi.com/trade-api/v2/markets"
    params = {"status": "open"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            markets = data.get('markets', [])
            
            print(f"📊 Searching through {len(markets)} open markets...")
            
            # Look for various crypto-related terms
            crypto_terms = [
                'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency',
                'coin', 'digital', 'blockchain', 'price', 'above', 'below',
                'hourly', 'daily', 'weekly', 'monthly'
            ]
            
            found_markets = []
            
            for market in markets:
                title = market.get('title', '').lower()
                ticker = market.get('ticker', '').lower()
                
                # Check if any crypto terms are in title or ticker
                for term in crypto_terms:
                    if term in title or term in ticker:
                        found_markets.append((market, term))
                        break
            
            print(f"\n🔍 Found {len(found_markets)} markets with crypto-related terms:")
            
            for market, matched_term in found_markets:
                print(f"\n📈 Market: {market.get('ticker', 'N/A')}")
                print(f"   Title: {market.get('title', 'N/A')}")
                print(f"   Matched term: '{matched_term}'")
                print(f"   Status: {market.get('status', 'N/A')}")
                print(f"   Yes Price: {market.get('yes_price', 'N/A')}¢")
                print(f"   Volume: {market.get('volume', 'N/A')}")
                print(f"   Close Time: {market.get('close_time', 'N/A')}")
                print(f"   Series: {market.get('series_ticker', 'N/A')}")
            
            # Also check for any markets with "price" in the title
            price_markets = []
            for market in markets:
                title = market.get('title', '').lower()
                if 'price' in title and len(price_markets) < 5:  # Limit to first 5
                    price_markets.append(market)
            
            if price_markets:
                print(f"\n💰 Markets with 'price' in title (first 5):")
                for market in price_markets:
                    print(f"  - {market.get('ticker', 'N/A')}: {market.get('title', 'N/A')}")
            
            return found_markets
            
        else:
            print(f"❌ API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def main():
    print("🔍 Searching for ANY crypto-related markets on Kalshi...")
    print("=" * 60)
    
    markets = search_all_markets()
    
    if not markets:
        print("\n❌ No crypto-related markets found.")
        print("💡 This might mean:")
        print("   - No crypto markets are currently active")
        print("   - They use different naming conventions")
        print("   - They're in a different category")
        print("\n🔄 Let's check what types of markets ARE available...")
        
        # Show market categories
        url = "https://api.elections.kalshi.com/trade-api/v2/markets"
        params = {"status": "open"}
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                markets = data.get('markets', [])
                
                # Group by series
                series_count = {}
                for market in markets:
                    series = market.get('series_ticker', 'Unknown')
                    series_count[series] = series_count.get(series, 0) + 1
                
                print(f"\n📊 Available market series (showing top 10):")
                sorted_series = sorted(series_count.items(), key=lambda x: x[1], reverse=True)
                for series, count in sorted_series[:10]:
                    print(f"  {series}: {count} markets")

if __name__ == "__main__":
    main()
