from __future__ import annotations
import math


def normal_cdf(x: float) -> float:
    """Standard normal CDF using erf (no SciPy dependency)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def digital_up_probability(*, S: float, K: float, sigma: float, T_years: float) -> float:
    """
    Probability that GBM(S, sigma) ends above strike K after time T (in years),
    assuming ~0 drift over short horizons.
    p = Phi( (ln(S/K) - 0.5*sigma^2*T) / (sigma*sqrt(T)) )
    Handles edge cases (T=0 or sigma=0).
    """
    if K <= 0 or S <= 0:
        return 0.5
    if T_years <= 0.0 or sigma <= 0.0:
        # Immediate resolution: it's above if S>K, below if S<K, tie => 0.5
        return 1.0 if S > K else (0.0 if S < K else 0.5)
    mu = math.log(S / K) - 0.5 * (sigma ** 2) * T_years
    denom = sigma * math.sqrt(T_years)
    z = mu / denom
    p = normal_cdf(z)
    # Numerical safety
    return max(0.0, min(1.0, p))
