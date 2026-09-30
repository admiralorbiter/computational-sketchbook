"""
Phase 1 Power Backplane & Physical Dependency Analysis Engine (ADR-020.1 Hardened)
Analyzes the literal multi-layer topological join between corporate financial obligations
and the physical facility/utility/grid backplane:
  1. Literal Multi-Layer Topology: corporate operator -> facility -> utility -> grid
     (Zero synthetic shortcuts; SERC excluded as operational grid node).
  2. Topological Join: component consolidation, cut-vertices (articulation points), and bridge analysis.
  3. CoreWeave Excision Experiment: tests whether ERCOT acts as a physical bridge preserving connectivity.
  4. ERCOT Articulation Test: excision of ERCOT isolates Texas power participants.
  5. Regional Grid Exposure Concentration Index (HHI-form) on non-overlapping capacity basis.
  6. Mechanism-Specific Reliability Regimes & Energized vs. Contracted MW Disaggregation.
  7. High-resolution publication figures and machine-readable summaries.
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


def build_joint_network(as_of_date: str = "2026-09-28") -> Dict[str, Any]:
    """
    Constructs the literal multi-layer network combining:
      1. Consolidated corporate financial graph (SPVs unwrapped to parents)
      2. Physical power connections:
         Operator -> Facility -> Utility -> Grid
         (No synthetic operator -> grid shortcuts; SERC excluded as operational node).
    """
    net = ObligationNetwork().economic_as_of(as_of_date)
    G_cons = net.unwrap_spv_perimeter()

    fac_df = pd.read_parquet(PROCESSED_DIR / "facilities.parquet")
    pwr_df = pd.read_parquet(PROCESSED_DIR / "power_relationships.parquet")
    ent_df = pd.read_parquet(PROCESSED_DIR / "entities.parquet").set_index("entity_id")

    # Joint MultiGraph preserving parallel legal and physical contracts
    M_joint = nx.MultiGraph()

    # 1. Financial Layer (corporate obligations)
    for u, v, k, data in G_cons.edges(keys=True, data=True):
        M_joint.add_edge(u, v, key=f"fin_{k}", edge_layer="financial", **data)

    # 2. Corporate Operator -> Physical Facility
    for _, fac in fac_df.iterrows():
        op = fac["operator_entity_id"]
        fid = fac["facility_id"]
        M_joint.add_edge(
            op, fid,
            key=f"fac_op_{fid}",
            edge_layer="facility_assignment",
            edge_type="operator_facility",
            facility_name=fac["facility_name"],
            state=fac["state_or_country"]
        )

    # 3. Physical Power Relationships (Facility -> Utility -> Grid)
    for _, r in pwr_df.iterrows():
        fid = r["facility_id"]
        util = r["utility_entity_id"]
        grid = r["grid_operator_entity_id"]
        rel_id = r["power_rel_id"]
        rel_type = r["relationship_type"]
        regime = r["reliability_regime"]
        cap_mw = r["capacity_basis_mw"]

        # Facility -> Utility
        if pd.notna(util):
            M_joint.add_edge(
                fid, util,
                key=f"pwr_{rel_id}_fac_util",
                edge_layer="physical_power",
                edge_type="facility_utility",
                power_rel_id=rel_id,
                relationship_type=rel_type,
                reliability_regime=regime,
                capacity_basis_mw=cap_mw
            )
            # Utility -> Grid Operator (excluding SERC)
            if pd.notna(grid) and grid != "SERC":
                M_joint.add_edge(
                    util, grid,
                    key=f"pwr_{rel_id}_util_grid",
                    edge_layer="physical_power",
                    edge_type="utility_grid",
                    power_rel_id=rel_id,
                    relationship_type=rel_type,
                    reliability_regime=regime,
                    capacity_basis_mw=cap_mw
                )
        elif pd.notna(grid) and grid != "SERC":
            # Direct facility transmission interconnection when utility is absent
            M_joint.add_edge(
                fid, grid,
                key=f"pwr_{rel_id}_fac_grid",
                edge_layer="physical_power",
                edge_type="facility_direct_grid",
                power_rel_id=rel_id,
                relationship_type=rel_type,
                reliability_regime=regime,
                capacity_basis_mw=cap_mw
            )

    # Simple undirected projection for topological metrics
    U_joint = nx.Graph(M_joint)
    active_nodes = [n for n in U_joint.nodes() if U_joint.degree(n) > 0]
    U_joint_active = U_joint.subgraph(active_nodes).copy()
    M_joint_active = M_joint.subgraph(active_nodes).copy()

    # Baseline pure financial active graph
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
    Analyzes topological differences between the baseline financial network
    and the literal multi-layer facility-first joint network.
    """
    U_fin = data["U_fin_active"]
    U_joint = data["U_joint_active"]
    M_joint = data["M_joint_active"]
    ent_df = data["ent_df"]

    # Connected components
    fin_comps = [sorted(list(c)) for c in sorted(nx.connected_components(U_fin), key=len, reverse=True)]
    joint_comps = [sorted(list(c)) for c in sorted(nx.connected_components(U_joint), key=len, reverse=True)]

    # Articulation points (cut-vertices)
    fin_art = sorted(list(nx.articulation_points(U_fin)))
    joint_art = sorted(list(nx.articulation_points(U_joint)))

    # Bridges on simple projection
    fin_bridges = [sorted(list(b)) for b in nx.bridges(U_fin)]
    joint_bridges = [sorted(list(b)) for b in nx.bridges(U_joint)]

    # Multigraph bridges (edges where multiplicity == 1)
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
        if n.startswith("FAC-"):
            cat = "physical_facility"
        elif n in ent_df.index:
            cat = ent_df.loc[n, "category"]
        else:
            cat = "unknown"

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
    Tests node excision across financial and literal joint networks.
    Evaluates:
      - Removing CoreWeave (CRWV): reveals ERCOT power bridge preserving connectivity
      - Removing ERCOT: cuts off Texas participant cluster
      - Removing key operators and utilities (CORZ, APLD, IREN, AEP_TEXAS, MDU, MISO)
    """
    U_fin = data["U_fin_active"]
    U_joint = data["U_joint_active"]

    test_nodes = ["CRWV", "ERCOT", "CORZ", "APLD", "IREN", "AEP_TEXAS", "MDU", "MISO"]
    results = []

    for node in test_nodes:
        # Financial Graph Excision
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

        # Joint Network Excision
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


def analyze_regional_grid_and_mw() -> Dict[str, Any]:
    """
    Computes non-overlapping Grid Exposure Concentration Index (HHI-form)
    across grid regions using strictly one capacity_basis_mw per relationship.
    Separates contracted service basis from energized and planned pipeline MW.
    """
    fac_df = pd.read_parquet(PROCESSED_DIR / "facilities.parquet")
    pwr_facts = pd.read_parquet(PROCESSED_DIR / "power_facts.parquet")
    pwr_rels = pd.read_parquet(PROCESSED_DIR / "power_relationships.parquet")

    # Map relationships to primary grid region
    # Relationships with None grid operator are local municipal / non-RTO
    rels_with_grid = pwr_rels.copy()
    grid_map = {
        "ERCOT": "ERCOT",
        "MISO": "MISO",
        "SPP": "SPP",
        "NYISO": "NYISO",
        "FINGRID": "Fingrid",
    }
    rels_with_grid["grid_region"] = rels_with_grid["grid_operator_entity_id"].map(grid_map).fillna("Non-RTO")

    # 1. Non-Overlapping Capacity Basis MW by Grid Region
    reg_basis = rels_with_grid.groupby("grid_region")["capacity_basis_mw"].agg(["count", "sum"]).reset_index()
    total_basis_mw = reg_basis["sum"].sum()
    reg_basis["share_pct"] = (reg_basis["sum"] / total_basis_mw) * 100.0
    hhi_basis = float((reg_basis["share_pct"] ** 2).sum())

    # 2. Energized MW by Grid Region
    fac_region_map = dict(zip(fac_df["facility_id"], fac_df["primary_grid_region"].map(grid_map).fillna("Non-RTO")))
    en_facts = pwr_facts[pwr_facts["mw_type"] == "energized_mw"].copy()
    en_facts["grid_region"] = en_facts["facility_id"].map(fac_region_map)
    reg_en = en_facts.groupby("grid_region")["value_mw"].sum().reset_index()
    total_en_mw = reg_en["value_mw"].sum()
    reg_en["share_pct"] = (reg_en["value_mw"] / total_en_mw) * 100.0
    hhi_energized = float((reg_en["share_pct"] ** 2).sum())

    # 3. Planned / Pipeline MW by Grid Region
    plan_facts = pwr_facts[pwr_facts["mw_type"] == "planned_mw"].copy()
    plan_facts["grid_region"] = plan_facts["facility_id"].map(fac_region_map)
    reg_plan = plan_facts.groupby("grid_region")["value_mw"].sum().reset_index()
    total_plan_mw = reg_plan["value_mw"].sum()
    reg_plan["share_pct"] = (reg_plan["value_mw"] / total_plan_mw) * 100.0
    hhi_planned = float((reg_plan["share_pct"] ** 2).sum())

    # Combined regional summary table
    all_regions = sorted(list(set(reg_basis["grid_region"]).union(set(reg_en["grid_region"]))))
    summary_rows = []
    for r in all_regions:
        b_val = reg_basis[reg_basis["grid_region"] == r]["sum"].sum() if r in set(reg_basis["grid_region"]) else 0.0
        e_val = reg_en[reg_en["grid_region"] == r]["value_mw"].sum() if r in set(reg_en["grid_region"]) else 0.0
        p_val = reg_plan[reg_plan["grid_region"] == r]["value_mw"].sum() if r in set(reg_plan["grid_region"]) else 0.0
        summary_rows.append({
            "grid_region": r,
            "capacity_basis_mw": round(b_val, 1),
            "capacity_share_pct": round((b_val / total_basis_mw) * 100.0, 2),
            "energized_mw": round(e_val, 1),
            "energized_share_pct": round((e_val / total_en_mw) * 100.0, 2) if total_en_mw > 0 else 0.0,
            "planned_mw": round(p_val, 1)
        })
    regional_summary_df = pd.DataFrame(summary_rows).sort_values("capacity_basis_mw", ascending=False)
    regional_summary_df.to_csv(OUTPUT_DIR / "regional_grid_mw_breakdown.csv", index=False)

    # Facility-level typed MW summary
    merged_facts = pwr_facts.merge(
        fac_df[["facility_id", "facility_name", "operator_entity_id", "primary_grid_region", "city", "state_or_country"]],
        on="facility_id", how="left"
    )
    fac_summary = merged_facts.groupby(["facility_id", "operator_entity_id", "primary_grid_region", "mw_type"])["value_mw"].sum().unstack(fill_value=0.0).reset_index()
    fac_summary.to_csv(OUTPUT_DIR / "facility_typed_mw_summary.csv", index=False)

    return {
        "regional_breakdown": regional_summary_df.to_dict(orient="records"),
        "total_capacity_basis_mw": round(total_basis_mw, 1),
        "total_energized_mw": round(total_en_mw, 1),
        "total_planned_mw": round(total_plan_mw, 1),
        "hhi_capacity_basis": round(hhi_basis, 1),
        "hhi_energized": round(hhi_energized, 1),
        "hhi_planned": round(hhi_planned, 1),
        "regional_shares_pct": dict(zip(regional_summary_df["grid_region"], regional_summary_df["capacity_share_pct"]))
    }


def analyze_curtailment_and_firmness() -> Dict[str, Any]:
    """
    Analyzes mechanism-specific reliability regimes across contracts and capacity:
      1. firm_service
      2. mandatory_grid_emergency_curtailment
      3. voluntary_price_response
      4. interconnection_not_energized
      5. interruptible_tariff
    """
    pwr_rels = pd.read_parquet(PROCESSED_DIR / "power_relationships.parquet")
    pwr_facts = pd.read_parquet(PROCESSED_DIR / "power_facts.parquet")
    fac_df = pd.read_parquet(PROCESSED_DIR / "facilities.parquet")

    # Contract count and capacity basis by reliability regime
    regime_summary = pwr_rels.groupby("reliability_regime")["capacity_basis_mw"].agg(["count", "sum"]).reset_index()
    total_mw = regime_summary["sum"].sum()
    regime_summary["share_pct"] = (regime_summary["sum"] / total_mw) * 100.0

    # Disaggregate energized MW by regime
    en_facts = pwr_facts[pwr_facts["mw_type"] == "energized_mw"]
    en_with_rel = en_facts.merge(pwr_rels[["power_rel_id", "reliability_regime"]], on="power_rel_id", how="left")
    en_by_regime = en_with_rel.groupby("reliability_regime")["value_mw"].sum().to_dict()

    curtailment_details = []
    for _, r in pwr_rels.merge(fac_df[["facility_id", "facility_name", "operator_entity_id"]], on="facility_id").iterrows():
        curtailment_details.append({
            "power_rel_id": r["power_rel_id"],
            "facility_name": r["facility_name"],
            "operator": r["operator_entity_id"],
            "utility": r["utility_entity_id"],
            "grid_operator": r["grid_operator_entity_id"],
            "reliability_regime": r["reliability_regime"],
            "capacity_basis_mw": r["capacity_basis_mw"],
            "curtailment_rights": r["curtailment_rights"],
            "tariff_structure": r["tariff_structure"]
        })

    return {
        "regime_contract_counts": dict(zip(regime_summary["reliability_regime"], regime_summary["count"])),
        "regime_capacity_basis_mw": dict(zip(regime_summary["reliability_regime"], regime_summary["sum"])),
        "regime_shares_pct": dict(zip(regime_summary["reliability_regime"], [round(s, 2) for s in regime_summary["share_pct"]])),
        "regime_energized_mw": en_by_regime,
        "curtailment_details": curtailment_details
    }


def generate_figures(data: Dict[str, Any], mw_analysis: Dict[str, Any], curtailment_analysis: Dict[str, Any]):
    """
    Generates publication-quality figures:
      1. power_joint_network_topology.png (literal multi-layer topology)
      2. regional_grid_mw_distribution.png (non-overlapping capacity basis & energized MW)
      3. power_curtailment_structure.png (mechanism-specific reliability regimes)
    """
    U_joint = data["U_joint_active"]
    ent_df = data["ent_df"]
    M_joint = data["M_joint_active"]

    # -------------------------------------------------------------
    # Figure 1: Literal Multi-Layer Topology
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    pos = nx.spring_layout(U_joint, k=0.42, seed=42, iterations=120)

    category_colors = {
        "neocloud_operator": "#E63946",       # Coral Red (CoreWeave)
        "datacenter_developer": "#457B9D",   # Slate Blue (APLD, CORZ, WULF, HUT, IREN)
        "hyperscaler_anchor": "#2A9D8F",     # Teal (MSFT, META)
        "hardware_supplier": "#1D3557",      # Navy (NVDA)
        "server_oem": "#F4A261",             # Ochre (SMCI)
        "private_credit_syndicate": "#6B705C",# Olive Grey
        "capital_provider": "#A5A58D",       # Muted Grey
        "electric_utility": "#E76F51",        # Terracotta (Utilities)
        "grid_operator_rto": "#9B5DE5",      # Purple (ERCOT, MISO, etc.)
        "physical_facility": "#E9C46A",      # Gold (Campuses / Facilities)
        "unknown": "#CCCCCC"
    }

    node_colors = []
    node_sizes = []
    for n in U_joint.nodes():
        if n.startswith("FAC-"):
            cat = "physical_facility"
            node_sizes.append(260)
        elif n in ent_df.index:
            cat = ent_df.loc[n, "category"]
            node_sizes.append(380 + U_joint.degree(n) * 100)
        else:
            cat = "unknown"
            node_sizes.append(200)
        node_colors.append(category_colors.get(cat, "#A8DADC"))

    # Edge classification
    fin_edges = []
    fac_edges = []
    pwr_edges = []
    for u, v, data_dict in M_joint.edges(data=True):
        layer = data_dict.get("edge_layer")
        if layer == "financial":
            fin_edges.append((u, v))
        elif layer == "facility_assignment":
            fac_edges.append((u, v))
        elif layer == "physical_power":
            pwr_edges.append((u, v))

    nx.draw_networkx_edges(U_joint, pos, edgelist=fin_edges, edge_color="#4A5568", alpha=0.6, width=1.5, ax=ax, style="solid")
    nx.draw_networkx_edges(U_joint, pos, edgelist=fac_edges, edge_color="#457B9D", alpha=0.7, width=1.8, ax=ax, style="dotted")
    nx.draw_networkx_edges(U_joint, pos, edgelist=pwr_edges, edge_color="#9B5DE5", alpha=0.85, width=2.2, ax=ax, style="dashed")
    nx.draw_networkx_nodes(U_joint, pos, node_color=node_colors, node_size=node_sizes, alpha=0.9, edgecolors="#1A202C", linewidths=1.2, ax=ax)

    # Clean node labels (short names for readability)
    labels = {}
    for n in U_joint.nodes():
        if n.startswith("FAC-"):
            labels[n] = n.replace("FAC-", "")
        else:
            labels[n] = n
    nx.draw_networkx_labels(U_joint, pos, labels=labels, font_size=7, font_weight="bold", font_family="sans-serif", ax=ax)

    # Legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', label='Neocloud (CoreWeave)', markerfacecolor='#E63946', markersize=9),
        plt.Line2D([0], [0], marker='o', color='w', label='Data Center Operator', markerfacecolor='#457B9D', markersize=9),
        plt.Line2D([0], [0], marker='s', color='w', label='Physical Facility (Campus)', markerfacecolor='#E9C46A', markersize=9),
        plt.Line2D([0], [0], marker='o', color='w', label='Electric Utility Provider', markerfacecolor='#E76F51', markersize=9),
        plt.Line2D([0], [0], marker='o', color='w', label='Grid Operator / RTO', markerfacecolor='#9B5DE5', markersize=9),
        plt.Line2D([0], [0], marker='o', color='w', label='Hyperscaler / Anchor Offtaker', markerfacecolor='#2A9D8F', markersize=9),
        plt.Line2D([0], [0], marker='o', color='w', label='Credit Syndicate / Bank', markerfacecolor='#6B705C', markersize=9),
        plt.Line2D([0], [0], color='#4A5568', lw=2, label='Financial Obligation Edge'),
        plt.Line2D([0], [0], color='#457B9D', lw=2, linestyle=':', label='Operator -> Facility Edge'),
        plt.Line2D([0], [0], color='#9B5DE5', lw=2, linestyle='--', label='Facility -> Utility -> Grid Edge'),
    ]
    ax.legend(handles=legend_elements, loc="upper right", frameon=True, fontsize=8, title="Literal Network Layers")
    ax.set_title("AI Infrastructure Joint Corporate-Physical Network (ADR-020.1 Hardened)\nLiteral Multi-Layer Architecture: Corporate Operator -> Facility -> Utility -> Transmission Grid", fontsize=12, fontweight="bold", pad=15)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "power_joint_network_topology.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Figure 2: Regional Grid MW Distribution (Non-Overlapping Basis)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    reg_df = pd.DataFrame(mw_analysis["regional_breakdown"]).set_index("grid_region")

    x = np.arange(len(reg_df.index))
    width = 0.28

    ax.bar(x - width, reg_df["capacity_basis_mw"], width, label="Contracted Service Basis (MW)", color="#264653", alpha=0.9, edgecolor="black", linewidth=0.5)
    ax.bar(x, reg_df["energized_mw"], width, label="Energized Operating (MW)", color="#2A9D8F", alpha=0.9, edgecolor="black", linewidth=0.5)
    ax.bar(x + width, reg_df["planned_mw"], width, label="Planned Expansion Envelope (MW)", color="#E9C46A", alpha=0.9, edgecolor="black", linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(reg_df.index, fontsize=10, fontweight="bold")
    ax.set_ylabel("Power Capacity (Megawatts - MW)", fontsize=10, fontweight="bold")
    ax.set_title(f"Regional Grid Power Footprint by Non-Overlapping Capacity Basis (ADR-020.1)\nGrid Exposure Concentration Index (HHI-form): {mw_analysis['hhi_capacity_basis']} (Basis), {mw_analysis['hhi_energized']} (Energized)", fontsize=11, fontweight="bold", pad=12)
    ax.legend(loc="upper right", frameon=True, fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "regional_grid_mw_distribution.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Figure 3: Mechanism-Specific Reliability Regimes
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6), dpi=300)

    reg_counts = curtailment_analysis["regime_contract_counts"]
    reg_mw = curtailment_analysis["regime_capacity_basis_mw"]

    regime_labels = {
        "interconnection_not_energized": "Unenergized Development",
        "firm_service": "Firm Service Tariff",
        "voluntary_price_response": "Voluntary Price Response",
        "mandatory_grid_emergency_curtailment": "Mandatory Emergency Curtailment",
        "interruptible_tariff": "Interruptible Tariff"
    }

    colors = ["#457B9D", "#2A9D8F", "#F4A261", "#E76F51", "#CCCCCC"]

    # Panel 1: Contract Counts
    ax1.pie(
        reg_counts.values(),
        labels=[regime_labels.get(k, k) for k in reg_counts.keys()],
        autopct='%1.1f%%',
        colors=colors[:len(reg_counts)],
        startangle=140,
        wedgeprops={"edgecolor": "black", "linewidth": 1}
    )
    ax1.set_title("Power Contracts by Reliability Regime (Counts)", fontsize=10, fontweight="bold")

    # Panel 2: Capacity Basis MW
    ax2.pie(
        reg_mw.values(),
        labels=[regime_labels.get(k, k) for k in reg_mw.keys()],
        autopct='%1.1f%%',
        colors=colors[:len(reg_mw)],
        startangle=140,
        wedgeprops={"edgecolor": "black", "linewidth": 1}
    )
    ax2.set_title(f"Capacity Basis (MW) by Reliability Regime\nTotal Modeled: {sum(reg_mw.values()):,.0f} MW", fontsize=10, fontweight="bold")

    plt.suptitle("AI Infrastructure Mechanism-Specific Reliability Architecture (ADR-020.1)", fontsize=12, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "power_curtailment_structure.png", dpi=300)
    plt.close()


def run_power_analysis_sprint():
    print("=== Executing Phase 1 Power Backplane Analysis Sprint (ADR-020.1 Hardened) ===")
    net_data = build_joint_network("2026-09-28")

    # 1. Topological join
    topo_res = analyze_topological_join(net_data)
    print("\n--- 1. Literal Topological Join Summary ---")
    print(f"Financial Baseline: {topo_res['financial_baseline']['node_count']} nodes, {topo_res['financial_baseline']['component_count']} components (Largest: {topo_res['financial_baseline']['largest_component_size']} nodes)")
    print(f"Joint Network:      {topo_res['joint_network']['node_count']} nodes, {topo_res['joint_network']['component_count']} components (Largest: {topo_res['joint_network']['largest_component_size']} nodes)")
    print(f"Joint Articulation Points ({len(topo_res['joint_network']['articulation_points'])}): {topo_res['joint_network']['articulation_points']}")

    # 2. Excision scenarios
    excision_res = analyze_excision_scenarios(net_data)
    print("\n--- 2. CoreWeave & Key Node Excision Analysis ---")
    crwv_exc = [r for r in excision_res if r["target_node"] == "CRWV"][0]
    ercot_exc = [r for r in excision_res if r["target_node"] == "ERCOT"][0]
    print(f"CRWV Excision on Financial Baseline: {crwv_exc['financial_baseline_impact']['component_count']} components, {crwv_exc['financial_baseline_impact']['isolated_count']} isolated nodes")
    print(f"CRWV Excision on Joint Network:        {crwv_exc['joint_network_impact']['component_count']} components, {crwv_exc['joint_network_impact']['isolated_count']} isolated nodes")
    print(f"Surviving Joint Components without CRWV: {[len(c) for c in crwv_exc['joint_network_impact']['components']]}")
    print(f"ERCOT Excision on Joint Network:       {ercot_exc['joint_network_impact']['component_count']} components (isolates Texas participants into separate component of size {len(ercot_exc['joint_network_impact']['components'][1])})")

    # 3. Regional Grid and Typed MW
    mw_res = analyze_regional_grid_and_mw()
    print("\n--- 3. Regional Grid & Typed MW Analysis (Non-Overlapping Basis) ---")
    print(f"Total Modeled Capacity Basis: {mw_res['total_capacity_basis_mw']:,.1f} MW")
    print(f"Total Energized Capacity:     {mw_res['total_energized_mw']:,.1f} MW")
    print(f"Total Planned Expansion:      {mw_res['total_planned_mw']:,.1f} MW")
    print(f"Grid Exposure Concentration Index (HHI-form): {mw_res['hhi_capacity_basis']} (Basis), {mw_res['hhi_energized']} (Energized)")
    print(f"Regional Capacity Shares:     {mw_res['regional_shares_pct']}")

    # 4. Curtailment and Firmness
    curt_res = analyze_curtailment_and_firmness()
    print("\n--- 4. Mechanism-Specific Reliability Regimes ---")
    print(f"Regime Contract Counts:     {curt_res['regime_contract_counts']}")
    print(f"Regime Capacity Basis (MW): {curt_res['regime_capacity_basis_mw']}")
    print(f"Regime Energized (MW):      {curt_res['regime_energized_mw']}")

    # 5. Generate Figures
    generate_figures(net_data, mw_res, curt_res)
    print("\n[OK] High-resolution publication figures generated in outputs/figures/")

    # 6. Save comprehensive summary JSON
    summary = {
        "analysis_id": "PHASE1-POWER-SPRINT-020.1",
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
