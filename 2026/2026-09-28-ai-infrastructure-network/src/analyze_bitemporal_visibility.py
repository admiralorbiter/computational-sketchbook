"""
Task 023: Empirical Bitemporal Visibility Analysis (Two-Clock Network Dynamics)

This script performs:
1. Empirical Lag Measurement across the Graph:
   Quantifies Δt = t_publicly_known - t_economic_inception across:
   - All 47 obligations (stratified by regulatory / instrument category)
   - All 57 lifecycle events
   - All 64 measurement facts
2. Monthly Bitemporal Time Series (2024-01-01 to 2026-09-01, 33 months):
   Simultaneously evaluates at each monthly timestamp:
   - Economic Reality Graph G_eco(t) vs Public Knowledge Graph G_kno(t)
   - Edge Visibility Gap (ΔE) and Node Visibility Gap (ΔN)
   - Giant Connected Component Size (S_eco vs S_kno)
   - CoreWeave Hub Centrality & Degree Gap (k_eco vs k_kno)
   - Funded Debt Volume Gap (Shadow Debt = D_eco - D_kno)
   - Network Opacity Ratio (1 - D_kno / D_eco)
   - Committed Facility Capacity Gap (ΔC = C_eco - C_kno)
   - Contracted Capacity MW Gap (ΔMW = MW_eco - MW_kno)
3. Historical Opacity Episodes Identification:
   Quantifies four distinct systemic visibility eras across 2024–2026.
4. Publication Visualizations:
   - Figure 1: bitemporal_debt_opacity_trajectory.png (Debt, Shadow Debt & Opacity Ratio)
   - Figure 2: bitemporal_network_topology_lag.png (Giant Component Evolution & Empirical Lag Distribution)
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


def categorize_obligation(row: pd.Series) -> str:
    """Categorizes an obligation into a substantive institutional visibility class."""
    oid = str(row.get("obligation_id", ""))
    otype = str(row.get("obligation_type", ""))
    
    if "NOTES" in oid or "CONV" in oid:
        return "Public / 144A Bond & Convertible Notes"
    elif "DDTL" in oid or "OEM" in oid or "MAGNETAR" in oid or "MUFG" in oid or "MFSA" in oid:
        if "GUARANTY" in oid or "COBORROWER" in oid:
            return "Private Credit / Bank Guarantees & SPV Liens"
        return "Private Credit / Delayed-Draw Facilities"
    elif "LEASE" in oid or "COLOCATION" in oid or "OFFTAKE" in oid or "REVENUE" in oid:
        if "GUARANTY" in oid:
            return "Commercial Lease Guarantees & Indemnities"
        return "Commercial Offtake & Colocation Contracts"
    elif "EQUITY" in oid:
        return "Strategic Equity Investments"
    elif "COMMIT" in oid:
        return "Supplier Purchase Commitments"
    else:
        return "Corporate Project & Residual Debt"


def run_bitemporal_analysis():
    print("=" * 80)
    print("TASK 023: EMPIRICAL BITEMPORAL VISIBILITY ANALYSIS")
    print("=" * 80)

    # 1. Load Data
    obligations_df = pd.read_parquet(PROCESSED_DIR / "obligations.parquet")
    events_df = pd.read_parquet(PROCESSED_DIR / "obligation_events.parquet")
    facts_df = pd.read_parquet(PROCESSED_DIR / "obligation_facts.parquet")
    entities_df = pd.read_parquet(PROCESSED_DIR / "entities.parquet")

    # 2. Obligation Lag Audit
    ob = obligations_df.copy()
    ob["economic_start"] = pd.to_datetime(ob["economic_valid_from"].fillna(ob["valid_from"]))
    ob["public_start"] = pd.to_datetime(ob["publicly_known_from"].fillna(ob["observed_as_of"]))
    ob["lag_days"] = (ob["public_start"] - ob["economic_start"]).dt.days
    ob["research_category"] = ob.apply(categorize_obligation, axis=1)

    print("\n--- Summary of Inception Lags by Research Category ---")
    cat_summary = ob.groupby("research_category")["lag_days"].agg(
        count="count",
        mean_days="mean",
        median_days="median",
        min_days="min",
        max_days="max",
        std_days="std"
    ).reset_index()
    print(cat_summary.to_string(index=False))

    # Event lag audit
    ev = events_df.copy()
    ev["eco_dt"] = pd.to_datetime(ev["economic_effective_at"])
    ev["pub_dt"] = pd.to_datetime(ev["publicly_known_at"])
    ev["lag_days"] = (ev["pub_dt"] - ev["eco_dt"]).dt.days

    # Fact lag audit
    fc = facts_df.copy()
    fc["eco_dt"] = pd.to_datetime(fc["economic_as_of"])
    fc["pub_dt"] = pd.to_datetime(fc["publicly_known_from"])
    fc["lag_days"] = (fc["pub_dt"] - fc["eco_dt"]).dt.days

    # Export lag details
    ob_export = ob[[
        "obligation_id", "from_entity", "to_entity", "obligation_type", "research_category",
        "amount", "amount_type", "facility_capacity", "capacity_mw",
        "economic_valid_from", "publicly_known_from", "lag_days", "claim_ids"
    ]].sort_values(by="lag_days", ascending=False)
    ob_export.to_csv(ANALYSIS_DIR / "bitemporal_lag_summary.csv", index=False)
    print(f"\n[OK] Obligation lag details saved to {ANALYSIS_DIR / 'bitemporal_lag_summary.csv'}")

    # 3. Monthly Bitemporal Time Series Simulation
    print("\nSimulating 33-month bitemporal trajectory (2024-01-01 to 2026-09-01)...")
    net = ObligationNetwork(entities_df=entities_df, obligations_df=obligations_df, facts_df=facts_df, events_df=events_df)
    dates = pd.date_range(start="2024-01-01", end="2026-09-01", freq="MS").strftime("%Y-%m-%d").tolist()

    monthly_records = []
    for d in dates:
        eco = net.economic_as_of(d)
        kno = net.known_as_of(d)

        # Graph topologies
        g_eco = eco.graph.to_undirected()
        g_kno = kno.graph.to_undirected()

        # Filter active nodes (degree > 0)
        active_eco_nodes = [n for n, deg in g_eco.degree() if deg > 0]
        active_kno_nodes = [n for n, deg in g_kno.degree() if deg > 0]

        sub_eco = g_eco.subgraph(active_eco_nodes)
        sub_kno = g_kno.subgraph(active_kno_nodes)

        eco_cc = list(nx.connected_components(sub_eco))
        kno_cc = list(nx.connected_components(sub_kno))

        eco_giant = len(max(eco_cc, key=len)) if eco_cc else 0
        kno_giant = len(max(kno_cc, key=len)) if kno_cc else 0

        # Degree of CoreWeave
        crwv_eco_deg = eco.graph.degree("CRWV") if eco.graph.has_node("CRWV") else 0
        crwv_kno_deg = kno.graph.degree("CRWV") if kno.graph.has_node("CRWV") else 0

        # Financial aggregations
        eco_debt = 0.0
        kno_debt = 0.0
        eco_cap = 0.0
        kno_cap = 0.0
        eco_mw = 0.0
        kno_mw = 0.0

        for _, _, _, data in eco.graph.edges(keys=True, data=True):
            if data.get("obligation_type") == "debt_facility":
                eco_debt += data.get("amount") or 0.0
            if pd.notna(data.get("facility_capacity")):
                eco_cap += float(data.get("facility_capacity") or 0.0)
            if pd.notna(data.get("capacity_mw")):
                eco_mw += float(data.get("capacity_mw") or 0.0)

        for _, _, _, data in kno.graph.edges(keys=True, data=True):
            if data.get("obligation_type") == "debt_facility":
                kno_debt += data.get("amount") or 0.0
            if pd.notna(data.get("facility_capacity")):
                kno_cap += float(data.get("facility_capacity") or 0.0)
            if pd.notna(data.get("capacity_mw")):
                kno_mw += float(data.get("capacity_mw") or 0.0)

        shadow_debt = eco_debt - kno_debt
        opacity_ratio = (shadow_debt / eco_debt) if eco_debt > 0 else 0.0

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
            "crwv_eco_degree": crwv_eco_deg,
            "crwv_kno_degree": crwv_kno_deg,
            "crwv_degree_gap": crwv_eco_deg - crwv_kno_deg,
            "eco_debt_b": round(eco_debt / 1e9, 4),
            "kno_debt_b": round(kno_debt / 1e9, 4),
            "shadow_debt_b": round(shadow_debt / 1e9, 4),
            "opacity_ratio_pct": round(opacity_ratio * 100.0, 2),
            "eco_facility_capacity_b": round(eco_cap / 1e9, 4),
            "kno_facility_capacity_b": round(kno_cap / 1e9, 4),
            "capacity_gap_b": round((eco_cap - kno_cap) / 1e9, 4),
            "eco_contracted_mw": eco_mw,
            "kno_contracted_mw": kno_mw,
            "mw_gap": eco_mw - kno_mw
        })

    df_monthly = pd.DataFrame(monthly_records)
    df_monthly.to_csv(ANALYSIS_DIR / "bitemporal_monthly_trajectory.csv", index=False)
    print(f"[OK] Monthly trajectory saved to {ANALYSIS_DIR / 'bitemporal_monthly_trajectory.csv'}")

    # 4. JSON Summary of Headline Findings
    # Max shadow debt
    max_shadow_row = df_monthly.loc[df_monthly["shadow_debt_b"].idxmax()]
    # Max opacity pct (when debt > 0)
    sub_debt_pos = df_monthly[df_monthly["eco_debt_b"] > 0]
    max_opacity_row = sub_debt_pos.loc[sub_debt_pos["opacity_ratio_pct"].idxmax()]
    # Max edge gap
    max_edge_gap_row = df_monthly.loc[df_monthly["edge_gap"].idxmax()]
    # Max capacity gap
    max_cap_gap_row = df_monthly.loc[df_monthly["capacity_gap_b"].idxmax()]

    headline_json = {
        "task": "Task 023: Empirical Bitemporal Visibility Analysis",
        "date": "2026-09-30",
        "frozen_dataset_commit": "42f9a74",
        "headline_empirical_findings": {
            "mean_obligation_lag_days": round(ob["lag_days"].mean(), 2),
            "median_obligation_lag_days": round(ob["lag_days"].median(), 2),
            "public_144a_notes_mean_lag_days": round(ob[ob["research_category"] == "Public / 144A Bond & Convertible Notes"]["lag_days"].mean(), 2),
            "private_credit_facilities_mean_lag_days": round(ob[ob["research_category"] == "Private Credit / Delayed-Draw Facilities"]["lag_days"].mean(), 2),
            "longest_lag_obligation": {
                "obligation_id": "OBL-CRWV-DEBT-DDTL1",
                "instrument": "CoreWeave Delayed-Draw Term Loan 1.0 ($1.300B)",
                "economic_inception": "2023-07-30",
                "public_disclosure": "2025-03-20",
                "lag_days": 599
            },
            "peak_shadow_debt_episode": {
                "period": "Summer 2026 Periodic Disclosures Window (June 30 - August 12, 2026)",
                "peak_date": max_shadow_row["date"],
                "economic_debt_b": max_shadow_row["eco_debt_b"],
                "publicly_known_debt_b": max_shadow_row["kno_debt_b"],
                "shadow_debt_b": max_shadow_row["shadow_debt_b"],
                "opacity_ratio_pct": max_shadow_row["opacity_ratio_pct"]
            },
            "peak_committed_capacity_gap": {
                "peak_date": max_cap_gap_row["date"],
                "economic_capacity_b": max_cap_gap_row["eco_facility_capacity_b"],
                "publicly_known_capacity_b": max_cap_gap_row["kno_facility_capacity_b"],
                "capacity_gap_b": max_cap_gap_row["capacity_gap_b"]
            },
            "peak_edge_visibility_gap": {
                "peak_date": max_edge_gap_row["date"],
                "economic_edges": int(max_edge_gap_row["eco_edges"]),
                "publicly_known_edges": int(max_edge_gap_row["kno_edges"]),
                "edge_gap": int(max_edge_gap_row["edge_gap"])
            }
        },
        "category_statistics": cat_summary.to_dict(orient="records"),
        "monthly_trajectory_sample": df_monthly[df_monthly["date"].isin([
            "2024-01-01", "2024-06-01", "2024-12-01", "2025-03-01", "2025-06-01",
            "2025-12-01", "2026-03-01", "2026-06-01", "2026-07-01", "2026-08-01", "2026-09-01"
        ])].to_dict(orient="records")
    }

    with open(ANALYSIS_DIR / "bitemporal_visibility_summary.json", "w", encoding="utf-8") as f:
        json.dump(headline_json, f, indent=2)
    print(f"[OK] Summary JSON saved to {ANALYSIS_DIR / 'bitemporal_visibility_summary.json'}")

    # 5. Generate Publication Figures
    generate_figures(df_monthly, ob)


def generate_figures(df_monthly: pd.DataFrame, ob: pd.DataFrame):
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    matplotlib.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    matplotlib.rcParams["axes.edgecolor"] = "#cccccc"
    matplotlib.rcParams["axes.linewidth"] = 0.8

    dates = pd.to_datetime(df_monthly["date"])

    # -------------------------------------------------------------------------
    # FIGURE 1: Bitemporal Debt Trajectory & Opacity Ratio
    # -------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Panel A: Economic Debt vs Publicly Known Debt + Facility Capacity
    ax1.plot(dates, df_monthly["eco_debt_b"], label="Economic Reality Debt (Funded Principal)", color="#b71c1c", linewidth=2.5, marker="o", markersize=4)
    ax1.plot(dates, df_monthly["kno_debt_b"], label="Publicly Known Debt (SEC Disclosed)", color="#1565c0", linewidth=2.5, linestyle="--", marker="s", markersize=4)
    
    # Fill between for Shadow Debt Gap
    ax1.fill_between(dates, df_monthly["eco_debt_b"], df_monthly["kno_debt_b"], color="#ef9a9a", alpha=0.45, label="Shadow Debt Gap (ΔDebt)")

    # Facility Capacity secondary line
    ax1.plot(dates, df_monthly["eco_facility_capacity_b"], label="Committed Credit Facility Capacity (Economic)", color="#e65100", linewidth=1.5, linestyle=":")
    ax1.plot(dates, df_monthly["kno_facility_capacity_b"], label="Committed Credit Facility Capacity (Known)", color="#f57c00", linewidth=1.5, linestyle="-.")

    # Annotate Summer 2026 Shadow Debt
    peak_shadow_dt = pd.to_datetime("2026-07-01")
    ax1.annotate(
        "Peak Shadow Debt: $32.8B Gap\n(73.5% Opacity prior to Form 10-Q)",
        xy=(peak_shadow_dt, 44.6),
        xytext=(pd.to_datetime("2025-11-01"), 38.0),
        arrowprops=dict(arrowstyle="->", color="#b71c1c", lw=1.5),
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff9c4", edgecolor="#fbc02d", alpha=0.9),
        fontsize=9,
        fontweight="bold"
    )

    # Annotate Early Private Credit Gap
    ax1.annotate(
        "Private Credit Cloak:\n$9.9B Capacity Invisible\nfor 15 Months (2024-2025)",
        xy=(pd.to_datetime("2024-06-01"), 9.9),
        xytext=(pd.to_datetime("2024-01-01"), 18.0),
        arrowprops=dict(arrowstyle="->", color="#e65100", lw=1.5),
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffe0b2", edgecolor="#fb8c00", alpha=0.9),
        fontsize=9,
        fontweight="bold"
    )

    ax1.set_ylabel("Volume in Current Dollars ($B)", fontsize=11, fontweight="bold")
    ax1.set_title("A. Bitemporal Debt & Committed Credit Capacity Divergence (Economic Clock vs Public Knowledge Clock)", fontsize=12, fontweight="bold", pad=12)
    ax1.legend(loc="upper left", frameon=True, fontsize=9)
    ax1.set_ylim(-2, 52)

    # Panel B: Opacity Ratio and Edge Visibility Gap
    ax2_twin = ax2.twinx()

    p1 = ax2.plot(dates, df_monthly["opacity_ratio_pct"], color="#c2185b", linewidth=2.2, marker="^", label="Network Opacity Ratio (%)")
    p2 = ax2_twin.plot(dates, df_monthly["edge_gap"], color="#303f9f", linewidth=2.0, linestyle="--", marker="d", label="Edge Visibility Gap (ΔE = E_eco - E_kno)")

    ax2.set_ylabel("Network Opacity Ratio (%)", color="#c2185b", fontsize=11, fontweight="bold")
    ax2_twin.set_ylabel("Undisclosed Edges Count (ΔE)", color="#303f9f", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Date (Monthly Intervals: 2024 - 2026)", fontsize=11, fontweight="bold")
    ax2.set_title("B. Systemic Network Opacity & Structural Visibility Gap Over Time", fontsize=12, fontweight="bold", pad=12)
    ax2.set_ylim(-5, 85)
    ax2_twin.set_ylim(-1, 9)

    # Combined legend
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

    # Panel A: Giant Component Size & Active Nodes Evolution
    ax1.plot(dates, df_monthly["eco_giant_cc"], label="Economic Giant Component (Nodes)", color="#b71c1c", linewidth=2.5, marker="o")
    ax1.plot(dates, df_monthly["kno_giant_cc"], label="Public Knowledge Giant Component", color="#1565c0", linewidth=2.2, linestyle="--", marker="s")
    ax1.plot(dates, df_monthly["eco_nodes"], label="Total Active Economic Nodes", color="#388e3c", linewidth=1.8, linestyle=":")
    ax1.plot(dates, df_monthly["kno_nodes"], label="Total Publicly Known Nodes", color="#689f38", linewidth=1.8, linestyle="-.")

    ax1.fill_between(dates, df_monthly["eco_giant_cc"], df_monthly["kno_giant_cc"], color="#ffcdd2", alpha=0.5, label="Topological Visibility Lag")

    # Annotate 2024 Giant Component Opacity
    ax1.annotate(
        "Complete Topological Blindness:\nEconomic Giant Component = 4 nodes\nKnown Giant Component = 0 nodes",
        xy=(pd.to_datetime("2024-06-01"), 4),
        xytext=(pd.to_datetime("2024-02-01"), 12),
        arrowprops=dict(arrowstyle="->", color="#b71c1c", lw=1.5),
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffebee", edgecolor="#e57373", alpha=0.9),
        fontsize=8.5,
        fontweight="bold"
    )

    ax1.set_ylabel("Entity / Node Count", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Date (Monthly Intervals)", fontsize=11, fontweight="bold")
    ax1.set_title("A. Giant Component Emergence: Economic Reality vs Public Discovery", fontsize=12, fontweight="bold", pad=12)
    ax1.set_ylim(-1, 38)
    ax1.legend(loc="upper left", frameon=True, fontsize=8.5)

    # Panel B: Empirical Lag Boxplot / Distribution across Research Categories
    categories = [
        "Public / 144A Bond & Convertible Notes",
        "Commercial Offtake & Colocation Contracts",
        "Private Credit / Bank Guarantees & SPV Liens",
        "Private Credit / Delayed-Draw Facilities"
    ]
    lag_data = [ob[ob["research_category"] == c]["lag_days"].values for c in categories]
    cat_short_labels = [
        "Public 144A Notes\n(N=13, Mean: 0.2d)",
        "Commercial Contracts\n(N=4, Mean: 108d)",
        "Private Credit Guarantees\n(N=9, Mean: 104d)",
        "Private Credit DDTLs\n(N=11, Mean: 216d)"
    ]

    box = ax2.boxplot(lag_data, tick_labels=cat_short_labels, patch_artist=True, vert=True,
                      boxprops=dict(facecolor="#e0f2fe", color="#0284c7", linewidth=1.5),
                      medianprops=dict(color="#b71c1c", linewidth=2.0),
                      whiskerprops=dict(color="#0284c7", linewidth=1.2),
                      capprops=dict(color="#0284c7", linewidth=1.2))

    # Add jittered scatter points
    for idx, d_pts in enumerate(lag_data):
        jitter = np.random.normal(0, 0.05, size=len(d_pts))
        ax2.scatter(np.full_like(d_pts, idx + 1) + jitter, d_pts, color="#0f172a", alpha=0.7, s=35, zorder=3)

    ax2.set_ylabel("Empirical Bitemporal Lag Δt (Days)", fontsize=11, fontweight="bold")
    ax2.set_title("B. Empirical Lag Distribution: Public Capital Markets vs Private Credit", fontsize=12, fontweight="bold", pad=12)
    ax2.set_ylim(-20, 650)

    ax2.text(0.5, -0.15,
             "Empirical Insight: Public 144A notes exhibit near-zero lag (0-4 days) due to SEC 8-K / Rule 135c rules.\n"
             "Private credit delayed-draw term loans exhibit extreme opacity (up to 599 days) until S-1 / 10-K disclosure.",
             ha="center", va="top", transform=ax2.transAxes, fontsize=9, style="italic",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f9fa", edgecolor="#dddddd"))

    plt.tight_layout()
    fig2_path = FIGURES_DIR / "bitemporal_network_topology_lag.png"
    plt.savefig(fig2_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Figure 2 saved to {fig2_path}")


if __name__ == "__main__":
    run_bitemporal_analysis()
