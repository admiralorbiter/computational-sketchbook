from __future__ import annotations

from typing import Tuple


def fee_adjusted_kelly(p_star: float, price: float, fee_in_per_contract: float) -> Tuple[float, float, float]:
    """
    Compute fee-aware Kelly fractions for a YES contract that pays $1.
    Returns (kelly_full, kelly_half, c_eff).
    c_eff = price + fee_in_per_contract
    k_full = max(0, (p_star - c_eff) / (1 - c_eff))
    k_half = 0.5 * k_full
    """
    c_eff = price + fee_in_per_contract
    if c_eff >= 1.0:
        return (0.0, 0.0, c_eff)
    k_full = max(0.0, (p_star - c_eff) / (1.0 - c_eff))
    return (k_full, 0.5 * k_full, c_eff)


def ev_hold_to_settlement(p_star: float, price: float, fee_in_per_contract: float) -> float:
    """
    Expected value per contract if held to settlement (single leg entry).
    EV = p_star - price - fee_in_per_contract
    """
    return p_star - price - fee_in_per_contract
