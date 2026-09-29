"""
Parameterized Financial Stress and Contagion Simulation Prototype (Phase 0.7.1 Refactor)
Simulates contract-calibrated transmission functions across balance sheets and obligations:
1. Hypothetical MTM Financing Sensitivity (71.42% Funding-Ratio Proxy): Evaluates secondary GPU collateral haircuts
   against a 71.42% advance rate proxy, while explicitly clarifying DDTL 5.0 contractual reality (71.42% of capex cost, 6-yr depreciation).
2. Anchor Customer Concentration & Conditional Springing Guaranty: Evaluates Microsoft recognized revenue ($3.44B),
   establishing an explicit Springing Events Predicate Engine (Events i, ii, iii, iv, up to 9 event groups under Exhibit 10.1 & 10.2)
   and modeling the conditional join ($4.13B ELN-03 / $6.88B total springing guarantees, excluding Building 4).
3. Interest Rate Transmission Split:
   a) SOFR Base Rate Shock: Immediate cash impact on unhedged floating debt anchored in reported $4.661B swap notional
      (Note 8) alongside contractual covenants (>=95% on DDTL 4.0 and 5.0; DDTL 1-3 hedge ratios undisclosed), providing an explicit sensitivity band ($32.6M to $309.2M/yr).
   b) Credit Spread / Refinancing Shock at Maturity: Evaluates refinancing penalties as scheduled debt principal matures ($10.60B across 2026-2027),
      with an exposed rollover fraction parameter.
4. Phased Grid Energization Delay at Polaris Forge 1: Models Building 2 (100 MW operating), Building 3 (150 MW partially operating with parameterized
   Class C operational estimate), and Building 4 (150 MW construction), evaluating a sensitivity band across 25 to 100 MW.
5. OEM Purchase Commitment Expected Loss (SMCI): Explicitly separates the Accounting Channel (non-cash $2.05B NRV loss provision reducing equity)
   from the Cash Liquidity Channel (working capital inventory cash drain vs cancellation settlement fee with exposed parameter).
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

try:
    from .graph import ObligationNetwork
except ImportError:
    from graph import ObligationNetwork

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"


class FinancialStressEngine:
    def __init__(self, network: Optional[ObligationNetwork] = None):
        self.network = network or ObligationNetwork()
        self.graph = self.network.graph
        self.financials = self._load_latest_financials()

    def _load_latest_financials(self) -> Dict[str, Dict[str, float]]:
        """Load latest audited balance sheet and flow metrics per entity from SEC XBRL facts."""
        df = pd.read_parquet(PROCESSED_DIR / "financials.parquet")
        instant = (
            df[df["duration_type"] == "instant"]
            .sort_values(by=["entity_id", "metric", "period_end", "filed_date"])
            .groupby(["entity_id", "metric"])
            .last()
            .reset_index()
        )
        p_inst = instant.pivot(index="entity_id", columns="metric", values="value")

        flows = (
            df[df["duration_type"].isin(["annual", "quarterly"])]
            .sort_values(by=["entity_id", "metric", "period_end", "filed_date"])
            .groupby(["entity_id", "metric"])
            .last()
            .reset_index()
        )
        p_flow = flows.pivot(index="entity_id", columns="metric", values="value")

        fin_dict = {}
        for entity in ["CRWV", "APLD", "SMCI", "NVDA", "ORCL", "MSFT"]:
            cash = p_inst.loc[entity, "cash_and_equivalents"] if entity in p_inst.index and "cash_and_equivalents" in p_inst.columns else 0.0
            debt = p_inst.loc[entity, "total_debt"] if entity in p_inst.index and "total_debt" in p_inst.columns else 0.0
            leases = p_inst.loc[entity, "operating_lease_liabilities"] if entity in p_inst.index and "operating_lease_liabilities" in p_inst.columns else 0.0
            ocf = p_flow.loc[entity, "operating_cash_flow"] if entity in p_flow.index and "operating_cash_flow" in p_flow.columns else 0.0
            rev = p_flow.loc[entity, "revenue"] if entity in p_flow.index and "revenue" in p_flow.columns else 0.0

            fin_dict[entity] = {
                "cash_and_equivalents": float(cash),
                "total_debt": float(debt),
                "operating_lease_liabilities": float(leases),
                "operating_cash_flow": float(ocf),
                "revenue": float(rev)
            }
        return fin_dict

    def simulate_gpu_collateral_haircut(self, haircut_pct: float = 0.40, funding_ratio_proxy: float = 0.7142) -> Dict[str, Any]:
        """
        Scenario 1: Hypothetical MTM Financing Sensitivity (71.42% Funding-Ratio Proxy)
        Evaluates CoreWeave's drawn DDTLs ($10.806B recourse) under a hypothetical secondary appraisal haircut.
        NOTE: Contractually, DDTL 5.0 (Exhibit 10.1) defines 71.42% as the Funding Date GPU Amount against capex acquisition cost
        with straight-line 6-year depreciation, NOT an ongoing secondary mark-to-market appraisal covenant.
        This scenario models a hypothetical refinancing tightening using the 71.42% funding ratio as an analytical proxy (Class C).
        """
        drawn_ddtl_keys = [
            "OBL-CRWV-DEBT-DDTL1", "OBL-CRWV-DEBT-DDTL2", "OBL-CRWV-DEBT-DDTL2-1",
            "OBL-CRWV-DEBT-DDTL3", "OBL-CRWV-DEBT-DDTL5"
        ]
        drawn_debt = 0.0
        for k in drawn_ddtl_keys:
            if self.graph.has_edge("CRWV", "BLACKSTONE_MAGNETAR_SYN", key=k):
                drawn_debt += self.graph.get_edge_data("CRWV", "BLACKSTONE_MAGNETAR_SYN", key=k).get("amount", 0.0)

        if drawn_debt == 0.0:
            drawn_debt = 10806000000.0

        # Baseline implied asset base to support drawn debt at funding ratio
        base_asset_value = drawn_debt / funding_ratio_proxy  # ~$15.130B
        stressed_asset_value = base_asset_value * (1.0 - haircut_pct)  # ~$9.078B
        allowable_capacity = stressed_asset_value * funding_ratio_proxy  # ~$6.484B

        modeled_refinancing_gap = max(0.0, drawn_debt - allowable_capacity)  # ~$4.322B
        crwv_cash = self.financials.get("CRWV", {}).get("cash_and_equivalents", 5520000000.0)
        # Note: Under DDTL 5.0 Credit Agreement Section 2.05, secondary market price declines do NOT trigger
        # an automated mandatory cash margin call or prepayment. Cash remains intact at $5.52B.
        gap_to_cash_pct = (modeled_refinancing_gap / crwv_cash) * 100.0 if crwv_cash else 0.0

        return {
            "scenario_name": "Hypothetical MTM Financing Sensitivity (Class C Proxy)",
            "haircut_pct": haircut_pct,
            "funding_ratio_proxy": funding_ratio_proxy,
            "drawn_ddtl_debt_usd": drawn_debt,
            "base_asset_value_usd": base_asset_value,
            "stressed_asset_value_usd": stressed_asset_value,
            "allowable_capacity_usd": allowable_capacity,
            "modeled_refinancing_gap_usd": modeled_refinancing_gap,
            "direct_cash_hit_usd": 0.0,  # Zero contractual mandatory cash prepayment
            "crwv_starting_cash_usd": crwv_cash,
            "crwv_cash_after_scenario_usd": crwv_cash,  # Cash intact
            "modeled_gap_to_cash_pct": round(gap_to_cash_pct, 1),
            "contractual_caveat": (
                "Under Exhibit 10.1 and Section 2.05 of the DDTL 5.0 Credit Agreement, debt sizing is tied to Funding Date Capex (cost) "
                "with straight-line 6-year depreciation, and mandatory prepayments govern asset sales, debt issuances, and defaults—not an automatic "
                "secondary market mark-to-market appraisal margin call. This $4.32B gap is an analytical sensitivity proxy (Class C) measuring "
                "refinancing capacity contraction rather than a contractual cash call."
            ),
            "transmission_narrative": (
                f"Applying a {int(haircut_pct*100)}% secondary market haircut against the 71.42% funding-ratio proxy models a "
                f"${modeled_refinancing_gap/1e9:.2f}B refinancing-capacity contraction across CoreWeave's ${drawn_debt/1e9:.2f}B in recourse DDTLs. "
                f"Under the Credit Agreement, this decline does NOT trigger an automatic contractual cash margin call or prepayment (cash remains ${crwv_cash/1e9:.2f}B), "
                f"but it eliminates borrowing availability on undrawn commitments and represents severe rollover friction upon loan maturity."
            )
        }

    def simulate_anchor_customer_trim(self, trim_pct: float = 0.30) -> Dict[str, Any]:
        """
        Scenario 2: Anchor Customer Demand Trim & Conditional Springing Guaranty
        Models a demand trim to Microsoft recognized revenue ($3.438B base), evaluating the literal legal
        predicates of the Unconditional Springing Guaranty (APLD Form 10-K Exhibit 10.1 and 10.2).
        
        Predicate Engine:
        - Predicate A (Customer Identity): Conditioned on Microsoft being the Colocation Customer at SPV VIII (Building ELN-03).
        - Predicate B (Contractual Default): Conditioned on the trim giving rise to a payment cessation, reduction, or termination (Springing Event ii).
        - Scope: Springing guarantees specifically cover Building 3 (150 MW assigned to SPV, carrying an inferred Class C reference proxy of $4.13B)
          and Building 2 SPV lease (Phase 2/4 Space, 2 of 4 data halls; unstated face value in Exhibit 10.1).
          Building 4 (150 MW, ~$4.13B) carries no CoreWeave parent springing guarantee (guaranteed by APLD parent).
        """
        base_revenue = 3437770000.0
        if self.graph.has_edge("MSFT", "CRWV", key="REL-MSFT-CRWV-REVENUE-CONCENTRATION"):
            base_revenue = self.graph.get_edge_data("MSFT", "CRWV", key="REL-MSFT-CRWV-REVENUE-CONCENTRATION").get("amount", 3437770000.0)

        annual_rev_loss = base_revenue * trim_pct  # $1.031B/yr at 30%

        # CoreWeave annual debt service across all funded tranches ($35.551B total):
        annual_debt_service = (
            10806000000.0 * 0.085 + 2837000000.0 * 0.075 + 10029000000.0 * 0.095 +
            6588000000.0 * 0.01875 + 4220000000.0 * 0.11 + 882000000.0 * 0.10
        )  # ~$2.76B/yr
        # Polaris Forge 1 lease rent: $11.0B / 15 years = $733.3M/yr fully energized (~$275.0M/yr operational 150 MW)
        annual_full_lease_rent = 11000000000.0 / 15.0
        operational_lease_rent = annual_full_lease_rent * (150.0 / 400.0)

        total_annual_commitments = annual_debt_service + annual_full_lease_rent  # ~$3.49B/yr
        crwv_cash = self.financials.get("CRWV", {}).get("cash_and_equivalents", 5520000000.0)

        # Springing Guarantees Scope:
        # Legal terms cover Base Rent, Additional Rent, charges, and performance obligations under SPV leases (uncapped fixed face value).
        # Class C reference exposure proxy for Building 3 (150 MW / 400 MW * $11.0B): ~$4.125B.
        eln03_reference_proxy_usd = 4125000000.0

        coverage_ratio = crwv_cash / total_annual_commitments

        return {
            "scenario_name": "Anchor Customer Demand Trim & Conditional Springing Guaranty",
            "trim_pct": trim_pct,
            "anchor_customer": "MSFT",
            "base_recognized_revenue_usd": base_revenue,
            "annual_revenue_loss_usd": annual_rev_loss,
            "crwv_annual_debt_service_usd": annual_debt_service,
            "polaris_forge_full_rent_usd": annual_full_lease_rent,
            "polaris_forge_operational_rent_usd": operational_lease_rent,
            "total_fixed_commitments_usd": total_annual_commitments,
            "crwv_cash_buffer_usd": crwv_cash,
            "coverage_years": round(coverage_ratio, 2),
            "eln03_reference_proxy_usd": eln03_reference_proxy_usd,
            "springing_event_analyzed": "Springing Event (ii) - Colocation Agreement Payment Cessation or Material Reduction",
            "conditional_join_status": "Conditional: requires Microsoft to be the specific Colocation Customer at Building ELN-03",
            "transmission_narrative": (
                f"A {int(trim_pct*100)}% demand trim on Microsoft's recognized revenue reduces CoreWeave's cash inflow by ${annual_rev_loss/1e9:.2f}B/yr. "
                f"Against ${total_annual_commitments/1e9:.2f}B in annual debt service and facility commitments, if Microsoft is the Colocation Customer "
                f"at SPV VIII (Building ELN-03) and reduces colocation payments, this fulfills the literal predicate of Springing Event (ii) under Exhibit 10.2, "
                f"conditionally activating CoreWeave parent's Unconditional Springing Guaranty on Building ELN-03 (carrying a Class C reference proxy of ${eln03_reference_proxy_usd/1e9:.2f}B) "
                f"and potentially Exhibit 10.1 for the Building 2 SPV lease (Phase 2/4 Space, 2 of 4 data halls; unstated face value). "
                f"Building 4 ($4.13B, 150 MW) is excluded as it carries no CoreWeave parent guarantee."
            )
        }

    def simulate_sofr_base_rate_shock(self, sofr_increase_bps: float = 300.0, as_of_date: str = "2026-05-31") -> Dict[str, Any]:
        """
        Scenario 3A: SOFR Benchmark Base Rate Shock (+300 bps)
        Rigorously evaluates immediate cash interest impact across floating debt facilities:
        - DDTL 1-3 ($9.705B floating): hedge ratio undisclosed in SEC disclosures.
        - DDTL 4.0 ($1.400B floating component): covenants >=95% interest rate hedge coverage within specified periods.
        - DDTL 5.0 ($1.101B floating): covenants >=95% interest rate swap coverage under Section 5.14.
        Total Floating Debt = $12.206B.
        Reported active interest rate swap notional (Note 8): $4.661B.
        Unhedged floating debt at June 30, 2026: $12.206B - $4.661B = $7.545B.
        Provides a sensitivity band from hypothetical 95% full fleet coverage ($27.3M/yr) to reported swaps baseline ($235.4M/yr)
        to minimal covenanted coverage with others unhedged ($303.9M/yr).
        Temporally parameterizes Applied Digital's $300M bridge facility: active as of May 31, 2026 snapshot ($9.0M/yr),
        refinanced on June 16, 2026 into 7% fixed notes ($0.0M/yr post-refinancing).
        """
        delta_r = sofr_increase_bps / 10000.0  # 0.03

        # Floating debt tranches
        crwv_ddtl_1_to_3_floating = 1300000000.0 + 3190000000.0 + 3000000000.0 + 2215000000.0  # $9.705B
        crwv_ddtl_4_floating = 1400000000.0  # $1.400B floating component of DDTL 4.0
        crwv_ddtl_5_floating = 1101000000.0  # $1.101B floating
        total_crwv_floating = crwv_ddtl_1_to_3_floating + crwv_ddtl_4_floating + crwv_ddtl_5_floating  # $12.206B

        # Reported balance sheet swap notional (CRWV 10-Q Note 8)
        reported_swap_notional = 4661000000.0  # $4.661B active interest rate swaps
        unhedged_reported_baseline = max(0.0, total_crwv_floating - reported_swap_notional)  # $7.545B

        # APLD floating bridge facility ($300.0M principal at May 31, 2026)
        # On June 16, 2026 (subsequent event), APLD refinanced the bridge facility into $1.59B 7.00% fixed notes.
        apld_floating_debt = 300000000.0 if as_of_date < "2026-06-16" else 0.0

        # 1. Reported Swaps Baseline Hit
        crwv_reported_hit = unhedged_reported_baseline * delta_r  # $226.35M/yr
        apld_hit = apld_floating_debt * delta_r                   # $9.00M/yr (May 31) or $0.0 (post June 16)
        network_reported_hit = crwv_reported_hit + apld_hit       # $235.35M/yr (May 31) or $226.35M/yr (post June 16)

        # 2. Covenanted Minimum Only (DDTL 4 & 5 at 95%, DDTL 1-3 unhedged)
        covenanted_swaps_only = (crwv_ddtl_4_floating * 0.95) + (crwv_ddtl_5_floating * 0.95)  # $2.376B
        unhedged_covenanted_only = total_crwv_floating - covenanted_swaps_only                  # $9.830B
        crwv_covenanted_only_hit = unhedged_covenanted_only * delta_r                          # $294.90M/yr
        network_covenanted_only_hit = crwv_covenanted_only_hit + apld_hit                      # $303.90M/yr

        # 3. Hypothetical Maximum Hedging (95% across all floating debt)
        unhedged_full_95 = total_crwv_floating * 0.05                                          # $610.3M
        crwv_full_95_hit = unhedged_full_95 * delta_r                                          # $18.31M/yr
        network_full_95_hit = crwv_full_95_hit + apld_hit                                      # $27.31M/yr

        crwv_cash = self.financials.get("CRWV", {}).get("cash_and_equivalents", 5520000000.0)
        apld_cash = self.financials.get("APLD", {}).get("cash_and_equivalents", 1590000000.0)

        return {
            "scenario_name": "SOFR Base Rate Shock (Reported Swaps vs Covenanted Range)",
            "sofr_increase_bps": sofr_increase_bps,
            "as_of_date": as_of_date,
            "total_crwv_floating_debt_usd": total_crwv_floating,
            "crwv_reported_swap_notional_usd": reported_swap_notional,
            "crwv_unhedged_floating_reported_usd": unhedged_reported_baseline,
            "crwv_cash_drain_reported_baseline_usd": crwv_reported_hit,
            "apld_floating_debt_may31_snapshot_usd": 300000000.0,
            "apld_floating_debt_post_refinancing_usd": 0.0,
            "apld_cash_drain_usd": apld_hit,
            "network_cash_drain_reported_baseline_usd": network_reported_hit,
            "network_cash_drain_may31_snapshot_usd": crwv_reported_hit + 9000000.0,
            "network_cash_drain_post_refinancing_usd": crwv_reported_hit,
            "network_cash_drain_full_95_hypothetical_usd": network_full_95_hit,
            "network_cash_drain_covenanted_only_usd": network_covenanted_only_hit,
            "crwv_cash_usd": crwv_cash,
            "apld_cash_usd": apld_cash,
            "transmission_narrative": (
                f"A +{int(sofr_increase_bps)} bps SOFR increase adds ${apld_hit/1e6:.1f}M/yr to Applied Digital's $300.0M floating bridge facility "
                f"under its May 31, 2026 balance sheet snapshot (which was refinanced on June 16, 2026 into 7.00% fixed notes, eliminating APLD floating rate exposure). "
                f"For CoreWeave, contractual 95% hedge covenants apply specifically to DDTL 4.0 and DDTL 5.0 ($2.50B floating combined), "
                f"while DDTLs 1.0-3.0 ($9.71B) carry no disclosed 95% hedge mandate. Anchored on CoreWeave's audited $4.66B interest rate swap notional (Note 8), "
                f"$7.55B in floating debt remains unhedged, creating a ${crwv_reported_hit/1e6:.1f}M/yr cash drain at CoreWeave and ${network_reported_hit/1e6:.1f}M/yr "
                f"across the network ({'$235.4M/yr at May 31, 2026 snapshot vs $226.4M/yr post-refinancing'}). Sensitivity analysis reveals a network impact range of "
                f"${network_full_95_hit/1e6:.1f}M/yr (if 95% hedged fleet-wide) to ${network_covenanted_only_hit/1e6:.1f}M/yr (if only DDTL 4/5 are hedged)."
            )
        }

    def simulate_refinancing_spread_shock(self, spread_increase_bps: float = 300.0, refi_rollover_fraction: float = 1.0) -> Dict[str, Any]:
        """
        Scenario 3B: Credit Spread / Refinancing Shock at Maturity (+300 bps)
        Evaluates the refinancing penalty when scheduled debt principal rolls over into higher secondary credit spreads.
        Uses CoreWeave's audited debt maturities table (CRWV 10-Q Note 7):
        - 2026 remainder: $4,413M ($4.413B)
        - 2027: $6,184M ($6.184B)
        - 2028: $4,416M ($4.416B)
        - 3-Year Total Scheduled Principal: $15.013B
        NOTE: These reflect contractual scheduled principal payments (including amortizations), not purely unamortized bullet maturities.
        The refi_rollover_fraction (default 1.0) parameterizes the portion that must be refinanced into debt rather than retired from cash.
        """
        delta_spread = spread_increase_bps / 10000.0  # 0.03
        maturing_2026 = 4413000000.0
        maturing_2027 = 6184000000.0
        maturing_2028 = 4416000000.0

        refi_cost_2026_yr = maturing_2026 * refi_rollover_fraction * delta_spread  # $132.39M/yr at 1.0
        refi_cost_2027_yr = maturing_2027 * refi_rollover_fraction * delta_spread  # $185.52M/yr at 1.0
        refi_cost_2028_yr = maturing_2028 * refi_rollover_fraction * delta_spread  # $132.48M/yr at 1.0

        cumulative_refi_cost_2yr = refi_cost_2026_yr + refi_cost_2027_yr  # $317.91M/yr
        cumulative_refi_cost_3yr = cumulative_refi_cost_2yr + refi_cost_2028_yr  # $450.39M/yr

        # Sensitivity across rollover fractions [0.50, 0.75, 1.00]
        sensitivity_2yr = {
            "50pct_rollover_usd": cumulative_refi_cost_2yr * 0.50,
            "75pct_rollover_usd": cumulative_refi_cost_2yr * 0.75,
            "100pct_rollover_usd": cumulative_refi_cost_2yr * 1.00,
        }

        crwv_cash = self.financials.get("CRWV", {}).get("cash_and_equivalents", 5520000000.0)

        return {
            "scenario_name": "Credit Spread / Refinancing Shock at Maturity",
            "spread_increase_bps": spread_increase_bps,
            "refi_rollover_fraction": refi_rollover_fraction,
            "crwv_maturing_2026_usd": maturing_2026,
            "crwv_maturing_2027_usd": maturing_2027,
            "crwv_maturing_2028_usd": maturing_2028,
            "crwv_refi_annual_penalty_2026_usd": refi_cost_2026_yr,
            "crwv_refi_annual_penalty_2027_usd": refi_cost_2027_yr,
            "crwv_refi_cumulative_penalty_2yr_usd": cumulative_refi_cost_2yr,
            "crwv_refi_cumulative_penalty_3yr_usd": cumulative_refi_cost_3yr,
            "refinancing_sensitivity_2yr": sensitivity_2yr,
            "crwv_starting_cash_usd": crwv_cash,
            "transmission_narrative": (
                f"Existing contractual fixed and floating spreads do not adjust immediately to secondary market credit spreads. "
                f"However, CoreWeave faces ${maturing_2026/1e9:.2f}B in 2026 scheduled debt principal and ${maturing_2027/1e9:.2f}B in 2027 ($10.60B across 24 months). "
                f"Assuming a {int(refi_rollover_fraction*100)}% rollover fraction, refinancing this scheduled debt under a +{int(spread_increase_bps)} bps market credit spread shock "
                f"imposes an incremental ${cumulative_refi_cost_2yr/1e6:.1f}M/year in debt service by 2027 (range: ${sensitivity_2yr['50pct_rollover_usd']/1e6:.1f}M at 50% rollover "
                f"to ${cumulative_refi_cost_2yr/1e6:.1f}M at 100%), and ${cumulative_refi_cost_3yr/1e6:.1f}M/year through 2028."
            )
        }

    def simulate_grid_energization_delay(self, delay_months: int = 12, building3_operational_mw: float = 50.0) -> Dict[str, Any]:
        """
        Scenario 4: Phased Grid Energization Delay at Polaris Forge 1
        Models building-level operational phasing (APLD 10-K Item 1):
        - Building 2 (ELN-02): 100 MW — fully operational ($183.3M/yr base rent ongoing).
        - Building 3 (ELN-03): 150 MW — partially operational (parameterized via building3_operational_mw, default 50.0 MW Class C proxy).
        - Building 4: 150 MW — under active construction / design.
        Total: operational_mw vs delayed_mw (400 MW total campus).
        Carrying cost on construction debt uses modeled Class C MW-allocation ($2.35B notes * delayed_mw / 400).
        Evaluates a sensitivity band across building3_operational_mw in [25, 50, 75, 100] MW.
        """
        total_mw = 400.0
        operational_mw = 100.0 + building3_operational_mw
        delayed_mw = total_mw - operational_mw
        annual_full_rent = 11000000000.0 / 15.0  # $733.3M/yr

        ongoing_operational_rent = annual_full_rent * (operational_mw / total_mw)
        deferred_expansion_rent = annual_full_rent * (delayed_mw / total_mw) * (delay_months / 12.0)

        # Carrying cost on Polaris Forge 1 debt ($2.35B 9.25% notes):
        construction_phase_debt = 2350000000.0 * (delayed_mw / total_mw)
        apld_construction_carrying_cost = construction_phase_debt * 0.0925 * (delay_months / 12.0)

        apld_cash = self.financials.get("APLD", {}).get("cash_and_equivalents", 1590000000.0)
        cash_drain_pct = (apld_construction_carrying_cost / apld_cash) * 100.0 if apld_cash else 100.0

        # Sensitivity band across Building 3 operational MW [25, 50, 75, 100]
        sensitivity_band = {}
        for b3_cand in [25.0, 50.0, 75.0, 100.0]:
            cand_del = total_mw - (100.0 + b3_cand)
            cand_cost = 2350000000.0 * (cand_del / total_mw) * 0.0925 * (delay_months / 12.0)
            cand_drain = (cand_cost / apld_cash) * 100.0 if apld_cash else 100.0
            sensitivity_band[f"{int(b3_cand)}MW_live"] = {
                "carrying_cost_usd": cand_cost,
                "cash_drain_pct": round(cand_drain, 1)
            }

        return {
            "scenario_name": "Phased Grid Energization Delay (Polaris Forge 1)",
            "delay_months": delay_months,
            "building3_operational_mw": building3_operational_mw,
            "project": "POLARIS_FORGE_1",
            "operational_mw": operational_mw,
            "delayed_mw": delayed_mw,
            "ongoing_operational_rent_usd": ongoing_operational_rent,
            "deferred_expansion_rent_usd": deferred_expansion_rent,
            "construction_phase_debt_modeled_usd": construction_phase_debt,
            "apld_debt_carrying_cost_usd": apld_construction_carrying_cost,
            "apld_starting_cash_usd": apld_cash,
            "apld_cash_drain_pct": round(cash_drain_pct, 1),
            "sensitivity_band": sensitivity_band,
            "debt_allocation_flag": "Class C (modeled MW allocation; not contractual debt tranche)",
            "transmission_narrative": (
                f"A {delay_months}-month grid delay defers ${deferred_expansion_rent/1e6:.1f}M in expansion rent across the unenergized {int(delayed_mw)} MW. "
                f"However, the ~{int(operational_mw)} MW operational capacity (Building 2 100 MW + Building 3 {int(building3_operational_mw)} MW Class C proxy) "
                f"generates ${ongoing_operational_rent/1e6:.1f}M/yr in ongoing base rent. Applied Digital's modeled construction carrying cost on the delayed phase is "
                f"${apld_construction_carrying_cost/1e6:.1f}M, consuming {cash_drain_pct:.1f}% of its ${apld_cash/1e9:.2f}B cash reserves. "
                f"Sensitivity analysis across 25MW to 100MW live in Building 3 yields an APLD cash drain range of "
                f"{sensitivity_band['100MW_live']['cash_drain_pct']}% (${sensitivity_band['100MW_live']['carrying_cost_usd']/1e6:.1f}M) to "
                f"{sensitivity_band['25MW_live']['cash_drain_pct']}% (${sensitivity_band['25MW_live']['carrying_cost_usd']/1e6:.1f}M)."
            )
        }

    def simulate_oem_purchase_commitment_markdown(
        self,
        excess_allocation_pct: float = 0.15,
        modeled_recovery_haircut: float = 0.40,
        cancellation_fee_rate: float = 0.15
    ) -> Dict[str, Any]:
        """
        Scenario 5: Hardware Supply Chain Purchase Commitment Expected Loss
        Rigorously separates:
        1. Accounting Channel (P&L / Equity): Non-cash Net Realizable Value (NRV) write-down provision under ASC 330.
        2. Cash Liquidity Channel: Working capital cash drain if taking delivery of unabsorbed inventory vs cancellation penalty.
        """
        total_commitments = 34200000000.0
        excess_commitments = total_commitments * excess_allocation_pct  # $5.13B excess hardware allocation
        
        # 1. Accounting Channel: Non-cash P&L write-down reducing stockholders' equity ($9.34B equity as of June 30, 2026)
        modeled_nrv_provision = excess_commitments * modeled_recovery_haircut  # $2.052B non-cash pre-tax charge
        
        # 2. Cash Liquidity Channel:
        # A) Cancellation Settlement Fee (parameterized by cancellation_fee_rate, default 15%): $769.5M cash drain
        modeled_cancellation_cash_drain = excess_commitments * cancellation_fee_rate  # $769.5M
        # B) Gross Inventory Delivery (taking full physical delivery of excess racks into working capital): $5.13B cash drain
        gross_inventory_cash_drain = excess_commitments  # $5.13B

        smci_cash = self.financials.get("SMCI", {}).get("cash_and_equivalents", 7520000000.0)
        cancellation_cash_drain_pct = (modeled_cancellation_cash_drain / smci_cash) * 100.0 if smci_cash else 100.0
        gross_delivery_cash_drain_pct = (gross_inventory_cash_drain / smci_cash) * 100.0 if smci_cash else 100.0

        return {
            "scenario_name": "OEM Purchase Commitment Expected Loss (SMCI)",
            "excess_allocation_pct": excess_allocation_pct,
            "modeled_recovery_haircut": modeled_recovery_haircut,
            "cancellation_fee_rate": cancellation_fee_rate,
            "target_entity": "SMCI",
            "total_purchase_commitments_usd": total_commitments,
            "excess_commitments_usd": excess_commitments,
            "accounting_nrv_write_down_usd": modeled_nrv_provision,
            "cancellation_settlement_cash_drain_usd": modeled_cancellation_cash_drain,
            "gross_delivery_cash_drain_usd": gross_inventory_cash_drain,
            "smci_starting_cash_usd": smci_cash,
            "cancellation_cash_drain_pct": round(cancellation_cash_drain_pct, 1),
            "gross_delivery_cash_drain_pct": round(gross_delivery_cash_drain_pct, 1),
            "transmission_narrative": (
                f"Under a {int(excess_allocation_pct*100)}% demand pause against Supermicro's ${total_commitments/1e9:.2f}B purchase commitments, "
                f"${excess_commitments/1e9:.2f}B becomes excess inventory allocation. In the Accounting Channel, applying a {int(modeled_recovery_haircut*100)}% "
                f"modeled recovery haircut creates a ${modeled_nrv_provision/1e9:.2f}B non-cash NRV loss provision reducing equity. In the Cash Liquidity Channel, "
                f"a negotiated cancellation settlement at {int(cancellation_fee_rate*100)}% consumes ${modeled_cancellation_cash_drain/1e6:.1f}M ({cancellation_cash_drain_pct:.1f}% of cash), "
                f"whereas taking physical delivery of unabsorbed inventory would consume ${gross_inventory_cash_drain/1e9:.2f}B ({gross_delivery_cash_drain_pct:.1f}% of cash)."
            )
        }

    def run_all_stress_scenarios(self) -> pd.DataFrame:
        """Run complete quantitative stress test suite and generate canonical summary table."""
        res_gpu = self.simulate_gpu_collateral_haircut(haircut_pct=0.40, funding_ratio_proxy=0.7142)
        res_cust = self.simulate_anchor_customer_trim(trim_pct=0.30)
        res_sofr = self.simulate_sofr_base_rate_shock(sofr_increase_bps=300.0)
        res_refi = self.simulate_refinancing_spread_shock(spread_increase_bps=300.0, refi_rollover_fraction=1.0)
        res_grid = self.simulate_grid_energization_delay(delay_months=12, building3_operational_mw=50.0)
        res_oem = self.simulate_oem_purchase_commitment_markdown(excess_allocation_pct=0.15, modeled_recovery_haircut=0.40, cancellation_fee_rate=0.15)

        summary_rows = [
            {
                "scenario_name": res_gpu["scenario_name"],
                "shock_parameter": "-40% GPU Collateral Value",
                "direct_cash_or_collateral_hit_usd": res_gpu["modeled_refinancing_gap_usd"],
                "target_entity": "CRWV",
                "covenant_or_liquidity_impact": f"Cash Intact ($5.52B) / ${res_gpu['modeled_refinancing_gap_usd']/1e9:.2f}B Refinancing Capacity Gap",
                "contagion_mechanism": "Does not trigger automatic cash prepayment under DDTL 5.0 §2.05; creates a $4.32B modeled refinancing gap (Class C proxy) eliminating undrawn capacity."
            },
            {
                "scenario_name": res_cust["scenario_name"],
                "shock_parameter": "-30% Microsoft Off-Take",
                "direct_cash_or_collateral_hit_usd": res_cust["annual_revenue_loss_usd"],
                "target_entity": "CRWV",
                "covenant_or_liquidity_impact": "Springing Guaranty Conditional Activation ($4.13B ELN-03 Class C Proxy / Uncapped Legal Guaranty)",
                "contagion_mechanism": "Reduces revenue by $1.03B; conditionally activates parent Unconditional Springing Guaranty for Building ELN-03 ($4.13B Class C reference proxy) and Building 2 SPV lease (Phase 2/4 Space, 2 of 4 halls; uncapped face value under Exhibit 10.1). Building 4 excluded."
            },
            {
                "scenario_name": res_sofr["scenario_name"],
                "shock_parameter": "+300 bps SOFR Benchmark",
                "direct_cash_or_collateral_hit_usd": res_sofr["network_cash_drain_reported_baseline_usd"],
                "target_entity": "CRWV / APLD",
                "covenant_or_liquidity_impact": "Reported Swaps Cash Drain: $235.4M/yr (Range: $27.3M - $303.9M/yr)",
                "contagion_mechanism": "Audited $4.66B swap notional leaves $7.55B floating unhedged ($226.4M CRWV + $9.0M APLD bridge facility). Sensitivity band: $27.3M (95% full) to $303.9M (covenanted only)."
            },
            {
                "scenario_name": res_refi["scenario_name"],
                "shock_parameter": "+300 bps Credit Spread at Maturity",
                "direct_cash_or_collateral_hit_usd": res_refi["crwv_refi_cumulative_penalty_2yr_usd"],
                "target_entity": "CRWV",
                "covenant_or_liquidity_impact": "$318M/yr Added Refinancing Interest (Range: $159M - $318M/yr)",
                "contagion_mechanism": "Existing spreads unaffected; hits $10.60B scheduled principal across 2026-2027. Refi rollover fraction 1.0 (range: $159M at 50% to $318M at 100%)."
            },
            {
                "scenario_name": res_grid["scenario_name"],
                "shock_parameter": "12-Month Energization Delay",
                "direct_cash_or_collateral_hit_usd": res_grid["apld_debt_carrying_cost_usd"],
                "target_entity": "APLD",
                "covenant_or_liquidity_impact": f"{res_grid['apld_cash_drain_pct']}% Cash Drain (Range: 6.8% - 9.4% across 25-100 MW)",
                "contagion_mechanism": "Defers $458M expansion rent on 250 MW pending, while 150 MW produces $275M base rent; carrying cost is $136M (range: $109M to $149M across 25-100 MW)."
            },
            {
                "scenario_name": res_oem["scenario_name"],
                "shock_parameter": "15% Demand Pullback",
                "direct_cash_or_collateral_hit_usd": res_oem["accounting_nrv_write_down_usd"],
                "target_entity": "SMCI",
                "covenant_or_liquidity_impact": f"{res_oem['cancellation_cash_drain_pct']}% to {res_oem['gross_delivery_cash_drain_pct']}% Cash Drain",
                "contagion_mechanism": "Accounting: $2.05B NRV loss provision on equity. Cash: $769M cancellation fee at 15% (10% cash) or $5.13B delivery (68% cash)."
            }
        ]

        df = pd.DataFrame(summary_rows)
        tables_dir = OUTPUTS_DIR / "tables"
        tables_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(tables_dir / "financial_stress_summary.csv", index=False)
        return df


if __name__ == "__main__":
    engine = FinancialStressEngine()
    df = engine.run_all_stress_scenarios()
    print("=== Parameterized Financial Stress Prototype Results (Phase 0.7.2) ===")
    print(df[["scenario_name", "shock_parameter", "direct_cash_or_collateral_hit_usd", "target_entity", "covenant_or_liquidity_impact"]])
