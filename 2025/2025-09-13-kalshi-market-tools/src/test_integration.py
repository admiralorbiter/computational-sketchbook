#!/usr/bin/env python3
"""
Simple test script to verify the real-time data integration works.
Run this to test the API connections before using the Flask app.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_fetcher import data_fetcher

def test_market_data():
    """Test the market data integration."""
    print("Testing real-time market data integration...")
    print("=" * 50)
    
    try:
        # Test crypto prices
        print("Fetching crypto prices...")
        crypto_prices = data_fetcher.get_crypto_prices()
        
        for symbol, price_data in crypto_prices.items():
            if price_data:
                print(f"{symbol}: ${price_data.price:.2f} ({price_data.source})")
            else:
                print(f"{symbol}: No data available")
        
        print("\nFetching NASDAQ price...")
        nasdaq_price = data_fetcher.get_nasdaq_price()
        if nasdaq_price:
            print(f"NASDAQ-100: ${nasdaq_price.price:.2f} ({nasdaq_price.source})")
        else:
            print("NASDAQ-100: No data available")
        
        print("\nFetching Kalshi BTC/ETH hourly markets...")
        kalshi_data = data_fetcher.kalshi_service.get_relevant_markets()
        
        print(f"BTC hourly markets found: {len(kalshi_data.get('btc_hourly', []))}")
        print(f"ETH hourly markets found: {len(kalshi_data.get('eth_hourly', []))}")
        
        # Show first few markets
        if kalshi_data.get('btc_hourly'):
            print("\nFirst BTC hourly market:")
            first_btc = kalshi_data['btc_hourly'][0]
            print(f"  Ticker: {first_btc.get('ticker', 'N/A')}")
            print(f"  Title: {first_btc.get('title', 'N/A')}")
            print(f"  Mid Price: {first_btc.get('yes_mid', 'N/A')}")
        
        if kalshi_data.get('eth_hourly'):
            print("\nFirst ETH hourly market:")
            first_eth = kalshi_data['eth_hourly'][0]
            print(f"  Ticker: {first_eth.get('ticker', 'N/A')}")
            print(f"  Title: {first_eth.get('title', 'N/A')}")
            print(f"  Mid Price: {first_eth.get('yes_mid', 'N/A')}")
        
        print("\n✅ Integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_market_data()
