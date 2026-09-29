"""
Obligation Network Multi-Graph Construction and Analysis Library (Phase 0.7 Hardening)
Constructs directed MultiDiGraphs preserving multiple distinct contracts per counterparty pair,
categorizes exposure by amount_type (avoiding false net netting), unwraps SPV perimeters dynamically
via corporate parent hierarchy, supports temporal filtering via network.as_of(date_str), and maps
shared systemic assumption dependencies without NaN poisoning on uncapped obligations.
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
                subsector=row.get("subsector"),
                status=row.get("status"),
                parent_entity_id=row.get("parent_entity_id"),
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

            amt = float(row["amount"]) if pd.notna(row.get("amount")) else None
            ref_amt = float(row["reference_exposure_estimate"]) if pd.notna(row.get("reference_exposure_estimate")) else None
            cap_mw = float(row["capacity_mw"]) if pd.notna(row.get("capacity_mw")) else None

            self.graph.add_edge(
                u,
                v,
                key=obl_id,
                obligation_id=obl_id,
                obligation_type=row.get("obligation_type"),
                amount=amt,
                amount_known=bool(pd.notna(row.get("amount"))),
                amount_type=row.get("amount_type", "unspecified"),
                as_of_date=row.get("as_of_date"),
                observed_as_of=row.get("observed_as_of"),
                valid_from=row.get("valid_from"),
                valid_to=row.get("valid_to"),
                superseded_by=row.get("superseded_by"),
                currency=row.get("currency", "USD"),
                term_years=row.get("term_years"),
                effective_date=row.get("effective_date"),
                maturity_date=row.get("maturity_date"),
                capacity_mw=cap_mw,
                capacity_description=row.get("capacity_description"),
                reference_exposure_estimate=ref_amt,
                reference_exposure_class=row.get("reference_exposure_class"),
                recourse=row.get("recourse"),
                collateral=row.get("collateral"),
                guarantee=row.get("guarantee"),
                evidence_class=row.get("evidence_class"),
                confidence=float(row.get("confidence", 1.0)),
                claim_ids=str(row.get("claim_ids", "")).split(","),
                shared_assumptions=assumptions
            )

    def get_root_parent(self, entity_id: str) -> str:
        """
        Traverse parent_entity_id hierarchy upwards to resolve the ultimate consolidated corporate parent.
        Example: APLD_ELN02_LLC -> APLD_COMPUTECO -> APLD.
        """
        curr = entity_id
        visited = set()
        while curr in self.entities_df.index and curr not in visited:
            visited.add(curr)
            parent = self.entities_df.loc[curr].get("parent_entity_id")
            if pd.notna(parent) and str(parent).strip() and str(parent).strip() != curr:
                curr = str(parent).strip()
            else:
                break
        return curr

    def as_of(self, date_str: str) -> "ObligationNetwork":
        """
        Returns a new ObligationNetwork reflecting the contractual topology active as of date_str.
        Filters out obligations where valid_from > date_str or valid_to < date_str.
        """
        valid_rows = []
        for _, row in self.obligations_df.iterrows():
            v_from = row.get("valid_from")
            v_to = row.get("valid_to")
            if pd.notna(v_from) and str(v_from) > date_str:
                continue
            if pd.notna(v_to) and str(v_to) < date_str:
                continue
            valid_rows.append(row)
        filtered_df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame(columns=self.obligations_df.columns)
        return ObligationNetwork(entities_df=self.entities_df.reset_index(), obligations_df=filtered_df)

    def compute_exposure_by_amount_type(self) -> pd.DataFrame:
        """
        Compute outgoing and incoming exposure broken down strictly by amount_type.
        Eliminates the false 'net contractual exposure' metric and prevents NaN poisoning from uncapped contracts.
        """
        records = []
        for node in self.graph.nodes():
            out_edges = self.graph.out_edges(node, data=True, keys=True)
            in_edges = self.graph.in_edges(node, data=True, keys=True)

            out_by_type = {}
            out_contingent_count = 0
            out_contingent_ref_proxy = 0.0

            for _, _, k, d in out_edges:
                atype = d.get("amount_type", "unspecified")
                amt = d.get("amount")
                if amt is not None:
                    out_by_type[atype] = out_by_type.get(atype, 0.0) + amt
                if atype == "contingent_obligations":
                    out_contingent_count += 1
                    ref_proxy = d.get("reference_exposure_estimate")
                    if ref_proxy is not None:
                        out_contingent_ref_proxy += ref_proxy

            in_by_type = {}
            in_contingent_count = 0
            for _, _, k, d in in_edges:
                atype = d.get("amount_type", "unspecified")
                amt = d.get("amount")
                if amt is not None:
                    in_by_type[atype] = in_by_type.get(atype, 0.0) + amt
                if atype == "contingent_obligations":
                    in_contingent_count += 1

            records.append({
                "entity_id": node,
                "ticker": self.graph.nodes[node].get("ticker"),
                "category": self.graph.nodes[node].get("category", "unknown"),
                "num_outgoing_contracts": len(out_edges),
                "num_incoming_contracts": len(in_edges),
                "outgoing_principal_debt_usd": out_by_type.get("principal_outstanding", 0.0),
                "outgoing_facility_capacity_usd": out_by_type.get("facility_capacity", 0.0),
                "outgoing_lease_lifetime_usd": out_by_type.get("lifetime_contract_value", 0.0),
                "outgoing_purchase_commitments_usd": out_by_type.get("remaining_commitment", 0.0),
                "outgoing_contingent_guarantees_usd": out_by_type.get("contingent_guarantee", 0.0),
                "outgoing_contingent_obligations_count": out_contingent_count,
                "outgoing_contingent_ref_proxy_usd": out_contingent_ref_proxy,
                "outgoing_equity_investments_usd": out_by_type.get("equity_investment", 0.0),
                "incoming_lease_claims_usd": in_by_type.get("lifetime_contract_value", 0.0),
                "incoming_debt_claims_usd": in_by_type.get("principal_outstanding", 0.0),
                "incoming_purchase_claims_usd": in_by_type.get("remaining_commitment", 0.0),
                "incoming_recognized_revenue_usd": in_by_type.get("recognized_revenue", 0.0),
                "incoming_contingent_obligations_count": in_contingent_count
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
                amt = d.get("amount")
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
                if amt is not None:
                    total_exposed_usd += amt
                    amount_type_breakdown[atype] = amount_type_breakdown.get(atype, 0.0) + amt
                else:
                    amount_type_breakdown[atype] = amount_type_breakdown.get(atype, 0.0)
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
        """
        Dynamically collapse SPVs and financing subsidiaries into parent corporate entities
        to reveal true consolidated economic exposure using corporate hierarchy.
        """
        collapsed = nx.MultiDiGraph()

        for u, v, k, d in self.graph.edges(data=True, keys=True):
            true_u = self.get_root_parent(u)
            true_v = self.get_root_parent(v)

            collapsed.add_edge(
                true_u,
                true_v,
                key=k,
                original_u=u,
                original_v=v,
                amount=d.get("amount"),
                amount_known=d.get("amount_known", True),
                amount_type=d.get("amount_type"),
                primary_type=d.get("obligation_type"),
                recourse=d.get("recourse")
            )

        return collapsed


if __name__ == "__main__":
    net = ObligationNetwork()
    summary = net.compute_exposure_by_amount_type()
    print("=== Contractual Exposure by Amount Type ===")
    print(summary[["entity_id", "outgoing_principal_debt_usd", "outgoing_lease_lifetime_usd", "outgoing_purchase_commitments_usd", "outgoing_contingent_obligations_count"]])

    print("\n=== Dynamic SPV Unwrapping (Root Parent Traversal) ===")
    collapsed = net.unwrap_spv_perimeter()
    print(f"Nodes in collapsed graph: {sorted(list(collapsed.nodes()))}")
    spv_nodes = [n for n in collapsed.nodes() if "SPV" in n or "LLC" in n]
    print(f"SPVs remaining in collapsed graph: {len(spv_nodes)} (expected 0)")

    print("\n=== Temporal Filtering: May 31, 2026 vs September 28, 2026 ===")
    net_may = net.as_of("2026-05-31")
    net_sep = net.as_of("2026-09-28")
    print(f"Edges at 2026-05-31: {net_may.graph.number_of_edges()}")
    print(f"Edges at 2026-09-28: {net_sep.graph.number_of_edges()} (Bridge Facility retired/refinanced)")
    print(f"Bridge present at May 31: {'OBL-APLD-DEBT-BRIDGE' in [k for _, _, k in net_may.graph.edges(keys=True)]}")
    print(f"Bridge present at Sep 28: {'OBL-APLD-DEBT-BRIDGE' in [k for _, _, k in net_sep.graph.edges(keys=True)]}")
