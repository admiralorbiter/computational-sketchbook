"""
Analysis Engine: Energization-at-Risk & Capital Synchronization Resilience (Task 021 / ADR-021.1)
Implements ADR-021.1 Stage B Analysis.

Calculates:
1. Facility-by-facility attribution table with typed completion dimensions:
   - utility_service_capacity_mw
   - utility_load_online_mw
   - critical_it_contracted_mw
   - service_ready_it_mw
   - gpu_equipment_deployment_state
   - gpu_compute_operational_mw
   (Preserves unknown/null without synthetic zero imputation).
2. Capital-at-Risk Before Service:
   - Facility-attributable funded debt: strictly $6,090.0M ($6.090B, APLD ComputeCo SPVs).
   - Committed equipment financing capacity: $2,400.0M ($2.400B, IREN Mackenzie).
   - Active corporate unallocated debt: $39,357.68M ($39.358B).
3. Exact coupon carrying costs:
   - PF1: $2.35B @ 9.25% ($217.375M) + $1.59B @ 7.00% ($111.300M) = $328.675M/yr
   - PF2: $2.15B @ 6.75% = $145.125M/yr
   - Total APLD project interest = $473.800M/yr
   - IREN Mackenzie: $216.0M/yr full-capacity coupon equivalent (not current carry).
4. Phased lease delay sensitivity:
   - Building 2 (100 MW) service-ready in Oct 2025.
   - Uncommissioned space (300 MW / 75%) exposed to delay: $550.0M/yr base ($275.0M / 6 mo).
5. Capital Synchronization Resilience:
   - Escrow holding (PF2 held until June 18, 2026).
   - Staged funding on equipment acceptance (IREN Dec 31, 2026 cliff).
   - Uncapped completion indemnities (ELN-02 / ELN-03).
"""

from pathlib import Path
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"
ANALYSIS_DIR = OUTPUTS_DIR / "analysis"
FIGURES_DIR = OUTPUTS_DIR / "figures"

ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def run_energization_analysis():
    # Load canonical datasets
    fac_df = pd.read_parquet(PROCESSED_DIR / "facilities.parquet")
    lnk_df = pd.read_parquet(PROCESSED_DIR / "obligation_facility_links.parquet")
    obl_df = pd.read_parquet(PROCESSED_DIR / "obligations.parquet")

    # -------------------------------------------------------------
    # 1. Typed Physical & Contractual Completion Dimensions
    # -------------------------------------------------------------
    # Primary source facts: utility capacity vs IT capacity vs GPU state
    typed_facility_dimensions = {
        "FAC-APLD-POLARIS-FORGE-1": {
            "utility_service_capacity_mw": 350.0,  # MDU ESA approved incremental capacity (180 MW initial)
            "utility_load_online_mw": 60.0,        # MDU incremental online load at PF1
            "critical_it_contracted_mw": 400.0,    # CoreWeave 15-yr master lease (Bldgs 2, 3, 4)
            "service_ready_it_mw": 100.0,          # Bldg 2 service-ready Oct 2025; Bldg 3 (150 MW) partial
            "gpu_equipment_deployment_state": "Tenant (CoreWeave) cluster commissioning & fit-out",
            "gpu_compute_operational_mw": None,    # Undisclosed / tenant-managed
            "next_milestone": "Building 2 full tenant occupancy & Building 3 commissioning (2026-2027)",
            "evidence_completeness": "Class A (10-K, 8-K, Ex 10.1 & 10.2)"
        },
        "FAC-APLD-POLARIS-FORGE-2": {
            "utility_service_capacity_mw": None,   # Pending service agreement finalization
            "utility_load_online_mw": None,        # Pre-energization
            "critical_it_contracted_mw": 200.0,    # Hyperscaler anchor lease
            "service_ready_it_mw": 0.0,            # Under construction
            "gpu_equipment_deployment_state": "Civil / electrical shell construction",
            "gpu_compute_operational_mw": None,
            "next_milestone": "Initial capacity H2 2026; full 200 MW early 2027",
            "evidence_completeness": "Class A (10-K Item 1 & Note 10)"
        },
        "FAC-IREN-MACKENZIE": {
            "utility_service_capacity_mw": 80.0,   # BC Hydro connection agreement (operating since April 2022)
            "utility_load_online_mw": 80.0,        # Fully energized data center campus
            "critical_it_contracted_mw": 80.0,     # Data center IT capacity
            "service_ready_it_mw": 80.0,           # Operational facility infrastructure
            "gpu_equipment_deployment_state": "Staged GPU server delivery & acceptance through Dec 31, 2026",
            "gpu_compute_operational_mw": None,    # Undisclosed point-in-time GPU deployment
            "next_milestone": "GPU server staged delivery & acceptance through Dec 31, 2026",
            "evidence_completeness": "Class A (10-K Note August 2026 Financing)"
        },
        "FAC-CORZ-DENTON": {
            "utility_service_capacity_mw": 394.0,  # Denton Municipal Electric total utility agreement
            "utility_load_online_mw": 100.0,       # Energized operating colocation capacity
            "critical_it_contracted_mw": 270.0,    # CoreWeave leased colocation capacity
            "service_ready_it_mw": 100.0,          # Operating data hall capacity
            "gpu_equipment_deployment_state": "Tenant fit-out / ongoing colocation conversion",
            "gpu_compute_operational_mw": None,
            "next_milestone": "Colocation fit-out across multi-building campus",
            "evidence_completeness": "Class A (10-K, 8-K Note Denton Lease)"
        },
        "FAC-CORZ-DALTON": {
            "utility_service_capacity_mw": 195.0,  # Dalton Utilities
            "utility_load_online_mw": None,        # Undisclosed operating split
            "critical_it_contracted_mw": None,     # Multi-facility contract allocation
            "service_ready_it_mw": None,
            "gpu_equipment_deployment_state": "HPC infrastructure retrofit from mining",
            "gpu_compute_operational_mw": None,
            "next_milestone": "HPC infrastructure retrofit from mining",
            "evidence_completeness": "Class A (10-K Colocation table)"
        },
        "FAC-CORZ-MUSKOGEE": {
            "utility_service_capacity_mw": 100.0,  # OG&E
            "utility_load_online_mw": None,
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": None,
            "gpu_equipment_deployment_state": "HPC infrastructure retrofit from mining",
            "gpu_compute_operational_mw": None,
            "next_milestone": "HPC infrastructure retrofit from mining",
            "evidence_completeness": "Class A (10-K Colocation table)"
        },
        "FAC-CORZ-MARBLE": {
            "utility_service_capacity_mw": 117.0,  # Duke Energy (82 MW) + Murphy EPB (35 MW)
            "utility_load_online_mw": None,
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": None,
            "gpu_equipment_deployment_state": "HPC infrastructure retrofit from mining",
            "gpu_compute_operational_mw": None,
            "next_milestone": "HPC infrastructure retrofit from mining",
            "evidence_completeness": "Class A (10-K Colocation table)"
        },
        "FAC-CORZ-AUSTIN": {
            "utility_service_capacity_mw": 20.0,   # Austin Energy
            "utility_load_online_mw": None,
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": None,
            "gpu_equipment_deployment_state": "HPC infrastructure retrofit from mining",
            "gpu_compute_operational_mw": None,
            "next_milestone": "HPC infrastructure retrofit from mining",
            "evidence_completeness": "Class A (10-K Colocation table)"
        },
        "FAC-WULF-LAKE-MARINER": {
            "utility_service_capacity_mw": 226.0,  # NYPA hydro + National Grid
            "utility_load_online_mw": 226.0,       # Energized operating capacity
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": 226.0,
            "gpu_equipment_deployment_state": "Operational mining / 500 MW expansion engineering",
            "gpu_compute_operational_mw": None,
            "next_milestone": "500 MW planned expansion engineering",
            "evidence_completeness": "Class A (10-K NYPA allocation)"
        },
        "FAC-IREN-CHILDRESS": {
            "utility_service_capacity_mw": 750.0,  # Connection agreement capacity
            "utility_load_online_mw": 650.0,       # Operating substation load
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": 650.0,
            "gpu_equipment_deployment_state": "Operating mining & cloud pilot",
            "gpu_compute_operational_mw": None,
            "next_milestone": "Final 100 MW substation expansion to 750 MW",
            "evidence_completeness": "Class A (10-K Item 1 & Note 7)"
        },
        "FAC-IREN-SWEETWATER-1": {
            "utility_service_capacity_mw": 1400.0, # Connection agreement executed (not energized)
            "utility_load_online_mw": None,
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": 0.0,
            "gpu_equipment_deployment_state": "Substation procurement & interconnection construction",
            "gpu_compute_operational_mw": None,
            "next_milestone": "Interconnection substation construction (1,400 MW)",
            "evidence_completeness": "Class A (10-K Item 1)"
        },
        "FAC-IREN-SWEETWATER-2": {
            "utility_service_capacity_mw": 600.0,  # Connection agreement executed (not energized)
            "utility_load_online_mw": None,
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": 0.0,
            "gpu_equipment_deployment_state": "AEP Texas substation engineering",
            "gpu_compute_operational_mw": None,
            "next_milestone": "AEP Texas 600 MW substation engineering",
            "evidence_completeness": "Class A (10-K Item 1)"
        },
        "FAC-NBIS-MANTSALA": {
            "utility_service_capacity_mw": 75.0,   # Nivos grid connection
            "utility_load_online_mw": 75.0,        # Fully energized commercial service
            "critical_it_contracted_mw": 75.0,
            "service_ready_it_mw": 75.0,
            "gpu_equipment_deployment_state": "Fully operational GPU cluster operations",
            "gpu_compute_operational_mw": 75.0,
            "next_milestone": "Commercial operational service / heat recovery",
            "evidence_completeness": "Class A (10-K & Utility Primary Source)"
        },
        "FAC-NBIS-LAPPEENRANTA": {
            "utility_service_capacity_mw": 310.0,  # Planned grid connection capacity
            "utility_load_online_mw": None,
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": 0.0,
            "gpu_equipment_deployment_state": "Engineering design / pre-construction",
            "gpu_compute_operational_mw": None,
            "next_milestone": "Pending grid interconnection & engineering review",
            "evidence_completeness": "Class B (10-K development announcement)"
        }
    }

    facility_rows = []
    for _, fac in fac_df.iterrows():
        fid = fac["facility_id"]
        fname = fac["facility_name"]
        op = fac["operator_entity_id"]
        dims = typed_facility_dimensions.get(fid, {})

        flinks = lnk_df[lnk_df["facility_id"] == fid]

        # Funded attributable debt (APLD ComputeCo notes only)
        funded_rows = flinks[flinks["amount_type"] == "funded_principal"]
        attributable_funded_debt = funded_rows["allocated_amount"].sum() if not funded_rows.empty else 0.0

        # Committed financing capacity (IREN August 2026 agreements)
        cap_rows = flinks[flinks["amount_type"] == "facility_capacity"]
        committed_financing_capacity = cap_rows["allocated_amount"].sum() if not cap_rows.empty else 0.0

        # Customer / lease commitment
        lease_rows = flinks[flinks["link_type"].isin(["direct_lease", "direct_customer_contract"])]
        attributable_lease = lease_rows["allocated_amount"].sum() if not lease_rows.empty else 0.0

        facility_rows.append({
            "facility_id": fid,
            "facility_name": fname,
            "operator_entity_id": op,
            "attributable_funded_debt_m": attributable_funded_debt / 1e6,
            "committed_financing_capacity_m": committed_financing_capacity / 1e6,
            "customer_lease_commitment_m": attributable_lease / 1e6,
            "utility_service_capacity_mw": dims.get("utility_service_capacity_mw"),
            "utility_load_online_mw": dims.get("utility_load_online_mw"),
            "critical_it_contracted_mw": dims.get("critical_it_contracted_mw"),
            "service_ready_it_mw": dims.get("service_ready_it_mw"),
            "gpu_equipment_deployment_state": dims.get("gpu_equipment_deployment_state"),
            "gpu_compute_operational_mw": dims.get("gpu_compute_operational_mw"),
            "next_milestone": dims.get("next_milestone", "Operational"),
            "evidence_completeness": dims.get("evidence_completeness", "Class A")
        })

    table_df = pd.DataFrame(facility_rows)
    table_df.to_csv(ANALYSIS_DIR / "facility_attribution_table.csv", index=False)

    # -------------------------------------------------------------
    # 2. Systemic Aggregates & Capital-at-Risk Before Service
    # -------------------------------------------------------------
    # Total facility-attributable funded debt is strictly $6,090.0M ($6.090B, APLD only)
    total_funded_debt = table_df["attributable_funded_debt_m"].sum()
    assert abs(total_funded_debt - 6090.0) < 1e-3, f"Expected $6,090M funded debt, got {total_funded_debt}"

    # Committed capacity is $2,400.0M ($2.400B, IREN Mackenzie)
    total_committed_cap = table_df["committed_financing_capacity_m"].sum()
    assert abs(total_committed_cap - 2400.0) < 1e-3, f"Expected $2,400M committed cap, got {total_committed_cap}"

    # Incomplete facilities with funded debt: PF1 ($3.94B) and PF2 ($2.15B) = $6.090B
    # Note: PF1 Building 2 (100 MW) is service-ready, but Buildings 3 and 4 (300 MW / 75%) are under construction
    capital_at_risk_before_service = total_funded_debt  # $6,090.0M

    # Unallocated corporate debt
    corp_links = lnk_df[lnk_df["allocation_scope"] == "corporate_unallocated"]
    corp_obls = obl_df[obl_df["obligation_id"].isin(corp_links["obligation_id"]) & (obl_df["amount_type"] == "principal_outstanding")]
    active_corp = corp_obls[corp_obls["valid_to"].isna() | (corp_obls["valid_to"] > "2026-09-28")]
    total_active_corp_debt = active_corp["amount"].sum() / 1e6  # $39,357.68M

    # -------------------------------------------------------------
    # 3. Exact Coupon Carrying Costs & Sensitivity Derivations
    # -------------------------------------------------------------
    # APLD Project Notes Interest Carry (Exact):
    # - PF1 2030 Notes: $2,350M @ 9.250% = $217.375M/yr
    # - PF1 2031 Notes (ComputeCo 3): $1,590M @ 7.000% = $111.300M/yr
    # - PF2 2031 Notes (ComputeCo 2): $2,150M @ 6.750% = $145.125M/yr
    # Total APLD Annual Carrying Cost = $473.800M/yr
    apld_annual_carrying_cost = (2350.0 * 0.0925) + (1590.0 * 0.0700) + (2150.0 * 0.0675)
    assert abs(apld_annual_carrying_cost - 473.8) < 1e-3, f"Carrying cost mismatch: {apld_annual_carrying_cost}"

    # IREN Mackenzie Full-Capacity Coupon Equivalent:
    # $2,400M @ 9.00% = $216.0M/yr (committed capacity coupon equivalent, not observed carry)
    iren_coupon_equivalent = 2400.0 * 0.0900

    # Phased Lease Revenue Delay on Uncommissioned Space:
    # APLD 15-yr master lease: $11.0B total = $733.33M/yr across 400 MW ($1.833M/MW/yr)
    # Building 2 (100 MW) is service-ready in Oct 2025 (generating or ready for lease revenue).
    # Uncommissioned space: Buildings 3 and 4 (300 MW out of 400 MW = 75%).
    # Maximum uncommissioned delayed lease cash flow = 75% * $733.33M = $550.0M/yr.
    annual_uncommissioned_lease_delay = (11000.0 / 15.0) * (300.0 / 400.0)  # $550.0M/yr

    slippage_scenarios = {
        "6_month_delay": {
            "apld_debt_carrying_cost_m": round(apld_annual_carrying_cost * 0.5, 3),  # $236.900M
            "iren_full_capacity_coupon_equivalent_m": round(iren_coupon_equivalent * 0.5, 3), # $108.0M
            "phased_uncommissioned_lease_delayed_m": round(annual_uncommissioned_lease_delay * 0.5, 3), # $275.0M
            "qualitative_risk_tier": "Modeled Hypothesis: Moderate (Reserves & Escrow Cushion Active)",
            "iren_financing_mechanism": "Staged equipment acceptance funding window expires Dec 31, 2026; un-drawn capacity may expire or require extension.",
            "covenant_and_resilience_notes": "PF2 escrow release already satisfied (June 18, 2026); ELN-02/ELN-03 springing indemnities provide CoreWeave completion backstop."
        },
        "12_month_delay": {
            "apld_debt_carrying_cost_m": round(apld_annual_carrying_cost * 1.0, 3),  # $473.800M
            "iren_full_capacity_coupon_equivalent_m": round(iren_coupon_equivalent * 1.0, 3), # $216.0M
            "phased_uncommissioned_lease_delayed_m": round(annual_uncommissioned_lease_delay * 1.0, 3), # $550.0M
            "qualitative_risk_tier": "Modeled Hypothesis: High (Carrying Costs Consume Liquidity Buffers)",
            "iren_financing_mechanism": "30-month maturity clock on drawn tranches begins amortizing; un-drawn capacity unavailable without formal credit amendment.",
            "covenant_and_resilience_notes": "Uncommissioned space lease delays require parent equity injections or debt service reserve drawdowns unless CoreWeave indemnities cure shortfall."
        },
        "18_month_delay": {
            "apld_debt_carrying_cost_m": round(apld_annual_carrying_cost * 1.5, 3),  # $710.700M
            "iren_full_capacity_coupon_equivalent_m": round(iren_coupon_equivalent * 1.5, 3), # $324.0M
            "phased_uncommissioned_lease_delayed_m": round(annual_uncommissioned_lease_delay * 1.5, 3), # $825.0M
            "qualitative_risk_tier": "Modeled Hypothesis: Critical (Restructuring or Refinancing Required)",
            "iren_financing_mechanism": "Over 50% of 30-month note term consumed without productive GPU ARR on drawn equipment.",
            "covenant_and_resilience_notes": "Project SPV debt service defaults probable without major corporate refinancing or equity recapitalization."
        }
    }

    # -------------------------------------------------------------
    # 4. Save JSON Summary
    # -------------------------------------------------------------
    summary = {
        "task": "Task 021 - Energization-at-Risk & Capital Synchronization Resilience",
        "stage": "ADR-021.1 Certified",
        "total_modeled_facilities": len(table_df),
        "total_facility_attributable_funded_debt_m": total_funded_debt,
        "total_committed_equipment_financing_capacity_m": total_committed_cap,
        "capital_at_risk_before_service_m": capital_at_risk_before_service,
        "capital_at_risk_funded_debt_pct": 100.0 * (capital_at_risk_before_service / total_funded_debt),
        "total_active_unallocated_corporate_debt_m": round(total_active_corp_debt, 2),
        "annual_funded_debt_carrying_cost_apld_m": round(apld_annual_carrying_cost, 3),
        "annual_iren_full_capacity_coupon_equivalent_m": round(iren_coupon_equivalent, 3),
        "annual_uncommissioned_lease_revenue_at_risk_m": round(annual_uncommissioned_lease_delay, 3),
        "synchronization_resilience_mechanisms": {
            "escrow_protections": "APLD PF2 $2.15B held in escrow from March 10, 2026 until condition satisfaction on June 18, 2026.",
            "staged_funding": "IREN $2.4B MFSA & Notes fund pro rata upon delivery and acceptance through Dec 31, 2026.",
            "completion_support": "CoreWeave uncapped legal indemnities (ELN-02 & ELN-03) protect Building 2 and Building 3 cash flows."
        },
        "slippage_scenarios": slippage_scenarios,
        "facility_metrics": facility_rows
    }

    with open(ANALYSIS_DIR / "energization_at_risk_summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    # -------------------------------------------------------------
    # 5. Generate Publication Visualizations
    # -------------------------------------------------------------
    # Figure 1: Capital Allocation Architecture vs Physical Energization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={'width_ratios': [1.2, 1]})

    # Panel A: Capital Structure (Funded Project Debt vs Committed Capacity vs Corporate)
    categories = ["APLD Project Debt\n(Funded SPV)", "IREN Mackenzie\n(Committed Cap)", "Unallocated Corporate\n(CRWV, WULF, etc.)"]
    amounts = [total_funded_debt / 1e3, total_committed_cap / 1e3, total_active_corp_debt / 1e3]
    colors = ["#d95f02", "#7570b3", "#1b9e77"]

    bars = ax1.bar(categories, amounts, color=colors, width=0.55, edgecolor="#333333", alpha=0.9)
    ax1.set_ylabel("Capital Amount ($ Billions)", fontsize=11, fontweight="bold")
    ax1.set_title("A. Capital Architecture: Project vs Corporate Debt ($47.85B Total)", fontsize=12, fontweight="bold", pad=12)
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, h + 0.8, f"${h:.2f}B", ha="center", va="bottom", fontsize=10, fontweight="bold")

    # Annotate semantics
    ax1.text(0, amounts[0]/2, "100% Funded\n($6.09B)", ha="center", va="center", color="white", fontweight="bold", fontsize=10)
    ax1.text(1, amounts[1]/2, "Committed Capacity\n($2.40B)", ha="center", va="center", color="white", fontweight="bold", fontsize=10)
    ax1.text(2, amounts[2]/2, "Corporate Balance Sheet\n($39.36B)", ha="center", va="center", color="white", fontweight="bold", fontsize=10)

    # Panel B: APLD Polaris Forge 1 Campus Phasing (400 MW Critical IT)
    bldg_names = ["Building 2\n(100 MW)", "Building 3\n(150 MW)", "Building 4\n(150 MW)"]
    service_ready_mw = [100.0, 0.0, 0.0]
    under_construction_mw = [0.0, 150.0, 150.0]

    b_idx = np.arange(len(bldg_names))
    b_width = 0.5

    ax2.bar(b_idx, service_ready_mw, b_width, label="Service-Ready IT MW (Oct 2025)", color="#2ca02c", alpha=0.9, edgecolor="#333333")
    ax2.bar(b_idx, under_construction_mw, b_width, bottom=service_ready_mw, label="Under Construction / Retrofit (MW)", color="#ff7f0e", alpha=0.85, edgecolor="#333333")

    ax2.set_xticks(b_idx)
    ax2.set_xticklabels(bldg_names, fontsize=10, fontweight="bold")
    ax2.set_ylabel("Critical IT Capacity (MW)", fontsize=11, fontweight="bold")
    ax2.set_title("B. Polaris Forge 1 Phasing: 25% Ready, 75% Uncommissioned", fontsize=12, fontweight="bold", pad=12)
    ax2.legend(frameon=True, facecolor="white", edgecolor="#cccccc", loc="upper left")
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    ax2.text(0, 50, "Service-Ready\n(100 MW)", ha="center", va="center", color="white", fontweight="bold", fontsize=9)
    ax2.text(1, 75, "Partial / Commissioning\n(150 MW)", ha="center", va="center", color="white", fontweight="bold", fontsize=9)
    ax2.text(2, 75, "Under Construction\n(150 MW)", ha="center", va="center", color="white", fontweight="bold", fontsize=9)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "capital_energization_gap.png", dpi=300)
    plt.close()

    # Figure 2: Temporal Carrying Cost vs Delay Slippage & Resilience Mechanisms
    fig, ax = plt.subplots(figsize=(10, 6))

    scenarios = ["6 Months Delay", "12 Months Delay", "18 Months Delay"]
    carrying_costs = [slippage_scenarios["6_month_delay"]["apld_debt_carrying_cost_m"],
                      slippage_scenarios["12_month_delay"]["apld_debt_carrying_cost_m"],
                      slippage_scenarios["18_month_delay"]["apld_debt_carrying_cost_m"]]
    lease_delays = [slippage_scenarios["6_month_delay"]["phased_uncommissioned_lease_delayed_m"],
                    slippage_scenarios["12_month_delay"]["phased_uncommissioned_lease_delayed_m"],
                    slippage_scenarios["18_month_delay"]["phased_uncommissioned_lease_delayed_m"]]
    iren_coupon_eq = [slippage_scenarios["6_month_delay"]["iren_full_capacity_coupon_equivalent_m"],
                      slippage_scenarios["12_month_delay"]["iren_full_capacity_coupon_equivalent_m"],
                      slippage_scenarios["18_month_delay"]["iren_full_capacity_coupon_equivalent_m"]]

    idx = np.arange(len(scenarios))
    w = 0.25

    rects1 = ax.bar(idx - w, carrying_costs, w, label="APLD Project Debt Carrying Cost ($M)", color="#d95f02", alpha=0.9, edgecolor="#333333")
    rects2 = ax.bar(idx, lease_delays, w, label="Delayed APLD Lease Revenue (75% Uncommissioned, $M)", color="#377eb8", alpha=0.9, edgecolor="#333333")
    rects3 = ax.bar(idx + w, iren_coupon_eq, w, label="IREN Mackenzie Full-Capacity Coupon Eq. ($M)", color="#7570b3", alpha=0.7, edgecolor="#333333", linestyle="--")

    for i in range(len(scenarios)):
        ax.text(idx[i] - w, carrying_costs[i] + 12, f"${carrying_costs[i]:,.1f}M", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.text(idx[i], lease_delays[i] + 12, f"${lease_delays[i]:,.1f}M", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.text(idx[i] + w, iren_coupon_eq[i] + 12, f"${iren_coupon_eq[i]:,.1f}M", ha="center", va="bottom", fontsize=8, color="#555555")

    ax.set_xticks(idx)
    ax.set_xticklabels(scenarios, fontsize=11, fontweight="bold")
    ax.set_ylabel("Financial Carrying Stress ($ Millions)", fontsize=11, fontweight="bold")
    ax.set_title("Substation & Equipment Delivery Slippage: Cash Flow Carrying Stress\n(Modeled Hypotheses vs Synchronization Resilience)", fontsize=12, fontweight="bold", pad=14)
    ax.legend(frameon=True, facecolor="white", edgecolor="#cccccc", loc="upper left")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Footnote highlighting synchronization mechanisms
    fig.text(0.5, 0.01, "Resilience Mechanisms: PF2 escrow ($2.15B released Jun 18, 2026), IREN staged drawdowns (cliff Dec 31, 2026), CoreWeave completion indemnities (ELN-02/03).",
             ha="center", fontsize=8.5, style="italic", color="#444444")

    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig(FIGURES_DIR / "temporal_mismatch_timeline.png", dpi=300)
    plt.close()

    print("=== Energization-at-Risk Analysis Completed (ADR-021.1) ===")
    print(f"Total Facility-Attributable Funded Debt: ${total_funded_debt:,.1f}M ($6.090B, APLD only)")
    print(f"Committed Equipment Financing Capacity: ${total_committed_cap:,.1f}M ($2.400B, IREN Mackenzie)")
    print(f"Active Corporate Unallocated Debt: ${total_active_corp_debt:,.2f}M ($39.358B)")
    print(f"APLD Annual Project Interest Carry: ${apld_annual_carrying_cost:,.3f}M/yr")
    print(f"IREN Full-Capacity Coupon Equivalent: ${iren_coupon_equivalent:,.3f}M/yr")
    print(f"Phased Lease Revenue at Risk (75% uncommissioned): ${annual_uncommissioned_lease_delay:,.3f}M/yr")

if __name__ == "__main__":
    run_energization_analysis()
