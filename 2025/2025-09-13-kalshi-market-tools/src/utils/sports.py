from __future__ import annotations
import math


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def estimate_wp_nfl_toy(*, margin: int, minutes_remaining: float, possession_flag: int, pregame_spread: float) -> float:
    """
    Toy (non-calibrated) NFL win-probability estimator for Team A.
    This is a placeholder for UI/testing only. For live trading, replace with a calibrated model.
    Features:
      - margin (TeamA - TeamB)
      - time-decay: margin matters more late
      - possession: small bump to offense
      - pregame_spread: converts to prior (favored => higher p at t=0)
    """
    total_minutes = 60.0
    t = max(0.0, min(total_minutes, minutes_remaining))
    phase = 1.0 - (t / total_minutes)  # early=0, endgame=1

    # Prior from spread: 1 score ~ 7 points ~ about 65/35; rough slope
    prior = _sigmoid(-pregame_spread / 7.0)

    # Margin impact increases late (phase^1.2), scale per score
    margin_term = (margin / 7.0) * (phase ** 1.2) * 2.2

    # Possession small effect, larger late
    poss_term = possession_flag * 0.12 * (0.6 + 0.4 * phase)

    z = math.log(prior / max(1e-9, 1.0 - prior)) + margin_term + poss_term
    return max(0.0, min(1.0, _sigmoid(z)))


def estimate_wp_nba_toy(*, margin: int, minutes_remaining: float, possession_flag: int, pregame_spread: float) -> float:
    """
    Toy (non-calibrated) NBA win-probability estimator for Team A.
    Placeholder for UI/testing only.
    """
    total_minutes = 48.0
    t = max(0.0, min(total_minutes, minutes_remaining))
    phase = 1.0 - (t / total_minutes)

    prior = _sigmoid(-pregame_spread / 10.0)  # NBA spreads wider

    # Margin matters a lot late; scale per ~6-point buckets
    margin_term = (margin / 6.0) * (phase ** 1.3) * 2.0
    poss_term = possession_flag * 0.06 * (0.5 + 0.5 * phase)

    z = math.log(prior / max(1e-9, 1.0 - prior)) + margin_term + poss_term
    return max(0.0, min(1.0, _sigmoid(z)))
