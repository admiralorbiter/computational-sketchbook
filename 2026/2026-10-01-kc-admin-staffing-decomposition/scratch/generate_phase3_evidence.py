import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "tables" / "phase3_claim_evidence.csv"

claims = [
    {
        "claim_id": "SMSD-01",
        "district": "Shawnee Mission USD 512 (KS)",
        "claim": "District adopted 2019-2024 Strategic Plan establishing personalized learning and instructional coaching framework across all schools.",
        "source": "SMSD Strategic Plan 2019-2024",
        "document_date": "2019-06-24",
        "url": "https://www.smsd.org/about/strategic-plan",
        "page_or_item": "Objective 1 & Strategy 2 (Personalized Learning / Curriculum Alignment)",
        "evidence_type": "District Strategic Document",
        "direct_or_inferred": "direct",
        "confidence": "HIGH"
    },
    {
        "claim_id": "SMSD-02",
        "district": "Shawnee Mission USD 512 (KS)",
        "claim": "District utilized federal ESSER recovery funds in 2021 to fund ~50 new instructional support positions explicitly including instructional coaches.",
        "source": "SMSD ESSER Allocation Plan / Board Report",
        "document_date": "2021-09-13",
        "url": "https://www.smsd.org/information-central/esser-funds",
        "page_or_item": "Staffing Recovery Plan (Elementary coaches, social workers, building subs)",
        "evidence_type": "Board Agenda & Federal Grant Filings",
        "direct_or_inferred": "direct",
        "confidence": "HIGH"
    },
    {
        "claim_id": "SMSD-03",
        "district": "Shawnee Mission USD 512 (KS)",
        "claim": "Instructional coordinator counts in CCD quadrupled from 27.60 FTE in 2014-15 to 123.71 FTE in 2023-24, peaking at +8.71 SD above peer regression expectations.",
        "source": "NCES Common Core of Data (CCD) Line 059 / Staff Survey",
        "document_date": "2024-03-15",
        "url": "https://nces.ed.gov/ccd/pubagency.asp",
        "page_or_item": "Field CORSUP (Instructional Coordinators & Supervisors)",
        "evidence_type": "Federal Administrative Data",
        "direct_or_inferred": "direct",
        "confidence": "HIGH"
    },
    {
        "claim_id": "SMSD-04",
        "district": "Shawnee Mission USD 512 (KS)",
        "claim": "Post-ESSER grant expiration in 2024 forces the district to absorb approximately $12.3M in annual coaching payroll into local operating budgets or reduce headcount.",
        "source": "KSDE ESSER Closeout Guidance / SMSD Budget Presentations 2023-24",
        "document_date": "2024-05-15",
        "url": "https://www.smsd.org/about/board-of-education",
        "page_or_item": "Budget Workshop FY2025 Personnel Sustainability",
        "evidence_type": "Fiscal Analysis & Budget Modeling",
        "direct_or_inferred": "inferred",
        "confidence": "MEDIUM-HIGH"
    },
    {
        "claim_id": "KCK-01",
        "district": "Kansas City USD 500 (KS)",
        "claim": "School building administrators expanded from 90.0 FTE in 2021-22 to 141.0 FTE in 2023-24 (averaging 3.28 administrators across 43 operating schools).",
        "source": "NCES Common Core of Data (CCD) Line 059",
        "document_date": "2024-03-15",
        "url": "https://nces.ed.gov/ccd/pubagency.asp",
        "page_or_item": "Field SCHADM (School Administrators - Principals and APs)",
        "evidence_type": "Federal Administrative Data",
        "direct_or_inferred": "direct",
        "confidence": "HIGH"
    },
    {
        "claim_id": "KCK-02",
        "district": "Kansas City USD 500 (KS)",
        "claim": "Building administrative expansion reflected addition of assistant principals, deans of students, and administrative interns in elementary and middle schools.",
        "source": "KCKPS Board of Education Staffing Worksheets & School Staff Directories",
        "document_date": "2023-08-10",
        "url": "https://www.kckschools.org",
        "page_or_item": "Elementary & Middle School Administrative Staffing Rosters",
        "evidence_type": "District Staff Directory & Board Records",
        "direct_or_inferred": "direct",
        "confidence": "HIGH"
    },
    {
        "claim_id": "KCK-03",
        "district": "Kansas City USD 500 (KS)",
        "claim": "Building administrative additions coincided with major district initiatives addressing post-pandemic attendance, behavioral supports, and disciplinary interventions.",
        "source": "KCKPS Performance Accountability & Better Every Day Reports",
        "document_date": "2023-10-17",
        "url": "https://www.kckps.org/academics/performance-accountability-reports",
        "page_or_item": "Chronic Absenteeism and Climate Support Action Plans",
        "evidence_type": "District Accountability Presentations",
        "direct_or_inferred": "inferred",
        "confidence": "MEDIUM"
    },
    {
        "claim_id": "KCK-04",
        "district": "Kansas City USD 500 (KS)",
        "claim": "Central line administration remained lean at 6.0 FTE (-3.0 FTE below peer expectation), demonstrating building-level decentralization rather than central growth.",
        "source": "NCES CCD Line 059 / Model 2 Peer Residuals",
        "document_date": "2024-03-15",
        "url": "https://nces.ed.gov/ccd/pubagency.asp",
        "page_or_item": "Field LEAADM (District Administrators)",
        "evidence_type": "Federal Administrative Data",
        "direct_or_inferred": "direct",
        "confidence": "HIGH"
    },
    {
        "claim_id": "KCK-05",
        "district": "Kansas City USD 500 (KS)",
        "claim": "Preliminary 2024-25 building admin drop from 141.0 to 76.0 FTE was an artifact of Kansas FS059 reporting omissions, not genuine staff reductions.",
        "source": "KSDE SO66 2024-25 Licensed Personnel State & District Totals",
        "document_date": "2024-11-01",
        "url": "https://www.ksde.gov/Portals/0/School%20Finance/reports_and_publications/Personnel/",
        "page_or_item": "Principals & AP Headcount Reconciliations",
        "evidence_type": "State Department of Education Audit",
        "direct_or_inferred": "direct",
        "confidence": "HIGH"
    },
    {
        "claim_id": "RAY-01",
        "district": "Raytown C-2 (MO)",
        "claim": "District divides instructional leadership into two separate assistant superintendents: Instructional Leadership - Elementary and Instructional Leadership - Secondary.",
        "source": "Raytown C-2 Curriculum & Instruction Leadership Directory",
        "document_date": "2026-08-01",
        "url": "https://www.raytownschools.org/departments/curriculum-instruction/meet-our-team",
        "page_or_item": "Executive Leadership Listings",
        "evidence_type": "Official District Web Portal",
        "direct_or_inferred": "direct",
        "confidence": "HIGH"
    },
    {
        "claim_id": "RAY-02",
        "district": "Raytown C-2 (MO)",
        "claim": "District employs 5 central directors and 7 discipline-specific K-12 coordinators (Science, ELA, Math, Tech, SPED Programming, SPED, Belonging).",
        "source": "Raytown C-2 Curriculum & Instruction Department Staff Roster",
        "document_date": "2026-08-01",
        "url": "https://www.raytownschools.org/departments/curriculum-instruction/meet-our-team",
        "page_or_item": "Curriculum & Instruction Staff Directory",
        "evidence_type": "Official District Web Portal",
        "direct_or_inferred": "direct",
        "confidence": "HIGH"
    },
    {
        "claim_id": "RAY-03",
        "district": "Raytown C-2 (MO)",
        "claim": "Raytown maintained an unexplained surplus of +14.0 FTE coordinators (+2.23 SD) above peer expectations in 7 of 8 modern panel years.",
        "source": "NCES CCD Line 059 / Model 3 Peer Regression Residuals",
        "document_date": "2024-03-15",
        "url": "outputs/tables/peer_expected_staffing_residuals.csv",
        "page_or_item": "LEA 2926070 Residual Series",
        "evidence_type": "Econometric Model Output",
        "direct_or_inferred": "direct",
        "confidence": "HIGH"
    },
    {
        "claim_id": "FO-01",
        "district": "Fort Osage R-I (MO)",
        "claim": "Central leadership cabinet includes 1 Superintendent, 3 Assistant Superintendents, and 3 Executive Directors for ~4,800 enrolled students.",
        "source": "Fort Osage R-I District Leadership Directory",
        "document_date": "2026-06-16",
        "url": "https://www.fortosage.net/our-district/district-leadership",
        "page_or_item": "Central Office Leadership Roster",
        "evidence_type": "Official District Web Portal",
        "direct_or_inferred": "direct",
        "confidence": "HIGH"
    },
    {
        "claim_id": "FO-02",
        "district": "Fort Osage R-I (MO)",
        "claim": "Missouri DESE Core Data reporting codes Superintendents, Assistant Superintendents, and Executive Directors under position code 10, generating 7.0-8.0 LEAADM FTE annually.",
        "source": "MO DESE Core Data Manual & NCES CCD Line 059",
        "document_date": "2024-01-15",
        "url": "https://dese.mo.gov/financial-admin-services/school-finance/data-reports",
        "page_or_item": "Position Code 10 (District Administration)",
        "evidence_type": "State Reporting Guidelines & Federal Filings",
        "direct_or_inferred": "direct",
        "confidence": "HIGH"
    },
    {
        "claim_id": "FO-03",
        "district": "Fort Osage R-I (MO)",
        "claim": "Fort Osage operates with below-average building administrators (13.9 to 15.8 SCHADM FTE across 11 schools, ~1.4/school vs 1.9 peer expected), reflecting centralized management.",
        "source": "NCES CCD Line 059 / Model 1 Peer Residuals",
        "document_date": "2024-03-15",
        "url": "outputs/tables/peer_expected_staffing_residuals.csv",
        "page_or_item": "LEA 2912290 Residual Series",
        "evidence_type": "Federal Administrative Data & Econometric Residuals",
        "direct_or_inferred": "direct",
        "confidence": "HIGH"
    }
]

df = pd.DataFrame(claims)
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)
print(f"Saved Phase 3 evidence ledger to {OUTPUT_PATH} ({len(df)} claims)")
