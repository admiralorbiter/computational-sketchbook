"""
Canonical Staffing Taxonomy & Intensity Metrics Specification.

Defines mutually exclusive staffing buckets, crosswalk mappings,
and multi-denominator metric calculations for the Kansas City
administrative intensity study.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np
import pandas as pd


class StaffBucket(str, Enum):
    """Mutually exclusive top-level staffing buckets."""
    CORE_MANAGEMENT = "core_management"
    INSTRUCTIONAL_ADMIN_SUPPORT = "instructional_admin_support"
    PROGRAM_COMPLIANCE_ADMIN = "program_compliance_admin"
    BUSINESS_OPERATIONS_ADMIN = "business_operations_admin"
    STUDENT_SUPPORT_SERVICES = "student_support_services"  # Quarantined from admin
    CLASSROOM_INSTRUCTION = "classroom_instruction"
    OPERATIONS_AUXILIARY = "operations_auxiliary"


@dataclass(frozen=True)
class StaffCategoryDefinition:
    bucket: StaffBucket
    code: str
    title: str
    description: str
    is_administrative: bool
    is_instructional: bool
    is_quarantined_student_support: bool


# Canonical taxonomy metadata registry
TAXONOMY_REGISTRY: Dict[str, StaffCategoryDefinition] = {
    "superintendent_deputy": StaffCategoryDefinition(
        bucket=StaffBucket.CORE_MANAGEMENT,
        code="1A",
        title="Executive Central Leadership",
        description="Superintendents, associate/deputy superintendents, cabinet leaders",
        is_administrative=True,
        is_instructional=False,
        is_quarantined_student_support=False,
    ),
    "lea_administrators": StaffCategoryDefinition(
        bucket=StaffBucket.CORE_MANAGEMENT,
        code="1B",
        title="Central Office Administration",
        description="District-wide directors, assistant superintendents, area directors",
        is_administrative=True,
        is_instructional=False,
        is_quarantined_student_support=False,
    ),
    "school_administrators": StaffCategoryDefinition(
        bucket=StaffBucket.CORE_MANAGEMENT,
        code="1C",
        title="School Building Administration",
        description="Building principals, assistant principals, vice principals",
        is_administrative=True,
        is_instructional=False,
        is_quarantined_student_support=False,
    ),
    "instructional_coordinators": StaffCategoryDefinition(
        bucket=StaffBucket.INSTRUCTIONAL_ADMIN_SUPPORT,
        code="2A",
        title="Instructional Coordinators & Coaches",
        description="Curriculum directors, instructional supervisors, coaches, trainers, CAI coordinators",
        is_administrative=True,  # Tracked separately as instructional administration
        is_instructional=True,
        is_quarantined_student_support=False,
    ),
    "program_compliance_admin": StaffCategoryDefinition(
        bucket=StaffBucket.PROGRAM_COMPLIANCE_ADMIN,
        code="3A",
        title="Program & Compliance Directors",
        description="Special education directors, federal programs coordinators, assessment coordinators",
        is_administrative=True,
        is_instructional=False,
        is_quarantined_student_support=False,
    ),
    "business_operations_admin": StaffCategoryDefinition(
        bucket=StaffBucket.BUSINESS_OPERATIONS_ADMIN,
        code="4A",
        title="Business & Operations Managers",
        description="CFOs, business managers, HR directors, IT directors, purchasing directors",
        is_administrative=True,
        is_instructional=False,
        is_quarantined_student_support=False,
    ),
    "student_support_services": StaffCategoryDefinition(
        bucket=StaffBucket.STUDENT_SUPPORT_SERVICES,
        code="5A",
        title="Student Support Services (Quarantined)",
        description="Guidance counselors, school psychologists, social workers, nurses, speech therapists",
        is_administrative=False,  # STRICTLY QUARANTINED
        is_instructional=False,
        is_quarantined_student_support=True,
    ),
    "classroom_teachers": StaffCategoryDefinition(
        bucket=StaffBucket.CLASSROOM_INSTRUCTION,
        code="6A",
        title="Classroom Teachers (K-12)",
        description="Pre-K, Kindergarten, Elementary, Secondary, and Ungraded classroom teachers",
        is_administrative=False,
        is_instructional=True,
        is_quarantined_student_support=False,
    ),
    "paraprofessionals": StaffCategoryDefinition(
        bucket=StaffBucket.CLASSROOM_INSTRUCTION,
        code="6B",
        title="Paraprofessionals & Instructional Aides",
        description="Classroom aides, special education paraprofessionals, title I aides",
        is_administrative=False,
        is_instructional=True,
        is_quarantined_student_support=False,
    ),
    "operations_auxiliary": StaffCategoryDefinition(
        bucket=StaffBucket.OPERATIONS_AUXILIARY,
        code="7A",
        title="Operations & Auxiliary Support Staff",
        description="Secretarial/clerical, custodial, maintenance, transportation, food service",
        is_administrative=False,
        is_instructional=False,
        is_quarantined_student_support=False,
    ),
}


def sanitize_negative_codes(val):
    """Convert NCES exception codes (-1, -2, -9) to np.nan while preserving zero."""
    if pd.isna(val):
        return np.nan
    try:
        fval = float(val)
        if fval < 0:
            return np.nan
        return fval
    except (ValueError, TypeError):
        return np.nan


def compute_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute canonical aggregates and multi-denominator intensity ratios
    for a district-staff-year panel dataframe.
    """
    df = df.copy()

    # Core Management Composite = School Administrators + LEA Administrators
    df["core_admin_fte"] = df["school_administrators_fte"].fillna(0) + df["lea_administrators_fte"].fillna(0)
    # Mask to NaN if both components are NaN
    both_na = df["school_administrators_fte"].isna() & df["lea_administrators_fte"].isna()
    df.loc[both_na, "core_admin_fte"] = np.nan

    # Instructional/Program Administration = Instructional Coordinators
    df["instructional_program_admin_fte"] = df["instructional_coordinators_fte"]

    # Total Administration + Coordinators Composite
    df["total_admin_and_coordinators_fte"] = (
        df["core_admin_fte"].fillna(0) + df["instructional_program_admin_fte"].fillna(0)
    )
    both_na_tot = df["core_admin_fte"].isna() & df["instructional_program_admin_fte"].isna()
    df.loc[both_na_tot, "total_admin_and_coordinators_fte"] = np.nan

    # Denominator 1: FTE per 1,000 Students
    valid_enr = df["enrollment_total"] > 0
    df["core_admin_per_1000_students"] = np.where(
        valid_enr, (df["core_admin_fte"] / df["enrollment_total"]) * 1000.0, np.nan
    )
    df["coordinators_per_1000_students"] = np.where(
        valid_enr, (df["instructional_coordinators_fte"] / df["enrollment_total"]) * 1000.0, np.nan
    )
    df["total_admin_coord_per_1000_students"] = np.where(
        valid_enr, (df["total_admin_and_coordinators_fte"] / df["enrollment_total"]) * 1000.0, np.nan
    )
    df["student_support_per_1000_students"] = np.where(
        valid_enr, (df["student_support_staff_fte"] / df["enrollment_total"]) * 1000.0, np.nan
    )
    df["teachers_per_1000_students"] = np.where(
        valid_enr, (df["teachers_k12_fte"] / df["enrollment_total"]) * 1000.0, np.nan
    )

    # Denominator 2: FTE per 100 Classroom Teachers
    valid_tch = df["teachers_k12_fte"] > 0
    df["core_admin_per_100_teachers"] = np.where(
        valid_tch, (df["core_admin_fte"] / df["teachers_k12_fte"]) * 100.0, np.nan
    )
    df["coordinators_per_100_teachers"] = np.where(
        valid_tch, (df["instructional_coordinators_fte"] / df["teachers_k12_fte"]) * 100.0, np.nan
    )
    df["total_admin_coord_per_100_teachers"] = np.where(
        valid_tch, (df["total_admin_and_coordinators_fte"] / df["teachers_k12_fte"]) * 100.0, np.nan
    )

    # Denominator 3: Administrative Share of Total District Staff (%)
    valid_tot_staff = df["total_staff_fte"] > 0
    df["core_admin_share_of_total_staff_pct"] = np.where(
        valid_tot_staff, (df["core_admin_fte"] / df["total_staff_fte"]) * 100.0, np.nan
    )
    df["admin_coord_share_of_total_staff_pct"] = np.where(
        valid_tot_staff, (df["total_admin_and_coordinators_fte"] / df["total_staff_fte"]) * 100.0, np.nan
    )
    df["teachers_share_of_total_staff_pct"] = np.where(
        valid_tot_staff, (df["teachers_k12_fte"] / df["total_staff_fte"]) * 100.0, np.nan
    )

    # Denominator 4: Administrators per School Building
    valid_sch = df["operating_schools_count"] > 0
    df["school_admin_per_school"] = np.where(
        valid_sch, df["school_administrators_fte"] / df["operating_schools_count"], np.nan
    )
    df["total_admin_per_school"] = np.where(
        valid_sch, df["total_admin_and_coordinators_fte"] / df["operating_schools_count"], np.nan
    )

    # Structural Workload Ratios
    df["students_per_school_admin"] = np.where(
        df["school_administrators_fte"] > 0, df["enrollment_total"] / df["school_administrators_fte"], np.nan
    )
    df["students_per_lea_admin"] = np.where(
        df["lea_administrators_fte"] > 0, df["enrollment_total"] / df["lea_administrators_fte"], np.nan
    )
    df["teachers_per_school_admin"] = np.where(
        df["school_administrators_fte"] > 0, df["teachers_k12_fte"] / df["school_administrators_fte"], np.nan
    )

    return df
