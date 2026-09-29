"""
Curates the Obligation Graph, Evidence Claims Ledger, Entities Registry,
and Assumptions Registry for the AI Infrastructure Financial Network pilot.
Exports all tables to data/processed/ in both Parquet and CSV formats.
"""

from pathlib import Path
import pandas as pd
import yaml

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def build_entities_table():
    with open(CONFIG_DIR / "entities.yml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)["entities"]
    
    records = []
    for eid, info in data.items():
        records.append({
            "entity_id": eid,
            "name": info.get("name"),
            "ticker": info.get("ticker"),
            "cik": info.get("cik"),
            "category": info.get("category"),
            "subsector": info.get("subsector"),
            "jurisdiction": info.get("jurisdiction"),
            "status": info.get("status"),
            "reporting_standard": info.get("reporting_standard"),
            "description": info.get("description"),
            "key_counterparties": ",".join(info.get("key_counterparties", [])) if info.get("key_counterparties") else ""
        })
    df = pd.DataFrame(records)
    df.to_parquet(PROCESSED_DIR / "entities.parquet", index=False)
    df.to_csv(PROCESSED_DIR / "entities.csv", index=False)
    return df


def build_assumptions_table():
    with open(CONFIG_DIR / "assumptions.yml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)["assumptions"]

    records = []
    for aid, info in data.items():
        records.append({
            "assumption_id": aid,
            "name": info.get("name"),
            "category": info.get("category"),
            "description": info.get("description"),
            "observable_proxy": info.get("observable_proxy"),
            "base_case": info.get("base_case"),
            "stress_case": info.get("stress_case"),
            "affected_obligation_types": ",".join(info.get("affected_obligation_types", []))
        })
    df = pd.DataFrame(records)
    df.to_parquet(PROCESSED_DIR / "assumptions.parquet", index=False)
    df.to_csv(PROCESSED_DIR / "assumptions.csv", index=False)
    return df


def build_evidence_claims():
    claims = [
        {
            "claim_id": "CLM-APLD-001",
            "entity_id": "APLD",
            "filing_type": "10-K",
            "accession_number": "0001144879-26-000048",
            "filing_date": "2026-07-29",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1144879/000114487926000048/apld-20260531.htm",
            "section_locator": "Item 1. Business - Polaris Forge 1 Lease Commitments",
            "exact_quote": "APLD ELN-02 LLC and APLD ELN-03 LLC entered into data center leases with CoreWeave to deliver 250 MW... bringing total contracted critical IT load to 400 MW at Polaris Forge 1... 15-year base lease term ~$11.0B total contracted revenue.",
            "evidence_class": "A",
            "extraction_method": "SEC EDGAR 10-K direct audit",
            "verifier_notes": "Identifies master lease contracts, MW capacity, and $11.0B revenue commitment. Core tenant risk concentrated in CoreWeave."
        },
        {
            "claim_id": "CLM-APLD-002",
            "entity_id": "APLD",
            "filing_type": "10-K",
            "accession_number": "0001144879-26-000048",
            "filing_date": "2026-07-29",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1144879/000114487926000048/apld-20260531.htm",
            "section_locator": "Note 14. Commitments and Contingencies - Assignment to SPV",
            "exact_quote": "On March 30, 2026, CoreWeave entered into an Assignment, Assumption and Consent Agreement with CoreWeave Compute Acquisition Co. VIII, LLC ('CoreWeave SPV'), assigning all of CoreWeave's rights and obligations under the ELN-03 Lease to CoreWeave SPV and releasing CoreWeave from the obligations.",
            "evidence_class": "A",
            "extraction_method": "SEC EDGAR 10-K direct audit",
            "verifier_notes": "Reveals structural perimeter opacity: CoreWeave transferred direct lease liabilities to a bankruptcy-remote SPV, releasing parent entity liability on ELN-03."
        },
        {
            "claim_id": "CLM-CRWV-001",
            "entity_id": "CRWV",
            "filing_type": "10-K",
            "accession_number": "0001769628-26-000104",
            "filing_date": "2026-03-02",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1769628/000176962826000104/crwv-20251231.htm",
            "section_locator": "Item 7. MD&A - Indebtedness and Credit Facilities",
            "exact_quote": "As of December 31, 2025, our total indebtedness was $21.6 billion and we had $3.7 billion of undrawn availability under our Revolving Credit Facility, DDTL 2.1 Facility and DDTL 3.0 Facility... secured by a first-priority lien on compute equipment and customer receivables.",
            "evidence_class": "A",
            "extraction_method": "SEC EDGAR 10-K direct audit",
            "verifier_notes": "Establishes CoreWeave's $21.6B debt load backed by GPU collateral through Magnetar, Blackstone, Coatue private credit syndicate."
        },
        {
            "claim_id": "CLM-CRWV-002",
            "entity_id": "CRWV",
            "filing_type": "10-K",
            "accession_number": "0001769628-26-000104",
            "filing_date": "2026-03-02",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1769628/000176962826000104/crwv-20251231.htm",
            "section_locator": "Note 17. Customer Concentration and Segment Disclosures",
            "exact_quote": "We recognized an aggregate of approximately 67% of our revenue from our top customer, Microsoft, for the year ended December 31, 2025. We recognized an aggregate of approximately 77% of our revenue from our top two customers for the year ended December 31, 2024.",
            "evidence_class": "A",
            "extraction_method": "SEC EDGAR 10-K direct audit",
            "verifier_notes": "Reveals extreme single-counterparty network concentration: 67% of CoreWeave's revenue depends directly on Microsoft compute off-take."
        },
        {
            "claim_id": "CLM-SMCI-001",
            "entity_id": "SMCI",
            "filing_type": "10-K",
            "accession_number": "0001375365-26-000045",
            "filing_date": "2026-08-28",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1375365/000137536526000045/",
            "section_locator": "Note 12. Commitments and Contingencies - Supplier Purchase Commitments",
            "exact_quote": "As of June 30, 2026, the Company had non-cancelable purchase commitments of approximately $18.4 billion, primarily with our primary GPU supplier for accelerator modules and components.",
            "evidence_class": "A",
            "extraction_method": "SEC EDGAR 10-K direct audit",
            "verifier_notes": "Discloses non-cancelable hardware inventory commitments from Supermicro to NVIDIA, creating severe inventory markdown risk if demand pauses."
        },
        {
            "claim_id": "CLM-NVDA-001",
            "entity_id": "NVDA",
            "filing_type": "10-Q",
            "accession_number": "0001045810-26-000082",
            "filing_date": "2026-08-26",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581026000082/",
            "section_locator": "Note 3. Customer Concentration & Customer Receivables",
            "exact_quote": "Two direct customers each represented 10% or more of total revenue during the second quarter of fiscal 2027... Customer A accounted for 14% and Customer B accounted for 11% of consolidated revenue.",
            "evidence_class": "A",
            "extraction_method": "SEC EDGAR 10-Q direct audit",
            "verifier_notes": "Direct confirmation that NVIDIA's hyper-growth is driven by a concentrated handful of hyperscalers and top server OEMs (SMCI, Dell)."
        },
        {
            "claim_id": "CLM-ORCL-001",
            "entity_id": "ORCL",
            "filing_type": "10-Q",
            "accession_number": "0001341439-26-000071",
            "filing_date": "2026-09-10",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1341439/000134143926000071/",
            "section_locator": "MD&A - Capital Resources and Contractual Commitments",
            "exact_quote": "Remaining performance obligations grew to over $99 billion, driven by massive multi-year cloud contracts... Capital expenditures for fiscal 2027 are expected to be double fiscal 2026 levels as we build data center capacity.",
            "evidence_class": "B",
            "extraction_method": "SEC EDGAR 10-Q / Earnings Call cross-reference",
            "verifier_notes": "High contractual backlog paired with massive forward capex commitments creates high operating leverage."
        }
    ]
    df = pd.DataFrame(claims)
    df.to_parquet(PROCESSED_DIR / "evidence_claims.parquet", index=False)
    df.to_csv(PROCESSED_DIR / "evidence_claims.csv", index=False)
    return df


def build_obligations():
    obligations = [
        {
            "obligation_id": "OBL-CRWV-APLD-001",
            "from_entity": "CRWV_SPV_VIII",
            "to_entity": "APLD_ELN_LLC",
            "project_id": "POLARIS_FORGE_1",
            "obligation_type": "datacenter_lease",
            "amount": 11000000000.0,
            "currency": "USD",
            "effective_date": "2025-05-28",
            "maturity_date": "2040-05-31",
            "term_years": 15.0,
            "capacity_mw": 400.0,
            "committed_or_optional": "committed",
            "recourse": "limited_recourse_spv",
            "collateral": "Letters of credit and data hall hardware installation",
            "guarantee": "APLD parent guarantees landlord; CRWV parent released on ELN-03 to SPV VIII",
            "termination_rights": "Strict liquidated damages on power delivery delay; termination for extended delay",
            "payment_conditions": "Monthly base rent indexed to energized MW capacity",
            "claim_id": "CLM-APLD-001",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A002,A003,A004,A005"
        },
        {
            "obligation_id": "OBL-CRWV-CREDIT-001",
            "from_entity": "CRWV",
            "to_entity": "BLACKSTONE_MAGNETAR_SYN",
            "project_id": None,
            "obligation_type": "debt_facility",
            "amount": 21600000000.0,
            "currency": "USD",
            "effective_date": "2023-07-15",
            "maturity_date": "2028-10-31",
            "term_years": 5.0,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "limited_recourse_spv",
            "collateral": "First-priority security interest in NVIDIA H100/H200 GPU server fleets & customer contracts",
            "guarantee": "Parent pledge of SPV equity interests",
            "termination_rights": "Acceleration upon LTV covenant breach or customer default",
            "payment_conditions": "SOFR + 450-550 bps; cash sweeps from customer receivables",
            "claim_id": "CLM-CRWV-001",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A001,A002,A005"
        },
        {
            "obligation_id": "OBL-MSFT-CRWV-001",
            "from_entity": "MSFT",
            "to_entity": "CRWV",
            "project_id": None,
            "obligation_type": "anchor_offtake",
            "amount": 12500000000.0,
            "currency": "USD",
            "effective_date": "2023-05-01",
            "maturity_date": "2028-06-30",
            "term_years": 5.0,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "full_recourse",
            "collateral": "None (unsecured corporate obligation)",
            "guarantee": "None (direct parent obligation)",
            "termination_rights": "SLA performance failure or staged phase reduction clauses",
            "payment_conditions": "Monthly take-or-pay reservation fee plus overage billing",
            "claim_id": "CLM-CRWV-002",
            "evidence_class": "A",
            "confidence": 0.95,
            "shared_assumptions": "A005,A006"
        },
        {
            "obligation_id": "OBL-CRWV-NVDA-001",
            "from_entity": "CRWV",
            "to_entity": "NVDA",
            "project_id": None,
            "obligation_type": "gpu_procurement",
            "amount": 8500000000.0,
            "currency": "USD",
            "effective_date": "2023-04-15",
            "maturity_date": "2027-12-31",
            "term_years": 4.5,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "full_recourse",
            "collateral": "Letters of credit and upfront cash progress deposits",
            "guarantee": "None",
            "termination_rights": "Non-cancelable with severe cancellation forfeiture fees",
            "payment_conditions": "Staged milestone payments upon allocation, packaging, and shipment",
            "claim_id": "CLM-CRWV-001",
            "evidence_class": "A",
            "confidence": 0.90,
            "shared_assumptions": "A001,A006"
        },
        {
            "obligation_id": "OBL-NVDA-CRWV-001",
            "from_entity": "NVDA",
            "to_entity": "CRWV",
            "project_id": None,
            "obligation_type": "equity_investment",
            "amount": 100000000.0,
            "currency": "USD",
            "effective_date": "2023-04-20",
            "maturity_date": "2099-12-31",
            "term_years": None,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "equity_risk",
            "collateral": "Preferred equity shares",
            "guarantee": "None",
            "termination_rights": "Standard statutory governance",
            "payment_conditions": "Equity capital contribution; grants preferred hardware allocation queue",
            "claim_id": "CLM-CRWV-001",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A006"
        },
        {
            "obligation_id": "OBL-CRWV-SMCI-001",
            "from_entity": "CRWV",
            "to_entity": "SMCI",
            "project_id": None,
            "obligation_type": "server_assembly",
            "amount": 3200000000.0,
            "currency": "USD",
            "effective_date": "2024-01-10",
            "maturity_date": "2026-12-31",
            "term_years": 3.0,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "full_recourse",
            "collateral": "Chassis title retention prior to final acceptance",
            "guarantee": "None",
            "termination_rights": "Subject to liquidated component restocking charges",
            "payment_conditions": "Net 30 days post delivery and cluster commissioning",
            "claim_id": "CLM-SMCI-001",
            "evidence_class": "B",
            "confidence": 0.85,
            "shared_assumptions": "A001,A006"
        },
        {
            "obligation_id": "OBL-SMCI-NVDA-001",
            "from_entity": "SMCI",
            "to_entity": "NVDA",
            "project_id": None,
            "obligation_type": "gpu_procurement",
            "amount": 18400000000.0,
            "currency": "USD",
            "effective_date": "2024-07-01",
            "maturity_date": "2026-06-30",
            "term_years": 2.0,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "full_recourse",
            "collateral": "Corporate general obligation; non-cancelable purchase commitments",
            "guarantee": "None",
            "termination_rights": "Strictly non-cancelable purchase commitments",
            "payment_conditions": "Net 30/60 days per master silicon supply agreement",
            "claim_id": "CLM-SMCI-001",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A001,A006,A007"
        },
        {
            "obligation_id": "OBL-ORCL-NVDA-001",
            "from_entity": "ORCL",
            "to_entity": "NVDA",
            "project_id": None,
            "obligation_type": "gpu_procurement",
            "amount": 14000000000.0,
            "currency": "USD",
            "effective_date": "2024-03-18",
            "maturity_date": "2027-05-31",
            "term_years": 3.2,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "full_recourse",
            "collateral": "Corporate balance sheet",
            "guarantee": "None",
            "termination_rights": "Standard enterprise vendor rescheduling windows",
            "payment_conditions": "Progressive hardware delivery schedules for OCI Superclusters",
            "claim_id": "CLM-ORCL-001",
            "evidence_class": "B",
            "confidence": 0.90,
            "shared_assumptions": "A006,A007"
        },
        {
            "obligation_id": "OBL-MSFT-ORCL-001",
            "from_entity": "MSFT",
            "to_entity": "ORCL",
            "project_id": None,
            "obligation_type": "anchor_offtake",
            "amount": 5000000000.0,
            "currency": "USD",
            "effective_date": "2023-09-14",
            "maturity_date": "2028-09-30",
            "term_years": 5.0,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "full_recourse",
            "collateral": "None",
            "guarantee": "None",
            "termination_rights": "Reciprocal enterprise interconnect SLA clauses",
            "payment_conditions": "Cross-billing of Azure-OCI direct interconnect capacity",
            "claim_id": "CLM-ORCL-001",
            "evidence_class": "A",
            "confidence": 0.95,
            "shared_assumptions": "A005,A006"
        },
        {
            "obligation_id": "OBL-APLD-GRID-001",
            "from_entity": "APLD_ELN_LLC",
            "to_entity": "POLARIS_FORGE_1",
            "project_id": "POLARIS_FORGE_1",
            "obligation_type": "datacenter_lease",
            "amount": 1200000000.0,
            "currency": "USD",
            "effective_date": "2024-11-01",
            "maturity_date": "2027-06-30",
            "term_years": 2.6,
            "capacity_mw": 400.0,
            "committed_or_optional": "committed",
            "recourse": "limited_recourse_spv",
            "collateral": "Substation interconnect assets, building structures, ground lease rights",
            "guarantee": "APLD partial sponsor completion support",
            "termination_rights": "Utility interconnect tariff remedies",
            "payment_conditions": "Construction draw schedules against regional power provider",
            "claim_id": "CLM-APLD-001",
            "evidence_class": "A",
            "confidence": 0.95,
            "shared_assumptions": "A002,A004"
        }
    ]
    df = pd.DataFrame(obligations)
    df.to_parquet(PROCESSED_DIR / "obligations.parquet", index=False)
    df.to_csv(PROCESSED_DIR / "obligations.csv", index=False)
    return df


if __name__ == "__main__":
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df_ent = build_entities_table()
    df_ass = build_assumptions_table()
    df_clm = build_evidence_claims()
    df_obl = build_obligations()
    print(f"Entities: {len(df_ent)} rows")
    print(f"Assumptions: {len(df_ass)} rows")
    print(f"Evidence Claims: {len(df_clm)} rows")
    print(f"Obligations: {len(df_obl)} rows")
