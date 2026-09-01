from __future__ import annotations
import os
import pandas as pd
import typer
from ..services.fred import fetch_fred_series
from ..services.transform import to_silver, rebase_index

app = typer.Typer(help="KC Econ Lab ETL & utilities")

DATA_DIR = os.getenv("DATA_DIR", "data")

def _ensure_dirs():
    for sub in ("bronze", "silver", "gold", "sample"):
        os.makedirs(os.path.join(DATA_DIR, sub), exist_ok=True)

@app.command()
def fred_cpi(series_id: str = "CPIAUCSL", base_date: str = "2018-01"):
    """Fetch CPI from FRED, save bronze/silver/gold."""
    _ensure_dirs()
    df = fetch_fred_series(series_id, observation_start="2010-01-01")
    # Persist bronze
    bronze = os.path.join(DATA_DIR, "bronze", f"{series_id}.csv")
    df.to_csv(bronze, index=False)
    # Silver
    silver = to_silver(df, series_id="cpi", geo_id="US", unit="index", source="FRED")
    silver.to_csv(os.path.join(DATA_DIR, "silver", "cpi.csv"), index=False)
    # Gold (index=100 at base_date)
    rebased = rebase_index(silver.rename(columns={"value":"value"}), base_date=base_date)
    rebased[["date","value"]].to_csv(os.path.join(DATA_DIR, "gold", "cpi_index100.csv"), index=False)
    typer.echo(f"Saved CPI: bronze:{bronze} silver:silver/cpi.csv gold:gold/cpi_index100.csv")

@app.command()
def fred_hpi_kc(series_id: str = "ATNHPIUS28140Q", base_date: str = "2018-01"):
    """Fetch FHFA HPI for KC MSA via FRED, save bronze/silver/gold.

    Note: quarterly series; base_date should exist in data (e.g., '2018-01' may be remapped).
    """
    _ensure_dirs()
    df = fetch_fred_series(series_id, observation_start="2010-01-01")
    # Bronze
    bronze = os.path.join(DATA_DIR, "bronze", f"{series_id}.csv")
    df.to_csv(bronze, index=False)
    # Silver
    silver = to_silver(df, series_id="hpi_kc", geo_id="CBSA-28140", unit="index", source="FRED")
    silver.to_csv(os.path.join(DATA_DIR, "silver", "hpi_kc.csv"), index=False)
    # Gold: since quarterly, use first available date as base if base_date not present
    base = base_date if (silver["date"] == base_date).any() else silver["date"].iloc[0]
    rebased = rebase_index(silver.rename(columns={"value":"value"}), base_date=base)
    rebased[["date","value"]].to_csv(os.path.join(DATA_DIR, "gold", "hpi_kc_index100.csv"), index=False)
    typer.echo(f"Saved HPI KC: bronze:{bronze} silver:silver/hpi_kc.csv gold:gold/hpi_kc_index100.csv (base={base})")

@app.command()
def all():
    fred_cpi()
    fred_hpi_kc()

if __name__ == "__main__":
    app()
