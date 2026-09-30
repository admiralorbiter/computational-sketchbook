"""
Phase 1 Analysis Sprint: Rigorous Structural, Epistemic, and Falsification Analysis
Answers the 6 core research questions on the frozen 2285391 dataset:
1. Articulation points & node/edge removal fragmentation.
2. Shared assumption density vs breadth (edges vs root entities vs counterparty pairs).
3. Concrete transmission chains (MSFT->CRWV->APLD/CORZ, META->NBIS->MUFG, IREN->OBDC/PIMCO).
4. Temporal network evolution (2024 -> 2025 -> 2026).
5. Missing edge sensitivity analysis.
6. Falsification exercise: topological dissection of the graph without CoreWeave.
"""

from pathlib import Path
import json
import networkx as nx
import pandas as pd
import numpy as np

try:
    from .graph import ObligationNetwork
except ImportError:
    from graph import ObligationNetwork

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs" / "analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_analysis_sprint():
    net = ObligationNetwork()
    as_of_date = "2026-09-28"
    net_active = net.economic_as_of(as_of_date)
    G_legal = net_active.graph
    G_cons = net_active.unwrap_spv_perimeter()

    print(f"=== Active Network State as of {as_of_date} ===")
    print(f"Legal Graph: {G_legal.number_of_nodes()} nodes, {G_legal.number_of_edges()} edges")
    print(f"Consolidated Graph: {G_cons.number_of_nodes()} root nodes, {G_cons.number_of_edges()} edges")

    # -------------------------------------------------------------
    # 1. Articulation Points & Node/Edge Removal
    # -------------------------------------------------------------
    print("\n" + "="*60)
    print("1. ARTICULATION POINTS & GRAPH FRAGMENTATION")
    print("="*60)

    # Undirected projections for connectivity analysis
    U_legal = G_legal.to_undirected()
    U_cons = G_cons.to_undirected()

    # Drop isolated nodes (nodes with degree 0) for component analysis
    U_legal_active = U_legal.subgraph([n for n in U_legal.nodes() if U_legal.degree(n) > 0]).copy()
    U_cons_active = U_cons.subgraph([n for n in U_cons.nodes() if U_cons.degree(n) > 0]).copy()

    comps_legal = list(nx.connected_components(U_legal_active))
    comps_cons = list(nx.connected_components(U_cons_active))

    print(f"Legal Graph Connected Components: {len(comps_legal)}")
    for i, c in enumerate(sorted(comps_legal, key=len, reverse=True), 1):
        print(f"  Component {i} ({len(c)} nodes): {sorted(list(c))}")

    print(f"\nConsolidated Graph Connected Components: {len(comps_cons)}")
    for i, c in enumerate(sorted(comps_cons, key=len, reverse=True), 1):
        print(f"  Component {i} ({len(c)} nodes): {sorted(list(c))}")

    art_legal = list(nx.articulation_points(U_legal_active))
    art_cons = list(nx.articulation_points(U_cons_active))
    print(f"\nArticulation Points (Legal): {art_legal}")
    print(f"Articulation Points (Consolidated): {art_cons}")

    bridges_cons = list(nx.bridges(U_cons_active))
    print(f"Bridges in Consolidated Graph: {len(bridges_cons)} bridges")
    for u, v in bridges_cons:
        print(f"  Bridge: {u} <---> {v}")

    # Node Removal Sensitivity Analysis
    candidate_removals = ["CRWV", "MUFG_BANK_SYN", "APLD", "BLUE_OWL_OBDC", "INSTITUTIONAL_BONDHOLDERS", "CORZ", "NBIS", "IREN", "WULF"]
    removal_results = []

    for node in candidate_removals:
        if node not in U_cons_active:
            continue
        U_sub = U_cons_active.copy()
        U_sub.remove_node(node)
        # remove degree 0
        active_sub = [n for n in U_sub.nodes() if U_sub.degree(n) > 0]
        sub_comps = list(nx.connected_components(U_sub.subgraph(active_sub)))
        comp_sizes = sorted([len(c) for c in sub_comps], reverse=True)
        max_size = comp_sizes[0] if comp_sizes else 0
        isolated_nodes = len(U_sub.nodes()) - len(active_sub)

        removal_results.append({
            "removed_node": node,
            "orig_components": len(comps_cons),
            "new_components": len(sub_comps),
            "max_component_size": max_size,
            "component_sizes": comp_sizes,
            "isolated_orphaned_nodes": isolated_nodes,
            "component_details": [sorted(list(c)) for c in sub_comps]
        })
        print(f"\nRemoval of {node}:")
        print(f"  Components: {len(comps_cons)} -> {len(sub_comps)}")
        print(f"  Component sizes: {comp_sizes}")
        print(f"  Isolated/Orphaned nodes: {isolated_nodes}")

    # -------------------------------------------------------------
    # 2. Shared Assumptions: Density vs Breadth
    # -------------------------------------------------------------
    print("\n" + "="*60)
    print("2. SHARED ASSUMPTIONS: DENSITY VS BREADTH")
    print("="*60)

    assump_df = pd.read_parquet(PROCESSED_DIR / "assumptions.parquet")
    assump_records = []

    for aid in assump_df["assumption_id"]:
        name = assump_df.loc[assump_df["assumption_id"] == aid, "name"].iloc[0]
        edges_with_a = []
        root_nodes_with_a = set()
        root_pairs_with_a = set()
        amount_by_type = {}
        total_dollars = 0.0

        for u, v, k, d in G_legal.edges(data=True, keys=True):
            assumps = d.get("shared_assumptions", [])
            if aid in assumps:
                edges_with_a.append(k)
                root_u = net_active.get_root_parent(u)
                root_v = net_active.get_root_parent(v)
                root_nodes_with_a.add(root_u)
                root_nodes_with_a.add(root_v)
                pair = tuple(sorted([root_u, root_v]))
                root_pairs_with_a.add(pair)

                amt = d.get("amount")
                atype = d.get("amount_type", "unspecified")
                if amt is not None:
                    amount_by_type[atype] = amount_by_type.get(atype, 0.0) + amt
                    total_dollars += amt

        density_edges_per_pair = len(edges_with_a) / len(root_pairs_with_a) if root_pairs_with_a else 0
        density_edges_per_node = len(edges_with_a) / len(root_nodes_with_a) if root_nodes_with_a else 0

        assump_records.append({
            "assumption_id": aid,
            "name": name,
            "edge_count": len(edges_with_a),
            "root_entity_count": len(root_nodes_with_a),
            "root_counterparty_pairs_count": len(root_pairs_with_a),
            "density_ratio_edges_to_pairs": round(density_edges_per_pair, 2),
            "density_ratio_edges_to_nodes": round(density_edges_per_node, 2),
            "total_quantified_usd": total_dollars,
            "amount_type_breakdown": amount_by_type,
            "root_entities": sorted(list(root_nodes_with_a)),
            "root_pairs": [f"{p[0]} <-> {p[1]}" for p in sorted(list(root_pairs_with_a))]
        })

    assump_analysis_df = pd.DataFrame(assump_records).sort_values(by="edge_count", ascending=False)
    for _, r in assump_analysis_df.iterrows():
        print(f"\n{r['assumption_id']}: {r['name']}")
        print(f"  Active Edges: {r['edge_count']} | Root Entities: {r['root_entity_count']} | Root Pairs: {r['root_counterparty_pairs_count']}")
        print(f"  Density (Edges / Root Pair): {r['density_ratio_edges_to_pairs']} | Density (Edges / Node): {r['density_ratio_edges_to_nodes']}")
        print(f"  Root Pairs: {', '.join(r['root_pairs'])}")
        print(f"  Dollar Breakdown: {r['amount_type_breakdown']}")

    # -------------------------------------------------------------
    # 3. Concrete Transmission Chains
    # -------------------------------------------------------------
    print("\n" + "="*60)
    print("3. CONCRETE TRANSMISSION CHAINS")
    print("="*60)

    # Chain 1: MSFT -> CRWV -> APLD / CORZ
    print("--- CHAIN 1: Hyperscaler Demand to Neocloud to Landlord/HPC Hosts ---")
    chain1_edges = [
        "REL-MSFT-CRWV-REVENUE-CONCENTRATION",
        "OBL-CRWV-APLD-LEASE",
        "OBL-CRWV-APLD-GUARANTY-ELN02",
        "OBL-CRWV-APLD-GUARANTY-ELN03",
        "OBL-CRWV-CORZ-COLOCATION-2024",
        "OBL-APLD-DEBT-PF1",
        "OBL-APLD-DEBT-PF2",
        "OBL-APLD-DEBT-CONV",
        "OBL-APLD-DEBT-7PCT-2026"
    ]
    for oid in chain1_edges:
        sub = net.obligations_df[net.obligations_df["obligation_id"] == oid].iloc[0]
        print(f"  [{oid}] {sub['from_entity']} -> {sub['to_entity']} | Type: {sub['obligation_type']} | Amount: ${sub['amount']/1e9:.3f}B ({sub['amount_type']}) | Known From: {sub['publicly_known_from']}")

    # Chain 2: META -> NBIS -> MUFG
    print("\n--- CHAIN 2: Foreign Private Issuer / Sovereign Cloud Pipeline ---")
    chain2_edges = [
        "OBL-NBIS-META-OFFTAKE-2026",
        "OBL-NBIS-DEBT-MUFG-2026"
    ]
    for oid in chain2_edges:
        sub = net.obligations_df[net.obligations_df["obligation_id"] == oid].iloc[0]
        amt_str = f"${sub['amount']/1e9:.3f}B" if pd.notna(sub['amount']) else "None"
        cap_str = f"Facility Cap: ${sub['facility_capacity']/1e9:.3f}B" if pd.notna(sub['facility_capacity']) else ""
        print(f"  [{oid}] {sub['from_entity']} -> {sub['to_entity']} | Type: {sub['obligation_type']} | Amount: {amt_str} {cap_str} | Known From: {sub['publicly_known_from']}")

    # Chain 3: IREN -> OBDC / PIMCO
    print("\n--- CHAIN 3: Direct GPU Equipment & Note Financing Pipeline ---")
    chain3_edges = [
        "OBL-IREN-DEBT-MFSA-2026",
        "OBL-IREN-DEBT-NOTES-2026",
        "OBL-IREN-GUARANTY-2026"
    ]
    for oid in chain3_edges:
        sub = net.obligations_df[net.obligations_df["obligation_id"] == oid].iloc[0]
        cap_str = f"Facility Cap: ${sub['facility_capacity']/1e9:.3f}B" if pd.notna(sub['facility_capacity']) else ""
        ref_str = f"Ref Proxy: ${sub['reference_exposure_estimate']/1e9:.3f}B" if pd.notna(sub['reference_exposure_estimate']) else ""
        print(f"  [{oid}] {sub['from_entity']} -> {sub['to_entity']} | Type: {sub['obligation_type']} | {cap_str} {ref_str} | Known From: {sub['publicly_known_from']}")

    # -------------------------------------------------------------
    # 4. Temporal Network Evolution (2024 -> 2025 -> 2026)
    # -------------------------------------------------------------
    print("\n" + "="*60)
    print("4. TEMPORAL NETWORK EVOLUTION (2024 -> 2025 -> 2026)")
    print("="*60)

    timeline_dates = [
        ("2024-01-01", "Early Neocloud (DDTL 1.0, Magnetar)"),
        ("2024-06-04", "CRWV / CORZ Initial 200 MW Colocation"),
        ("2024-06-25", "CORZ Option 1 Exercise (270 MW)"),
        ("2024-08-06", "CORZ Option 2 Exercise (382 MW)"),
        ("2024-10-23", "CORZ Option 3 Exercise (500 MW)"),
        ("2024-10-25", "WULF 2030 Convertible Notes ($500M)"),
        ("2024-12-31", "End of 2024 Baseline"),
        ("2025-02-27", "CORZ Option 4 / Denton Expansion (590 MW)"),
        ("2025-05-28", "APLD Polaris Forge 1 Lease ($11.0B, 400 MW)"),
        ("2025-08-20", "WULF 2031 Convertible Initial ($850M)"),
        ("2025-08-22", "WULF 2031 Greenshoe Exercise ($1.0B total)"),
        ("2025-09-29", "CRWV DDTL 2.1 Facility ($3.0B)"),
        ("2025-10-31", "WULF 2032 Convertible Notes ($1.025B)"),
        ("2025-12-31", "End of 2025 Baseline"),
        ("2026-03-30", "CRWV DDTL 4.0 MUFG Facility ($8.5B capacity)"),
        ("2026-04-21", "CRWV 9.75% Notes Add-on ($2.75B total)"),
        ("2026-05-11", "HUT 8 Coatue Note Extinction"),
        ("2026-06-16", "APLD Bridge Refinancing into 7% Notes ($1.59B)"),
        ("2026-06-18", "CRWV 2032 Senior Notes ($1.25B + €2.0B)"),
        ("2026-09-28", "Current Hardened Snapshot")
    ]

    temporal_records = []
    for dt, desc in timeline_dates:
        # Economic
        net_econ = net.economic_as_of(dt)
        g_econ = net_econ.graph
        cons_econ = net_econ.unwrap_spv_perimeter()
        u_cons_econ = cons_econ.to_undirected()
        active_nodes_econ = [n for n in u_cons_econ.nodes() if u_cons_econ.degree(n) > 0]
        n_comps_econ = len(list(nx.connected_components(u_cons_econ.subgraph(active_nodes_econ)))) if active_nodes_econ else 0

        # Known
        net_known = net.known_as_of(dt)
        g_known = net_known.graph
        cons_known = net_known.unwrap_spv_perimeter()
        u_cons_known = cons_known.to_undirected()
        active_nodes_known = [n for n in u_cons_known.nodes() if u_cons_known.degree(n) > 0]
        n_comps_known = len(list(nx.connected_components(u_cons_known.subgraph(active_nodes_known)))) if active_nodes_known else 0

        # Debt and Capacity
        debt_total_econ = sum(d.get("amount", 0.0) or 0.0 for _, _, _, d in g_econ.edges(data=True, keys=True) if d.get("amount_type") == "principal_outstanding")
        debt_total_known = sum(d.get("amount", 0.0) or 0.0 for _, _, _, d in g_known.edges(data=True, keys=True) if d.get("amount_type") == "principal_outstanding")

        corz_cap = net_econ.get_fact("OBL-CRWV-CORZ-COLOCATION-2024", "capacity_mw")

        temporal_records.append({
            "date": dt,
            "description": desc,
            "economic_edges": g_econ.number_of_edges(),
            "economic_root_nodes": len(active_nodes_econ),
            "economic_components": n_comps_econ,
            "economic_debt_usd": debt_total_econ,
            "known_edges": g_known.number_of_edges(),
            "known_root_nodes": len(active_nodes_known),
            "known_components": n_comps_known,
            "known_debt_usd": debt_total_known,
            "corz_mw": corz_cap
        })

    temporal_df = pd.DataFrame(temporal_records)
    print(temporal_df[["date", "description", "economic_edges", "known_edges", "economic_debt_usd", "known_debt_usd", "corz_mw"]].to_string())

    # -------------------------------------------------------------
    # 5. Missing Edge Sensitivity Analysis
    # -------------------------------------------------------------
    print("\n" + "="*60)
    print("5. MISSING EDGE SENSITIVITY ANALYSIS")
    print("="*60)

    # What edge, if added, would connect components or collapse articulation points?
    # Candidate hypothetical edges:
    # 1. META -> APLD (Hyperscaler contracts directly with Data Center Host)
    # 2. MSFT -> CORZ (Hyperscaler contracts directly with HPC Host)
    # 3. MUFG -> APLD (MUFG expands syndicated lending to APLD)
    # 4. BLACKSTONE -> NBIS (Blackstone expands debt to Nebius)
    # 5. Common Utility (e.g. AEP) -> APLD, CORZ, WULF
    # 6. Common Equipment (e.g. VRT) -> CRWV, APLD, NBIS

    hypo_edges = [
        ("META", "APLD", "Hyperscaler Offtake: META -> APLD"),
        ("MSFT", "CORZ", "Hyperscaler Offtake: MSFT -> CORZ"),
        ("MUFG_BANK_SYN", "APLD", "Common Lender: MUFG -> APLD"),
        ("BLACKSTONE_MAGNETAR_SYN", "NBIS", "Common Lender: Blackstone -> NBIS"),
        ("MUFG_BANK_SYN", "BLUE_OWL_OBDC", "Interbank / Co-lending: MUFG <-> OBDC"),
        ("AEP", "APLD", "Grid Node: AEP -> APLD & CORZ"),
    ]

    for u_hypo, v_hypo, desc in hypo_edges:
        G_hypo = U_cons_active.copy()
        if not G_hypo.has_node(u_hypo):
            G_hypo.add_node(u_hypo)
        if not G_hypo.has_node(v_hypo):
            G_hypo.add_node(v_hypo)
        G_hypo.add_edge(u_hypo, v_hypo)

        sub_nodes = [n for n in G_hypo.nodes() if G_hypo.degree(n) > 0]
        comps = list(nx.connected_components(G_hypo.subgraph(sub_nodes)))
        art_pts = list(nx.articulation_points(G_hypo.subgraph(sub_nodes)))
        crwv_is_art = "CRWV" in art_pts
        print(f"\nHypothetical Edge: {desc}")
        print(f"  Connected Components: {len(comps_cons)} -> {len(comps)}")
        print(f"  Largest Component Size: {max(len(c) for c in comps)}")
        print(f"  CRWV is Articulation Point: {crwv_is_art}")
        print(f"  Total Articulation Points: {len(art_pts)} ({art_pts})")

    # -------------------------------------------------------------
    # 6. Falsification Exercise: Network Without CoreWeave
    # -------------------------------------------------------------
    print("\n" + "="*60)
    print("6. FALSIFICATION EXERCISE: THE NETWORK WITHOUT COREWEAVE")
    print("="*60)

    # Excise CRWV from consolidated graph
    G_no_crwv = U_cons_active.copy()
    G_no_crwv.remove_node("CRWV")

    active_no_crwv = [n for n in G_no_crwv.nodes() if G_no_crwv.degree(n) > 0]
    isolated_no_crwv = [n for n in G_no_crwv.nodes() if G_no_crwv.degree(n) == 0]
    comps_no_crwv = list(nx.connected_components(G_no_crwv.subgraph(active_no_crwv)))

    print(f"Original Active Nodes: {len(U_cons_active.nodes())}")
    print(f"Nodes remaining after CRWV excision: {len(G_no_crwv.nodes())}")
    print(f"Active Connected Nodes: {len(active_no_crwv)}")
    print(f"Orphaned / Degree-0 Nodes: {len(isolated_no_crwv)}: {sorted(isolated_no_crwv)}")
    print(f"Connected Components Remaining: {len(comps_no_crwv)}")
    for i, c in enumerate(sorted(comps_no_crwv, key=len, reverse=True), 1):
        print(f"  Component {i} ({len(c)} nodes): {sorted(list(c))}")

    # Check edges in G_no_crwv
    legal_edges_no_crwv = [
        (u, v, k, d) for u, v, k, d in G_legal.edges(data=True, keys=True)
        if net_active.get_root_parent(u) != "CRWV" and net_active.get_root_parent(v) != "CRWV"
    ]
    print(f"\nLegal Edges Remaining Without CoreWeave: {len(legal_edges_no_crwv)} / {G_legal.number_of_edges()}")
    for u, v, k, d in legal_edges_no_crwv:
        print(f"  [{k}] {u} -> {v} (${d.get('amount') or 0.0:,.0f} {d.get('amount_type')})")

    # Check assumptions surviving without CoreWeave
    print("\nAssumptions Surviving Across Non-CoreWeave Edges:")
    assump_no_crwv = {}
    for u, v, k, d in legal_edges_no_crwv:
        for a in d.get("shared_assumptions", []):
            if a:
                root_u = net_active.get_root_parent(u)
                root_v = net_active.get_root_parent(v)
                if a not in assump_no_crwv:
                    assump_no_crwv[a] = {"edges": 0, "root_entities": set(), "root_pairs": set()}
                assump_no_crwv[a]["edges"] += 1
                assump_no_crwv[a]["root_entities"].add(root_u)
                assump_no_crwv[a]["root_entities"].add(root_v)
                assump_no_crwv[a]["root_pairs"].add(tuple(sorted([root_u, root_v])))

    for a, data in sorted(assump_no_crwv.items()):
        print(f"  {a}: {data['edges']} edges | {len(data['root_entities'])} root entities: {sorted(list(data['root_entities']))} | {len(data['root_pairs'])} pairs")

    # Save output artifacts
    out_payload = {
        "as_of_date": as_of_date,
        "articulation_points": art_cons,
        "bridges": bridges_cons,
        "node_removal_sensitivity": removal_results,
        "assumption_density_breadth": assump_records,
        "falsification_no_crwv": {
            "edges_remaining": len(legal_edges_no_crwv),
            "total_edges": G_legal.number_of_edges(),
            "components_count": len(comps_no_crwv),
            "components": [sorted(list(c)) for c in comps_no_crwv],
            "orphaned_nodes": sorted(isolated_no_crwv),
            "surviving_assumptions": {k: {"edges": v["edges"], "entities": sorted(list(v["root_entities"]))} for k, v in assump_no_crwv.items()}
        }
    }

    with open(OUTPUT_DIR / "phase1_analysis_sprint.json", "w") as f:
        json.dump(out_payload, f, indent=2)

    temporal_df.to_csv(OUTPUT_DIR / "temporal_network_evolution.csv", index=False)
    assump_analysis_df.to_csv(OUTPUT_DIR / "assumption_density_breadth.csv", index=False)
    print(f"\nSaved analysis results to {OUTPUT_DIR}/")


if __name__ == "__main__":
    run_analysis_sprint()
