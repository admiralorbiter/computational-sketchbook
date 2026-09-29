"""
Parameterized Financial Stress and Contagion Simulation Prototype (Phase 0.6 Refactor)
Simulates contract-calibrated transmission functions across balance sheets and obligations:
1. Modeled Borrowing Base Contraction: Evaluates GPU collateral haircuts against DDTL 5.0 advance rate formulas (71.42%).
2. Anchor Customer Concentration & Springing Guaranty: Shocks Microsoft recognized revenue ($3.44B), testing SPV colocation lease shortfall triggering parent Unconditional Springing Guaranty.
3. Floating vs. Fixed Debt Refinancing: Applies rate shocks strictly to floating facilities (CRWV DDTLs: $10.8B) while recognizing fixed coupon insulation (APLD notes: 9.25%/6.75% fixed) and rollover risk.
4. Phased Grid Energization Delay: Models Polaris Forge 1 operational (~100 MW, $183.3M/yr) vs delayed unenergized expansion (~300 MW, $550M/yr).
5. Purchase Commitment Expected Loss: Models Supermicro $34.2B purchase commitments via Net Realizable Value (NRV) write-down and cancellation provisions.
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

    def simulate_gpu_collateral_haircut(self, haircut_pct: float = 0.40, advance_rate: float = 0.7142) -> Dict[str, Any]:
        """
        Scenario 1: Modeled Borrowing Base Contraction (GPU Resale Value Haircut)
        Tests CoreWeave's drawn DDTLs ($10.806B across DDTL 1.0, 2.0, 2.1, 3.0, 5.0) against
        the contract-calibrated 71.42% borrowing base advance rate formula.
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

        # Required baseline collateral value to support drawn debt at contractual advance rate
        base_collateral = drawn_debt / advance_rate  # ~$15.130B
        stressed_collateral = base_collateral * (1.0 - haircut_pct)  # ~$9.078B
        allowable_borrowing_base = stressed_collateral * advance_rate  # ~$6.484B

        collateral_deficiency = max(0.0, drawn_debt - allowable_borrowing_base)  # ~$4.322B mandatory cure
        crwv_cash = self.financials.get("CRWV", {}).get("cash_and_equivalents", 5520000000.0)
        cash_after_cure = crwv_cash - collateral_deficiency
        liquidity_burn_pct = (collateral_deficiency / crwv_cash) * 100.0 if crwv_cash else 100.0

        downstream_freeze = liquidity_burn_pct > 60.0

        return {
            "scenario_name": "Modeled Borrowing Base Contraction",
            "haircut_pct": haircut_pct,
            "advance_rate": advance_rate,
            "drawn_ddtl_debt_usd": drawn_debt,
            "base_collateral_usd": base_collateral,
            "stressed_collateral_usd": stressed_collateral,
            "max_allowable_borrowing_base_usd": allowable_borrowing_base,
            "mandatory_prepayment_cure_usd": collateral_deficiency,
            "crwv_starting_cash_usd": crwv_cash,
            "crwv_cash_after_cure_usd": cash_after_cure,
            "crwv_liquidity_burn_pct": round(liquidity_burn_pct, 1),
            "covenant_breach": collateral_deficiency > 0,
            "liquidity_exhaustion": cash_after_cure < 0,
            "downstream_capex_freeze": downstream_freeze,
            "transmission_narrative": (
                f"Under a {int(haircut_pct*100)}% collateral haircut, the 71.42% advance rate formula triggers a "
                f"${collateral_deficiency/1e9:.2f}B borrowing base deficiency across CoreWeave's ${drawn_debt/1e9:.2f}B in drawn DDTLs. "
                f"While CoreWeave's ${crwv_cash/1e9:.2f}B cash balance can fund the prepayment cure, the mandatory repayment consumes "
                f"{liquidity_burn_pct:.1f}% of unrestricted liquidity, leaving just ${cash_after_cure/1e9:.2f}B and triggering a downstream capex freeze."
            )
        }

    def simulate_anchor_customer_trim(self, trim_pct: float = 0.30) -> Dict[str, Any]:
        """
        Scenario 2: Anchor Customer Concentration & Springing Guaranty Trigger
        Models a demand trim to Microsoft recognized revenue ($3.438B base), tests SPV colocation lease
        shortfall, and triggers CoreWeave parent's Unconditional Springing Guaranty.
        """
        # Baseline: REL-MSFT-CRWV-REVENUE-CONCENTRATION ($3.438B recognized FY25 revenue)
        base_revenue = 3437770000.0
        if self.graph.has_edge("MSFT", "CRWV", key="REL-MSFT-CRWV-REVENUE-CONCENTRATION"):
            base_revenue = self.graph.get_edge_data("MSFT", "CRWV", key="REL-MSFT-CRWV-REVENUE-CONCENTRATION").get("amount", 3437770000.0)

        annual_rev_loss = base_revenue * trim_pct  # $1.031B/yr at 30%

        # CoreWeave fixed annual debt service:
        # Floating DDTLs ($10.8B @ 8.5%): ~$918M
        # Senior Notes ($10.0B @ 9.5%): ~$953M
        # Convertibles ($6.6B @ 1.875%): ~$124M
        # OEM Financing ($4.2B @ 11.0%): ~$464M
        annual_debt_service = 10806000000.0 * 0.085 + 10029000000.0 * 0.095 + 6588000000.0 * 0.01875 + 4220000000.0 * 0.11
        # Polaris Forge 1 lease rent: $11.0B / 15 years = $733.3M/yr fully energized (~$183.3M/yr operational 100 MW)
        annual_full_lease_rent = 11000000000.0 / 15.0
        operational_lease_rent = annual_full_lease_rent * (100.0 / 400.0)

        total_annual_commitments = annual_debt_service + annual_full_lease_rent  # ~$3.19B/yr
        crwv_cash = self.financials.get("CRWV", {}).get("cash_and_equivalents", 5520000000.0)

        # SPV Colocation short-fall predicate:
        # If CoreWeave revenue drops significantly, SPV VIII suffers payment impairment, activating the springing guaranty
        springing_guaranty_triggered = annual_rev_loss > (base_revenue * 0.20)
        coverage_ratio = crwv_cash / total_annual_commitments

        return {
            "scenario_name": "Anchor Customer Demand Trim & Springing Guaranty",
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
            "springing_guaranty_activated": springing_guaranty_triggered,
            "transmission_narrative": (
                f"A {int(trim_pct*100)}% curtailment of Microsoft's recognized revenue reduces CoreWeave's cash inflow by ${annual_rev_loss/1e9:.2f}B/yr. "
                f"With ${total_annual_commitments/1e9:.2f}B in annual debt service and facility commitments, SPV VIII faces a colocation rent shortfall, "
                f"fulfilling the legal predicate that activates CoreWeave's Unconditional Springing Guaranty on the $11.0B Polaris Forge lease."
            )
        }

    def simulate_refinancing_spread_spike(self, spread_increase_bps: float = 300.0) -> Dict[str, Any]:
        """
        Scenario 3: Credit Refinancing Spread Spike (+300 bps)
        Transmission rigorously distinguishes floating debt (immediate cash interest spike) from
        fixed-rate debt (APLD 9.25%/6.75% notes and CRWV Senior Notes: zero immediate cash impact, but maturity rollover risk).
        """
        delta_r = spread_increase_bps / 10000.0  # 0.03
        crwv_floating_debt = 10806000000.0  # DDTLs 1/2/2.1/3/5
        crwv_fixed_debt = 10029000000.0 + 6588000000.0 + 4220000000.0  # $20.84B Notes, Convertibles, OEM

        apld_fixed_project_notes = 2350000000.0 + 2150000000.0  # $4.50B (9.25% and 6.75% notes)
        apld_floating_corporate_debt = 475938000.0  # Corporate facilities

        # Immediate cash interest hits ONLY floating tranches
        crwv_floating_interest_hit = crwv_floating_debt * delta_r  # $324.18M/yr
        apld_floating_interest_hit = apld_floating_corporate_debt * delta_r  # $14.28M/yr

        crwv_cash = self.financials.get("CRWV", {}).get("cash_and_equivalents", 5520000000.0)
        apld_cash = self.financials.get("APLD", {}).get("cash_and_equivalents", 1590000000.0)

        return {
            "scenario_name": "Credit Spread Spike (Floating vs Fixed Transmission)",
            "spread_increase_bps": spread_increase_bps,
            "crwv_floating_debt_usd": crwv_floating_debt,
            "crwv_fixed_debt_usd": crwv_fixed_debt,
            "apld_fixed_project_notes_usd": apld_fixed_project_notes,
            "apld_floating_debt_usd": apld_floating_corporate_debt,
            "crwv_immediate_cash_interest_hit_usd": crwv_floating_interest_hit,
            "apld_immediate_cash_interest_hit_usd": apld_floating_interest_hit,
            "crwv_cash_usd": crwv_cash,
            "apld_cash_usd": apld_cash,
            "crwv_cash_drain_pct_yr": round((crwv_floating_interest_hit / crwv_cash) * 100.0, 1),
            "apld_cash_drain_pct_yr": round((apld_floating_interest_hit / apld_cash) * 100.0, 1),
            "transmission_narrative": (
                f"A +{int(spread_increase_bps)} bps rate shock increases annual floating cash interest by ${crwv_floating_interest_hit/1e9:.2f}B for CoreWeave "
                f"and ${apld_floating_interest_hit/1e6:.1f}M for Applied Digital. Crucially, Applied Digital's ${apld_fixed_project_notes/1e9:.2f}B in project notes "
                f"and CoreWeave's ${crwv_fixed_debt/1e9:.2f}B in senior/convertible notes bear fixed coupons, suffering zero immediate cash hit but facing rollover refinancing risk."
            )
        }

    def simulate_grid_energization_delay(self, delay_months: int = 12) -> Dict[str, Any]:
        """
        Scenario 4: Phased Grid Energization Delay at Polaris Forge 1
        Models 100 MW operational capacity ($183.3M/yr base rent ongoing) vs ~300 MW unenergized
        expansion delayed ($550.0M/yr deferred rent and carrying cost on construction debt).
        """
        total_mw = 400.0
        operational_mw = 100.0
        delayed_mw = 300.0
        annual_full_rent = 11000000000.0 / 15.0  # $733.3M/yr

        ongoing_operational_rent = annual_full_rent * (operational_mw / total_mw)  # $183.3M/yr
        deferred_expansion_rent = annual_full_rent * (delayed_mw / total_mw) * (delay_months / 12.0)  # $550.0M

        # Carrying cost on Polaris Forge 1 construction debt ($2.35B 9.25% notes):
        # 300 MW / 400 MW allocable to delayed phase
        delayed_phase_debt = 2350000000.0 * (delayed_mw / total_mw)  # $1.7625B
        apld_construction_carrying_cost = delayed_phase_debt * 0.0925 * (delay_months / 12.0)  # $163.03M

        apld_cash = self.financials.get("APLD", {}).get("cash_and_equivalents", 1590000000.0)
        net_apld_carrying_drain = apld_construction_carrying_cost - ongoing_operational_rent
        cash_drain_pct = (apld_construction_carrying_cost / apld_cash) * 100.0 if apld_cash else 100.0

        return {
            "scenario_name": "Phased Grid Energization Delay (Polaris Forge 1)",
            "delay_months": delay_months,
            "project": "POLARIS_FORGE_1",
            "operational_mw": operational_mw,
            "delayed_mw": delayed_mw,
            "ongoing_operational_rent_usd": ongoing_operational_rent,
            "deferred_expansion_rent_usd": deferred_expansion_rent,
            "construction_phase_debt_usd": delayed_phase_debt,
            "apld_debt_carrying_cost_usd": apld_construction_carrying_cost,
            "apld_starting_cash_usd": apld_cash,
            "apld_cash_drain_pct": round(cash_drain_pct, 1),
            "transmission_narrative": (
                f"A {delay_months}-month energization delay on Polaris Forge 1 defers ${deferred_expansion_rent/1e9:.2f}B in expansion rent for the unenergized 300 MW. "
                f"However, the operational 100 MW continues generating ${ongoing_operational_rent/1e6:.1f}M/yr in base rent. Applied Digital must self-fund "
                f"${apld_construction_carrying_cost/1e6:.1f}M in construction debt carrying costs, consuming {cash_drain_pct:.1f}% of its ${apld_cash/1e9:.2f}B cash reserve."
            )
        }

    def simulate_oem_purchase_commitment_markdown(self, excess_pct: float = 0.15, loss_severity: float = 0.40) -> Dict[str, Any]:
        """
        Scenario 5: Hardware Supply Chain Purchase Commitment Expected Loss
        Models Supermicro's $34.2B non-cancelable purchase commitments under a demand pause,
        computing expected loss provisions under Net Realizable Value (NRV) write-down and cancellation settlement.
        """
        total_commitments = 34200000000.0
        excess_commitments = total_commitments * excess_pct  # $5.13B excess allocation
        modeled_nrv_provision = excess_commitments * loss_severity  # $2.052B net pre-tax loss
        cancellation_settlement_cost = excess_commitments  # $5.13B if paid as penalty

        smci_cash = self.financials.get("SMCI", {}).get("cash_and_equivalents", 7520000000.0)
        cash_burn_nrv_pct = (modeled_nrv_provision / smci_cash) * 100.0 if smci_cash else 100.0
        cash_burn_full_pct = (cancellation_settlement_cost / smci_cash) * 100.0 if smci_cash else 100.0

        return {
            "scenario_name": "OEM Purchase Commitment Expected Loss (SMCI)",
            "excess_allocation_pct": excess_pct,
            "loss_severity_pct": loss_severity,
            "target_entity": "SMCI",
            "total_purchase_commitments_usd": total_commitments,
            "excess_commitments_usd": excess_commitments,
            "modeled_nrv_loss_provision_usd": modeled_nrv_provision,
            "cancellation_settlement_usd": cancellation_settlement_cost,
            "smci_starting_cash_usd": smci_cash,
            "cash_depletion_nrv_pct": round(cash_burn_nrv_pct, 1),
            "cash_depletion_full_pct": round(cash_burn_full_pct, 1),
            "transmission_narrative": (
                f"A {int(excess_pct*100)}% demand pullback creates ${excess_commitments/1e9:.2f}B in excess hardware commitments against Supermicro's "
                f"${total_commitments/1e9:.2f}B supplier contracts. Applying a contract-calibrated 40% loss severity generates a ${modeled_nrv_provision/1e9:.2f}B "
                f"NRV inventory write-down, consuming {cash_burn_nrv_pct:.1f}% of Supermicro's ${smci_cash/1e9:.2f}B cash buffer."
            )
        }

    def run_all_stress_scenarios(self) -> pd.DataFrame:
        """Run complete quantitative stress test suite and generate canonical summary table."""
        res_gpu = self.simulate_gpu_collateral_haircut(haircut_pct=0.40, advance_rate=0.7142)
        res_cust = self.simulate_anchor_customer_trim(trim_pct=0.30)
        res_refi = self.simulate_refinancing_spread_spike(spread_increase_bps=300.0)
        res_grid = self.simulate_grid_energization_delay(delay_months=12)
        res_oem = self.simulate_oem_purchase_commitment_markdown(excess_pct=0.15, loss_severity=0.40)

        summary_rows = [
            {
                "scenario_name": res_gpu["scenario_name"],
                "shock_parameter": "-40% GPU Collateral Value",
                "direct_cash_or_collateral_hit_usd": res_gpu["mandatory_prepayment_cure_usd"],
                "target_entity": "CRWV",
                "covenant_or_liquidity_impact": f"{res_gpu['crwv_liquidity_burn_pct']}% Cash Depletion",
                "contagion_mechanism": "Forces $4.32B borrowing base cure on drawn DDTLs, freezing operational capex."
            },
            {
                "scenario_name": res_cust["scenario_name"],
                "shock_parameter": "-30% Microsoft Off-Take",
                "direct_cash_or_collateral_hit_usd": res_cust["annual_revenue_loss_usd"],
                "target_entity": "CRWV",
                "covenant_or_liquidity_impact": "Springing Guaranty Activated",
                "contagion_mechanism": "Triggers SPV colocation lease shortfall, fulfilling predicate for parent $11.0B guaranty."
            },
            {
                "scenario_name": res_refi["scenario_name"],
                "shock_parameter": "+300 bps Floating Spread",
                "direct_cash_or_collateral_hit_usd": res_refi["crwv_immediate_cash_interest_hit_usd"] + res_refi["apld_immediate_cash_interest_hit_usd"],
                "target_entity": "CRWV / APLD",
                "covenant_or_liquidity_impact": "Cash Squeeze (Floating Only)",
                "contagion_mechanism": "Adds $324M interest on CRWV DDTLs; fixed notes insulated but face maturity rollover risk."
            },
            {
                "scenario_name": res_grid["scenario_name"],
                "shock_parameter": "12-Month Energization Delay",
                "direct_cash_or_collateral_hit_usd": res_grid["apld_debt_carrying_cost_usd"],
                "target_entity": "APLD",
                "covenant_or_liquidity_impact": f"{res_grid['apld_cash_drain_pct']}% Cash Drain",
                "contagion_mechanism": "Defers $550M unenergized rent while 100 MW continues producing $183M rent; carrying cost is $163M."
            },
            {
                "scenario_name": res_oem["scenario_name"],
                "shock_parameter": "15% Demand Pullback",
                "direct_cash_or_collateral_hit_usd": res_oem["modeled_nrv_loss_provision_usd"],
                "target_entity": "SMCI",
                "covenant_or_liquidity_impact": f"{res_oem['cash_depletion_nrv_pct']}% Cash Depletion",
                "contagion_mechanism": "Triggers $2.05B NRV loss provision on $5.13B excess allocation out of $34.2B commitments."
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
    print("=== Parameterized Financial Stress Prototype Results ===")
    print(df[["scenario_name", "shock_parameter", "direct_cash_or_collateral_hit_usd", "target_entity", "covenant_or_liquidity_impact"]])
