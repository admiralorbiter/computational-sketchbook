"""
Phase 1 Power Backplane & Physical Dependency Analysis Engine (ADR-020)
Analyzes the multi-layer topological join between corporate financial obligations
and the physical facility/utility/grid backplane:
1. Tripartite & Consolidated Joint Network construction.
2. Topological Join: component consolidation, articulation points, and bridge analysis.
3. CoreWeave Excision Experiment: does the network survive through ERCOT?
4. ERCOT Articulation Test: ERCOT as the single physical bridge.
5. Regional Grid Fragmentation & Typed MW Concentration (HHI).
6. Power Curtailment & Firmness Risk Structure.
7. Generates publication-grade figures and machine-readable JSON/CSV summaries.
"""

from pathlib import Path
import json
from typing import Dict, List, Set, Any, Tuple
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    from .graph import ObligationNetwork
except ImportError:
    from graph import ObligationNetwork

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "analysis"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def build_joint_network(as_of_date: str = "2026-09-28"):
    """
    Constructs the consolidated joint network combining:
      1. Consolidated corporate financial graph (SPVs unwrapped to parents)
      2. Physical power connections: Operator <-> Utility, Utility <-> Grid, Operator <-> Grid
    """
    net = ObligationNetwork().economic_as_of(as_of_date)
    G_cons = net.unwrap_spv_perimeter()

    fac_df = pd.read_parquet(PROCESSED_DIR / "facilities.parquet")
    pwr_df = pd.read_parquet(PROCESSED_DIR / "power_relationships.parquet")
    ent_df = pd.read_parquet(PROCESSED_DIR / "entities.parquet").set_index("entity_id")

    # Joint MultiDiGraph preserving parallel edges
    M_joint = nx.MultiGraph()
    # Add financial edges from G_cons
    for u, v, k, data in G_cons.edges(keys=True, data=True):
        M_joint.add_edge(u, v, key=f"fin_{k}", edge_layer="financial", **data)

    # Add physical power edges
    for _, r in pwr_df.iterrows():
        fid = r["facility_id"]
        fac = fac_df[fac_df["facility_id"] == fid].iloc[0]
        op = fac["operator_entity_id"]
        tenant = fac["tenant_entity_id"]
        util = r["utility_entity_id"]
        grid = r["grid_operator_entity_id"]
        rel_type = r["relationship_type"]
        firmness = r["firm_or_interruptible"]

        # Operator to Utility
        if pd.notna(util):
            M_joint.add_edge(
                op, util,
                key=f"pwr_{r['power_rel_id']}_util",
                edge_layer="physical_power",
                edge_type="utility_service",
                facility_id=fid,
                relationship_type=rel_type,
                firmness=firmness
            )
        # Utility to Grid Operator
        if pd.notna(util) and pd.notna(grid):
            M_joint.add_edge(
                util, grid,
                key=f"pwr_{r['power_rel_id']}_grid",
                edge_layer="physical_power",
                edge_type="grid_interconnect",
                facility_id=fid,
                relationship_type=rel_type,
                firmness=firmness
            )
        # Operator direct to Grid (wholesale market / large load interconnection)
        if pd.notna(grid):
            M_joint.add_edge(
                op, grid,
                key=f"pwr_{r['power_rel_id']}_direct_grid",
                edge_layer="physical_power",
                edge_type="direct_grid_market",
                facility_id=fid,
                relationship_type=rel_type,
                firmness=firmness
            )

    # Simple undirected projection
    U_joint = nx.Graph(M_joint)
    # Filter to active nodes
    active_nodes = [n for n in U_joint.nodes() if U_joint.degree(n) > 0]
    U_joint_active = U_joint.subgraph(active_nodes).copy()
    M_joint_active = M_joint.subgraph(active_nodes).copy()

    # Also build the pure financial active graph for baseline comparison
    U_fin = nx.Graph(G_cons)
    active_fin = [n for n in U_fin.nodes() if U_fin.degree(n) > 0]
    U_fin_active = U_fin.subgraph(active_fin).copy()

    return {
        "G_cons": G_cons,
        "U_fin_active": U_fin_active,
        "U_joint_active": U_joint_active,
        "M_joint_active": M_joint_active,
        "fac_df": fac_df,
        "pwr_df": pwr_df,
        "ent_df": ent_df
    }


def analyze_topological_join(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compares baseline pure financial graph vs joint financial-physical graph:
    component counts, articulation points, bridges, and centrality.
    """
    U_fin = data["U_fin_active"]
    U_joint = data["U_joint_active"]
    M_joint = data["M_joint_active"]
    ent_df = data["ent_df"]

    # Components
    fin_comps = [sorted(list(c)) for c in sorted(nx.connected_components(U_fin), key=len, reverse=True)]
    joint_comps = [sorted(list(c)) for c in sorted(nx.connected_components(U_joint), key=len, reverse=True)]

    # Articulation points
    fin_art = sorted(list(nx.articulation_points(U_fin)))
    joint_art = sorted(list(nx.articulation_points(U_joint)))

    # Bridges on simple projection
    fin_bridges = [sorted(list(b)) for b in nx.bridges(U_fin)]
    joint_bridges = [sorted(list(b)) for b in nx.bridges(U_joint)]

    # Multigraph single-contract / single-link bridges
    joint_multigraph_bridges = []
    for u, v in nx.bridges(U_joint):
        edge_count = M_joint.number_of_edges(u, v)
        if edge_count == 1:
            joint_multigraph_bridges.append((u, v))

    # Centrality metrics on Joint Graph
    deg_cent = nx.degree_centrality(U_joint)
    bet_cent = nx.betweenness_centrality(U_joint)
    close_cent = nx.closeness_centrality(U_joint)

    centrality_records = []
    for n in U_joint.nodes():
        cat = ent_df.loc[n, "category"] if n in ent_df.index else "unknown"
        centrality_records.append({
            "entity_id": n,
            "category": cat,
            "degree": U_joint.degree(n),
            "degree_centrality": round(deg_cent[n], 4),
            "betweenness_centrality": round(bet_cent[n], 4),
            "closeness_centrality": round(close_cent[n], 4),
        })
    centrality_df = pd.DataFrame(centrality_records).sort_values("betweenness_centrality", ascending=False)
    centrality_df.to_csv(OUTPUT_DIR / "joint_network_centrality.csv", index=False)

    return {
        "financial_baseline": {
            "node_count": U_fin.number_of_nodes(),
            "edge_count": U_fin.number_of_edges(),
            "component_count": len(fin_comps),
            "largest_component_size": len(fin_comps[0]) if fin_comps else 0,
            "components": fin_comps,
            "articulation_points": fin_art,
            "simple_bridges_count": len(fin_bridges),
        },
        "joint_network": {
            "node_count": U_joint.number_of_nodes(),
            "edge_count": U_joint.number_of_edges(),
            "multigraph_edge_count": M_joint.number_of_edges(),
            "component_count": len(joint_comps),
            "largest_component_size": len(joint_comps[0]) if joint_comps else 0,
            "components": joint_comps,
            "articulation_points": joint_art,
            "simple_bridges_count": len(joint_bridges),
            "multigraph_bridges_count": len(joint_multigraph_bridges),
        },
        "centrality_top10": centrality_df.head(10).to_dict(orient="records")
    }


def analyze_excision_scenarios(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Tests node removal (excision) on both the financial graph and the joint graph.
    Specifically evaluates:
      - Removing CoreWeave (CRWV)
      - Removing ERCOT
      - Removing AEP_TEXAS
      - Removing APLD
      - Removing CORZ
      - Removing IREN
    """
    U_fin = data["U_fin_active"]
    U_joint = data["U_joint_active"]

    test_nodes = ["CRWV", "ERCOT", "CORZ", "APLD", "IREN", "AEP_TEXAS", "MDU", "MISO"]
    results = []

    for node in test_nodes:
        # 1. Removal on Financial Graph (if present)
        fin_impact = None
        if node in U_fin:
            U_f_sub = U_fin.copy()
            U_f_sub.remove_node(node)
            act_f = [n for n in U_f_sub if U_f_sub.degree(n) > 0]
            comps_f = [sorted(list(c)) for c in sorted(nx.connected_components(U_f_sub.subgraph(act_f)), key=len, reverse=True)]
            iso_f = [n for n in U_f_sub if U_f_sub.degree(n) == 0]
            fin_impact = {
                "active_nodes": len(act_f),
                "component_count": len(comps_f),
                "largest_comp_size": len(comps_f[0]) if comps_f else 0,
                "isolated_count": len(iso_f),
                "isolated_nodes": sorted(iso_f),
                "components": comps_f
            }

        # 2. Removal on Joint Graph
        U_j_sub = U_joint.copy()
        U_j_sub.remove_node(node)
        act_j = [n for n in U_j_sub if U_j_sub.degree(n) > 0]
        comps_j = [sorted(list(c)) for c in sorted(nx.connected_components(U_j_sub.subgraph(act_j)), key=len, reverse=True)]
        iso_j = [n for n in U_j_sub if U_j_sub.degree(n) == 0]
        joint_impact = {
            "active_nodes": len(act_j),
            "component_count": len(comps_j),
            "largest_comp_size": len(comps_j[0]) if comps_j else 0,
            "isolated_count": len(iso_j),
            "isolated_nodes": sorted(iso_j),
            "components": comps_j
        }

        results.append({
            "target_node": node,
            "financial_baseline_impact": fin_impact,
            "joint_network_impact": joint_impact
        })

    # Save CSV comparison
    rows = []
    for r in results:
        tn = r["target_node"]
        fi = r["financial_baseline_impact"]
        ji = r["joint_network_impact"]
        rows.append({
            "target_node": tn,
            "fin_active_nodes": fi["active_nodes"] if fi else "N/A",
            "fin_components": fi["component_count"] if fi else "N/A",
            "fin_largest_comp": fi["largest_comp_size"] if fi else "N/A",
            "fin_isolated_nodes": fi["isolated_count"] if fi else "N/A",
            "joint_active_nodes": ji["active_nodes"],
            "joint_components": ji["component_count"],
            "joint_largest_comp": ji["largest_comp_size"],
            "joint_isolated_nodes": ji["isolated_count"],
            "joint_orphaned_list": ",".join(ji["isolated_nodes"])
        })
    excision_df = pd.DataFrame(rows)
    excision_df.to_csv(OUTPUT_DIR / "power_network_excision_comparison.csv", index=False)
    return results


def analyze_regional_grid_and_mw():
    """
    Analyzes MW capacity distribution across RTO/grid regions and typed MW categories.
    Calculates Herfindahl-Hirschman Index (HHI) for regional grid concentration.
    """
    fac_df = pd.read_parquet(PROCESSED_DIR / "facilities.parquet")
    pwr_facts = pd.read_parquet(PROCESSED_DIR / "power_facts.parquet")
    pwr_rels = pd.read_parquet(PROCESSED_DIR / "power_relationships.parquet")

    # Merge facts with facility metadata to attach grid region and operator
    merged = pwr_facts.merge(
        fac_df[["facility_id", "operator_entity_id", "primary_grid_region", "city", "state_or_country"]],
        on="facility_id", how="left"
    )

    # Standardize grid region names (NYISO_ZONE_A -> NYISO, FINGRID_NORDIC -> Fingrid)
    region_map = {
        "NYISO_ZONE_A": "NYISO",
        "FINGRID_NORDIC": "Fingrid"
    }
    merged["grid_region"] = merged["primary_grid_region"].replace(region_map)

    # Pivot: Grid Region x MW Type
    pivot_mw = merged.pivot_table(
        index="grid_region",
        columns="mw_type",
        values="value_mw",
        aggfunc="sum",
        fill_value=0.0
    ).reset_index()

    # Ensure all expected typed MW columns exist
    mw_types = [
        "critical_it_mw", "leased_customer_mw", "gross_utility_capacity_mw",
        "contracted_service_mw", "energized_mw", "planned_mw", "interconnection_request_mw"
    ]
    for col in mw_types:
        if col not in pivot_mw.columns:
            pivot_mw[col] = 0.0

    # Add total capacity metrics
    pivot_mw["total_firm_and_utility_mw"] = (
        pivot_mw["gross_utility_capacity_mw"] + pivot_mw["contracted_service_mw"]
    )
    pivot_mw.to_csv(OUTPUT_DIR / "regional_grid_mw_breakdown.csv", index=False)

    # Calculate Regional Grid Concentration (HHI)
    # HHI based on total gross utility + contracted service MW
    total_srv_mw = pivot_mw["total_firm_and_utility_mw"].sum()
    shares = (pivot_mw["total_firm_and_utility_mw"] / total_srv_mw) * 100.0
    hhi_service = (shares ** 2).sum()

    # HHI based on energized MW
    total_energized_mw = pivot_mw["energized_mw"].sum()
    shares_energized = (pivot_mw[pivot_mw["energized_mw"] > 0]["energized_mw"] / total_energized_mw) * 100.0
    hhi_energized = (shares_energized ** 2).sum()

    # HHI based on planned / pipeline MW
    total_planned = pivot_mw["planned_mw"].sum()
    shares_planned = (pivot_mw[pivot_mw["planned_mw"] > 0]["planned_mw"] / total_planned) * 100.0
    hhi_planned = (shares_planned ** 2).sum()

    # Facility-level breakdown
    fac_breakdown = merged.groupby(["facility_id", "operator_entity_id", "grid_region", "mw_type"])["value_mw"].sum().unstack(fill_value=0.0).reset_index()
    fac_breakdown.to_csv(OUTPUT_DIR / "facility_typed_mw_summary.csv", index=False)

    return {
        "pivot_mw": pivot_mw.to_dict(orient="records"),
        "total_service_mw": float(total_srv_mw),
        "total_energized_mw": float(total_energized_mw),
        "total_planned_mw": float(total_planned),
        "hhi_utility_service": round(float(hhi_service), 1),
        "hhi_energized": round(float(hhi_energized), 1),
        "hhi_planned": round(float(hhi_planned), 1),
        "regional_shares_pct": dict(zip(pivot_mw["grid_region"], [round(s, 2) for s in shares]))
    }


def analyze_curtailment_and_firmness():
    """
    Analyzes power firmness vs curtailable capacity and regulatory regimes.
    """
    pwr_rels = pd.read_parquet(PROCESSED_DIR / "power_relationships.parquet")
    pwr_facts = pd.read_parquet(PROCESSED_DIR / "power_facts.parquet")
    fac_df = pd.read_parquet(PROCESSED_DIR / "facilities.parquet")

    # Link relationships with facts
    merged = pwr_rels.merge(fac_df[["facility_id", "facility_name", "operator_entity_id", "primary_grid_region"]], on="facility_id")

    firmness_counts = merged["firm_or_interruptible"].value_counts().to_dict()

    # Sum capacity by firmness category
    # Attach gross utility or contracted MW
    cap_facts = pwr_facts[pwr_facts["mw_type"].isin(["gross_utility_capacity_mw", "contracted_service_mw"])]
    merged_cap = merged.merge(cap_facts[["power_rel_id", "value_mw", "mw_type"]], on="power_rel_id", how="left")

    firmness_mw = merged_cap.groupby("firm_or_interruptible")["value_mw"].sum().to_dict()

    curtailment_details = []
    for _, r in merged.iterrows():
        curtailment_details.append({
            "power_rel_id": r["power_rel_id"],
            "facility_name": r["facility_name"],
            "operator": r["operator_entity_id"],
            "grid_region": r["primary_grid_region"],
            "utility": r["utility_entity_id"],
            "firm_or_interruptible": r["firm_or_interruptible"],
            "curtailment_rights": r["curtailment_rights"],
            "tariff_structure": r["tariff_structure"]
        })

    return {
        "firmness_contract_counts": firmness_counts,
        "firmness_capacity_mw": firmness_mw,
        "curtailment_details": curtailment_details
    }


def generate_figures(data: Dict[str, Any], mw_analysis: Dict[str, Any], curtailment_analysis: Dict[str, Any]):
    """
    Generates high-resolution publication-quality figures:
      1. power_joint_network_topology.png
      2. regional_grid_mw_distribution.png
      3. power_curtailment_structure.png
    """
    U_joint = data["U_joint_active"]
    ent_df = data["ent_df"]

    # -------------------------------------------------------------
    # Figure 1: Joint Network Topology
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    pos = nx.spring_layout(U_joint, k=0.45, seed=42, iterations=100)

    # Color map by entity category
    category_colors = {
        "neocloud_operator": "#E63946",       # Coral Red (CoreWeave)
        "datacenter_developer": "#457B9D",   # Slate Blue (APLD, CORZ, WULF, HUT, IREN)
        "hyperscaler_anchor": "#2A9D8F",     # Teal (MSFT, META)
        "hardware_supplier": "#1D3557",      # Navy (NVDA)
        "server_oem": "#F4A261",             # Ochre (SMCI, DELL, HPE)
        "private_credit_syndicate": "#6B705C",# Olive Grey
        "capital_provider": "#A5A58D",       # Muted Grey
        "electric_utility": "#E76F51",        # Terracotta / Orange
        "grid_operator_rto": "#9B5DE5",      # Purple
        "unknown": "#CCCCCC"
    }

    node_colors = []
    node_sizes = []
    for n in U_joint.nodes():
        cat = ent_df.loc[n, "category"] if n in ent_df.index else "unknown"
        node_colors.append(category_colors.get(cat, "#A8DADC"))
        deg = U_joint.degree(n)
        node_sizes.append(250 + deg * 120)

    # Draw edges
    # Separate financial edges vs physical power edges
    M_joint = data["M_joint_active"]
    fin_edges = []
    pwr_edges = []
    for u, v, data_dict in M_joint.edges(data=True):
        if data_dict.get("edge_layer") == "physical_power":
            pwr_edges.append((u, v))
        else:
            fin_edges.append((u, v))

    nx.draw_networkx_edges(U_joint, pos, edgelist=fin_edges, edge_color="#4A5568", alpha=0.5, width=1.5, ax=ax, style="solid")
    nx.draw_networkx_edges(U_joint, pos, edgelist=pwr_edges, edge_color="#9B5DE5", alpha=0.8, width=2.2, ax=ax, style="dashed")
    nx.draw_networkx_nodes(U_joint, pos, node_color=node_colors, node_size=node_sizes, alpha=0.9, edgecolors="#1A202C", linewidths=1.5, ax=ax)

    # Node labels
    labels = {n: n for n in U_joint.nodes()}
    nx.draw_networkx_labels(U_joint, pos, labels=labels, font_size=8, font_weight="bold", font_family="sans-serif", ax=ax)

    # Legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', label='Neocloud (CoreWeave)', markerfacecolor='#E63946', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Data Center / Compute Co', markerfacecolor='#457B9D', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Electric Utility', markerfacecolor='#E76F51', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Grid Operator / RTO', markerfacecolor='#9B5DE5', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Hyperscaler / Anchor Offtaker', markerfacecolor='#2A9D8F', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Credit Syndicate / Bank', markerfacecolor='#6B705C', markersize=10),
        plt.Line2D([0], [0], color='#4A5568', lw=2, label='Financial / Contractual Obligation'),
        plt.Line2D([0], [0], color='#9B5DE5', lw=2, linestyle='--', label='Physical Power Backplane Link'),
    ]
    ax.legend(handles=legend_elements, loc="upper right", frameon=True, fontsize=9, title="Network Layers")
    ax.set_title("AI Infrastructure Joint Corporate-Physical Power Backplane (ADR-020)\nMulti-Layer Topology: Financial Obligations + Electric Utilities + Transmission Grids", fontsize=13, fontweight="bold", pad=15)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "power_joint_network_topology.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Figure 2: Regional Grid MW Distribution
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    pivot_df = pd.DataFrame(mw_analysis["pivot_mw"]).set_index("grid_region")
    
    # Plot grouped bars for selected key MW types
    plot_cols = ["gross_utility_capacity_mw", "critical_it_mw", "contracted_service_mw", "energized_mw", "planned_mw"]
    labels = ["Gross Utility Capacity", "Critical IT Load", "Contracted Service", "Energized MW", "Planned Expansion"]
    colors = ["#264653", "#2A9D8F", "#E76F51", "#F4A261", "#E9C46A"]

    x = np.arange(len(pivot_df.index))
    width = 0.16
    for i, (col, label, color) in enumerate(zip(plot_cols, labels, colors)):
        ax.bar(x + i * width, pivot_df[col], width, label=label, color=color, alpha=0.9, edgecolor="black", linewidth=0.5)

    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(pivot_df.index, fontsize=11, fontweight="bold")
    ax.set_ylabel("Power Capacity (Megawatts - MW)", fontsize=11, fontweight="bold")
    ax.set_title("Regional Grid Power Footprint by Strictly Typed MW Category (ADR-020)\nERCOT Dominance vs. MISO, SERC, SPP, NYISO, and Fingrid", fontsize=12, fontweight="bold", pad=12)
    ax.legend(loc="upper right", frameon=True, fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "regional_grid_mw_distribution.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Figure 3: Curtailment and Firmness Structure
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    
    # Panel 1: Contract counts
    f_counts = curtailment_analysis["firmness_contract_counts"]
    ax1.pie(
        f_counts.values(),
        labels=[k.replace('_', ' ').title() for k in f_counts.keys()],
        autopct='%1.1f%%',
        colors=["#2A9D8F", "#E76F51", "#457B9D", "#CCCCCC"],
        startangle=140,
        wedgeprops={"edgecolor": "black", "linewidth": 1}
    )
    ax1.set_title("Power Contracts by Firmness Classification", fontsize=11, fontweight="bold")

    # Panel 2: Capacity MW by firmness
    f_mw = curtailment_analysis["firmness_capacity_mw"]
    ax2.pie(
        f_mw.values(),
        labels=[k.replace('_', ' ').title() for k in f_mw.keys()],
        autopct='%1.1f%%',
        colors=["#2A9D8F", "#E76F51", "#457B9D"],
        startangle=140,
        wedgeprops={"edgecolor": "black", "linewidth": 1}
    )
    ax2.set_title("Power Capacity (MW) by Firmness / Curtailment Exposure", fontsize=11, fontweight="bold")

    plt.suptitle("AI Infrastructure Power Reliability & Curtailment Architecture (ADR-020)", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "power_curtailment_structure.png", dpi=300)
    plt.close()


def run_power_analysis_sprint():
    print("=== Executing Phase 1 Power Backplane Analysis Sprint (ADR-020) ===")
    net_data = build_joint_network("2026-09-28")
    
    # 1. Topological join
    topo_res = analyze_topological_join(net_data)
    print("\n--- 1. Topological Join Summary ---")
    print(f"Financial Baseline: {topo_res['financial_baseline']['node_count']} nodes, {topo_res['financial_baseline']['component_count']} components (Largest: {topo_res['financial_baseline']['largest_component_size']} nodes)")
    print(f"Joint Network:      {topo_res['joint_network']['node_count']} nodes, {topo_res['joint_network']['component_count']} components (Largest: {topo_res['joint_network']['largest_component_size']} nodes)")
    print(f"Joint Articulation Points: {topo_res['joint_network']['articulation_points']}")

    # 2. Excision scenarios
    excision_res = analyze_excision_scenarios(net_data)
    print("\n--- 2. CoreWeave & Key Node Excision Analysis ---")
    crwv_exc = [r for r in excision_res if r["target_node"] == "CRWV"][0]
    print(f"CRWV Excision on Pure Financial Graph: {crwv_exc['financial_baseline_impact']['component_count']} components, {crwv_exc['financial_baseline_impact']['isolated_count']} isolated nodes")
    print(f"CRWV Excision on Joint Network:        {crwv_exc['joint_network_impact']['component_count']} components, {crwv_exc['joint_network_impact']['isolated_count']} isolated nodes")
    print(f"Surviving Joint Components without CRWV: {[len(c) for c in crwv_exc['joint_network_impact']['components']]}")

    # 3. Regional Grid and Typed MW
    mw_res = analyze_regional_grid_and_mw()
    print("\n--- 3. Regional Grid & Typed MW Analysis ---")
    print(f"Total Modeled Service Capacity: {mw_res['total_service_mw']:,.1f} MW")
    print(f"Total Energized Capacity:       {mw_res['total_energized_mw']:,.1f} MW")
    print(f"Total Planned Expansion:        {mw_res['total_planned_mw']:,.1f} MW")
    print(f"Grid HHI Concentration:         {mw_res['hhi_utility_service']} (Service), {mw_res['hhi_energized']} (Energized)")
    print(f"Regional Service Shares:        {mw_res['regional_shares_pct']}")

    # 4. Curtailment and Firmness
    curt_res = analyze_curtailment_and_firmness()
    print("\n--- 4. Power Firmness & Curtailment Risk ---")
    print(f"Contract Firmness Counts: {curt_res['firmness_contract_counts']}")
    print(f"Capacity MW by Firmness:  {curt_res['firmness_capacity_mw']}")

    # 5. Generate Figures
    generate_figures(net_data, mw_res, curt_res)
    print("\n[OK] High-resolution figures generated in outputs/figures/")

    # 6. Save comprehensive summary JSON
    summary = {
        "analysis_id": "PHASE1-POWER-SPRINT-020",
        "as_of_date": "2026-09-28",
        "topological_join": topo_res,
        "excision_experiments": excision_res,
        "regional_grid_mw": mw_res,
        "curtailment_structure": curt_res
    }
    with open(OUTPUT_DIR / "power_sprint_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[OK] Summary exported to {OUTPUT_DIR / 'power_sprint_summary.json'}")

    return summary


if __name__ == "__main__":
    run_power_analysis_sprint()
