from __future__ import annotations
import os, pandas as pd
from typing import Optional
from ..models.series import SeriesResponse, SeriesPoint

def _load_csv_if_exists(path: str) -> Optional[pd.DataFrame]:
    return pd.read_csv(path) if os.path.exists(path) else None

def _subset(df: pd.DataFrame, date_from: str | None, date_to: str | None) -> pd.DataFrame:
    out = df.copy()
    if date_from:
        out = out[out["date"] >= date_from]
    if date_to:
        out = out[out["date"] <= date_to]
    return out

def load_series_observations(series_id: str, data_dir: str, date_from: str | None, date_to: str | None) -> SeriesResponse:
    # Resolution order: gold -> silver -> sample
    if series_id == "cpi":
        # try gold
        gold = _load_csv_if_exists(os.path.join(data_dir, "gold", "cpi_index100.csv"))
        if gold is None:
            silver = _load_csv_if_exists(os.path.join(data_dir, "silver", "cpi.csv"))
            if silver is None:
                # fall back to sample
                df = pd.read_csv(os.path.join(data_dir, "sample", "cpiaucsl.csv"))
                geo_id, unit = "US", "index"
            else:
                df = silver[["date","value"]]
                geo_id, unit = "US", "index"
        else:
            df = gold[["date","value"]]
            geo_id, unit = "US", "index"
    elif series_id == "hpi_kc":
        gold = _load_csv_if_exists(os.path.join(data_dir, "gold", "hpi_kc_index100.csv"))
        if gold is None:
            silver = _load_csv_if_exists(os.path.join(data_dir, "silver", "hpi_kc.csv"))
            if silver is None:
                # fall back to sample
                df = pd.read_csv(os.path.join(data_dir, "sample", "hpi_kc.csv"))
                geo_id, unit = "CBSA-28140", "index"
            else:
                df = silver[["date","value"]]
                geo_id, unit = "CBSA-28140", "index"
        else:
            df = gold[["date","value"]]
            geo_id, unit = "CBSA-28140", "index"
    else:
        raise FileNotFoundError(f"unknown series_id '{series_id}'")

    df = _subset(df, date_from, date_to)
    obs = [SeriesPoint(date=r["date"], value=float(r["value"])) for _, r in df.iterrows()]
    return SeriesResponse(series_id=series_id, geo_id=geo_id, unit=unit, observations=obs)
