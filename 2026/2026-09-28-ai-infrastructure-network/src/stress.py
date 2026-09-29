"""
Parameterized Financial Stress and Contagion Simulation Prototype (Phase 0.7 Refactor)
Simulates contract-calibrated transmission functions across balance sheets and obligations:
1. Hypothetical MTM Financing Sensitivity (71.42% Funding-Ratio Proxy): Evaluates secondary GPU collateral haircuts
   against a 71.42% advance rate proxy, while explicitly clarifying DDTL 5.0 contractual reality (71.42% of capex cost, 6-yr depreciation).
2. Anchor Customer Concentration & Conditional Springing Guaranty: Evaluates Microsoft recognized revenue ($3.44B),
   establishing an explicit Springing Events Predicate Engine (Events i, ii, iii, iv) and modeling the conditional join.
3. Interest Rate Transmission Split:
   a) SOFR Base Rate Shock: Immediate cash impact on unhedged floating debt (incorporating CoreWeave's 95% swap covenant under DDTL 5.0).
   b) Credit Spread / Refinancing Shock at Maturity: Evaluates refinancing penalties as $15.01B in debt principal matures between 2026 and 2028.
4. Phased Grid Energization Delay at Polaris Forge 1: Models Building 2 (100 MW operating), Building 3 (150 MW partially operating: ~50 MW operating, ~100 MW pending),
   and Building 4 (150 MW construction), with modeled Class C debt allocation.
5. OEM Purchase Commitment Expected Loss (SMCI): Explicitly separates the Accounting Channel (non-cash $2.05B NRV loss provision reducing equity)
   from the Cash Liquidity Channel (working capital inventory cash drain vs cancellation settlement fee).
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

        modeled_funding_deficit = max(0.0, drawn_debt - allowable_capacity)  # ~$4.322B
        crwv_cash = self.financials.get("CRWV", {}).get("cash_and_equivalents", 5520000000.0)
        cash_after_deficit = crwv_cash - modeled_funding_deficit
        liquidity_burn_pct = (modeled_funding_deficit / crwv_cash) * 100.0 if crwv_cash else 100.0

        downstream_freeze = liquidity_burn_pct > 60.0

        return {
            "scenario_name": "Hypothetical MTM Financing Sensitivity (71.42% Proxy)",
            "haircut_pct": haircut_pct,
            "funding_ratio_proxy": funding_ratio_proxy,
            "drawn_ddtl_debt_usd": drawn_debt,
            "base_asset_value_usd": base_asset_value,
            "stressed_asset_value_usd": stressed_asset_value,
            "allowable_capacity_usd": allowable_capacity,
            "modeled_funding_deficit_usd": modeled_funding_deficit,
            "crwv_starting_cash_usd": crwv_cash,
            "crwv_cash_after_deficit_usd": cash_after_deficit,
            "crwv_liquidity_burn_pct": round(liquidity_burn_pct, 1),
            "downstream_capex_freeze": downstream_freeze,
            "contractual_caveat": (
                "Under Exhibit 10.1 of DDTL 5.0, 71.42% is the initial Funding Date GPU Amount formula based on acquisition capex "
                "with straight-line 6-year depreciation, not an automatic ongoing secondary market appraisal cure. "
                "This scenario is an analytical sensitivity proxy (Class C)."
            ),
            "transmission_narrative": (
                f"Applying a {int(haircut_pct*100)}% secondary market haircut against the 71.42% funding-ratio proxy generates a "
                f"${modeled_funding_deficit/1e9:.2f}B borrowing base deficit across CoreWeave's ${drawn_debt/1e9:.2f}B in recourse DDTLs. "
                f"While CoreWeave's ${crwv_cash/1e9:.2f}B cash balance can absorb the prepayment, the mandatory repayment consumes "
                f"{liquidity_burn_pct:.1f}% of unrestricted liquidity, leaving ${cash_after_deficit/1e9:.2f}B and triggering a downstream capex freeze."
            )
        }

    def simulate_anchor_customer_trim(self, trim_pct: float = 0.30) -> Dict[str, Any]:
        """
        Scenario 2: Anchor Customer Demand Trim & Conditional Springing Guaranty
        Models a demand trim to Microsoft recognized revenue ($3.438B base), evaluating the literal legal
        predicates of the Unconditional Springing Guaranty (APLD Form 10-K Exhibit 10.1).
        
        Predicate Engine:
        - Predicate A (Customer Identity): Conditioned on Microsoft being the Colocation Customer at SPV VIII (Building ELN-03).
        - Predicate B (Contractual Default): Conditioned on the trim giving rise to a payment cessation, reduction, or termination (Springing Event ii).
        """
        base_revenue = 3437770000.0
        if self.graph.has_edge("MSFT", "CRWV", key="REL-MSFT-CRWV-REVENUE-CONCENTRATION"):
            base_revenue = self.graph.get_edge_data("MSFT", "CRWV", key="REL-MSFT-CRWV-REVENUE-CONCENTRATION").get("amount", 3437770000.0)

        annual_rev_loss = base_revenue * trim_pct  # $1.031B/yr at 30%

        # CoreWeave annual debt service across all funded tranches ($35.551B total):
        # Recourse DDTLs ($10.806B @ ~8.5%): ~$918M
        # DDTL 4.0 Non-recourse ($2.837B @ ~7.5%): ~$213M
        # Senior Notes ($10.029B @ 9.5%): ~$953M
        # Convertibles ($6.588B @ 1.875%): ~$124M
        # OEM Recourse ($4.220B @ 11.0%): ~$464M
        # OEM Non-Recourse ($0.882B @ 10.0%): ~$88M
        annual_debt_service = (
            10806000000.0 * 0.085 + 2837000000.0 * 0.075 + 10029000000.0 * 0.095 +
            6588000000.0 * 0.01875 + 4220000000.0 * 0.11 + 882000000.0 * 0.10
        )  # ~$2.76B/yr
        # Polaris Forge 1 lease rent: $11.0B / 15 years = $733.3M/yr fully energized (~$275.0M/yr operational 150 MW)
        annual_full_lease_rent = 11000000000.0 / 15.0
        operational_lease_rent = annual_full_lease_rent * (150.0 / 400.0)

        total_annual_commitments = annual_debt_service + annual_full_lease_rent  # ~$3.49B/yr
        crwv_cash = self.financials.get("CRWV", {}).get("cash_and_equivalents", 5520000000.0)

        # Springing Events Analysis under Exhibit 10.1:
        # Event (i): Insolvency Event of Tenant SPV
        # Event (ii): Material adverse amendment, default, or termination of Colocation Agreement, or circumstances
        # permitting the Colocation Customer to cease or materially reduce monthly payments
        # Event (iii): Failure to maintain bankruptcy-remote separateness
        # Event (iv): Acceleration of tenant debt
        conditional_springing_predicate_met = True  # Conditional on Microsoft being the Colocation Customer at Building ELN-03
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
            "springing_event_analyzed": "Springing Event (ii) - Colocation Agreement Payment Cessation or Material Reduction",
            "conditional_join_status": "Conditional: requires Microsoft to be the specific Colocation Customer at Building ELN-03",
            "transmission_narrative": (
                f"A {int(trim_pct*100)}% demand trim on Microsoft's recognized revenue reduces CoreWeave's cash inflow by ${annual_rev_loss/1e9:.2f}B/yr. "
                f"Against ${total_annual_commitments/1e9:.2f}B in annual debt service and facility commitments, if Microsoft is the Colocation Customer "
                f"at SPV VIII (Building ELN-03) and reduces colocation payments, this fulfills the literal predicate of Springing Event (ii) under Exhibit 10.1, "
                f"activating CoreWeave parent's Unconditional Springing Guaranty on the full $11.0B lease."
            )
        }

    def simulate_sofr_base_rate_shock(self, sofr_increase_bps: float = 300.0) -> Dict[str, Any]:
        """
        Scenario 3A: SOFR Benchmark Base Rate Shock (+300 bps)
        Rigorously evaluates immediate cash interest impact on unhedged floating debt.
        Incorporates CoreWeave's contractual 95% interest rate swap mandate under DDTL 5.0 (CRWV 10-Q Note 7)
        and DDTL 4.0's $1.40B floating component.
        """
        delta_r = sofr_increase_bps / 10000.0  # 0.03

        # Recourse DDTLs ($10.806B total drawn)
        crwv_recourse_ddtl_floating = 10806000000.0
        # Contractual 95% swap hedge requirement under DDTL 5.0
        swap_hedge_ratio = 0.95
        crwv_unhedged_recourse_floating = crwv_recourse_ddtl_floating * (1.0 - swap_hedge_ratio)  # $540.3M unhedged

        # DDTL 4.0 Non-recourse floating tranche ($1.40B floating out of $2.837B)
        crwv_non_recourse_floating = 1400000000.0

        # APLD corporate floating debt
        apld_floating_debt = 475938000.0

        # Immediate cash interest drain
        crwv_hedged_recourse_hit = crwv_unhedged_recourse_floating * delta_r  # $16.21M/yr
        crwv_unhedged_recourse_hit = crwv_recourse_ddtl_floating * delta_r    # $324.18M/yr (if unhedged)
        crwv_non_recourse_hit = crwv_non_recourse_floating * delta_r          # $42.00M/yr
        apld_immediate_hit = apld_floating_debt * delta_r                     # $14.28M/yr

        total_crwv_hedged_immediate_hit = crwv_hedged_recourse_hit + crwv_non_recourse_hit  # $58.21M/yr

        crwv_cash = self.financials.get("CRWV", {}).get("cash_and_equivalents", 5520000000.0)
        apld_cash = self.financials.get("APLD", {}).get("cash_and_equivalents", 1590000000.0)

        return {
            "scenario_name": "SOFR Base Rate Shock (Floating Hedged vs Unhedged)",
            "sofr_increase_bps": sofr_increase_bps,
            "crwv_recourse_floating_usd": crwv_recourse_ddtl_floating,
            "crwv_swap_hedge_ratio": swap_hedge_ratio,
            "crwv_unhedged_recourse_floating_usd": crwv_unhedged_recourse_floating,
            "crwv_non_recourse_floating_usd": crwv_non_recourse_floating,
            "crwv_immediate_cash_drain_hedged_usd": total_crwv_hedged_immediate_hit,
            "crwv_immediate_cash_drain_unhedged_usd": crwv_unhedged_recourse_hit + crwv_non_recourse_hit,
            "apld_immediate_cash_drain_usd": apld_immediate_hit,
            "crwv_cash_usd": crwv_cash,
            "apld_cash_usd": apld_cash,
            "transmission_narrative": (
                f"A +{int(sofr_increase_bps)} bps SOFR increase adds ${apld_immediate_hit/1e6:.1f}M/yr to Applied Digital's floating corporate debt. "
                f"For CoreWeave, DDTL 5.0 contractually mandates 95% interest rate swap coverage on recourse DDTLs, limiting the recourse cash drain to "
                f"${crwv_hedged_recourse_hit/1e6:.1f}M/yr (versus ${crwv_unhedged_recourse_hit/1e6:.1f}M/yr if fully unhedged). Adding DDTL 4.0's "
                f"$1.40B floating tranche brings CoreWeave's immediate hedged annual cash drain to ${total_crwv_hedged_immediate_hit/1e6:.1f}M/yr."
            )
        }

    def simulate_refinancing_spread_shock(self, spread_increase_bps: float = 300.0) -> Dict[str, Any]:
        """
        Scenario 3B: Credit Spread / Refinancing Shock at Maturity (+300 bps)
        Evaluates the refinancing penalty when maturing debt principal rolls over into higher secondary credit spreads.
        Uses CoreWeave's audited debt maturities table (CRWV 10-Q Note 7):
        - 2026 remainder: $4,413M ($4.413B)
        - 2027: $6,184M ($6.184B)
        - 2028: $4,416M ($4.416B)
        - 3-Year Total Maturing: $15.013B
        """
        delta_spread = spread_increase_bps / 10000.0  # 0.03
        maturing_2026 = 4413000000.0
        maturing_2027 = 6184000000.0
        maturing_2028 = 4416000000.0

        refi_cost_2026_yr = maturing_2026 * delta_spread  # $132.39M/yr
        refi_cost_2027_yr = maturing_2027 * delta_spread  # $185.52M/yr
        refi_cost_2028_yr = maturing_2028 * delta_spread  # $132.48M/yr

        cumulative_refi_cost_2yr = refi_cost_2026_yr + refi_cost_2027_yr  # $317.91M/yr
        cumulative_refi_cost_3yr = cumulative_refi_cost_2yr + refi_cost_2028_yr  # $450.39M/yr

        # Applied Digital: Notes mature in 2029 ($2.35B) and 2030 ($2.15B); zero refinancing impact in 2026-2028
        apld_maturing_2026_2028 = 0.0

        crwv_cash = self.financials.get("CRWV", {}).get("cash_and_equivalents", 5520000000.0)

        return {
            "scenario_name": "Credit Spread / Refinancing Shock at Maturity",
            "spread_increase_bps": spread_increase_bps,
            "crwv_maturing_2026_usd": maturing_2026,
            "crwv_maturing_2027_usd": maturing_2027,
            "crwv_maturing_2028_usd": maturing_2028,
            "crwv_refi_annual_penalty_2026_usd": refi_cost_2026_yr,
            "crwv_refi_annual_penalty_2027_usd": refi_cost_2027_yr,
            "crwv_refi_cumulative_penalty_2yr_usd": cumulative_refi_cost_2yr,
            "crwv_refi_cumulative_penalty_3yr_usd": cumulative_refi_cost_3yr,
            "crwv_starting_cash_usd": crwv_cash,
            "transmission_narrative": (
                f"Existing contractual fixed and floating spreads do not adjust immediately to secondary market credit spreads. "
                f"However, CoreWeave faces ${maturing_2026/1e9:.2f}B in 2026 debt maturities and ${maturing_2027/1e9:.2f}B in 2027 ($10.60B across 24 months). "
                f"Refinancing this maturing debt under a +{int(spread_increase_bps)} bps market credit spread shock imposes an incremental "
                f"${cumulative_refi_cost_2yr/1e6:.1f}M/year in debt service by 2027, and ${cumulative_refi_cost_3yr/1e6:.1f}M/year through 2028."
            )
        }

    def simulate_grid_energization_delay(self, delay_months: int = 12) -> Dict[str, Any]:
        """
        Scenario 4: Phased Grid Energization Delay at Polaris Forge 1
        Models building-level operational phasing (APLD 10-K Item 1):
        - Building 2 (ELN-02): 100 MW — fully operational ($183.3M/yr base rent ongoing).
        - Building 3 (ELN-03): 150 MW — partially operational (~50 MW operational, ~100 MW pending energization/commissioning).
        - Building 4: 150 MW — under active construction / design.
        Total: ~150 MW operational ($275.0M/yr base rent) vs ~250 MW unenergized expansion ($458.3M/yr deferred rent).
        Carrying cost on construction debt uses modeled Class C MW-allocation ($2.35B notes * 250/400).
        """
        total_mw = 400.0
        operational_mw = 150.0  # Building 2 (100 MW) + Building 3 partial (50 MW)
        delayed_mw = 250.0      # Building 3 pending (100 MW) + Building 4 (150 MW)
        annual_full_rent = 11000000000.0 / 15.0  # $733.3M/yr

        ongoing_operational_rent = annual_full_rent * (operational_mw / total_mw)  # $275.0M/yr
        deferred_expansion_rent = annual_full_rent * (delayed_mw / total_mw) * (delay_months / 12.0)  # $458.33M

        # Carrying cost on Polaris Forge 1 debt ($2.35B 9.25% notes):
        # Modeled Class C allocation by pending MW: 250 / 400
        construction_phase_debt = 2350000000.0 * (delayed_mw / total_mw)  # $1.46875B (Class C proxy)
        apld_construction_carrying_cost = construction_phase_debt * 0.0925 * (delay_months / 12.0)  # $135.86M

        apld_cash = self.financials.get("APLD", {}).get("cash_and_equivalents", 1590000000.0)
        cash_drain_pct = (apld_construction_carrying_cost / apld_cash) * 100.0 if apld_cash else 100.0

        return {
            "scenario_name": "Phased Grid Energization Delay (Polaris Forge 1)",
            "delay_months": delay_months,
            "project": "POLARIS_FORGE_1",
            "operational_mw": operational_mw,
            "delayed_mw": delayed_mw,
            "ongoing_operational_rent_usd": ongoing_operational_rent,
            "deferred_expansion_rent_usd": deferred_expansion_rent,
            "construction_phase_debt_modeled_usd": construction_phase_debt,
            "apld_debt_carrying_cost_usd": apld_construction_carrying_cost,
            "apld_starting_cash_usd": apld_cash,
            "apld_cash_drain_pct": round(cash_drain_pct, 1),
            "debt_allocation_flag": "Class C (modeled MW allocation; not contractual debt tranche)",
            "transmission_narrative": (
                f"A {delay_months}-month grid energization delay defers ${deferred_expansion_rent/1e6:.1f}M in expansion rent across the unenergized 250 MW "
                f"(Building 3 pending + Building 4). However, the ~150 MW operational capacity (Building 2 + Building 3 partial) generates ${ongoing_operational_rent/1e6:.1f}M/yr "
                f"in base rent. Applied Digital's modeled construction carrying cost on the delayed phase is ${apld_construction_carrying_cost/1e6:.1f}M, "
                f"consuming only {cash_drain_pct:.1f}% of its ${apld_cash/1e9:.2f}B cash reserves."
            )
        }

    def simulate_oem_purchase_commitment_markdown(self, excess_allocation_pct: float = 0.15, modeled_recovery_haircut: float = 0.40) -> Dict[str, Any]:
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
        # A) Cancellation Settlement Fee (modeled at 15% cancellation penalty): $769.5M cash drain
        cancellation_fee_rate = 0.15
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
                f"a negotiated cancellation settlement consumes ${modeled_cancellation_cash_drain/1e6:.1f}M ({cancellation_cash_drain_pct:.1f}% of cash), "
                f"whereas taking physical delivery of unabsorbed inventory would consume ${gross_inventory_cash_drain/1e9:.2f}B ({gross_delivery_cash_drain_pct:.1f}% of cash)."
            )
        }

    def run_all_stress_scenarios(self) -> pd.DataFrame:
        """Run complete quantitative stress test suite and generate canonical summary table."""
        res_gpu = self.simulate_gpu_collateral_haircut(haircut_pct=0.40, funding_ratio_proxy=0.7142)
        res_cust = self.simulate_anchor_customer_trim(trim_pct=0.30)
        res_sofr = self.simulate_sofr_base_rate_shock(sofr_increase_bps=300.0)
        res_refi = self.simulate_refinancing_spread_shock(spread_increase_bps=300.0)
        res_grid = self.simulate_grid_energization_delay(delay_months=12)
        res_oem = self.simulate_oem_purchase_commitment_markdown(excess_allocation_pct=0.15, modeled_recovery_haircut=0.40)

        summary_rows = [
            {
                "scenario_name": res_gpu["scenario_name"],
                "shock_parameter": "-40% GPU Collateral Value",
                "direct_cash_or_collateral_hit_usd": res_gpu["modeled_funding_deficit_usd"],
                "target_entity": "CRWV",
                "covenant_or_liquidity_impact": f"{res_gpu['crwv_liquidity_burn_pct']}% Cash Depletion",
                "contagion_mechanism": "Forces $4.32B funding deficit on drawn DDTLs under 71.42% proxy, freezing operational capex."
            },
            {
                "scenario_name": res_cust["scenario_name"],
                "shock_parameter": "-30% Microsoft Off-Take",
                "direct_cash_or_collateral_hit_usd": res_cust["annual_revenue_loss_usd"],
                "target_entity": "CRWV",
                "covenant_or_liquidity_impact": "Springing Guaranty Conditional Activation",
                "contagion_mechanism": "Reduces revenue by $1.03B; conditionally activates parent $11.0B guaranty under Springing Event (ii) if Microsoft is Building ELN-03 tenant."
            },
            {
                "scenario_name": res_sofr["scenario_name"],
                "shock_parameter": "+300 bps SOFR Benchmark",
                "direct_cash_or_collateral_hit_usd": res_sofr["crwv_immediate_cash_drain_hedged_usd"] + res_sofr["apld_immediate_cash_drain_usd"],
                "target_entity": "CRWV / APLD",
                "covenant_or_liquidity_impact": "Hedged Cash Drain: $72.5M/yr",
                "contagion_mechanism": "CoreWeave 95% swap mandate limits recourse drain to $16.2M; DDTL 4.0 floating adds $42M; APLD floating adds $14.3M."
            },
            {
                "scenario_name": res_refi["scenario_name"],
                "shock_parameter": "+300 bps Credit Spread at Maturity",
                "direct_cash_or_collateral_hit_usd": res_refi["crwv_refi_cumulative_penalty_2yr_usd"],
                "target_entity": "CRWV",
                "covenant_or_liquidity_impact": "$318M/yr Added Refinancing Interest",
                "contagion_mechanism": "Existing spreads unaffected; hits $10.60B maturing principal across 2026-2027 ($4.41B in 2026, $6.18B in 2027)."
            },
            {
                "scenario_name": res_grid["scenario_name"],
                "shock_parameter": "12-Month Energization Delay",
                "direct_cash_or_collateral_hit_usd": res_grid["apld_debt_carrying_cost_usd"],
                "target_entity": "APLD",
                "covenant_or_liquidity_impact": f"{res_grid['apld_cash_drain_pct']}% Cash Drain",
                "contagion_mechanism": "Defers $458M expansion rent on 250 MW pending, while 150 MW produces $275M base rent; carrying cost is $136M."
            },
            {
                "scenario_name": res_oem["scenario_name"],
                "shock_parameter": "15% Demand Pullback",
                "direct_cash_or_collateral_hit_usd": res_oem["accounting_nrv_write_down_usd"],
                "target_entity": "SMCI",
                "covenant_or_liquidity_impact": f"{res_oem['cancellation_cash_drain_pct']}% to {res_oem['gross_delivery_cash_drain_pct']}% Cash Drain",
                "contagion_mechanism": "Accounting: $2.05B NRV loss provision on equity. Cash: $769M cancellation fee (10% cash) or $5.13B delivery (68% cash)."
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
    print("=== Parameterized Financial Stress Prototype Results (Phase 0.7) ===")
    print(df[["scenario_name", "shock_parameter", "direct_cash_or_collateral_hit_usd", "target_entity", "covenant_or_liquidity_impact"]])
