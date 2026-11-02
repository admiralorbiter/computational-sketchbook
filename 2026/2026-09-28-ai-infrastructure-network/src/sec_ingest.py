"""
SEC EDGAR XBRL Ingestion Pipeline (Phase 0.6 Refactor)
Fetches standardized financial facts from data.sec.gov for network entities,
distinguishes instant balance-sheet facts from duration flow facts (quarterly vs annual),
aggregates multi-component funded debt and lease liabilities,
and exports clean, normalized Parquet and CSV tables.
"""

from datetime import datetime
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

USER_AGENT = "ComputationalSketchbook/1.0 (researcher@computational-sketchbook.org)"
SEC_HEADERS = {"User-Agent": USER_AGENT, "Accept-Encoding": "gzip, deflate"}

# Concepts for Duration Flow Metrics (Modern ASC 606 first)
FLOW_METRIC_CONCEPTS = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet"
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
    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivities"
    ],
    "capital_expenditures": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets"
    ]
}

# Concepts for Instant Balance Sheet Metrics
INSTANT_METRIC_CONCEPTS = {
    "cash_and_equivalents": [
        "CashAndCashEquivalentsAtCarryingValue"
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
    "backlog_rpo": [
        "RevenueRemainingPerformanceObligation"
    ]
}

# Company-specific metric extraction overrides to keep the ingestion engine generic for Phase 1 scaling
FINANCIAL_METRIC_OVERRIDES = {
    "CRWV": {
        "total_debt": {
            "method": "preferred_concept",
            "concept_order": ["DebtLongtermAndShorttermCombinedAmount", "DebtInstrumentCarryingAmount"],
            "min_threshold": 1e10
        },
        "contractual_principal": {
            "2026-06-30": 35551000000.0  # Form 10-Q Note 7 Table 36 future debt principal across 11 components
        }
    },
    "SMCI": {
        "total_debt": {
            "method": "sum_components",
            "components": [
                ["DebtLongtermAndShorttermCombinedAmount", "DebtInstrumentCarryingAmount"],
                ["ConvertibleLongTermNotesPayable", "ConvertibleDebtNoncurrent"]
            ]
        }
    },
    "APLD": {
        "total_debt": {
            "method": "sum_components",
            "components": [
                ["LongTermNotesPayable"],
                ["NotesPayableCurrent"]
            ]
        },
        "contractual_principal": {
            "2026-05-31": 5306680000.0  # Form 10-K Note 8 contractual remaining principal payments
        }
    }
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
        time.sleep(0.2)
        response = requests.get(url, headers=SEC_HEADERS, timeout=20)
        response.raise_for_status()
        data = response.json()

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return data

    def _classify_duration(self, start_date: Optional[str], end_date: str) -> Tuple[str, int]:
        """Classify flow observation duration type (quarterly, semi_annual, annual)."""
        if not start_date or start_date == end_date:
            return "instant", 0
        try:
            d_start = datetime.strptime(start_date, "%Y-%m-%d")
            d_end = datetime.strptime(end_date, "%Y-%m-%d")
            days = (d_end - d_start).days
            if 60 <= days <= 125:
                return "quarterly", days
            elif 160 <= days <= 215:
                return "semi_annual", days
            elif 250 <= days <= 310:
                return "nine_months", days
            elif 335 <= days <= 385:
                return "annual", days
            else:
                return f"other_{days}d", days
        except Exception:
            return "unknown", 0

    def extract_metrics(self, entity_id: str, ticker: str, cik: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and categorize standardized financial facts from raw XBRL payload."""
        facts_gaap = data.get("facts", {}).get("us-gaap", {})
        extracted = []

        ALLOWED_FORMS = ["10-K", "10-Q", "10-K/A", "10-Q/A", "20-F", "20-F/A"]

        # 1. Flow metrics - inspect all concepts with priority and deduplicate
        for metric, concepts in FLOW_METRIC_CONCEPTS.items():
            metric_flow_records = []
            for p_idx, c in enumerate(concepts):
                if c in facts_gaap:
                    units = facts_gaap[c].get("units", {}).get("USD", [])
                    recent_units = [u for u in units if u.get("form") in ALLOWED_FORMS]
                    for item in recent_units:
                        end_date = item.get("end")
                        start_date = item.get("start")
                        val = item.get("val")
                        if val is None or not end_date:
                            continue
                        dur_type, dur_days = self._classify_duration(start_date, end_date)
                        metric_flow_records.append({
                            "entity_id": entity_id,
                            "ticker": ticker,
                            "cik": cik,
                            "metric": metric,
                            "concept_name": c,
                            "priority": p_idx,
                            "period_end": end_date,
                            "start_date": start_date,
                            "duration_type": dur_type,
                            "duration_days": dur_days,
                            "fiscal_year": item.get("fy"),
                            "fiscal_period": item.get("fp"),
                            "form": item.get("form"),
                            "value": float(val),
                            "unit": "USD",
                            "filed_date": item.get("filed"),
                            "accession_number": item.get("accn")
                        })
            if metric_flow_records:
                df_flow = pd.DataFrame(metric_flow_records)
                # Sort by filed_date descending, then priority ascending (preferred concept first)
                df_flow = df_flow.sort_values(by=["filed_date", "priority"], ascending=[False, True])
                df_flow_dedup = df_flow.drop_duplicates(subset=["period_end", "duration_type", "fiscal_period"], keep="first")
                
                # Check for derived Q4: if annual and nine_months exist for the same fiscal year
                annual_rows = df_flow_dedup[df_flow_dedup["duration_type"] == "annual"]
                nine_rows = df_flow_dedup[df_flow_dedup["duration_type"] == "nine_months"]
                derived_q4_records = []
                for _, a_row in annual_rows.iterrows():
                    a_end = a_row["period_end"]
                    a_start = a_row.get("start_date")
                    # Match nine_months row that starts on the identical start_date (first day of fiscal year)
                    # and ends 60-125 days prior to the annual period end
                    matched_9m = nine_rows[
                        (nine_rows["period_end"] < a_end) & 
                        (nine_rows["start_date"] == a_start) &
                        (nine_rows["concept_name"].isin(FLOW_METRIC_CONCEPTS[metric]))
                    ].sort_values(by="period_end", ascending=False)
                    
                    if not matched_9m.empty:
                        m_row = matched_9m.iloc[0]
                        try:
                            d_a = datetime.strptime(a_end, "%Y-%m-%d")
                            d_m = datetime.strptime(m_row["period_end"], "%Y-%m-%d")
                            gap_days = (d_a - d_m).days
                            if 60 <= gap_days <= 125:
                                q4_val = float(a_row["value"]) - float(m_row["value"])
                                existing_q4 = df_flow_dedup[(df_flow_dedup["period_end"] == a_end) & (df_flow_dedup["duration_type"] == "quarterly")]
                                if existing_q4.empty:
                                    derived_q4_records.append({
                                        "entity_id": entity_id,
                                        "ticker": ticker,
                                        "cik": cik,
                                        "metric": metric,
                                        "concept_name": f"{a_row['concept_name']} (Derived Q4: FY - 9M)",
                                        "period_end": a_row["period_end"],
                                        "start_date": m_row["period_end"],
                                        "duration_type": "quarterly",
                                        "duration_days": gap_days,
                                        "fiscal_year": a_row["fiscal_year"],
                                        "fiscal_period": "Q4",
                                        "form": "10-K (derived)",
                                        "value": q4_val,
                                        "unit": "USD",
                                        "filed_date": a_row["filed_date"],
                                        "accession_number": a_row["accession_number"]
                                    })
                        except Exception:
                            pass

                for r in df_flow_dedup.to_dict(orient="records"):
                    r.pop("priority", None)
                    extracted.append(r)
                extracted.extend(derived_q4_records)

        # 2. Instant metrics - inspect all concepts with priority and deduplicate
        for metric, concepts in INSTANT_METRIC_CONCEPTS.items():
            metric_inst_records = []
            for p_idx, c in enumerate(concepts):
                if c in facts_gaap:
                    units = facts_gaap[c].get("units", {}).get("USD", [])
                    matched = [u for u in units if u.get("form") in ALLOWED_FORMS]
                    for item in matched:
                        end_date = item.get("end")
                        val = item.get("val")
                        if val is None or not end_date:
                            continue
                        metric_inst_records.append({
                            "entity_id": entity_id,
                            "ticker": ticker,
                            "cik": cik,
                            "metric": metric,
                            "concept_name": c,
                            "priority": p_idx,
                            "period_end": end_date,
                            "start_date": None,
                            "duration_type": "instant",
                            "duration_days": 0,
                            "fiscal_year": item.get("fy"),
                            "fiscal_period": item.get("fp"),
                            "form": item.get("form"),
                            "value": float(val),
                            "unit": "USD",
                            "filed_date": item.get("filed"),
                            "accession_number": item.get("accn")
                        })
            if metric_inst_records:
                df_inst = pd.DataFrame(metric_inst_records)
                df_inst = df_inst.sort_values(by=["filed_date", "priority"], ascending=[False, True])
                df_inst_dedup = df_inst.drop_duplicates(subset=["period_end", "form"], keep="first")
                for r in df_inst_dedup.to_dict(orient="records"):
                    r.pop("priority", None)
                    extracted.append(r)

        # 3. Debt Extraction
        reporting_dates = set()
        for k in ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "CashAndCashEquivalentsAtCarryingValue", "OperatingIncomeLoss"]:
            if k in facts_gaap:
                for u in facts_gaap[k].get("units", {}).get("USD", []):
                    if u.get("form") in ALLOWED_FORMS:
                        reporting_dates.add((u.get("end"), u.get("form"), u.get("fy"), u.get("fp"), u.get("filed"), u.get("accn")))

        for (end_date, form, fy, fp, filed, accn) in reporting_dates:
            if not end_date:
                continue

            def get_val(concept_list):
                for c in concept_list:
                    if c in facts_gaap:
                        for u in facts_gaap[c].get("units", {}).get("USD", []):
                            if u.get("end") == end_date and u.get("form") == form:
                                return float(u.get("val", 0.0)), c
                return 0.0, None

            # Combined total or carrying amount
            v_comb, c_comb = get_val(["DebtLongtermAndShorttermCombinedAmount", "DebtInstrumentCarryingAmount"])
            # Separate components
            v_lt, c_lt = get_val(["LongTermDebtNoncurrent", "LongTermNotesPayable", "LongTermNotesAndLoans", "LongTermDebtAndCapitalLeaseObligations", "LongTermDebt"])
            v_cur, c_cur = get_val(["LongTermDebtCurrent", "NotesPayableCurrent", "DebtCurrent"])
            v_conv, c_conv = get_val(["ConvertibleLongTermNotesPayable", "ConvertibleDebtNoncurrent", "ConvertibleDebtCurrent"])

            total_debt = 0.0
            concept_used = ""

            # Check for configured company-specific override
            override = FINANCIAL_METRIC_OVERRIDES.get(ticker, {}).get("total_debt")
            if override:
                method = override.get("method")
                if method == "preferred_concept":
                    v_pref, c_pref = get_val(override.get("concept_order", []))
                    if v_pref >= override.get("min_threshold", 0.0):
                        total_debt = v_pref
                        concept_used = c_pref
                elif method == "sum_components":
                    comp_vals = []
                    comp_tags = []
                    for comp_concepts in override.get("components", []):
                        cv, ct = get_val(comp_concepts)
                        if cv > 0:
                            comp_vals.append(cv)
                            comp_tags.append(ct)
                    if comp_vals:
                        total_debt = sum(comp_vals)
                        concept_used = "+".join(comp_tags)

            # Generic fallback logic
            if total_debt == 0.0:
                if v_comb > 0 and v_comb >= (v_lt + v_cur):
                    total_debt = v_comb
                    concept_used = c_comb
                elif (v_lt + v_cur + v_conv) > 0:
                    total_debt = v_lt + v_cur + v_conv
                    tags = [t for t in [c_lt, c_cur, c_conv] if t]
                    concept_used = "+".join(tags)
                elif v_comb > 0:
                    total_debt = v_comb
                    concept_used = c_comb

            if total_debt > 0:
                extracted.append({
                    "entity_id": entity_id,
                    "ticker": ticker,
                    "cik": cik,
                    "metric": "total_debt",
                    "concept_name": concept_used,
                    "period_end": end_date,
                    "start_date": None,
                    "duration_type": "instant",
                    "duration_days": 0,
                    "fiscal_year": fy,
                    "fiscal_period": fp,
                    "form": form,
                    "value": float(total_debt),
                    "unit": "USD",
                    "filed_date": filed,
                    "accession_number": accn
                })

            # Record gross contractual principal if configured
            contractual_principal_cfg = FINANCIAL_METRIC_OVERRIDES.get(ticker, {}).get("contractual_principal", {})
            if end_date in contractual_principal_cfg:
                p_val = contractual_principal_cfg[end_date]
                extracted.append({
                    "entity_id": entity_id,
                    "ticker": ticker,
                    "cik": cik,
                    "metric": "principal_outstanding",
                    "concept_name": "ContractualRemainingPrincipalPayments (Note Disclosure)",
                    "period_end": end_date,
                    "start_date": None,
                    "duration_type": "instant",
                    "duration_days": 0,
                    "fiscal_year": fy,
                    "fiscal_period": fp,
                    "form": form,
                    "value": float(p_val),
                    "unit": "USD",
                    "filed_date": filed,
                    "accession_number": accn
                })

            # Lease liabilities
            v_lease_comb, c_lease_comb = get_val(["OperatingLeaseLiability"])
            v_lease_nc, c_lease_nc = get_val(["OperatingLeaseLiabilityNoncurrent"])
            v_lease_c, c_lease_c = get_val(["OperatingLeaseLiabilityCurrent"])

            total_lease = 0.0
            lease_tag = ""
            if v_lease_comb > 0:
                total_lease = v_lease_comb
                lease_tag = c_lease_comb
            elif (v_lease_nc + v_lease_c) > 0:
                total_lease = v_lease_nc + v_lease_c
                tags = [t for t in [c_lease_nc, c_lease_c] if t]
                lease_tag = "+".join(tags)
            elif v_lease_nc > 0:
                total_lease = v_lease_nc
                lease_tag = c_lease_nc

            if total_lease > 0:
                extracted.append({
                    "entity_id": entity_id,
                    "ticker": ticker,
                    "cik": cik,
                    "metric": "operating_lease_liabilities",
                    "concept_name": lease_tag,
                    "period_end": end_date,
                    "start_date": None,
                    "duration_type": "instant",
                    "duration_days": 0,
                    "fiscal_year": fy,
                    "fiscal_period": fp,
                    "form": form,
                    "value": float(total_lease),
                    "unit": "USD",
                    "filed_date": filed,
                    "accession_number": accn
                })

        return extracted

    def run(self, entities: Dict[str, Any], force_refresh: bool = False) -> pd.DataFrame:
        """Run complete extraction for all entities with valid CIKs."""
        all_records = []
        for entity_id, meta in entities.items():
            cik = meta.get("cik")
            ticker = meta.get("ticker")
            if not cik or not ticker:
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
            df = df.sort_values(by=["entity_id", "metric", "period_end", "filed_date"]).drop_duplicates(
                subset=["entity_id", "metric", "period_end", "form", "duration_type", "fiscal_period"], keep="last"
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
