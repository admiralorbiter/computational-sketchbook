"""
Obligation Network Multi-Graph Construction and Analysis Library (Phase 0.5 Refactor)
Constructs directed MultiDiGraphs preserving multiple distinct contracts per counterparty pair,
categorizes exposure by amount_type (avoiding false net netting), unwraps SPV perimeters,
and maps shared systemic assumption dependencies.
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
        # Use MultiDiGraph so distinct facilities/contracts between the same (u, v) pair are preserved
        self.graph = nx.MultiDiGraph()
        self._build_graph()

    def _build_graph(self):
        """Populate MultiDiGraph with entities as nodes and contracts as keyed edges."""
        for eid, row in self.entities_df.iterrows():
            self.graph.add_node(
                eid,
                name=row.get("name", eid),
                ticker=row.get("ticker"),
                category=row.get("category"),
                status=row.get("status"),
                description=row.get("description")
            )

        for _, row in self.obligations_df.iterrows():
            u = row["from_entity"]
            v = row["to_entity"]
            obl_id = row["obligation_id"]
            assumptions = [a.strip() for a in str(row.get("shared_assumptions", "")).split(",") if a.strip()]

            if not self.graph.has_node(u):
                self.graph.add_node(u, name=u, category="external_node")
            if not self.graph.has_node(v):
                self.graph.add_node(v, name=v, category="external_node")

            self.graph.add_edge(
                u,
                v,
                key=obl_id,
                obligation_id=obl_id,
                obligation_type=row.get("obligation_type"),
                amount=float(row.get("amount", 0.0)),
                amount_type=row.get("amount_type", "unspecified"),
                as_of_date=row.get("as_of_date"),
                currency=row.get("currency", "USD"),
                term_years=row.get("term_years"),
                effective_date=row.get("effective_date"),
                maturity_date=row.get("maturity_date"),
                recourse=row.get("recourse"),
                collateral=row.get("collateral"),
                guarantee=row.get("guarantee"),
                evidence_class=row.get("evidence_class"),
                confidence=float(row.get("confidence", 1.0)),
                claim_ids=str(row.get("claim_ids", "")).split(","),
                shared_assumptions=assumptions
            )

    def compute_exposure_by_amount_type(self) -> pd.DataFrame:
        """
        Compute outgoing and incoming exposure broken down strictly by amount_type.
        Eliminates the false 'net contractual exposure' metric.
        """
        records = []
        for node in self.graph.nodes():
            out_edges = self.graph.out_edges(node, data=True, keys=True)
            in_edges = self.graph.in_edges(node, data=True, keys=True)

            out_by_type = {}
            for _, _, k, d in out_edges:
                atype = d.get("amount_type", "unspecified")
                out_by_type[atype] = out_by_type.get(atype, 0.0) + d.get("amount", 0.0)

            in_by_type = {}
            for _, _, k, d in in_edges:
                atype = d.get("amount_type", "unspecified")
                in_by_type[atype] = in_by_type.get(atype, 0.0) + d.get("amount", 0.0)

            records.append({
                "entity_id": node,
                "ticker": self.graph.nodes[node].get("ticker"),
                "category": self.graph.nodes[node].get("category", "unknown"),
                "num_outgoing_contracts": len(out_edges),
                "num_incoming_contracts": len(in_edges),
                "outgoing_principal_debt_usd": out_by_type.get("principal_outstanding", 0.0),
                "outgoing_lease_lifetime_usd": out_by_type.get("lifetime_contract_value", 0.0),
                "outgoing_purchase_commitments_usd": out_by_type.get("remaining_commitment", 0.0),
                "outgoing_contingent_guarantees_usd": out_by_type.get("contingent_guarantee", 0.0),
                "outgoing_equity_investments_usd": out_by_type.get("equity_investment", 0.0),
                "incoming_lease_claims_usd": in_by_type.get("lifetime_contract_value", 0.0),
                "incoming_debt_claims_usd": in_by_type.get("principal_outstanding", 0.0),
                "incoming_purchase_claims_usd": in_by_type.get("remaining_commitment", 0.0),
                "incoming_annualized_run_rate_usd": in_by_type.get("annualized_run_rate", 0.0)
            })

        df = pd.DataFrame(records).sort_values(by="outgoing_principal_debt_usd", ascending=False)
        return df

    def query_assumption_reachability(self, assumption_id: str) -> Dict[str, Any]:
        """
        Identify all edges, nodes, and contractual dollar volume relying on a specific assumption.
        Note: This is an Assumption Dependency Footprint / Reachability metric, NOT financial loss.
        """
        matching_edges = []
        total_exposed_usd = 0.0
        exposed_nodes = set()
        amount_type_breakdown = {}

        for u, v, k, d in self.graph.edges(data=True, keys=True):
            assumptions = d.get("shared_assumptions", [])
            if assumption_id in assumptions:
                amt = d.get("amount", 0.0)
                atype = d.get("amount_type", "unspecified")
                matching_edges.append({
                    "obligation_id": k,
                    "from_entity": u,
                    "to_entity": v,
                    "type": d.get("obligation_type"),
                    "amount_usd": amt,
                    "amount_type": atype,
                    "evidence_class": d.get("evidence_class")
                })
                total_exposed_usd += amt
                amount_type_breakdown[atype] = amount_type_breakdown.get(atype, 0.0) + amt
                exposed_nodes.add(u)
                exposed_nodes.add(v)

        return {
            "assumption_id": assumption_id,
            "total_contract_value_usd": total_exposed_usd,
            "amount_type_breakdown": amount_type_breakdown,
            "num_edges": len(matching_edges),
            "num_entities": len(exposed_nodes),
            "entities": sorted(list(exposed_nodes)),
            "edges": matching_edges
        }

    def aggregate_all_assumptions(self) -> pd.DataFrame:
        """Rank all shared assumptions by total contractual value supported."""
        all_assumptions = set()
        for _, _, _, d in self.graph.edges(data=True, keys=True):
            for a in d.get("shared_assumptions", []):
                if a:
                    all_assumptions.add(a)

        records = []
        for aid in sorted(list(all_assumptions)):
            res = self.query_assumption_reachability(aid)
            records.append({
                "assumption_id": aid,
                "total_contract_value_usd": res["total_contract_value_usd"],
                "num_edges_supported": res["num_edges"],
                "num_entities_involved": res["num_entities"],
                "entities_involved": ", ".join(res["entities"])
            })

        df = pd.DataFrame(records).sort_values(by="total_contract_value_usd", ascending=False)
        return df

    def unwrap_spv_perimeter(self) -> nx.MultiDiGraph:
        """Collapse SPVs into parent corporate entities to reveal true consolidated exposure."""
        collapsed = nx.MultiDiGraph()
        spv_map = {
            "CRWV_SPV_VIII": "CRWV",
            "APLD_ELN_LLC": "APLD"
        }

        for u, v, k, d in self.graph.edges(data=True, keys=True):
            true_u = spv_map.get(u, u)
            true_v = spv_map.get(v, v)

            collapsed.add_edge(
                true_u,
                true_v,
                key=k,
                original_u=u,
                original_v=v,
                amount=d.get("amount", 0.0),
                amount_type=d.get("amount_type"),
                primary_type=d.get("obligation_type"),
                recourse=d.get("recourse")
            )

        return collapsed


if __name__ == "__main__":
    net = ObligationNetwork()
    summary = net.compute_exposure_by_amount_type()
    print("=== Contractual Exposure by Amount Type ===")
    print(summary[["entity_id", "outgoing_principal_debt_usd", "outgoing_lease_lifetime_usd", "outgoing_purchase_commitments_usd"]])

    print("\n=== Systemic Assumptions Ranked by Supported Contract Value ===")
    rank_df = net.aggregate_all_assumptions()
    print(rank_df[["assumption_id", "total_contract_value_usd", "num_edges_supported", "entities_involved"]])
