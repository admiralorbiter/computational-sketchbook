"""
Curate Facility Completion Facts (ADR-021.1a)
Moves typed facility dimensions from hardcoded Python structures into a canonical evidence table.
Produces data/processed/facility_completion_facts.parquet and .csv.

Dimensions captured:
- utility_service_capacity_mw: Total utility agreement service capacity (MW)
- utility_load_online_mw: Utility load energized and online as of observation horizon (MW)
- critical_it_contracted_mw: Contracted critical IT capacity under lease/colocation (MW)
- service_ready_it_mw: Critical IT capacity certified ready-for-service / operating (MW)
- gpu_equipment_deployment_state: Textual description of GPU / cluster deployment status
- gpu_compute_operational_mw: IT load with operational GPUs actively executing compute (MW)
- equipment_accepted_fraction: Fraction of IT equipment delivered, accepted, and funded (0.0 to 1.0)
- completion_status: Categorical status of facility buildout
- next_milestone: Next development or energization milestone
- Bitemporal provenance: economic_as_of, publicly_known_from, truth_claim_id, knowledge_claim_id, evidence_class
"""

from pathlib import Path
import pandas as pd
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"


def curate_facility_completion_facts():
    fac_df = pd.read_parquet(PROCESSED_DIR / "facilities.parquet")
    clm_df = pd.read_parquet(PROCESSED_DIR / "evidence_claims.parquet")
    pwr_clm_df = pd.read_parquet(PROCESSED_DIR / "power_claims.parquet")
    all_claims = pd.concat([clm_df, pwr_clm_df], ignore_index=True)
    claims_dict = {r["claim_id"]: r["filing_date"] for _, r in all_claims.iterrows()}

    facts = [
        {
            "facility_id": "FAC-APLD-POLARIS-FORGE-1",
            "facility_name": "Polaris Forge 1 (Ellendale)",
            "operator_entity_id": "APLD",
            "utility_service_capacity_mw": 350.0,
            "utility_load_online_mw": 60.0,
            "critical_it_contracted_mw": 400.0,
            "service_ready_it_mw": 100.0,
            "gpu_equipment_deployment_state": "Tenant (CoreWeave) cluster commissioning & fit-out",
            "gpu_compute_operational_mw": None,
            "equipment_accepted_fraction": None,
            "completion_status": "operational_and_expanding",
            "next_milestone": "Building 2 full tenant occupancy & Building 3 commissioning (2026-2027)",
            "economic_as_of": "2026-05-31",
            "publicly_known_from": "2026-07-29",
            "truth_claim_id": "CLM-APLD-004",
            "knowledge_claim_id": "CLM-APLD-004",
            "evidence_class": "A",
            "verifier_notes": "100 MW Building 2 operational; 150 MW Building 3 partially operational; 150 MW Building 4 under construction. MDU reports 60 MW initial service ramp toward 350 MW approved agreement."
        },
        {
            "facility_id": "FAC-APLD-POLARIS-FORGE-2",
            "facility_name": "Polaris Forge 2",
            "operator_entity_id": "APLD",
            "utility_service_capacity_mw": None,
            "utility_load_online_mw": None,
            "critical_it_contracted_mw": 200.0,
            "service_ready_it_mw": 0.0,
            "gpu_equipment_deployment_state": "Civil / electrical shell construction",
            "gpu_compute_operational_mw": None,
            "equipment_accepted_fraction": 0.0,
            "completion_status": "under_construction",
            "next_milestone": "Initial capacity H2 2026; full 200 MW early 2027",
            "economic_as_of": "2026-05-31",
            "publicly_known_from": "2026-07-29",
            "truth_claim_id": "CLM-APLD-003",
            "knowledge_claim_id": "CLM-APLD-011",
            "evidence_class": "A",
            "verifier_notes": "Under active construction. $2.15B gross proceeds held in escrow until electric service agreement satisfied on June 18, 2026."
        },
        {
            "facility_id": "FAC-IREN-MACKENZIE",
            "facility_name": "Mackenzie Data Center",
            "operator_entity_id": "IREN",
            "utility_service_capacity_mw": 80.0,
            "utility_load_online_mw": 80.0,
            "critical_it_contracted_mw": 80.0,
            "service_ready_it_mw": 80.0,
            "gpu_equipment_deployment_state": "Staged GPU server delivery & acceptance through Dec 31, 2026",
            "gpu_compute_operational_mw": None,
            "equipment_accepted_fraction": 0.0,
            "completion_status": "operational_and_expanding",
            "next_milestone": "GPU server staged delivery & acceptance through Dec 31, 2026",
            "economic_as_of": "2026-06-30",
            "publicly_known_from": "2026-08-27",
            "truth_claim_id": "CLM-IREN-001",
            "knowledge_claim_id": "CLM-IREN-001",
            "evidence_class": "A",
            "verifier_notes": "Facility infrastructure fully energized at 80 MW under BC Hydro connection agreement. $2.4B financing staged to delivery and acceptance conditions."
        },
        {
            "facility_id": "FAC-CORZ-DENTON",
            "facility_name": "Denton Data Center Campus",
            "operator_entity_id": "CORZ",
            "utility_service_capacity_mw": 394.0,
            "utility_load_online_mw": 100.0,
            "critical_it_contracted_mw": 270.0,
            "service_ready_it_mw": 100.0,
            "gpu_equipment_deployment_state": "Tenant fit-out / ongoing colocation conversion",
            "gpu_compute_operational_mw": None,
            "equipment_accepted_fraction": None,
            "completion_status": "operational_and_expanding",
            "next_milestone": "Colocation fit-out across multi-building campus",
            "economic_as_of": "2026-06-30",
            "publicly_known_from": "2026-07-28",
            "truth_claim_id": "CLM-CORZ-001",
            "knowledge_claim_id": "CLM-CORZ-001",
            "evidence_class": "A",
            "verifier_notes": "394 MW total DME utility agreement; 100 MW initial colocation data hall energized and leased to CoreWeave out of 270 MW contracted."
        },
        {
            "facility_id": "FAC-CORZ-DALTON",
            "facility_name": "Dalton Facility",
            "operator_entity_id": "CORZ",
            "utility_service_capacity_mw": 195.0,
            "utility_load_online_mw": None,
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": None,
            "gpu_equipment_deployment_state": "HPC infrastructure retrofit from mining",
            "gpu_compute_operational_mw": None,
            "equipment_accepted_fraction": None,
            "completion_status": "operational",
            "next_milestone": "HPC infrastructure retrofit from mining",
            "economic_as_of": "2025-12-31",
            "publicly_known_from": "2026-03-02",
            "truth_claim_id": "CLM-PWR-CORZ-001",
            "knowledge_claim_id": "CLM-PWR-CORZ-001",
            "evidence_class": "A",
            "verifier_notes": "195 MW Dalton Utilities agreement. Operational bitcoin mining infrastructure undergoing staged HPC retrofit."
        },
        {
            "facility_id": "FAC-CORZ-MUSKOGEE",
            "facility_name": "Muskogee Facility",
            "operator_entity_id": "CORZ",
            "utility_service_capacity_mw": 100.0,
            "utility_load_online_mw": None,
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": None,
            "gpu_equipment_deployment_state": "HPC infrastructure retrofit from mining",
            "gpu_compute_operational_mw": None,
            "equipment_accepted_fraction": None,
            "completion_status": "operational",
            "next_milestone": "HPC infrastructure retrofit from mining",
            "economic_as_of": "2025-12-31",
            "publicly_known_from": "2026-03-02",
            "truth_claim_id": "CLM-PWR-CORZ-001",
            "knowledge_claim_id": "CLM-PWR-CORZ-001",
            "evidence_class": "A",
            "verifier_notes": "100 MW OG&E agreement. Operational bitcoin mining site undergoing staged HPC retrofit."
        },
        {
            "facility_id": "FAC-CORZ-MARBLE",
            "facility_name": "Marble Facility",
            "operator_entity_id": "CORZ",
            "utility_service_capacity_mw": 117.0,
            "utility_load_online_mw": None,
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": None,
            "gpu_equipment_deployment_state": "HPC infrastructure retrofit from mining",
            "gpu_compute_operational_mw": None,
            "equipment_accepted_fraction": None,
            "completion_status": "operational",
            "next_milestone": "HPC infrastructure retrofit from mining",
            "economic_as_of": "2025-12-31",
            "publicly_known_from": "2026-03-02",
            "truth_claim_id": "CLM-PWR-CORZ-001",
            "knowledge_claim_id": "CLM-PWR-CORZ-001",
            "evidence_class": "A",
            "verifier_notes": "117 MW dual utility supply (82 MW Duke Energy, 35 MW Murphy EPB). Operational bitcoin mining site undergoing staged HPC retrofit."
        },
        {
            "facility_id": "FAC-CORZ-AUSTIN",
            "facility_name": "Austin Facility",
            "operator_entity_id": "CORZ",
            "utility_service_capacity_mw": 20.0,
            "utility_load_online_mw": None,
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": None,
            "gpu_equipment_deployment_state": "HPC infrastructure retrofit from mining",
            "gpu_compute_operational_mw": None,
            "equipment_accepted_fraction": None,
            "completion_status": "operational",
            "next_milestone": "HPC infrastructure retrofit from mining",
            "economic_as_of": "2025-12-31",
            "publicly_known_from": "2026-03-02",
            "truth_claim_id": "CLM-PWR-CORZ-001",
            "knowledge_claim_id": "CLM-PWR-CORZ-001",
            "evidence_class": "A",
            "verifier_notes": "20 MW Austin Energy municipal service. Small operational testbed / retrofit facility."
        },
        {
            "facility_id": "FAC-WULF-LAKE-MARINER",
            "facility_name": "Lake Mariner Facility",
            "operator_entity_id": "WULF",
            "utility_service_capacity_mw": 226.0,
            "utility_load_online_mw": 226.0,
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": 226.0,
            "gpu_equipment_deployment_state": "Operational mining / 500 MW expansion engineering",
            "gpu_compute_operational_mw": None,
            "equipment_accepted_fraction": None,
            "completion_status": "operational_and_expanding",
            "next_milestone": "500 MW planned expansion engineering",
            "economic_as_of": "2026-06-30",
            "publicly_known_from": "2026-08-05",
            "truth_claim_id": "CLM-WULF-001",
            "knowledge_claim_id": "CLM-WULF-001",
            "evidence_class": "A",
            "verifier_notes": "226 MW operational energization from NYPA / National Grid. Expansion engineering underway toward 500 MW target."
        },
        {
            "facility_id": "FAC-IREN-CHILDRESS",
            "facility_name": "Childress Facility",
            "operator_entity_id": "IREN",
            "utility_service_capacity_mw": 750.0,
            "utility_load_online_mw": 650.0,
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": 650.0,
            "gpu_equipment_deployment_state": "Operating mining & cloud pilot",
            "gpu_compute_operational_mw": None,
            "equipment_accepted_fraction": None,
            "completion_status": "operational_and_expanding",
            "next_milestone": "Final 100 MW substation expansion to 750 MW",
            "economic_as_of": "2025-06-30",
            "publicly_known_from": "2025-08-28",
            "truth_claim_id": "CLM-PWR-IREN-001",
            "knowledge_claim_id": "CLM-PWR-IREN-001",
            "evidence_class": "A",
            "verifier_notes": "750 MW executed connection agreement with AEP Texas in ERCOT. 650 MW substation energized and operational."
        },
        {
            "facility_id": "FAC-IREN-SWEETWATER-1",
            "facility_name": "Sweetwater 1",
            "operator_entity_id": "IREN",
            "utility_service_capacity_mw": 1400.0,
            "utility_load_online_mw": None,
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": 0.0,
            "gpu_equipment_deployment_state": "Substation procurement & interconnection construction",
            "gpu_compute_operational_mw": None,
            "equipment_accepted_fraction": 0.0,
            "completion_status": "under_construction",
            "next_milestone": "Interconnection substation construction (1,400 MW)",
            "economic_as_of": "2025-06-30",
            "publicly_known_from": "2025-08-28",
            "truth_claim_id": "CLM-PWR-IREN-001",
            "knowledge_claim_id": "CLM-PWR-IREN-001",
            "evidence_class": "A",
            "verifier_notes": "1,400 MW connection agreement executed with Oncor in ERCOT. Not energized; under substation procurement and construction."
        },
        {
            "facility_id": "FAC-IREN-SWEETWATER-2",
            "facility_name": "Sweetwater 2",
            "operator_entity_id": "IREN",
            "utility_service_capacity_mw": 600.0,
            "utility_load_online_mw": None,
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": 0.0,
            "gpu_equipment_deployment_state": "AEP Texas substation engineering",
            "gpu_compute_operational_mw": None,
            "equipment_accepted_fraction": 0.0,
            "completion_status": "under_construction",
            "next_milestone": "AEP Texas 600 MW substation engineering",
            "economic_as_of": "2025-06-30",
            "publicly_known_from": "2025-08-28",
            "truth_claim_id": "CLM-PWR-IREN-001",
            "knowledge_claim_id": "CLM-PWR-IREN-001",
            "evidence_class": "A",
            "verifier_notes": "600 MW connection agreement executed with AEP Texas in ERCOT. Not energized; preliminary substation engineering."
        },
        {
            "facility_id": "FAC-NBIS-MANTSALA",
            "facility_name": "Mantsala Data Center",
            "operator_entity_id": "NBIS",
            "utility_service_capacity_mw": 75.0,
            "utility_load_online_mw": 75.0,
            "critical_it_contracted_mw": 75.0,
            "service_ready_it_mw": 75.0,
            "gpu_equipment_deployment_state": "Fully operational GPU cluster operations",
            "gpu_compute_operational_mw": 75.0,
            "equipment_accepted_fraction": 1.0,
            "completion_status": "operational",
            "next_milestone": "Commercial operational service / heat recovery",
            "economic_as_of": "2025-12-31",
            "publicly_known_from": "2026-03-31",
            "truth_claim_id": "CLM-PWR-NBIS-002",
            "knowledge_claim_id": "CLM-PWR-NBIS-002",
            "evidence_class": "A",
            "verifier_notes": "75 MW connection with Nivos in Fingrid zone. Fully energized and hosting commercial GPU clusters."
        },
        {
            "facility_id": "FAC-NBIS-LAPPEENRANTA",
            "facility_name": "Lappeenranta Project",
            "operator_entity_id": "NBIS",
            "utility_service_capacity_mw": 310.0,
            "utility_load_online_mw": None,
            "critical_it_contracted_mw": None,
            "service_ready_it_mw": 0.0,
            "gpu_equipment_deployment_state": "Engineering design / pre-construction",
            "gpu_compute_operational_mw": None,
            "equipment_accepted_fraction": 0.0,
            "completion_status": "announced",
            "next_milestone": "Pending grid interconnection & engineering review",
            "economic_as_of": "2025-12-31",
            "publicly_known_from": "2026-04-30",
            "truth_claim_id": "CLM-PWR-NBIS-001",
            "knowledge_claim_id": "CLM-PWR-NBIS-001",
            "evidence_class": "B",
            "verifier_notes": "310 MW planned development in Finland. Grid connection study and pre-construction engineering underway."
        },
    ]

    facts_df = pd.DataFrame(facts)

    # Validate foreign keys
    fac_ids = set(fac_df["facility_id"])
    assert set(facts_df["facility_id"]) == fac_ids, f"Facility mismatch: {set(facts_df['facility_id']) ^ fac_ids}"

    # Validate bitemporal timing
    for _, r in facts_df.iterrows():
        fid = r["facility_id"]
        k_cid = r["knowledge_claim_id"]
        if k_cid in claims_dict:
            k_fdate = str(claims_dict[k_cid])
            assert str(r["publicly_known_from"]) >= k_fdate, (
                f"Facility {fid}: publicly_known_from {r['publicly_known_from']} predates knowledge claim {k_cid} filing date {k_fdate}"
            )

    # Save to parquet and csv
    facts_df.to_parquet(PROCESSED_DIR / "facility_completion_facts.parquet", index=False)
    facts_df.to_csv(PROCESSED_DIR / "facility_completion_facts.csv", index=False)
    print(f"Curated {len(facts_df)} facility completion facts to facility_completion_facts.parquet and .csv")


if __name__ == "__main__":
    curate_facility_completion_facts()
