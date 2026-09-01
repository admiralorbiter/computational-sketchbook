from __future__ import annotations
import os, requests, pandas as pd
from typing import List, Dict

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

def fetch_fred_series(series_id: str, api_key: str | None = None, **params) -> pd.DataFrame:
    key = api_key or os.getenv("FRED_API_KEY")
    if not key:
        raise RuntimeError("FRED_API_KEY not set in .env")
    p = {"series_id": series_id, "api_key": key, "file_type": "json"}
    p.update(params)
    r = requests.get(FRED_BASE, params=p, timeout=30)
    r.raise_for_status()
    data = r.json()
    # Keep only valid numeric observations
    obs = [{"date": o["date"][:7], "value": float(o["value"])} for o in data.get("observations", []) if o["value"] not in (".", "", None)]
    df = pd.DataFrame(obs)
    return df
