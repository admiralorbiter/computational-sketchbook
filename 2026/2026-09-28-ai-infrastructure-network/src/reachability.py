"""
Contractual Reachability and Assumption Dependency Footprint Engine
Measures the topological reachability of edges and entities within 1 and 2 hops of shared assumptions.
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

    def analyze_assumption_footprint(self, scenario_id: str, assumptions: List[str], description: str) -> Dict[str, Any]:
        """
        Compute the 1st-order and 2nd-order topological reachability footprint of an assumption set.
        
        1st Order: Edges whose performance explicitly depends on the assumption(s).
        1st Order Nodes: Entities at either end of 1st-order edges.
        2nd Order: Outgoing contractual edges originating from 1st-order nodes.
        """
        order_1_edges = []
        order_1_value = 0.0
        order_1_nodes = set()
        seen_keys = set()

        for u, v, k, d in self.graph.edges(data=True, keys=True):
            edge_assumptions = d.get("shared_assumptions", [])
            intersect = set(assumptions).intersection(set(edge_assumptions))
            if intersect:
                amt = d.get("amount", 0.0)
                order_1_edges.append({
                    "obligation_id": k,
                    "from_entity": u,
                    "to_entity": v,
                    "type": d.get("obligation_type"),
                    "amount_usd": amt,
                    "amount_type": d.get("amount_type"),
                    "recourse": d.get("recourse"),
                    "matched_assumptions": list(intersect)
                })
                order_1_value += amt
                order_1_nodes.add(u)
                order_1_nodes.add(v)
                seen_keys.add(k)

        order_2_edges = []
        order_2_value = 0.0
        for u in order_1_nodes:
            search_nodes = [u]
            if u == "CRWV":
                search_nodes.append("CRWV_SPV_VIII")
            elif u == "APLD":
                search_nodes.append("APLD_ELN_LLC")

            for node in search_nodes:
                if self.graph.has_node(node):
                    for _, to_node, k, d in self.graph.out_edges(node, data=True, keys=True):
                        if k not in seen_keys:
                            amt = d.get("amount", 0.0)
                            order_2_edges.append({
                                "obligation_id": k,
                                "from_entity": node,
                                "to_entity": to_node,
                                "type": d.get("obligation_type"),
                                "amount_usd": amt,
                                "amount_type": d.get("amount_type"),
                                "recourse": d.get("recourse"),
                                "reachable_via": u
                            })
                            order_2_value += amt
                            seen_keys.add(k)

        total_network_value = sum(d.get("amount", 0.0) for _, _, _, d in self.graph.edges(data=True, keys=True))
        total_edges = self.graph.number_of_edges()
        total_reachable_value = order_1_value + order_2_value
        total_reachable_edges = len(order_1_edges) + len(order_2_edges)

        return {
            "scenario_id": scenario_id,
            "description": description,
            "assumptions": assumptions,
            "order_1_edges_count": len(order_1_edges),
            "order_1_value_usd": order_1_value,
            "order_1_nodes": sorted(list(order_1_nodes)),
            "order_2_edges_count": len(order_2_edges),
            "order_2_value_usd": order_2_value,
            "total_reachable_edges": total_reachable_edges,
            "total_network_edges": total_edges,
            "edge_reachability_pct": round((total_reachable_edges / total_edges) * 100, 1) if total_edges else 0,
            "total_reachable_value_usd": total_reachable_value,
            "total_network_value_usd": total_network_value,
            "value_reachability_pct": round((total_reachable_value / total_network_value) * 100, 1) if total_network_value else 0
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
            results.append({
                "scenario_id": s["scenario_id"],
                "assumptions": ", ".join(s["assumptions"]),
                "order_1_edges": res["order_1_edges_count"],
                "order_1_value_usd": res["order_1_value_usd"],
                "order_2_edges": res["order_2_edges_count"],
                "order_2_value_usd": res["order_2_value_usd"],
                "total_reachable_edges": res["total_reachable_edges"],
                "edge_reachability_pct": res["edge_reachability_pct"],
                "total_reachable_value_usd": res["total_reachable_value_usd"],
                "value_reachability_pct": res["value_reachability_pct"],
                "description": s["description"]
            })

        df = pd.DataFrame(results).sort_values(by="total_reachable_value_usd", ascending=False)
        return df


if __name__ == "__main__":
    reach = ContractualReachability()
    df = reach.run_standard_footprints()
    print("=== Contractual Reachability & Assumption Footprints ===")
    print(df[["scenario_id", "total_reachable_edges", "edge_reachability_pct", "total_reachable_value_usd", "value_reachability_pct"]])
