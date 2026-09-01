from __future__ import annotations
from flask import Blueprint, current_app, jsonify, request
from ..services.data_access import load_series_observations
from ..models.series import SeriesResponse
from ..models.labs import SupplyDemandParams, SupplyDemandResponse
from ..services.supply_demand import (
    baseline_summary,
    apply_per_unit_tax_linear,
    apply_ad_valorem_tax_linear,
    apply_quota_linear,
    apply_price_control_linear,
)

api_bp = Blueprint("api", __name__)

@api_bp.get("/series/<series_id>")
def get_series(series_id: str):
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    try:
        payload = load_series_observations(series_id, current_app.config["DATA_DIR"], date_from, date_to)
    except FileNotFoundError:
        return jsonify({"error": f"unknown series_id '{series_id}'"}), 404

    return jsonify(payload.model_dump()), 200


@api_bp.post("/lab/supply-demand")
def lab_supply_demand():
    """Compute linear supply-demand baseline and one scenario.

    Expected JSON body (SupplyDemandParams):
    {
      "a_d": 10, "b_d": 1.0, "a_s": 2, "b_s": 1.0,
      "policy": "per_unit_tax", "tau": 1.0
    }
    """
    try:
        params = SupplyDemandParams(**request.get_json(force=True))
    except Exception as e:
        return jsonify({"error": f"invalid payload: {e}"}), 400

    base = baseline_summary(params.a_d, params.b_d, params.a_s, params.b_s)

    if params.policy == "none":
        outcome = {
            "kind": "none",
            "buyer_price": base.price_star,
            "seller_price": base.price_star,
            "quantity": base.quantity_star,
            "consumer_surplus": base.consumer_surplus,
            "producer_surplus": base.producer_surplus,
            "tax_revenue": 0.0,
            "deadweight_loss": 0.0,
            "quota_rent": 0.0,
        }
    elif params.policy == "per_unit_tax":
        res = apply_per_unit_tax_linear(params.a_d, params.b_d, params.a_s, params.b_s, params.tau)
        outcome = res.__dict__
    elif params.policy == "ad_valorem_tax":
        res = apply_ad_valorem_tax_linear(params.a_d, params.b_d, params.a_s, params.b_s, params.t)
        outcome = res.__dict__
    elif params.policy == "quota":
        res = apply_quota_linear(params.a_d, params.b_d, params.a_s, params.b_s, params.q_cap)
        outcome = res.__dict__
    elif params.policy in ("price_floor", "price_ceiling"):
        res = apply_price_control_linear(params.a_d, params.b_d, params.a_s, params.b_s, params.p_bar, params.policy)
        outcome = res.__dict__
    else:
        return jsonify({"error": f"unknown policy '{params.policy}'"}), 400

    deltas = {
        "delta_cs": outcome["consumer_surplus"] - base.consumer_surplus,
        "delta_ps": outcome["producer_surplus"] - base.producer_surplus,
        "delta_q": outcome["quantity"] - base.quantity_star,
        "delta_p_b": outcome["buyer_price"] - base.price_star,
        "delta_p_s": outcome["seller_price"] - base.price_star,
    }

    resp = SupplyDemandResponse(
        baseline={
            "p_star": base.price_star,
            "q_star": base.quantity_star,
            "cs": base.consumer_surplus,
            "ps": base.producer_surplus,
            "p_int_d": base.demand_price_intercept,
            "p_int_s": base.supply_price_intercept,
        },
        outcome=outcome,  # pydantic will re-validate
        deltas=deltas,
    )
    return jsonify(resp.model_dump()), 200
