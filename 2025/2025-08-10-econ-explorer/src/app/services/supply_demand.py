from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Tuple


Number = float


@dataclass
class BaselineEquilibrium:
    price_star: Number
    quantity_star: Number
    consumer_surplus: Number
    producer_surplus: Number
    demand_price_intercept: Number
    supply_price_intercept: Number


@dataclass
class ScenarioOutcome:
    kind: Literal[
        "none",
        "per_unit_tax",
        "ad_valorem_tax",
        "quota",
        "price_floor",
        "price_ceiling",
    ]
    buyer_price: Number
    seller_price: Number
    quantity: Number
    consumer_surplus: Number
    producer_surplus: Number
    tax_revenue: Number
    deadweight_loss: Number
    quota_rent: Number = 0.0


def _validate_slopes(b_d: Number, b_s: Number) -> None:
    if b_d <= 0 or b_s <= 0:
        raise ValueError("Demand and supply slopes must be strictly positive (b_d, b_s > 0)")


def compute_linear_equilibrium(a_d: Number, b_d: Number, a_s: Number, b_s: Number) -> Tuple[Number, Number]:
    """Return (p_star, q_star) for linear demand and supply.

    Demand: Qd(p) = a_d - b_d * p
    Supply: Qs(p) = -a_s + b_s * p
    """
    _validate_slopes(b_d, b_s)
    p_star = (a_d + a_s) / (b_d + b_s)
    q_star = (a_d * b_s - a_s * b_d) / (b_d + b_s)
    return p_star, q_star


def compute_welfare_linear(
    a_d: Number,
    b_d: Number,
    a_s: Number,
    b_s: Number,
    price: Number,
    quantity: Number,
) -> Tuple[Number, Number, Number, Number]:
    """Return (CS, PS, p_int_d, p_int_s) at given (price, quantity).

    Uses triangle areas for linear curves; assumes intersections with axes are relevant.
    """
    _validate_slopes(b_d, b_s)
    p_int_d = a_d / b_d
    p_int_s = a_s / b_s if b_s != 0 else 0.0
    # Ensure non-negative quantity for surplus calculations
    q = max(0.0, quantity)
    cs = max(0.0, 0.5 * (p_int_d - price) * q)
    ps = max(0.0, 0.5 * (price - p_int_s) * q)
    return cs, ps, p_int_d, p_int_s


def baseline_summary(a_d: Number, b_d: Number, a_s: Number, b_s: Number) -> BaselineEquilibrium:
    p_star, q_star = compute_linear_equilibrium(a_d, b_d, a_s, b_s)
    cs, ps, p_int_d, p_int_s = compute_welfare_linear(a_d, b_d, a_s, b_s, p_star, q_star)
    return BaselineEquilibrium(
        price_star=p_star,
        quantity_star=q_star,
        consumer_surplus=cs,
        producer_surplus=ps,
        demand_price_intercept=p_int_d,
        supply_price_intercept=p_int_s,
    )


def apply_per_unit_tax_linear(
    a_d: Number, b_d: Number, a_s: Number, b_s: Number, tau: Number
) -> ScenarioOutcome:
    """Per-unit tax on buyers: demand sees p_b = p_s + tau.

    Solve a_d - b_d * (p_s + tau) = -a_s + b_s * p_s.
    """
    p_s = (a_d + a_s - b_d * tau) / (b_d + b_s)
    q = a_d - b_d * (p_s + tau)
    p_b = p_s + tau
    cs, ps, _, _ = compute_welfare_linear(a_d, b_d, a_s, b_s, p_b, q)
    tr = max(0.0, tau * max(0.0, q))
    # Baseline for DWL
    p0, q0 = compute_linear_equilibrium(a_d, b_d, a_s, b_s)
    dwl = max(0.0, 0.5 * tau * max(0.0, q0 - q))
    return ScenarioOutcome(
        kind="per_unit_tax",
        buyer_price=p_b,
        seller_price=p_s,
        quantity=q,
        consumer_surplus=cs,
        producer_surplus=ps,
        tax_revenue=tr,
        deadweight_loss=dwl,
    )


def apply_ad_valorem_tax_linear(
    a_d: Number, b_d: Number, a_s: Number, b_s: Number, t: Number
) -> ScenarioOutcome:
    """Ad valorem tax of rate t on buyers: demand sees p_b = (1+t) * p_s.

    Solve a_d - b_d * (1 + t) * p_s = -a_s + b_s * p_s.
    """
    denom = b_d * (1.0 + t) + b_s
    p_s = (a_d + a_s) / denom
    q = a_d - b_d * (1.0 + t) * p_s
    p_b = (1.0 + t) * p_s
    cs, ps, _, _ = compute_welfare_linear(a_d, b_d, a_s, b_s, p_b, q)
    tr = max(0.0, t * p_s * max(0.0, q))
    # Baseline for DWL (approx; exact polygon equals loss in CS+PS-TR)
    p0, q0 = compute_linear_equilibrium(a_d, b_d, a_s, b_s)
    # DWL via surplus accounting
    cs0, ps0, _, _ = compute_welfare_linear(a_d, b_d, a_s, b_s, p0, q0)
    dwl = max(0.0, (cs0 - cs) + (ps0 - ps) - tr)
    return ScenarioOutcome(
        kind="ad_valorem_tax",
        buyer_price=p_b,
        seller_price=p_s,
        quantity=q,
        consumer_surplus=cs,
        producer_surplus=ps,
        tax_revenue=tr,
        deadweight_loss=dwl,
    )


def apply_quota_linear(
    a_d: Number, b_d: Number, a_s: Number, b_s: Number, q_cap: Number
) -> ScenarioOutcome:
    """Quota ceiling on quantity traded.

    If q_cap >= q*, outcome is baseline. If q_cap < q*, buyer and seller prices
    are given by inverse demand and supply at q_cap, with quota rent between them.
    """
    p0, q0 = compute_linear_equilibrium(a_d, b_d, a_s, b_s)
    if q_cap >= q0:
        cs, ps, _, _ = compute_welfare_linear(a_d, b_d, a_s, b_s, p0, q0)
        return ScenarioOutcome(
            kind="quota",
            buyer_price=p0,
            seller_price=p0,
            quantity=q0,
            consumer_surplus=cs,
            producer_surplus=ps,
            tax_revenue=0.0,
            deadweight_loss=0.0,
            quota_rent=0.0,
        )
    # Inverse demand/supply at q_cap
    p_b = (a_d - q_cap) / b_d
    p_s = (q_cap + a_s) / b_s
    cs, ps, _, _ = compute_welfare_linear(a_d, b_d, a_s, b_s, p_b, q_cap)
    # DWL via lost trades triangle between q_cap and q0
    dwl = max(0.0, 0.5 * (p_b - p_s) * (q0 - q_cap))
    quota_rent = max(0.0, (p_b - p_s) * q_cap)
    return ScenarioOutcome(
        kind="quota",
        buyer_price=p_b,
        seller_price=p_s,
        quantity=q_cap,
        consumer_surplus=cs,
        producer_surplus=ps,
        tax_revenue=0.0,
        deadweight_loss=dwl,
        quota_rent=quota_rent,
    )


def apply_price_control_linear(
    a_d: Number,
    b_d: Number,
    a_s: Number,
    b_s: Number,
    p_bar: Number,
    kind: Literal["price_floor", "price_ceiling"],
) -> ScenarioOutcome:
    """Apply a binding price control if applicable.

    - Floor: if p_bar > p*, trades at q = min(Qd(p_bar), Qs(p_bar)).
    - Ceiling: if p_bar < p*, trades at q = min(Qd(p_bar), Qs(p_bar)).
    """
    p0, q0 = compute_linear_equilibrium(a_d, b_d, a_s, b_s)
    # Quantities at the controlled price
    qd = a_d - b_d * p_bar
    qs = -a_s + b_s * p_bar
    q = min(max(0.0, qd), max(0.0, qs))
    # Determine if binding
    if (kind == "price_floor" and p_bar <= p0) or (kind == "price_ceiling" and p_bar >= p0):
        # Not binding → baseline
        cs0, ps0, _, _ = compute_welfare_linear(a_d, b_d, a_s, b_s, p0, q0)
        return ScenarioOutcome(
            kind=kind,
            buyer_price=p0,
            seller_price=p0,
            quantity=q0,
            consumer_surplus=cs0,
            producer_surplus=ps0,
            tax_revenue=0.0,
            deadweight_loss=0.0,
        )
    # Binding control at price p_bar; no tax revenue by default
    # Buyer and seller price coincide at p_bar; rationing abstracted away
    cs, ps, _, _ = compute_welfare_linear(a_d, b_d, a_s, b_s, p_bar, q)
    # DWL via difference in total surplus vs baseline
    cs0, ps0, _, _ = compute_welfare_linear(a_d, b_d, a_s, b_s, p0, q0)
    dwl = max(0.0, (cs0 + ps0) - (cs + ps))
    return ScenarioOutcome(
        kind=kind,
        buyer_price=p_bar,
        seller_price=p_bar,
        quantity=q,
        consumer_surplus=cs,
        producer_surplus=ps,
        tax_revenue=0.0,
        deadweight_loss=dwl,
    )


