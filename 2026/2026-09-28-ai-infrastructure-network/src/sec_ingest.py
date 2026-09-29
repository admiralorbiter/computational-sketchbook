"""
SEC EDGAR XBRL Ingestion Pipeline
Fetches standardized financial facts from data.sec.gov for network entities,
caches raw JSON files in data/raw/sec/, and standardizes into tidy Parquet/CSV tables.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

USER_AGENT = "ComputationalSketchbook/1.0 (researcher@computational-sketchbook.org)"
SEC_HEADERS = {"User-Agent": USER_AGENT, "Accept-Encoding": "gzip, deflate"}

# GAAP Concept Priorities for standard metrics
METRIC_CONCEPTS = {
    "revenue": [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "SalesRevenueNet",
        "GrossProfit"
    ],
    "cost_of_revenue": [
        "CostOfRevenue",
        "CostOfGoodsAndServicesSold"
    ],
    "operating_income": [
        "OperatingIncomeLoss"
    ],
    "net_income": [
        "NetIncomeLoss"
    ],
    "cash_and_equivalents": [
        "CashAndCashEquivalentsAtCarryingValue"
    ],
    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivities"
    ],
    "capital_expenditures": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets"
    ],
    "ppe_net": [
        "PropertyPlantAndEquipmentNet"
    ],
    "accounts_receivable": [
        "AccountsReceivableNetCurrent"
    ],
    "inventory": [
        "InventoryNet"
    ],
    "operating_lease_liabilities": [
        "OperatingLeaseLiability",
        "OperatingLeaseLiabilityNoncurrent"
    ],
    "operating_lease_liabilities_current": [
        "OperatingLeaseLiabilityCurrent"
    ],
    "total_debt": [
        "LongTermDebtAndCapitalLeaseObligations",
        "LongTermDebtNoncurrent",
        "DebtInstrumentCarryingAmount",
        "LongTermDebt"
    ],
    "current_debt": [
        "DebtCurrent",
        "LongTermDebtCurrent"
    ],
    "backlog_rpo": [
        "RevenueRemainingPerformanceObligation"
    ]
}


class SECIngestPipeline:
    def __init__(self, raw_dir: Path, processed_dir: Path):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def fetch_company_facts(self, cik: str, ticker: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Fetch company facts JSON from SEC EDGAR or load from local cache."""
        cik_padded = str(cik).zfill(10)
        cache_file = self.raw_dir / f"{ticker.upper()}_facts_{cik_padded}.json"

        if cache_file.exists() and not force_refresh:
            logger.info(f"Loading cached SEC facts for {ticker} from {cache_file.name}")
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)

        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json"
        logger.info(f"Downloading SEC facts for {ticker} (CIK {cik_padded}) from {url}")
        
        # Respect SEC rate limit (max 10 requests per second)
        time.sleep(0.2)
        response = requests.get(url, headers=SEC_HEADERS, timeout=20)
        response.raise_for_status()
        data = response.json()

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Successfully cached raw facts for {ticker} ({len(response.content)} bytes)")
        return data

    def extract_metrics(self, entity_id: str, ticker: str, cik: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and harmonize standardized financial facts from raw XBRL payload."""
        facts_gaap = data.get("facts", {}).get("us-gaap", {})
        extracted_records = []

        for standard_metric, concept_candidates in METRIC_CONCEPTS.items():
            matched_concept = None
            units_data = None
            
            for candidate in concept_candidates:
                if candidate in facts_gaap:
                    cand_units = facts_gaap[candidate].get("units", {}).get("USD", [])
                    if cand_units:
                        matched_concept = candidate
                        units_data = cand_units
                        break

            if not units_data:
                continue

            for item in units_data:
                # Filter for periodic filings (10-K, 10-Q, S-1)
                form = item.get("form", "")
                if form not in ["10-K", "10-Q", "10-K/A", "10-Q/A", "S-1"]:
                    continue

                fp = item.get("fp", "")
                fy = item.get("fy")
                end_date = item.get("end")
                val = item.get("val")
                filed_date = item.get("filed")
                accn = item.get("accn")

                if val is None or not end_date:
                    continue

                extracted_records.append({
                    "entity_id": entity_id,
                    "ticker": ticker,
                    "cik": cik,
                    "metric": standard_metric,
                    "concept_name": matched_concept,
                    "period_end": end_date,
                    "fiscal_year": fy,
                    "fiscal_period": fp,
                    "form": form,
                    "value": float(val),
                    "unit": "USD",
                    "filed_date": filed_date,
                    "accession_number": accn,
                    "start_date": item.get("start")
                })

        return extracted_records

    def run(self, entities: Dict[str, Any], force_refresh: bool = False) -> pd.DataFrame:
        """Run complete extraction for all entities with valid CIKs."""
        all_records = []
        for entity_id, meta in entities.items():
            cik = meta.get("cik")
            ticker = meta.get("ticker")
            if not cik or not ticker:
                logger.info(f"Skipping {entity_id} (non-public / no CIK registered)")
                continue

            try:
                raw_facts = self.fetch_company_facts(cik=cik, ticker=ticker, force_refresh=force_refresh)
                records = self.extract_metrics(entity_id=entity_id, ticker=ticker, cik=cik, data=raw_facts)
                all_records.extend(records)
                logger.info(f"Extracted {len(records)} metric observations for {ticker}")
            except Exception as e:
                logger.error(f"Failed to fetch/parse facts for {ticker}: {e}")

        df = pd.DataFrame(all_records)
        if not df.empty:
            # Deduplicate keeping latest filed accession
            df = df.sort_values(by=["entity_id", "metric", "period_end", "filed_date"]).drop_duplicates(
                subset=["entity_id", "metric", "period_end", "form", "fiscal_period"], keep="last"
            )

            parquet_path = self.processed_dir / "financials.parquet"
            csv_path = self.processed_dir / "financials.csv"
            df.to_parquet(parquet_path, index=False)
            df.to_csv(csv_path, index=False)
            logger.info(f"Saved {len(df)} standardized facts to {parquet_path.name} and {csv_path.name}")

        return df


if __name__ == "__main__":
    import yaml
    project_root = Path(__file__).resolve().parent.parent
    config_path = project_root / "config" / "entities.yml"
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    pipeline = SECIngestPipeline(
        raw_dir=project_root / "data" / "raw" / "sec",
        processed_dir=project_root / "data" / "processed"
    )
    df_facts = pipeline.run(config_data.get("entities", {}))
    print(f"\nPipeline Complete. Processed {len(df_facts)} facts across {df_facts['entity_id'].nunique()} entities.")
