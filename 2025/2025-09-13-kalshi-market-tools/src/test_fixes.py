#!/usr/bin/env python3
"""
Test script to verify the fixes work.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic functionality without external APIs."""
    print("🧪 Testing basic functionality...")
    
    try:
        from utils.data_fetcher import data_fetcher
        
        print("✅ Data fetcher imported successfully")
        
        # Test crypto prices (should work with fallbacks)
        print("\n📊 Testing crypto prices...")
        crypto_prices = data_fetcher.get_crypto_prices()
        
        for symbol, price_data in crypto_prices.items():
            if price_data:
                print(f"  {symbol}: ${price_data.price:.2f} ({price_data.source})")
            else:
                print(f"  {symbol}: No data")
        
        # Test NASDAQ price
        print("\n📈 Testing NASDAQ price...")
        nasdaq_price = data_fetcher.get_nasdaq_price()
        if nasdaq_price:
            print(f"  NASDAQ-100: ${nasdaq_price.price:.2f} ({nasdaq_price.source})")
        else:
            print("  NASDAQ-100: No data")
        
        # Test market summary
        print("\n📋 Testing market summary...")
        market_summary = data_fetcher.get_market_summary()
        print(f"  Timestamp: {market_summary.get('timestamp', 'N/A')}")
        print(f"  BTC price available: {'BTC' in market_summary.get('crypto_prices', {})}")
        print(f"  ETH price available: {'ETH' in market_summary.get('crypto_prices', {})}")
        
        print("\n✅ Basic functionality test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_app():
    """Test if Flask app can start."""
    print("\n🌐 Testing Flask app startup...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test main page
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Main page loads successfully")
            else:
                print(f"❌ Main page failed: {response.status_code}")
                return False
            
            # Test prices page
            response = client.get('/prices')
            if response.status_code == 200:
                print("✅ Prices page loads successfully")
            else:
                print(f"❌ Prices page failed: {response.status_code}")
                return False
            
            # Test API endpoint
            response = client.get('/api/market-data')
            if response.status_code == 200:
                print("✅ API endpoint works")
                data = response.get_json()
                print(f"  Response keys: {list(data.keys())}")
            else:
                print(f"❌ API endpoint failed: {response.status_code}")
                return False
        
        print("✅ Flask app test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 Running Fix Verification Tests")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    if test_basic_functionality():
        tests_passed += 1
    
    if test_flask_app():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The app should work now.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
