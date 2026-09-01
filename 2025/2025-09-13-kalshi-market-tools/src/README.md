# Kalshi Trade Helper (Flask + Bootstrap)

Tiny Flask app to help evaluate trades for:
- **Sports (live in-game)** — toy NFL/NBA win probability estimator → fees, EV, Kelly.
- **BTC/ETH & NASDAQ‑100 above/below** — GBM-based `p(up)` → fees, EV, Kelly with **real-time data**.
- **Fee calculator** — product-aware (general, sports maker-fee series, NASDAQ100/SPX reduced taker).
- **Live Kalshi Markets** — Real-time BTC/ETH hourly market data and order book information.

> **Disclaimer:** Educational demo only. Replace toy sports models with calibrated ones before trading. Fees/terms can change; verify against the current schedule and product rule pages.

## 🚀 New Features

- **Real-time Market Data**: Live BTC/ETH prices from Coinbase, Kraken, and Binance APIs
- **Kalshi Integration**: Actual BTC/ETH hourly market data and order book information
- **Auto-refresh**: Market data updates automatically every 30-60 seconds
- **Fallback Handling**: Graceful degradation when APIs are unavailable

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
flask run
# then open http://127.0.0.1:5000
```

## Pages

- `/fees` — compute entry fee given price, role (maker/taker), and product type.
- `/kelly` — fee-aware Kelly sizing and EV (hold-to-settlement).
- `/prices` — estimate probability of finishing **above** a strike (GBM shortcut) for BTC/ETH/NDX; then evaluate fees/EV/Kelly with **real-time data**.
- `/kalshi-markets` — view live Kalshi BTC/ETH hourly markets with order book data.
- `/sports` — quick in-game helper for NFL/NBA; **toy** WP model for UI; replace with your model.

## Data Sources

- **Crypto Prices**: Coinbase Advanced Trade API, Kraken API, Binance.US API
- **Kalshi Markets**: Kalshi public market data API for BTC/ETH hourly markets (no authentication required)
- **NASDAQ-100**: Currently uses mock data (implement real NASDAQ data source as needed)

## Where to plug your models

- Replace functions in `utils/sports.py` with calibrated NFL/NBA WP models (e.g., based on play-by-play features).
- Implement real NASDAQ-100 data source in `utils/market_data.py` (currently mocked).
- Add additional crypto exchanges by extending `MarketDataService` class.

## Notes on fees (encode current schedule yourself)
- General taker: `0.07 * C * P * (1 - P)` (rounded up to next cent).
- NASDAQ100/SPX taker: **half** that (`0.035 * C * P * (1 - P)`).
- Maker (sports maker-fee series): `0.0175 * C * P * (1 - P)` when your resting order fills.
- Non-maker-fee series makers: typically **$0** to post; verify per product.

## Tests

A tiny sanity test for fees lives in `tests/test_fees.py` (needs `pytest`).

```bash
pip install -r requirements.txt
pytest -q
```

## Security

- This app uses a dev `SECRET_KEY`. Set a strong secret if you deploy beyond local testing.
- No credentials or trading actions are included; this is a sandboxed calculator.
```

