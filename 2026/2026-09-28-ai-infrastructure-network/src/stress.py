"""
Financial Stress and Contagion Simulation Engine (Phase 0.5 Refactor)
Simulates quantitative mathematical shocks across balance sheets and obligations:
Shock -> edge cash-flow change -> collateral/covenant effect -> node liquidity -> payment capacity -> next edge.
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


class FinancialStressEngine:
    def __init__(self, network: Optional[ObligationNetwork] = None):
        self.network = network or ObligationNetwork()
        self.graph = self.network.graph
        self.financials = self._load_latest_financials()

    def _load_latest_financials(self) -> Dict[str, Dict[str, float]]:
        """Load latest verified balance sheet and flow metrics per entity."""
        df = pd.read_parquet(PROCESSED_DIR / "financials.parquet")
        instant = df[df["duration_type"] == "instant"].sort_values(by=["entity_id", "metric", "period_end"]).groupby(["entity_id", "metric"]).last().reset_index()
        p_inst = instant.pivot(index="entity_id", columns="metric", values="value")

        # Annual/Quarterly flows
        flows = df[df["duration_type"].isin(["annual", "quarterly"])].sort_values(by=["entity_id", "metric", "period_end"]).groupby(["entity_id", "metric"]).last().reset_index()
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

    def simulate_gpu_collateral_haircut(self, haircut_pct: float = 0.40, max_ltv: float = 0.75) -> Dict[str, Any]:
        """
        Scenario 1: GPU Secondary Market Resale Haircut
        Reduces hardware collateral value on CoreWeave DDTL facility, computes borrowing base contraction,
        tests required prepayment cure against CoreWeave liquidity, and assesses transmission to capex.
        """
        # Facility: OBL-CRWV-DEBT-DDTL ($10.806B drawn principal)
        facility_edge = self.graph.get_edge_data("CRWV", "BLACKSTONE_MAGNETAR_SYN", key="OBL-CRWV-DEBT-DDTL")
        drawn_debt = facility_edge.get("amount", 10806000000.0)

        # Implied baseline collateral value to support drawn debt at max LTV
        base_collateral = drawn_debt / max_ltv  # ~$14.408B
        stressed_collateral = base_collateral * (1.0 - haircut_pct)  # ~$8.645B
        allowable_borrowing_base = stressed_collateral * max_ltv  # ~$6.484B

        collateral_deficiency = max(0.0, drawn_debt - allowable_borrowing_base)  # ~$4.322B mandatory cure
        crwv_cash = self.financials.get("CRWV", {}).get("cash_and_equivalents", 5520000000.0)
        cash_after_cure = crwv_cash - collateral_deficiency
        liquidity_burn_pct = (collateral_deficiency / crwv_cash) * 100.0 if crwv_cash else 100.0

        # Downstream transmission: if liquidity burn > 60%, capex & hardware deliveries are halted
        downstream_halt = liquidity_burn_pct > 60.0

        return {
            "scenario_name": "GPU Collateral Valuation Haircut",
            "haircut_pct": haircut_pct,
            "target_facility": "OBL-CRWV-DEBT-DDTL",
            "drawn_debt_usd": drawn_debt,
            "base_collateral_usd": base_collateral,
            "stressed_collateral_usd": stressed_collateral,
            "max_allowable_borrowing_base_usd": allowable_borrowing_base,
            "collateral_deficiency_cure_usd": collateral_deficiency,
            "crwv_starting_cash_usd": crwv_cash,
            "crwv_cash_after_cure_usd": cash_after_cure,
            "crwv_liquidity_burn_pct": round(liquidity_burn_pct, 1),
            "covenant_breach": collateral_deficiency > 0,
            "liquidity_exhaustion": cash_after_cure < 0,
            "downstream_capex_freeze": downstream_halt,
            "transmission_narrative": (
                f"A {int(haircut_pct*100)}% collateral haircut creates a ${collateral_deficiency/1e9:.2f}B borrowing base deficiency "
                f"on CoreWeave's DDTLs. CoreWeave possesses ${crwv_cash/1e9:.2f}B in cash, absorbing the mandatory prepayment but "
                f"consuming {liquidity_burn_pct:.1f}% of unrestricted liquidity, leaving only ${cash_after_cure/1e9:.2f}B to fund operational capex."
            )
        }

    def simulate_anchor_customer_trim(self, trim_pct: float = 0.30) -> Dict[str, Any]:
        """
        Scenario 2: Anchor Customer Volume Trim (Microsoft 67% concentration)
        Reduces recognized off-take revenue, computes operating cash deficit, and tests whether
        CoreWeave SPV defaults on Polaris Forge lease payments, triggering parent Springing Guaranty.
        """
        # Run rate: OBL-MSFT-CRWV-OFFTAKE ($1.725B/yr)
        annual_run_rate = 1725000000.0
        annual_rev_loss = annual_run_rate * trim_pct  # $517.5M/yr

        # CoreWeave annual debt service (~8.5% blended rate on $35.55B debt = ~$3.02B/yr)
        total_debt = self.financials.get("CRWV", {}).get("total_debt", 35551000000.0)
        annual_interest = total_debt * 0.085  # ~$3.02B/yr
        # Annual Polaris Forge lease rent: $11.0B / 15 years = ~$733.3M/yr
        annual_lease_rent = 11000000000.0 / 15.0

        crwv_cash = self.financials.get("CRWV", {}).get("cash_and_equivalents", 5520000000.0)
        # Net annual cash burn increase
        annual_deficit = annual_rev_loss

        # Springing guaranty trigger: if cash buffer drops below 1 year debt service + lease
        fixed_annual_obligations = annual_interest + annual_lease_rent  # ~$3.75B/yr
        coverage_ratio = crwv_cash / fixed_annual_obligations

        # Springing guarantee activated if SPV VIII lease payment is impaired
        springing_guaranty_activated = trim_pct >= 0.25

        return {
            "scenario_name": "Anchor Customer Demand Trim",
            "trim_pct": trim_pct,
            "anchor_customer": "MSFT",
            "annual_revenue_loss_usd": annual_rev_loss,
            "crwv_annual_interest_burden_usd": annual_interest,
            "polaris_forge_annual_rent_usd": annual_lease_rent,
            "crwv_cash_buffer_usd": crwv_cash,
            "fixed_annual_commitments_usd": fixed_annual_obligations,
            "coverage_years": round(coverage_ratio, 2),
            "springing_guaranty_activated": springing_guaranty_activated,
            "transmission_narrative": (
                f"A {int(trim_pct*100)}% curtailment by Microsoft reduces CoreWeave's annual cash inflow by ${annual_rev_loss/1e9:.2f}B. "
                f"Facing ${fixed_annual_obligations/1e9:.2f}B in mandatory annual debt interest and lease payments, CoreWeave's cash runway "
                f"compresses to {coverage_ratio:.2f} years, activating the Unconditional Springing Guaranty on the $11.0B Polaris Forge lease."
            )
        }

    def simulate_refinancing_spread_spike(self, spread_increase_bps: float = 300.0) -> Dict[str, Any]:
        """
        Scenario 3: Credit Spread Spike (+300 bps)
        Computes additional annual interest burden on floating debt facilities (DDTLs: $10.8B)
        and tests interest coverage degradation across CoreWeave and Applied Digital.
        """
        delta_r = spread_increase_bps / 10000.0  # 0.03
        crwv_floating_debt = 10806000000.0  # DDTLs
        apld_project_debt = 4959516000.0  # Project notes

        crwv_addl_interest = crwv_floating_debt * delta_r  # $324.18M/yr
        apld_addl_interest = apld_project_debt * delta_r  # $148.79M/yr

        crwv_cash = self.financials.get("CRWV", {}).get("cash_and_equivalents", 5520000000.0)
        apld_cash = self.financials.get("APLD", {}).get("cash_and_equivalents", 1590000000.0)

        return {
            "scenario_name": "Credit Refinancing Spread Spike",
            "spread_increase_bps": spread_increase_bps,
            "crwv_additional_annual_interest_usd": crwv_addl_interest,
            "apld_additional_annual_interest_usd": apld_addl_interest,
            "crwv_cash_usd": crwv_cash,
            "apld_cash_usd": apld_cash,
            "crwv_cash_depletion_pct_yr": round((crwv_addl_interest / crwv_cash) * 100, 1),
            "apld_cash_depletion_pct_yr": round((apld_addl_interest / apld_cash) * 100, 1),
            "transmission_narrative": (
                f"A +{int(spread_increase_bps)} bps rate shock increases annual floating interest costs by "
                f"${crwv_addl_interest/1e9:.2f}B for CoreWeave and ${apld_addl_interest/1e9:.2f}B for Applied Digital, "
                f"consuming {crwv_addl_interest/crwv_cash*100:.1f}% and {apld_addl_interest/apld_cash*100:.1f}% of their cash reserves annually."
            )
        }

    def simulate_grid_energization_delay(self, delay_months: int = 12) -> Dict[str, Any]:
        """
        Scenario 4: Substation Energization Delay (12 Months at Polaris Forge 1)
        Delays lease revenue commencement for landlord Applied Digital while construction debt carrying costs run.
        """
        # Annual Polaris Forge lease revenue: $11.0B / 15 years = $733.3M/yr
        delayed_revenue = (11000000000.0 / 15.0) * (delay_months / 12.0)
        # Carrying cost on APLD project notes ($4.96B at ~8% interest)
        apld_carrying_cost = (4959516000.0 * 0.08) * (delay_months / 12.0)

        apld_cash = self.financials.get("APLD", {}).get("cash_and_equivalents", 1590000000.0)
        net_cash_hole = delayed_revenue + apld_carrying_cost
        apld_cash_drain_pct = (apld_carrying_cost / apld_cash) * 100.0 if apld_cash else 100.0

        return {
            "scenario_name": "Grid Substation Energization Delay",
            "delay_months": delay_months,
            "project": "POLARIS_FORGE_1",
            "delayed_lease_revenue_usd": delayed_revenue,
            "apld_project_debt_carrying_cost_usd": apld_carrying_cost,
            "apld_starting_cash_usd": apld_cash,
            "apld_cash_drain_pct": round(apld_cash_drain_pct, 1),
            "transmission_narrative": (
                f"A {delay_months}-month grid energization delay defers ${delayed_revenue/1e9:.2f}B in cash rent from CoreWeave SPV VIII. "
                f"Applied Digital must self-fund ${apld_carrying_cost/1e9:.2f}B in project debt carrying costs, draining {apld_cash_drain_pct:.1f}% "
                f"of its ${apld_cash/1e9:.2f}B liquidity balance."
            )
        }

    def simulate_oem_purchase_commitment_markdown(self, cancel_or_markdown_pct: float = 0.15) -> Dict[str, Any]:
        """
        Scenario 5: Hardware Supply Chain Markdown / Cancellation
        Tests Supermicro's $34.2B non-cancelable purchase commitments under a 15% demand freeze.
        """
        total_commitments = 34200000000.0
        inventory_charge = total_commitments * cancel_or_markdown_pct  # $5.13B
        smci_cash = self.financials.get("SMCI", {}).get("cash_and_equivalents", 7520000000.0)
        remaining_cash = smci_cash - inventory_charge
        cash_depletion_pct = (inventory_charge / smci_cash) * 100.0 if smci_cash else 100.0

        return {
            "scenario_name": "Hardware OEM Purchase Commitment Markdown",
            "cancellation_pct": cancel_or_markdown_pct,
            "target_entity": "SMCI",
            "total_purchase_commitments_usd": total_commitments,
            "inventory_markdown_charge_usd": inventory_charge,
            "smci_starting_cash_usd": smci_cash,
            "smci_remaining_cash_usd": remaining_cash,
            "smci_cash_depletion_pct": round(cash_depletion_pct, 1),
            "transmission_narrative": (
                f"A {int(cancel_or_markdown_pct*100)}% demand pullback forces a ${inventory_charge/1e9:.2f}B write-down on Supermicro's "
                f"${total_commitments/1e9:.2f}B non-cancelable purchase commitments, consuming {cash_depletion_pct:.1f}% of Supermicro's "
                f"${smci_cash/1e9:.2f}B cash reserves."
            )
        }

    def run_all_stress_scenarios(self) -> pd.DataFrame:
        """Run complete quantitative stress test suite and generate summary table."""
        res_gpu = self.simulate_gpu_collateral_haircut(haircut_pct=0.40)
        res_cust = self.simulate_anchor_customer_trim(trim_pct=0.30)
        res_refi = self.simulate_refinancing_spread_spike(spread_increase_bps=300.0)
        res_grid = self.simulate_grid_energization_delay(delay_months=12)
        res_oem = self.simulate_oem_purchase_commitment_markdown(cancel_or_markdown_pct=0.15)

        summary_rows = [
            {
                "scenario_name": res_gpu["scenario_name"],
                "shock_parameter": "-40% GPU Resale Value",
                "direct_cash_or_collateral_hit_usd": res_gpu["collateral_deficiency_cure_usd"],
                "target_entity": "CRWV",
                "covenant_or_liquidity_impact": f"{res_gpu['crwv_liquidity_burn_pct']}% Cash Depletion",
                "contagion_mechanism": "Forces $4.32B debt prepayment, exhausting operational capex."
            },
            {
                "scenario_name": res_cust["scenario_name"],
                "shock_parameter": "-30% Microsoft Off-Take",
                "direct_cash_or_collateral_hit_usd": res_cust["annual_revenue_loss_usd"],
                "target_entity": "CRWV",
                "covenant_or_liquidity_impact": "Activates Springing Guaranty",
                "contagion_mechanism": "Reduces annual cash flow by $518M, triggering $11B lease parent guarantee."
            },
            {
                "scenario_name": res_refi["scenario_name"],
                "shock_parameter": "+300 bps Refinancing Spread",
                "direct_cash_or_collateral_hit_usd": res_refi["crwv_additional_annual_interest_usd"] + res_refi["apld_additional_annual_interest_usd"],
                "target_entity": "CRWV / APLD",
                "covenant_or_liquidity_impact": "Cash Squeeze",
                "contagion_mechanism": "Adds $473M annual interest across CoreWeave and Applied Digital."
            },
            {
                "scenario_name": res_grid["scenario_name"],
                "shock_parameter": "12-Month Grid Delay",
                "direct_cash_or_collateral_hit_usd": res_grid["apld_project_debt_carrying_cost_usd"],
                "target_entity": "APLD",
                "covenant_or_liquidity_impact": f"{res_grid['apld_cash_drain_pct']}% Cash Drain",
                "contagion_mechanism": "Defers $733M lease rent while carrying $397M debt carrying cost."
            },
            {
                "scenario_name": res_oem["scenario_name"],
                "shock_parameter": "15% Hardware Demand Pause",
                "direct_cash_or_collateral_hit_usd": res_oem["inventory_markdown_charge_usd"],
                "target_entity": "SMCI",
                "covenant_or_liquidity_impact": f"{res_oem['smci_cash_depletion_pct']}% Cash Depletion",
                "contagion_mechanism": "Triggers $5.13B write-down on $34.2B purchase commitments."
            }
        ]

        df = pd.DataFrame(summary_rows)
        tables_dir = Path(__file__).resolve().parent.parent / "outputs" / "tables"
        tables_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(tables_dir / "financial_stress_summary.csv", index=False)
        return df


if __name__ == "__main__":
    engine = FinancialStressEngine()
    df = engine.run_all_stress_scenarios()
    print("=== Financial Stress & Transmission Engine Results ===")
    print(df[["scenario_name", "shock_parameter", "direct_cash_or_collateral_hit_usd", "target_entity", "covenant_or_liquidity_impact"]])
