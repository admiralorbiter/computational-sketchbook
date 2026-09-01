#!/usr/bin/env python3
"""
Check for markets in the specific crypto series we found.
"""

import requests
import json

def check_crypto_series():
    """Check for markets in crypto series."""
    print("🔍 Checking for markets in crypto series...")
    
    # The crypto series we found
    crypto_series = [
        'KXBTCD',  # Bitcoin price Above/below
        'KXETHD',  # Ethereum price Above/below
        'KXBTC',   # Bitcoin range
        'KXETH',   # Ethereum range
        'KXBTCMAXY',  # How high will Bitcoin get this year?
        'KXETHMAXY',  # How high will Ethereum get this year?
        'KXBTCMINY',  # How low will Bitcoin fall this year?
        'KXETHMINY',  # How low will Ethereum fall this year?
    ]
    
    for series_ticker in crypto_series:
        print(f"\n📊 Checking series: {series_ticker}")
        
        try:
            # Get markets for this specific series
            url = f"https://api.elections.kalshi.com/trade-api/v2/markets"
            params = {
                "status": "open",
                "series_ticker": series_ticker
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                markets = data.get('markets', [])
                print(f"  ✅ Found {len(markets)} open markets")
                
                if markets:
                    for market in markets:
                        print(f"    📈 {market.get('ticker')}: {market.get('title')}")
                        print(f"       Yes Price: {market.get('yes_price', 'N/A')}¢")
                        print(f"       Volume: {market.get('volume', 'N/A')}")
                        print(f"       Close Time: {market.get('close_time', 'N/A')}")
                else:
                    print(f"    ❌ No open markets in {series_ticker}")
                    
                    # Check if there are closed markets
                    closed_params = {
                        "status": "closed",
                        "series_ticker": series_ticker
                    }
                    closed_response = requests.get(url, params=closed_params, timeout=10)
                    
                    if closed_response.status_code == 200:
                        closed_data = closed_response.json()
                        closed_markets = closed_data.get('markets', [])
                        print(f"    📊 Found {len(closed_markets)} closed markets")
                        
                        if closed_markets:
                            print(f"    📋 Recent closed markets:")
                            for market in closed_markets[:3]:  # Show first 3
                                print(f"      - {market.get('ticker')}: {market.get('title')}")
            else:
                print(f"  ❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error checking {series_ticker}: {e}")

def check_all_statuses():
    """Check markets in all possible statuses."""
    print("\n🔍 Checking all market statuses for crypto series...")
    
    statuses = ['open', 'closed', 'resolved', 'paused']
    crypto_series = ['KXBTCD', 'KXETHD', 'KXBTC', 'KXETH']
    
    for series_ticker in crypto_series:
        print(f"\n📊 Series: {series_ticker}")
        
        for status in statuses:
            try:
                url = f"https://api.elections.kalshi.com/trade-api/v2/markets"
                params = {
                    "status": status,
                    "series_ticker": series_ticker
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    markets = data.get('markets', [])
                    print(f"  {status}: {len(markets)} markets")
                    
                    if markets and len(markets) <= 3:  # Show details if few markets
                        for market in markets:
                            print(f"    - {market.get('ticker')}: {market.get('title')}")
                else:
                    print(f"  {status}: API Error {response.status_code}")
                    
            except Exception as e:
                print(f"  {status}: Error - {e}")

def main():
    print("🚀 Checking Crypto Series for Markets")
    print("=" * 50)
    
    check_crypto_series()
    check_all_statuses()
    
    print("\n💡 If no open markets found, this explains why the app shows mock data.")
    print("   The series exist but may not have active markets right now.")

if __name__ == "__main__":
    main()
