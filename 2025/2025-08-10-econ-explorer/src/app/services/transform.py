from __future__ import annotations
import pandas as pd

def to_silver(df: pd.DataFrame, series_id: str, geo_id: str, unit: str, source: str) -> pd.DataFrame:
    out = df.copy()
    out["series_id"] = series_id
    out["geo_id"] = geo_id
    out["unit"] = unit
    out["source"] = source
    cols = ["series_id", "geo_id", "date", "value", "unit", "source"]
    return out[cols].sort_values("date")

def rebase_index(df: pd.DataFrame, base_date: str) -> pd.DataFrame:
    base_val = float(df.loc[df["date"] == base_date, "value"].iloc[0])
    rebased = df.copy()
    rebased["value"] = df["value"] / base_val * 100.0
    return rebased
