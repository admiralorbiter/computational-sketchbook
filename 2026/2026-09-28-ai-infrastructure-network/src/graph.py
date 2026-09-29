"""
Obligation Network Graph Construction and Analysis Library
Constructs directed contractual graphs, computes network exposure matrices,
unwraps SPV perimeters, and maps shared systemic assumption dependencies.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

import networkx as nx
import pandas as pd

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


class ObligationNetwork:
    def __init__(self, entities_df: Optional[pd.DataFrame] = None, obligations_df: Optional[pd.DataFrame] = None):
        if entities_df is None:
            entities_df = pd.read_parquet(PROCESSED_DIR / "entities.parquet")
        if obligations_df is None:
            obligations_df = pd.read_parquet(PROCESSED_DIR / "obligations.parquet")

        self.entities_df = entities_df.set_index("entity_id")
        self.obligations_df = obligations_df
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        """Populate NetworkX graph with entities and contractual edges."""
        # Add nodes with metadata
        for eid, row in self.entities_df.iterrows():
            self.graph.add_node(
                eid,
                name=row.get("name", eid),
                ticker=row.get("ticker"),
                category=row.get("category"),
                status=row.get("status"),
                description=row.get("description")
            )

        # Add edges
        for _, row in self.obligations_df.iterrows():
            u = row["from_entity"]
            v = row["to_entity"]
            obl_id = row["obligation_id"]
            assumptions = [a.strip() for a in str(row["shared_assumptions"]).split(",") if a.strip()]

            # Add node if not already present
            if not self.graph.has_node(u):
                self.graph.add_node(u, name=u, category="external_node")
            if not self.graph.has_node(v):
                self.graph.add_node(v, name=v, category="external_node")

            self.graph.add_edge(
                u,
                v,
                key=obl_id,
                obligation_id=obl_id,
                obligation_type=row["obligation_type"],
                amount=float(row["amount"]),
                term_years=row["term_years"],
                recourse=row["recourse"],
                collateral=row["collateral"],
                guarantee=row["guarantee"],
                evidence_class=row["evidence_class"],
                confidence=float(row["confidence"]),
                shared_assumptions=assumptions
            )

    def compute_exposure_summary(self) -> pd.DataFrame:
        """Compute outgoing obligations, incoming claims, and net contractual exposure."""
        summary = []
        for node in self.graph.nodes():
            out_edges = self.graph.out_edges(node, data=True)
            in_edges = self.graph.in_edges(node, data=True)

            out_amount = sum(d.get("amount", 0.0) for _, _, d in out_edges)
            in_amount = sum(d.get("amount", 0.0) for _, _, d in in_edges)

            out_types = list(set(d.get("obligation_type") for _, _, d in out_edges))
            in_types = list(set(d.get("obligation_type") for _, _, d in in_edges))

            category = self.graph.nodes[node].get("category", "unknown")
            ticker = self.graph.nodes[node].get("ticker")

            summary.append({
                "entity_id": node,
                "ticker": ticker,
                "category": category,
                "outgoing_obligations_usd": out_amount,
                "incoming_claims_usd": in_amount,
                "net_contractual_exposure_usd": out_amount - in_amount,
                "num_outgoing_contracts": len(out_edges),
                "num_incoming_contracts": len(in_edges),
                "outgoing_types": ", ".join(out_types),
                "incoming_types": ", ".join(in_types)
            })

        df = pd.DataFrame(summary).sort_values(by="outgoing_obligations_usd", ascending=False)
        return df

    def query_assumption_footprint(self, assumption_id: str) -> Dict[str, Any]:
        """Identify all edges, nodes, and contractual dollar volume relying on a specific assumption."""
        matching_edges = []
        total_exposed_usd = 0.0
        exposed_nodes = set()

        for u, v, d in self.graph.edges(data=True):
            assumptions = d.get("shared_assumptions", [])
            if assumption_id in assumptions:
                matching_edges.append({
                    "obligation_id": d.get("obligation_id"),
                    "from_entity": u,
                    "to_entity": v,
                    "type": d.get("obligation_type"),
                    "amount_usd": d.get("amount"),
                    "evidence_class": d.get("evidence_class")
                })
                total_exposed_usd += d.get("amount", 0.0)
                exposed_nodes.add(u)
                exposed_nodes.add(v)

        return {
            "assumption_id": assumption_id,
            "total_exposed_usd": total_exposed_usd,
            "num_edges": len(matching_edges),
            "num_entities": len(exposed_nodes),
            "entities": sorted(list(exposed_nodes)),
            "edges": matching_edges
        }

    def aggregate_all_assumptions(self) -> pd.DataFrame:
        """Rank all shared assumptions by total contractual value supported."""
        all_assumptions = set()
        for _, _, d in self.graph.edges(data=True):
            for a in d.get("shared_assumptions", []):
                if a:
                    all_assumptions.add(a)

        records = []
        for aid in sorted(list(all_assumptions)):
            res = self.query_assumption_footprint(aid)
            records.append({
                "assumption_id": aid,
                "total_contract_value_usd": res["total_exposed_usd"],
                "num_edges_supported": res["num_edges"],
                "num_entities_involved": res["num_entities"],
                "entities_involved": ", ".join(res["entities"])
            })

        df = pd.DataFrame(records).sort_values(by="total_contract_value_usd", ascending=False)
        return df

    def unwrap_spv_perimeter(self) -> nx.DiGraph:
        """Collapse SPVs into parent corporate entities to reveal true economic leverage."""
        collapsed = nx.DiGraph()
        spv_map = {
            "CRWV_SPV_VIII": "CRWV",
            "APLD_ELN_LLC": "APLD"
        }

        for u, v, d in self.graph.edges(data=True):
            true_u = spv_map.get(u, u)
            true_v = spv_map.get(v, v)

            if true_u == true_v:
                continue

            if collapsed.has_edge(true_u, true_v):
                collapsed[true_u][true_v]["amount"] += d.get("amount", 0.0)
                collapsed[true_u][true_v]["contract_count"] += 1
            else:
                collapsed.add_edge(
                    true_u,
                    true_v,
                    amount=d.get("amount", 0.0),
                    contract_count=1,
                    primary_type=d.get("obligation_type")
                )

        return collapsed


if __name__ == "__main__":
    net = ObligationNetwork()
    summary = net.compute_exposure_summary()
    print("=== Contractual Exposure Summary ===")
    print(summary[["entity_id", "outgoing_obligations_usd", "incoming_claims_usd", "net_contractual_exposure_usd"]])

    print("\n=== Systemic Assumptions Ranked by Value Supported ===")
    rank_df = net.aggregate_all_assumptions()
    print(rank_df[["assumption_id", "total_contract_value_usd", "num_edges_supported", "entities_involved"]])
