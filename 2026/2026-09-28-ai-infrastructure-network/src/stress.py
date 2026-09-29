"""
Stress and Contagion Propagation Engine for AI Infrastructure Financial Network
Simulates macro and operational shocks, traces multi-order contagion paths through
the obligation graph, and identifies the single change that breaks the largest number of edges.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import pandas as pd
import networkx as nx

from .graph import ObligationNetwork

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


class StressEngine:
    def __init__(self, network: Optional[ObligationNetwork] = None):
        self.network = network or ObligationNetwork()
        self.graph = self.network.graph

    def simulate_shock(self, scenario_id: str, primary_assumptions: List[str], severity: str, description: str) -> Dict[str, Any]:
        """
        Trace 1st-order and 2nd-order contagion through the obligation graph.
        
        1st Order: Edges whose performance explicitly depends on the perturbed assumption(s).
        1st Order Entities: Nodes that suffer cash flow reductions, debt service stress, or collateral deficits.
        2nd Order: Outgoing obligations from 1st-order stressed entities that become impaired due to liquidity contagion.
        """
        order_1_edges = []
        order_1_value = 0.0
        order_1_debtors = set()
        order_1_creditors = set()

        # Step 1: Find 1st-order edges directly relying on perturbed assumptions
        for u, v, d in self.graph.edges(data=True):
            assumptions = d.get("shared_assumptions", [])
            intersect = set(primary_assumptions).intersection(set(assumptions))
            if intersect:
                order_1_edges.append({
                    "obligation_id": d.get("obligation_id"),
                    "from_entity": u,
                    "to_entity": v,
                    "type": d.get("obligation_type"),
                    "amount_usd": d.get("amount", 0.0),
                    "recourse": d.get("recourse"),
                    "triggering_assumptions": list(intersect)
                })
                order_1_value += d.get("amount", 0.0)
                order_1_debtors.add(u)
                order_1_creditors.add(v)

        # Step 2: Map 1st-order stressed entities (debtors facing payment burdens or creditors facing cash flow holes)
        order_1_stressed_entities = order_1_debtors.union(order_1_creditors)

        # Step 3: Find 2nd-order edges: outgoing obligations originating from stressed entities
        order_2_edges = []
        order_2_value = 0.0
        seen_obl_ids = set(e["obligation_id"] for e in order_1_edges)

        for u in order_1_stressed_entities:
            # Check SPV aliases too
            search_nodes = [u]
            if u == "CRWV":
                search_nodes.append("CRWV_SPV_VIII")
            elif u == "APLD":
                search_nodes.append("APLD_ELN_LLC")

            for node in search_nodes:
                for _, to_node, d in self.graph.out_edges(node, data=True):
                    obl_id = d.get("obligation_id")
                    if obl_id not in seen_obl_ids:
                        order_2_edges.append({
                            "obligation_id": obl_id,
                            "from_entity": node,
                            "to_entity": to_node,
                            "type": d.get("obligation_type"),
                            "amount_usd": d.get("amount", 0.0),
                            "recourse": d.get("recourse"),
                            "impaired_by": u
                        })
                        order_2_value += d.get("amount", 0.0)
                        seen_obl_ids.add(obl_id)

        total_network_value = sum(d.get("amount", 0.0) for _, _, d in self.graph.edges(data=True))
        total_stressed_value = order_1_value + order_2_value
        total_edges_stressed = len(order_1_edges) + len(order_2_edges)
        total_edges = self.graph.number_of_edges()

        return {
            "scenario_id": scenario_id,
            "description": description,
            "severity": severity,
            "primary_assumptions": primary_assumptions,
            "order_1_edges_count": len(order_1_edges),
            "order_1_value_usd": order_1_value,
            "order_1_edges": order_1_edges,
            "order_1_stressed_entities": sorted(list(order_1_stressed_entities)),
            "order_2_edges_count": len(order_2_edges),
            "order_2_value_usd": order_2_value,
            "order_2_edges": order_2_edges,
            "total_edges_stressed": total_edges_stressed,
            "total_edges_in_network": total_edges,
            "edge_stress_percentage": round((total_edges_stressed / total_edges) * 100, 1) if total_edges else 0,
            "total_stressed_value_usd": total_stressed_value,
            "total_network_value_usd": total_network_value,
            "value_stress_percentage": round((total_stressed_value / total_network_value) * 100, 1) if total_network_value else 0
        }

    def run_standard_scenarios(self) -> pd.DataFrame:
        """Run standard suite of systemic shock scenarios and produce comparative evaluation."""
        scenarios = [
            {
                "scenario_id": "SCEN_01_GPU_RESIDUAL_CRASH",
                "assumptions": ["A001"],
                "severity": "-40% secondary market resale value",
                "description": "Secondary market clearing prices for H100/H200 fleets fall 40%, triggering margin calls on asset-backed debt facilities."
            },
            {
                "scenario_id": "SCEN_02_REFINANCING_SPIKE",
                "assumptions": ["A002"],
                "severity": "+300 bps borrowing spread spike",
                "description": "Private credit syndicated debt markets tighten; borrowing rates rise 300 bps, reducing debt service coverage below 1.0x."
            },
            {
                "scenario_id": "SCEN_03_HYPERSCALER_CAPEX_TRIM",
                "assumptions": ["A006"],
                "severity": "-20% hyperscaler capex growth reduction",
                "description": "Top cloud hyperscalers decelerate infrastructure capex expansion, curbing third-party off-take and GPU hardware orders."
            },
            {
                "scenario_id": "SCEN_04_ANCHOR_CUSTOMER_RETRENCH",
                "assumptions": ["A005"],
                "severity": "-30% anchor customer volume reduction",
                "description": "Anchor customer (Microsoft) reduces compute off-take or transitions workloads to internal custom silicon (Maia)."
            },
            {
                "scenario_id": "SCEN_05_POWER_ENERGIZATION_DELAY",
                "assumptions": ["A004"],
                "severity": "12-month substation interconnect delay",
                "description": "MISO substation delivery at Polaris Forge 1 is delayed 12 months, halting lease revenue commencement while carrying costs run."
            },
            {
                "scenario_id": "SCEN_06_UTILIZATION_CONTRACTION",
                "assumptions": ["A003"],
                "severity": "-15% spot cluster utilization drop",
                "description": "Uncontracted GPU capacity spot utilization drops from 85% to 60%, eliminating operator operating cash flow buffer."
            }
        ]

        results = []
        for s in scenarios:
            res = self.simulate_shock(
                scenario_id=s["scenario_id"],
                primary_assumptions=s["assumptions"],
                severity=s["severity"],
                description=s["description"]
            )
            results.append({
                "scenario_id": s["scenario_id"],
                "perturbed_assumptions": ", ".join(s["assumptions"]),
                "severity": s["severity"],
                "order_1_edges": res["order_1_edges_count"],
                "order_1_value_usd": res["order_1_value_usd"],
                "order_2_edges": res["order_2_edges_count"],
                "order_2_value_usd": res["order_2_value_usd"],
                "total_stressed_edges": res["total_edges_stressed"],
                "edge_stress_pct": res["edge_stress_percentage"],
                "total_stressed_value_usd": res["total_stressed_value_usd"],
                "value_stress_pct": res["value_stress_percentage"],
                "description": s["description"]
            })

        df = pd.DataFrame(results).sort_values(by="total_stressed_value_usd", ascending=False)
        return df


if __name__ == "__main__":
    engine = StressEngine()
    summary = engine.run_standard_scenarios()
    print("=== Systemic Stress Scenarios Ranked by Total Stressed Value ===")
    print(summary[["scenario_id", "total_stressed_edges", "edge_stress_pct", "total_stressed_value_usd", "value_stress_pct"]])
