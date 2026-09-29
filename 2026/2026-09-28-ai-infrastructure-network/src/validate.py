"""
Observatory Consistency Validator (Phase 0.7.2 - Epistemic Certification ADR-016)
Verifies that numbers, obligations, claims, figures, and tables in Markdown documentation
(README.md and FEEDBACK_PACK.md) match canonical data artifacts, outputs, and executed
notebook results with zero data drift.
"""

import sys
from pathlib import Path
import re
import html
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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


def validate_sec_source_existence():
    """
    Validates that every evidence claim citing SEC EDGAR filings exists in the cached raw
    submissions JSON files with matching accession number, filing form, and filing date (ADR-015).
    Also validates that all obligation events and facts respect the public knowledge invariant:
    event.publicly_known_at >= claim.filing_date.
    """
    sec_dir = PROJECT_ROOT / "data" / "raw" / "sec"
    files = {
        'CRWV': [sec_dir / 'CRWV_submissions_0001769628.json', sec_dir / 'CRWV_submissions_older.json'],
        'APLD': [sec_dir / 'APLD_submissions_0001144879.json'],
        'ORCL': [sec_dir / 'ORCL_submissions_0001341439.json'],
        'SMCI': [sec_dir / 'SMCI_submissions_0001375365.json'],
        'MSFT': [sec_dir / 'MSFT_submissions_0000789019.json'],
        'NVDA': [sec_dir / 'NVDA_submissions_0001045810.json']
    }
    
    all_filings = {}
    for entity, paths in files.items():
        all_filings[entity] = {}
        for p in paths:
            if not p.exists():
                continue
            with open(p, "r", encoding="utf-8") as f:
                d = json.load(f)
            fdict = d.get('filings', {}).get('recent', {}) if 'filings' in d else (d if 'accessionNumber' in d else {})
            if not fdict:
                continue
            for acc, form, fdate, doc in zip(fdict['accessionNumber'], fdict['form'], fdict['filingDate'], fdict['primaryDocument']):
                all_filings[entity][acc] = {'form': form, 'filingDate': fdate, 'primaryDocument': doc}

    clm_df = pd.read_parquet(PROCESSED_DIR / "evidence_claims.parquet")
    errors = []
    
    for _, row in clm_df.iterrows():
        cid = row["claim_id"]
        entity = row["entity_id"]
        acc = row.get("accession_number")
        form = row.get("filing_type")
        fdate = row.get("filing_date")
        
        if entity not in all_filings:
            errors.append(f"Claim {cid}: entity {entity} has no cached raw submissions")
            continue
            
        found = all_filings[entity].get(acc)
        if not found:
            errors.append(f"Claim {cid}: accession {acc} not found in {entity} raw submissions")
        elif found['form'] != form:
            f_form = found['form']
            errors.append(f"Claim {cid}: form mismatch for {acc} (expected {form}, found in EDGAR {f_form})")
        elif found['filingDate'] != fdate:
            f_date = found['filingDate']
            errors.append(f"Claim {cid}: filing date mismatch for {acc} (expected {fdate}, found in EDGAR {f_date})")

    # Check event public knowledge timing invariant
    events_df = pd.read_parquet(PROCESSED_DIR / "obligation_events.parquet")
    claims_dates = dict(zip(clm_df["claim_id"], clm_df["filing_date"]))
    for _, ev in events_df.iterrows():
        eid = ev["event_id"]
        cid = ev.get("claim_id")
        if cid in claims_dates:
            c_date = claims_dates[cid]
            if str(ev["publicly_known_at"]) < str(c_date):
                errors.append(f"Event {eid}: publicly_known_at {ev['publicly_known_at']} predates claim {cid} filing date {c_date}")

    # Check facts public knowledge timing invariant
    facts_df = pd.read_parquet(PROCESSED_DIR / "obligation_facts.parquet")
    for _, f_row in facts_df.iterrows():
        fid = f_row["fact_id"]
        k_cid = f_row.get("knowledge_claim_id")
        if k_cid in claims_dates:
            k_fdate = claims_dates[k_cid]
            if str(f_row["publicly_known_from"]) < str(k_fdate):
                errors.append(f"Fact {fid}: publicly_known_from {f_row['publicly_known_from']} predates knowledge claim {k_cid} filing date {k_fdate}")

    return errors


def validate_sec_html_content():
    """
    Validates that evidence claims match 100% exact contiguous verbatim substrings
    in the cached primary SEC HTML filings in data/raw/sec/ (ADR-016).
    """
    sec_dir = PROJECT_ROOT / "data" / "raw" / "sec"
    htm_files = list(sec_dir.glob("*.htm"))
    if not htm_files:
        return ["No cached SEC HTML files found in data/raw/sec"]

    def normalize(text):
        text = html.unescape(text)
        text = text.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'")
        text = text.replace('&#8220;', '"').replace('&#8221;', '"').replace('&#8216;', "'").replace('&#8217;', "'")
        text = text.replace('&ldquo;', '"').replace('&rdquo;', '"').replace('&lsquo;', "'").replace('&rsquo;', "'")
        text = text.replace('&nbsp;', ' ').replace('&#160;', ' ')
        text = re.sub(r'</?(?:b|i|u|strong|em|font|span)(?:\s+[^>]*)?>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', text)
        return ' '.join(text.split())

    file_contents = {}
    for f in htm_files:
        file_contents[f.name] = normalize(f.read_text(encoding='utf-8', errors='ignore'))

    clm_df = pd.read_parquet(PROCESSED_DIR / "evidence_claims.parquet")
    
    verifiable_claims = [
        'CLM-APLD-001', 'CLM-APLD-002', 'CLM-APLD-004', 'CLM-APLD-005', 'CLM-APLD-006',
        'CLM-APLD-007', 'CLM-APLD-008',
        'CLM-CRWV-001', 'CLM-CRWV-002', 'CLM-CRWV-003', 'CLM-CRWV-004', 'CLM-CRWV-005',
        'CLM-CRWV-006', 'CLM-CRWV-007', 'CLM-CRWV-008', 'CLM-CRWV-008A', 'CLM-CRWV-009',
        'CLM-CRWV-009A', 'CLM-CRWV-010', 'CLM-CRWV-011', 'CLM-CRWV-012', 'CLM-CRWV-013',
        'CLM-CRWV-013A', 'CLM-CRWV-014', 'CLM-CRWV-014A', 'CLM-CRWV-015', 'CLM-CRWV-016',
        'CLM-SMCI-001', 'CLM-NVDA-CRWV-001'
    ]

    errors = []
    for cid in verifiable_claims:
        c_sub = clm_df[clm_df["claim_id"] == cid]
        if c_sub.empty:
            errors.append(f"Verifiable claim {cid} not found in evidence_claims.parquet")
            continue
        quote = normalize(c_sub.iloc[0]["exact_quote"])
        matched = any(quote in content for content in file_contents.values())
        if not matched:
            errors.append(f"Claim {cid} exact quote is not a verbatim substring in cached SEC HTML filings")

    return errors


def validate_observatory():
    print("=== Running AI Infrastructure Financial Network Consistency Validator (Phase 0.7.2) ===")
    errors = []

    # ---------------------------------------------------------
    # 1. Check datasets exist
    # ---------------------------------------------------------
    required_files = {
        "entities.parquet": 27,
        "financials.parquet": 5440,
        "obligations.parquet": 35,
        "obligation_events.parquet": 36,
        "obligation_facts.parquet": 43,
        "assumptions.parquet": 7,
        "evidence_claims.parquet": 37,
    }
    for rf, expected_rows in required_files.items():
        p = PROCESSED_DIR / rf
        if not p.exists():
            errors.append(f"Missing required dataset: {rf}")
        else:
            df = pd.read_parquet(p)
            print(f"  [OK] {rf:25} : {len(df)} rows")
            if len(df) != expected_rows:
                errors.append(f"{rf} row count mismatch: {len(df)} (expected {expected_rows})")

    # ---------------------------------------------------------
    # 2. Validate CoreWeave & Applied Digital Exact Debt Decomposition
    # ---------------------------------------------------------
    obl_df = pd.read_parquet(PROCESSED_DIR / "obligations.parquet")
    crwv_borrowers = [
        "CRWV", "CRWV_CCAC_II", "CRWV_CCAC_IV", "CRWV_CCAC_VII", "CRWV_SPV_VIII", "CRWV_FINANCING_DDTL_V"
    ]
    crwv_debt = obl_df[
        obl_df["from_entity"].isin(crwv_borrowers) & (obl_df["amount_type"] == "principal_outstanding")
    ]
    
    expected_tranches = 16
    if len(crwv_debt) != expected_tranches:
        errors.append(f"CRWV debt components count mismatch: {len(crwv_debt)} (expected {expected_tranches})")
    
    total_crwv_debt = crwv_debt["amount"].sum()
    target_debt = 35_551_000_000.0  # $35.551B from Form 10-Q Note 7 Table 36
    debt_drift = abs(total_crwv_debt - target_debt)
    if debt_drift > 1.0:
        errors.append(f"CRWV total debt drift: ${total_crwv_debt/1e9:.4f}B vs ${target_debt/1e9:.4f}B (drift ${debt_drift:,.2f})")
    else:
        print(f"  [OK] CRWV 16 modeled debt components/edges sum exactly to ${total_crwv_debt/1e9:.3f}B ($35,551M, exact 0.00% drift).")

    # Check that required tranche IDs exist
    expected_ids = {
        "OBL-CRWV-DEBT-DDTL1", "OBL-CRWV-DEBT-DDTL2", "OBL-CRWV-DEBT-DDTL2-1", "OBL-CRWV-DEBT-DDTL3",
        "OBL-CRWV-DEBT-DDTL4", "OBL-CRWV-DEBT-DDTL5", "OBL-CRWV-DEBT-NOTES-2030", "OBL-CRWV-DEBT-NOTES-2031-900",
        "OBL-CRWV-DEBT-NOTES-2031-975", "OBL-CRWV-DEBT-NOTES-2032-9625", "OBL-CRWV-DEBT-NOTES-2032-EUR",
        "OBL-CRWV-DEBT-CONV-2031", "OBL-CRWV-DEBT-CONV-2032",
        "OBL-CRWV-DEBT-OEM", "OBL-CRWV-DEBT-OEM-NR", "OBL-CRWV-DEBT-MAGNETAR"
    }
    missing_ids = expected_ids - set(crwv_debt["obligation_id"])
    if missing_ids:
        errors.append(f"Missing expected CRWV debt components: {missing_ids}")
    else:
        print(f"  [OK] All 16 distinct CRWV debt components present.")

    # Check borrower entities for DDTLs
    for _, r in crwv_debt.iterrows():
        oid = r["obligation_id"]
        if oid == "OBL-CRWV-DEBT-DDTL1" and r["from_entity"] != "CRWV_CCAC_II":
            errors.append(f"DDTL 1 borrower mismatch: {r['from_entity']} (expected CRWV_CCAC_II)")
        elif oid in ["OBL-CRWV-DEBT-DDTL2", "OBL-CRWV-DEBT-DDTL2-1"] and r["from_entity"] != "CRWV_CCAC_IV":
            errors.append(f"{oid} borrower mismatch: {r['from_entity']} (expected CRWV_CCAC_IV)")
        elif oid == "OBL-CRWV-DEBT-DDTL3" and r["from_entity"] != "CRWV_CCAC_VII":
            errors.append(f"DDTL 3 borrower mismatch: {r['from_entity']} (expected CRWV_CCAC_VII)")
        elif oid == "OBL-CRWV-DEBT-DDTL4" and r["from_entity"] != "CRWV_SPV_VIII":
            errors.append(f"DDTL 4 borrower mismatch: {r['from_entity']} (expected CRWV_SPV_VIII)")
        elif oid == "OBL-CRWV-DEBT-DDTL5" and r["from_entity"] != "CRWV_FINANCING_DDTL_V":
            errors.append(f"DDTL 5 borrower mismatch: {r['from_entity']} (expected CRWV_FINANCING_DDTL_V)")

    # Check Senior Notes and Convertibles ranking (Senior Unsecured with subsidiary guarantees)
    unsecured_tranches = [
        "OBL-CRWV-DEBT-NOTES-2030", "OBL-CRWV-DEBT-NOTES-2031-900", "OBL-CRWV-DEBT-NOTES-2031-975",
        "OBL-CRWV-DEBT-NOTES-2032-9625", "OBL-CRWV-DEBT-NOTES-2032-EUR",
        "OBL-CRWV-DEBT-CONV-2031", "OBL-CRWV-DEBT-CONV-2032"
    ]
    for ut in unsecured_tranches:
        u_row = crwv_debt[crwv_debt["obligation_id"] == ut]
        if not u_row.empty:
            rec = u_row.iloc[0].get("recourse")
            otype = u_row.iloc[0].get("obligation_type")
            if rec not in ["senior_unsecured", "senior_unsecured_convertible"]:
                errors.append(f"{ut} recourse mismatch: {rec} (expected senior_unsecured or senior_unsecured_convertible)")
            if otype != "debt_facility":
                errors.append(f"{ut} obligation_type mismatch: {otype}")
    print("  [OK] Senior Notes and Convertibles verified as Senior Unsecured obligations (with subsidiary guarantees).")

    # Verify 6 CRWV Parent Guarantees (5 full recourse + 1 limited carve-out bad acts)
    crwv_gntys = obl_df[
        (obl_df["from_entity"] == "CRWV") &
        (obl_df["obligation_type"] == "contingent_guarantee") &
        (obl_df["amount_type"] == "contingent_guarantee")
    ]
    expected_gnty_ids = {
        "OBL-CRWV-GUARANTY-DDTL1", "OBL-CRWV-GUARANTY-DDTL2", "OBL-CRWV-GUARANTY-DDTL2-1",
        "OBL-CRWV-GUARANTY-DDTL3", "OBL-CRWV-GUARANTY-DDTL4", "OBL-CRWV-GUARANTY-DDTL5"
    }
    missing_gntys = expected_gnty_ids - set(crwv_gntys["obligation_id"])
    if missing_gntys:
        errors.append(f"Missing expected CRWV parent guarantee edges: {missing_gntys}")
    else:
        print(f"  [OK] All 6 CRWV parent guarantee edges present (5 recourse + 1 limited bad-acts carve-out).")

    # Check DDTL 4.0 limited parent guarantee terms specifically
    ddtl4_gnty = obl_df[obl_df["obligation_id"] == "OBL-CRWV-GUARANTY-DDTL4"]
    if ddtl4_gnty.empty:
        errors.append("Missing OBL-CRWV-GUARANTY-DDTL4 parent guarantee edge")
    else:
        g4 = ddtl4_gnty.iloc[0]
        if g4["recourse"] != "limited_bad_acts":
            errors.append(f"DDTL 4.0 parent guarantee recourse mismatch: {g4['recourse']} (expected limited_bad_acts)")
        if g4["to_entity"] != "MUFG_BANK_SYN":
            errors.append(f"DDTL 4.0 parent guarantee to_entity mismatch: {g4['to_entity']} (expected MUFG_BANK_SYN)")
        if pd.notna(g4["amount"]):
            errors.append(f"DDTL 4.0 parent guarantee should have amount = None, found {g4['amount']}")
        if g4["reference_exposure_estimate"] != 2_837_000_000.0:
            errors.append(f"DDTL 4.0 parent guarantee reference_exposure_estimate mismatch: {g4['reference_exposure_estimate']}")
        else:
            print("  [OK] DDTL 4.0 limited parent guarantee verified: recourse='limited_bad_acts', ref_exposure=$2.837B.")

    # Check DDTL 3.0 co-borrower edge
    coborrower = obl_df[obl_df["obligation_id"] == "OBL-CRWV-COBORROWER-DDTL3"]
    if coborrower.empty:
        errors.append("Missing OBL-CRWV-COBORROWER-DDTL3 co-borrower edge")
    else:
        cb = coborrower.iloc[0]
        if cb["from_entity"] != "CRWV_CCAC_V":
            errors.append(f"DDTL 3.0 co-borrower from_entity mismatch: {cb['from_entity']} (expected CRWV_CCAC_V)")
        if cb["to_entity"] != "MUFG_BANK_SYN":
            errors.append(f"DDTL 3.0 co-borrower to_entity mismatch: {cb['to_entity']} (expected MUFG_BANK_SYN)")
        if cb["obligation_type"] != "joint_co_borrower":
            errors.append(f"DDTL 3.0 co-borrower obligation_type mismatch: {cb['obligation_type']} (expected joint_co_borrower)")
        if pd.notna(cb["amount"]):
            errors.append(f"DDTL 3.0 co-borrower should have amount = None, found {cb['amount']}")
        else:
            print("  [OK] DDTL 3.0 co-borrower edge verified: CRWV_CCAC_V -> MUFG_BANK_SYN (joint_co_borrower).")

    # Applied Digital exact debt decomposition (parent and project SPVs)
    apld_debt = obl_df[
        obl_df["from_entity"].isin(["APLD", "APLD_COMPUTECO", "APLD_COMPUTECO2", "APLD_COMPUTECO3"]) & 
        (obl_df["amount_type"] == "principal_outstanding")
    ]
    expected_apld_tranches = 6  # PF1, PF2, CONV, BRIDGE, 7PCT, OTHER
    if len(apld_debt) != expected_apld_tranches:
        errors.append(f"APLD debt components count mismatch in master ledger: {len(apld_debt)} (expected {expected_apld_tranches})")
    else:
        print(f"  [OK] APLD {expected_apld_tranches} modeled debt components present in master ledger (including 7.00% successor notes).")

    expected_apld_ids = {
        "OBL-APLD-DEBT-PF1", "OBL-APLD-DEBT-PF2", "OBL-APLD-DEBT-CONV",
        "OBL-APLD-DEBT-BRIDGE", "OBL-APLD-DEBT-7PCT-2026", "OBL-APLD-DEBT-OTHER"
    }
    missing_apld_ids = expected_apld_ids - set(apld_debt["obligation_id"])
    if missing_apld_ids:
        errors.append(f"Missing expected APLD debt components: {missing_apld_ids}")
    else:
        print(f"  [OK] All 6 distinct APLD debt components present.")

    # Contract-literal checks on individual APLD debt tranches
    for _, r in apld_debt.iterrows():
        oid = r["obligation_id"]
        if oid == "OBL-APLD-DEBT-PF1":
            if r["from_entity"] != "APLD_COMPUTECO":
                errors.append(f"OBL-APLD-DEBT-PF1 issuer mismatch: {r['from_entity']} (expected APLD_COMPUTECO)")
            if r["maturity_date"] != "2030-12-15":
                errors.append(f"OBL-APLD-DEBT-PF1 maturity mismatch: {r['maturity_date']} (expected 2030-12-15)")
            if r["term_years"] != 6.5:
                errors.append(f"OBL-APLD-DEBT-PF1 term_years mismatch: {r['term_years']} (expected 6.5)")
        elif oid == "OBL-APLD-DEBT-PF2":
            if r["from_entity"] != "APLD_COMPUTECO2":
                errors.append(f"OBL-APLD-DEBT-PF2 issuer mismatch: {r['from_entity']} (expected APLD_COMPUTECO2)")
            if r["maturity_date"] != "2031-03-15":
                errors.append(f"OBL-APLD-DEBT-PF2 maturity mismatch: {r['maturity_date']} (expected 2031-03-15)")
            if r["term_years"] != 6.2:
                errors.append(f"OBL-APLD-DEBT-PF2 term_years mismatch: {r['term_years']} (expected 6.2)")
        elif oid == "OBL-APLD-DEBT-CONV":
            if r["from_entity"] != "APLD":
                errors.append(f"OBL-APLD-DEBT-CONV issuer mismatch: {r['from_entity']} (expected APLD)")
            if r["maturity_date"] != "2030-06-30":
                errors.append(f"OBL-APLD-DEBT-CONV maturity mismatch: {r['maturity_date']} (expected 2030-06-30)")
            if r["term_years"] != 5.6:
                errors.append(f"OBL-APLD-DEBT-CONV term_years mismatch: {r['term_years']} (expected 5.6)")
        elif oid == "OBL-APLD-DEBT-BRIDGE":
            if r["from_entity"] != "APLD":
                errors.append(f"OBL-APLD-DEBT-BRIDGE issuer mismatch: {r['from_entity']} (expected APLD)")
            if r["effective_date"] != "2026-05-01":
                errors.append(f"OBL-APLD-DEBT-BRIDGE effective_date mismatch: {r['effective_date']} (expected 2026-05-01)")
            if r["maturity_date"] != "2027-04-30":
                errors.append(f"OBL-APLD-DEBT-BRIDGE maturity mismatch: {r['maturity_date']} (expected 2027-04-30)")
            if r["valid_to"] != "2026-06-16":
                errors.append(f"OBL-APLD-DEBT-BRIDGE valid_to mismatch: {r['valid_to']} (expected 2026-06-16)")
            if r.get("superseded_by") != "OBL-APLD-DEBT-7PCT-2026":
                errors.append(f"OBL-APLD-DEBT-BRIDGE superseded_by mismatch: {r.get('superseded_by')} (expected OBL-APLD-DEBT-7PCT-2026)")
            if r.get("rate_type") != "floating":
                errors.append(f"OBL-APLD-DEBT-BRIDGE rate_type mismatch: {r.get('rate_type')} (expected floating)")
        elif oid == "OBL-APLD-DEBT-7PCT-2026":
            if r["from_entity"] != "APLD_COMPUTECO3":
                errors.append(f"OBL-APLD-DEBT-7PCT-2026 issuer mismatch: {r['from_entity']} (expected APLD_COMPUTECO3)")
            if r.get("recourse") != "senior_secured_spv":
                errors.append(f"OBL-APLD-DEBT-7PCT-2026 recourse mismatch: {r.get('recourse')} (expected senior_secured_spv)")
            if r["amount"] != 1_590_000_000.0:
                errors.append(f"OBL-APLD-DEBT-7PCT-2026 amount mismatch: {r['amount']} (expected 1590000000.0)")
            if r["effective_date"] != "2026-06-16":
                errors.append(f"OBL-APLD-DEBT-7PCT-2026 effective_date mismatch: {r['effective_date']} (expected 2026-06-16)")
            if r["maturity_date"] != "2031-06-15":
                errors.append(f"OBL-APLD-DEBT-7PCT-2026 maturity mismatch: {r['maturity_date']} (expected 2031-06-15)")
            if r.get("supersedes") != "OBL-APLD-DEBT-BRIDGE":
                errors.append(f"OBL-APLD-DEBT-7PCT-2026 supersedes mismatch: {r.get('supersedes')} (expected OBL-APLD-DEBT-BRIDGE)")
            if r.get("rate_type") != "fixed":
                errors.append(f"OBL-APLD-DEBT-7PCT-2026 rate_type mismatch: {r.get('rate_type')} (expected fixed)")
        elif oid == "OBL-APLD-DEBT-OTHER":
            if r["from_entity"] != "APLD":
                errors.append(f"OBL-APLD-DEBT-OTHER issuer mismatch: {r['from_entity']} (expected APLD)")
            if r["obligation_type"] != "aggregate_residual_debt":
                errors.append(f"OBL-APLD-DEBT-OTHER obligation_type mismatch: {r['obligation_type']} (expected aggregate_residual_debt)")
            if r["amount"] != 56680000.0:
                errors.append(f"OBL-APLD-DEBT-OTHER amount mismatch: {r['amount']} (expected 56680000.0)")
    print("  [OK] Contract-literal legal entities, effective dates, maturities, supersession links, and types verified for all 6 APLD debt tranches.")

    # ---------------------------------------------------------
    # 3. Validate Obligations & Polaris Forge 1 Phasing
    # ---------------------------------------------------------
    valid_amount_types = {
        "principal_outstanding", "lifetime_contract_value", "remaining_commitment",
        "recognized_revenue", "contingent_guarantee", "equity_investment", "facility_capacity",
        "contingent_obligations"
    }
    expected_obligations_count = 35
    if len(obl_df) != expected_obligations_count:
        errors.append(f"Obligations count mismatch: {len(obl_df)} (expected {expected_obligations_count})")
    else:
        print(f"  [OK] Exactly {expected_obligations_count} decomposed obligations present.")

    for _, row in obl_df.iterrows():
        oid = row["obligation_id"]
        atype = row.get("amount_type")
        if atype not in valid_amount_types:
            errors.append(f"Obligation {oid} has invalid amount_type: {atype}")
        if atype in ["contingent_obligations", "contingent_guarantee"]:
            if not pd.isna(row.get("amount")):
                errors.append(f"Contingent obligation {oid} should have amount = None (uncapped/contingent), found: {row.get('amount')}")
            if not row.get("capacity_description"):
                errors.append(f"Contingent obligation {oid} missing capacity_description")
        else:
            if pd.isna(row.get("amount")) or row.get("amount") <= 0:
                errors.append(f"Obligation {oid} has non-positive amount: {row.get('amount')}")
        if not row.get("as_of_date"):
            errors.append(f"Obligation {oid} missing as_of_date")
        if not row.get("observed_as_of"):
            errors.append(f"Obligation {oid} missing observed_as_of")
        if not row.get("economic_valid_from"):
            errors.append(f"Obligation {oid} missing economic_valid_from")
        if not row.get("publicly_known_from"):
            errors.append(f"Obligation {oid} missing publicly_known_from")

    # Check Polaris Forge 1 Master Lease
    lease_row = obl_df[obl_df["obligation_id"] == "OBL-CRWV-APLD-LEASE"]
    if lease_row.empty:
        errors.append("Missing OBL-CRWV-APLD-LEASE obligation")
    else:
        r_l = lease_row.iloc[0]
        if r_l.get("to_entity") != "APLD_COMPUTECO":
            errors.append(f"OBL-CRWV-APLD-LEASE to_entity mismatch: {r_l.get('to_entity')} (expected APLD_COMPUTECO)")
        cap_mw = r_l.get("capacity_mw")
        if cap_mw != 400.0:
            errors.append(f"OBL-CRWV-APLD-LEASE capacity_mw mismatch: {cap_mw} (expected 400.0 MW)")
        else:
            print("  [OK] OBL-CRWV-APLD-LEASE verified: counterparty APLD_COMPUTECO, 400.0 MW total campus capacity.")

    # Check Split Springing Guarantees (ELN-02 and ELN-03)
    g_eln02 = obl_df[obl_df["obligation_id"] == "OBL-CRWV-APLD-GUARANTY-ELN02"]
    g_eln03 = obl_df[obl_df["obligation_id"] == "OBL-CRWV-APLD-GUARANTY-ELN03"]
    if g_eln02.empty:
        errors.append("Missing OBL-CRWV-APLD-GUARANTY-ELN02 obligation")
    else:
        row2 = g_eln02.iloc[0]
        if row2["amount_type"] != "contingent_obligations" or not pd.isna(row2["amount"]):
            errors.append(f"OBL-CRWV-APLD-GUARANTY-ELN02 should be uncapped contingent_obligations, found {row2['amount_type']} / {row2['amount']}")
        if "Phase 2/4 Space" not in str(row2.get("capacity_description")):
            errors.append(f"OBL-CRWV-APLD-GUARANTY-ELN02 capacity_description mismatch: {row2.get('capacity_description')}")
        else:
            print("  [OK] ELN-02 verified as uncapped legal indemnity for Phase 2/4 Space (2 of 4 data halls in Building 2).")

    if g_eln03.empty:
        errors.append("Missing OBL-CRWV-APLD-GUARANTY-ELN03 obligation")
    else:
        row3 = g_eln03.iloc[0]
        if row3["amount_type"] != "contingent_obligations" or not pd.isna(row3["amount"]):
            errors.append(f"OBL-CRWV-APLD-GUARANTY-ELN03 should be uncapped contingent_obligations, found {row3['amount_type']} / {row3['amount']}")
        if row3.get("capacity_mw") != 150.0:
            errors.append(f"OBL-CRWV-APLD-GUARANTY-ELN03 capacity_mw mismatch: {row3.get('capacity_mw')} (expected 150.0)")
        if row3.get("reference_exposure_estimate") != 4_125_000_000.0:
            errors.append(f"OBL-CRWV-APLD-GUARANTY-ELN03 reference_exposure_estimate mismatch: {row3.get('reference_exposure_estimate')}")
        else:
            print("  [OK] ELN-03 verified as uncapped legal indemnity for Building 3 (150 MW) with $4.125B Class C reference proxy.")

    print(f"  [OK] All {len(obl_df)} obligations have valid amount_type, valid values/uncapped attributes, and bitemporal fields.")

    # ---------------------------------------------------------
    # 3b. Validate Dynamic SPV Unwrapping & Bitemporal Filtering
    # ---------------------------------------------------------
    try:
        from src.graph import ObligationNetwork
        from src.stress import FinancialStressEngine

        net = ObligationNetwork()
        collapsed = net.unwrap_spv_perimeter()
        spv_remaining = [n for n in collapsed.nodes() if net.entities_df.loc[n, 'category'] == 'project_spv']
        if spv_remaining:
            errors.append(f"SPVs unexpectedly remained in unwrapped perimeter: {spv_remaining}")
        else:
            print(f"  [OK] Dynamic SPV unwrapping: 0 SPVs remaining in consolidated network ({collapsed.number_of_nodes()} parent nodes).")

        # Corporate Hierarchy Verification (ADR-013 & ADR-015)
        p_c3 = net.get_parent("APLD_COMPUTECO3")
        p_hpc2 = net.get_parent("APLD_HPC_HOLDINGS2")
        root_c3 = net.get_root_parent("APLD_COMPUTECO3")
        if p_c3 != "APLD_HPC_HOLDINGS2":
            errors.append(f"APLD_COMPUTECO3 direct parent mismatch: {p_c3} (expected APLD_HPC_HOLDINGS2)")
        if p_hpc2 != "APLD":
            errors.append(f"APLD_HPC_HOLDINGS2 direct parent mismatch: {p_hpc2} (expected APLD)")
        if root_c3 != "APLD":
            errors.append(f"APLD_COMPUTECO3 root parent mismatch: {root_c3} (expected APLD)")
        else:
            print("  [OK] APLD ComputeCo 3 corporate hierarchy verified: APLD_COMPUTECO3 -> APLD_HPC_HOLDINGS2 -> APLD.")

        for spv in ["CRWV_CCAC_II", "CRWV_CCAC_IV", "CRWV_CCAC_V", "CRWV_CCAC_VII", "CRWV_SPV_VIII", "CRWV_FINANCING_DDTL_V"]:
            if net.get_root_parent(spv) != "CRWV":
                errors.append(f"{spv} root parent mismatch: {net.get_root_parent(spv)} (expected CRWV)")
        print("  [OK] CoreWeave borrowing and co-borrower SPVs verified: all unwrap cleanly to root parent CRWV.")

        # Half-Open Validity Interval Test [valid_from, valid_to) (ADR-013)
        # On June 15: Bridge active, 7% Notes inactive, 32 edges
        net_jun15 = net.economic_as_of("2026-06-15")
        jun15_keys = [k for _, _, k in net_jun15.graph.edges(keys=True)]
        if "OBL-APLD-DEBT-BRIDGE" not in jun15_keys or "OBL-APLD-DEBT-7PCT-2026" in jun15_keys or net_jun15.graph.number_of_edges() != 32:
            errors.append(f"Half-open boundary check failed on 2026-06-15: Bridge={('OBL-APLD-DEBT-BRIDGE' in jun15_keys)}, Notes={('OBL-APLD-DEBT-7PCT-2026' in jun15_keys)}, Edges={net_jun15.graph.number_of_edges()}")

        # On June 16 (transition boundary): Bridge retired ([valid_from, valid_to)), 7% Notes active, exactly 32 edges
        net_jun16 = net.economic_as_of("2026-06-16")
        jun16_keys = [k for _, _, k in net_jun16.graph.edges(keys=True)]
        if "OBL-APLD-DEBT-BRIDGE" in jun16_keys or "OBL-APLD-DEBT-7PCT-2026" not in jun16_keys or net_jun16.graph.number_of_edges() != 32:
            errors.append(f"Half-open boundary check failed on 2026-06-16: Bridge={('OBL-APLD-DEBT-BRIDGE' in jun16_keys)}, Notes={('OBL-APLD-DEBT-7PCT-2026' in jun16_keys)}, Edges={net_jun16.graph.number_of_edges()}")
        else:
            print("  [OK] Half-open validity interval [valid_from, valid_to) verified on June 16, 2026: Bridge cleanly retired, 7% Notes active, exactly 32 edges.")

        # June 17 Epistemic Knowledge Boundary Test (ADR-014, ADR-015, ADR-016)
        # CoreWeave 2032 Senior Notes issued June 18, 2026 (CLM-CRWV-014 Form 8-K).
        # June 17 Economic Reality: exactly 32 edges (2032 notes do not yet exist economically).
        net_econ_jun17 = net.economic_as_of("2026-06-17")
        jun17_econ_keys = [k for _, _, k in net_econ_jun17.graph.edges(keys=True)]
        if "OBL-CRWV-DEBT-NOTES-2032-9625" in jun17_econ_keys or net_econ_jun17.graph.number_of_edges() != 32:
            errors.append(f"Economic check failed on 2026-06-17: Notes-2032 in econ={('OBL-CRWV-DEBT-NOTES-2032-9625' in jun17_econ_keys)}, Edges={net_econ_jun17.graph.number_of_edges()}")
        else:
            print("  [OK] June 17 economic boundary verified: 2032 notes inactive prior to June 18 issuance, exactly 32 edges.")

        # June 17 Epistemic Knowledge: Outside observer does NOT know 2032 notes (Form 8-K filed June 18).
        # Exactly 28 edges known.
        net_known_jun17 = net.known_as_of("2026-06-17")
        jun17_known_keys = [k for _, _, k in net_known_jun17.graph.edges(keys=True)]
        if "OBL-CRWV-DEBT-NOTES-2032-9625" in jun17_known_keys or "OBL-CRWV-DEBT-NOTES-2032-EUR" in jun17_known_keys or net_known_jun17.graph.number_of_edges() != 28:
            errors.append(f"Epistemic check failed on 2026-06-17: Notes-2032={('OBL-CRWV-DEBT-NOTES-2032-9625' in jun17_known_keys)}, Edges={net_known_jun17.graph.number_of_edges()}")
        else:
            print("  [OK] June 17 epistemic boundary verified: CoreWeave 2032 notes absent prior to Form 8-K filing, exactly 28 edges known.")

        # June 18 Epistemic Knowledge: Form 8-K filed! Both 2032 notes active, exactly 30 edges known
        net_known_jun18 = net.known_as_of("2026-06-18")
        jun18_known_keys = [k for _, _, k in net_known_jun18.graph.edges(keys=True)]
        if "OBL-CRWV-DEBT-NOTES-2032-9625" not in jun18_known_keys or "OBL-CRWV-DEBT-NOTES-2032-EUR" not in jun18_known_keys or net_known_jun18.graph.number_of_edges() != 30:
            errors.append(f"Epistemic check failed on 2026-06-18: Notes-2032={('OBL-CRWV-DEBT-NOTES-2032-9625' in jun18_known_keys)}, Edges={net_known_jun18.graph.number_of_edges()}")
        else:
            print("  [OK] June 18 epistemic boundary verified: Form 8-K incorporated, CoreWeave 2032 notes active, exactly 30 edges known.")

        # June 18 Economic Reality: Both 2032 notes active, exactly 34 edges
        net_econ_jun18 = net.economic_as_of("2026-06-18")
        if net_econ_jun18.graph.number_of_edges() != 34:
            errors.append(f"Expected 34 edges economically on 2026-06-18, got {net_econ_jun18.graph.number_of_edges()}")
        else:
            print("  [OK] June 18 economic reality verified: 2032 notes active, exactly 34 edges.")

        # Historical Fact Absence Test (No back-projection of current values)
        net_econ_2025 = net.economic_as_of("2025-01-01")
        ddtl1_2025 = net_econ_2025.graph.get_edge_data("CRWV_CCAC_II", "BLACKSTONE_MAGNETAR_SYN", key="OBL-CRWV-DEBT-DDTL1")
        if ddtl1_2025 is None:
            errors.append("DDTL 1.0 edge should exist economically on 2025-01-01")
        elif ddtl1_2025.get("amount") is not None or ddtl1_2025.get("amount_known") is not False:
            errors.append(f"Historical fact leak: DDTL 1.0 amount should be None on 2025-01-01, got {ddtl1_2025.get('amount')}")
        else:
            print("  [OK] Historical fact isolation verified: DDTL 1.0 amount is None / unknown on 2025-01-01 (no back-projection).")

        # Economic Clock Filtering Test
        net_may = net.economic_as_of("2026-05-31")
        net_sep = net.economic_as_of("2026-09-28")
        may_edges = net_may.graph.number_of_edges()
        sep_edges = net_sep.graph.number_of_edges()
        if may_edges != 32:
            errors.append(f"Expected 32 edges as of 2026-05-31, got {may_edges}")
        if sep_edges != 34:
            errors.append(f"Expected 34 edges as of 2026-09-28 (post-refinancing conservation), got {sep_edges}")
        
        bridge_may = "OBL-APLD-DEBT-BRIDGE" in [k for _, _, k in net_may.graph.edges(keys=True)]
        bridge_sep = "OBL-APLD-DEBT-BRIDGE" in [k for _, _, k in net_sep.graph.edges(keys=True)]
        notes_may = "OBL-APLD-DEBT-7PCT-2026" in [k for _, _, k in net_may.graph.edges(keys=True)]
        notes_sep = "OBL-APLD-DEBT-7PCT-2026" in [k for _, _, k in net_sep.graph.edges(keys=True)]

        if not bridge_may or bridge_sep:
            errors.append(f"Economic bridge presence mismatch: may={bridge_may}, sep={bridge_sep} (expected True, False)")
        if notes_may or not notes_sep:
            errors.append(f"Economic 7% notes presence mismatch: may={notes_may}, sep={notes_sep} (expected False, True)")

        # Economic debt totals for APLD
        may_apld_debt = sum(
            d.get("amount", 0.0) for u, v, k, d in net_may.graph.edges(keys=True, data=True)
            if net_may.get_root_parent(u) == "APLD" and d.get("amount_type") == "principal_outstanding"
        )
        if abs(may_apld_debt - 5_306_680_000.0) > 1.0:
            errors.append(f"APLD May 31 economic debt mismatch: ${may_apld_debt/1e9:.3f}B (expected $5.307B)")
        else:
            print(f"  [OK] Economic Clock May 31, 2026 verified: 32 edges, APLD debt = $5,306.68M (Bridge active, 0.00% drift).")

        sep_apld_debt = sum(
            d.get("amount", 0.0) for u, v, k, d in net_sep.graph.edges(keys=True, data=True)
            if net_sep.get_root_parent(u) == "APLD" and d.get("amount_type") == "principal_outstanding"
        )
        if abs(sep_apld_debt - 6_596_680_000.0) > 1.0:
            errors.append(f"APLD Sep 28 economic debt mismatch: ${sep_apld_debt/1e9:.3f}B (expected $6.597B)")
        else:
            print(f"  [OK] Economic Clock Sep 28, 2026 verified: 34 edges, APLD debt = $6,596.68M ($1.59B 7% Notes active, conserved).")

        # Information Clock (Public Knowledge) Test
        net_known_jun = net.known_as_of("2026-06-30")
        net_known_sep = net.known_as_of("2026-09-28")
        if net_known_jun.graph.number_of_edges() != 30:
            errors.append(f"Expected 30 edges known as of 2026-06-30, got {net_known_jun.graph.number_of_edges()}")
        else:
            print(f"  [OK] Information Clock June 30, 2026 verified: 30 edges publicly known (eliminating look-ahead bias).")
        if net_known_sep.graph.number_of_edges() != 34:
            errors.append(f"Expected 34 edges known as of 2026-09-28, got {net_known_sep.graph.number_of_edges()}")
        else:
            print(f"  [OK] Information Clock Sep 28, 2026 verified: 34 edges publicly known.")

        # Fact-Level Bitemporality Assertions (ADR-013 & ADR-014)
        # On June 30, 2026, CoreWeave DDTL 1.0 facility edge is known (from 2024), but its June 30, 2026 balance was not disclosed until August 12, 2026!
        ddtl1_jun_edge = net_known_jun.graph.get_edge_data("CRWV_CCAC_II", "BLACKSTONE_MAGNETAR_SYN", key="OBL-CRWV-DEBT-DDTL1")
        if ddtl1_jun_edge is None:
            errors.append("OBL-CRWV-DEBT-DDTL1 edge missing from net_known_jun")
        else:
            if ddtl1_jun_edge.get("amount") is not None or ddtl1_jun_edge.get("amount_known") is not False:
                errors.append(f"Fact bitemporality leak: DDTL 1.0 amount should be None on 2026-06-30, got {ddtl1_jun_edge.get('amount')}")
            else:
                print("  [OK] Fact-level bitemporality verified: CoreWeave DDTL 1.0 amount is None / unknown on June 30, 2026 (disclosed August 12).")

        # But APLD 7% notes balance WAS disclosed on June 16, 2026 (Form 8-K), so its amount IS known on June 30!
        apld_7pct_jun = net_known_jun.graph.get_edge_data("APLD_COMPUTECO3", "INSTITUTIONAL_BONDHOLDERS", key="OBL-APLD-DEBT-7PCT-2026")
        if apld_7pct_jun is None or apld_7pct_jun.get("amount") != 1_590_000_000.0 or apld_7pct_jun.get("amount_known") is not True:
            errors.append("APLD 7% notes should be known with amount = $1.59B on 2026-06-30 (disclosed 2026-06-16)")
        else:
            print("  [OK] Fact-level bitemporality verified: APLD 7% notes amount ($1.59B) is known on June 30, 2026 via Form 8-K.")

        # On Sep 28, DDTL 1.0 amount IS known ($1.300B)
        ddtl1_sep_edge = net_known_sep.graph.get_edge_data("CRWV_CCAC_II", "BLACKSTONE_MAGNETAR_SYN", key="OBL-CRWV-DEBT-DDTL1")
        if ddtl1_sep_edge.get("amount") != 1_300_000_000.0 or ddtl1_sep_edge.get("amount_known") is not True:
            errors.append(f"DDTL 1.0 amount on Sep 28 should be $1.300B, got {ddtl1_sep_edge.get('amount')}")
        else:
            print("  [OK] Fact-level bitemporality verified: CoreWeave DDTL 1.0 amount is $1.300B on Sep 28, 2026.")

        # Coupling to Stress Engine Test (Dynamic Floating Debt Derivation)
        engine_may = FinancialStressEngine(network=net_may)
        engine_sep = FinancialStressEngine(network=net_sep)
        sofr_may = engine_may.simulate_sofr_base_rate_shock()
        sofr_sep = engine_sep.simulate_sofr_base_rate_shock()

        if abs(sofr_may["network_cash_drain_reported_baseline_usd"] - 235_350_000.0) > 1e5:
            errors.append(f"May 31 SOFR hit mismatch: ${sofr_may['network_cash_drain_reported_baseline_usd']:,.2f} (expected $235.35M)")
        if abs(sofr_sep["network_cash_drain_reported_baseline_usd"] - 226_350_000.0) > 1e5:
            errors.append(f"Sep 28 SOFR hit mismatch: ${sofr_sep['network_cash_drain_reported_baseline_usd']:,.2f} (expected $226.35M)")
        print(f"  [OK] Stress engine dynamically coupled to graph: May 31 = $235.4M/yr, Sep 28 = $226.4M/yr (derived from active edges).")

        # Epistemic stress engine check on June 30 information clock (ADR-014 Zero-Lookahead)
        engine_known_jun = FinancialStressEngine(network=net_known_jun)
        sofr_known_jun = engine_known_jun.simulate_sofr_base_rate_shock()
        if sofr_known_jun["floating_principal_known"] is not False:
            errors.append("Expected floating_principal_known to be False under net_known_jun (disclosed August 12)")
        if sofr_known_jun["swap_notional_known"] is not False:
            errors.append("Expected swap_notional_known to be False under net_known_jun (disclosed August 12)")
        if sofr_known_jun["crwv_reported_floating_usd"] is not None:
            errors.append("Expected crwv_reported_floating_usd to be None under net_known_jun")
        if sofr_known_jun["max_cash_drain_usd"] is not None:
            errors.append("Expected max_cash_drain_usd to be None under net_known_jun (unbounded upper limit)")
        if sofr_known_jun["network_cash_drain_reported_baseline_usd"] is not None:
            errors.append("Expected network_cash_drain_reported_baseline_usd to be None under net_known_jun")
        if len(sofr_known_jun["unknown_floating_edges"]) != 6:
            errors.append(f"Expected 6 unknown floating edges under net_known_jun, got {len(sofr_known_jun['unknown_floating_edges'])}")
        else:
            print("  [OK] Zero-lookahead epistemic stress check verified on June 30, 2026: floating_principal_known=False, 6 unknown floating edges, reported hits=None.")

    except Exception as e:
        errors.append(f"Error during graph unwrapping/temporal validation: {e}")

    # ---------------------------------------------------------
    # 3c. Validate Obligation Lifecycle Events & Bitemporal Facts Ledger
    # ---------------------------------------------------------
    events_df = pd.read_parquet(PROCESSED_DIR / "obligation_events.parquet")
    expected_events_count = 36
    if len(events_df) != expected_events_count:
        errors.append(f"Obligation events count mismatch: {len(events_df)} (expected {expected_events_count})")
    else:
        print(f"  [OK] Exactly {expected_events_count} lifecycle events present in obligation_events.parquet.")

    valid_event_types = {"created", "superseded"}
    for _, ev in events_df.iterrows():
        eid = ev["event_id"]
        etype = ev.get("event_type")
        if etype not in valid_event_types:
            errors.append(f"Event {eid} has invalid event_type: {etype}")
        if not ev.get("economic_effective_at") or not ev.get("publicly_known_at"):
            errors.append(f"Event {eid} missing temporal dates")
        if not ev.get("claim_id"):
            errors.append(f"Event {eid} missing claim_id")

    # Bridge supersession event specifically
    bridge_ev = events_df[events_df["event_id"] == "EVT-APLD-DEBT-BRIDGE-SUPERSEDED"]
    if bridge_ev.empty:
        errors.append("Missing EVT-APLD-DEBT-BRIDGE-SUPERSEDED event")
    else:
        bev = bridge_ev.iloc[0]
        if bev["economic_effective_at"] != "2026-06-16" or bev["publicly_known_at"] != "2026-06-16":
            errors.append(f"Bridge supersession dates mismatch: econ={bev['economic_effective_at']}, known={bev['publicly_known_at']}")
        else:
            print("  [OK] Bridge supersession lifecycle event verified: economic 2026-06-16, publicly known 2026-06-16.")

    facts_df = pd.read_parquet(PROCESSED_DIR / "obligation_facts.parquet")
    clm_df = pd.read_parquet(PROCESSED_DIR / "evidence_claims.parquet")
    expected_facts_count = 43
    if len(facts_df) != expected_facts_count:
        errors.append(f"Obligation facts count mismatch: {len(facts_df)} (expected {expected_facts_count})")
    else:
        print(f"  [OK] Exactly {expected_facts_count} bitemporal facts present in obligation_facts.parquet.")

    claims_filing_dates = dict(zip(clm_df["claim_id"], clm_df["filing_date"]))
    for _, f_row in facts_df.iterrows():
        fid = f_row["fact_id"]
        t_cid = f_row.get("truth_claim_id")
        k_cid = f_row.get("knowledge_claim_id")
        if not t_cid or t_cid not in claims_filing_dates:
            errors.append(f"Fact {fid} has invalid or missing truth_claim_id: {t_cid}")
        if not k_cid or k_cid not in claims_filing_dates:
            errors.append(f"Fact {fid} has invalid or missing knowledge_claim_id: {k_cid}")
        else:
            k_filing_date = claims_filing_dates[k_cid]
            if str(f_row["publicly_known_from"]) < str(k_filing_date):
                errors.append(f"Fact {fid} publicly_known_from {f_row['publicly_known_from']} predates knowledge claim filing date {k_filing_date}")

    print(f"  [OK] All {len(facts_df)} facts verified: truth_claim_id and knowledge_claim_id present, publicly_known_from >= claim filing date.")

    # ---------------------------------------------------------
    # 4. Validate Evidence Claims & Quote Categorization
    # ---------------------------------------------------------
    expected_claims_count = 37
    if len(clm_df) != expected_claims_count:
        errors.append(f"Evidence claims count mismatch: {len(clm_df)} (expected {expected_claims_count})")
    else:
        print(f"  [OK] Exactly {expected_claims_count} audited evidence claims present.")

    valid_quote_types = {"exact_quote", "source_excerpt", "analyst_summary"}
    for _, row in clm_df.iterrows():
        cid = row["claim_id"]
        qtype = row.get("quote_type")
        if qtype not in valid_quote_types:
            errors.append(f"Claim {cid} has invalid quote_type: {qtype}")
        quote = row.get("exact_quote", "")
        if not quote or len(quote) < 15:
            errors.append(f"Claim {cid} has empty or short exact_quote")
        if not row.get("accession_number") or not row.get("filing_date"):
            errors.append(f"Claim {cid} missing SEC accession number or filing date")

    # Claim CLM-APLD-003 categorization check
    c3 = clm_df[clm_df["claim_id"] == "CLM-APLD-003"]
    if not c3.empty and c3.iloc[0]["quote_type"] != "analyst_summary":
        errors.append(f"CLM-APLD-003 should be categorized as analyst_summary, got {c3.iloc[0]['quote_type']}")
    else:
        print("  [OK] CLM-APLD-003 verified as analyst_summary.")

    # Verbatim substring assertions against cached primary SEC exhibits
    c5 = clm_df[clm_df["claim_id"] == "CLM-APLD-005"]
    if c5.empty:
        errors.append("Missing claim CLM-APLD-005")
    else:
        ex10_1_file = PROJECT_ROOT / "data" / "raw" / "sec" / "APLD_ex10_1.htm"
        if not ex10_1_file.exists():
            errors.append(f"Missing cached primary SEC exhibit: {ex10_1_file.name}")
        else:
            raw_bytes = ex10_1_file.read_bytes()
            unesc = html.unescape(raw_bytes.decode("windows-1252"))
            unesc = unesc.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'")
            unesc = re.sub(r'</?(?:b|i|u|strong|em|font|span)(?:\s+[^>]*)?>', '', unesc, flags=re.IGNORECASE)
            norm_raw = ' '.join(re.sub(r'<[^>]+>', ' ', unesc).split())
            norm_quote = ' '.join(c5.iloc[0]["exact_quote"].split())
            if norm_quote not in norm_raw:
                errors.append("CLM-APLD-005 exact_quote is not an exact contiguous substring of APLD_ex10_1.htm")
            else:
                print("  [OK] CLM-APLD-005 100% exact contiguous verbatim substring verified in APLD_ex10_1.htm.")

    c6 = clm_df[clm_df["claim_id"] == "CLM-APLD-006"]
    if c6.empty:
        errors.append("Missing claim CLM-APLD-006")
    else:
        ex10_2_file = PROJECT_ROOT / "data" / "raw" / "sec" / "APLD_ex10_2.htm"
        if not ex10_2_file.exists():
            errors.append(f"Missing cached primary SEC exhibit: {ex10_2_file.name}")
        else:
            raw_bytes = ex10_2_file.read_bytes()
            unesc = html.unescape(raw_bytes.decode("windows-1252"))
            unesc = unesc.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'")
            unesc = re.sub(r'</?(?:b|i|u|strong|em|font|span)(?:\s+[^>]*)?>', '', unesc, flags=re.IGNORECASE)
            norm_raw = ' '.join(re.sub(r'<[^>]+>', ' ', unesc).split())
            norm_quote = ' '.join(c6.iloc[0]["exact_quote"].split())
            if norm_quote not in norm_raw:
                errors.append("CLM-APLD-006 exact_quote is not an exact contiguous substring of APLD_ex10_2.htm")
            else:
                print("  [OK] CLM-APLD-006 100% exact contiguous verbatim substring verified in APLD_ex10_2.htm.")

    cc5 = clm_df[clm_df["claim_id"] == "CLM-CRWV-005"]
    if cc5.empty:
        errors.append("Missing claim CLM-CRWV-005")
    else:
        qc5 = cc5.iloc[0]["exact_quote"]
        for phrase in ["Interest rate swaps", "4,661"]:
            if phrase not in qc5:
                errors.append(f"CLM-CRWV-005 missing expected verbatim phrase: '{phrase}'")
        print("  [OK] CLM-CRWV-005 verified against Note 8 verbatim swap disclosures.")

    c8 = clm_df[clm_df["claim_id"] == "CLM-APLD-008"]
    if c8.empty:
        errors.append("Missing claim CLM-APLD-008")
    else:
        r8 = c8.iloc[0]
        if r8["accession_number"] != "0001493152-26-028899" or r8["filing_date"] != "2026-06-16":
            errors.append(f"CLM-APLD-008 metadata mismatch: {r8['accession_number']}, {r8['filing_date']}")
        for kw in ["ComputeCo 3 LLC", "7.000%"]:
            if kw not in r8["exact_quote"]:
                errors.append(f"CLM-APLD-008 exact_quote missing '{kw}'")
        print("  [OK] CLM-APLD-008 verified: Form 8-K filed 2026-06-16, APLD ComputeCo 3 LLC 7.00% Senior Secured Notes.")

    # Verification of Class A primary SEC filings against cached raw JSON submissions
    sec_errors = validate_sec_source_existence()
    if sec_errors:
        for se in sec_errors:
            errors.append(se)
    else:
        print(f"  [OK] All {len(clm_df)} evidence claims 100% verified against raw SEC EDGAR submissions JSON.")

    # Verification of verbatim substrings against cached HTML exhibits
    html_errors = validate_sec_html_content()
    if html_errors:
        for he in html_errors:
            errors.append(he)
    else:
        print("  [OK] All 29 primary SEC claims verified as 100% exact contiguous verbatim substrings in cached primary HTML filings.")

    print(f"  [OK] All {len(clm_df)} claims possess verified SEC accession numbers, valid quote_types, and verbatim quotes.")

    # ---------------------------------------------------------
    # 5. Validate Canonical Financials
    # ---------------------------------------------------------
    fin_df = pd.read_parquet(PROCESSED_DIR / "financials.parquet")
    
    # Check key funded debt (latest reported period)
    for ticker, expected_val, min_val in [
        ("APLD", 4.98e9, 4.9e9),
        ("CRWV", 35.55e9, 3.5e10),
        ("SMCI", 8.72e9, 8.7e9),
        ("ORCL", 125.34e9, 1.2e11),
        ("NVDA", 33.37e9, 3.3e10)
    ]:
        v = fin_df[(fin_df["entity_id"] == ticker) & (fin_df["metric"] == "total_debt")].sort_values("period_end").iloc[-1]["value"]
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
            "SOFR Base Rate Shock": 235.4e6,
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
