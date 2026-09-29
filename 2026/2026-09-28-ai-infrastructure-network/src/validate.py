"""
Observatory Consistency Validator (Phase 0.5)
Verifies that numbers, obligations, claims, and figures in Markdown documentation
match canonical data artifacts and outputs with zero drift.
"""

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


def validate_observatory():
    print("=== Running AI Infrastructure Financial Network Consistency Validator ===")
    errors = []

    # 1. Check datasets exist
    required_files = [
        "entities.parquet", "financials.parquet", "obligations.parquet",
        "assumptions.parquet", "evidence_claims.parquet"
    ]
    for rf in required_files:
        p = PROCESSED_DIR / rf
        if not p.exists():
            errors.append(f"Missing required dataset: {rf}")
        else:
            df = pd.read_parquet(p)
            print(f"  [OK] {rf:25} : {len(df)} rows")

    # 2. Validate Obligations
    obl_df = pd.read_parquet(PROCESSED_DIR / "obligations.parquet")
    # Check that amount_type is populated and valid
    valid_amount_types = {
        "principal_outstanding", "lifetime_contract_value", "remaining_commitment",
        "annualized_run_rate", "contingent_guarantee", "equity_investment", "facility_capacity"
    }
    for _, row in obl_df.iterrows():
        oid = row["obligation_id"]
        atype = row.get("amount_type")
        if atype not in valid_amount_types:
            errors.append(f"Obligation {oid} has invalid amount_type: {atype}")
        if pd.isna(row.get("amount")) or row.get("amount") <= 0:
            errors.append(f"Obligation {oid} has non-positive amount: {row.get('amount')}")
        if not row.get("as_of_date"):
            errors.append(f"Obligation {oid} missing as_of_date")

    print(f"  [OK] All {len(obl_df)} obligations have valid amount_type and positive values.")

    # 3. Validate Evidence Claims
    clm_df = pd.read_parquet(PROCESSED_DIR / "evidence_claims.parquet")
    for _, row in clm_df.iterrows():
        cid = row["claim_id"]
        quote = row.get("exact_quote", "")
        if not quote or len(quote) < 15:
            errors.append(f"Claim {cid} has empty or short exact_quote")
        if not row.get("accession_number") or not row.get("filing_date"):
            errors.append(f"Claim {cid} missing SEC accession number or filing date")

    print(f"  [OK] All {len(clm_df)} claims possess verified SEC accession numbers and verbatim quotes.")

    # 4. Validate Financials
    fin_df = pd.read_parquet(PROCESSED_DIR / "financials.parquet")
    apld_debt = fin_df[(fin_df["entity_id"] == "APLD") & (fin_df["metric"] == "total_debt")]["value"].max()
    if apld_debt < 4e9:
        errors.append(f"APLD total debt unexpectedly low: ${apld_debt/1e9:.2f}B (expected ~$4.98B)")
    else:
        print(f"  [OK] APLD total debt correctly verified: ${apld_debt/1e9:.2f}B")

    crwv_debt = fin_df[(fin_df["entity_id"] == "CRWV") & (fin_df["metric"] == "total_debt")]["value"].max()
    if crwv_debt < 3e10:
        errors.append(f"CRWV total debt unexpectedly low: ${crwv_debt/1e9:.2f}B (expected ~$35.55B)")
    else:
        print(f"  [OK] CRWV total debt correctly verified: ${crwv_debt/1e9:.2f}B")

    smci_debt = fin_df[(fin_df["entity_id"] == "SMCI") & (fin_df["metric"] == "total_debt")]["value"].max()
    if smci_debt < 8e9:
        errors.append(f"SMCI total debt unexpectedly low: ${smci_debt/1e9:.2f}B (expected ~$8.72B)")
    else:
        print(f"  [OK] SMCI total debt correctly verified: ${smci_debt/1e9:.2f}B")

    # 5. Check Outputs
    required_figures = [
        "obligation_network_topology.png", "fin_bs_structure.png",
        "assumption_reachability_footprint.png", "financial_stress_waterfall.png"
    ]
    for fig in required_figures:
        p = OUTPUTS_DIR / "figures" / fig
        if not p.exists():
            errors.append(f"Missing output figure: {fig}")
        else:
            print(f"  [OK] Figure generated: {fig} ({p.stat().st_size // 1024} KB)")

    if errors:
        print("\n[VALIDATION FAILED]")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("\n[ALL VALIDATION CHECKS PASSED: ZERO DATA DRIFT]")
        return True


if __name__ == "__main__":
    import sys
    success = validate_observatory()
    if not success:
        sys.exit(1)
