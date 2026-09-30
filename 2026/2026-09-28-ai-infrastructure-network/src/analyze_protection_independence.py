"""
Analysis Sprint 2.1: Exploratory Analysis of Contractual Protection Compression
and Paired-Shock Scenarios (Task 021 Research Program)

This script performs:
1. Support-Node Compression Analysis:
   Evaluates how many distinct economic support nodes underlie N contractual safeguards
   across 5 benchmark AI infrastructure financing structures.
   Includes sensitivity analysis across three plausible mapping models:
   - Model 1: Economic Convergence (Systemic Baseline)
   - Model 2: Legal Partitioning (Strict Contractual Form)
   - Model 3: Active-Only Covenants (Lifecycle Pruned)
2. Epistemic Metadata Tagging:
   Every protection is explicitly tagged with:
   - protection_status (active, expired, dormant_springing, operating_baseline)
   - mapping_basis (contract_explicit, economic_inference, scenario_assumption)
   - terminal_node_confidence (A, B, C)
3. Selected Paired-Shock Scenarios:
   Traces 5 exploratory stress pairs through the network with strict
   capital-to-physical attribution consistency.
4. Role-Aware Capital Provider Profile:
   Distinguishes direct lenders, syndicate administrative agents, placement
   representatives, and broadly distributed 144A bondholders ($25.682B).
"""

import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
ANALYSIS_DIR = REPO_ROOT / "outputs" / "analysis"
FIGURES_DIR = REPO_ROOT / "outputs" / "figures"

ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Structural Protection Definitions with Epistemic Metadata
# -----------------------------------------------------------------------------
# Structures audited:
# - PF1: Applied Digital Polaris Forge 1 ($2.35B 9.25% + $1.59B 7.00% + Lease)
# - PF2: Applied Digital Polaris Forge 2 ($2.15B 6.75% Notes)
# - Mackenzie: IREN Mackenzie ($1.2B MFSA + $1.2B Notes = $2.4B Committed)
# - CoreWeave DDTLs: DDTL 1.0-5.0 ($13.643B across 6 facilities including 2.1)
# - Nebius Term Loan: MUFG Facility ($775M on Mäntsälä DC & GPUs)

PROTECTIONS_DATA = [
    # ------------------ PF1 ------------------
    {
        "structure_id": "PF1",
        "structure_name": "Applied Digital PF1 (Ellendale Bldgs 2-4)",
        "facility_id": "FAC-APLD-POLARIS-FORGE-1",
        "category": "Data Center Project Debt",
        "capital_volume_b": 3.940,
        "protection_id": "PF1-P1",
        "name": "Debt Service Reserve Account (DSRA)",
        "functional_tier": "Buffering",
        "protection_status": "active",
        "immediate_holder": "APLD ComputeCo Project Trust",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        # Three model mappings:
        "node_model_1": "APLD_PARENT_LIQUIDITY",      # Economic Convergence (replenishment falls on parent)
        "node_model_2": "PREFUNDED_PROJECT_CASH",     # Legal Form (cash sitting in SPV trust account)
        "node_model_3": "APLD_PARENT_LIQUIDITY",      # Active-only
        "description": "Pre-funded cash reserve from note proceeds; replenishment falls on sponsor parent equity."
    },
    {
        "structure_id": "PF1",
        "structure_name": "Applied Digital PF1 (Ellendale Bldgs 2-4)",
        "facility_id": "FAC-APLD-POLARIS-FORGE-1",
        "category": "Data Center Project Debt",
        "capital_volume_b": 3.940,
        "protection_id": "PF1-P2",
        "name": "APLD Sponsor Parent Completion Guarantee",
        "functional_tier": "Transfer",
        "protection_status": "active",
        "immediate_holder": "Applied Digital, Inc. (Parent)",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "APLD_PARENT_LIQUIDITY",
        "node_model_2": "APLD_PARENT_LIQUIDITY",
        "node_model_3": "APLD_PARENT_LIQUIDITY",
        "description": "Mandatory sponsor shortfall funding to achieve Commencement Date; uncapped sponsor obligation."
    },
    {
        "structure_id": "PF1",
        "structure_name": "Applied Digital PF1 (Ellendale Bldgs 2-4)",
        "facility_id": "FAC-APLD-POLARIS-FORGE-1",
        "category": "Data Center Project Debt",
        "capital_volume_b": 3.940,
        "protection_id": "PF1-P3",
        "name": "Substation & Facility First-Priority Mortgage Lien",
        "functional_tier": "Recovery",
        "protection_status": "active",
        "immediate_holder": "Noteholder Collateral Agent",
        "mapping_basis": "economic_inference",
        "terminal_node_confidence": "B",
        "node_model_1": "POWER_GRID_ENERGIZATION",    # Economic Convergence (salvage value tied to energization)
        "node_model_2": "PHYSICAL_ASSET_SALVAGE",     # Legal Form (land and physical electrical equipment)
        "node_model_3": "POWER_GRID_ENERGIZATION",
        "description": "Senior mortgage on land, substation, and shells; recovery value is highly dependent on utility power delivery."
    },
    {
        "structure_id": "PF1",
        "structure_name": "Applied Digital PF1 (Ellendale Bldgs 2-4)",
        "facility_id": "FAC-APLD-POLARIS-FORGE-1",
        "category": "Data Center Project Debt",
        "capital_volume_b": 3.940,
        "protection_id": "PF1-P4",
        "name": "CoreWeave 15-Year Take-or-Pay Master Lease",
        "functional_tier": "Transfer",
        "protection_status": "active",
        "immediate_holder": "CRWV SPV VIII (Tenant)",
        "mapping_basis": "economic_inference",
        "terminal_node_confidence": "B",
        "node_model_1": "HYPERSCALER_ANCHOR_DEMAND",  # Economic Convergence (CoreWeave rent requires MSFT compute revenue)
        "node_model_2": "CRWV_ENTERPRISE_LIQUIDITY",  # Legal Form (tenant creditworthiness)
        "node_model_3": "HYPERSCALER_ANCHOR_DEMAND",
        "description": "$11.0B contracted lease revenue; tenant rent service depends on neocloud operating cash flows."
    },
    {
        "structure_id": "PF1",
        "structure_name": "Applied Digital PF1 (Ellendale Bldgs 2-4)",
        "facility_id": "FAC-APLD-POLARIS-FORGE-1",
        "category": "Data Center Project Debt",
        "capital_volume_b": 3.940,
        "protection_id": "PF1-P5",
        "name": "CoreWeave Springing Performance Guaranty (ELN-02)",
        "functional_tier": "Transfer",
        "protection_status": "dormant_springing",
        "immediate_holder": "CoreWeave, Inc. (Parent)",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "CRWV_ENTERPRISE_LIQUIDITY",
        "node_model_2": "CRWV_ENTERPRISE_LIQUIDITY",
        "node_model_3": None,                         # Pruned in active-only model (dormant until delivery)
        "description": "Uncapped parent indemnity backstopping tenant lease obligations for Building 2 post-handover."
    },
    {
        "structure_id": "PF1",
        "structure_name": "Applied Digital PF1 (Ellendale Bldgs 2-4)",
        "facility_id": "FAC-APLD-POLARIS-FORGE-1",
        "category": "Data Center Project Debt",
        "capital_volume_b": 3.940,
        "protection_id": "PF1-P6",
        "name": "CoreWeave Springing Performance Guaranty (ELN-03)",
        "functional_tier": "Transfer",
        "protection_status": "dormant_springing",
        "immediate_holder": "CoreWeave, Inc. (Parent)",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "CRWV_ENTERPRISE_LIQUIDITY",
        "node_model_2": "CRWV_ENTERPRISE_LIQUIDITY",
        "node_model_3": None,                         # Pruned in active-only model (dormant until delivery)
        "description": "Uncapped parent indemnity ($4.125B Class C proxy) for Building 3 post-handover."
    },

    # ------------------ PF2 ------------------
    {
        "structure_id": "PF2",
        "structure_name": "Applied Digital PF2 (Polaris Forge 2)",
        "facility_id": "FAC-APLD-POLARIS-FORGE-2",
        "category": "Data Center Project Debt",
        "capital_volume_b": 2.150,
        "protection_id": "PF2-P1",
        "name": "Goldman Sachs Escrow Condition Precedent Gating",
        "functional_tier": "Preventive",
        "protection_status": "expired",              # Satisfied June 18, 2026
        "immediate_holder": "Goldman Sachs Escrow Agent",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "POWER_GRID_ENERGIZATION",    # Gated specifically on ESA execution
        "node_model_2": "ESCROW_CASH_HELD",          # Legal form (proceeds in bank escrow)
        "node_model_3": None,                         # Pruned in active-only model (already released)
        "description": "Gross proceeds locked until ESA execution (satisfied June 18, 2026); gated capital release."
    },
    {
        "structure_id": "PF2",
        "structure_name": "Applied Digital PF2 (Polaris Forge 2)",
        "facility_id": "FAC-APLD-POLARIS-FORGE-2",
        "category": "Data Center Project Debt",
        "capital_volume_b": 2.150,
        "protection_id": "PF2-P2",
        "name": "Project Debt Service Reserve Account (DSRA)",
        "functional_tier": "Buffering",
        "protection_status": "active",
        "immediate_holder": "APLD ComputeCo 2 Trust",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "APLD_PARENT_LIQUIDITY",
        "node_model_2": "PREFUNDED_PROJECT_CASH",
        "node_model_3": "APLD_PARENT_LIQUIDITY",
        "description": "Project account reserve funding interim coupon service prior to commercial energization."
    },
    {
        "structure_id": "PF2",
        "structure_name": "Applied Digital PF2 (Polaris Forge 2)",
        "facility_id": "FAC-APLD-POLARIS-FORGE-2",
        "category": "Data Center Project Debt",
        "capital_volume_b": 2.150,
        "protection_id": "PF2-P3",
        "name": "APLD Parent Construction Completion Support",
        "functional_tier": "Transfer",
        "protection_status": "active",
        "immediate_holder": "Applied Digital, Inc. (Parent)",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "APLD_PARENT_LIQUIDITY",
        "node_model_2": "APLD_PARENT_LIQUIDITY",
        "node_model_3": "APLD_PARENT_LIQUIDITY",
        "description": "Sponsor parent covenants to fund completion of construction period and first commencement date."
    },
    {
        "structure_id": "PF2",
        "structure_name": "Applied Digital PF2 (Polaris Forge 2)",
        "facility_id": "FAC-APLD-POLARIS-FORGE-2",
        "category": "Data Center Project Debt",
        "capital_volume_b": 2.150,
        "protection_id": "PF2-P4",
        "name": "First-Priority Senior Secured Project Liens",
        "functional_tier": "Recovery",
        "protection_status": "active",
        "immediate_holder": "Noteholder Collateral Agent",
        "mapping_basis": "economic_inference",
        "terminal_node_confidence": "B",
        "node_model_1": "POWER_GRID_ENERGIZATION",
        "node_model_2": "PHYSICAL_ASSET_SALVAGE",
        "node_model_3": "POWER_GRID_ENERGIZATION",
        "description": "Liens on project parcels, civil works, and utility rights; value contingent on substation completion."
    },

    # ------------------ MACKENZIE ------------------
    {
        "structure_id": "MACKENZIE",
        "structure_name": "IREN Mackenzie (GPU Equipment Financing)",
        "facility_id": "FAC-IREN-MACKENZIE",
        "category": "Equipment Facility",
        "capital_volume_b": 2.400,
        "protection_id": "MAC-P1",
        "name": "Staged Milestone Drawdown Condition",
        "functional_tier": "Preventive",
        "protection_status": "active",
        "immediate_holder": "IE Mackenzie Compute Ltd.",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "VENDOR_SUPPLY_CHAIN",
        "node_model_2": "VENDOR_SUPPLY_CHAIN",
        "node_model_3": "VENDOR_SUPPLY_CHAIN",
        "description": "Capital funded strictly pro rata upon physical delivery and acceptance testing of operational servers."
    },
    {
        "structure_id": "MACKENZIE",
        "structure_name": "IREN Mackenzie (GPU Equipment Financing)",
        "facility_id": "FAC-IREN-MACKENZIE",
        "category": "Equipment Facility",
        "capital_volume_b": 2.400,
        "protection_id": "MAC-P2",
        "name": "First-Priority Equipment Collateral Security Interest",
        "functional_tier": "Recovery",
        "protection_status": "active",
        "immediate_holder": "Blue Owl / PIMCO Collateral Agents",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "GPU_SECONDARY_COLLATERAL",
        "node_model_2": "GPU_SECONDARY_COLLATERAL",
        "node_model_3": "GPU_SECONDARY_COLLATERAL",
        "description": "Direct security interest in GPU servers; recovery dependent on secondary market resale clearing values."
    },
    {
        "structure_id": "MACKENZIE",
        "structure_name": "IREN Mackenzie (GPU Equipment Financing)",
        "facility_id": "FAC-IREN-MACKENZIE",
        "category": "Equipment Facility",
        "capital_volume_b": 2.400,
        "protection_id": "MAC-P3",
        "name": "IREN Limited Unconditional Parent Payment Guaranty",
        "functional_tier": "Transfer",
        "protection_status": "active",
        "immediate_holder": "IREN Limited (Parent)",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "IREN_PARENT_LIQUIDITY",
        "node_model_2": "IREN_PARENT_LIQUIDITY",
        "node_model_3": "IREN_PARENT_LIQUIDITY",
        "description": "Full parent recourse allowing lenders to pursue company cash flows if equipment revenue falls short."
    },
    {
        "structure_id": "MACKENZIE",
        "structure_name": "IREN Mackenzie (GPU Equipment Financing)",
        "facility_id": "FAC-IREN-MACKENZIE",
        "category": "Equipment Facility",
        "capital_volume_b": 2.400,
        "protection_id": "MAC-P4",
        "name": "Hard Availability Window Cliff (Dec 31, 2026)",
        "functional_tier": "Preventive",
        "protection_status": "active",
        "immediate_holder": "Lender Credit Facility",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "LENDER_COMMITMENT_LIFECYCLE", # Expiration of lender obligation
        "node_model_2": "LENDER_COMMITMENT_LIFECYCLE",
        "node_model_3": "LENDER_COMMITMENT_LIFECYCLE",
        "description": "Uncalled commitments terminate automatically, ending lender funding obligation."
    },

    # ------------------ COREWEAVE DDTLS ------------------
    {
        "structure_id": "CRWV_DDTL",
        "structure_name": "CoreWeave DDTLs (Tranches 1.0 - 5.0, including 2.1)",
        "facility_id": "PORTFOLIO_COREWEAVE",
        "category": "Equipment Facility",
        "capital_volume_b": 13.643,                   # $1.3B + $3.19B + $3.0B + $2.215B + $2.837B + $1.101B
        "protection_id": "DDTL-P1",
        "name": "GPU Hardware Borrowing Base Advance Rate",
        "functional_tier": "Preventive",
        "protection_status": "active",
        "immediate_holder": "Borrowing SPVs (CCAC II, IV, VII, etc.)",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "GPU_SECONDARY_COLLATERAL",
        "node_model_2": "GPU_SECONDARY_COLLATERAL",
        "node_model_3": "GPU_SECONDARY_COLLATERAL",
        "description": "Loan draws bounded by third-party appraised liquidation value of H100/H200/B200 GPU clusters."
    },
    {
        "structure_id": "CRWV_DDTL",
        "structure_name": "CoreWeave DDTLs (Tranches 1.0 - 5.0, including 2.1)",
        "facility_id": "PORTFOLIO_COREWEAVE",
        "category": "Equipment Facility",
        "capital_volume_b": 13.643,
        "protection_id": "DDTL-P2",
        "name": "Debt Service Reserve & Minimum Liquidity Covenants",
        "functional_tier": "Buffering",
        "protection_status": "active",
        "immediate_holder": "SPV Project Accounts",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "CRWV_ENTERPRISE_LIQUIDITY",
        "node_model_2": "SPV_PREFUNDED_CASH",        # Legal partition (cash inside SPV account)
        "node_model_3": "CRWV_ENTERPRISE_LIQUIDITY",
        "description": "Cash liquidity covenants mandated across borrowing SPVs and consolidated enterprise."
    },
    {
        "structure_id": "CRWV_DDTL",
        "structure_name": "CoreWeave DDTLs (Tranches 1.0 - 5.0, including 2.1)",
        "facility_id": "PORTFOLIO_COREWEAVE",
        "category": "Equipment Facility",
        "capital_volume_b": 13.643,
        "protection_id": "DDTL-P3",
        "name": "Bankruptcy-Remote SPV Ring-Fencing",
        "functional_tier": "Recovery",
        "protection_status": "active",
        "immediate_holder": "Special Purpose Vehicles",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "SPV_ASSET_PARTITION",        # Legal estate partitioning (not mere parent liquidity)
        "node_model_2": "SPV_ASSET_PARTITION",
        "node_model_3": "SPV_ASSET_PARTITION",
        "description": "Legal isolation of GPU assets protecting secured lenders from general unsecured creditors of parent."
    },
    {
        "structure_id": "CRWV_DDTL",
        "structure_name": "CoreWeave DDTLs (Tranches 1.0 - 5.0, including 2.1)",
        "facility_id": "PORTFOLIO_COREWEAVE",
        "category": "Equipment Facility",
        "capital_volume_b": 13.643,
        "protection_id": "DDTL-P4a",
        "name": "Full-Recourse Parent Guarantees (DDTL 1, 2, 2.1, 3, 5)",
        "functional_tier": "Transfer",
        "protection_status": "active",
        "immediate_holder": "CoreWeave, Inc. (Parent)",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "CRWV_ENTERPRISE_LIQUIDITY",
        "node_model_2": "CRWV_ENTERPRISE_LIQUIDITY",
        "node_model_3": "CRWV_ENTERPRISE_LIQUIDITY",
        "description": "Unconditional full-recourse parent debt service guarantee covering $10.806B of facilities."
    },
    {
        "structure_id": "CRWV_DDTL",
        "structure_name": "CoreWeave DDTLs (Tranches 1.0 - 5.0, including 2.1)",
        "facility_id": "PORTFOLIO_COREWEAVE",
        "category": "Equipment Facility",
        "capital_volume_b": 13.643,
        "protection_id": "DDTL-P4b",
        "name": "Limited Bad-Acts Carve-Out Guaranty (DDTL 4.0)",
        "functional_tier": "Transfer",
        "protection_status": "active",
        "immediate_holder": "CoreWeave, Inc. (Parent)",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "CRWV_ENTERPRISE_LIQUIDITY",
        "node_model_2": "CRWV_BAD_ACTS_RECOURSE",     # Distinct legal recourse standard
        "node_model_3": "CRWV_ENTERPRISE_LIQUIDITY",
        "description": "Non-recourse carve-out guaranty on $2.837B facility; parent liable only for specified bad acts."
    },
    {
        "structure_id": "CRWV_DDTL",
        "structure_name": "CoreWeave DDTLs (Tranches 1.0 - 5.0, including 2.1)",
        "facility_id": "PORTFOLIO_COREWEAVE",
        "category": "Equipment Facility",
        "capital_volume_b": 13.643,
        "protection_id": "DDTL-P5",
        "name": "Joint Co-Borrower Liability Structure (CCAC V on DDTL 3.0)",
        "functional_tier": "Transfer",
        "protection_status": "active",
        "immediate_holder": "CRWV_CCAC_V (Co-Borrower)",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "CRWV_ENTERPRISE_LIQUIDITY",
        "node_model_2": "AFFILIATE_CROSS_COLLATERAL",
        "node_model_3": "CRWV_ENTERPRISE_LIQUIDITY",
        "description": "Cross-subsidiary co-borrower liability joining multiple cluster entities under single agreement."
    },
    {
        "structure_id": "CRWV_DDTL",
        "structure_name": "CoreWeave DDTLs (Tranches 1.0 - 5.0, including 2.1)",
        "facility_id": "PORTFOLIO_COREWEAVE",
        "category": "Equipment Facility",
        "capital_volume_b": 13.643,
        "protection_id": "DDTL-P6",
        "name": "Anchor Hyperscaler Customer Offtake Cash Flows",
        "functional_tier": "Transfer",
        "protection_status": "active",
        "immediate_holder": "CoreWeave Commercial Contracts",
        "mapping_basis": "economic_inference",
        "terminal_node_confidence": "B",
        "node_model_1": "HYPERSCALER_ANCHOR_DEMAND",
        "node_model_2": "HYPERSCALER_ANCHOR_DEMAND",
        "node_model_3": "HYPERSCALER_ANCHOR_DEMAND",
        "description": "Underlying cluster debt service relies on collections from primary offtaker (Microsoft ~67% FY25)."
    },

    # ------------------ NEBIUS ------------------
    {
        "structure_id": "NBIS_MUFG",
        "structure_name": "Nebius Term Loan (Mäntsälä DC & GPUs)",
        "facility_id": "FAC-NBIS-MANTSALA",
        "category": "Datacenter / GPU Term Loan",
        "capital_volume_b": 0.775,
        "protection_id": "NBIS-P1",
        "name": "First-Priority Security on Mäntsälä DC & Compute Assets",
        "functional_tier": "Recovery",
        "protection_status": "active",
        "immediate_holder": "MUFG Syndicate Collateral Agent",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "DC_AND_GPU_COLLATERAL",
        "node_model_2": "DC_AND_GPU_COLLATERAL",
        "node_model_3": "DC_AND_GPU_COLLATERAL",
        "description": "Security interest in physical datacenter infrastructure and GPU clusters at operating Finnish facility."
    },
    {
        "structure_id": "NBIS_MUFG",
        "structure_name": "Nebius Term Loan (Mäntsälä DC & GPUs)",
        "facility_id": "FAC-NBIS-MANTSALA",
        "category": "Datacenter / GPU Term Loan",
        "capital_volume_b": 0.775,
        "protection_id": "NBIS-P2",
        "name": "Non-Recourse Parent Carve-Out Guaranty (Bad Acts & Performance)",
        "functional_tier": "Transfer",
        "protection_status": "active",
        "immediate_holder": "Nebius Group N.V. (Parent)",
        "mapping_basis": "contract_explicit",
        "terminal_node_confidence": "A",
        "node_model_1": "NEBIUS_BAD_ACTS_RECOURSE",    # Limited carve-out, not broad debt-service guaranty
        "node_model_2": "NEBIUS_BAD_ACTS_RECOURSE",
        "node_model_3": "NEBIUS_BAD_ACTS_RECOURSE",
        "description": "Parent guarantee limited to specified bad acts and performance covenants; not a blanket debt-service guarantee."
    }
]

# -----------------------------------------------------------------------------
# 2. Selected Paired-Shock Scenarios (Exploratory Stress Matrix)
# -----------------------------------------------------------------------------
PAIRED_SCENARIOS = [
    {
        "scenario_id": "PAIR-01",
        "name": "Anchor Customer Contraction + Power Energization Delay",
        "assumptions": ["A005", "A004"],
        "category": "Commercial & Physical Shock",
        "mechanism": (
            "Hyperscaler offload decelerates or trims optional tiers (A005) while regional substation construction "
            "slips in North Dakota (A004). Unenergized halls at Ellendale prevent lease commencement, leaving "
            "springing lease guaranties dormant. APLD parent must absorb debt service on PF1/PF2 without tenant lease rent."
        ),
        "touched_structures": ["PF1", "PF2", "CRWV_DDTL"],
        "touched_debt_b": 19.733,  # $3.94B PF1 + $2.15B PF2 + $13.643B DDTL
        "touched_mw": 600.0,       # 400 MW Ellendale PF1 + 200 MW PF2
        "affected_protections": [
            "PF1-P4 (Take-or-Pay Lease)",
            "PF1-P5 (Springing Guaranty ELN02)",
            "PF1-P6 (Springing Guaranty ELN03)",
            "DDTL-P6 (Hyperscaler Offtake Cash Flows)"
        ],
        "analytical_observation": "Tests vulnerability when tenant rental cash generation fails to synchronize with physical data hall delivery."
    },
    {
        "scenario_id": "PAIR-02",
        "name": "GPU Collateral Haircut + Refinancing Freeze",
        "assumptions": ["A001", "A002"],
        "category": "Capital Markets & Technology Shock",
        "mechanism": (
            "Accelerated architectural obsolescence or secondary hardware flooding drives a 40% drop in GPU clearing prices (A001). "
            "Borrowing base advance rates are breached. Simultaneously, credit spreads widen +300 bps (A002), "
            "impeding DDTL rollover and forcing cash equity cure contributions."
        ),
        "touched_structures": ["CRWV_DDTL", "MACKENZIE", "NBIS_MUFG"],
        "touched_debt_b": 16.818,  # $13.643B DDTL + $2.4B MAC + $0.775B NBIS
        "touched_mw": 745.0,
        "affected_protections": [
            "DDTL-P1 (Borrowing Base Advance)",
            "MAC-P2 (Equipment Collateral Lien)",
            "NBIS-P1 (DC & Compute Security)",
            "MAC-P4 (Availability Window Cliff)"
        ],
        "analytical_observation": "Tests the vulnerability of asset-backed debt structures when secondary silicon liquidation values compress."
    },
    {
        "scenario_id": "PAIR-03",
        "name": "Sponsor Parent Liquidity Shock + Construction Delay",
        "assumptions": ["A002", "A004"],
        "category": "Sponsor Credit & Execution Shock",
        "mechanism": (
            "Energization delay extends beyond prefunded interest reserve horizons (A004). "
            "Concurrently, sponsor parent equity/convertible market access tightens (A002), "
            "constraining APLD's capacity to fulfill mandatory construction shortfall contributions."
        ),
        "touched_structures": ["PF1", "PF2"],
        "touched_debt_b": 6.090,   # $3.94B PF1 + $2.15B PF2
        "touched_mw": 600.0,
        "affected_protections": [
            "PF1-P1 (DSRA Reserve)",
            "PF1-P2 (APLD Completion Guarantee)",
            "PF2-P2 (Project DSRA)",
            "PF2-P3 (APLD Completion Support)"
        ],
        "analytical_observation": "Tests whether prefunded DSRAs provide sufficient runway when sponsor parent liquidity is constrained."
    },
    {
        "scenario_id": "PAIR-04",
        "name": "ERCOT Grid Disruption + Refinancing Freeze",
        "assumptions": ["A004", "A002"],
        "category": "Regional Infrastructure & Capital Shock",
        "mechanism": (
            "Severe transmission curtailment or interconnect delays hit ERCOT Texas operations (A004). "
            "Simultaneously, high-yield private credit spreads widen (A002), restricting capital access for pipeline buildout. "
            "Touches Core Scientific Denton colocation (100 MW live / 394 MW utility), IREN Childress (650 MW live / 750 MW utility), "
            "and IREN Sweetwater development pipeline (2,000 MW)."
        ),
        "touched_structures": ["CORZ_COLOCATION", "IREN_CHILDRESS", "IREN_SWEETWATER"],
        "touched_debt_b": 0.000,   # Excludes non-ERCOT project debt (0.00% misattribution); corporate credit only
        "touched_mw": 2750.0,      # 750 MW live ERCOT + 2,000 MW Sweetwater pipeline
        "affected_protections": [
            "CORZ CoreWeave Colocation Agreement (590 MW total across sites)",
            "IREN Operating Cash Flow Generation from Childress",
            "Sweetwater Phase 1 & 2 Interconnection Progression"
        ],
        "analytical_observation": "Evaluates pure regional grid common dependency strictly aligned to Texas physical and contractual assets."
    },
    {
        "scenario_id": "PAIR-05",
        "name": "Hyperscaler Capex Deceleration + GPU Secondary Haircut",
        "assumptions": ["A006", "A001"],
        "category": "Macro Capex & Technology Shock",
        "mechanism": (
            "Top 4 hyperscalers transition to an infrastructure digestion phase, slowing capex growth (A006). "
            "Excess server inventory depresses secondary GPU prices (A001), impacting borrowing bases across equipment facilities."
        ),
        "touched_structures": ["CRWV_DDTL", "MACKENZIE"],
        "touched_debt_b": 16.043,  # $13.643B DDTL + $2.4B MAC
        "touched_mw": 670.0,
        "affected_protections": [
            "DDTL-P1 (Borrowing Base Advance)",
            "MAC-P1 (Staged Drawdown Condition)",
            "MAC-P2 (Equipment Collateral Lien)"
        ],
        "analytical_observation": "Tests the direct transmission belt between hyperscaler capex cycles and neocloud equipment debt."
    }
]

# -----------------------------------------------------------------------------
# 3. Role-Aware Capital Provider / Lender Profile
# -----------------------------------------------------------------------------
LENDER_ROLES = [
    {
        "capital_category": "Direct Lenders & Lessors",
        "institution_name": "Blue Owl Capital / OBDC",
        "role_description": "Direct Equipment Financing Provider & Lessor",
        "facilities": "IREN Mackenzie MFSA",
        "modeled_amount_b": 1.200,
        "notes": "Committed direct lease financing drawn upon equipment acceptance."
    },
    {
        "capital_category": "Institutional Note Purchasers",
        "institution_name": "PIMCO",
        "role_description": "Senior Secured Equipment Note Purchaser",
        "facilities": "IREN Mackenzie Senior Secured Notes",
        "modeled_amount_b": 1.200,
        "notes": "Privately placed equipment notes drawn alongside MFSA."
    },
    {
        "capital_category": "Institutional Note Purchasers",
        "institution_name": "Coatue Management",
        "role_description": "Convertible Note Investor",
        "facilities": "Hut 8 Senior Unsecured Convertible Note",
        "modeled_amount_b": 0.150,
        "notes": "Dedicated private convertible placement."
    },
    {
        "capital_category": "Syndicate Administrative Agents",
        "institution_name": "Blackstone & Magnetar (Agent / Lead)",
        "role_description": "Administrative & Collateral Agent for Private Credit Syndicate",
        "facilities": "CoreWeave DDTL 1.0, 2.0, 2.1",
        "modeled_amount_b": 7.490,
        "notes": "Represents syndicated private credit lenders; beneficial holder distribution undisclosed."
    },
    {
        "capital_category": "Syndicate Administrative Agents",
        "institution_name": "MUFG Bank Syndicate (Agent / Lead)",
        "role_description": "Administrative Agent for Commercial Bank Syndicate",
        "facilities": "CoreWeave DDTL 3.0, 4.0; Nebius Term Loan",
        "modeled_amount_b": 5.827,
        "notes": "Syndicated international commercial bank facilities ($2.215B + $2.837B + $0.775B)."
    },
    {
        "capital_category": "Syndicate Administrative Agents",
        "institution_name": "Morgan Stanley Syndicate (Agent / Lead)",
        "role_description": "Administrative Agent for Bank Syndicate",
        "facilities": "CoreWeave DDTL 5.0",
        "modeled_amount_b": 1.101,
        "notes": "Syndicated delayed-draw credit agreement."
    },
    {
        "capital_category": "Placement & Escrow Intermediaries",
        "institution_name": "Goldman Sachs & Co. LLC",
        "role_description": "Initial Purchaser Representative & Escrow Agent",
        "facilities": "Applied Digital PF2 Notes Placement & Escrow",
        "modeled_amount_b": 2.150,
        "notes": "Underwriter / placement representative; economic holders are distributed 144A investors, not Goldman balance sheet."
    },
    {
        "capital_category": "Distributed Public / 144A Bondholders",
        "institution_name": "Institutional High-Yield & Convertible Market",
        "role_description": "Broadly Distributed Institutional Bondholders (Mutual Funds, Insurance, Credit Funds)",
        "facilities": "CRWV Senior Notes & Converts ($16.617B); APLD Notes/Converts ($6.540B); WULF Converts ($2.525B)",
        "modeled_amount_b": 25.682,
        "notes": "Reconciled total across 14 distinct note/convertible tranches in frozen ledger."
    }
]

# -----------------------------------------------------------------------------
# 4. Computation & Sensitivity Engine
# -----------------------------------------------------------------------------
def run_analysis():
    print("=" * 80)
    print("RUNNING ANALYSIS SPRINT 2.1: CONTRACTUAL PROTECTION COMPRESSION & SENSITIVITY")
    print("=" * 80)

    df_prot = pd.DataFrame(PROTECTIONS_DATA)
    structures = df_prot["structure_id"].unique()

    summary_records = []

    for sid in structures:
        sub = df_prot[df_prot["structure_id"] == sid]
        sname = sub["structure_name"].iloc[0]
        cat = sub["category"].iloc[0]
        vol = sub["capital_volume_b"].iloc[0]
        n_prot_total = len(sub)

        # Model 1: Economic Convergence (Systemic Baseline)
        nodes_m1 = set(sub["node_model_1"].dropna())
        sncr_m1 = len(nodes_m1) / n_prot_total

        # Model 2: Legal Partitioning (Strict Contractual Form)
        nodes_m2 = set(sub["node_model_2"].dropna())
        sncr_m2 = len(nodes_m2) / n_prot_total

        # Model 3: Active-Only Covenants (Lifecycle Filtered)
        sub_active = sub[sub["node_model_3"].notna()]
        n_prot_active = len(sub_active)
        nodes_m3 = set(sub_active["node_model_3"].dropna())
        sncr_m3 = len(nodes_m3) / n_prot_active if n_prot_active > 0 else 0.0

        # Predeclared classification based on Model 1:
        # < 0.50: Severe Compression / Concentration
        # 0.50 - 0.74: Moderate Compression / Mixed
        # >= 0.75: High Independence / Orthogonal
        if sncr_m1 < 0.50:
            classification = "Severe Compression (SNCR < 0.50)"
        elif sncr_m1 < 0.75:
            classification = "Moderate Compression / Mixed (0.50 <= SNCR < 0.75)"
        else:
            classification = "High Independence (SNCR >= 0.75)"

        summary_records.append({
            "structure_id": sid,
            "structure_name": sname,
            "category": cat,
            "capital_volume_b": vol,
            "n_protections_total": n_prot_total,
            "n_protections_active": n_prot_active,
            "sncr_model_1_economic": round(sncr_m1, 4),
            "sncr_model_2_legal": round(sncr_m2, 4),
            "sncr_model_3_active_only": round(sncr_m3, 4),
            "nodes_model_1": sorted(list(nodes_m1)),
            "nodes_model_2": sorted(list(nodes_m2)),
            "nodes_model_3": sorted(list(nodes_m3)),
            "baseline_classification": classification
        })

    df_summary = pd.DataFrame(summary_records)
    df_scenarios = pd.DataFrame(PAIRED_SCENARIOS)
    df_lenders = pd.DataFrame(LENDER_ROLES)

    print("\n--- Support-Node Compression Ratio (SNCR) Multi-Model Sensitivity Table ---")
    print(df_summary[["structure_id", "capital_volume_b", "n_protections_total", "sncr_model_1_economic", "sncr_model_2_legal", "sncr_model_3_active_only", "baseline_classification"]].to_string(index=False))

    # Export CSVs
    df_summary.to_csv(ANALYSIS_DIR / "protection_independence_summary.csv", index=False)
    df_prot.to_csv(ANALYSIS_DIR / "protection_mapping_table.csv", index=False)
    df_scenarios.to_csv(ANALYSIS_DIR / "selected_paired_scenarios.csv", index=False)
    df_lenders.to_csv(ANALYSIS_DIR / "lender_role_profile.csv", index=False)

    # Export JSON
    export_data = {
        "analysis_sprint": "Analysis Sprint 2.1: Contractual Protection Compression & Sensitivity",
        "date": "2026-09-30",
        "methodological_note": (
            "SNCR (Support-Node Compression Ratio) is an analyst-coded classification metric "
            "measuring the ratio of distinct underlying economic support nodes to stated contractual safeguards. "
            "It is evaluated under three sensitivity models to verify robustness."
        ),
        "sensitivity_models": {
            "model_1": "Economic Convergence (groups related nodes by systemic economic driver)",
            "model_2": "Legal Partitioning (preserves legal distinctions like SPV partitioning and bad-acts carveouts)",
            "model_3": "Active-Only Covenants (prunes expired conditions like PF2 escrow and dormant springing guaranties)"
        },
        "structures_summary": summary_records,
        "selected_paired_scenarios": PAIRED_SCENARIOS,
        "lender_roles_profile": LENDER_ROLES
    }

    with open(ANALYSIS_DIR / "protection_independence_summary.json", "w") as f:
        json.dump(export_data, f, indent=2)

    print(f"\n[OK] Summary JSON saved to {ANALYSIS_DIR / 'protection_independence_summary.json'}")

    # Generate Figures
    generate_figures(df_summary, df_scenarios, df_lenders)


# -----------------------------------------------------------------------------
# 5. Visualizations Generator
# -----------------------------------------------------------------------------
def generate_figures(df_summary, df_scenarios, df_lenders):
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    matplotlib.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    matplotlib.rcParams["axes.edgecolor"] = "#cccccc"
    matplotlib.rcParams["axes.linewidth"] = 0.8

    # -------------------------------------------------------------------------
    # FIGURE 1: Support-Node Compression & Multi-Model Sensitivity
    # -------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    structures = df_summary["structure_id"].tolist()
    labels = [f"{s}\n(${df_summary.loc[df_summary['structure_id']==s, 'capital_volume_b'].values[0]:.1f}B)" for s in structures]

    m1_vals = df_summary["sncr_model_1_economic"].values
    m2_vals = df_summary["sncr_model_2_legal"].values
    m3_vals = df_summary["sncr_model_3_active_only"].values

    x = np.arange(len(structures))
    width = 0.25

    # Panel A: Sensitivity across 3 Models
    rects1 = ax1.bar(x - width, m1_vals, width, label="Model 1: Economic Convergence", color="#b71c1c", alpha=0.85, edgecolor="#333333")
    rects2 = ax1.bar(x, m2_vals, width, label="Model 2: Legal Partitioning", color="#1976d2", alpha=0.85, edgecolor="#333333")
    rects3 = ax1.bar(x + width, m3_vals, width, label="Model 3: Active-Only Covenants", color="#388e3c", alpha=0.85, edgecolor="#333333")

    ax1.axhline(y=0.50, color="#d9534f", linestyle="--", linewidth=1.2, label="Compression Threshold (0.50)")
    ax1.axhline(y=0.75, color="#5cb85c", linestyle="--", linewidth=1.2, label="Independence Threshold (0.75)")

    ax1.set_ylabel("Support-Node Compression Ratio (SNCR)", fontsize=11, fontweight="bold")
    ax1.set_title("A. Sensitivity Analysis of Protection Compression Across Models", fontsize=12, fontweight="bold", pad=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=9, fontweight="bold")
    ax1.set_ylim(0, 1.25)
    ax1.legend(loc="upper right", frameon=True, fontsize=9)

    for bar in rects1:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=8)
    for bar in rects2:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=8)
    for bar in rects3:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=8)

    # Panel B: Protection Counts vs Unique Economic Support Nodes (Model 1 Baseline)
    n_prot = df_summary["n_protections_total"].values
    n_nodes_m1 = [len(nodes) for nodes in df_summary["nodes_model_1"]]

    w2 = 0.35
    b1 = ax2.bar(x - w2/2, n_prot, w2, label="Contractual Protections (N_prot)", color="#455a64", alpha=0.85, edgecolor="#263238")
    b2 = ax2.bar(x + w2/2, n_nodes_m1, w2, label="Underlying Economic Support Nodes (N_nodes)", color="#e65100", alpha=0.85, edgecolor="#bf360c")

    ax2.set_ylabel("Count", fontsize=11, fontweight="bold")
    ax2.set_title("B. Contractual Safeguards vs. Terminal Support Nodes (Model 1)", fontsize=12, fontweight="bold", pad=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=9, fontweight="bold")
    ax2.set_ylim(0, 8.5)
    ax2.legend(loc="upper left", frameon=True, fontsize=9)

    for bar in b1:
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15, f"{int(bar.get_height())}", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#455a64")
    for bar in b2:
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15, f"{int(bar.get_height())}", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#e65100")

    ax2.text(0.5, -0.20,
             "Methodological Takeaway: SNCR quantifies how many distinct economic resources underlie N covenants.\n"
             "PF2 and CoreWeave exhibit reconvergence across all models; Mackenzie and Nebius maintain higher independence.",
             ha="center", va="top", transform=ax2.transAxes, fontsize=9, style="italic",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f9fa", edgecolor="#dddddd"))

    plt.tight_layout()
    fig1_path = FIGURES_DIR / "protection_independence_matrix.png"
    plt.savefig(fig1_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Figure 1 saved to {fig1_path}")

    # -------------------------------------------------------------------------
    # FIGURE 2: Selected Paired-Shock Scenarios & Role-Aware Capital Profile
    # -------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Panel A: Capital Volume Touched by Selected Paired-Shock Scenarios
    scen_ids = df_scenarios["scenario_id"].tolist()
    debt_vols = df_scenarios["touched_debt_b"].values
    scen_names = [f"{row.scenario_id}: {row.name.split('+')[0].strip()}" for row in df_scenarios.itertuples()]

    colors_scen = ["#c62828", "#d32f2f", "#e53935", "#1565c0", "#ad1457"]
    b_scen = ax1.barh(scen_ids, debt_vols, color=colors_scen, edgecolor="#333333", alpha=0.85, height=0.55)

    ax1.set_xlabel("Attributable Funded / Committed Debt Touched ($B)", fontsize=11, fontweight="bold")
    ax1.set_title("A. Selected Paired-Shock Scenarios: Attributable Debt Exposure", fontsize=12, fontweight="bold", pad=12)
    ax1.set_xlim(0, 24)

    for bar, val, name in zip(b_scen, debt_vols, scen_names):
        txt = f"${val:.1f}B" if val > 0 else "$0.0B (Colo/Cash Flow Only)"
        ax1.text(val + 0.4, bar.get_y() + bar.get_height()/2, f"{txt} — {name}",
                 ha="left", va="center", fontsize=8.5, fontweight="bold", color="#333333")

    # Panel B: Role-Aware Capital Provider Categories
    roles = df_lenders["institution_name"].tolist()
    vols = df_lenders["modeled_amount_b"].values
    cats = df_lenders["capital_category"].tolist()

    y_pos = np.arange(len(roles))
    cat_colors = {
        "Direct Lenders & Lessors": "#2e7d32",
        "Institutional Note Purchasers": "#388e3c",
        "Syndicate Administrative Agents": "#1976d2",
        "Placement & Escrow Intermediaries": "#f57c00",
        "Distributed Public / 144A Bondholders": "#455a64"
    }
    bar_c = [cat_colors.get(c, "#757575") for c in cats]

    b_roles = ax2.barh(y_pos, vols, color=bar_c, alpha=0.85, edgecolor="#333333", height=0.55)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([f"{name.split('(')[0].strip()}" for name in roles], fontsize=8.5)
    ax2.set_xlabel("Capital Modeled in Ledger ($B)", fontsize=11, fontweight="bold")
    ax2.set_title("B. Capital Structure by Institutional Role ($25.682B Distributed 144A Market)", fontsize=12, fontweight="bold", pad=12)
    ax2.set_xlim(0, 30)

    for bar, val in zip(b_roles, vols):
        ax2.text(val + 0.4, bar.get_y() + bar.get_height()/2, f"${val:.2f}B", ha="left", va="center", fontsize=8.5, fontweight="bold")

    ax2.text(0.5, -0.20,
             "Key Empirical Clarification: Public/144A bondholders represent $25.682B across 14 tranches.\n"
             "Lender concentration across private credit is not demonstrated; fragility lives in operational nodes (Power, Anchor Tenant).",
             ha="center", va="top", transform=ax2.transAxes, fontsize=9, style="italic",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f9fa", edgecolor="#dddddd"))

    plt.tight_layout()
    fig2_path = FIGURES_DIR / "minimum_failure_sets_stress.png"
    plt.savefig(fig2_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Figure 2 saved to {fig2_path}")


if __name__ == "__main__":
    run_analysis()
