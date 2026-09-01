# Usage Example

## Testing the Integration

Before running the Flask app, you can test the data integration:

```bash
cd kalshi_flask_app
python test_integration.py
```

This will test all API connections and show you what data is available.

## Running the App

```bash
cd kalshi_flask_app
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Using Real-time Data

1. **Go to the BTC/ETH/NDX Probability page** (`/prices`)
2. **Select your symbol** (BTC, ETH, or NASDAQ-100)
3. **Check "Use Real-time Price"** to auto-fill current market price
4. **Enter your strike price** and other parameters
5. **Click "Estimate & Evaluate"** to get probability and Kelly sizing

## Viewing Kalshi Markets

1. **Go to the Kalshi Markets page** (`/kalshi-markets`)
2. **View live market data** for BTC and ETH hourly markets
3. **See bid/ask spreads** and trading volumes for hourly predictions
4. **Use this data** to inform your probability calculations for hourly trades

## Testing Kalshi API Directly

You can test the Kalshi API directly using the example script:

```bash
cd kalshi_flask_app
python kalshi_example.py
```

This will search for and display BTC/ETH hourly markets from Kalshi.

## API Endpoints

- `/api/market-data` - JSON endpoint for real-time market data
- `/kalshi-markets` - HTML page showing Kalshi market data
- `/prices` - Main probability calculator with real-time data integration

## Troubleshooting

If you see "No data available" messages:

1. **Check your internet connection**
2. **Verify API endpoints are accessible** (some may be rate-limited)
3. **Check the console logs** for specific error messages
4. **Try the test script** to diagnose issues

The app includes fallback mechanisms, so it will still work even if some APIs are unavailable.
