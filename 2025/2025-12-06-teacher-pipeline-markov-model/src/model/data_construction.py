"""
Teacher Pipeline Model - Data Construction Guide
=================================================

This module provides utilities for constructing model inputs from
federal data sources (NCES, Title II, IPEDS).

Includes:
- NTPS data processing
- Title II completer aggregation
- Experience distribution computation
- Admin/coach count extraction
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# NTPS SUBJECT FIELD MAPPING
# =============================================================================

# NTPS Field codes and their model subject mapping
NTPS_FIELD_TO_SUBJECT = {
    # Elementary
    'General elementary education': 'ELEM',
    'Elementary education, general': 'ELEM',
    
    # Special Education
    'Special education': 'SPED',
    'Special education, general': 'SPED',
    
    # English/Language Arts
    'English and language arts': 'ELA',
    'English': 'ELA',
    'Language arts': 'ELA',
    'Reading': 'ELA',
    
    # STEM
    'Mathematics': 'STEM',
    'Science - general': 'STEM',
    'Biology or life sciences': 'STEM',
    'Physical sciences': 'STEM',
    'Chemistry': 'STEM',
    'Physics': 'STEM',
    'Earth sciences': 'STEM',
    'Computer science': 'STEM',
    
    # Social Studies
    'Social studies or social sciences': 'SOCSCI',
    'History': 'SOCSCI',
    'Civics or government': 'SOCSCI',
    'Geography': 'SOCSCI',
    'Economics': 'SOCSCI',
    
    # Languages
    'English as a second language': 'LANG',
    'Foreign languages': 'LANG',
    'Spanish': 'LANG',
    'French': 'LANG',
    
    # Other
    'Arts and music': 'OTHER',
    'Music': 'OTHER',
    'Art': 'OTHER',
    'Health education': 'OTHER',
    'Physical education': 'OTHER',
    'Vocational/technical education': 'OTHER',
    'Career and technical education': 'OTHER',
    'All other fields': 'OTHER',
}


# =============================================================================
# DATA SOURCE URLS
# =============================================================================

DATA_SOURCES = {
    'digest_208_20': {
        'url': 'https://nces.ed.gov/programs/digest/d23/tables/dt23_208.20.asp',
        'description': 'Public and private school teachers, enrollment, and pupil/teacher ratios',
        'years': '1955-2022',
    },
    'digest_209_10': {
        'url': 'https://nces.ed.gov/programs/digest/d23/tables/dt23_209.10.asp',
        'description': 'Number and percentage distribution of teachers by characteristics',
        'years': '1987-2021',
    },
    'digest_213_10': {
        'url': 'https://nces.ed.gov/programs/digest/d23/tables/dt23_213.10.asp',
        'description': 'Staff employed in public schools by assignment',
        'years': '1970-2021',
    },
    'ntps_main_assignment': {
        'url': 'https://nces.ed.gov/surveys/ntps/tables.asp',
        'description': 'NTPS tables on main teaching assignment',
        'tables': ['ntps2021_flt03_t1n', 'ntps2021_sflt03_t1s'],
    },
    'title_ii': {
        'url': 'https://title2.ed.gov/Public/Home.aspx',
        'description': 'Teacher preparation enrollment and completers',
        'years': '2008-2022',
    },
    'tfs_2022': {
        'url': 'https://nces.ed.gov/pubsearch/pubsinfo.asp?pubid=2024039',
        'description': 'Teacher Follow-up Survey 2021-22 results',
        'report': 'NCES 2024-039',
    },
}


# =============================================================================
# ANCHOR YEAR DATA TEMPLATES
# =============================================================================

@dataclass
class AnchorYearData:
    """Template for storing anchor year data."""
    
    year: int
    source: str  # 'SASS' or 'NTPS'
    
    # Total teachers from Digest 209.10
    total_teachers: float
    
    # Subject distribution (percentages, should sum to ~100)
    subject_pct: Dict[str, float]
    
    # Experience distribution (percentages)
    experience_pct: Dict[str, float]
    
    # Admin/staff counts from Digest 213.10
    principals: float
    assistant_principals: float
    instructional_coordinators: float
    
    # Title II completers for that year
    title_ii_completers: float


# Example anchor year data structures
ANCHOR_2011_12 = AnchorYearData(
    year=2011,
    source='SASS',
    total_teachers=3_103_000,  # Digest 209.10
    subject_pct={
        'ELEM': 45.0,
        'SPED': 12.5,
        'ELA': 9.0,
        'STEM': 11.5,
        'SOCSCI': 5.5,
        'LANG': 3.5,
        'OTHER': 13.0,
    },
    experience_pct={
        '0-2': 14.8,
        '3-9': 33.2,
        '10+': 52.0,
    },
    principals=89_810,
    assistant_principals=57_670,
    instructional_coordinators=56_130,
    title_ii_completers=195_000,
)

ANCHOR_2017_18 = AnchorYearData(
    year=2017,
    source='NTPS',
    total_teachers=3_174_000,  # Digest 209.10
    subject_pct={
        'ELEM': 44.5,
        'SPED': 13.0,
        'ELA': 9.5,
        'STEM': 12.0,
        'SOCSCI': 5.5,
        'LANG': 3.5,
        'OTHER': 12.0,
    },
    experience_pct={
        '0-2': 15.2,
        '3-9': 35.8,
        '10+': 49.0,
    },
    principals=90_410,
    assistant_principals=65_680,
    instructional_coordinators=64_890,
    title_ii_completers=170_000,
)

ANCHOR_2020_21 = AnchorYearData(
    year=2020,
    source='NTPS',
    total_teachers=3_038_000,  # Digest 209.10 (pandemic year)
    subject_pct={
        'ELEM': 44.0,
        'SPED': 13.5,
        'ELA': 9.5,
        'STEM': 12.0,
        'SOCSCI': 5.5,
        'LANG': 3.5,
        'OTHER': 12.0,
    },
    experience_pct={
        '0-2': 13.5,  # Fewer new teachers during pandemic
        '3-9': 34.0,
        '10+': 52.5,
    },
    principals=91_850,
    assistant_principals=73_120,
    instructional_coordinators=71_890,
    title_ii_completers=160_000,
)


# =============================================================================
# DATA CONSTRUCTION FUNCTIONS
# =============================================================================

def compute_subject_counts(anchor: AnchorYearData) -> Dict[str, float]:
    """
    Compute absolute teacher counts by subject from anchor year data.
    
    N_{t,s} = T_t × (p_{t,s} / 100)
    """
    counts = {}
    for subject, pct in anchor.subject_pct.items():
        counts[subject] = anchor.total_teachers * (pct / 100)
    return counts


def compute_experience_counts(
    anchor: AnchorYearData,
    subject_counts: Dict[str, float],
) -> Dict[str, Dict[str, float]]:
    """
    Distribute teachers by experience band within each subject.
    
    Assumes experience distribution is uniform across subjects
    (refinement: use subject-specific distributions if available)
    """
    experience = {}
    for subject, total in subject_counts.items():
        experience[subject] = {
            'T0': total * (anchor.experience_pct['0-2'] / 100),
            'T1': total * (anchor.experience_pct['3-9'] / 100),
            'T2': total * (anchor.experience_pct['10+'] / 100),
        }
    return experience


def interpolate_between_anchors(
    anchor_start: AnchorYearData,
    anchor_end: AnchorYearData,
    target_year: int,
) -> Dict[str, float]:
    """
    Linear interpolation of teacher counts between anchor years.
    """
    year_start = anchor_start.year
    year_end = anchor_end.year
    
    if target_year < year_start or target_year > year_end:
        raise ValueError(f"Target year {target_year} outside range [{year_start}, {year_end}]")
    
    # Interpolation weight
    w = (target_year - year_start) / (year_end - year_start)
    
    counts_start = compute_subject_counts(anchor_start)
    counts_end = compute_subject_counts(anchor_end)
    
    interpolated = {}
    for subject in counts_start.keys():
        interpolated[subject] = (1 - w) * counts_start[subject] + w * counts_end[subject]
    
    return interpolated


# =============================================================================
# TITLE II COMPLETER PROCESSING
# =============================================================================

def aggregate_title_ii_completers(
    raw_data: pd.DataFrame,
    subject_crosswalk: Dict[str, str],
) -> Dict[str, float]:
    """
    Aggregate Title II completers to 7-subject model categories.
    
    Args:
        raw_data: DataFrame with columns ['program_area', 'completers']
        subject_crosswalk: Mapping from Title II categories to model subjects
    
    Returns:
        Completers by model subject
    """
    result = {s: 0.0 for s in ['ELEM', 'SPED', 'ELA', 'STEM', 'SOCSCI', 'LANG', 'OTHER']}
    
    for _, row in raw_data.iterrows():
        program = row['program_area']
        completers = row['completers']
        
        # Find matching subject
        subject = subject_crosswalk.get(program, 'OTHER')
        result[subject] += completers
    
    return result


def apply_pass_rates(
    completers: Dict[str, float],
    pass_rates: Dict[str, float],
) -> Dict[str, float]:
    """
    Apply licensure pass rates to get licensed completers.
    
    Default pass rates derived from Title II aggregate data and NCTQ analysis.
    """
    default_pass_rates = {
        'ELEM': 0.92,
        'SPED': 0.88,
        'ELA': 0.91,
        'STEM': 0.85,  # Lower for math/science
        'SOCSCI': 0.90,
        'LANG': 0.87,
        'OTHER': 0.90,
    }
    
    rates = {**default_pass_rates, **pass_rates}
    
    return {subject: count * rates.get(subject, 0.90) 
            for subject, count in completers.items()}


# =============================================================================
# ATTRITION DATA PROCESSING
# =============================================================================

@dataclass
class TFSResults:
    """Structure for TFS stayer/mover/leaver data."""
    
    year: str
    stayers_pct: float
    movers_pct: float  # Same school type
    leavers_pct: float
    
    # Leaver destinations (% of leavers)
    left_for_other_ed: float
    left_for_non_ed: float
    retired: float


TFS_2021_22 = TFSResults(
    year='2021-22',
    stayers_pct=86.1,
    movers_pct=5.8,
    leavers_pct=8.1,
    left_for_other_ed=18.3,
    left_for_non_ed=42.1,
    retired=27.4,
)


def compute_attrition_rate_from_tfs(tfs: TFSResults) -> float:
    """
    Compute pure attrition rate (leavers only, not movers).
    """
    return tfs.leavers_pct / 100


def compute_destination_shares(tfs: TFSResults) -> Dict[str, float]:
    """
    Compute shares of different exit destinations.
    """
    return {
        'other_ed': tfs.left_for_other_ed / 100,
        'non_ed': tfs.left_for_non_ed / 100,
        'retired': tfs.retired / 100,
        'other': 1 - (tfs.left_for_other_ed + tfs.left_for_non_ed + tfs.retired) / 100,
    }


# =============================================================================
# ADMIN/COACH ALLOCATION
# =============================================================================

def allocate_admin_to_subjects(
    total_principals: float,
    total_aps: float,
    total_coordinators: float,
    principal_weights: Dict[str, float],
    coach_weights: Dict[str, float],
) -> Dict[str, Dict[str, float]]:
    """
    Allocate administrators and instructional coordinators to subjects.
    
    Returns nested dict: {subject: {role: count}}
    """
    result = {}
    
    for subject in principal_weights.keys():
        result[subject] = {
            'principal': total_principals * principal_weights[subject],
            'ap': total_aps * principal_weights[subject],  # Use same weights for APs
            'coordinator': total_coordinators * coach_weights[subject],
        }
    
    return result


# =============================================================================
# VALIDATION UTILITIES
# =============================================================================

def validate_subject_totals(
    subject_counts: Dict[str, float],
    expected_total: float,
    tolerance: float = 0.01,
) -> bool:
    """Check that subject counts sum to expected total."""
    computed_total = sum(subject_counts.values())
    error = abs(computed_total - expected_total) / expected_total
    return error <= tolerance


def validate_experience_distribution(
    experience_counts: Dict[str, float],
    expected_shares: Dict[str, float],
    tolerance: float = 0.02,
) -> Dict[str, bool]:
    """Validate experience distribution against expected shares."""
    total = sum(experience_counts.values())
    results = {}
    
    for band, count in experience_counts.items():
        computed_share = count / total if total > 0 else 0
        expected_share = expected_shares.get(band, 0)
        error = abs(computed_share - expected_share)
        results[band] = error <= tolerance
    
    return results


# =============================================================================
# EXAMPLE: FULL DATA CONSTRUCTION PIPELINE
# =============================================================================

def construct_model_inputs(
    anchor_year: AnchorYearData,
    title_ii_raw: Optional[pd.DataFrame] = None,
    custom_pass_rates: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Full pipeline to construct model inputs from an anchor year.
    
    Returns:
        Dictionary with all required model inputs
    """
    # 1. Compute subject counts
    subject_counts = compute_subject_counts(anchor_year)
    
    # 2. Validate totals
    assert validate_subject_totals(subject_counts, anchor_year.total_teachers)
    
    # 3. Distribute by experience
    experience_by_subject = compute_experience_counts(anchor_year, subject_counts)
    
    # 4. Process Title II completers if provided
    if title_ii_raw is not None:
        completers_raw = aggregate_title_ii_completers(
            title_ii_raw, 
            NTPS_FIELD_TO_SUBJECT
        )
        completers_licensed = apply_pass_rates(
            completers_raw,
            custom_pass_rates or {}
        )
    else:
        # Use anchor year total distributed proportionally
        completers_licensed = {
            subject: anchor_year.title_ii_completers * (pct / 100)
            for subject, pct in anchor_year.subject_pct.items()
        }
    
    # 5. Allocate admin/coaches
    admin_allocation = allocate_admin_to_subjects(
        anchor_year.principals,
        anchor_year.assistant_principals,
        anchor_year.instructional_coordinators,
        principal_weights={
            'ELEM': 0.45, 'SPED': 0.05, 'ELA': 0.15,
            'STEM': 0.12, 'SOCSCI': 0.12, 'LANG': 0.03, 'OTHER': 0.08,
        },
        coach_weights={
            'ELEM': 0.15, 'SPED': 0.10, 'ELA': 0.40,
            'STEM': 0.15, 'SOCSCI': 0.08, 'LANG': 0.07, 'OTHER': 0.05,
        },
    )
    
    return {
        'year': anchor_year.year,
        'total_teachers': anchor_year.total_teachers,
        'subject_counts': subject_counts,
        'experience_by_subject': experience_by_subject,
        'completers_licensed': completers_licensed,
        'admin_by_subject': admin_allocation,
        'experience_distribution': anchor_year.experience_pct,
    }


# =============================================================================
# MAIN: EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Construct inputs for 2017-18
    inputs = construct_model_inputs(ANCHOR_2017_18)
    
    print("=" * 60)
    print("MODEL INPUT CONSTRUCTION: 2017-18")
    print("=" * 60)
    
    print(f"\nTotal Teachers: {inputs['total_teachers']:,.0f}")
    
    print("\nTeachers by Subject:")
    for subject, count in inputs['subject_counts'].items():
        pct = count / inputs['total_teachers'] * 100
        print(f"  {subject:8s}: {count:>12,.0f}  ({pct:5.1f}%)")
    
    print("\nExperience Distribution (ELEM example):")
    for band, count in inputs['experience_by_subject']['ELEM'].items():
        print(f"  {band}: {count:,.0f}")
    
    print("\nLicensed Completers by Subject:")
    for subject, count in inputs['completers_licensed'].items():
        print(f"  {subject:8s}: {count:>8,.0f}")
    
    print("\nAdmin Allocation (ELEM example):")
    for role, count in inputs['admin_by_subject']['ELEM'].items():
        print(f"  {role:12s}: {count:,.0f}")
    
    # Example interpolation
    print("\n" + "=" * 60)
    print("INTERPOLATION: 2015 (between 2011 and 2017)")
    print("=" * 60)
    
    counts_2015 = interpolate_between_anchors(ANCHOR_2011_12, ANCHOR_2017_18, 2015)
    for subject, count in counts_2015.items():
        print(f"  {subject:8s}: {count:>12,.0f}")
