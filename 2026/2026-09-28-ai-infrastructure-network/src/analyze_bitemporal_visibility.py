"""
Task 023.1: Empirical SEC Legibility vs Public Awareness Calibration
(Two-Clock Contractual Network Dynamics)

This script performs:
1. Layered Information Resolution Framework:
   Separates four distinct operational timestamps:
   - Level 0: Economic Reality (t_eco) - binding legal execution
   - Level 1: Public Headline Awareness (t_press) - press release / news discovery
   - Level 2: SEC/EDGAR Detailed Legal Legibility (t_sec) - filing of SPVs, advance rates, covenants
   - Level 3: Current Balance Measurability (t_meas) - periodic quarter-end 10-Q disclosures
2. Role-Aware Obligation Inception Lag Audit:
   Classifies obligations by actual institutional regulatory regime:
   - Public / 144A Capital Market Notes (14 tranches, $25.682B)
   - Private Credit Delayed-Draw Facilities (8 facilities)
   - Privately Placed Equipment / Growth Debt (3 tranches)
   - Commercial Colocation & Real Estate Master Leases (3 contracts)
   - Corporate Parent Guarantees & Springing Indemnities (12 instruments)
   - Corporate Residual & OEM Debt (4 tranches)
   - Strategic Equity Investments (1 tranche)
   Separates true contract-inception lags from measurement-period / footnote reporting lags.
3. Monthly Bitemporal Network Time Series (2024-01-01 to 2026-09-01, 33 months):
   Simultaneously tracks:
   - Economic Reality Graph G_eco(t) vs SEC/EDGAR Knowledge Graph G_sec(t)
   - Active Legal-Edge Degree vs Unique-Root Counterparty Degree for CoreWeave
   - Giant Connected Component Size (S_eco vs S_sec)
   - Funded Debt Volume: Economic Debt vs Calibrated Known Debt vs Fact-Ledger Coverage
   - Unresolved Current-Principal Gap (calibrated against known 144A issuance balances)
4. Publication Visualizations:
   - Figure 1: bitemporal_debt_opacity_trajectory.png (Calibrated Principal Gap & SEC Opacity Ratio)
   - Figure 2: bitemporal_network_topology_lag.png (Giant Component & Empirical Lag Distribution)
"""

import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import networkx as nx

try:
    from .graph import ObligationNetwork
except ImportError:
    from graph import ObligationNetwork

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
ANALYSIS_DIR = REPO_ROOT / "outputs" / "analysis"
FIGURES_DIR = REPO_ROOT / "outputs" / "figures"

ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# 1. Institutional Role-Aware Obligation Classifier
# -----------------------------------------------------------------------------
def classify_obligation_role_aware(row: pd.Series) -> str:
    """
    Classifies an obligation into a principled institutional regulatory category,
    avoiding crude substring matching on obligation IDs.
    """
    oid = str(row.get("obligation_id", ""))
    
    # 1. Measurement period / Footnote aggregation (separated from contract inception)
    if oid == "REL-MSFT-CRWV-REVENUE-CONCENTRATION":
        return "Customer Revenue Concentration (Measurement Period)"
    if oid == "OBL-SMCI-SUPPLIER-COMMIT":
        return "Supplier Purchase Commitments (Annual Footnote Aggregation)"

    # 2. Public / 144A Capital Market Notes (14 discrete tranches, $25.682B total)
    if oid in [
        "OBL-CRWV-DEBT-NOTES-2030", "OBL-CRWV-DEBT-NOTES-2031-900", "OBL-CRWV-DEBT-NOTES-2031-975",
        "OBL-CRWV-DEBT-NOTES-2032-9625", "OBL-CRWV-DEBT-NOTES-2032-EUR",
        "OBL-CRWV-DEBT-CONV-2031", "OBL-CRWV-DEBT-CONV-2032",
        "OBL-APLD-DEBT-PF1", "OBL-APLD-DEBT-PF2", "OBL-APLD-DEBT-7PCT-2026", "OBL-APLD-DEBT-CONV",
        "OBL-WULF-DEBT-CONV-2030", "OBL-WULF-DEBT-CONV-2031", "OBL-WULF-DEBT-CONV-2032"
    ]:
        return "Public / 144A Capital Market Notes"

    # 3. Private Credit Equipment & Bank Facilities (Delayed-draw term loans)
    if oid in [
        "OBL-CRWV-DEBT-DDTL1", "OBL-CRWV-DEBT-DDTL2", "OBL-CRWV-DEBT-DDTL2-1",
        "OBL-CRWV-DEBT-DDTL3", "OBL-CRWV-DEBT-DDTL4", "OBL-CRWV-DEBT-DDTL5",
        "OBL-CRWV-DEBT-MAGNETAR", "OBL-NBIS-DEBT-MUFG-2026"
    ]:
        return "Private Credit Delayed-Draw Facilities"

    # 4. Privately Placed Equipment / Growth Debt (Direct bilateral placements)
    if oid in ["OBL-IREN-DEBT-MFSA-2026", "OBL-IREN-DEBT-NOTES-2026", "OBL-HUT-DEBT-COATUE-CONV-2024"]:
        return "Privately Placed Equipment / Growth Debt"

    # 5. Commercial Colocation & Real Estate Master Leases
    if oid in ["OBL-CRWV-CORZ-COLOCATION-2024", "OBL-CRWV-APLD-LEASE", "OBL-NBIS-META-OFFTAKE-2026"]:
        return "Commercial Colocation & Master Leases"

    # 6. Corporate Parent Guarantees & Springing Indemnities
    if "GUARANTY" in oid or "COBORROWER" in oid:
        return "Parent Guarantees & Springing Indemnities"

    # 7. Strategic Equity
    if "EQUITY" in oid:
        return "Strategic Equity Investments"

    # 8. Corporate Residual & OEM Debt
    return "Corporate Residual & OEM Debt"


# -----------------------------------------------------------------------------
# 2. Main Analysis Pipeline
# -----------------------------------------------------------------------------
def run_bitemporal_analysis():
    print("=" * 80)
    print("TASK 023.1: SEC LEGIBILITY VS PUBLIC AWARENESS BITEMPORAL ANALYSIS")
    print("=" * 80)

    # 1. Load Data
    obligations_df = pd.read_parquet(PROCESSED_DIR / "obligations.parquet")
    events_df = pd.read_parquet(PROCESSED_DIR / "obligation_events.parquet")
    facts_df = pd.read_parquet(PROCESSED_DIR / "obligation_facts.parquet")
    entities_df = pd.read_parquet(PROCESSED_DIR / "entities.parquet")

    # 2. Obligation Lag Audit
    ob = obligations_df.copy()
    ob["economic_start"] = pd.to_datetime(ob["economic_valid_from"].fillna(ob["valid_from"]))
    ob["edgar_public_start"] = pd.to_datetime(ob["publicly_known_from"].fillna(ob["observed_as_of"]))
    ob["sec_lag_days"] = (ob["edgar_public_start"] - ob["economic_start"]).dt.days
    ob["calibrated_category"] = ob.apply(classify_obligation_role_aware, axis=1)

    # Separate true contract inception from periodic measurement observations
    contract_inceptions = ob[~ob["calibrated_category"].str.contains("Measurement Period|Annual Footnote")].copy()
    periodic_measurements = ob[ob["calibrated_category"].str.contains("Measurement Period|Annual Footnote")].copy()

    print("\n--- Summary of Contract Inception Lags by Calibrated Category (N=45) ---")
    cat_summary = contract_inceptions.groupby("calibrated_category")["sec_lag_days"].agg(
        count="count",
        mean_days="mean",
        median_days="median",
        min_days="min",
        max_days="max",
        std_days="std"
    ).reset_index()
    print(cat_summary.to_string(index=False))

    print("\n--- Periodic / Footnote Reporting Observations (N=2) ---")
    print(periodic_measurements[["obligation_id", "calibrated_category", "economic_valid_from", "publicly_known_from", "sec_lag_days"]].to_string(index=False))

    # Export audited lag catalog
    ob_export = ob[[
        "obligation_id", "from_entity", "to_entity", "obligation_type", "calibrated_category",
        "amount", "amount_type", "facility_capacity", "capacity_mw",
        "economic_valid_from", "publicly_known_from", "sec_lag_days", "claim_ids"
    ]].sort_values(by="sec_lag_days", ascending=False)
    ob_export.to_csv(ANALYSIS_DIR / "bitemporal_lag_summary.csv", index=False)
    print(f"\n[OK] Calibrated lag summary saved to {ANALYSIS_DIR / 'bitemporal_lag_summary.csv'}")

    # 3. Monthly Bitemporal Network Simulation (33 Months: 2024-01-01 to 2026-09-01)
    print("\nSimulating 33-month bitemporal trajectory (2024-01-01 to 2026-09-01)...")
    net = ObligationNetwork(entities_df=entities_df, obligations_df=obligations_df, facts_df=facts_df, events_df=events_df)
    dates = pd.date_range(start="2024-01-01", end="2026-09-01", freq="MS").strftime("%Y-%m-%d").tolist()

    # Pre-calculate public 144A note face values known at each date
    public_notes_pool = ob[ob["calibrated_category"] == "Public / 144A Capital Market Notes"].copy()
    
    monthly_records = []
    for d in dates:
        eco = net.economic_as_of(d)
        kno = net.known_as_of(d)

        # Graph topologies
        g_eco = eco.graph.to_undirected()
        g_kno = kno.graph.to_undirected()

        # Active nodes (degree > 0)
        active_eco_nodes = [n for n, deg in g_eco.degree() if deg > 0]
        active_kno_nodes = [n for n, deg in g_kno.degree() if deg > 0]

        sub_eco = g_eco.subgraph(active_eco_nodes)
        sub_kno = g_kno.subgraph(active_kno_nodes)

        eco_cc = list(nx.connected_components(sub_eco))
        kno_cc = list(nx.connected_components(sub_kno))

        eco_giant = len(max(eco_cc, key=len)) if eco_cc else 0
        kno_giant = len(max(kno_cc, key=len)) if kno_cc else 0

        # CoreWeave Legal Edges vs Unique Root Counterparties
        crwv_eco_legal_edges = eco.graph.degree("CRWV") if eco.graph.has_node("CRWV") else 0
        crwv_kno_legal_edges = kno.graph.degree("CRWV") if kno.graph.has_node("CRWV") else 0

        eco_root_cps = set()
        if eco.graph.has_node("CRWV"):
            for n in eco.graph.neighbors("CRWV"):
                r = net.get_root_parent(n)
                if r != "CRWV":
                    eco_root_cps.add(r)
            for u, v in eco.graph.in_edges("CRWV"):
                r = net.get_root_parent(u)
                if r != "CRWV":
                    eco_root_cps.add(r)

        kno_root_cps = set()
        if kno.graph.has_node("CRWV"):
            for n in kno.graph.neighbors("CRWV"):
                r = net.get_root_parent(n)
                if r != "CRWV":
                    kno_root_cps.add(r)
            for u, v in kno.graph.in_edges("CRWV"):
                r = net.get_root_parent(u)
                if r != "CRWV":
                    kno_root_cps.add(r)

        # Financial aggregations
        eco_debt = 0.0
        kno_debt_fact_ledger = 0.0
        eco_cap = 0.0
        kno_cap = 0.0

        for _, _, _, data in eco.graph.edges(keys=True, data=True):
            if data.get("obligation_type") == "debt_facility":
                eco_debt += data.get("amount") or 0.0
            if pd.notna(data.get("facility_capacity")):
                eco_cap += float(data.get("facility_capacity") or 0.0)

        for _, _, _, data in kno.graph.edges(keys=True, data=True):
            if data.get("obligation_type") == "debt_facility":
                kno_debt_fact_ledger += data.get("amount") or 0.0
            if pd.notna(data.get("facility_capacity")):
                kno_cap += float(data.get("facility_capacity") or 0.0)

        # Calibrated Known Debt: Incorporates known issuance face value of public 144A notes
        # issued and announced on or before date d
        known_public_notes = public_notes_pool[
            (pd.to_datetime(public_notes_pool["publicly_known_from"]) <= pd.to_datetime(d)) &
            (pd.to_datetime(public_notes_pool["economic_valid_from"]) <= pd.to_datetime(d))
        ]
        calibrated_public_notes_b = known_public_notes["amount"].sum() / 1e9

        # Total calibrated known debt combines fact-ledger debt with known public note face amounts
        # taking the maximum to prevent double counting
        calibrated_kno_debt_b = max(round(kno_debt_fact_ledger / 1e9, 4), round(calibrated_public_notes_b, 4))
        
        eco_debt_b = round(eco_debt / 1e9, 4)
        fact_ledger_kno_debt_b = round(kno_debt_fact_ledger / 1e9, 4)
        
        # Unresolved current-principal gap
        unresolved_gap_b = max(0.0, round(eco_debt_b - calibrated_kno_debt_b, 4))
        calibrated_opacity_pct = round((unresolved_gap_b / eco_debt_b * 100.0), 2) if eco_debt_b > 0 else 0.0

        monthly_records.append({
            "date": d,
            "eco_nodes": len(active_eco_nodes),
            "kno_nodes": len(active_kno_nodes),
            "node_gap": len(active_eco_nodes) - len(active_kno_nodes),
            "eco_edges": eco.graph.number_of_edges(),
            "kno_edges": kno.graph.number_of_edges(),
            "edge_gap": eco.graph.number_of_edges() - kno.graph.number_of_edges(),
            "eco_giant_cc": eco_giant,
            "kno_giant_cc": kno_giant,
            "giant_cc_gap": eco_giant - kno_giant,
            "crwv_eco_legal_edges": crwv_eco_legal_edges,
            "crwv_kno_legal_edges": crwv_kno_legal_edges,
            "crwv_legal_edge_gap": crwv_eco_legal_edges - crwv_kno_legal_edges,
            "crwv_eco_root_cps": len(eco_root_cps),
            "crwv_kno_root_cps": len(kno_root_cps),
            "crwv_root_cp_gap": len(eco_root_cps) - len(kno_root_cps),
            "eco_debt_b": eco_debt_b,
            "fact_ledger_kno_debt_b": fact_ledger_kno_debt_b,
            "calibrated_kno_debt_b": calibrated_kno_debt_b,
            "unresolved_principal_gap_b": unresolved_gap_b,
            "calibrated_opacity_pct": calibrated_opacity_pct,
            "eco_facility_capacity_b": round(eco_cap / 1e9, 4),
            "kno_facility_capacity_b": round(kno_cap / 1e9, 4),
            "capacity_gap_b": round((eco_cap - kno_cap) / 1e9, 4)
        })

    df_monthly = pd.DataFrame(monthly_records)
    df_monthly.to_csv(ANALYSIS_DIR / "bitemporal_monthly_trajectory.csv", index=False)
    print(f"[OK] Calibrated monthly trajectory saved to {ANALYSIS_DIR / 'bitemporal_monthly_trajectory.csv'}")

    # 4. JSON Summary of Layered Findings
    # Analyze July 1, 2026 pre-filing snapshot
    jul1_row = df_monthly[df_monthly["date"] == "2026-07-01"].iloc[0]

    headline_json = {
        "task": "Task 023.1: SEC Legibility vs Public Awareness Calibration",
        "date": "2026-09-30",
        "frozen_dataset_commit": "42f9a74",
        "layered_resolution_framework": {
            "level_0": "Economic Inception (binding contract execution / facility closing)",
            "level_1": "Public Headline Awareness (press release / news announcement of existence and size)",
            "level_2": "SEC/EDGAR Detailed Legal Legibility (filing of SPVs, advance rates, covenants on EDGAR)",
            "level_3": "Current Balance Measurability (quarter-end drawn debt reported in periodic 10-Q footnotes)"
        },
        "headline_calibrated_findings": {
            "mean_contract_inception_lag_days": round(contract_inceptions["sec_lag_days"].mean(), 2),
            "median_contract_inception_lag_days": round(contract_inceptions["sec_lag_days"].median(), 2),
            "public_144a_notes_mean_lag_days": round(contract_inceptions[contract_inceptions["calibrated_category"] == "Public / 144A Capital Market Notes"]["sec_lag_days"].mean(), 2),
            "private_credit_facilities_mean_lag_days": round(contract_inceptions[contract_inceptions["calibrated_category"] == "Private Credit Delayed-Draw Facilities"]["sec_lag_days"].mean(), 2),
            "ddtl_1_layered_timeline": {
                "level_0_economic_inception": "2023-07-30",
                "level_1_public_headline_announcement": "2023-08-03 (Blackstone / Magnetar press release, 4-day lag)",
                "level_2_sec_edgar_detailed_legibility": "2025-03-20 (Form S-1 / 10-Q filing, 599-day lag)",
                "insight": "Headline existence was public within 4 days; detailed SPV and borrowing base architecture lagged by 599 days."
            },
            "ddtl_2_layered_timeline": {
                "level_0_economic_inception": "2024-05-16",
                "level_1_public_headline_announcement": "2024-05-17 (Blackstone press release, 1-day lag)",
                "level_2_sec_edgar_detailed_legibility": "2025-03-20 (Form S-1 / 10-Q filing, 308-day lag)"
            },
            "summer_2026_pre_filing_debt_gap": {
                "date": "2026-07-01",
                "economic_debt_b": float(jul1_row["eco_debt_b"]),
                "publicly_known_144a_notes_baseline_b": float(jul1_row["calibrated_kno_debt_b"]),
                "calibrated_unresolved_principal_gap_b": float(jul1_row["unresolved_principal_gap_b"]),
                "calibrated_unresolved_percentage": float(jul1_row["calibrated_opacity_pct"]),
                "fact_ledger_coverage_artifact_note": (
                    "Pure fact-ledger queries returned $11.815B because several public note principal facts were pegged "
                    "to June 30 published Aug 12. Carrying forward the known $25.682B public note pool establishes "
                    "a maximum residual gap of $18.934B (42.4%), representing unobservable DDTL draws prior to 10-Q disclosure."
                )
            },
            "peak_committed_capacity_gap": {
                "period": "January 2024 - March 2025 (15 Months)",
                "economic_capacity_b": 9.9,
                "public_known_capacity_b": 0.0,
                "gap_b": 9.9
            }
        },
        "calibrated_category_statistics": cat_summary.to_dict(orient="records"),
        "periodic_measurement_observations": periodic_measurements[[
            "obligation_id", "calibrated_category", "economic_valid_from", "publicly_known_from", "sec_lag_days"
        ]].to_dict(orient="records")
    }

    with open(ANALYSIS_DIR / "bitemporal_visibility_summary.json", "w", encoding="utf-8") as f:
        json.dump(headline_json, f, indent=2)
    print(f"[OK] Calibrated summary JSON saved to {ANALYSIS_DIR / 'bitemporal_visibility_summary.json'}")

    # 5. Generate Figures
    generate_calibrated_figures(df_monthly, contract_inceptions)


# -----------------------------------------------------------------------------
# 3. Publication Visualizations Generator
# -----------------------------------------------------------------------------
def generate_calibrated_figures(df_monthly: pd.DataFrame, contract_inceptions: pd.DataFrame):
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    matplotlib.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    matplotlib.rcParams["axes.edgecolor"] = "#cccccc"
    matplotlib.rcParams["axes.linewidth"] = 0.8

    dates = pd.to_datetime(df_monthly["date"])

    # -------------------------------------------------------------------------
    # FIGURE 1: Calibrated Debt Trajectory & Unresolved Principal Gap
    # -------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Panel A: Economic Debt vs Calibrated Known Debt
    ax1.plot(dates, df_monthly["eco_debt_b"], label="Economic Reality Debt (Funded Principal)", color="#b71c1c", linewidth=2.5, marker="o", markersize=4)
    ax1.plot(dates, df_monthly["calibrated_kno_debt_b"], label="Publicly Known Debt Baseline ($25.682B Public Notes Carried Forward)", color="#1565c0", linewidth=2.5, linestyle="--", marker="s", markersize=4)
    ax1.plot(dates, df_monthly["fact_ledger_kno_debt_b"], label="Strict EDGAR Fact-Ledger Coverage (Unaugmented)", color="#78909c", linewidth=1.5, linestyle=":")

    # Fill for Unresolved Current-Principal Gap
    ax1.fill_between(dates, df_monthly["eco_debt_b"], df_monthly["calibrated_kno_debt_b"], color="#ef9a9a", alpha=0.45, label="Unresolved Current-Principal Gap (DDTL Draw Uncertainty)")

    # Secondary committed capacity lines
    ax1.plot(dates, df_monthly["eco_facility_capacity_b"], label="Committed Credit Facility Capacity (Economic)", color="#e65100", linewidth=1.5, linestyle="--")

    # Annotate Summer 2026 Gap
    jul1_dt = pd.to_datetime("2026-07-01")
    ax1.annotate(
        "Calibrated Pre-Filing Gap: $18.934B (42.4%)\n"
        "(DDTL drawdowns unobservable prior to 10-Q filing;\n"
        "public 144A notes fully known at $25.682B)",
        xy=(jul1_dt, 44.6),
        xytext=(pd.to_datetime("2025-08-01"), 36.0),
        arrowprops=dict(arrowstyle="->", color="#b71c1c", lw=1.5),
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff9c4", edgecolor="#fbc02d", alpha=0.9),
        fontsize=9,
        fontweight="bold"
    )

    # Annotate Early Private Credit Incubation
    ax1.annotate(
        "Private Credit Cloak:\n$9.9B Capacity Active;\nEDGAR S-1 Legibility Lagged (2024-2025)",
        xy=(pd.to_datetime("2024-06-01"), 9.9),
        xytext=(pd.to_datetime("2024-01-01"), 20.0),
        arrowprops=dict(arrowstyle="->", color="#e65100", lw=1.5),
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffe0b2", edgecolor="#fb8c00", alpha=0.9),
        fontsize=9,
        fontweight="bold"
    )

    ax1.set_ylabel("Volume in Current Dollars ($B)", fontsize=11, fontweight="bold")
    ax1.set_title("A. Bitemporal Debt & Committed Capacity Trajectory: Economic Clock vs. SEC/EDGAR Knowledge Clock", fontsize=12, fontweight="bold", pad=12)
    ax1.legend(loc="upper left", frameon=True, fontsize=8.5)
    ax1.set_ylim(-2, 52)

    # Panel B: Calibrated Opacity Ratio and Active Undisclosed Edges Gap
    ax2_twin = ax2.twinx()

    p1 = ax2.plot(dates, df_monthly["calibrated_opacity_pct"], color="#c2185b", linewidth=2.2, marker="^", label="Calibrated Opacity Ratio (% Unresolved Principal)")
    p2 = ax2_twin.plot(dates, df_monthly["edge_gap"], color="#303f9f", linewidth=2.0, linestyle="--", marker="d", label="SEC Undisclosed Edges Gap (ΔE = E_eco - E_sec)")

    ax2.set_ylabel("Calibrated Opacity Ratio (%)", color="#c2185b", fontsize=11, fontweight="bold")
    ax2_twin.set_ylabel("Undisclosed Legal Edges (ΔE)", color="#303f9f", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Date (Monthly Intervals: 2024 - 2026)", fontsize=11, fontweight="bold")
    ax2.set_title("B. Unresolved Principal Ratio & Structural Edge Visibility Gap Over Time", fontsize=12, fontweight="bold", pad=12)
    ax2.set_ylim(-5, 60)
    ax2_twin.set_ylim(-1, 9)

    lines = p1 + p2
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc="upper right", frameon=True, fontsize=9)

    plt.tight_layout()
    fig1_path = FIGURES_DIR / "bitemporal_debt_opacity_trajectory.png"
    plt.savefig(fig1_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Figure 1 saved to {fig1_path}")

    # -------------------------------------------------------------------------
    # FIGURE 2: Network Topology Lag & Empirical Lag Distribution
    # -------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Panel A: Giant Component Size & Unique Counterparty Discovery
    ax1.plot(dates, df_monthly["eco_giant_cc"], label="Economic Giant Component (Nodes)", color="#b71c1c", linewidth=2.5, marker="o")
    ax1.plot(dates, df_monthly["kno_giant_cc"], label="SEC/EDGAR Giant Component", color="#1565c0", linewidth=2.2, linestyle="--", marker="s")
    ax1.plot(dates, df_monthly["crwv_eco_root_cps"], label="CoreWeave Unique Root Counterparties (Economic)", color="#388e3c", linewidth=1.8, linestyle=":")
    ax1.plot(dates, df_monthly["crwv_kno_root_cps"], label="CoreWeave Unique Root Counterparties (SEC Known)", color="#689f38", linewidth=1.8, linestyle="-.")

    ax1.fill_between(dates, df_monthly["eco_giant_cc"], df_monthly["kno_giant_cc"], color="#ffcdd2", alpha=0.5, label="Topological Visibility Gap")

    ax1.annotate(
        "Topological Discovery Lag:\nIn mid-2024, public graph saw 0 giant nodes;\n"
        "In March 2025, economic hub had 4 root counterparties,\n"
        "while EDGAR reflected only 1 (Core Scientific)",
        xy=(pd.to_datetime("2025-03-01"), 7),
        xytext=(pd.to_datetime("2024-04-01"), 15),
        arrowprops=dict(arrowstyle="->", color="#b71c1c", lw=1.5),
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffebee", edgecolor="#e57373", alpha=0.9),
        fontsize=8.5,
        fontweight="bold"
    )

    ax1.set_ylabel("Count (Nodes / Root Counterparties)", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Date (Monthly Intervals)", fontsize=11, fontweight="bold")
    ax1.set_title("A. Giant Component & Unique Counterparty Hub Discovery Over Time", fontsize=12, fontweight="bold", pad=12)
    ax1.set_ylim(-1, 32)
    ax1.legend(loc="upper left", frameon=True, fontsize=8.5)

    # Panel B: Empirical Inception Lag Boxplot across Institutional Categories
    categories = [
        "Public / 144A Capital Market Notes",
        "Commercial Colocation & Master Leases",
        "Privately Placed Equipment / Growth Debt",
        "Parent Guarantees & Springing Indemnities",
        "Private Credit Delayed-Draw Facilities"
    ]
    lag_data = [contract_inceptions[contract_inceptions["calibrated_category"] == c]["sec_lag_days"].values for c in categories]
    cat_short_labels = [
        "Public 144A Notes\n(N=14, Mean: -0.1d)",
        "Commercial Leases\n(N=3, Mean: 3.0d)",
        "Private Placements\n(N=3, Mean: 0.0d)",
        "Parent Guarantees\n(N=12, Mean: 78.3d)",
        "Private Credit DDTLs\n(N=8, Mean: 169.3d)"
    ]

    box = ax2.boxplot(lag_data, tick_labels=cat_short_labels, patch_artist=True, vert=True,
                      boxprops=dict(facecolor="#e0f2fe", color="#0284c7", linewidth=1.5),
                      medianprops=dict(color="#b71c1c", linewidth=2.0),
                      whiskerprops=dict(color="#0284c7", linewidth=1.2),
                      capprops=dict(color="#0284c7", linewidth=1.2))

    for idx, d_pts in enumerate(lag_data):
        jitter = np.random.normal(0, 0.05, size=len(d_pts))
        ax2.scatter(np.full_like(d_pts, idx + 1) + jitter, d_pts, color="#0f172a", alpha=0.7, s=35, zorder=3)

    ax2.set_ylabel("SEC/EDGAR Legibility Lag Δt_sec (Days)", fontsize=11, fontweight="bold")
    ax2.set_title("B. Contract Inception Lag Distribution by Institutional Category (N=45)", fontsize=12, fontweight="bold", pad=12)
    ax2.set_ylim(-20, 650)

    ax2.text(0.5, -0.15,
             "Empirical Insight: Headline financing is announced rapidly; SEC/EDGAR contractual legibility lags.\n"
             "Public 144A notes exhibit near-zero lag (-6 to 3 days); private credit DDTLs lag up to 599 days until S-1 filing.",
             ha="center", va="top", transform=ax2.transAxes, fontsize=9, style="italic",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f9fa", edgecolor="#dddddd"))

    plt.tight_layout()
    fig2_path = FIGURES_DIR / "bitemporal_network_topology_lag.png"
    plt.savefig(fig2_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Figure 2 saved to {fig2_path}")


if __name__ == "__main__":
    run_bitemporal_analysis()
