"""
Kansas KSDE Form USD-E Budget Parser for Function 2200 (Instructional Support).
Extracts audited actual expenditures across all operating, categorical, and capital funds
for the Kansas focal archetypes: Shawnee Mission USD 512, Olathe USD 233, and Kansas City USD 500.

Object Categories in Kansas Chart of Accounts:
- 110: Certified / Licensed Salaries
- 120: Non-Certified / Classified Salaries
- 200: Employee Benefits (210 Insurance, 220 Social Security, 290 Other, plus KPERS Fund 51 Line 85)
- 300: Purchased Professional & Technical Services
- 400: Purchased Property Services
- 500: Other Purchased Services
- 600: Supplies Family:
    * 640/644: Books & Periodicals / Textbooks
    * 650: Technology Supplies & Technology Software
    * 680/681/682/683/684: Miscellaneous Supplies & Student Materials
- 700: Property (Equipment & Furnishings) [Capital Outlay - excluded from current F-33 E07]
- 800: Other Objects (Dues, fees, judgments)
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
import fitz  # PyMuPDF


def clean_val(v: str) -> float:
    """Parse numeric dollar string into float."""
    if not v:
        return 0.0
    v = v.replace(",", "").replace("$", "").replace("(", "-").replace(")", "").strip()
    try:
        return float(v)
    except ValueError:
        return 0.0


def parse_ks_file(fpath: str | Path, target_col_idx: int = 1) -> Tuple[Dict[str, float], List[Dict]]:
    """
    Parses a Kansas Form USD-E PDF for Function 2200 expenditures.
    
    Args:
        fpath: Path to the PDF file (e.g. 512_Codes2024_Actuals2023.pdf)
        target_col_idx: Index of the target column in the 3-column layout:
            0 = Col 1 (Prior Year Actual, t-2)
            1 = Col 2 (Current Actual, t-1) [Default for audited actuals]
            2 = Col 3 (Budget Year, t)
            
    Returns:
        totals: Dict of aggregated dollar amounts by detailed object code
        fund_breakdowns: List of individual line item extractions with fund context
    """
    doc = fitz.open(str(fpath))
    
    totals = {
        "sal_certified": 0.0,
        "sal_noncertified": 0.0,
        "benefits_insurance": 0.0,
        "benefits_socsec": 0.0,
        "benefits_other": 0.0,
        "purchased_prof_300": 0.0,
        "purchased_prop_400": 0.0,
        "other_purch_500": 0.0,
        "supplies_books_640": 0.0,
        "supplies_tech_650": 0.0,
        "supplies_misc_680": 0.0,
        "property_700": 0.0,
        "other_800": 0.0,
    }

    fund_breakdowns = []

    for p_num in range(len(doc)):
        text = doc[p_num].get_text()
        if "2200" in text and any(w in text for w in ["Instr", "Support", "Instructional"]):
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            
            # Identify fund context from page headers
            fund_name = f"Page_{p_num+1}"
            for l in lines[:25]:
                u = l.upper()
                if any(k in u for k in [
                    "GENERAL FUND", "SUPPLEMENTAL GENERAL", "FEDERAL FUNDS", "AT-RISK", 
                    "CAPITAL OUTLAY", "SPECIAL EDUCATION", "BILINGUAL", "TEXTBOOK", 
                    "PROFESSIONAL DEVELOPMENT", "KPERS", "PARENT EDUCATION"
                ]):
                    fund_name = l
                    break

            in_2200 = False
            i = 0
            while i < len(lines):
                line = lines[i]
                if "2200" in line and any(w in line for w in ["Instr", "Support", "Instructional"]):
                    in_2200 = True
                    i += 1
                    continue
                if in_2200 and any(line.startswith(prefix) for prefix in [
                    "2300", "2400", "2500", "2600", "2700", "2900", "TOTAL EXPENDITURES"
                ]):
                    in_2200 = False
                    break

                if in_2200:
                    matched_key = None
                    if "110 Certified" in line or "110 Licensed" in line:
                        matched_key = "sal_certified"
                    elif "120 Non-Certified" in line or "120 NonCertified" in line or "120 Non-Licensed" in line:
                        matched_key = "sal_noncertified"
                    elif "210 Insurance" in line:
                        matched_key = "benefits_insurance"
                    elif "220 Social Security" in line:
                        matched_key = "benefits_socsec"
                    elif "290 Other" in line:
                        matched_key = "benefits_other"
                    elif "300 Purchased Professional" in line:
                        matched_key = "purchased_prof_300"
                    elif "400 Purchased Property" in line:
                        matched_key = "purchased_prop_400"
                    elif "500 Other Purchased" in line:
                        matched_key = "other_purch_500"
                    elif "640 Books" in line or "644 Textbooks" in line:
                        matched_key = "supplies_books_640"
                    elif "650 Supplies - Technology" in line or "650 Technology Supplies" in line:
                        matched_key = "supplies_tech_650"
                    elif "680 Miscellaneous Supplies" in line or "683 Other Material" in line or "682 Musical" in line:
                        matched_key = "supplies_misc_680"
                    elif "700 Property" in line:
                        matched_key = "property_700"
                    elif "800 Other" in line:
                        matched_key = "other_800"
                    elif "200 Employee Benefits" in line and i + 1 < len(lines) and lines[i+1].isdigit() and len(lines[i+1]) <= 3:
                        # Matches KPERS line item (e.g. line 85)
                        matched_key = "benefits_other"

                    if matched_key:
                        idx = i + 1
                        if idx < len(lines) and re.match(r"^\d{1,4}$", lines[idx]):
                            line_no = lines[idx]
                            idx += 1
                            vals = []
                            while idx < len(lines) and len(vals) < 3:
                                cand = lines[idx]
                                if re.match(r"^-?[\d,]+(\.\d+)?$", cand):
                                    vals.append(clean_val(cand))
                                    idx += 1
                                else:
                                    break
                            if vals:
                                val = vals[target_col_idx] if target_col_idx < len(vals) else vals[-1]
                                totals[matched_key] += val
                                if val > 0:
                                    fund_breakdowns.append({
                                        "fund": fund_name,
                                        "object": matched_key,
                                        "line_no": line_no,
                                        "value": val
                                    })
                        i = idx
                        continue
                i += 1

    return totals, fund_breakdowns


if __name__ == "__main__":
    import sys
    test_pdf = Path("data/raw/kansas_budget/shawnee_mission/512_Codes2024_Actuals2023.pdf")
    if test_pdf.exists():
        totals, fb = parse_ks_file(test_pdf, target_col_idx=1)
        print(f"Parsed {test_pdf.name} successfully:")
        for k, v in totals.items():
            print(f"  {k}: ${v:,.2f}")
    else:
        print(f"File not found: {test_pdf}")
