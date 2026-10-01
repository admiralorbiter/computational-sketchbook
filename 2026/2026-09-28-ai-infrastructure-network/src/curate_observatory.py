"""Curate Canonical Observatory Parquet & CSV Datasets.

Generates the canonical datasets for the Infrastructure Stress Observatory:
    1. data/processed/observatory_scenarios.parquet (.csv)
    2. data/processed/observatory_indicators.parquet (.csv)
    3. data/processed/observatory_observations.parquet (.csv)

Enforces strict provenance, epistemic classifications, and bitemporal dates:
    - signal_role: EARLY_WARNING | CONFIRMATION | FINANCIAL_RECOGNITION | OUTCOME
    - observability: PUBLIC | COMMERCIAL_DATA | PRIVATE_OR_UNAVAILABLE
    - lead_time_status: OBSERVED | RIGHT_CENSORED_OBSERVED | MONITORING_WINDOW | HYPOTHESIZED_WINDOW
"""

import os
import pandas as pd

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed")


def build_scenarios_table() -> pd.DataFrame:
    """Builds the 6 certified reusable failure archetypes."""
    data = [
        {
            "scenario_id": "SCN-ARCH-001",
            "title": "Physical Milestone Misses Financial Payment Date",
            "archetype_exemplar": "BINARY_RENT_STEPUP",
            "project_exemplar": "Polaris Forge 1",
            "physical_clock_event": "Utility substation energization delayed past target commercial operation date",
            "contract_clock_event": "Commercial rent commencement blocked (tenant cash rent stays at $0)",
            "financial_clock_event": "Semiannual coupon payment date arrives (Months 6, 12, 18)",
            "support_clock_event": "DSRA / debt-service reserve drains toward zero",
            "binding_collision_condition": "T_energize > T_coupon_date AND DSRA_cash < InterestDue",
            "reconverging_entity": "Project SPV -> Bondholders (direct monetary payment default)",
            "subordinate_boundary_mechanic": "Discrete semiannual interest shortfall boundary; DSRA tier exhaustion threshold",
            "source_status": "DERIVED_DETERMINISTIC",
            "model_treatment": "EXACT",
            "valid_from": "2026-06-16",
            "known_from": "2026-06-16",
            "evidence_claim_ids": "CLM-APLD-008",
        },
        {
            "scenario_id": "SCN-ARCH-002",
            "title": "Contract Cash-Flow State Step-Down (Force-Majeure Dispute)",
            "archetype_exemplar": "MULTI_STATE_OFFTAKE_CARRY",
            "project_exemplar": "Project Jupiter",
            "physical_clock_event": "Pipeline ROW permit denied or delayed, impairing fuel delivery to microgrid",
            "contract_clock_event": "Tenant declares force majeure, disputing rent step-up and extending lower development-stage carry",
            "financial_clock_event": "Floating SOFR + 250 bps debt interest carry accrues on drawn loan (payment/reset frequency unobserved)",
            "support_clock_event": "Carry cash covers interest only if dev carry payment >= debt carry liability (up to 3-year obligation)",
            "binding_collision_condition": "T_permit_delay > T_carry_obligation_limit (3 years) OR DevCarry < DebtInterestDue",
            "reconverging_entity": "Project SPV -> Syndicated Bank Consortium (loan trading discount at 89-91c)",
            "subordinate_boundary_mechanic": "Monthly debt-service runway: T_runway = f(Liquidity, DevCarry, DebtService)",
            "source_status": "PRIMARY_DISCLOSED",
            "model_treatment": "CONDITIONAL",
            "valid_from": "2026-07-15",
            "known_from": "2026-09-24",
            "evidence_claim_ids": "CLM-JUP-001,CLM-JUP-002",
        },
        {
            "scenario_id": "SCN-ARCH-003",
            "title": "Reserve / Liquidity Exhaustion Before Commercial Operation",
            "archetype_exemplar": "BINARY_RENT_STEPUP",
            "project_exemplar": "Polaris Forge 1 (Silo 2)",
            "physical_clock_event": "Continuous physical commissioning slippage",
            "contract_clock_event": "Pre-operational period extended prior to Ready-for-Service",
            "financial_clock_event": "Reserve tier exhausted (e.g. 6-month or 12-month DSRA exhausted at coupon date)",
            "support_clock_event": "Operating cash drains to $0 via opex and debt service waterfall",
            "binding_collision_condition": "CumulativePreOperationalInterest > InitialReserves + OperatingCashInflows",
            "reconverging_entity": "Project SPV -> Bondholder Workout / Debt Acceleration Boundary (post-shortfall continuation unmodeled)",
            "subordinate_boundary_mechanic": "Exact cents-level reserve exhaustion milestone T_reserve_exhaustion",
            "source_status": "DERIVED_DETERMINISTIC",
            "model_treatment": "EXACT",
            "valid_from": "2026-06-16",
            "known_from": "2026-06-16",
            "evidence_claim_ids": "CLM-APLD-008",
        },
        {
            "scenario_id": "SCN-ARCH-004",
            "title": "Financing Availability Window Expiration Cliff",
            "archetype_exemplar": "STAGED_EQUIPMENT_ACCEPTANCE_CLIFF",
            "project_exemplar": "IREN Mackenzie",
            "physical_clock_event": "GPU hardware delivery, cluster commissioning, or customer qualification testing delayed",
            "contract_clock_event": "Equipment acceptance unachieved prior to December 31, 2026",
            "financial_clock_event": "Hard December 31, 2026 credit facility availability period ends (undrawn principal incurs no 9% coupon)",
            "support_clock_event": "Unaccepted equipment loses loan draw eligibility permanently",
            "binding_collision_condition": "T_acceptance > December 31, 2026 AND HardwareCommitted > DrawnPrincipal",
            "reconverging_entity": "Project SPV -> Borrower Capital Gap (replacement-funding requirement; unfinanced hardware capex exceeds committed debt)",
            "subordinate_boundary_mechanic": "Date-boundary slack: acceptance_slack_days = Dec 31, 2026 - T_acceptance; financing_capacity_at_risk calculated when unaccepted equipment value disclosed",
            "source_status": "PRIMARY_DISCLOSED",
            "model_treatment": "EXACT",
            "valid_from": "2026-08-25",
            "known_from": "2026-08-28",
            "evidence_claim_ids": "CLM-IREN-001",
        },
        {
            "scenario_id": "SCN-ARCH-005",
            "title": "Shared Sponsor / Parent Support Reconvergence",
            "archetype_exemplar": "SHARED_SPONSOR_RECONVERGENCE",
            "project_exemplar": "Polaris Forge 1 (Dual Silos)",
            "physical_clock_event": "Independent construction cost overruns across multiple legal silos",
            "contract_clock_event": "Completion guarantees triggered across both silos simultaneously",
            "financial_clock_event": "Separate project debt remains non-recourse, but parent balance sheet absorbs capex shortfalls",
            "support_clock_event": "Parent unrestricted corporate cash depleted by simultaneous capex cash calls",
            "binding_collision_condition": "Sum(Silo_i_CapexDeficit) > ParentCorporateCashAvailable",
            "reconverging_entity": "Independent Project SPVs -> Single Parent Sponsor (Applied Digital capex completion support)",
            "subordinate_boundary_mechanic": "Multi-silo capex deficit summation and pre-shortfall cash relief analysis",
            "source_status": "PRIMARY_DISCLOSED",
            "model_treatment": "CONDITIONAL",
            "valid_from": "2026-06-16",
            "known_from": "2026-06-16",
            "evidence_claim_ids": "CLM-APLD-005,CLM-APLD-006",
        },
        {
            "scenario_id": "SCN-ARCH-006",
            "title": "Refinancing / Maturity Collision in Dislocated Capital Markets",
            "archetype_exemplar": "MULTI_STATE_OFFTAKE_CARRY",
            "project_exemplar": "Project Jupiter / Polaris Forge 1",
            "physical_clock_event": "Delayed commissioning or prolonged dispute unresolved at facility maturity",
            "contract_clock_event": "Extension conditions (e.g. operational hurdles) unfulfilled",
            "financial_clock_event": "Four-year construction loan maturity (Jupiter) or 2030/2031 bullet maturity (PF1)",
            "support_clock_event": "Refinancing window blocked by debt market discount or rate environment",
            "binding_collision_condition": "T_refinance_date arrives WHILE SecondaryDiscount > Threshold OR RateSpike",
            "reconverging_entity": "Borrower SPV -> Debt Restructuring / Syndicate Workout",
            "subordinate_boundary_mechanic": "Maturity cliff evaluation vs debt yield and extension covenants",
            "source_status": "MARKET",
            "model_treatment": "CONDITIONAL",
            "valid_from": "2026-07-01",
            "known_from": "2026-07-01",
            "evidence_claim_ids": "CLM-MKT-001",
        },
    ]
    return pd.DataFrame(data)


def build_indicators_table() -> pd.DataFrame:
    """Builds the certified cross-project early-warning indicators with signal_role & observability."""
    data = [
        {
            "indicator_id": "IND-JUP-001",
            "project_id": "PROJECT_JUPITER",
            "archetype": "MULTI_STATE_OFFTAKE_CARRY",
            "name": "State Trust Land Pipeline Right-of-Way Denial",
            "layer": "REGULATORY",
            "signal_role": "EARLY_WARNING",
            "observability": "PUBLIC",
            "source_description": "New Mexico State Land Office (NMSLO) formal denial order and press release",
            "trigger_event": "Denial of ROW permit for 0.6-mile segment of 17-mile natural gas pipeline across state trust land",
            "affected_clock": "PHYSICAL",
            "threatened_boundary": "Fuel availability and operational energization date of 2,450 MW Bloom Energy microgrid",
            "lead_time_status": "OBSERVED",
            "lead_time_days_min": 65.0,
            "lead_time_days_max": 65.0,
            "lead_time_notes": "July 15, 2026 (NMSLO denial) -> September 18, 2026 (syndicated loan trading discount at 89-91c)",
            "source_status": "PRIMARY_DISCLOSED",
            "model_treatment": "EXACT",
            "valid_from": "2026-07-15",
            "known_from": "2026-07-15",
            "evidence_claim_ids": "CLM-JUP-001",
        },
        {
            "indicator_id": "IND-JUP-002",
            "project_id": "PROJECT_JUPITER",
            "archetype": "MULTI_STATE_OFFTAKE_CARRY",
            "name": "Tenant Offtake Force-Majeure Declaration",
            "layer": "CONTRACT_LEGAL",
            "signal_role": "EARLY_WARNING",
            "observability": "PUBLIC",
            "source_description": "Oracle formal legal notice citing pipeline permitting impasse",
            "trigger_event": "Notice invoking force majeure to extend development-stage carry and delay full operational rent",
            "affected_clock": "CONTRACT",
            "threatened_boundary": "Transition from development-stage carry to higher operational rent",
            "lead_time_status": "OBSERVED",
            "lead_time_days_min": 71.0,
            "lead_time_days_max": 71.0,
            "lead_time_notes": "July 15, 2026 (NMSLO denial) -> September 24, 2026 (Oracle force-majeure notice)",
            "source_status": "PRIMARY_DISCLOSED",
            "model_treatment": "EXACT",
            "valid_from": "2026-09-24",
            "known_from": "2026-09-24",
            "evidence_claim_ids": "CLM-JUP-002",
        },
        {
            "indicator_id": "IND-JUP-003",
            "project_id": "PROJECT_JUPITER",
            "archetype": "MULTI_STATE_OFFTAKE_CARRY",
            "name": "SEC EDGAR Public Corporate Disclosure Lag",
            "layer": "EDGAR_FILING",
            "signal_role": "CONFIRMATION",
            "observability": "PUBLIC",
            "source_description": "SEC Form 8-K / 10-Q filings by public sponsors (ORCL, OBDC)",
            "trigger_event": "Material disclosure of project permitting bottleneck or loan valuation impairment on EDGAR",
            "affected_clock": "FINANCIAL",
            "threatened_boundary": "Public market awareness of project distress and credit discount",
            "lead_time_status": "RIGHT_CENSORED_OBSERVED",
            "lead_time_days_min": 77.0,
            "lead_time_days_max": 77.0,
            "lead_time_notes": "July 15, 2026 (NMSLO denial) -> September 30, 2026 (0 filings on EDGAR; right-censored >= 77 days)",
            "source_status": "PRIMARY_DISCLOSED",
            "model_treatment": "EXACT",
            "valid_from": "2026-07-15",
            "known_from": "2026-09-30",
            "evidence_claim_ids": "CLM-JUP-003",
        },
        {
            "indicator_id": "IND-JUP-004",
            "project_id": "PROJECT_JUPITER",
            "archetype": "MULTI_STATE_OFFTAKE_CARRY",
            "name": "Syndicated Loan Secondary Trading Discount",
            "layer": "DEBT_MARKET",
            "signal_role": "FINANCIAL_RECOGNITION",
            "observability": "COMMERCIAL_DATA",
            "source_description": "Private credit & syndicated loan secondary trading quotes (Financial Times reporting)",
            "trigger_event": "Syndicated bank facility quotes drop to 89-91 cents on the dollar prior to public lease notice",
            "affected_clock": "FINANCIAL",
            "threatened_boundary": "Refinancing capacity and lender syndicate syndicate extension willingness",
            "lead_time_status": "OBSERVED",
            "lead_time_days_min": 0.0,
            "lead_time_days_max": 0.0,
            "lead_time_notes": "September 18, 2026 baseline financial recognition mark (establishes the 65-day lead from July 15)",
            "source_status": "MARKET",
            "model_treatment": "INTERVAL",
            "valid_from": "2026-09-18",
            "known_from": "2026-09-18",
            "evidence_claim_ids": "CLM-JUP-004",
        },
        {
            "indicator_id": "IND-PF1-001",
            "project_id": "POLARIS_FORGE_1",
            "archetype": "BINARY_RENT_STEPUP",
            "name": "Electric Utility Substation Interconnection Queue Filing",
            "layer": "UTILITY_DOCKET",
            "signal_role": "EARLY_WARNING",
            "observability": "PUBLIC",
            "source_description": "Montana-Dakota Utilities (MDU) / Otter Tail Power public regulatory dockets",
            "trigger_event": "Interconnection study report detailing transmission upgrade schedules or energization delays",
            "affected_clock": "PHYSICAL",
            "threatened_boundary": "Commercial commencement date gating Silo 1 / Silo 2 tenant operational rent",
            "lead_time_status": "MONITORING_WINDOW",
            "lead_time_days_min": 90.0,
            "lead_time_days_max": 180.0,
            "lead_time_notes": "Standard utility RTO interconnection study and filing revision cycle window",
            "source_status": "PRIMARY_DISCLOSED",
            "model_treatment": "CONDITIONAL",
            "valid_from": "2026-01-01",
            "known_from": "2026-01-01",
            "evidence_claim_ids": "CLM-APLD-009",
        },
        {
            "indicator_id": "IND-PF1-002",
            "project_id": "POLARIS_FORGE_1",
            "archetype": "BINARY_RENT_STEPUP",
            "name": "Sponsor Balance Sheet Liquidity Depletion",
            "layer": "EDGAR_FILING",
            "signal_role": "CONFIRMATION",
            "observability": "PUBLIC",
            "source_description": "Applied Digital (APLD) SEC Form 10-Q / 8-K cash & capital disclosures",
            "trigger_event": "Emergency convertible debt issuance, ATM equity offerings, or parent revolver exhaustion",
            "affected_clock": "SUPPORT",
            "threatened_boundary": "Parent ability to honor completion guarantees funding dual-silo construction deficits",
            "lead_time_status": "HYPOTHESIZED_WINDOW",
            "lead_time_days_min": 30.0,
            "lead_time_days_max": 90.0,
            "lead_time_notes": "Corporate liquidity burn trajectory preceding parent balance sheet exhaustion",
            "source_status": "PRIMARY_DISCLOSED",
            "model_treatment": "CONDITIONAL",
            "valid_from": "2026-06-16",
            "known_from": "2026-06-16",
            "evidence_claim_ids": "CLM-APLD-007",
        },
        {
            "indicator_id": "IND-MAC-001",
            "project_id": "IREN_MACKENZIE",
            "archetype": "STAGED_EQUIPMENT_ACCEPTANCE_CLIFF",
            "name": "GPU Equipment Delivery & Acceptance Testing Progress",
            "layer": "PHYSICAL_LOGISTICS",
            "signal_role": "EARLY_WARNING",
            "observability": "PRIVATE_OR_UNAVAILABLE",
            "source_description": "Hardware delivery manifests, customer acceptance testing logs, cloud RFS press releases",
            "trigger_event": "Hardware delivery slippage or customer qualification testing delays approaching December 31, 2026",
            "affected_clock": "PHYSICAL",
            "threatened_boundary": "Hard December 31, 2026 facility availability window expiration cliff",
            "lead_time_status": "MONITORING_WINDOW",
            "lead_time_days_min": 30.0,
            "lead_time_days_max": 60.0,
            "lead_time_notes": "Final equipment delivery and qualification window preceding December 31, 2026 facility expiration",
            "source_status": "UNOBSERVED",
            "model_treatment": "CONDITIONAL",
            "valid_from": "2026-08-25",
            "known_from": "2026-08-28",
            "evidence_claim_ids": "CLM-IREN-001",
        },
        {
            "indicator_id": "IND-MAC-002",
            "project_id": "IREN_MACKENZIE",
            "archetype": "STAGED_EQUIPMENT_ACCEPTANCE_CLIFF",
            "name": "Quarterly Debt Draw Exhibit Disclosure",
            "layer": "EDGAR_FILING",
            "signal_role": "FINANCIAL_RECOGNITION",
            "observability": "PUBLIC",
            "source_description": "IREN Limited SEC Form 10-Q Note on August 2026 Financing Agreements",
            "trigger_event": "Disclosed cumulative drawn borrowings under MFSA and Notes relative to $2.4B capacity",
            "affected_clock": "FINANCIAL",
            "threatened_boundary": "Unused commitment expiration and replacement-funding requirement",
            "lead_time_status": "MONITORING_WINDOW",
            "lead_time_days_min": 45.0,
            "lead_time_days_max": 60.0,
            "lead_time_notes": "Q1 FY27 Form 10-Q filing window (period ended Sept 30, 2026, filed Nov 2026)",
            "source_status": "PRIMARY_DISCLOSED",
            "model_treatment": "EXACT",
            "valid_from": "2026-09-30",
            "known_from": "2026-11-15",
            "evidence_claim_ids": "CLM-IREN-002",
        },
    ]
    return pd.DataFrame(data)


def build_observations_table() -> pd.DataFrame:
    """Builds the bitemporal observations tracking leading indicators to financial recognition."""
    data = [
        {
            "observation_id": "OBS-20260715-JUP01",
            "indicator_id": "IND-JUP-001",
            "project_id": "PROJECT_JUPITER",
            "source_event_date": "2026-07-15",
            "first_publicly_observable_date": "2026-07-15",
            "ingestion_date": "2026-09-30",
            "clock_affected": "PHYSICAL",
            "threatened_boundary": "Bloom Energy microgrid fuel supply & commercial energization date",
            "signal_role": "EARLY_WARNING",
            "observability": "PUBLIC",
            "headline_text": "NMSLO denies ROW permit across 0.6-mile state land segment for 17-mile natural gas pipeline",
            "raw_source_uri": "https://www.nmstatelands.org/orders/2026/07-15-pipeline-row-denial",
            "lead_time_days_to_financial_recognition": 65.0,
            "lead_time_status": "OBSERVED",
        },
        {
            "observation_id": "OBS-20260918-JUP02",
            "indicator_id": "IND-JUP-004",
            "project_id": "PROJECT_JUPITER",
            "source_event_date": "2026-09-18",
            "first_publicly_observable_date": "2026-09-18",
            "ingestion_date": "2026-09-30",
            "clock_affected": "FINANCIAL",
            "threatened_boundary": "Secondary debt market loan valuation and bank syndicate extension willingness",
            "signal_role": "FINANCIAL_RECOGNITION",
            "observability": "COMMERCIAL_DATA",
            "headline_text": "Project Jupiter ~$18B syndicated construction loan trades under pressure at 89-91 cents on the dollar",
            "raw_source_uri": "https://www.ft.com/content/a96bf05a-a299-4d6a-a753-b298dd0f4016",
            "lead_time_days_to_financial_recognition": 0.0,
            "lead_time_status": "OBSERVED",
        },
        {
            "observation_id": "OBS-20260924-JUP03",
            "indicator_id": "IND-JUP-002",
            "project_id": "PROJECT_JUPITER",
            "source_event_date": "2026-09-24",
            "first_publicly_observable_date": "2026-09-24",
            "ingestion_date": "2026-09-30",
            "clock_affected": "CONTRACT",
            "threatened_boundary": "Commercial offtake rent step-up (extends development carry)",
            "signal_role": "EARLY_WARNING",
            "observability": "PUBLIC",
            "headline_text": "Oracle issues formal force-majeure notice citing NMSLO natural gas pipeline permitting impasse",
            "raw_source_uri": "https://www.reuters.com/business/energy/oracle-force-majeure-new-mexico-20260924",
            "lead_time_days_to_financial_recognition": -6.0,  # 6 days after secondary debt recognition
            "lead_time_status": "OBSERVED",
        },
        {
            "observation_id": "OBS-20260930-JUP04",
            "indicator_id": "IND-JUP-003",
            "project_id": "PROJECT_JUPITER",
            "source_event_date": "2026-09-30",
            "first_publicly_observable_date": "2026-09-30",
            "ingestion_date": "2026-09-30",
            "clock_affected": "FINANCIAL",
            "threatened_boundary": "SEC EDGAR public corporate awareness of project permitting impasse",
            "signal_role": "CONFIRMATION",
            "observability": "PUBLIC",
            "headline_text": "Zero SEC Form 8-K or 10-Q disclosures filed by Oracle or Blue Owl OBDC regarding pipeline dispute as of Q3 end",
            "raw_source_uri": "https://www.sec.gov/edgar/searchedgar/companysearch",
            "lead_time_days_to_financial_recognition": None,
            "lead_time_status": "RIGHT_CENSORED_OBSERVED",
        },
        {
            "observation_id": "OBS-20260825-MAC01",
            "indicator_id": "IND-MAC-001",
            "project_id": "IREN_MACKENZIE",
            "source_event_date": "2026-08-25",
            "first_publicly_observable_date": "2026-08-28",
            "ingestion_date": "2026-10-01",
            "clock_affected": "FINANCIAL",
            "threatened_boundary": "Hard December 31, 2026 availability window expiration cliff",
            "signal_role": "EARLY_WARNING",
            "observability": "PUBLIC",
            "headline_text": "IE Mackenzie Compute enters up-to-$2.4B staged equipment financing facility with Blue Owl & PIMCO through Dec 31, 2026",
            "raw_source_uri": "https://www.sec.gov/Archives/edgar/data/1878848/000187884826000052/iren-20260630.htm",
            "lead_time_days_to_financial_recognition": None,
            "lead_time_status": "MONITORING_WINDOW",
        },
    ]
    return pd.DataFrame(data)


def main():
    """Generates all canonical Parquet and CSV files."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df_scenarios = build_scenarios_table()
    df_indicators = build_indicators_table()
    df_observations = build_observations_table()

    # Save scenarios
    scenarios_parquet = os.path.join(OUTPUT_DIR, "observatory_scenarios.parquet")
    scenarios_csv = os.path.join(OUTPUT_DIR, "observatory_scenarios.csv")
    df_scenarios.to_parquet(scenarios_parquet, index=False)
    df_scenarios.to_csv(scenarios_csv, index=False)
    print(f"Saved {len(df_scenarios)} scenarios to {scenarios_parquet}")

    # Save indicators
    indicators_parquet = os.path.join(OUTPUT_DIR, "observatory_indicators.parquet")
    indicators_csv = os.path.join(OUTPUT_DIR, "observatory_indicators.csv")
    df_indicators.to_parquet(indicators_parquet, index=False)
    df_indicators.to_csv(indicators_csv, index=False)
    print(f"Saved {len(df_indicators)} indicators to {indicators_parquet}")

    # Save observations
    observations_parquet = os.path.join(OUTPUT_DIR, "observatory_observations.parquet")
    observations_csv = os.path.join(OUTPUT_DIR, "observatory_observations.csv")
    df_observations.to_parquet(observations_parquet, index=False)
    df_observations.to_csv(observations_csv, index=False)
    print(f"Saved {len(df_observations)} observations to {observations_parquet}")


if __name__ == "__main__":
    main()
