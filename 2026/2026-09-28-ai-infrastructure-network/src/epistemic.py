"""
Generic Epistemic Resolver & Typed Contractual Rate Schema (ADR-017 Engine Refinement)

Provides:
1. KnowledgeState: Typed container representing the epistemic state of any fact, observation,
   or contract attribute (status in {"known", "unknown", "not_yet_existent"}, value, dates, claim IDs).
2. ContractualRate: Typed schema for contract interest rates (fixed coupons, benchmark floating margins,
   floors, and credit spread grids like DDTL 2.0).
3. EpistemicResolver: Universal resolution engine eliminating scenario-specific date conditionals,
   recording an immutable audit trail of all consumed data, and enforcing the Universal Zero-Lookahead Invariant.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import pandas as pd
import yaml

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


@dataclass
class KnowledgeState:
    """
    Epistemic state of an observable fact, metric, or contract attribute.
    Ensures 'unknown' is strictly preserved as None rather than silently defaulting to 0.0 or current values.
    """
    status: str  # "known", "unknown", "not_yet_existent"
    value: Any = None
    economic_date: Optional[str] = None
    public_date: Optional[str] = None
    evidence_claim_ids: List[str] = field(default_factory=list)
    entity_id: Optional[str] = None
    obligation_id: Optional[str] = None
    attribute: Optional[str] = None

    @property
    def is_known(self) -> bool:
        return self.status == "known" and self.value is not None

    @property
    def is_unknown(self) -> bool:
        return self.status == "unknown"

    @property
    def is_not_yet_existent(self) -> bool:
        return self.status == "not_yet_existent"

    def unwrap(self, default: Any = None) -> Any:
        """Returns the resolved value if known; otherwise returns default."""
        return self.value if self.is_known else default


@dataclass
class ContractualRate:
    """
    Typed contractual rate definition replacing bespoke string parsers.
    Supports fixed coupons, benchmark floating spreads (SOFR/EURIBOR), floors, and credit spread grids.
    """
    rate_type: str = "none"  # "fixed", "floating", "spread_grid", "none"
    benchmark: Optional[str] = None  # "SOFR", "EURIBOR", None
    margin_bps: Optional[float] = None
    floor_bps: Optional[float] = None
    fixed_coupon: Optional[float] = None
    spread_grid_id: Optional[str] = None

    @classmethod
    def from_edge(cls, edge_data: Dict[str, Any]) -> "ContractualRate":
        """Instantiate ContractualRate from graph edge data or obligation row."""
        rtype = edge_data.get("rate_type") or "none"
        bm = edge_data.get("benchmark") or edge_data.get("benchmark_rate")
        m_bps = edge_data.get("margin_bps")
        f_bps = edge_data.get("floor_bps")
        fc = edge_data.get("fixed_coupon")
        grid = edge_data.get("spread_grid_id")

        return cls(
            rate_type=str(rtype).lower() if rtype else "none",
            benchmark=str(bm) if bm and pd.notna(bm) else None,
            margin_bps=float(m_bps) if m_bps is not None and pd.notna(m_bps) else None,
            floor_bps=float(f_bps) if f_bps is not None and pd.notna(f_bps) else None,
            fixed_coupon=float(fc) if fc is not None and pd.notna(fc) else None,
            spread_grid_id=str(grid) if grid and pd.notna(grid) else None
        )

    def compute_rate(self, sofr_rate: float = 0.053, customer_tier: Optional[str] = None) -> float:
        """
        Computes effective annual interest rate from typed fields:
        - Fixed: returns fixed_coupon
        - Floating: returns benchmark rate + margin_bps / 10,000, respecting floor_bps
        - Spread Grid: resolves margin from spread grid tiers, plus benchmark rate
        """
        if self.rate_type == "fixed":
            return float(self.fixed_coupon) if self.fixed_coupon is not None else 0.0

        if self.rate_type == "floating":
            base = sofr_rate if (self.benchmark == "SOFR" or self.benchmark is None) else 0.05
            margin = (self.margin_bps / 10000.0) if self.margin_bps is not None else 0.0
            floor = (self.floor_bps / 10000.0) if self.floor_bps is not None else 0.0
            return max(base + margin, floor)

        if self.rate_type == "spread_grid":
            base = sofr_rate
            if self.spread_grid_id == "GRID-CRWV-DDTL2":
                # Customer credit rating grid (CLM-CRWV-016)
                if customer_tier == "specified_investment_grade":
                    margin = 0.0600
                elif customer_tier == "investment_grade":
                    margin = 0.0650
                elif customer_tier == "non_investment_grade":
                    margin = 0.1300
                else:
                    margin = 0.0800  # Default weighted average / portfolio proxy
                return base + margin
            margin = (self.margin_bps / 10000.0) if self.margin_bps is not None else 0.0600
            return base + margin

        return 0.0


class EpistemicResolver:
    """
    Generic Epistemic Resolver for AI Infrastructure Financial Network.
    Enforces ADR-014 and ADR-017 zero-lookahead semantics across all stress functions.
    Tracks an immutable audit trail of every fact resolved, and certifies that no fact
    with a public filing timestamp > as_of_date is ever consumed in knowledge mode.
    """
    def __init__(
        self,
        as_of_date: Optional[str] = None,
        temporal_mode: str = "economic",
        network: Optional[Any] = None,
        facts_df: Optional[pd.DataFrame] = None,
        events_df: Optional[pd.DataFrame] = None,
        financials_df: Optional[pd.DataFrame] = None,
        claims_df: Optional[pd.DataFrame] = None,
    ):
        self.as_of_date = as_of_date or "2026-09-28"
        self.temporal_mode = temporal_mode or "economic"
        self.network = network

        self.facts_df = (
            facts_df if facts_df is not None
            else (pd.read_parquet(PROCESSED_DIR / "obligation_facts.parquet") if (PROCESSED_DIR / "obligation_facts.parquet").exists() else pd.DataFrame())
        )
        self.events_df = (
            events_df if events_df is not None
            else (pd.read_parquet(PROCESSED_DIR / "obligation_events.parquet") if (PROCESSED_DIR / "obligation_events.parquet").exists() else pd.DataFrame())
        )
        self.financials_df = (
            financials_df if financials_df is not None
            else (pd.read_parquet(PROCESSED_DIR / "financials.parquet") if (PROCESSED_DIR / "financials.parquet").exists() else pd.DataFrame())
        )
        self.claims_df = (
            claims_df if claims_df is not None
            else (pd.read_parquet(PROCESSED_DIR / "evidence_claims.parquet") if (PROCESSED_DIR / "evidence_claims.parquet").exists() else pd.DataFrame())
        )

        self.audit_trail: List[KnowledgeState] = []

    def resolve_fact(
        self,
        obligation_id: Optional[str] = None,
        entity_id: Optional[str] = None,
        attribute: str = ""
    ) -> KnowledgeState:
        """
        Resolves an observable fact or contract attribute according to the temporal mode and as_of_date.
        If the fact was not yet publicly filed in known mode, returns KnowledgeState(status='unknown', value=None).
        """
        ks: KnowledgeState

        # 1. Check if matching facts exist in obligation_facts.parquet
        matching = pd.DataFrame()
        if not self.facts_df.empty:
            cond = (self.facts_df["attribute"] == attribute)
            if obligation_id:
                cond = cond & (self.facts_df["obligation_id"] == obligation_id)
            if entity_id:
                cond = cond & (self.facts_df["entity_id"] == entity_id)
            matching = self.facts_df[cond]

        if not matching.empty:
            # Sort by chronology
            sort_cols = [c for c in ["economic_as_of", "publicly_known_from", "fact_id"] if c in matching.columns]
            matching_sorted = matching.sort_values(by=sort_cols)
            latest_fact = matching_sorted.iloc[-1]

            eco_date = str(latest_fact["economic_as_of"]) if pd.notna(latest_fact.get("economic_as_of")) else None
            pub_date = str(latest_fact["publicly_known_from"]) if pd.notna(latest_fact.get("publicly_known_from")) else None
            claims = [str(c) for c in [latest_fact.get("knowledge_claim_id"), latest_fact.get("truth_claim_id")] if pd.notna(c) and str(c).strip()]

            if self.temporal_mode in ["known", "knowledge"]:
                # Public Knowledge Clock: Must have been filed on or before as_of_date
                if pub_date and pub_date > self.as_of_date:
                    ks = KnowledgeState(
                        status="unknown",
                        value=None,
                        economic_date=eco_date,
                        public_date=pub_date,
                        evidence_claim_ids=claims,
                        entity_id=entity_id,
                        obligation_id=obligation_id,
                        attribute=attribute
                    )
                elif eco_date and eco_date > self.as_of_date:
                    ks = KnowledgeState(
                        status="not_yet_existent",
                        value=None,
                        economic_date=eco_date,
                        public_date=pub_date,
                        evidence_claim_ids=claims,
                        entity_id=entity_id,
                        obligation_id=obligation_id,
                        attribute=attribute
                    )
                else:
                    ks = KnowledgeState(
                        status="known",
                        value=latest_fact["value"],
                        economic_date=eco_date,
                        public_date=pub_date,
                        evidence_claim_ids=claims,
                        entity_id=entity_id,
                        obligation_id=obligation_id,
                        attribute=attribute
                    )
            else:
                # Economic Reality Clock: Must have been effective on or before as_of_date
                if eco_date and eco_date > self.as_of_date:
                    ks = KnowledgeState(
                        status="not_yet_existent",
                        value=None,
                        economic_date=eco_date,
                        public_date=pub_date,
                        evidence_claim_ids=claims,
                        entity_id=entity_id,
                        obligation_id=obligation_id,
                        attribute=attribute
                    )
                else:
                    ks = KnowledgeState(
                        status="known",
                        value=latest_fact["value"],
                        economic_date=eco_date,
                        public_date=pub_date,
                        evidence_claim_ids=claims,
                        entity_id=entity_id,
                        obligation_id=obligation_id,
                        attribute=attribute
                    )
            self.audit_trail.append(ks)
            return ks

        # 2. Check canonical entity-level periodic disclosures bound to SEC evidence claims:
        # A) CoreWeave Debt Maturities Schedule (CLM-CRWV-001, Form 10-Q Note 10)
        if entity_id == "CRWV" and attribute in ["debt_maturities", "debt_maturity_schedule"]:
            claim_id = "CLM-CRWV-001"
            eco_date = "2026-06-30"
            pub_date = "2026-08-12"
            raw_value = {
                "2026": 4413000000.0,
                "2027": 6184000000.0,
                "2028": 4416000000.0,
                "total_3yr": 15013000000.0
            }
            if self.temporal_mode in ["known", "knowledge"] and self.as_of_date < pub_date:
                ks = KnowledgeState("unknown", None, eco_date, pub_date, [claim_id], entity_id, obligation_id, attribute)
            elif self.as_of_date < eco_date:
                ks = KnowledgeState("not_yet_existent", None, eco_date, pub_date, [claim_id], entity_id, obligation_id, attribute)
            else:
                ks = KnowledgeState("known", raw_value, eco_date, pub_date, [claim_id], entity_id, obligation_id, attribute)
            self.audit_trail.append(ks)
            return ks

        # B) Applied Digital Campus Construction Phasing (CLM-APLD-004, Form 10-K Item 1)
        if (entity_id == "APLD" or obligation_id == "POLARIS_FORGE_1") and attribute in ["campus_construction_phasing", "operational_mw"]:
            claim_id = "CLM-APLD-004"
            eco_date = "2026-05-31"
            pub_date = "2026-07-29"
            raw_value = {
                "building2_operational_mw": 100.0,
                "building3_total_mw": 150.0,
                "building3_operational_proxy_mw": 50.0,
                "building4_construction_mw": 150.0,
                "total_campus_mw": 400.0
            }
            if self.temporal_mode in ["known", "knowledge"] and self.as_of_date < pub_date:
                ks = KnowledgeState("unknown", None, eco_date, pub_date, [claim_id], entity_id, obligation_id, attribute)
            elif self.as_of_date < eco_date:
                ks = KnowledgeState("not_yet_existent", None, eco_date, pub_date, [claim_id], entity_id, obligation_id, attribute)
            else:
                ks = KnowledgeState("known", raw_value, eco_date, pub_date, [claim_id], entity_id, obligation_id, attribute)
            self.audit_trail.append(ks)
            return ks

        # C) Supermicro Non-Cancelable Purchase Commitments (CLM-SMCI-001, Form 10-K Note 12)
        if entity_id == "SMCI" and attribute in ["purchase_commitments", "remaining_commitment"]:
            claim_id = "CLM-SMCI-001"
            eco_date = "2026-06-30"
            pub_date = "2026-08-31"
            raw_value = 34200000000.0
            if self.temporal_mode in ["known", "knowledge"] and self.as_of_date < pub_date:
                ks = KnowledgeState("unknown", None, eco_date, pub_date, [claim_id], entity_id, obligation_id, attribute)
            elif self.as_of_date < eco_date:
                ks = KnowledgeState("not_yet_existent", None, eco_date, pub_date, [claim_id], entity_id, obligation_id, attribute)
            else:
                ks = KnowledgeState("known", raw_value, eco_date, pub_date, [claim_id], entity_id, obligation_id, attribute)
            self.audit_trail.append(ks)
            return ks

        # Default fallback if attribute completely unmodelled
        ks = KnowledgeState("unknown", None, None, None, [], entity_id, obligation_id, attribute)
        self.audit_trail.append(ks)
        return ks

    def resolve_financial(self, entity_id: str, metric: str) -> KnowledgeState:
        """
        Resolves an audited financial fact from SEC XBRL disclosures with strict temporal filtering.
        """
        if self.financials_df.empty:
            ks = KnowledgeState("unknown", None, None, None, [], entity_id=entity_id, attribute=metric)
            self.audit_trail.append(ks)
            return ks

        sub = self.financials_df[(self.financials_df["entity_id"] == entity_id) & (self.financials_df["metric"] == metric)].copy()
        if sub.empty:
            ks = KnowledgeState("unknown", None, None, None, [], entity_id=entity_id, attribute=metric)
            self.audit_trail.append(ks)
            return ks

        if self.temporal_mode in ["known", "knowledge"]:
            sub = sub[sub["filed_date"] <= self.as_of_date]
        else:
            sub = sub[sub["period_end"] <= self.as_of_date]

        if sub.empty:
            ks = KnowledgeState("unknown", None, None, None, [], entity_id=entity_id, attribute=metric)
            self.audit_trail.append(ks)
            return ks

        latest = sub.sort_values(by=["period_end", "filed_date"]).iloc[-1]
        val = float(latest["value"]) if pd.notna(latest["value"]) else None
        ks = KnowledgeState(
            status="known" if val is not None else "unknown",
            value=val,
            economic_date=str(latest["period_end"]),
            public_date=str(latest["filed_date"]),
            evidence_claim_ids=[f"XBRL-{entity_id}-{metric}"],
            entity_id=entity_id,
            attribute=metric
        )
        self.audit_trail.append(ks)
        return ks

    def assert_zero_lookahead(self) -> None:
        """
        Universal Zero-Lookahead Invariant:
        In known mode, certifies that every consumed fact, financial observation,
        and contract attribute has a public disclosure timestamp <= as_of_date.
        Also asserts that any observation with status='unknown' has value=None (no silent fallback).
        """
        if self.temporal_mode not in ["known", "knowledge"]:
            return

        for ks in self.audit_trail:
            if ks.status == "known":
                if ks.public_date and str(ks.public_date) > str(self.as_of_date):
                    raise AssertionError(
                        f"Universal Zero-Lookahead Invariant VIOLATED: Consumed '{ks.attribute}' "
                        f"for entity='{ks.entity_id}' obligation='{ks.obligation_id}' with public_date '{ks.public_date}' "
                        f"which is strictly after query as_of_date '{self.as_of_date}'!"
                    )
            elif ks.status in ["unknown", "not_yet_existent"]:
                if ks.value is not None:
                    raise AssertionError(
                        f"Epistemic Integrity VIOLATED: '{ks.attribute}' has status='{ks.status}' "
                        f"but contains non-null value {ks.value}!"
                    )
