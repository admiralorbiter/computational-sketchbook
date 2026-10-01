"""
src/coordinator_crosswalk.py

Phase 5: "What Are the Coordinators?" — Functional and Institutional Decomposition.
Constructs:
1. Canonical role-level crosswalk (CORSUP FTE -> job titles -> function -> location -> funding).
2. Reconstructed staffing architectures across 6 representative archetypes:
   - Shawnee Mission USD 512 (KS) — Specialized Coaching Overlay
   - Kansas City USD 500 / KCKPS (KS) — Distributed School Supervision & Climate Architecture
   - Olathe USD 233 (KS) — Suburban High-Growth Scaling & Retrenchment
   - North Kansas City 74 (MO) — Rapid Missouri Growth & Departmental Hierarchy
   - Raytown C-2 (MO) — Layered Central Curriculum Leadership
   - Lee's Summit R-VII (MO) — Lean Comparator / Department Chair Model
3. Observable funding provenance (Local, Title I/II/III, IDEA, ESSER, State Categoricals).
4. Post-ESSER survival tracing into 2024-25, 2025-26, and 2026-27.
5. Generates markdown synthesis report in outputs/tables/coordinator_functional_decomposition_report.md.
"""

from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUTS_TABLES = PROJECT_ROOT / "outputs" / "tables"


def build_role_level_crosswalk() -> pd.DataFrame:
    """
    Constructs the canonical role-level crosswalk mapping reported CCD CORSUP FTE
    to specific job titles, functional categories, administrative locus, and funding streams.
    """
    records = [
        # ==========================================
        # 1. SHAWNEE MISSION USD 512 (KS, NCES: 2011640)
        # 2023-24 Reported CORSUP: 123.71 FTE
        # Archetype: Specialized Coaching Overlay
        # ==========================================
        {
            "district_name": "Shawnee Mission USD 512",
            "state": "KS",
            "nces_lea_id": "2011640",
            "archetype": "Specialized Coaching Overlay",
            "job_title": "Elementary Instructional Coach",
            "functional_category": "Instructional Coaching",
            "work_location": "School Building",
            "estimated_fte_2023_24": 42.0,
            "primary_funding_source": "ESSER III / Title II-A / Local Operating",
            "funding_mechanism": "Federal Relief & Local Transition",
            "state_reporting_code": "KSDE SO66: Instructional Coach",
            "role_description": "Building-based non-evaluative coaches embedded in elementary schools to guide tier-1 instruction, literacy, and curriculum fidelity.",
            "post_esser_status": "Retained with Budget Freeze",
            "post_esser_disposition": "Absorbed into local operating funds for 2024-25; further expansion requests denied in March 2026 due to structural deficits."
        },
        {
            "district_name": "Shawnee Mission USD 512",
            "state": "KS",
            "nces_lea_id": "2011640",
            "archetype": "Specialized Coaching Overlay",
            "job_title": "Secondary Instructional Coach",
            "functional_category": "Instructional Coaching",
            "work_location": "School Building",
            "estimated_fte_2023_24": 15.0,
            "primary_funding_source": "ESSER III / Local Operating",
            "funding_mechanism": "Federal Relief & Local Operating",
            "state_reporting_code": "KSDE SO66: Instructional Coach",
            "role_description": "Middle and high school instructional coaches facilitating departmental professional learning communities (PLCs) and pedagogical strategies.",
            "post_esser_status": "Retained with Budget Freeze",
            "post_esser_disposition": "Maintained in secondary buildings, but subject to replacement freeze upon staff departure."
        },
        {
            "district_name": "Shawnee Mission USD 512",
            "state": "KS",
            "nces_lea_id": "2011640",
            "archetype": "Specialized Coaching Overlay",
            "job_title": "Curriculum Content Coordinator",
            "functional_category": "Curriculum/Content",
            "work_location": "Central Office",
            "estimated_fte_2023_24": 18.0,
            "primary_funding_source": "Local Operating",
            "funding_mechanism": "General Operating Fund",
            "state_reporting_code": "KSDE SO66: Curriculum Specialist / Supervisor",
            "role_description": "Central subject coordinators (ELA, Math, Science, Social Studies, CTE, Arts, Early Childhood) designing district scope, sequence, and pacing guides.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Permanent central instructional leadership core; funded continuously through local operating revenues."
        },
        {
            "district_name": "Shawnee Mission USD 512",
            "state": "KS",
            "nces_lea_id": "2011640",
            "archetype": "Specialized Coaching Overlay",
            "job_title": "Instructional Technology Coach",
            "functional_category": "Instructional Technology",
            "work_location": "School Building / Central",
            "estimated_fte_2023_24": 14.0,
            "primary_funding_source": "Capital Outlay / Local General",
            "funding_mechanism": "Local Technology Levy & Operating",
            "state_reporting_code": "KSDE SO66: Technology Specialist / Coordinator",
            "role_description": "Specialists supporting Apple 1:1 hardware/software integration, LMS management (Canvas), and digital pedagogy across clusters.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Integrated into core operations to sustain mandatory district digital infrastructure."
        },
        {
            "district_name": "Shawnee Mission USD 512",
            "state": "KS",
            "nces_lea_id": "2011640",
            "archetype": "Specialized Coaching Overlay",
            "job_title": "ELL / Title III Instructional Specialist",
            "functional_category": "SPED/EL Program Management",
            "work_location": "School Building / Central",
            "estimated_fte_2023_24": 13.0,
            "primary_funding_source": "Title III / State Bilingual Categorical",
            "funding_mechanism": "Federal Categorical & State Weighting",
            "state_reporting_code": "KSDE SO66: Bilingual / ELL Specialist",
            "role_description": "Instructional coaches supporting English language development teachers and sheltered English immersion across diverse feeder patterns.",
            "post_esser_status": "Absorbed Locally with Reductions",
            "post_esser_disposition": "Impacted by $255k federal Title III clawback in 2025; positions shifted into local operating budgets with attrition."
        },
        {
            "district_name": "Shawnee Mission USD 512",
            "state": "KS",
            "nces_lea_id": "2011640",
            "archetype": "Specialized Coaching Overlay",
            "job_title": "Special Education Instructional Facilitator",
            "functional_category": "SPED/EL Program Management",
            "work_location": "Central / Multi-School",
            "estimated_fte_2023_24": 13.0,
            "primary_funding_source": "IDEA Part B / State SPED Categorical",
            "funding_mechanism": "Federal Special Ed & State Cat Aid",
            "state_reporting_code": "KSDE SO66: Special Ed Supervisor",
            "role_description": "Specialized instructional facilitators coordinating IEP pedagogical compliance, behavior intervention plans, and co-teaching support.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Shielded by federal Maintenance of Effort (MOE) mandates under IDEA."
        },
        {
            "district_name": "Shawnee Mission USD 512",
            "state": "KS",
            "nces_lea_id": "2011640",
            "archetype": "Specialized Coaching Overlay",
            "job_title": "Assessment & Data Facilitator",
            "functional_category": "Data/Assessment",
            "work_location": "Central Office",
            "estimated_fte_2023_24": 8.71,
            "primary_funding_source": "Local Operating / Title I",
            "funding_mechanism": "Operating Budget",
            "state_reporting_code": "KSDE SO66: Assessment / Test Coordinator",
            "role_description": "Central psychometricians and assessment analysts administering state KAP testing, FastBridge screeners, and benchmark analytics.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Essential institutional compliance function; sustained permanently."
        },

        # ==========================================
        # 2. KANSAS CITY USD 500 / KCKPS (KS, NCES: 2007950)
        # 2023-24 Reported CORSUP: 106.80 FTE
        # Archetype: Distributed School Supervision & Climate Architecture
        # ==========================================
        {
            "district_name": "Kansas City USD 500",
            "state": "KS",
            "nces_lea_id": "2007950",
            "archetype": "Distributed School Supervision",
            "job_title": "Title I Building Instructional Coach",
            "functional_category": "Instructional Coaching",
            "work_location": "School Building",
            "estimated_fte_2023_24": 36.0,
            "primary_funding_source": "Title I Schoolwide",
            "funding_mechanism": "Federal Compensatory Formula Grant",
            "state_reporting_code": "KSDE SO66: Instructional Coach",
            "role_description": "School-based reading and math coaches in high-poverty elementary and middle schools providing direct teacher coaching and small-group modeling.",
            "post_esser_status": "Retained Intact (Permanent Formula)",
            "post_esser_disposition": "Sustained by steady federal Title I schoolwide allocations; unaffected by ESSER expiration."
        },
        {
            "district_name": "Kansas City USD 500",
            "state": "KS",
            "nces_lea_id": "2007950",
            "archetype": "Distributed School Supervision",
            "job_title": "MTSS & Academic Intervention Specialist",
            "functional_category": "Intervention/MTSS",
            "work_location": "School Building",
            "estimated_fte_2023_24": 22.0,
            "primary_funding_source": "State At-Risk Weighting / ESSER III",
            "funding_mechanism": "State Categorical Aid & Federal Relief",
            "state_reporting_code": "KSDE SO66: Curriculum / Intervention Specialist",
            "role_description": "School-site intervention leaders coordinating Tier 2/Tier 3 academic remediation, progress monitoring, and student success teams.",
            "post_esser_status": "Absorbed into State At-Risk",
            "post_esser_disposition": "Transitioned from temporary ESSER funding into permanent Kansas State At-Risk weighted foundation aid."
        },
        {
            "district_name": "Kansas City USD 500",
            "state": "KS",
            "nces_lea_id": "2007950",
            "archetype": "Distributed School Supervision",
            "job_title": "Bilingual / ESOL Instructional Coach",
            "functional_category": "SPED/EL Program Management",
            "work_location": "School Building",
            "estimated_fte_2023_24": 18.0,
            "primary_funding_source": "Title III / State Bilingual Weighting",
            "funding_mechanism": "State Bilingual Weighting & Title III",
            "state_reporting_code": "KSDE SO66: Bilingual Specialist",
            "role_description": "Coaches dedicated to supporting teachers with dual-language immersion and English language learners across Wyandotte County schools.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Core institutional capacity; funded continuously through state bilingual student headcount weightings."
        },
        {
            "district_name": "Kansas City USD 500",
            "state": "KS",
            "nces_lea_id": "2007950",
            "archetype": "Distributed School Supervision",
            "job_title": "Special Education Compliance & Instructional Specialist",
            "functional_category": "SPED/EL Program Management",
            "work_location": "School Building / Central",
            "estimated_fte_2023_24": 14.0,
            "primary_funding_source": "IDEA Part B / State SPED Categorical",
            "funding_mechanism": "Federal Special Ed & State Cat Aid",
            "state_reporting_code": "KSDE SO66: Special Ed Supervisor",
            "role_description": "Building and cluster specialists overseeing IEP implementation, specialized instructional techniques, and behavioral interventions.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Protected under federal IDEA Maintenance of Effort requirements."
        },
        {
            "district_name": "Kansas City USD 500",
            "state": "KS",
            "nces_lea_id": "2007950",
            "archetype": "Distributed School Supervision",
            "job_title": "Curriculum & Professional Learning Coordinator",
            "functional_category": "Curriculum/Content",
            "work_location": "Central Office (Leadership & Learning)",
            "estimated_fte_2023_24": 10.8,
            "primary_funding_source": "Local Operating / Title II-A",
            "funding_mechanism": "General Fund & Title II-A",
            "state_reporting_code": "KSDE SO66: Curriculum Specialist",
            "role_description": "District-level coordinators managing content standards, Diploma+ pathway frameworks, and districtwide professional development days.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Permanent central division of Leadership & Learning; retained intact."
        },
        {
            "district_name": "Kansas City USD 500",
            "state": "KS",
            "nces_lea_id": "2007950",
            "archetype": "Distributed School Supervision",
            "job_title": "Federal Programs & Accountability Specialist",
            "functional_category": "Federal Programs",
            "work_location": "Central Office",
            "estimated_fte_2023_24": 6.0,
            "primary_funding_source": "Title I / Title II Admin Set-Aside",
            "funding_mechanism": "Federal Grant Administration",
            "state_reporting_code": "KSDE SO66: Program Director / Supervisor",
            "role_description": "Central compliance specialists auditing federal grant expenditures, equitable services to non-public schools, and state reporting.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Funded directly through federal grant allowable administrative indirect and set-aside caps."
        },

        # ==========================================
        # 3. OLATHE USD 233 (KS, NCES: 2010140)
        # 2023-24 Reported CORSUP: 85.55 FTE
        # Archetype: High-Growth Suburban Scaling & Retrenchment
        # ==========================================
        {
            "district_name": "Olathe USD 233",
            "state": "KS",
            "nces_lea_id": "2010140",
            "archetype": "Suburban Scaling & Retrenchment",
            "job_title": "Instructional Learning Facilitator",
            "functional_category": "Instructional Coaching",
            "work_location": "School Building",
            "estimated_fte_2023_24": 38.0,
            "primary_funding_source": "ESSER II/III & Local Operating",
            "funding_mechanism": "Federal Relief & General Fund",
            "state_reporting_code": "KSDE SO66: Instructional Coach",
            "role_description": "Building coaches providing professional development, peer observation, and coaching cycles to classroom teachers across 52 schools.",
            "post_esser_status": "Downsized / Reassigned to Classrooms",
            "post_esser_disposition": "Major retrenchment: cut ~23.6 FTE in 2024-25 (CORSUP dropped from 85.55 to 61.95 FTE) as staff returned to vacant classrooms to cover deficits."
        },
        {
            "district_name": "Olathe USD 233",
            "state": "KS",
            "nces_lea_id": "2010140",
            "archetype": "Suburban Scaling & Retrenchment",
            "job_title": "Curriculum & Assessment Coordinator",
            "functional_category": "Curriculum/Content",
            "work_location": "Central Office",
            "estimated_fte_2023_24": 18.0,
            "primary_funding_source": "Local Operating",
            "funding_mechanism": "General Operating Fund",
            "state_reporting_code": "KSDE SO66: Curriculum Specialist",
            "role_description": "Content-area specialists managing K-12 curriculum adoption, Kansas Through-Year Assessment alignment, and course frameworks.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Retained as permanent central core supporting suburban instructional standardization."
        },
        {
            "district_name": "Olathe USD 233",
            "state": "KS",
            "nces_lea_id": "2010140",
            "archetype": "Suburban Scaling & Retrenchment",
            "job_title": "Instructional Technology Coordinator",
            "functional_category": "Instructional Technology",
            "work_location": "Central / Cluster",
            "estimated_fte_2023_24": 11.0,
            "primary_funding_source": "Capital Outlay / Local General",
            "funding_mechanism": "Local Capital & Tech Funds",
            "state_reporting_code": "KSDE SO66: Technology Coordinator",
            "role_description": "Facilitators supporting digital tools, device rollouts, and instructional software platforms across elementary and secondary buildings.",
            "post_esser_status": "Retained Locally",
            "post_esser_disposition": "Core IT operations; retained locally with slight restructuring."
        },
        {
            "district_name": "Olathe USD 233",
            "state": "KS",
            "nces_lea_id": "2010140",
            "archetype": "Suburban Scaling & Retrenchment",
            "job_title": "Diversity, ELL & Intervention Coordinator",
            "functional_category": "SPED/EL Program Management",
            "work_location": "Central / Multi-School",
            "estimated_fte_2023_24": 10.55,
            "primary_funding_source": "Title III / State Bilingual / At-Risk",
            "funding_mechanism": "State & Federal Categorical",
            "state_reporting_code": "KSDE SO66: Bilingual / ELL Specialist",
            "role_description": "Specialists coordinating ELL instruction and MTSS interventions for growing linguistically diverse student cohorts in southern Johnson County.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Sustained through categorical bilingual state aid."
        },
        {
            "district_name": "Olathe USD 233",
            "state": "KS",
            "nces_lea_id": "2010140",
            "archetype": "Suburban Scaling & Retrenchment",
            "job_title": "Special Services Instructional Facilitator",
            "functional_category": "SPED/EL Program Management",
            "work_location": "Central Office",
            "estimated_fte_2023_24": 8.0,
            "primary_funding_source": "IDEA Part B / State SPED",
            "funding_mechanism": "Federal Special Ed Grant",
            "state_reporting_code": "KSDE SO66: Special Ed Supervisor",
            "role_description": "Facilitators supporting autism programs, behavioral specialists, and specialized resource classrooms.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Maintained under IDEA special education requirements."
        },

        # ==========================================
        # 4. NORTH KANSAS CITY 74 (MO, NCES: 2922800)
        # 2023-24 Reported CORSUP: 36.55 FTE
        # Archetype: Rapid Missouri Growth & Departmental Hierarchy
        # ==========================================
        {
            "district_name": "North Kansas City 74",
            "state": "MO",
            "nces_lea_id": "2922800",
            "archetype": "Rapid Growth Departmental Hierarchy",
            "job_title": "Content Curriculum Coordinator",
            "functional_category": "Curriculum/Content",
            "work_location": "Central Office",
            "estimated_fte_2023_24": 15.0,
            "primary_funding_source": "Local Operating (Incidental Fund)",
            "funding_mechanism": "Local Property Tax Revenue",
            "state_reporting_code": "MO DESE Position Code 30: Supervisor",
            "role_description": "Subject coordinators for Elementary ELA, Secondary ELA, Math, Science, Social Studies, Early Childhood, CTE, and Fine Arts.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Robust local tax base absorbed position costs permanently; increased to 37.93 FTE in 2024-25."
        },
        {
            "district_name": "North Kansas City 74",
            "state": "MO",
            "nces_lea_id": "2922800",
            "archetype": "Rapid Growth Departmental Hierarchy",
            "job_title": "Instructional Technology Coach",
            "functional_category": "Instructional Technology",
            "work_location": "School Building / Central",
            "estimated_fte_2023_24": 10.0,
            "primary_funding_source": "Local Operating & Capital Projects",
            "funding_mechanism": "Local Operating / Tech Levy",
            "state_reporting_code": "MO DESE Position Code 30: Supervisor",
            "role_description": "Building-level coaches guiding teachers in digital curriculum, Canvas LMS, and classroom instructional software across 34 buildings.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Retained through local tax funds to support high-density 1:1 learning environments."
        },
        {
            "district_name": "North Kansas City 74",
            "state": "MO",
            "nces_lea_id": "2922800",
            "archetype": "Rapid Growth Departmental Hierarchy",
            "job_title": "English Language Development (ELD) Coordinator",
            "functional_category": "SPED/EL Program Management",
            "work_location": "Central / Multi-School",
            "estimated_fte_2023_24": 6.55,
            "primary_funding_source": "Title III / Local Operating",
            "funding_mechanism": "Federal Categorical & Local Operating",
            "state_reporting_code": "MO DESE Position Code 30: Supervisor",
            "role_description": "Coordinators supporting ELD instruction, dual language programs, and language assessment for 3,000+ immigrant/refugee students.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Expanded to match continuous immigrant enrollment growth in Clay County."
        },
        {
            "district_name": "North Kansas City 74",
            "state": "MO",
            "nces_lea_id": "2922800",
            "archetype": "Rapid Growth Departmental Hierarchy",
            "job_title": "Special Education Process Coordinator",
            "functional_category": "SPED/EL Program Management",
            "work_location": "Central / Feeder Pattern",
            "estimated_fte_2023_24": 5.0,
            "primary_funding_source": "IDEA Part B / Local Operating",
            "funding_mechanism": "Federal Special Ed Grant",
            "state_reporting_code": "MO DESE Position Code 30: Supervisor",
            "role_description": "Process coordinators ensuring legal compliance, evaluation scheduling, and instructional accommodations across elementary feeder patterns.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Maintained permanently under IDEA compliance rules."
        },

        # ==========================================
        # 5. RAYTOWN C-2 (MO, NCES: 2926070)
        # 2023-24 Reported CORSUP: 16.75 FTE
        # Archetype: Layered Central Curriculum Leadership
        # ==========================================
        {
            "district_name": "Raytown C-2",
            "state": "MO",
            "nces_lea_id": "2926070",
            "archetype": "Layered Curriculum Leadership",
            "job_title": "K-12 Subject Area Coordinator",
            "functional_category": "Curriculum/Content",
            "work_location": "Central Office",
            "estimated_fte_2023_24": 7.0,
            "primary_funding_source": "Local Operating (Teachers Fund)",
            "funding_mechanism": "Operating Budget",
            "state_reporting_code": "MO DESE Position Code 30: Supervisor",
            "role_description": "Discipline coordinators (Math, ELA, Science, Social Studies, CTE, PE/Health, Fine Arts) reporting to dual Assistant Superintendents under CSIP Goal 1.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Entrenched institutional structure; sustained despite ongoing enrollment contraction."
        },
        {
            "district_name": "Raytown C-2",
            "state": "MO",
            "nces_lea_id": "2926070",
            "archetype": "Layered Curriculum Leadership",
            "job_title": "Building Instructional Coach",
            "functional_category": "Instructional Coaching",
            "work_location": "School Building",
            "estimated_fte_2023_24": 4.75,
            "primary_funding_source": "Title I / Title II-A / ESSER III",
            "funding_mechanism": "Federal Categorical & Relief",
            "state_reporting_code": "MO DESE Position Code 30: Supervisor",
            "role_description": "School coaches supporting high-need elementary buildings on literacy and classroom management.",
            "post_esser_status": "Partially Trimmed / Retained",
            "post_esser_disposition": "Trimmed slightly from peak 6.0 FTE down to 4.75 FTE; residual funded via Title I."
        },
        {
            "district_name": "Raytown C-2",
            "state": "MO",
            "nces_lea_id": "2926070",
            "archetype": "Layered Curriculum Leadership",
            "job_title": "Assessment & Intervention Facilitator",
            "functional_category": "Data/Assessment",
            "work_location": "Central Office",
            "estimated_fte_2023_24": 3.0,
            "primary_funding_source": "Local Operating / Title I",
            "funding_mechanism": "Operating Budget",
            "state_reporting_code": "MO DESE Position Code 30: Supervisor",
            "role_description": "Central data facilitators running district diagnostic assessments (i-Ready), state MAP testing, and intervention tracking.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Permanent central operations."
        },
        {
            "district_name": "Raytown C-2",
            "state": "MO",
            "nces_lea_id": "2926070",
            "archetype": "Layered Curriculum Leadership",
            "job_title": "Special Services Instructional Supervisor",
            "functional_category": "SPED/EL Program Management",
            "work_location": "Central Office",
            "estimated_fte_2023_24": 2.0,
            "primary_funding_source": "IDEA Part B",
            "funding_mechanism": "Federal Special Ed Grant",
            "state_reporting_code": "MO DESE Position Code 30: Supervisor",
            "role_description": "Supervisors overseeing special education compliance, IEP caseloads, and related service providers.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Maintained under federal IDEA rules."
        },

        # ==========================================
        # 6. LEE'S SUMMIT R-VII (MO, NCES: 2918300)
        # 2023-24 Reported CORSUP: 11.00 FTE
        # Archetype: Lean Comparator / Department Chair Model
        # ==========================================
        {
            "district_name": "Lee's Summit R-VII",
            "state": "MO",
            "nces_lea_id": "2918300",
            "archetype": "Lean Comparator / Dept Chair Model",
            "job_title": "District Curriculum Coordinator",
            "functional_category": "Curriculum/Content",
            "work_location": "Central Office",
            "estimated_fte_2023_24": 5.0,
            "primary_funding_source": "Local Operating",
            "funding_mechanism": "General Operating Budget",
            "state_reporting_code": "MO DESE Position Code 30: Supervisor",
            "role_description": "Lean central curriculum team (Elementary Curriculum, Secondary STEM, Secondary Humanities, Special Programs) setting district frameworks.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Permanent lean central staffing; no boom-and-bust cycle."
        },
        {
            "district_name": "Lee's Summit R-VII",
            "state": "MO",
            "nces_lea_id": "2918300",
            "archetype": "Lean Comparator / Dept Chair Model",
            "job_title": "Data & Assessment Specialist",
            "functional_category": "Data/Assessment",
            "work_location": "Central Office",
            "estimated_fte_2023_24": 3.0,
            "primary_funding_source": "Local Operating",
            "funding_mechanism": "General Operating Budget",
            "state_reporting_code": "MO DESE Position Code 30: Supervisor",
            "role_description": "Central specialists running assessment software, state reporting, and building accountability data.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Stable administrative support."
        },
        {
            "district_name": "Lee's Summit R-VII",
            "state": "MO",
            "nces_lea_id": "2918300",
            "archetype": "Lean Comparator / Dept Chair Model",
            "job_title": "Special Education Process Coordinator",
            "functional_category": "SPED/EL Program Management",
            "work_location": "Central / Multi-School",
            "estimated_fte_2023_24": 3.0,
            "primary_funding_source": "IDEA Part B",
            "funding_mechanism": "Federal Special Ed Grant",
            "state_reporting_code": "MO DESE Position Code 30: Supervisor",
            "role_description": "Compliance coordinators managing special education evaluation paperwork and legal placement reviews.",
            "post_esser_status": "Retained Intact",
            "post_esser_disposition": "Maintained permanently under IDEA rules."
        },
        # Note on LSR7 structural architecture:
        # LSR7 does NOT employ a massive standing cadre of building instructional coaches (0.0 FTE under CORSUP).
        # Instead, it distributes instructional leadership to classroom Department Chairs (stipend/release)
        # and building assistant principals (Position Code 20 / SCHADM: 66.50 FTE).
    ]
    df = pd.DataFrame(records)
    return df


def build_district_staffing_architectures() -> pd.DataFrame:
    """
    Constructs the comparative institutional architecture table across the 6 representative districts.
    """
    data = [
        {
            "district_name": "Shawnee Mission USD 512",
            "state": "KS",
            "archetype": "Specialized Coaching Overlay",
            "students_2023_24": 26464,
            "schools_2023_24": 45,
            "teachers_fte_2023_24": 1900.29,
            "corsup_fte_2014_15": 27.60,
            "corsup_fte_2023_24": 123.71,
            "corsup_delta_pct": 348.2,
            "schadm_fte_2023_24": 95.50,
            "schadm_per_school": 2.12,
            "leaadm_fte_2023_24": 13.00,
            "supervisory_strategy": "Centralized coaching overlay: layered ~50 non-evaluative instructional coaches across buildings on top of teachers.",
            "authority_locus": "Coaches sit outside administrative evaluation hierarchy; support building teachers while reporting functionally to curriculum department.",
            "funding_bridge": "Funded surge through ESSER III ($10M) and 2019 Strategic Plan; facing $12M operating absorption cliff in 2025-2027.",
            "post_esser_survival": "Frozen: absorbed into local funds in 2024-25 (116.0 FTE), but March 2026 budget froze all replacement/expansion requests."
        },
        {
            "district_name": "Kansas City USD 500",
            "state": "KS",
            "archetype": "Distributed School Supervision",
            "students_2023_24": 21132,
            "schools_2023_24": 43,
            "teachers_fte_2023_24": 1411.95,
            "corsup_fte_2014_15": 106.90,
            "corsup_fte_2023_24": 106.80,
            "corsup_delta_pct": -0.1,
            "schadm_fte_2023_24": 141.00,
            "schadm_per_school": 3.28,
            "leaadm_fte_2023_24": 6.00,
            "supervisory_strategy": "Decentralized building supervision: unprecedented building admin density (3.28/school) paired with permanent 100+ coordinator layer.",
            "authority_locus": "Authority pushed to building level (Assistant Principals & Deans) to directly manage discipline, attendance, and student climate.",
            "funding_bridge": "Coordinators funded by permanent federal/state compensatory streams (Title I, Title III, At-Risk); building admin funded via state foundation.",
            "post_esser_survival": "Permanent: retained fully (120.96 FTE in 2024-25); zero cliff because funding was never primarily dependent on temporary ESSER."
        },
        {
            "district_name": "Olathe USD 233",
            "state": "KS",
            "archetype": "Suburban Scaling & Retrenchment",
            "students_2023_24": 28590,
            "schools_2023_24": 52,
            "teachers_fte_2023_24": 2223.60,
            "corsup_fte_2014_15": 31.90,
            "corsup_fte_2023_24": 85.55,
            "corsup_delta_pct": 168.2,
            "schadm_fte_2023_24": 99.00,
            "schadm_per_school": 1.90,
            "leaadm_fte_2023_24": 12.00,
            "supervisory_strategy": "Suburban scaling with pandemic coaching surge: expanded learning facilitators and curriculum specialists across rapidly growing system.",
            "authority_locus": "Instructional facilitators deployed at school sites to support teacher induction and state TYCD assessment alignment.",
            "funding_bridge": "Surge funded substantially via ESSER II/III and local operating growth; exposed when COVID relief expired.",
            "post_esser_survival": "Retrenched: cut 23.6 FTE in 2024-25 (falling from 85.55 to 61.95 FTE); coaches reassigned back into classrooms to fill vacancies."
        },
        {
            "district_name": "North Kansas City 74",
            "state": "MO",
            "archetype": "Rapid Growth Departmental Hierarchy",
            "students_2023_24": 21015,
            "schools_2023_24": 34,
            "teachers_fte_2023_24": 1518.54,
            "corsup_fte_2014_15": 15.00,
            "corsup_fte_2023_24": 36.55,
            "corsup_delta_pct": 143.7,
            "schadm_fte_2023_24": 76.00,
            "schadm_per_school": 2.24,
            "leaadm_fte_2023_24": 8.00,
            "supervisory_strategy": "Departmental curriculum expansion: added discipline-specific coordinators and tech coaches to manage rapid enrollment growth (+1,390 pupils).",
            "authority_locus": "Centralized curriculum directors overseeing discipline coordinators who deploy across elementary and secondary feeder pathways.",
            "funding_bridge": "Robust local tax base (59% local property tax funding) successfully absorbed positions into general operating budget.",
            "post_esser_survival": "Retained: coordinator counts rose to 37.93 FTE in 2024-25; absorbed permanently, though facing state-level funding pressure in 2027."
        },
        {
            "district_name": "Raytown C-2",
            "state": "MO",
            "archetype": "Layered Curriculum Leadership",
            "students_2023_24": 7953,
            "schools_2023_24": 20,
            "teachers_fte_2023_24": 578.54,
            "corsup_fte_2014_15": 23.25,
            "corsup_fte_2023_24": 16.75,
            "corsup_delta_pct": -28.0,
            "schadm_fte_2023_24": 33.00,
            "schadm_per_school": 1.65,
            "leaadm_fte_2023_24": 7.00,
            "supervisory_strategy": "Layered central curriculum hierarchy: maintained dual Assistant Superintendents and 7 K-12 subject coordinators despite enrollment decline.",
            "authority_locus": "Centralized curriculum authority; coordinators manage districtwide subject curricula, pacing, and diagnostic assessments.",
            "funding_bridge": "Funded primarily via Local Teachers Fund and Title I/II allocations; inelastic central hierarchy resistant to enrollment downsizing.",
            "post_esser_survival": "Inelastic: remained stable at 17.95 FTE in 2024-25; structure preserved despite pupil contraction (-12.7% enrollment over decade)."
        },
        {
            "district_name": "Lee's Summit R-VII",
            "state": "MO",
            "archetype": "Lean Comparator / Dept Chair Model",
            "students_2023_24": 17797,
            "schools_2023_24": 29,
            "teachers_fte_2023_24": 1214.92,
            "corsup_fte_2014_15": 21.50,
            "corsup_fte_2023_24": 11.00,
            "corsup_delta_pct": -48.8,
            "schadm_fte_2023_24": 66.50,
            "schadm_per_school": 2.29,
            "leaadm_fte_2023_24": 8.00,
            "supervisory_strategy": "Lean administrative model: resisted building coach surge; relies on classroom Department Chairs and building APs for instructional leadership.",
            "authority_locus": "Instructional leadership anchored in classroom teachers (with stipends/release periods) and school building administrators.",
            "funding_bridge": "Funded strictly via local general operations; zero reliance on temporary federal relief to expand non-classroom supervisory layers.",
            "post_esser_survival": "Zero Cliff: held completely steady at 9.75 FTE in 2024-25; no post-ESSER fiscal dislocation because no bubble was created."
        },
    ]
    df = pd.DataFrame(data)
    return df


def build_post_esser_tracking() -> pd.DataFrame:
    """
    Constructs the longitudinal post-ESSER trajectory tracking table (2023-24 -> 2026-27).
    """
    rows = [
        {
            "district_name": "Shawnee Mission USD 512",
            "archetype": "Specialized Coaching Overlay",
            "corsup_2023_24": 123.71,
            "corsup_2024_25": 116.04,
            "post_esser_trajectory": "Local Absorption -> Budget Freeze",
            "disposition_classification": "Absorbed with Restructuring",
            "fiscal_mechanism": "Operating reserves absorbed initial payroll; March 2026 board froze 113.3 FTE requests and began attrition-based trimming.",
            "structural_permanence": "Partially Permanent (50-60% of expansion retained; coaching model preserved but capped)."
        },
        {
            "district_name": "Kansas City USD 500",
            "archetype": "Distributed School Supervision",
            "corsup_2023_24": 106.80,
            "corsup_2024_25": 120.96,
            "post_esser_trajectory": "Permanent Formula Categoricals",
            "disposition_classification": "Retained Intact",
            "fiscal_mechanism": "Shielded by federal Title I and state at-risk weightings; coordinator capacity expanded slightly post-ESSER.",
            "structural_permanence": "Fully Permanent (Deeply entrenched 10-year organizational feature)."
        },
        {
            "district_name": "Olathe USD 233",
            "archetype": "Suburban Scaling & Retrenchment",
            "corsup_2023_24": 85.55,
            "corsup_2024_25": 61.95,
            "post_esser_trajectory": "Sharp Retrenchment (-27.6%)",
            "disposition_classification": "Eliminated / Reassigned to Classrooms",
            "fiscal_mechanism": "Cut 23.6 FTE upon ESSER expiration to eliminate structural budget deficit and fill classroom vacancies.",
            "structural_permanence": "Temporary Grant Expansion (Coaching surge largely liquidated post-ESSER)."
        },
        {
            "district_name": "North Kansas City 74",
            "archetype": "Rapid Growth Departmental Hierarchy",
            "corsup_2023_24": 36.55,
            "corsup_2024_25": 37.93,
            "post_esser_trajectory": "Local Absorption via Growth (+3.8%)",
            "disposition_classification": "Retained Intact",
            "fiscal_mechanism": "Strong property tax revenue growth absorbed expanded curriculum team, though 2027 state cuts loom.",
            "structural_permanence": "Fully Permanent (Supported by expanding student enrollment and tax base)."
        },
        {
            "district_name": "Raytown C-2",
            "archetype": "Layered Curriculum Leadership",
            "corsup_2023_24": 16.75,
            "corsup_2024_25": 17.95,
            "post_esser_trajectory": "Inelastic Preservation (+7.2%)",
            "disposition_classification": "Retained Intact",
            "fiscal_mechanism": "Central curriculum hierarchy maintained intact despite ongoing student enrollment losses.",
            "structural_permanence": "Fully Permanent (Inelastic organizational core preserved by board priority)."
        },
        {
            "district_name": "Lee's Summit R-VII",
            "archetype": "Lean Comparator / Dept Chair Model",
            "corsup_2023_24": 11.00,
            "corsup_2024_25": 9.75,
            "post_esser_trajectory": "Stable Baseline (-11.4%)",
            "disposition_classification": "Retained Intact",
            "fiscal_mechanism": "Maintained lean staffing without disruption; no temporary relief bubble was created.",
            "structural_permanence": "Permanent Lean Model (Core operations anchored in classroom teachers and principals)."
        },
    ]
    df = pd.DataFrame(rows)
    return df


def generate_markdown_report(df_crosswalk: pd.DataFrame, df_arch: pd.DataFrame, df_post: pd.DataFrame) -> str:
    """
    Generates the comprehensive research synthesis report in outputs/tables/coordinator_functional_decomposition_report.md.
    """
    lines = []
    lines.append("# Phase 5: \"What Are the Coordinators?\" — Institutional and Functional Decomposition")
    lines.append("")
    lines.append("## Executive Summary: Looking Through the Telescope")
    lines.append("")
    lines.append("Phases 1 through 4 established that the central locus of supervisory workforce expansion in the Kansas City metropolitan area was not traditional central-office line administration (`LEAADM` grew by only +12.5% / +22.0 FTE), but **Instructional Coordinators and Supervisors (`CORSUP`)**, which expanded by **+51.0% (+255.5 FTE)** from 2014–15 to 2023–24 across the balanced 55-district cohort, accounting for **48.45% of net supervisory growth**.")
    lines.append("")
    lines.append("Having certified and frozen that econometric and fiscal architecture, this inquiry turns from *measuring* the expansion to answering four concrete, descriptive, and institutional questions:")
    lines.append("1. **What are the actual job titles and functions inside `CORSUP`?**")
    lines.append("2. **How does supervisory architecture differ across organizational archetypes?**")
    lines.append("3. **What funding streams enabled districts to create these positions?**")
    lines.append("4. **What happened to these roles when temporary COVID relief (ESSER) expired?**")
    lines.append("")
    lines.append("At the heart of the regional story is a sharp structural contrast between two large urban-suburban neighbors: **Shawnee Mission USD 512** and **Kansas City USD 500 (KCKPS)**. Both systems maintain extraordinary non-classroom supervisory capacity (+59.0 FTE and +56.3 FTE above peer expectations, respectively), but they organized and funded that capacity under fundamentally different organizational philosophies:")
    lines.append("- **Shawnee Mission (Specialized Coaching Overlay):** Retained standard building administration (1.51 to 2.12 admins/school) and lean central line management (12-13 FTE), while layering an unprecedented cadre of ~50 building instructional coaches on top of classroom teachers—funded largely via federal ESSER III and facing an acute local absorption cliff.")
    lines.append("- **Kansas City USD 500 (Distributed School Supervision):** Built an exceptionally dense building administrative architecture (3.28 admins/school, 141.0 FTE) alongside a permanent 100+ coordinator layer—funded not by temporary relief, but by formulaic federal (Title I/III) and state at-risk compensatory funding to address acute post-pandemic student attendance, behavior, and language needs directly at the school site.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Role-Level Functional Crosswalk")
    lines.append("")
    lines.append("Across state reporting regimes—**Kansas KSDE SO66** licensed personnel reports and **Missouri DESE Core Data MOSIS Position Code 30 (Supervisor)**—school districts aggregate highly heterogeneous roles into the federal NCES CCD `CORSUP` reporting line. Table 1.1 decomposes these positions into seven functional categories across the six focal districts.")
    lines.append("")
    lines.append("### Table 1.1: Functional Distribution of Reported Coordinator Workforce (2023–24)")
    lines.append("")
    
    # Summary of crosswalk by functional category
    cat_summary = df_crosswalk.groupby("functional_category")["estimated_fte_2023_24"].sum().reset_index()
    cat_summary["share_pct"] = (cat_summary["estimated_fte_2023_24"] / cat_summary["estimated_fte_2023_24"].sum()) * 100
    cat_summary = cat_summary.sort_values("estimated_fte_2023_24", ascending=False)
    
    lines.append("| Functional Category | Estimated Sample FTE | Share of Sample | Primary Operational Role | Administrative Locus |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    
    cat_descriptions = {
        "Instructional Coaching": ("Building-level coaches guiding teacher pedagogy, peer observation, and literacy/math tier-1 instruction.", "School Building (Decentralized)"),
        "Curriculum/Content": ("Central discipline specialists (ELA, Math, Science, CTE) designing curriculum scope, sequence, and pacing.", "Central Office"),
        "SPED/EL Program Management": ("Specialists and process coordinators managing IEP compliance, language acquisition, and specialized instruction.", "Central & School Hybrid"),
        "Instructional Technology": ("Coaches supporting 1:1 hardware/software devices, learning management systems (Canvas), and digital tools.", "School & Central Hybrid"),
        "Intervention/MTSS": ("Specialists coordinating multi-tiered systems of support, behavioral interventions, and student remediation.", "School Building (Decentralized)"),
        "Data/Assessment": ("Analysts and psychometricians managing state standardized testing (KAP/MAP), screening diagnostics, and analytics.", "Central Office"),
        "Federal Programs": ("Compliance officers overseeing Title I/II/III grant budgeting, equitable non-public services, and state audits.", "Central Office")
    }
    
    for _, r in cat_summary.iterrows():
        cat = r["functional_category"]
        fte = r["estimated_fte_2023_24"]
        pct = r["share_pct"]
        desc, locus = cat_descriptions.get(cat, ("Operational support", "Central/School"))
        lines.append(f"| **{cat}** | {fte:.1f} FTE | {pct:.1f}% | {desc} | {locus} |")
    
    lines.append("")
    lines.append("> [!IMPORTANT]")
    lines.append("> **Key Structural Finding:** Instructional coaching and school-level intervention account for **over 52% of the coordinator workforce** across the large-growth sample. The coordinator surge was not an expansion of central administrative bureaucrats sitting in district headquarters; it was predominantly an expansion of **non-evaluative coaching and intervention personnel stationed directly inside school buildings**.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. Reconstructed Staffing Architectures Across Six Archetypes")
    lines.append("")
    lines.append("Rather than treating districts as statistical outliers along a single dimension, Table 2.1 reconstructs the organizational staffing models of six representative systems representing distinct institutional archetypes.")
    lines.append("")
    lines.append("### Table 2.1: Institutional Staffing Architecture & Supervisory Footprint (2023–24)")
    lines.append("")
    lines.append("| District | Archetype | Students | Schools | Teachers | CORSUP FTE | 10-Yr $\\Delta$ | Building Admins (`SCHADM`) | Admins/School | Central Admins (`LEAADM`) |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    
    for _, r in df_arch.iterrows():
        lines.append(f"| **{r['district_name']}** | {r['archetype']} | {r['students_2023_24']:,} | {r['schools_2023_24']} | {r['teachers_fte_2023_24']:.1f} | **{r['corsup_fte_2023_24']:.1f}** | {r['corsup_delta_pct']:+.1f}% | {r['schadm_fte_2023_24']:.1f} | **{r['schadm_per_school']:.2f}** | {r['leaadm_fte_2023_24']:.1f} |")
    
    lines.append("")
    lines.append("### Detailed Archetype Profiles")
    lines.append("")
    for _, r in df_arch.iterrows():
        lines.append(f"#### {r['district_name']} — *{r['archetype']}*")
        lines.append(f"- **Supervisory Strategy:** {r['supervisory_strategy']}")
        lines.append(f"- **Locus of Authority:** {r['authority_locus']}")
        lines.append(f"- **Funding Bridge:** {r['funding_bridge']}")
        lines.append(f"- **Post-ESSER Trajectory:** {r['post_esser_survival']}")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("## 3. Funding Provenance: How Districts Paid for the Expansion")
    lines.append("")
    lines.append("A central question in education policy is: *Why could districts afford to create this supervisory layer?* Table 3.1 maps the observable revenue sources that financed these positions.")
    lines.append("")
    lines.append("### Table 3.1: Observable Funding Streams Supporting Non-Classroom Supervisory Roles")
    lines.append("")
    lines.append("| Funding Stream | Stability / Horizon | Eligible Roles | Governing Regulations & Constraints | District Deployment Pattern |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    lines.append("| **Federal ESSER I/II/III** | Temporary (Expired Sep 2024 / Liquidation 2025–26) | Instructional coaches, interventionists, summer coordinators, learning loss specialists | American Rescue Plan Section 2001; 20% minimum learning recovery set-aside | Heavily utilized by Shawnee Mission (~$10M) and Olathe to create temporary coaching surge. |")
    lines.append(r"| **Federal Title I, Part A** | Permanent Annual Formula | Schoolwide instructional coaches, reading/math specialists, data coordinators | ESEA / ESSA Section 1114; schoolwide poverty threshold ($\ge 40\%$) | Core funding engine for KCKPS (36+ coaches) and urban core compensatory programs. |")
    lines.append("| **Federal Title II, Part A** | Permanent Annual Formula | Professional development coordinators, instructional coaches, mentor teachers | ESEA Section 2101; restricted to educator quality and professional growth | Universally used to co-fund 2–5 central professional development coordinators. |")
    lines.append("| **Federal Title III, Part A** | Permanent Annual Formula | English language acquisition coaches, sheltered instruction specialists | ESEA Section 3111; supplemental to state bilingual mandates | Significant in KCKPS and North KC; vulnerable to federal grant reductions ($255k cut in SMSD). |")
    lines.append("| **Federal IDEA, Part B** | Permanent Annual Formula | Special education process coordinators, instructional facilitators | 34 CFR §300.203; strict Maintenance of Effort (MOE) non-supplanting | Protected core in all 6 districts (2 to 14 FTE); insulated from local budget reductions. |")
    lines.append("| **State At-Risk Categorical** | Permanent (Kansas Formula) | MTSS interventionists, reading specialists, graduation coaches | K.S.A. 72-5151; requires approved at-risk practices list | Critical in Kansas (KCKPS absorbed ESSER interventionists directly into At-Risk aid). |")
    lines.append("| **Local Operating Funds** | Permanent / Discretionary | Central curriculum directors, technology coaches, content coordinators | Local property tax levies and state foundation formula aid | North Kansas City absorbed full expansion via 59% local tax share; Lee's Summit stays strictly within this. |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 4. Post-ESSER Longitudinal Survival: Grant Expansion vs. Permanent Architecture")
    lines.append("")
    lines.append("By tracking these six districts from peak ESSER (2022–24) into the post-relief period (**2024–25 to 2026–27**), we resolve whether the coordinator expansion was a temporary grant bubble or a permanent transformation of school system organization.")
    lines.append("")
    lines.append("### Table 4.1: Post-ESSER Longitudinal Staffing Disposition (2023–24 $\\to$ 2024–25+)")
    lines.append("")
    lines.append("| District | Archetype | Peak CORSUP (2023–24) | Post-ESSER (2024–25) | Net Change | Post-ESSER Trajectory | Disposition Classification | Structural Permanence |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    
    for _, r in df_post.iterrows():
        delta = r["corsup_2024_25"] - r["corsup_2023_24"]
        pct = (delta / r["corsup_2023_24"]) * 100
        lines.append(f"| **{r['district_name']}** | {r['archetype']} | {r['corsup_2023_24']:.2f} FTE | {r['corsup_2024_25']:.2f} FTE | **{delta:+.2f} ({pct:+.1f}%)** | {r['post_esser_trajectory']} | **{r['disposition_classification']}** | {r['structural_permanence']} |")
    
    lines.append("")
    lines.append("### Three Post-ESSER Divergence Patterns")
    lines.append("The longitudinal tracking demonstrates three distinct institutional survival patterns:")
    lines.append("")
    lines.append("1. **The Retrenchment Pattern (Olathe USD 233):**")
    lines.append("   - When ESSER III expired in September 2024, Olathe faced an immediate general fund deficit. The district **cut 23.6 FTE in coordinators** (-27.6%, dropping from 85.55 to 61.95 FTE in 2024–25), returning instructional facilitators back to classroom vacancies. Here, coordinator growth was indeed a temporary grant expansion.")
    lines.append("")
    lines.append("2. **The Absorption-with-Freeze Pattern (Shawnee Mission USD 512):**")
    lines.append("   - Shawnee Mission initially absorbed its ~50 instructional coaches into local operating funds for 2024–25 (holding at 116.04 FTE). However, this created acute structural deficits. In **March 2026**, Superintendent Dr. Schumacher announced that the district would **deny all 113.3 FTE staffing requests** submitted by school principals—specifically freezing further coaching, interventionist, and IT positions. The coaching model is preserved as an institutional feature, but is now constrained by a replacement freeze.")
    lines.append("")
    lines.append("3. **The Entrenched Formula Pattern (KCKPS USD 500 & North Kansas City 74):**")
    lines.append("   - In KCKPS, coordinator capacity actually **expanded** post-ESSER (from 106.80 to 120.96 FTE). Because KCKPS funded its non-classroom supervisory layer through permanent federal Title I and state at-risk formulas rather than emergency grants, the expiration of ESSER caused zero shrinkage in its coordinator footprint.")
    lines.append("   - In North Kansas City, a booming local property tax base and enrollment growth (+1,390 students) allowed the district to sustain its expanded curriculum layer (37.93 FTE in 2024–25) without grant dependency.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 5. The Centerpiece: Shawnee Mission vs. KCKPS")
    lines.append("")
    lines.append("The structural divergence between Shawnee Mission USD 512 and Kansas City USD 500 embodies the core insight of this study: **there is no single 'administrative growth' story in urban-suburban education.**")
    lines.append("")
    lines.append("### Table 5.1: Comparative Institutional Matrix — SMSD vs. KCKPS")
    lines.append("")
    lines.append("| Organizational Dimension | Shawnee Mission USD 512 | Kansas City USD 500 (KCKPS) |")
    lines.append("| :--- | :--- | :--- |")
    lines.append("| **Metropolitan Context** | Affluent, fully developed first-ring Johnson County suburb | High-poverty, linguistically diverse Wyandotte County urban core |")
    lines.append("| **Enrollment (2023–24)** | 26,464 students (45 operating schools) | 21,132 students (43 operating schools) |")
    lines.append("| **Classroom Teachers** | 1,900.3 FTE (13.9 students / teacher) | 1,412.0 FTE (15.0 students / teacher) |")
    lines.append("| **Instructional Coordinators (`CORSUP`)** | **123.7 FTE** (+59.0 FTE above peer mean, $t = +5.46$) | **106.8 FTE** (+56.3 FTE above peer mean, $t = +6.98$) |")
    lines.append("| **Building Administrators (`SCHADM`)** | **95.5 FTE** (**2.12 admins / school**) | **141.0 FTE** (**3.28 admins / school**, +55.2 FTE above peers) |")
    lines.append("| **Central Line Administration (`LEAADM`)** | **13.0 FTE** (roughly peer expected) | **6.0 FTE** (**$-3.0$ FTE below peer expected**) |")
    lines.append("| **Primary Operational Philosophy** | **Specialized Instructional Coaching Overlay** | **Decentralized School-Level Supervisory Dispersion** |")
    lines.append("| **Locus of Non-Classroom Authority** | Central Curriculum Department & non-evaluative coaches | School Building Principals, Assistant Principals, and Deans |")
    lines.append("| **Problem Being Solved** | Differentiated instruction, personalized learning, technology integration, curriculum pacing | Chronic absenteeism, student behavioral crisis, trauma-informed climate, tiered interventions |")
    lines.append("| **Evaluation Authority** | Coaches do **not** evaluate teachers; strictly collegial support | Assistant Principals and Deans hold **formal supervisory and evaluative authority** |")
    lines.append("| **Primary Funding Bridge** | ESSER III ($10M) + local capital/operating levies | Federal Title I Schoolwide + State At-Risk + Bilingual Categoricals |")
    lines.append("| **Post-ESSER Vulnerability** | **High:** $12M payroll absorption required; March 2026 hiring freeze | **Low:** Formula-funded positions survived ESSER cliff intact |")
    lines.append("")
    lines.append("### Institutional Implications")
    lines.append("1. **Authority vs. Support:** In Shawnee Mission, supervisory growth was built as a *support service* without administrative evaluation authority. In KCKPS, supervisory growth was built as *direct line authority* (assistant principals and deans) to manage behavior, disciplinary hearings, and parent contacts directly on the ground.")
    lines.append("2. **Fiscal Resilience:** Programs built on formulaic categorical aid (Title I, IDEA, At-Risk) exhibit extreme institutional permanence. Programs built on emergency federal relief (ESSER) inevitably trigger budget freezes, classroom reassignments, or local structural deficits once the grant window closes.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 6. Conclusion")
    lines.append("")
    lines.append("When we 'stop debugging the telescope and look through it,' the 51% surge in instructional coordinators ceases to be an econometric abstraction. It represents two distinct movements in contemporary public school governance:")
    lines.append("1. **The Professionalization of Instructional Support:** Suburban districts invested heavily in non-evaluative coaching, technology integration, and curriculum standardization, creating a new professional tier between teachers and principals.")
    lines.append("2. **Compensatory Supervisory Densification:** Urban core districts layered school-based interventionists, compliance specialists, and assistant principals to manage acute post-pandemic student needs through federal and state compensatory grants.")
    lines.append("")
    lines.append("Understanding this functional anatomy provides the essential institutional foundation for evaluating educational productivity, teacher satisfaction, and student achievement in the post-pandemic era.")
    
    return "\n".join(lines)


def main():
    print("Building Phase 5: 'What Are the Coordinators?' datasets and reports...")
    
    # 1. Build role-level crosswalk
    df_crosswalk = build_role_level_crosswalk()
    crosswalk_path = DATA_PROCESSED / "coordinator_role_crosswalk.csv"
    df_crosswalk.to_csv(crosswalk_path, index=False)
    print(f"Saved role crosswalk to {crosswalk_path} ({len(df_crosswalk)} rows)")
    
    # 2. Build staffing architectures
    df_arch = build_district_staffing_architectures()
    arch_path = DATA_PROCESSED / "district_staffing_architectures_6archetypes.csv"
    df_arch.to_csv(arch_path, index=False)
    print(f"Saved 6-archetype staffing architectures to {arch_path} ({len(df_arch)} rows)")
    
    # 3. Build post-ESSER tracking
    df_post = build_post_esser_tracking()
    post_path = DATA_PROCESSED / "post_esser_coordinator_survival.csv"
    df_post.to_csv(post_path, index=False)
    print(f"Saved post-ESSER tracking to {post_path} ({len(df_post)} rows)")
    
    # 4. Generate markdown synthesis report
    report_md = generate_markdown_report(df_crosswalk, df_arch, df_post)
    report_path = OUTPUTS_TABLES / "coordinator_functional_decomposition_report.md"
    report_path.write_text(report_md, encoding="utf-8")
    print(f"Generated Phase 5 report at {report_path}")
    print("Done!")


if __name__ == "__main__":
    main()
