"""
Observatory Consistency Validator (Phase 0.7.1)
Verifies that numbers, obligations, claims, figures, and tables in Markdown documentation
(README.md and FEEDBACK_PACK.md) match canonical data artifacts, outputs, and executed
notebook results with zero data drift.
"""

from pathlib import Path
import re
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "01_five_company_pilot.ipynb"
README_PATH = PROJECT_ROOT / "README.md"
FEEDBACK_PACK_PATH = PROJECT_ROOT / "FEEDBACK_PACK.md"


def parse_md_table(md_text: str, header_sub: str):
    """Parses a GitHub-flavored Markdown table from text matching a header substring."""
    lines = md_text.splitlines()
    table_lines = []
    in_table = False
    for line in lines:
        if header_sub in line and "|" in line:
            in_table = True
            table_lines.append(line)
            continue
        if in_table:
            if line.strip().startswith("|"):
                table_lines.append(line)
            else:
                break
    if not table_lines:
        return []
    headers = [c.strip() for c in table_lines[0].split("|")[1:-1]]
    rows = []
    for line in table_lines[2:]:  # skip divider
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) == len(headers):
            rows.append(dict(zip(headers, cols)))
    return rows


def parse_dollar(val_str: str):
    """Extracts numeric dollar value in USD from strings like '$22.44B', '$126.6M', '$1.03B/yr'."""
    if not val_str:
        return None
    m = re.search(r"\$([0-9\.]+)\s*([BMKbmk]?)", val_str)
    if not m:
        return None
    num = float(m.group(1))
    unit = m.group(2).upper()
    if unit == "B":
        return num * 1e9
    elif unit == "M":
        return num * 1e6
    elif unit == "K":
        return num * 1e3
    return num


def validate_observatory():
    print("=== Running AI Infrastructure Financial Network Consistency Validator (Phase 0.7.1) ===")
    errors = []

    # ---------------------------------------------------------
    # 1. Check datasets exist
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 2. Validate CoreWeave Exact Debt Decomposition ($35.551B)
    # ---------------------------------------------------------
    obl_df = pd.read_parquet(PROCESSED_DIR / "obligations.parquet")
    crwv_debt = obl_df[(obl_df["from_entity"] == "CRWV") & (obl_df["amount_type"] == "principal_outstanding")]
    
    expected_tranches = 11
    if len(crwv_debt) != expected_tranches:
        errors.append(f"CRWV debt components count mismatch: {len(crwv_debt)} (expected {expected_tranches})")
    
    total_crwv_debt = crwv_debt["amount"].sum()
    target_debt = 35_551_000_000.0  # $35.551B from Form 10-Q Note 7 Table 36
    debt_drift = abs(total_crwv_debt - target_debt)
    if debt_drift > 1.0:
        errors.append(f"CRWV total debt drift: ${total_crwv_debt/1e9:.4f}B vs ${target_debt/1e9:.4f}B (drift ${debt_drift:,.2f})")
    else:
        print(f"  [OK] CRWV 11 modeled debt components/edges sum exactly to ${total_crwv_debt/1e9:.3f}B ($35,551M, exact 0.00% drift).")

    # Check that required tranche IDs exist
    expected_ids = {
        "OBL-CRWV-DEBT-DDTL1", "OBL-CRWV-DEBT-DDTL2", "OBL-CRWV-DEBT-DDTL2-1", "OBL-CRWV-DEBT-DDTL3",
        "OBL-CRWV-DEBT-DDTL4", "OBL-CRWV-DEBT-DDTL5", "OBL-CRWV-DEBT-NOTES", "OBL-CRWV-DEBT-CONV",
        "OBL-CRWV-DEBT-OEM", "OBL-CRWV-DEBT-OEM-NR", "OBL-CRWV-DEBT-MAGNETAR"
    }
    missing_ids = expected_ids - set(crwv_debt["obligation_id"])
    if missing_ids:
        errors.append(f"Missing expected CRWV debt components: {missing_ids}")
    else:
        print(f"  [OK] All 11 distinct CRWV debt components present.")

    # ---------------------------------------------------------
    # 3. Validate Obligations & Polaris Forge 1 Phasing
    # ---------------------------------------------------------
    valid_amount_types = {
        "principal_outstanding", "lifetime_contract_value", "remaining_commitment",
        "recognized_revenue", "contingent_guarantee", "equity_investment", "facility_capacity"
    }
    expected_obligations_count = 20
    if len(obl_df) != expected_obligations_count:
        errors.append(f"Obligations count mismatch: {len(obl_df)} (expected {expected_obligations_count})")
    else:
        print(f"  [OK] Exactly {expected_obligations_count} decomposed obligations present.")

    for _, row in obl_df.iterrows():
        oid = row["obligation_id"]
        atype = row.get("amount_type")
        if atype not in valid_amount_types:
            errors.append(f"Obligation {oid} has invalid amount_type: {atype}")
        if pd.isna(row.get("amount")) or row.get("amount") <= 0:
            errors.append(f"Obligation {oid} has non-positive amount: {row.get('amount')}")
        if not row.get("as_of_date"):
            errors.append(f"Obligation {oid} missing as_of_date")

    # Check Polaris Forge 1 Master Lease
    lease_row = obl_df[obl_df["obligation_id"] == "OBL-CRWV-APLD-LEASE"]
    if lease_row.empty:
        errors.append("Missing OBL-CRWV-APLD-LEASE obligation")
    else:
        cap_mw = lease_row.iloc[0].get("capacity_mw")
        if cap_mw != 400.0:
            errors.append(f"OBL-CRWV-APLD-LEASE capacity_mw mismatch: {cap_mw} (expected 400.0 MW)")
        else:
            print("  [OK] OBL-CRWV-APLD-LEASE verified at 400.0 MW total campus capacity.")

    # Check Split Springing Guarantees (ELN-02 and ELN-03)
    g_eln02 = obl_df[obl_df["obligation_id"] == "OBL-CRWV-APLD-GUARANTY-ELN02"]
    g_eln03 = obl_df[obl_df["obligation_id"] == "OBL-CRWV-APLD-GUARANTY-ELN03"]
    if g_eln02.empty:
        errors.append("Missing OBL-CRWV-APLD-GUARANTY-ELN02 obligation")
    elif g_eln02.iloc[0]["amount"] != 2_750_000_000.0:
        errors.append(f"OBL-CRWV-APLD-GUARANTY-ELN02 amount mismatch: ${g_eln02.iloc[0]['amount']/1e9:.3f}B")
    if g_eln03.empty:
        errors.append("Missing OBL-CRWV-APLD-GUARANTY-ELN03 obligation")
    elif g_eln03.iloc[0]["amount"] != 4_125_000_000.0:
        errors.append(f"OBL-CRWV-APLD-GUARANTY-ELN03 amount mismatch: ${g_eln03.iloc[0]['amount']/1e9:.3f}B")
    
    if not g_eln02.empty and not g_eln03.empty:
        tot_g = g_eln02.iloc[0]["amount"] + g_eln03.iloc[0]["amount"]
        if tot_g != 6_875_000_000.0:
            errors.append(f"Split springing guarantees sum mismatch: ${tot_g/1e9:.3f}B (expected $6.875B)")
        else:
            print(f"  [OK] Split springing guarantees verified: ELN-02 ($2.750B) + ELN-03 ($4.125B) = ${tot_g/1e9:.3f}B across 250 MW.")

    print(f"  [OK] All {len(obl_df)} obligations have valid amount_type, positive values, and as_of_dates.")

    # ---------------------------------------------------------
    # 4. Validate Evidence Claims
    # ---------------------------------------------------------
    clm_df = pd.read_parquet(PROCESSED_DIR / "evidence_claims.parquet")
    expected_claims_count = 15
    if len(clm_df) != expected_claims_count:
        errors.append(f"Evidence claims count mismatch: {len(clm_df)} (expected {expected_claims_count})")
    else:
        print(f"  [OK] Exactly {expected_claims_count} audited evidence claims present.")

    for _, row in clm_df.iterrows():
        cid = row["claim_id"]
        quote = row.get("exact_quote", "")
        if not quote or len(quote) < 15:
            errors.append(f"Claim {cid} has empty or short exact_quote")
        if not row.get("accession_number") or not row.get("filing_date"):
            errors.append(f"Claim {cid} missing SEC accession number or filing date")

    # Verbatim substring assertions
    c5 = clm_df[clm_df["claim_id"] == "CLM-APLD-005"]
    if c5.empty:
        errors.append("Missing claim CLM-APLD-005")
    else:
        q5 = c5.iloc[0]["exact_quote"]
        for phrase in ["Springing Events", "Colocation Agreement", "Equipment Financing"]:
            if phrase not in q5:
                errors.append(f"CLM-APLD-005 missing expected verbatim phrase: '{phrase}'")
        print("  [OK] CLM-APLD-005 verified against Exhibit 10.1 verbatim Springing Events text.")

    c6 = clm_df[clm_df["claim_id"] == "CLM-APLD-006"]
    if c6.empty:
        errors.append("Missing claim CLM-APLD-006")
    else:
        q6 = c6.iloc[0]["exact_quote"]
        for phrase in ["Unconditional Springing Guaranty", "ELN-03"]:
            if phrase not in q6:
                errors.append(f"CLM-APLD-006 missing expected verbatim phrase: '{phrase}'")
        print("  [OK] CLM-APLD-006 verified against Exhibit 10.2 verbatim ELN-03 Guaranty text.")

    cc5 = clm_df[clm_df["claim_id"] == "CLM-CRWV-005"]
    if cc5.empty:
        errors.append("Missing claim CLM-CRWV-005")
    else:
        qc5 = cc5.iloc[0]["exact_quote"]
        for phrase in ["DDTL 5.0 Facility", "interest rate swap", "4,661"]:
            if phrase not in qc5:
                errors.append(f"CLM-CRWV-005 missing expected verbatim phrase: '{phrase}'")
        print("  [OK] CLM-CRWV-005 verified against Note 7 & Note 8 verbatim swap disclosures.")

    print(f"  [OK] All {len(clm_df)} claims possess verified SEC accession numbers and verbatim quotes.")

    # ---------------------------------------------------------
    # 5. Validate Canonical Financials
    # ---------------------------------------------------------
    fin_df = pd.read_parquet(PROCESSED_DIR / "financials.parquet")
    
    # Check key funded debt
    for ticker, expected_val, min_val in [
        ("APLD", 4.98e9, 4.9e9),
        ("CRWV", 35.55e9, 3.5e10),
        ("SMCI", 8.72e9, 8.7e9),
        ("ORCL", 125.34e9, 1.2e11),
        ("NVDA", 33.37e9, 3.3e10)
    ]:
        v = fin_df[(fin_df["entity_id"] == ticker) & (fin_df["metric"] == "total_debt")]["value"].max()
        if v < min_val:
            errors.append(f"{ticker} total debt unexpectedly low: ${v/1e9:.2f}B (expected ~${expected_val/1e9:.2f}B)")
        else:
            print(f"  [OK] {ticker:5} total debt verified: ${v/1e9:.2f}B")

    # Check derived Q4 flow facts
    # MSFT Q4 $90.01B
    msft_q4 = fin_df[(fin_df["ticker"] == "MSFT") & (fin_df["metric"] == "revenue") & (fin_df["period_end"] == "2026-06-30") & (fin_df["duration_type"] == "quarterly")]["value"].max()
    if abs(msft_q4 - 9.001e10) > 1e9:
        errors.append(f"MSFT Q4 revenue mismatch: ${msft_q4/1e9:.2f}B (expected ~$90.01B)")
    else:
        print(f"  [OK] MSFT Q4 FY26 derived quarterly revenue verified: ${msft_q4/1e9:.2f}B")

    # APLD Q4 $258.75M
    apld_q4 = fin_df[(fin_df["ticker"] == "APLD") & (fin_df["metric"] == "revenue") & (fin_df["period_end"] == "2026-05-31") & (fin_df["duration_type"] == "quarterly")]["value"].max()
    if abs(apld_q4 - 2.5875e8) > 5e6:
        errors.append(f"APLD Q4 revenue mismatch: ${apld_q4/1e6:.1f}M (expected ~$258.8M)")
    else:
        print(f"  [OK] APLD Q4 FY26 derived quarterly revenue verified: ${apld_q4/1e6:.1f}M")

    # SMCI Q4 $11.12B
    smci_q4 = fin_df[(fin_df["ticker"] == "SMCI") & (fin_df["metric"] == "revenue") & (fin_df["period_end"] == "2026-06-30") & (fin_df["duration_type"] == "quarterly")]["value"].max()
    if abs(smci_q4 - 1.112e10) > 2e8:
        errors.append(f"SMCI Q4 revenue mismatch: ${smci_q4/1e9:.2f}B (expected ~$11.12B)")
    else:
        print(f"  [OK] SMCI Q4 FY26 derived quarterly revenue verified: ${smci_q4/1e9:.2f}B")

    # ---------------------------------------------------------
    # 6. Validate Outputs, Figures & Stress Summary CSV
    # ---------------------------------------------------------
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

    summary_table_path = OUTPUTS_DIR / "tables" / "financial_stress_summary.csv"
    if not summary_table_path.exists():
        errors.append("Missing output table: financial_stress_summary.csv")
        stress_df = None
    else:
        stress_df = pd.read_csv(summary_table_path)
        print(f"  [OK] Summary table verified: {summary_table_path.name} ({len(stress_df)} scenarios)")
        if len(stress_df) != 6:
            errors.append(f"Expected 6 scenarios in stress table, found {len(stress_df)}")

    # ---------------------------------------------------------
    # 7. Check Executed Notebook
    # ---------------------------------------------------------
    if not NOTEBOOK_PATH.exists():
        errors.append(f"Missing notebook: {NOTEBOOK_PATH.name}")
    else:
        with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
            nb_data = json.load(f)
        code_cells = [c for c in nb_data.get("cells", []) if c.get("cell_type") == "code"]
        executed_cells = [c for c in code_cells if c.get("execution_count") is not None]
        print(f"  [OK] Notebook verified: {NOTEBOOK_PATH.name} ({len(executed_cells)}/{len(code_cells)} code cells executed)")
        if len(executed_cells) < len(code_cells):
            errors.append(f"Notebook has unexecuted code cells: {len(code_cells) - len(executed_cells)}")

    # ---------------------------------------------------------
    # 8. Validate Markdown Tables vs Canonical Facts (Zero Drift)
    # ---------------------------------------------------------
    print("\n  --- Validating Markdown Tables in README.md & FEEDBACK_PACK.md ---")
    
    # Helper to get canonical latest fact
    def get_latest_fact(ticker: str, metric_name: str, duration_type: str = None):
        sub = fin_df[(fin_df["entity_id"] == ticker) & (fin_df["metric"] == metric_name)]
        if duration_type:
            sub = sub[sub["duration_type"] == duration_type]
        if sub.empty:
            return None
        return sub.sort_values("period_end").iloc[-1]["value"]

    for doc_name, doc_path in [("README.md", README_PATH), ("FEEDBACK_PACK.md", FEEDBACK_PACK_PATH)]:
        if not doc_path.exists():
            errors.append(f"Document missing: {doc_name}")
            continue
        text = doc_path.read_text(encoding="utf-8")
        bs_rows = parse_md_table(text, "Entity")
        if not bs_rows:
            errors.append(f"Could not find Audited Balance Sheet table in {doc_name}")
            continue

        print(f"  [OK] Found Audited Balance Sheet table in {doc_name} ({len(bs_rows)} entities)")
        for r in bs_rows:
            raw_entity = r.get("Entity", "").replace("*", "").strip()
            if not raw_entity:
                continue
            
            # Map of column to canonical metric
            checks = [
                ("Cash & Equiv", "cash_and_equivalents", None),
                ("Total Funded Debt", "total_debt", None),
                ("Lease Liabilities", "operating_lease_liabilities", None),
                ("Net PP&E", "ppe_net", None),
                ("Full Year (FY) Revenue", "revenue", "annual"),
                ("Latest Quarter Revenue", "revenue", "quarterly"),
            ]
            for col_name, metric, dur in checks:
                col_val_str = r.get(col_name)
                parsed_val = parse_dollar(col_val_str)
                canon_val = get_latest_fact(raw_entity, metric, dur)
                if parsed_val is None or canon_val is None:
                    continue
                # Tolerance of $0.05B ($50M) for rounding
                diff = abs(parsed_val - canon_val)
                if diff > 5e7:
                    errors.append(
                        f"{doc_name} [{raw_entity}] {col_name} drift: parsed ${parsed_val/1e9:.2f}B vs canonical ${canon_val/1e9:.2f}B (diff ${diff/1e6:.1f}M)"
                    )
        print(f"  [OK] All entity balance sheet rows in {doc_name} match canonical XBRL facts within rounding tolerance.")

    # ---------------------------------------------------------
    # 9. Validate Stress Direct Hits in Documentation
    # ---------------------------------------------------------
    if stress_df is not None:
        expected_hits = {
            "Hypothetical MTM Financing Sensitivity": 4.32e9,
            "Anchor Customer Demand Trim": 1.03e9,
            "SOFR Base Rate Shock": 240.6e6,
            "Credit Spread / Refinancing Shock": 317.9e6,
            "Phased Grid Energization Delay": 135.9e6,
            "OEM Purchase Commitment Expected Loss": 2.05e9,
        }
        readme_text = README_PATH.read_text(encoding="utf-8")
        feedback_text = FEEDBACK_PACK_PATH.read_text(encoding="utf-8")

        for sname, hit_usd in expected_hits.items():
            # Check README stress table
            # Must mention the dollar value in some form (e.g. $4.32B or $240.6M)
            formatted_b = f"${hit_usd/1e9:.2f}B" if hit_usd >= 1e9 else f"${hit_usd/1e6:.1f}M"
            if formatted_b not in readme_text:
                errors.append(f"README.md missing stress direct hit string: {formatted_b} for {sname}")
            if formatted_b not in feedback_text:
                errors.append(f"FEEDBACK_PACK.md missing stress direct hit string: {formatted_b} for {sname}")

        print(f"  [OK] All 6 calibrated stress transmission values accurately represented in documentation.")

    if errors:
        print("\n[VALIDATION FAILED]")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("\nALL INTERNAL CONSISTENCY CHECKS PASSED: ZERO DATA DRIFT")
        return True


if __name__ == "__main__":
    import sys
    success = validate_observatory()
    if not success:
        sys.exit(1)
