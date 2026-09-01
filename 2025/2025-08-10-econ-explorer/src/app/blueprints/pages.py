from __future__ import annotations
from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)

@pages_bp.get("/")
def index():
    return render_template("index.html")

@pages_bp.get("/explore")
def explore():
    return render_template("explore.html")

@pages_bp.get("/lab/basics")
def lab_supply_basics_page():
    return render_template("lab_supply_basics.html")

@pages_bp.get("/lab/supply-demand")
def lab_supply_demand_page():
    return render_template("lab_supply_demand.html")

@pages_bp.get("/lab/consumer-theory")
def lab_consumer_theory_page():
    return render_template("lab_consumer_theory.html")

@pages_bp.get("/lab/producer-theory")
def lab_producer_theory_page():
    return render_template("lab_producer_theory.html")

@pages_bp.get("/lab/market-equilibrium")
def lab_market_equilibrium_page():
    return render_template("lab_market_equilibrium.html")

@pages_bp.get("/lab/game-theory")
def lab_game_theory_page():
    return render_template("lab_game_theory.html")

@pages_bp.get("/lab/auctions")
def lab_auctions_page():
    return render_template("lab_auctions.html")

@pages_bp.get("/lab/growth-models")
def lab_growth_models_page():
    return render_template("lab_growth_models.html")
