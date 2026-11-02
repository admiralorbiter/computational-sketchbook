"""
Build Tri-District Comparative Governance Panel and Synthesis.
Triangulates board governance records, meeting frequencies, career/CTE actions,
and institutional transition mechanisms across Grandview C-4, Center 58, and Hickman Mills C-1.
"""

import pandas as pd
import json
from pathlib import Path

BASE_DIR = Path("2026/2026-09-26-rwl-institutionalization")

gv_items = pd.read_csv(BASE_DIR / "districts/grandview-c4/governance/priority_meeting_items.csv")
c58_items = pd.read_csv(BASE_DIR / "districts/center-58/governance/priority_meeting_items.csv")
hm_items = pd.read_csv(BASE_DIR / "districts/hickman-mills/governance/priority_meeting_items.csv")

gv_items["district"] = "Grandview C-4"
gv_items["district_code"] = "048-074"

c58_items["district"] = "Center 58"
c58_items["district_code"] = "048-080"

hm_items["district"] = "Hickman Mills C-1"
hm_items["district_code"] = "048-072"

# Combine priority items
all_items = pd.concat([gv_items, c58_items, hm_items], ignore_index=True)

# Save combined items
out_csv = BASE_DIR / "synthesis/tri_district_priority_meeting_items.csv"
all_items.to_csv(out_csv, index=False)
print(f"Saved {len(all_items)} combined items to {out_csv}")

# Generate District Summary Panel
summary_rows = []

for dist_name, df_d, code, s_id, total_mtgs in [
    ("Grandview C-4", gv_items, "048-074", "225", 788),
    ("Center 58", c58_items, "048-080", "229", 330),
    ("Hickman Mills C-1", hm_items, "048-072", "223", 383),
]:
    tot_items = len(df_d)
    rwl_c = df_d["explicit_rwl"].sum()
    mva_c = df_d["explicit_mva"].sum()
    cte_c = df_d["career_connected_semantic"].sum()
    money_c = df_d["money_mentioned"].sum()
    
    summary_rows.append({
        "district": dist_name,
        "district_code": code,
        "simbli_school_id": s_id,
        "total_board_meetings_on_simbli": total_mtgs,
        "focal_meetings_harvested": df_d["meeting_date"].nunique(),
        "total_agenda_items_indexed": tot_items,
        "explicit_rwl_items": rwl_c,
        "explicit_mva_items": mva_c,
        "career_connected_cte_items": cte_c,
        "pct_career_connected": round((cte_c / tot_items) * 100, 2),
        "financial_amount_items": money_c,
        "pct_financial_items": round((money_c / tot_items) * 100, 2),
    })

df_summary = pd.DataFrame(summary_rows)
summary_csv = BASE_DIR / "synthesis/tri_district_governance_panel.csv"
df_summary.to_csv(summary_csv, index=False)
print(f"Saved governance summary panel to {summary_csv}")
print(df_summary.to_string())
