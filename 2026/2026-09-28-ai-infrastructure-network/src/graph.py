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
    def __init__(
        self,
        entities_df: Optional[pd.DataFrame] = None,
        obligations_df: Optional[pd.DataFrame] = None,
        facts_df: Optional[pd.DataFrame] = None,
        events_df: Optional[pd.DataFrame] = None
    ):
        if entities_df is None:
            entities_df = pd.read_parquet(PROCESSED_DIR / "entities.parquet")
        if obligations_df is None:
            obligations_df = pd.read_parquet(PROCESSED_DIR / "obligations.parquet")
        if facts_df is None:
            facts_path = PROCESSED_DIR / "obligation_facts.parquet"
            if facts_path.exists():
                facts_df = pd.read_parquet(facts_path)
            else:
                facts_df = pd.DataFrame()
        if events_df is None:
            events_path = PROCESSED_DIR / "obligation_events.parquet"
            if events_path.exists():
                events_df = pd.read_parquet(events_path)
            else:
                events_df = pd.DataFrame()

        self.entities_df = entities_df.set_index("entity_id") if "entity_id" in entities_df.columns else entities_df
        self.obligations_df = obligations_df
        self.facts_df = facts_df
        self.events_df = events_df
        self.as_of_date = None
        self.temporal_mode = None
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
            flt_amt = float(row["floating_principal"]) if pd.notna(row.get("floating_principal")) else None
            fac_cap = float(row["facility_capacity"]) if pd.notna(row.get("facility_capacity")) else None

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
                economic_valid_from=row.get("economic_valid_from", row.get("valid_from")),
                economic_valid_to=row.get("economic_valid_to", row.get("valid_to")),
                publicly_known_from=row.get("publicly_known_from", row.get("observed_as_of")),
                rate_type=row.get("rate_type", "fixed" if row.get("obligation_type") == "debt_facility" else "none"),
                benchmark_rate=row.get("benchmark_rate"),
                floating_principal=flt_amt,
                facility_capacity=fac_cap,
                supersedes=row.get("supersedes"),
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

    def get_parent(self, entity_id: str):
        """Resolve the direct parent entity ID, or None if entity is at the root."""
        if entity_id in self.entities_df.index:
            p = self.entities_df.loc[entity_id].get("parent_entity_id")
            if pd.notna(p) and str(p).strip():
                return str(p).strip()
        return None

    def get_root_parent(self, entity_id: str) -> str:
        """
        Traverse parent_entity_id hierarchy upwards to resolve the ultimate consolidated corporate parent.
        Example: APLD_ELN02_LLC -> APLD_COMPUTECO -> APLD.
        Example: APLD_COMPUTECO3 -> APLD_HPC_HOLDINGS2 -> APLD.
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

    def economic_as_of(self, date_str: str) -> "ObligationNetwork":
        """
        Economic Clock: Returns the contractual topology active in economic reality on date_str.
        Filters obligations using discrete lifecycle events from obligation_events when available:
          - created.economic_effective_at <= date_str
          - no terminated/superseded event with economic_effective_at <= date_str
          - contractual half-open maturity [valid_from, valid_to): date_str < valid_to.
        Clears mutable fact-managed fields to None ("no historical fact = unknown") before overlaying
        eligible facts where economic_as_of <= date_str, sorting deterministically.
        """
        valid_rows = []
        for _, row in self.obligations_df.iterrows():
            oid = row["obligation_id"]

            # 1. Edge existence: Creation event check
            eff_from = row.get("economic_valid_from") or row.get("valid_from")
            if not self.events_df.empty:
                c_evts = self.events_df[(self.events_df["obligation_id"] == oid) & (self.events_df["event_type"] == "created")]
                if not c_evts.empty:
                    eff_from = c_evts.iloc[0]["economic_effective_at"]
            if pd.notna(eff_from) and str(eff_from) > date_str:
                continue

            # 2. Edge existence: Termination / supersession event check
            retired = False
            if not self.events_df.empty:
                t_evts = self.events_df[(self.events_df["obligation_id"] == oid) & (self.events_df["event_type"].isin(["terminated", "superseded"]))]
                if not t_evts.empty:
                    t_date = t_evts.iloc[0]["economic_effective_at"]
                    if pd.notna(t_date) and str(t_date) <= date_str:
                        retired = True
            if retired:
                continue

            # Half-open interval [v_from, v_to): expired if date_str >= v_to
            v_to = row.get("economic_valid_to") or row.get("valid_to")
            if pd.notna(v_to) and str(v_to) <= date_str:
                continue

            r = row.copy()
            # Reset mutable fact fields to None before overlaying facts (ADR-014: no back-projection)
            r["amount"] = None
            r["amount_known"] = False
            r["floating_principal"] = None
            r["facility_capacity"] = None
            r["capacity_mw"] = None
            r["reference_exposure_estimate"] = None

            if not self.facts_df.empty:
                matching_facts = self.facts_df[
                    (self.facts_df["obligation_id"] == oid) &
                    (self.facts_df["economic_as_of"] <= date_str)
                ]
                if not matching_facts.empty:
                    sort_cols = [c for c in ["economic_as_of", "publicly_known_from", "fact_id"] if c in matching_facts.columns]
                    for attr, grp in matching_facts.groupby("attribute"):
                        latest_fact = grp.sort_values(by=sort_cols).iloc[-1]
                        f_val = latest_fact["value"]
                        if attr in ["principal_outstanding", "lifetime_contract_value", "remaining_commitment", "recognized_revenue", "equity_investment"]:
                            r["amount"] = f_val
                            r["amount_known"] = bool(pd.notna(f_val))
                        elif attr == "contingent_obligations":
                            r["amount"] = None
                            r["amount_known"] = False
                        elif attr == "facility_capacity":
                            r["facility_capacity"] = f_val
                        elif attr == "floating_principal":
                            r["floating_principal"] = f_val
                        elif attr == "reference_exposure_estimate":
                            r["reference_exposure_estimate"] = f_val
                        elif attr == "capacity_mw":
                            r["capacity_mw"] = f_val
            valid_rows.append(r)
        filtered_df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame(columns=self.obligations_df.columns)
        net = ObligationNetwork(entities_df=self.entities_df.reset_index(), obligations_df=filtered_df, facts_df=self.facts_df, events_df=self.events_df)
        net.as_of_date = date_str
        net.temporal_mode = "economic"
        return net

    def known_as_of(self, date_str: str) -> "ObligationNetwork":
        """
        Information Clock (Public Knowledge / Epistemic Clock):
        Returns the contractual topology that a public observer could actually have known on date_str
        without look-ahead bias (ADR-013 & ADR-014).
        Filters contract existence where:
          - created.publicly_known_at <= date_str AND created.economic_effective_at <= date_str
          - no terminated/superseded event with publicly_known_at <= date_str AND economic_effective_at <= date_str
          - if no explicit early termination event exists, contractual maturity date > date_str.
        Fact-Level Bitemporality:
          Attaches measurements ONLY from facts where publicly_known_from <= date_str AND economic_as_of <= date_str.
          Resets all mutable fields to None before overlaying facts, so if an obligation's current measurement
          was not yet publicly known on date_str, its amount remains None (amount_known = False).
        """
        valid_rows = []
        for _, row in self.obligations_df.iterrows():
            oid = row["obligation_id"]

            # 1. Edge existence: Creation event knowledge check
            k_from = row.get("publicly_known_from") or row.get("observed_as_of")
            eff_from = row.get("economic_valid_from") or row.get("valid_from")
            if not self.events_df.empty:
                c_evts = self.events_df[(self.events_df["obligation_id"] == oid) & (self.events_df["event_type"] == "created")]
                if not c_evts.empty:
                    k_from = c_evts.iloc[0]["publicly_known_at"]
                    eff_from = c_evts.iloc[0]["economic_effective_at"]

            if pd.notna(k_from) and str(k_from) > date_str:
                continue
            if pd.notna(eff_from) and str(eff_from) > date_str:
                continue

            # 2. Edge existence: Termination / supersession event knowledge check
            retired_known = False
            has_term_event = False
            if not self.events_df.empty:
                t_evts = self.events_df[(self.events_df["obligation_id"] == oid) & (self.events_df["event_type"].isin(["terminated", "superseded"]))]
                if not t_evts.empty:
                    has_term_event = True
                    k_term = t_evts.iloc[0]["publicly_known_at"]
                    eff_term = t_evts.iloc[0]["economic_effective_at"]
                    if pd.notna(k_term) and str(k_term) <= date_str and pd.notna(eff_term) and str(eff_term) <= date_str:
                        retired_known = True

            if retired_known:
                continue

            # If no explicit termination event exists, check scheduled contractual maturity
            if not has_term_event:
                v_to = row.get("economic_valid_to") or row.get("valid_to")
                if pd.notna(v_to) and str(v_to) <= date_str:
                    continue

            r = row.copy()
            # Reset mutable fact fields to None before overlaying facts (ADR-014: no back-projection)
            r["amount"] = None
            r["amount_known"] = False
            r["floating_principal"] = None
            r["facility_capacity"] = None
            r["capacity_mw"] = None
            r["reference_exposure_estimate"] = None

            if not self.facts_df.empty:
                matching_facts = self.facts_df[
                    (self.facts_df["obligation_id"] == oid) &
                    (self.facts_df["publicly_known_from"] <= date_str) &
                    (self.facts_df["economic_as_of"] <= date_str)
                ]
                if not matching_facts.empty:
                    sort_cols = [c for c in ["economic_as_of", "publicly_known_from", "fact_id"] if c in matching_facts.columns]
                    for attr, grp in matching_facts.groupby("attribute"):
                        latest_fact = grp.sort_values(by=sort_cols).iloc[-1]
                        f_val = latest_fact["value"]
                        if attr in ["principal_outstanding", "lifetime_contract_value", "remaining_commitment", "recognized_revenue", "equity_investment"]:
                            r["amount"] = f_val
                            r["amount_known"] = bool(pd.notna(f_val))
                        elif attr == "contingent_obligations":
                            r["amount"] = None
                            r["amount_known"] = False
                        elif attr == "facility_capacity":
                            r["facility_capacity"] = f_val
                        elif attr == "floating_principal":
                            r["floating_principal"] = f_val
                        elif attr == "reference_exposure_estimate":
                            r["reference_exposure_estimate"] = f_val
                        elif attr == "capacity_mw":
                            r["capacity_mw"] = f_val

            valid_rows.append(r)
        filtered_df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame(columns=self.obligations_df.columns)
        net = ObligationNetwork(entities_df=self.entities_df.reset_index(), obligations_df=filtered_df, facts_df=self.facts_df, events_df=self.events_df)
        net.as_of_date = date_str
        net.temporal_mode = "known"
        return net

    def as_of(self, date_str: str, mode: str = "economic") -> "ObligationNetwork":
        """
        Unified temporal query dispatcher.
        mode='economic' (default): queries economic reality clock.
        mode='known': queries public knowledge clock (eliminates look-ahead bias).
        """
        if mode == "known":
            return self.known_as_of(date_str)
        return self.economic_as_of(date_str)

    def get_fact(self, obligation_id: str, attribute: str) -> Optional[float]:
        """Query active fact for a given obligation and attribute based on the network's temporal state."""
        if self.facts_df.empty:
            return None
        sub = self.facts_df[(self.facts_df["obligation_id"] == obligation_id) & (self.facts_df["attribute"] == attribute)]
        if sub.empty:
            return None
        if self.as_of_date:
            if self.temporal_mode == "known":
                sub = sub[(sub["publicly_known_from"] <= self.as_of_date) & (sub["economic_as_of"] <= self.as_of_date)]
            else:
                sub = sub[sub["economic_as_of"] <= self.as_of_date]
        if sub.empty:
            return None
        sort_cols = [c for c in ["economic_as_of", "publicly_known_from", "fact_id"] if c in sub.columns]
        latest = sub.sort_values(by=sort_cols).iloc[-1]
        return float(latest["value"]) if pd.notna(latest["value"]) else None

    def get_entity_fact(self, entity_id: str, attribute: str) -> Optional[float]:
        """Query active fact for an entity across all its obligations based on temporal state."""
        if self.facts_df.empty:
            return None
        sub = self.facts_df[(self.facts_df["entity_id"] == entity_id) & (self.facts_df["attribute"] == attribute)]
        if sub.empty:
            return None
        if self.as_of_date:
            if self.temporal_mode == "known":
                sub = sub[(sub["publicly_known_from"] <= self.as_of_date) & (sub["economic_as_of"] <= self.as_of_date)]
            else:
                sub = sub[sub["economic_as_of"] <= self.as_of_date]
        if sub.empty:
            return None
        sort_cols = [c for c in ["economic_as_of", "publicly_known_from", "fact_id"] if c in sub.columns]
        latest = sub.sort_values(by=sort_cols).iloc[-1]
        return float(latest["value"]) if pd.notna(latest["value"]) else None

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
                recourse=d.get("recourse"),
                rate_type=d.get("rate_type"),
                benchmark_rate=d.get("benchmark_rate"),
                floating_principal=d.get("floating_principal"),
                facility_capacity=d.get("facility_capacity"),
                capacity_mw=d.get("capacity_mw"),
                reference_exposure_estimate=d.get("reference_exposure_estimate"),
                economic_valid_from=d.get("economic_valid_from"),
                economic_valid_to=d.get("economic_valid_to"),
                publicly_known_from=d.get("publicly_known_from"),
                supersedes=d.get("supersedes"),
                superseded_by=d.get("superseded_by")
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

    print("\n=== Economic Clock: May 31, 2026 vs June 16, 2026 vs September 28, 2026 ===")
    net_may = net.economic_as_of("2026-05-31")
    net_jun16 = net.economic_as_of("2026-06-16")
    net_sep = net.economic_as_of("2026-09-28")
    print(f"Edges at 2026-05-31: {net_may.graph.number_of_edges()}")
    print(f"Edges at 2026-06-16: {net_jun16.graph.number_of_edges()} (Half-open [start, end) interval: 1 active note tranche)")
    print(f"Edges at 2026-09-28: {net_sep.graph.number_of_edges()} (Conserved: $300M Bridge -> $1.59B 7% Notes)")
    print(f"Bridge present at May 31: {'OBL-APLD-DEBT-BRIDGE' in [k for _, _, k in net_may.graph.edges(keys=True)]}")
    print(f"Bridge present at June 16: {'OBL-APLD-DEBT-BRIDGE' in [k for _, _, k in net_jun16.graph.edges(keys=True)]} (Expected False)")
    print(f"7% Notes present at June 16: {'OBL-APLD-DEBT-7PCT-2026' in [k for _, _, k in net_jun16.graph.edges(keys=True)]} (Expected True)")
    print(f"Bridge present at Sep 28: {'OBL-APLD-DEBT-BRIDGE' in [k for _, _, k in net_sep.graph.edges(keys=True)]}")
    print(f"7% Notes present at May 31: {'OBL-APLD-DEBT-7PCT-2026' in [k for _, _, k in net_may.graph.edges(keys=True)]}")
    print(f"7% Notes present at Sep 28: {'OBL-APLD-DEBT-7PCT-2026' in [k for _, _, k in net_sep.graph.edges(keys=True)]}")

    print("\n=== Information Clock: Known as of June 30, 2026 vs September 28, 2026 ===")
    net_known_jun = net.known_as_of("2026-06-30")
    net_known_sep = net.known_as_of("2026-09-28")
    known_jun_edges = net_known_jun.graph.number_of_edges()
    known_jun_with_amt = sum(1 for _, _, _, d in net_known_jun.graph.edges(data=True, keys=True) if d.get("amount") is not None)
    print(f"Edges known as of 2026-06-30: {known_jun_edges} (Contract existence known)")
    print(f"Edges with known amounts as of 2026-06-30: {known_jun_with_amt} (Fact-level bitemporality eliminates look-ahead leakage)")
    print(f"Edges known as of 2026-09-28: {net_known_sep.graph.number_of_edges()} (Full public knowledge)")

