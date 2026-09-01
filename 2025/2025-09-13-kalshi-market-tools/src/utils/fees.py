from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    taker = "taker"
    maker = "maker"


class ProductType(str, Enum):
    general = "general"          # default fee schedule (most markets)
    sports = "sports"            # maker-fee list applies (posting costs a small fee when filled)
    nasdaq_spx = "nasdaq_spx"    # reduced taker fee (NASDAQ100 / SPX intraday/close)


@dataclass
class FeeInput:
    price: float      # Kalshi price in dollars (0..1)
    contracts: int    # number of contracts


def round_up_cent(x: float) -> float:
    """Round a positive number UP to the next cent (2 decimals)."""
    if x <= 0:
        return 0.0
    return math.ceil(x * 100.0) / 100.0


def taker_fee(fin: FeeInput, product_type: ProductType = ProductType.general) -> float:
    """
    Compute taker fee per the schedule:
      general:   0.07 * C * P * (1 - P)
      nasdaq_spx:0.035 * C * P * (1 - P)
    Then round up to next cent.
    """
    P, C = fin.price, fin.contracts
    base = 0.07
    if product_type == ProductType.nasdaq_spx:
        base = 0.035
    fee = base * C * P * (1.0 - P)
    return round_up_cent(fee)


def maker_fee(fin: FeeInput, product_type: ProductType = ProductType.general) -> float:
    """
    Maker fees apply only to listed series (e.g., many sports tickers). Otherwise zero.
    Formula: 0.0175 * C * P * (1 - P), rounded up to the next cent.
    """
    if product_type != ProductType.sports:
        return 0.0
    P, C = fin.price, fin.contracts
    fee = 0.0175 * C * P * (1.0 - P)
    return round_up_cent(fee)


def compute_fee(fin: FeeInput, role: Role, product_type: ProductType) -> float:
    """Return the total entry fee for the order given role & product type."""
    if role == Role.taker:
        return taker_fee(fin, product_type)
    else:
        return maker_fee(fin, product_type)
