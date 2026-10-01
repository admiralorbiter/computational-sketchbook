"""
Phase 2.1 Level 1: Published Delay-Tolerance Milestone Surfaces & Parent Reconvergence Analysis
Generates empirical parameter surfaces, milestone arrival trajectories, and parent completion support
curves for Polaris Forge 1 across Silo 1 and Silo 2.

Epistemic Governance & Invariant Enforcement:
  1. Strict Silo Isolation: Zero cross-silo subsidization; waterfalls run in legal isolation.
  2. Absorbing Default Boundary & Censorship (Patch 2.1.4): Headline parent completion support
     strictly ceases accumulating once a silo reaches T_payment_shortfall. Unmodeled post-default
     continuation is isolated to diagnostic metrics.
  3. Zero Silent Priors: Every unobserved financial and schedule parameter is explicitly declared.
  4. State-Dependent Amortization Offset: Silo 2 principal amortization is explicitly tied to
     actual commencement date.
"""

from pathlib import Path
from typing import Dict, List, Any, Tuple
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

from phase2_level1_engine import (
    DeterministicDelayEngine,
    SiloTerms,
    AccountState,
    ConstructionScenario,
    RentScenario,
    AmortizationScenario,
    create_default_pf1_silos,
    demo_pf1_analyst_scenario,
    compute_delay_tolerance_surface,
    CANONICAL_PF1_START_DATE,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
TABLES_DIR = OUTPUTS_DIR / "tables"
FIGURES_DIR = OUTPUTS_DIR / "figures"
ANALYSIS_DIR = OUTPUTS_DIR / "analysis"

TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# 1. Surface Computation Pipelines
# -----------------------------------------------------------------------------

def generate_synchronized_delay_surface() -> pd.DataFrame:
    """Computes milestone arrivals and parent support across synchronized delay grid for 3 reserve tiers.
    
    Tiers:
      - Tier 1 (Zero Reserves): R_0,1 = $0, R_0,2 = $0
      - Tier 2 (6-Month Carry Reserve): R_0,1 = $108.6875M, R_0,2 = $55.65M
      - Tier 3 (12-Month Carry Reserve): R_0,1 = $217.375M, R_0,2 = $111.3M
    """
    print("  [1/4] Computing Synchronized Delay Milestone Surfaces (3 Reserve Tiers x 13 Delays)...")
    p = demo_pf1_analyst_scenario()
    
    delay_grid = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 24]
    
    reserve_tiers = [
        ("Zero_Reserve", 0.0, 0.0),
        ("6Mo_Carry_Reserve", 108_687_500.0, 55_650_000.0),
        ("12Mo_Carry_Reserve", 217_375_000.0, 111_300_000.0),
    ]
    
    rows = []
    engine = DeterministicDelayEngine(simulation_months=60)
    
    for tier_name, r1, r2 in reserve_tiers:
        for d in delay_grid:
            s1_init = AccountState(
                construction_cash=p["silo1_initial_construction_cash"],
                dsra_cash=r1,
                operating_cash=p["silo1_initial_operating_cash"],
            )
            s2_init = AccountState(
                construction_cash=p["silo2_initial_construction_cash"],
                dsra_cash=r2,
                operating_cash=p["silo2_initial_operating_cash"],
            )
            s1_const = ConstructionScenario(
                scheduled_commencement_month=p["scheduled_commencement_month_silo1"],
                delay_months=d,
                monthly_capex_burn=15_000_000.0,
                remaining_capex_total=p["silo1_remaining_capex_total"],
            )
            s2_const = ConstructionScenario(
                scheduled_commencement_month=p["scheduled_commencement_month_silo2"],
                delay_months=d,
                monthly_capex_burn=20_000_000.0,
                remaining_capex_total=p["silo2_remaining_capex_total"],
            )
            
            res = engine.run_pf1_simulation(
                s1_init, s2_init,
                s1_const, s2_const,
                p["silo1_rent_scenario"], p["silo2_rent_scenario"],
                p["silo1_amort_scenario"], p["silo2_amort_scenario"],
                waterfall_priority=p["waterfall_priority"],
            )
            
            headline_support = res.monthly_ledger["cumulative_parent_support_required_pre_shortfall_usd"].iloc[-1]
            unrestricted_support = res.monthly_ledger["cumulative_parent_support_required_unrestricted_diagnostic_usd"].iloc[-1]
            censored_support = unrestricted_support - headline_support
            
            rows.append({
                "reserve_tier": tier_name,
                "dsra_silo1": r1,
                "dsra_silo2": r2,
                "delay_months": d,
                "t_coverage_silo1": res.silo1_milestones.t_coverage,
                "t_oper_exhaustion_silo1": res.silo1_milestones.t_operating_exhaustion,
                "t_dsra_silo1": res.silo1_milestones.t_dsra,
                "t_completion_support_silo1": res.silo1_milestones.t_completion_support,
                "t_payment_shortfall_silo1": res.silo1_milestones.t_payment_shortfall,
                "t_coverage_silo2": res.silo2_milestones.t_coverage,
                "t_oper_exhaustion_silo2": res.silo2_milestones.t_operating_exhaustion,
                "t_dsra_silo2": res.silo2_milestones.t_dsra,
                "t_completion_support_silo2": res.silo2_milestones.t_completion_support,
                "t_payment_shortfall_silo2": res.silo2_milestones.t_payment_shortfall,
                "cumulative_parent_support_pre_shortfall_usd": headline_support,
                "cumulative_parent_support_unrestricted_diagnostic_usd": unrestricted_support,
                "censored_post_shortfall_support_usd": censored_support,
            })
            
    df = pd.DataFrame(rows)
    df.to_csv(TABLES_DIR / "phase2_delay_tolerance_surface_synchronized.csv", index=False)
    return df


def generate_decoupled_delay_surface() -> pd.DataFrame:
    """Computes the 2D decoupled delay surface across independent delay grids for Silo 1 and Silo 2."""
    print("  [2/4] Computing Decoupled Delay Matrix (7 x 7 = 49 combinations)...")
    p = demo_pf1_analyst_scenario()
    
    delay_grid_s1 = [0, 3, 6, 9, 12, 18, 24]
    delay_grid_s2 = [0, 3, 6, 9, 12, 18, 24]
    
    df = compute_delay_tolerance_surface(
        reserve_grid_silo1=[108_687_500.0],  # 6-month reserve
        reserve_grid_silo2=[55_650_000.0],   # 6-month reserve
        capex_burn_grid_silo1=[15_000_000.0],
        capex_burn_grid_silo2=[20_000_000.0],
        scheduled_commencement_month_silo1=p["scheduled_commencement_month_silo1"],
        scheduled_commencement_month_silo2=p["scheduled_commencement_month_silo2"],
        delay_grid_silo1=delay_grid_s1,
        delay_grid_silo2=delay_grid_s2,
        shared_campus_delay_mode=False,
        silo1_rent_scenario=p["silo1_rent_scenario"],
        silo2_rent_scenario=p["silo2_rent_scenario"],
        silo1_amort_scenario=p["silo1_amort_scenario"],
        silo2_amort_scenario=p["silo2_amort_scenario"],
        silo1_initial_construction_cash=p["silo1_initial_construction_cash"],
        silo2_initial_construction_cash=p["silo2_initial_construction_cash"],
        silo1_initial_operating_cash=p["silo1_initial_operating_cash"],
        silo2_initial_operating_cash=p["silo2_initial_operating_cash"],
        silo1_remaining_capex_total=p["silo1_remaining_capex_total"],
        silo2_remaining_capex_total=p["silo2_remaining_capex_total"],
        waterfall_priority=p["waterfall_priority"],
    )
    df.to_csv(TABLES_DIR / "phase2_delay_tolerance_surface_decoupled.csv", index=False)
    return df


def generate_amortization_offset_trajectory() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Computes monthly trajectory for Silo 2 comparing on-time vs delayed commencement."""
    print("  [3/4] Computing State-Dependent Amortization Offset Trajectory...")
    p = demo_pf1_analyst_scenario()
    _, s2_terms = create_default_pf1_silos()
    engine = DeterministicDelayEngine(simulation_months=60)
    
    # Run Case A: On-time (commencement month 18)
    s2_init = AccountState(
        construction_cash=p["silo2_initial_construction_cash"],
        dsra_cash=111_300_000.0,
        operating_cash=50_000_000.0,
    )
    const_ontime = ConstructionScenario(
        scheduled_commencement_month=18,
        delay_months=0,
        monthly_capex_burn=20_000_000.0,
        remaining_capex_total=p["silo2_remaining_capex_total"],
    )
    df_ontime, m_ontime = engine.run_silo_waterfall(
        s2_terms, s2_init, const_ontime, p["silo2_rent_scenario"], p["silo2_amort_scenario"]
    )
    
    # Run Case B: Delayed by 6 months (commencement month 24)
    const_delayed = ConstructionScenario(
        scheduled_commencement_month=18,
        delay_months=6,
        monthly_capex_burn=20_000_000.0,
        remaining_capex_total=p["silo2_remaining_capex_total"],
    )
    df_delayed, m_delayed = engine.run_silo_waterfall(
        s2_terms, s2_init, const_delayed, p["silo2_rent_scenario"], p["silo2_amort_scenario"]
    )
    
    return df_ontime, df_delayed


def generate_waterfall_priority_comparison() -> pd.DataFrame:
    """Evaluates arrival of milestones under opex_first vs debt_service_first priority."""
    print("  [4/4] Evaluating Waterfall Priority Sensitivity (opex_first vs debt_service_first)...")
    p = demo_pf1_analyst_scenario()
    engine = DeterministicDelayEngine(simulation_months=60)
    delay_grid = [0, 3, 6, 9, 12, 18]
    
    rows = []
    for priority in ("opex_first", "debt_service_first"):
        for d in delay_grid:
            s1_init = AccountState(
                construction_cash=p["silo1_initial_construction_cash"],
                dsra_cash=108_687_500.0,
                operating_cash=p["silo1_initial_operating_cash"],
            )
            s2_init = AccountState(
                construction_cash=p["silo2_initial_construction_cash"],
                dsra_cash=55_650_000.0,
                operating_cash=p["silo2_initial_operating_cash"],
            )
            s1_const = ConstructionScenario(
                scheduled_commencement_month=p["scheduled_commencement_month_silo1"],
                delay_months=d,
                monthly_capex_burn=15_000_000.0,
                remaining_capex_total=p["silo1_remaining_capex_total"],
            )
            s2_const = ConstructionScenario(
                scheduled_commencement_month=p["scheduled_commencement_month_silo2"],
                delay_months=d,
                monthly_capex_burn=20_000_000.0,
                remaining_capex_total=p["silo2_remaining_capex_total"],
            )
            
            res = engine.run_pf1_simulation(
                s1_init, s2_init,
                s1_const, s2_const,
                p["silo1_rent_scenario"], p["silo2_rent_scenario"],
                p["silo1_amort_scenario"], p["silo2_amort_scenario"],
                waterfall_priority=priority,
            )
            
            rows.append({
                "waterfall_priority": priority,
                "delay_months": d,
                "t_oper_exhaustion_silo1": res.silo1_milestones.t_operating_exhaustion,
                "t_dsra_silo1": res.silo1_milestones.t_dsra,
                "t_payment_shortfall_silo1": res.silo1_milestones.t_payment_shortfall,
                "t_oper_exhaustion_silo2": res.silo2_milestones.t_operating_exhaustion,
                "t_dsra_silo2": res.silo2_milestones.t_dsra,
                "t_payment_shortfall_silo2": res.silo2_milestones.t_payment_shortfall,
                "cumulative_parent_support_pre_shortfall_usd": res.monthly_ledger["cumulative_parent_support_required_pre_shortfall_usd"].iloc[-1],
            })
            
    df = pd.DataFrame(rows)
    df.to_csv(TABLES_DIR / "phase2_waterfall_priority_sensitivity.csv", index=False)
    return df


# -----------------------------------------------------------------------------
# 2. Publication Figure Generation
# -----------------------------------------------------------------------------

def plot_published_surfaces(
    sync_df: pd.DataFrame,
    decoupled_df: pd.DataFrame,
    df_ontime: pd.DataFrame,
    df_delayed: pd.DataFrame,
    priority_df: pd.DataFrame,
):
    """Generates the master 4-panel publication figure."""
    print("\nGenerating Master Publication Figure: outputs/figures/phase2_delay_tolerance_surfaces.png...")
    
    # Style setup
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "figure.titlesize": 13,
    })
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=300)
    fig.suptitle(
        "Polaris Forge 1 (PF1) Level 1 Deterministic Milestone Surfaces & Parent Overlay\n"
        "Strict Silo Isolation, Absorbing Boundary Censorship (Patch 2.1.4), and State-Dependent Amortization",
        fontweight="bold",
        y=0.98,
    )
    
    # -------------------------------------------------------------------------
    # Panel A: Delay vs Cumulative Parent Support Required (Headline vs Diagnostic)
    # -------------------------------------------------------------------------
    ax_a = axes[0, 0]
    ax_a.set_title("A. Cumulative Parent Support Required vs Delay (Headline vs Continuation)", fontweight="bold")
    
    colors = {"Zero_Reserve": "#e74c3c", "6Mo_Carry_Reserve": "#2980b9", "12Mo_Carry_Reserve": "#27ae60"}
    labels = {
        "Zero_Reserve": "Zero DSRA Reserve",
        "6Mo_Carry_Reserve": "6-Month Carry Reserve ($164.3M total)",
        "12Mo_Carry_Reserve": "12-Month Carry Reserve ($328.7M total)",
    }
    
    for tier, grp in sync_df.groupby("reserve_tier"):
        grp = grp.sort_values("delay_months")
        c = colors.get(tier, "black")
        lbl = labels.get(tier, tier)
        
        # Valid headline (pre-shortfall)
        ax_a.plot(
            grp["delay_months"],
            grp["cumulative_parent_support_pre_shortfall_usd"] / 1e6,
            marker="o",
            linewidth=2.2,
            color=c,
            label=f"{lbl} (Valid Pre-Shortfall)",
        )
        # Unrestricted continuation (diagnostic dashed)
        ax_a.plot(
            grp["delay_months"],
            grp["cumulative_parent_support_unrestricted_diagnostic_usd"] / 1e6,
            linestyle="--",
            linewidth=1.5,
            color=c,
            alpha=0.6,
            label=f"{lbl} (Unrestricted Diagnostic)",
        )
        
        # Highlight censorship area where unrestricted diverged from pre-shortfall
        censored_mask = grp["censored_post_shortfall_support_usd"] > 0
        if censored_mask.any():
            ax_a.fill_between(
                grp["delay_months"],
                grp["cumulative_parent_support_pre_shortfall_usd"] / 1e6,
                grp["cumulative_parent_support_unrestricted_diagnostic_usd"] / 1e6,
                color=c,
                alpha=0.12,
            )
            
    ax_a.set_xlabel("Synchronized Delay Across Both Silos (Months)")
    ax_a.set_ylabel("Cumulative Parent Support Required ($ Millions)")
    ax_a.grid(True, linestyle=":", alpha=0.6)
    ax_a.legend(loc="upper left", framealpha=0.9)
    ax_a.yaxis.set_major_formatter(ticker.FormatStrFormatter("$%.0fM"))
    ax_a.set_xlim(-0.5, 24.5)
    
    # Annotation on absorbing boundary censorship
    ax_a.annotate(
        "Shaded Region:\nUnmodeled Post-Default\nContinuation Censored\nby Patch 2.1.4",
        xy=(15, 250),
        xytext=(14, 150),
        arrowprops=dict(facecolor="#34495e", arrowstyle="->", lw=1.2),
        bbox=dict(boxstyle="round,pad=0.3", fc="#f8f9fa", ec="#bdc3c7", lw=1),
        fontsize=8.5,
    )
    
    # -------------------------------------------------------------------------
    # Panel B: Milestone Arrival Trajectories Across Delays (Silo 1 vs Silo 2)
    # -------------------------------------------------------------------------
    ax_b = axes[0, 1]
    ax_b.set_title("B. Independent Milestone Arrival Trajectories (6-Month Reserve Tier)", fontweight="bold")
    
    tier_6m = sync_df[sync_df["reserve_tier"] == "6Mo_Carry_Reserve"].sort_values("delay_months")
    
    # Silo 1 Milestones
    ax_b.plot(tier_6m["delay_months"], tier_6m["t_completion_support_silo1"], "s-", color="#e67e22", label="Silo 1: T_completion_support", lw=2)
    ax_b.plot(tier_6m["delay_months"], tier_6m["t_dsra_silo1"], "^-", color="#d35400", label="Silo 1: T_dsra", lw=2)
    ax_b.plot(tier_6m["delay_months"], tier_6m["t_payment_shortfall_silo1"], "x--", color="#c0392b", label="Silo 1: T_payment_shortfall", lw=2)
    
    # Silo 2 Milestones
    ax_b.plot(tier_6m["delay_months"], tier_6m["t_completion_support_silo2"], "o-", color="#3498db", label="Silo 2: T_completion_support", lw=2)
    ax_b.plot(tier_6m["delay_months"], tier_6m["t_dsra_silo2"], "v-", color="#2980b9", label="Silo 2: T_dsra", lw=2)
    ax_b.plot(tier_6m["delay_months"], tier_6m["t_payment_shortfall_silo2"], "+--", color="#1f618d", label="Silo 2: T_payment_shortfall", lw=2)
    
    ax_b.set_xlabel("Synchronized Delay Across Both Silos (Months)")
    ax_b.set_ylabel("Milestone Arrival Month (from July 1, 2026)")
    ax_b.grid(True, linestyle=":", alpha=0.6)
    ax_b.legend(loc="upper left", framealpha=0.9, ncol=2)
    ax_b.yaxis.set_major_locator(ticker.MultipleLocator(6))
    ax_b.set_xlim(-0.5, 24.5)
    
    # -------------------------------------------------------------------------
    # Panel C: Decoupled Silo Delay Surface Heatmap: Parent Support ($M)
    # -------------------------------------------------------------------------
    ax_c = axes[1, 0]
    ax_c.set_title("C. Decoupled Silo Delay Matrix: Valid Parent Support ($M)", fontweight="bold")
    
    pivot_support = decoupled_df.pivot(
        index="delay_months_silo1",
        columns="delay_months_silo2",
        values="cumulative_parent_support_required_pre_shortfall_usd",
    ) / 1e6
    
    im = ax_c.imshow(
        pivot_support.values,
        origin="lower",
        cmap="YlOrRd",
        aspect="auto",
    )
    cbar = fig.colorbar(im, ax=ax_c)
    cbar.set_label("Cumulative Parent Support Required ($M)")
    
    # Set tick labels
    ax_c.set_xticks(range(len(pivot_support.columns)))
    ax_c.set_xticklabels([f"{c}m" for c in pivot_support.columns])
    ax_c.set_yticks(range(len(pivot_support.index)))
    ax_c.set_yticklabels([f"{r}m" for r in pivot_support.index])
    ax_c.set_xlabel("Silo 2 Delay (Months)")
    ax_c.set_ylabel("Silo 1 Delay (Months)")
    
    # Overlay values in heatmap cells
    for i in range(len(pivot_support.index)):
        for j in range(len(pivot_support.columns)):
            val = pivot_support.values[i, j]
            text_color = "white" if val > pivot_support.values.max() * 0.65 else "black"
            ax_c.text(j, i, f"${val:.0f}M", ha="center", va="center", color=text_color, fontsize=8, fontweight="bold")
            
    # -------------------------------------------------------------------------
    # Panel D: State-Dependent Principal Amortization Structural Offset (Silo 2)
    # -------------------------------------------------------------------------
    ax_d = axes[1, 1]
    ax_d.set_title("D. Silo 2 State-Dependent Principal Amortization Offset", fontweight="bold")
    
    m_range = range(1, 40)
    sub_ontime = df_ontime[df_ontime["month"].isin(m_range)]
    sub_delayed = df_delayed[df_delayed["month"].isin(m_range)]
    
    ax_d.plot(
        sub_ontime["month"],
        sub_ontime["total_debt_service_due"] / 1e6,
        "k-o",
        label="On-Time Commencement (Month 18) -> Amort starts Month 24",
        lw=2,
        markersize=4,
    )
    ax_d.plot(
        sub_delayed["month"],
        sub_delayed["total_debt_service_due"] / 1e6,
        "r--s",
        label="Delayed 6 Months (Month 24) -> Amort starts Month 30",
        lw=2,
        markersize=4,
    )
    
    # Highlight the cash relief offset window in Month 24
    m24_ontime_ds = sub_ontime[sub_ontime["month"] == 24]["total_debt_service_due"].iloc[0] / 1e6
    m24_delayed_ds = sub_delayed[sub_delayed["month"] == 24]["total_debt_service_due"].iloc[0] / 1e6
    relief_amount = m24_ontime_ds - m24_delayed_ds
    
    ax_d.fill_between(
        [23.5, 24.5],
        [m24_delayed_ds, m24_delayed_ds],
        [m24_ontime_ds, m24_ontime_ds],
        color="#2ecc71",
        alpha=0.3,
        label=f"Amortization Deferral Relief (-${relief_amount:.1f}M)",
    )
    
    ax_d.annotate(
        f"Month 24 Cash Relief:\nDelayed owes ${m24_delayed_ds:.1f}M coupon,\n"
        f"saving ${relief_amount:.1f}M principal installment!",
        xy=(24, m24_delayed_ds),
        xytext=(26, 180),
        arrowprops=dict(facecolor="#27ae60", arrowstyle="->", lw=1.5),
        bbox=dict(boxstyle="round,pad=0.3", fc="#eafaf1", ec="#27ae60", lw=1),
        fontsize=8.5,
    )
    
    ax_d.set_xlabel("Simulation Month (from July 1, 2026)")
    ax_d.set_ylabel("Total Silo 2 Debt Service Due ($ Millions)")
    ax_d.grid(True, linestyle=":", alpha=0.6)
    ax_d.legend(loc="upper left", framealpha=0.9)
    ax_d.yaxis.set_major_formatter(ticker.FormatStrFormatter("$%.0fM"))
    ax_d.set_xlim(12, 38)
    
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    output_path = FIGURES_DIR / "phase2_delay_tolerance_surfaces.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Master figure saved successfully: {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")


# -----------------------------------------------------------------------------
# 3. Main Execution
# -----------------------------------------------------------------------------

def main():
    print("================================================================================")
    print("PHASE 2.1 LEVEL 1: PUBLISHED DELAY-TOLERANCE MILESTONE SURFACES")
    print("================================================================================")
    
    # 1. Compute synchronized delay surfaces
    sync_df = generate_synchronized_delay_surface()
    print(f"  -> Generated {len(sync_df)} rows for synchronized delay surfaces.")
    
    # 2. Compute decoupled delay surfaces
    decoupled_df = generate_decoupled_delay_surface()
    print(f"  -> Generated {len(decoupled_df)} rows for decoupled delay surfaces.")
    
    # 3. Compute state-dependent amortization offset trajectories
    df_ontime, df_delayed = generate_amortization_offset_trajectory()
    print("  -> Generated on-time and delayed trajectories for Silo 2.")
    
    # 4. Compute waterfall priority sensitivity
    priority_df = generate_waterfall_priority_comparison()
    print(f"  -> Generated {len(priority_df)} rows for waterfall priority sensitivity.")
    
    # 5. Plot master publication figure
    plot_published_surfaces(sync_df, decoupled_df, df_ontime, df_delayed, priority_df)
    
    print("\n[SUCCESS] All published parameter surfaces and figures generated successfully.")


if __name__ == "__main__":
    main()
