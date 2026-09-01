from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

from flask import Flask, render_template, request, redirect, url_for, flash

from utils.fees import compute_fee, FeeInput, ProductType, Role, round_up_cent
from utils.probs import digital_up_probability
from utils.sports import estimate_wp_nfl_toy, estimate_wp_nba_toy
from utils.kelly import fee_adjusted_kelly, ev_hold_to_settlement
from utils.data_fetcher import data_fetcher

# --- Flask app setup ---
app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-change-me"  # replace in production


# --- Helpers ---
def parse_float(name: str, default: Optional[float] = None) -> Optional[float]:
    raw = request.form.get(name, "").strip()
    if raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def parse_int(name: str, default: Optional[int] = None) -> Optional[int]:
    raw = request.form.get(name, "").strip()
    if raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/market-data")
def market_data():
    """API endpoint for real-time market data."""
    try:
        market_summary = data_fetcher.get_market_summary()
        return market_summary
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/kalshi-markets")
def kalshi_markets():
    """Display Kalshi markets for BTC/ETH with betting analysis."""
    try:
        # Get bankroll from query parameter, default to 1000
        bankroll = request.args.get('bankroll', 1000, type=float)
        if bankroll < 100:
            bankroll = 1000  # Minimum bankroll
        
        # Get Bitcoin analysis for enhanced recommendations
        bitcoin_analysis = None
        try:
            from utils.bitcoin_analyzer import BitcoinAnalyzer
            analyzer = BitcoinAnalyzer()
            bitcoin_analysis = analyzer.get_comprehensive_analysis()
        except Exception as e:
            print(f"Warning: Could not load Bitcoin analysis: {e}")
            bitcoin_analysis = None
        
        kalshi_data = data_fetcher.get_kalshi_markets_with_analysis(bankroll=bankroll, bitcoin_analysis=bitcoin_analysis)
        
        return render_template("kalshi_markets.html", 
                             kalshi_data=kalshi_data, 
                             user_bankroll=bankroll,
                             bitcoin_analysis=bitcoin_analysis)
    except Exception as e:
        flash(f"Error loading Kalshi markets: {e}", "danger")
        return render_template("kalshi_markets.html", kalshi_data={"btc_daily": [], "eth_daily": [], "timestamp": "Error"}, user_bankroll=1000, bitcoin_analysis=None)


@app.route("/fees", methods=["GET", "POST"])
def fees():
    result = None
    if request.method == "POST":
        try:
            price = parse_float("price", None)
            contracts = parse_int("contracts", 1) or 1
            role = request.form.get("role", "taker")
            product_type = request.form.get("product_type", "general")

            if price is None or not (0.0 < price < 1.0):
                flash("Enter a valid price between 0 and 1 (e.g., 0.55).", "warning")
                return render_template("fees.html", result=None)

            fee_in = compute_fee(
                FeeInput(price=price, contracts=contracts),
                role=Role(role),
                product_type=ProductType(product_type)
            )
            result = {
                "price": price,
                "contracts": contracts,
                "role": role,
                "product_type": product_type,
                "fee_total": fee_in,
                "fee_per_contract": fee_in / max(contracts, 1),
            }
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template("fees.html", result=result)


@app.route("/kelly", methods=["GET", "POST"])
def kelly():
    result = None
    if request.method == "POST":
        try:
            p_star = parse_float("p_star", None)
            price = parse_float("price", None)
            bankroll = parse_float("bankroll", None)
            contracts = parse_int("contracts", 1) or 1
            role = request.form.get("role", "taker")
            product_type = request.form.get("product_type", "general")

            if p_star is None or not (0.0 <= p_star <= 1.0):
                flash("Enter a valid model probability p* between 0 and 1.", "warning")
                return render_template("kelly.html", result=None)
            if price is None or not (0.0 < price < 1.0):
                flash("Enter a valid Kalshi price between 0 and 1.", "warning")
                return render_template("kelly.html", result=None)
            if bankroll is None or bankroll <= 0:
                flash("Enter a positive bankroll (in dollars).", "warning")
                return render_template("kelly.html", result=None)

            fee_in = compute_fee(
                FeeInput(price=price, contracts=contracts),
                role=Role(role),
                product_type=ProductType(product_type),
            )
            k_full, k_half, c_eff = fee_adjusted_kelly(p_star, price, fee_in/contracts)
            ev = ev_hold_to_settlement(p_star, price, fee_in/contracts)
            # Suggested contracts: half-kelly on bankroll, respecting $1 max payoff
            # Each contract risks c_eff dollars; suggested size = k_half * bankroll / c_eff
            suggested = 0
            if c_eff > 0:
                suggested = math.floor(max(0.0, k_half * bankroll / c_eff))

            result = {
                "p_star": p_star,
                "price": price,
                "bankroll": bankroll,
                "contracts": contracts,
                "role": role,
                "product_type": product_type,
                "fee_total": fee_in,
                "fee_per_contract": fee_in / contracts,
                "kelly_full": k_full,
                "kelly_half": k_half,
                "c_eff": c_eff,
                "ev_per_contract": ev,
                "suggested_contracts": suggested,
            }
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template("kelly.html", result=result)


@app.route("/prices", methods=["GET", "POST"])
def prices():
    result = None
    market_data = None
    
    # Get real-time market data
    try:
        market_data = data_fetcher.get_market_summary()
    except Exception as e:
        flash(f"Warning: Could not fetch real-time data: {e}", "warning")
    
    if request.method == "POST":
        try:
            # Get symbol and use real-time price if available
            symbol = request.form.get("symbol", "BTC")
            use_realtime = request.form.get("use_realtime") == "on"
            
            if use_realtime and market_data:
                # Use real-time price
                if symbol == "BTC" and market_data["crypto_prices"]["BTC"]:
                    S = market_data["crypto_prices"]["BTC"].price
                elif symbol == "ETH" and market_data["crypto_prices"]["ETH"]:
                    S = market_data["crypto_prices"]["ETH"].price
                elif symbol == "NDX" and market_data["nasdaq_price"]:
                    S = market_data["nasdaq_price"].price
                else:
                    S = parse_float("S")
            else:
                S = parse_float("S")
            
            # If S is still None and we have real-time data, use it as fallback
            if S is None and market_data:
                if symbol == "BTC" and market_data["crypto_prices"]["BTC"]:
                    S = market_data["crypto_prices"]["BTC"].price
                elif symbol == "ETH" and market_data["crypto_prices"]["ETH"]:
                    S = market_data["crypto_prices"]["ETH"].price
                elif symbol == "NDX" and market_data["nasdaq_price"]:
                    S = market_data["nasdaq_price"].price
            
            K = parse_float("K")
            minutes = parse_float("minutes")
            sigma_annual = parse_float("sigma")
            price = parse_float("price")
            contracts = parse_int("contracts", 1) or 1

            role = request.form.get("role", "taker")
            product_type = request.form.get("product_type", "general")

            if None in (S, K, minutes, sigma_annual, price):
                flash("Please fill all numeric fields.", "warning")
                return render_template("prices.html", result=None, market_data=market_data)

            # Convert minutes to years
            T_years = max(0.0, minutes) / (365.0 * 24.0 * 60.0)
            p_up = digital_up_probability(S=S, K=K, sigma=sigma_annual, T_years=T_years)

            fee_in = compute_fee(
                FeeInput(price=price, contracts=contracts),
                role=Role(role),
                product_type=ProductType(product_type),
            )
            # EV & Kelly on this p*
            k_full, k_half, c_eff = fee_adjusted_kelly(p_up, price, fee_in/contracts)
            ev = ev_hold_to_settlement(p_up, price, fee_in/contracts)

            result = {
                "symbol": symbol,
                "S": S, "K": K, "minutes": minutes, "sigma": sigma_annual,
                "T_years": T_years, "p_up": p_up,
                "price": price, "contracts": contracts,
                "role": role, "product_type": product_type,
                "fee_total": fee_in, "fee_per_contract": fee_in/contracts,
                "kelly_full": k_full, "kelly_half": k_half, "c_eff": c_eff,
                "ev_per_contract": ev,
                "use_realtime": use_realtime
            }
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template("prices.html", result=result, market_data=market_data)


@app.route("/bitcoin-analysis")
def bitcoin_analysis():
    """Display Bitcoin price analysis with technical indicators."""
    try:
        from utils.bitcoin_analyzer import BitcoinAnalyzer
        analyzer = BitcoinAnalyzer()
        analysis_data = analyzer.get_comprehensive_analysis()
        return render_template("bitcoin_analysis.html", analysis=analysis_data)
    except Exception as e:
        flash(f"Error loading Bitcoin analysis: {e}", "danger")
        return render_template("bitcoin_analysis.html", analysis={"error": str(e)})


@app.route("/sports", methods=["GET", "POST"])
def sports():
    result = None
    if request.method == "POST":
        try:
            league = request.form.get("league", "NFL")
            # Inputs common
            price = parse_float("price")
            contracts = parse_int("contracts", 1) or 1
            role = request.form.get("role", "maker")
            product_type = request.form.get("product_type", "sports")

            # Sports state
            margin = parse_int("margin", 0) or 0  # Team A minus Team B
            minutes_remaining = parse_float("minutes_remaining", 15.0) or 0.0
            possession = request.form.get("possession", "none")
            pre_spread = parse_float("pre_spread", 0.0) or 0.0  # Team A spread (negative means favored)

            if price is None or not (0.0 < price < 1.0):
                flash("Enter a valid Kalshi price between 0 and 1.", "warning")
                return render_template("sports.html", result=None)

            # Estimate WP (toy). For production, plug in a calibrated model.
            if league == "NFL":
                p_star = estimate_wp_nfl_toy(
                    margin=margin,
                    minutes_remaining=minutes_remaining,
                    possession_flag=(1 if possession == "A" else (-1 if possession == "B" else 0)),
                    pregame_spread=pre_spread
                )
            else:
                p_star = estimate_wp_nba_toy(
                    margin=margin,
                    minutes_remaining=minutes_remaining,
                    possession_flag=(1 if possession == "A" else (-1 if possession == "B" else 0)),
                    pregame_spread=pre_spread
                )

            fee_in = compute_fee(
                FeeInput(price=price, contracts=contracts),
                role=Role(role),
                product_type=ProductType(product_type),
            )
            k_full, k_half, c_eff = fee_adjusted_kelly(p_star, price, fee_in/contracts)
            ev = ev_hold_to_settlement(p_star, price, fee_in/contracts)

            result = {
                "league": league,
                "p_star": p_star,
                "price": price,
                "contracts": contracts,
                "role": role,
                "product_type": product_type,
                "fee_total": fee_in,
                "fee_per_contract": fee_in / contracts,
                "kelly_full": k_full,
                "kelly_half": k_half,
                "c_eff": c_eff,
                "ev_per_contract": ev,
                "inputs": {
                    "margin": margin,
                    "minutes_remaining": minutes_remaining,
                    "possession": possession,
                    "pre_spread": pre_spread,
                }
            }
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template("sports.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
