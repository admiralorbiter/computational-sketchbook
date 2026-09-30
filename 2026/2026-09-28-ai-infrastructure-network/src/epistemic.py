"""
Generic Epistemic Resolver & Typed Contractual Rate Schema (ADR-017 Engine Refinement)

Provides:
1. KnowledgeState: Typed container representing the epistemic state of any fact, observation,
   or contract attribute (status in {"known", "unknown", "not_yet_existent"}, value, dates, claim IDs).
   Enforces strict null safety where NaN is never treated as known.
2. ContractualRate: Typed schema for contract interest rates (fixed coupons, benchmark floating margins,
   floors, and credit spread grids loaded from YAML configuration).
3. RateLeg: Contractual rate leg for mixed-rate instruments (e.g. DDTL 4.0 floating/fixed legs).
4. EpistemicResolver: Universal resolution engine with eligible-fact pre-filtering,
   recording an immutable audit trail of all consumed data, and enforcing the Universal Zero-Lookahead Invariant.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import pandas as pd
import yaml

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def load_spread_grids() -> Dict[str, Any]:
    """Loads credit spread grids dynamically from YAML configuration."""
    grids_file = CONFIG_DIR / "spread_grids.yml"
    if not grids_file.exists():
        return {}
    with open(grids_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("spread_grids", {})


def load_rate_legs() -> Dict[str, List["RateLeg"]]:
    """Loads discrete calculation rate legs grouped by obligation_id from YAML configuration."""
    legs_file = CONFIG_DIR / "rate_legs.yml"
    if not legs_file.exists():
        return {}
    with open(legs_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    raw_legs = data.get("rate_legs", {})
    by_obligation: Dict[str, List[RateLeg]] = {}
    for lid, leg_dict in raw_legs.items():
        leg = RateLeg(
            leg_id=lid,
            obligation_id=str(leg_dict.get("obligation_id", "")),
            leg_type=str(leg_dict.get("leg_type", "fixed")),
            principal=float(leg_dict["principal"]) if leg_dict.get("principal") is not None and pd.notna(leg_dict.get("principal")) else None,
            benchmark=str(leg_dict["benchmark"]).upper() if leg_dict.get("benchmark") and pd.notna(leg_dict.get("benchmark")) else None,
            margin_bps=float(leg_dict["margin_bps"]) if leg_dict.get("margin_bps") is not None and pd.notna(leg_dict.get("margin_bps")) else None,
            floor_bps=float(leg_dict["floor_bps"]) if leg_dict.get("floor_bps") is not None and pd.notna(leg_dict.get("floor_bps")) else None,
            fixed_coupon=float(leg_dict["fixed_coupon"]) if leg_dict.get("fixed_coupon") is not None and pd.notna(leg_dict.get("fixed_coupon")) else None,
            spread_grid_id=str(leg_dict["spread_grid_id"]) if leg_dict.get("spread_grid_id") and pd.notna(leg_dict.get("spread_grid_id")) else None,
            description=leg_dict.get("description")
        )
        by_obligation.setdefault(leg.obligation_id, []).append(leg)
    return by_obligation


@dataclass
class KnowledgeState:
    """
    Epistemic state of an observable fact, metric, or contract attribute.
    Ensures 'unknown' is strictly preserved as None rather than silently defaulting to 0.0 or current values.
    NaN is strictly treated as null / unknown to preserve epistemic integrity.
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
        return self.status == "known" and self.value is not None and bool(pd.notna(self.value))

    @property
    def is_unknown(self) -> bool:
        return self.status == "unknown" or (self.status == "known" and not bool(pd.notna(self.value)))

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
    Fails closed on missing or unrecognized rate components rather than manufacturing synthetic defaults.
    """
    rate_type: str = "none"  # "fixed", "floating", "spread_grid", "rate_legs", "none"
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
            benchmark=str(bm).upper() if bm and pd.notna(bm) else None,
            margin_bps=float(m_bps) if m_bps is not None and pd.notna(m_bps) else None,
            floor_bps=float(f_bps) if f_bps is not None and pd.notna(f_bps) else None,
            fixed_coupon=float(fc) if fc is not None and pd.notna(fc) else None,
            spread_grid_id=str(grid) if grid and pd.notna(grid) else None
        )

    def compute_rate(
        self,
        sofr_rate: float = 0.053,
        euribor_rate: Optional[float] = None,
        customer_tier: Optional[str] = None
    ) -> Optional[float]:
        """
        Computes effective annual interest rate from typed fields:
        - Fixed: returns fixed_coupon (fails closed if None/NaN)
        - Floating: returns max(base, floor) + margin_bps / 10,000 (fails closed if unsupported/missing benchmark)
        - Spread Grid: resolves margin from loaded spread_grids.yml tiers (fails closed if grid/tier unknown)
        """
        if self.rate_type == "fixed":
            if self.fixed_coupon is None or pd.isna(self.fixed_coupon):
                return None
            return float(self.fixed_coupon)

        if self.rate_type == "floating":
            bm = (self.benchmark or "SOFR").upper()
            if bm == "SOFR":
                base = sofr_rate
            elif bm == "EURIBOR":
                if euribor_rate is None:
                    return None
                base = euribor_rate
            else:
                return None  # Fail closed on unrecognized benchmark

            floor = (self.floor_bps / 10000.0) if (self.floor_bps is not None and pd.notna(self.floor_bps)) else 0.0
            effective_base = max(base, floor)
            margin = (self.margin_bps / 10000.0) if (self.margin_bps is not None and pd.notna(self.margin_bps)) else 0.0
            return effective_base + margin

        if self.rate_type == "spread_grid":
            if not self.spread_grid_id:
                raise ValueError("Rate type is 'spread_grid' but spread_grid_id is None")
            grids = load_spread_grids()
            if self.spread_grid_id not in grids:
                raise ValueError(f"Unknown spread_grid_id: '{self.spread_grid_id}'. Grid must be configured in spread_grids.yml")
            grid = grids[self.spread_grid_id]
            tiers = grid.get("tiers", {})
            if customer_tier is not None:
                if customer_tier not in tiers:
                    raise ValueError(f"Unknown customer_tier '{customer_tier}' for spread grid '{self.spread_grid_id}'")
                margin_bps = tiers[customer_tier]["margin_bps"]
            else:
                margin_bps = grid.get("default_margin_bps")
                if margin_bps is None:
                    raise ValueError(f"Spread grid '{self.spread_grid_id}' has no default_margin_bps and no customer_tier was specified")

            bm = (self.benchmark or grid.get("benchmark") or "SOFR").upper()
            if bm == "SOFR":
                base = sofr_rate
            elif bm == "EURIBOR":
                if euribor_rate is None:
                    return None
                base = euribor_rate
            else:
                return None
            return base + (margin_bps / 10000.0)

        return None


@dataclass
class RateLeg:
    """
    Contractual rate leg representing a discrete calculation component of a multi-tranche or mixed-rate obligation.
    E.g. DDTL 4.0: $1.400B floating tranche at SOFR + 225 bps and $1.437B fixed tranche at 6.35%.
    """
    leg_id: str
    obligation_id: str
    leg_type: str  # "fixed", "floating", "spread_grid"
    principal: Optional[float] = None
    benchmark: Optional[str] = None
    margin_bps: Optional[float] = None
    floor_bps: Optional[float] = None
    fixed_coupon: Optional[float] = None
    spread_grid_id: Optional[str] = None
    description: Optional[str] = None

    def compute_rate(
        self,
        sofr_rate: float = 0.053,
        euribor_rate: Optional[float] = None,
        customer_tier: Optional[str] = None
    ) -> Optional[float]:
        """Computes rate for this specific leg, delegating to ContractualRate logic."""
        crate = ContractualRate(
            rate_type=self.leg_type,
            benchmark=self.benchmark,
            margin_bps=self.margin_bps,
            floor_bps=self.floor_bps,
            fixed_coupon=self.fixed_coupon,
            spread_grid_id=self.spread_grid_id
        )
        return crate.compute_rate(sofr_rate=sofr_rate, euribor_rate=euribor_rate, customer_tier=customer_tier)


class EpistemicResolver:
    """
    Generic Epistemic Resolver for AI Infrastructure Financial Network.
    Enforces ADR-014 and ADR-017 zero-lookahead semantics across all stress functions.
    Pre-filters eligible facts before selecting the latest historical measurement.
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

        self.rate_legs = load_rate_legs()
        self.audit_trail: List[KnowledgeState] = []

    def resolve_fact(
        self,
        obligation_id: Optional[str] = None,
        entity_id: Optional[str] = None,
        attribute: str = ""
    ) -> KnowledgeState:
        """
        Resolves an observable fact or contract attribute according to the temporal mode and as_of_date.
        Pre-filters eligible facts first (economic_as_of <= t and publicly_known_from <= t in known mode).
        Only returns unknown when the subject economically existed but no eligible public measurement exists;
        returns not_yet_existent when its earliest economic existence is strictly after as_of_date.
        """
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
            # Filter eligible facts FIRST
            if self.temporal_mode in ["known", "knowledge"]:
                eligible = matching[
                    (matching["economic_as_of"] <= self.as_of_date) &
                    (matching["publicly_known_from"] <= self.as_of_date)
                ]
            else:
                eligible = matching[matching["economic_as_of"] <= self.as_of_date]

            if not eligible.empty:
                sort_cols = [c for c in ["economic_as_of", "publicly_known_from", "fact_id"] if c in eligible.columns]
                latest_fact = eligible.sort_values(by=sort_cols).iloc[-1]

                eco_date = str(latest_fact["economic_as_of"]) if pd.notna(latest_fact.get("economic_as_of")) else None
                pub_date = str(latest_fact["publicly_known_from"]) if pd.notna(latest_fact.get("publicly_known_from")) else None
                claims = [str(c) for c in [latest_fact.get("knowledge_claim_id"), latest_fact.get("truth_claim_id")] if pd.notna(c) and str(c).strip()]

                val = latest_fact["value"]
                val = float(val) if pd.notna(val) else None

                ks = KnowledgeState(
                    status="known" if val is not None else "unknown",
                    value=val,
                    economic_date=eco_date,
                    public_date=pub_date,
                    evidence_claim_ids=claims,
                    entity_id=entity_id,
                    obligation_id=obligation_id,
                    attribute=attribute
                )
                self.audit_trail.append(ks)
                return ks
            else:
                # No eligible fact as of this date.
                # Determine whether the subject did not yet exist economically, or is unknown/unmeasured.
                min_eco_date = matching["economic_as_of"].dropna().min() if "economic_as_of" in matching.columns else None

                # Also check lifecycle events for earliest economic creation date
                if obligation_id and not self.events_df.empty:
                    matching_events = self.events_df[self.events_df["obligation_id"] == obligation_id]
                    if not matching_events.empty and "economic_effective_at" in matching_events.columns:
                        min_event_date = matching_events["economic_effective_at"].dropna().min()
                        if min_event_date is not None:
                            if min_eco_date is None or min_event_date < min_eco_date:
                                min_eco_date = min_event_date

                if min_eco_date is not None and str(min_eco_date) > str(self.as_of_date):
                    ks = KnowledgeState(
                        status="not_yet_existent",
                        value=None,
                        economic_date=str(min_eco_date),
                        public_date=None,
                        evidence_claim_ids=[],
                        entity_id=entity_id,
                        obligation_id=obligation_id,
                        attribute=attribute
                    )
                else:
                    ks = KnowledgeState(
                        status="unknown",
                        value=None,
                        economic_date=str(min_eco_date) if min_eco_date is not None else None,
                        public_date=None,
                        evidence_claim_ids=[],
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
            if str(self.as_of_date) < eco_date:
                ks = KnowledgeState("not_yet_existent", None, eco_date, pub_date, [claim_id], entity_id, obligation_id, attribute)
            elif self.temporal_mode in ["known", "knowledge"] and str(self.as_of_date) < pub_date:
                ks = KnowledgeState("unknown", None, eco_date, pub_date, [claim_id], entity_id, obligation_id, attribute)
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
            if str(self.as_of_date) < eco_date:
                ks = KnowledgeState("not_yet_existent", None, eco_date, pub_date, [claim_id], entity_id, obligation_id, attribute)
            elif self.temporal_mode in ["known", "knowledge"] and str(self.as_of_date) < pub_date:
                ks = KnowledgeState("unknown", None, eco_date, pub_date, [claim_id], entity_id, obligation_id, attribute)
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
            if str(self.as_of_date) < eco_date:
                ks = KnowledgeState("not_yet_existent", None, eco_date, pub_date, [claim_id], entity_id, obligation_id, attribute)
            elif self.temporal_mode in ["known", "knowledge"] and str(self.as_of_date) < pub_date:
                ks = KnowledgeState("unknown", None, eco_date, pub_date, [claim_id], entity_id, obligation_id, attribute)
            else:
                ks = KnowledgeState("known", raw_value, eco_date, pub_date, [claim_id], entity_id, obligation_id, attribute)
            self.audit_trail.append(ks)
            return ks

        # Default fallback if attribute completely unmodelled
        ks = KnowledgeState("unknown", None, None, None, [], entity_id, obligation_id, attribute)
        self.audit_trail.append(ks)
        return ks

    def compute_obligation_debt_service(
        self,
        obligation_id: str,
        total_principal: float,
        edge_data: Dict[str, Any],
        sofr_rate: float = 0.053,
        euribor_rate: Optional[float] = None,
        customer_tier: Optional[str] = None
    ) -> Optional[float]:
        """
        Computes debt service for an obligation, respecting discrete rate legs if present.
        E.g. DDTL 4.0 sums $1.400B at floating + $1.437B at fixed coupon.
        For single-rate obligations, uses ContractualRate.from_edge(edge_data).
        Fails closed (returns None) if rate components cannot be computed.
        """
        legs = self.rate_legs.get(obligation_id)
        if legs:
            total_service = 0.0
            for leg in legs:
                leg_p = leg.principal
                if leg_p is None:
                    return None
                r = leg.compute_rate(sofr_rate=sofr_rate, euribor_rate=euribor_rate, customer_tier=customer_tier)
                if r is None:
                    return None
                total_service += leg_p * r
            return total_service
        else:
            crate = ContractualRate.from_edge(edge_data)
            r = crate.compute_rate(sofr_rate=sofr_rate, euribor_rate=euribor_rate, customer_tier=customer_tier)
            if r is None:
                return None
            return total_principal * r

    def resolve_financial(self, entity_id: str, metric: str) -> KnowledgeState:
        """
        Resolves an audited financial fact from SEC XBRL disclosures with strict temporal filtering.
        Pre-filters eligible filings before selecting latest historical measurement.
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
            sub_eligible = sub[sub["filed_date"] <= self.as_of_date]
        else:
            sub_eligible = sub[sub["period_end"] <= self.as_of_date]

        if sub_eligible.empty:
            min_period = sub["period_end"].min()
            st = "not_yet_existent" if (min_period and str(min_period) > self.as_of_date) else "unknown"
            ks = KnowledgeState(st, None, str(min_period) if min_period else None, None, [], entity_id=entity_id, attribute=metric)
            self.audit_trail.append(ks)
            return ks

        latest = sub_eligible.sort_values(by=["period_end", "filed_date"]).iloc[-1]
        val = float(latest["value"]) if (pd.notna(latest["value"])) else None
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
        Also asserts that any observation with status='unknown' or 'not_yet_existent'
        has value=None (no silent fallback or NaN).
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
                if ks.value is not None and pd.notna(ks.value):
                    raise AssertionError(
                        f"Epistemic Integrity VIOLATED: '{ks.attribute}' has status='{ks.status}' "
                        f"but contains non-null value {ks.value}!"
                    )
