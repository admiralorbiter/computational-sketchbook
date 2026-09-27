"""
Inspect Kauffman Foundation Form 990-PF electronic filings (2019-2024)
via ProPublica Nonprofit Explorer e-file XML/HTML endpoints for
Center 58 (048080) and Hickman Mills C-1 (048072).
"""

import urllib.request
import gzip
import re
import json

FILINGS = {
    "TY2024": "202523169349103332",
    "TY2023": "202443209349101644",
    "TY2022": "202303199349101530",
    "TY2021": "202213189349105236",
    "TY2020": "202143159349103869",
    "TY2019": "202003169349101105",
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def parse_grants():
    results = {"center-58": [], "hickman-mills": []}

    for ty, fid in FILINGS.items():
        url = f"https://projects.propublica.org/nonprofits/full_text/{fid}/IRS990PF"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            print(f"Fetching {ty} ({fid})...")
            resp = urllib.request.urlopen(req)
            raw = resp.read()
            html = gzip.decompress(raw).decode("utf-8", errors="replace") if raw[:2] == b"\x1f\x8b" else raw.decode("utf-8", errors="replace")

            # Find table rows
            rows = re.findall(r"<tr[^>]*>.*?</tr>", html, re.DOTALL | re.I)
            print(f"  Found {len(rows)} table rows in {ty}")

            for r in rows:
                clean = " ".join(re.sub(r"<[^>]+>", " | ", r).split())

                # Check Center 58
                if ("CENTER SCHOOL DISTRICT" in clean.upper() or "CENTER 58" in clean.upper()) and "8701 HOLMES" in clean.upper():
                    is_3b = "GrantOrContriApprvForFutGrp" in r or "Approved for Future" in clean
                    results["center-58"].append({
                        "tax_year": ty,
                        "filing_id": fid,
                        "line": "3b (Approved for Future)" if is_3b else "3a (Paid During Year)",
                        "row_text": clean
                    })

                # Check Hickman Mills C-1
                if "HICKMAN MILLS" in clean.upper() and ("5401 E 103" in clean.upper() or "C-1" in clean.upper() or "DISTRICT" in clean.upper()):
                    if "United Believers" not in clean: # skip church
                        is_3b = "GrantOrContriApprvForFutGrp" in r or "Approved for Future" in clean
                        results["hickman-mills"].append({
                            "tax_year": ty,
                            "filing_id": fid,
                            "line": "3b (Approved for Future)" if is_3b else "3a (Paid During Year)",
                            "row_text": clean
                        })

        except Exception as e:
            print(f"Error fetching {ty}: {e}")

    out_file = "2026/2026-09-26-rwl-institutionalization/data/raw/regional/kauffman_990pf_center_hickman_grants.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved raw grants to {out_file}")

    print("\n================== CENTER 58 GRANTS ==================")
    for g in results["center-58"]:
        print(f"[{g['tax_year']}] {g['line']}: {g['row_text']}")

    print("\n================== HICKMAN MILLS C-1 GRANTS ==================")
    for g in results["hickman-mills"]:
        print(f"[{g['tax_year']}] {g['line']}: {g['row_text']}")

if __name__ == "__main__":
    parse_grants()
