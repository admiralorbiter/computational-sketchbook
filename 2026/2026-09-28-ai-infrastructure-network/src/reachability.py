"""
Contractual Reachability and Assumption Dependency Footprint Engine (Phase 0.7 Hardening)
Measures the topological reachability of edges and entities within 1 and 2 hops of shared assumptions.
Eliminates unweighted cross-category dollar aggregation; reports reachability strictly broken down
by amount_type (principal debt %, purchase commitments %, lease value %, revenue %, contingent obligations)
alongside edge reachability percentages, with dynamic SPV traversal and zero NaN poisoning.

NOTE: This is an epistemic dependency footprint metric measuring network exposure, NOT a financial loss or impairment engine.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import pandas as pd
import networkx as nx

try:
    from .graph import ObligationNetwork
except ImportError:
    from graph import ObligationNetwork

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


class ContractualReachability:
    def __init__(self, network: Optional[ObligationNetwork] = None):
        self.network = network or ObligationNetwork()
        self.graph = self.network.graph
        self.network_by_amount_type = self._compute_network_totals_by_amount_type()

    def _compute_network_totals_by_amount_type(self) -> Dict[str, float]:
        """Compute aggregate baseline values per amount_type across the entire network."""
        totals = {}
        for _, _, _, d in self.graph.edges(data=True, keys=True):
            atype = d.get("amount_type", "unspecified")
            amt = d.get("amount")
            if amt is not None:
                totals[atype] = totals.get(atype, 0.0) + float(amt)
        return totals

    def analyze_assumption_footprint(self, scenario_id: str, assumptions: List[str], description: str) -> Dict[str, Any]:
        """
        Compute the 1st-order and 2nd-order topological reachability footprint of an assumption set.
        
        1st Order: Edges whose performance explicitly depends on the assumption(s).
        1st Order Nodes: Entities at either end of 1st-order edges.
        2nd Order: Outgoing contractual edges originating from 1st-order nodes (including SPV perimeters via corporate hierarchy).
        """
        order_1_edges = []
        order_1_nodes = set()
        seen_keys = set()

        for u, v, k, d in self.graph.edges(data=True, keys=True):
            edge_assumptions = d.get("shared_assumptions", [])
            intersect = set(assumptions).intersection(set(edge_assumptions))
            if intersect:
                amt = d.get("amount")
                atype = d.get("amount_type", "unspecified")
                order_1_edges.append({
                    "obligation_id": k,
                    "from_entity": u,
                    "to_entity": v,
                    "type": d.get("obligation_type"),
                    "amount_usd": amt,
                    "amount_type": atype,
                    "recourse": d.get("recourse"),
                    "matched_assumptions": list(intersect)
                })
                order_1_nodes.add(u)
                order_1_nodes.add(v)
                seen_keys.add(k)

        order_2_edges = []
        for u in order_1_nodes:
            # Dynamically identify all corporate nodes sharing the root parent hierarchy
            root_u = self.network.get_root_parent(u)
            search_nodes = [n for n in self.graph.nodes() if self.network.get_root_parent(n) == root_u]
            if u not in search_nodes:
                search_nodes.append(u)

            for node in search_nodes:
                if self.graph.has_node(node):
                    for _, to_node, k, d in self.graph.out_edges(node, data=True, keys=True):
                        if k not in seen_keys:
                            amt = d.get("amount")
                            atype = d.get("amount_type", "unspecified")
                            order_2_edges.append({
                                "obligation_id": k,
                                "from_entity": node,
                                "to_entity": to_node,
                                "type": d.get("obligation_type"),
                                "amount_usd": amt,
                                "amount_type": atype,
                                "recourse": d.get("recourse"),
                                "reachable_via": u
                            })
                            seen_keys.add(k)

        all_reachable_edges = order_1_edges + order_2_edges
        total_edges = self.graph.number_of_edges()
        total_reachable_edges = len(all_reachable_edges)

        # Reachability broken down strictly by amount_type (avoiding NaN addition)
        reachable_by_amount_type = {}
        for e in all_reachable_edges:
            atype = e.get("amount_type", "unspecified")
            amt = e.get("amount_usd")
            if amt is not None:
                reachable_by_amount_type[atype] = reachable_by_amount_type.get(atype, 0.0) + float(amt)

        reachability_pct_by_type = {}
        for atype, total_val in self.network_by_amount_type.items():
            reach_val = reachable_by_amount_type.get(atype, 0.0)
            reachability_pct_by_type[atype] = round((reach_val / total_val) * 100.0, 1) if total_val > 0 else 0.0

        all_reachable_nodes = set(order_1_nodes)
        for e in order_2_edges:
            all_reachable_nodes.add(e["from_entity"])
            all_reachable_nodes.add(e["to_entity"])

        return {
            "scenario_id": scenario_id,
            "description": description,
            "assumptions": assumptions,
            "order_1_edges_count": len(order_1_edges),
            "order_1_nodes": sorted(list(order_1_nodes)),
            "order_2_edges_count": len(order_2_edges),
            "total_reachable_edges": total_reachable_edges,
            "total_network_edges": total_edges,
            "edge_reachability_pct": round((total_reachable_edges / total_edges) * 100, 1) if total_edges else 0,
            "reachable_by_amount_type_usd": reachable_by_amount_type,
            "reachability_pct_by_type": reachability_pct_by_type,
            "all_reachable_nodes": sorted(list(all_reachable_nodes)),
            "order_1_edges": order_1_edges,
            "order_2_edges": order_2_edges
        }

    def run_standard_footprints(self) -> pd.DataFrame:
        """Run reachability analysis across standard assumption clusters."""
        scenarios = [
            {
                "scenario_id": "REACH_A006_CAPEX_EXPANSION",
                "assumptions": ["A006"],
                "description": "Footprint of contracts dependent upon compounding hyperscaler capex growth."
            },
            {
                "scenario_id": "REACH_A001_GPU_RESIDUAL_VALUE",
                "assumptions": ["A001"],
                "description": "Footprint of contracts dependent upon secondary market GPU collateral values."
            },
            {
                "scenario_id": "REACH_A005_ANCHOR_CUSTOMER",
                "assumptions": ["A005"],
                "description": "Footprint of contracts dependent upon anchor customer (Microsoft) demand."
            },
            {
                "scenario_id": "REACH_A002_REFINANCING",
                "assumptions": ["A002"],
                "description": "Footprint of contracts dependent upon credit refinancing availability."
            },
            {
                "scenario_id": "REACH_A004_POWER_DELIVERY",
                "assumptions": ["A004"],
                "description": "Footprint of contracts dependent upon on-time grid substation energization."
            },
            {
                "scenario_id": "REACH_A003_UTILIZATION",
                "assumptions": ["A003"],
                "description": "Footprint of contracts dependent upon continuous high billable cluster utilization."
            }
        ]

        results = []
        for s in scenarios:
            res = self.analyze_assumption_footprint(
                scenario_id=s["scenario_id"],
                assumptions=s["assumptions"],
                description=s["description"]
            )
            pcts = res["reachability_pct_by_type"]
            results.append({
                "scenario_id": s["scenario_id"],
                "assumptions": ", ".join(s["assumptions"]),
                "reachable_edges": res["total_reachable_edges"],
                "total_edges": res["total_network_edges"],
                "edge_reach_pct": res["edge_reachability_pct"],
                "order_1_edges": res["order_1_edges_count"],
                "order_2_edges": res["order_2_edges_count"],
                "debt_principal_reach_pct": pcts.get("principal_outstanding", 0.0),
                "purchase_commit_reach_pct": pcts.get("remaining_commitment", 0.0),
                "lease_value_reach_pct": pcts.get("lifetime_contract_value", 0.0),
                "revenue_reach_pct": pcts.get("recognized_revenue", 0.0),
                "guarantee_reach_pct": pcts.get("contingent_obligations", pcts.get("contingent_guarantee", 0.0)),
                "reachable_entities_count": len(res["all_reachable_nodes"]),
                "description": s["description"]
            })

        df = pd.DataFrame(results).sort_values(by="edge_reach_pct", ascending=False)
        return df


if __name__ == "__main__":
    reach = ContractualReachability()
    df = reach.run_standard_footprints()
    print("=== Contractual Reachability & Assumption Footprints (By Amount Type) ===")
    print(df[["scenario_id", "reachable_edges", "edge_reach_pct", "debt_principal_reach_pct", "purchase_commit_reach_pct", "lease_value_reach_pct"]])
