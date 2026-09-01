from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal, List


class SupplyDemandParams(BaseModel):
    a_d: float = Field(..., description="Demand intercept (quantity at p=0)")
    b_d: float = Field(..., gt=0, description="Demand slope (>0)")
    a_s: float = Field(..., ge=0, description="Supply intercept parameter (price intercept a_s/b_s)")
    b_s: float = Field(..., gt=0, description="Supply slope (>0)")
    policy: Literal["none", "per_unit_tax", "ad_valorem_tax", "quota", "price_floor", "price_ceiling"] = "none"
    tau: float = 0.0
    t: float = 0.0
    q_cap: float = 0.0
    p_bar: float = 0.0


class SupplyDemandOutcome(BaseModel):
    kind: str
    buyer_price: float
    seller_price: float
    quantity: float
    consumer_surplus: float
    producer_surplus: float
    tax_revenue: float
    deadweight_loss: float
    quota_rent: float = 0.0


class SupplyDemandResponse(BaseModel):
    baseline: dict
    outcome: SupplyDemandOutcome
    deltas: dict


