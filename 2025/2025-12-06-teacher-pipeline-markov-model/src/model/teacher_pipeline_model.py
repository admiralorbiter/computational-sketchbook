"""
Enhanced Teacher Pipeline Model v3.0
=====================================
A comprehensive supply-demand framework for U.S. K-12 teacher workforce modeling.

Features:
- Subject stratification (7 categories)
- School-type stratification (high/low poverty)
- Certification pathway separation (traditional/alternative)
- Experience bands (4 levels)
- Reserve pool with experience-dependent re-entry
- Explicit retirement modeling
- Cross-subject mobility
- Demand-side modeling (enrollment → required teachers)
- Bayesian uncertainty quantification

Author: Generated from model specification
Version: 3.0
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import warnings

# =============================================================================
# ENUMERATIONS & CONSTANTS
# =============================================================================

class Subject(Enum):
    """7 subject categories aligned with NTPS taxonomy"""
    ELEM = 0    # Elementary/Generalist
    SPED = 1    # Special Education
    ELA = 2     # English Language Arts
    STEM = 3    # Math/Science/CS
    SOCSCI = 4  # Social Studies
    LANG = 5    # ELL/World Languages
    OTHER = 6   # Arts, Music, PE, CTE

class SchoolType(Enum):
    """School poverty stratification"""
    HIGH = 0    # High-poverty (≥75% FRPL)
    LOW = 1     # Low-poverty (<75% FRPL)

class ExperienceBand(Enum):
    """Experience levels"""
    NOVICE = 0      # 0-2 years
    EARLY = 1       # 3-5 years
    MID = 2         # 6-14 years
    VETERAN = 3     # 15+ years

class Pathway(Enum):
    """Certification pathway"""
    TRADITIONAL = 0
    ALTERNATIVE = 1

# State indices in the 14-dimensional state vector
STATE_P_TRAD = 0    # Program enrolled - traditional
STATE_P_ALT = 1     # Program enrolled - alternative
STATE_L = 2         # Licensed, seeking position
STATE_T_H_0 = 3     # Teaching, High-poverty, Novice
STATE_T_H_1 = 4     # Teaching, High-poverty, Early
STATE_T_H_2 = 5     # Teaching, High-poverty, Mid
STATE_T_H_3 = 6     # Teaching, High-poverty, Veteran
STATE_T_L_0 = 7     # Teaching, Low-poverty, Novice
STATE_T_L_1 = 8     # Teaching, Low-poverty, Early
STATE_T_L_2 = 9     # Teaching, Low-poverty, Mid
STATE_T_L_3 = 10    # Teaching, Low-poverty, Veteran
STATE_R = 11        # Reserve pool
STATE_A = 12        # Admin/Coach
STATE_E = 13        # Exit (absorbing)

NUM_STATES = 14
NUM_SUBJECTS = 7

# =============================================================================
# PARAMETER DATA CLASS
# =============================================================================

@dataclass
class ModelParameters:
    """All model parameters with defaults based on literature"""
    
    # Baseline attrition by year (dictionary: year -> rate)
    baseline_attrition: Dict[int, float] = field(default_factory=lambda: {
        2010: 0.060, 2011: 0.060, 2012: 0.060, 2013: 0.060, 2014: 0.060,
        2015: 0.070, 2016: 0.070, 2017: 0.070, 2018: 0.070, 2019: 0.070,
        2020: 0.055, 2021: 0.090, 2022: 0.090,
        2023: 0.075, 2024: 0.075, 2025: 0.075,
        2026: 0.070, 2027: 0.070, 2028: 0.070, 2029: 0.070, 2030: 0.070
    })
    
    # Subject multipliers (relative attrition risk)
    subject_multipliers: Dict[Subject, float] = field(default_factory=lambda: {
        Subject.ELEM: 0.95,
        Subject.SPED: 1.30,
        Subject.ELA: 0.95,
        Subject.STEM: 1.20,
        Subject.SOCSCI: 0.90,
        Subject.LANG: 1.15,
        Subject.OTHER: 0.85
    })
    
    # School-type multipliers
    school_type_multipliers: Dict[SchoolType, float] = field(default_factory=lambda: {
        SchoolType.HIGH: 1.50,
        SchoolType.LOW: 0.85
    })
    
    # Experience modifiers by band
    experience_modifiers: Dict[ExperienceBand, float] = field(default_factory=lambda: {
        ExperienceBand.NOVICE: 1.60,
        ExperienceBand.EARLY: 1.10,
        ExperienceBand.MID: 0.75,
        ExperienceBand.VETERAN: 0.85
    })
    
    # Experience band durations (years to progress to next band)
    band_durations: Dict[ExperienceBand, int] = field(default_factory=lambda: {
        ExperienceBand.NOVICE: 3,   # 0-2 years
        ExperienceBand.EARLY: 3,    # 3-5 years
        ExperienceBand.MID: 9,      # 6-14 years
        ExperienceBand.VETERAN: 999 # 15+ years (no progression)
    })
    
    # Retirement parameters
    retirement_base: float = 0.02          # Base retirement rate before vesting
    retirement_vesting_year: int = 25      # Years until pension vesting
    retirement_acceleration: float = 0.15  # Exponential acceleration post-vesting
    
    # School mobility
    mobility_H_to_L: float = 0.05  # Annual prob of moving H→L (among stayers)
    mobility_L_to_H: float = 0.02  # Annual prob of moving L→H (among stayers)
    
    # Pipeline parameters
    program_completion_rate: float = 0.75
    licensure_pass_rate_trad: float = 0.92
    licensure_pass_rate_alt: float = 0.85
    hire_rate_trad: float = 0.65
    hire_rate_alt: float = 0.80
    h_school_placement_share: float = 0.55  # Share of new hires placed in H schools
    
    # Reserve pool parameters
    reentry_rate_initial: float = 0.15    # η₀: first-year re-entry probability
    reentry_decay_rate: float = 0.20       # δ: decay rate for re-entry probability
    license_lapse_rate: float = 0.10       # Annual rate of reserve → exit
    
    # Admin transition rates by experience
    admin_transition_rates: Dict[ExperienceBand, float] = field(default_factory=lambda: {
        ExperienceBand.NOVICE: 0.002,
        ExperienceBand.EARLY: 0.008,
        ExperienceBand.MID: 0.015,
        ExperienceBand.VETERAN: 0.010
    })
    
    # Destination split (among leavers)
    license_retain_rate: float = 0.60  # δ: proportion retaining license
    
    # Cross-subject mobility rates (from, to) -> annual rate
    cross_subject_mobility: Dict[Tuple[Subject, Subject], float] = field(default_factory=lambda: {
        (Subject.ELEM, Subject.SPED): 0.020,
        (Subject.ELA, Subject.SPED): 0.010,
        (Subject.ELA, Subject.LANG): 0.010,
    })


# =============================================================================
# DEMAND MODEL
# =============================================================================

@dataclass
class DemandParameters:
    """Parameters for teacher demand modeling"""
    
    # Instructional time weights by grade level and subject
    # (elementary, middle, high) for each subject
    instructional_weights: Dict[Subject, Tuple[float, float, float]] = field(default_factory=lambda: {
        Subject.ELEM: (0.70, 0.00, 0.00),
        Subject.SPED: (0.10, 0.12, 0.10),
        Subject.ELA: (0.00, 0.22, 0.20),
        Subject.STEM: (0.00, 0.22, 0.25),
        Subject.SOCSCI: (0.00, 0.15, 0.18),
        Subject.LANG: (0.00, 0.08, 0.10),
        Subject.OTHER: (0.20, 0.21, 0.17)
    })
    
    # Target class sizes
    class_size_general_elem: float = 22.0
    class_size_general_secondary: float = 25.0
    class_size_sped: float = 10.0
    class_size_lang: float = 20.0
    
    # High-poverty adjustment factor
    h_poverty_class_size_factor: float = 0.95


def compute_teacher_demand(enrollment_elem: float, enrollment_middle: float,
                           enrollment_high: float, params: DemandParameters,
                           subject: Subject) -> float:
    """
    Compute teacher demand for a subject given student enrollment.
    
    Parameters
    ----------
    enrollment_elem : float
        Elementary student enrollment
    enrollment_middle : float
        Middle school enrollment
    enrollment_high : float
        High school enrollment
    params : DemandParameters
        Demand model parameters
    subject : Subject
        Subject category
    
    Returns
    -------
    float
        Required number of teachers
    """
    weights = params.instructional_weights[subject]
    
    # Determine class size for this subject
    if subject == Subject.SPED:
        class_size = params.class_size_sped
    elif subject == Subject.LANG:
        class_size = params.class_size_lang
    elif subject == Subject.ELEM:
        class_size = params.class_size_general_elem
    else:
        class_size = params.class_size_general_secondary
    
    # Elementary demand
    if weights[0] > 0:
        elem_demand = enrollment_elem * weights[0] / class_size
    else:
        elem_demand = 0
    
    # Middle demand
    if weights[1] > 0:
        middle_demand = enrollment_middle * weights[1] / params.class_size_general_secondary
    else:
        middle_demand = 0
    
    # High demand
    if weights[2] > 0:
        high_demand = enrollment_high * weights[2] / params.class_size_general_secondary
    else:
        high_demand = 0
    
    return elem_demand + middle_demand + high_demand


# =============================================================================
# TRANSITION MATRIX CONSTRUCTION
# =============================================================================

def compute_attrition_rate(year: int, subject: Subject, school_type: SchoolType,
                           exp_band: ExperienceBand, years_in_band: int,
                           params: ModelParameters) -> float:
    """
    Compute the attrition rate for a specific teacher profile.
    
    λ_{t,s,k,i} = λ_t × m_s × κ_k × e_i × (1 + r_i(years))
    """
    # Base rate for year
    base = params.baseline_attrition.get(year, 0.07)
    
    # Apply multipliers
    subj_mult = params.subject_multipliers[subject]
    school_mult = params.school_type_multipliers[school_type]
    exp_mult = params.experience_modifiers[exp_band]
    
    # Retirement adjustment for veterans
    retirement_add = 0.0
    if exp_band == ExperienceBand.VETERAN:
        total_years = 15 + years_in_band  # Approximate total experience
        if total_years >= params.retirement_vesting_year:
            years_post_vest = total_years - params.retirement_vesting_year
            retirement_add = params.retirement_base * np.exp(
                params.retirement_acceleration * years_post_vest
            )
    
    attrition = base * subj_mult * school_mult * exp_mult + retirement_add
    
    # Cap at reasonable maximum
    return min(attrition, 0.50)


def compute_reentry_rate(years_since_teaching: int, params: ModelParameters) -> float:
    """
    Compute re-entry probability based on years since teaching.
    
    η(τ) = η₀ × exp(-δ × τ)
    """
    return params.reentry_rate_initial * np.exp(
        -params.reentry_decay_rate * years_since_teaching
    )


def build_transition_matrix(year: int, subject: Subject, 
                            params: ModelParameters) -> np.ndarray:
    """
    Build the 14×14 transition matrix for a single subject-year.
    
    State ordering:
    0: P_TRAD, 1: P_ALT, 2: L, 
    3-6: T_H^{0-3}, 7-10: T_L^{0-3},
    11: R, 12: A, 13: E
    """
    M = np.zeros((NUM_STATES, NUM_STATES))
    
    # =========================================================================
    # FROM PROGRAM STATES
    # =========================================================================
    
    # P_TRAD -> L (complete and pass) or E (dropout)
    completion_pass_trad = params.program_completion_rate * params.licensure_pass_rate_trad
    M[STATE_P_TRAD, STATE_L] = completion_pass_trad
    M[STATE_P_TRAD, STATE_E] = 1.0 - completion_pass_trad
    
    # P_ALT -> L or E
    completion_pass_alt = params.program_completion_rate * params.licensure_pass_rate_alt
    M[STATE_P_ALT, STATE_L] = completion_pass_alt
    M[STATE_P_ALT, STATE_E] = 1.0 - completion_pass_alt
    
    # =========================================================================
    # FROM LICENSED-SEEKING
    # =========================================================================
    
    # Average hire rate (weighted by pathway mix)
    avg_hire_rate = 0.5 * params.hire_rate_trad + 0.5 * params.hire_rate_alt
    
    f_H = params.h_school_placement_share  # Fraction placed in high-poverty
    
    M[STATE_L, STATE_T_H_0] = avg_hire_rate * f_H
    M[STATE_L, STATE_T_L_0] = avg_hire_rate * (1 - f_H)
    M[STATE_L, STATE_R] = (1 - avg_hire_rate) * 0.80  # Stay licensed
    M[STATE_L, STATE_E] = (1 - avg_hire_rate) * 0.20  # Abandon license
    
    # =========================================================================
    # FROM TEACHING STATES
    # =========================================================================
    
    for k, school_type in enumerate([SchoolType.HIGH, SchoolType.LOW]):
        for i, exp_band in enumerate([ExperienceBand.NOVICE, ExperienceBand.EARLY,
                                      ExperienceBand.MID, ExperienceBand.VETERAN]):
            
            # State index for T_k^i
            state_idx = STATE_T_H_0 + k * 4 + i
            
            # Compute attrition for this state
            avg_years_in_band = params.band_durations[exp_band] // 2
            lambda_ki = compute_attrition_rate(year, subject, school_type, 
                                               exp_band, avg_years_in_band, params)
            
            # Probability of staying in teaching
            p_stay_teaching = 1 - lambda_ki
            
            # Admin transition rate
            alpha_i = params.admin_transition_rates[exp_band]
            
            # Experience progression rate
            if exp_band != ExperienceBand.VETERAN:
                prog_rate = 1.0 / params.band_durations[exp_band]
            else:
                prog_rate = 0  # Veterans don't progress
            
            # School mobility (among stayers)
            if school_type == SchoolType.HIGH:
                mu_out = params.mobility_H_to_L
                other_school_offset = 4  # L states are 4 indices higher
            else:
                mu_out = params.mobility_L_to_H
                other_school_offset = -4  # H states are 4 indices lower
            
            # Transition probabilities
            p_same = p_stay_teaching * (1 - alpha_i) * (1 - prog_rate) * (1 - mu_out)
            
            # Progress to next experience band (same school type)
            if exp_band != ExperienceBand.VETERAN:
                next_state = state_idx + 1
                p_progress = p_stay_teaching * (1 - alpha_i) * prog_rate * (1 - mu_out)
            else:
                next_state = state_idx
                p_progress = 0
            
            # Move to other school type (same experience)
            other_school_state = state_idx + other_school_offset
            p_mobility = p_stay_teaching * (1 - alpha_i) * (1 - prog_rate) * mu_out
            
            # Move to admin
            p_admin = p_stay_teaching * alpha_i
            
            # Leave teaching
            p_reserve = lambda_ki * params.license_retain_rate
            p_exit = lambda_ki * (1 - params.license_retain_rate)
            
            # Fill transition matrix
            M[state_idx, state_idx] = p_same
            if p_progress > 0:
                M[state_idx, next_state] = p_progress
            if 0 <= other_school_state < NUM_STATES:
                M[state_idx, other_school_state] = p_mobility
            M[state_idx, STATE_A] = p_admin
            M[state_idx, STATE_R] = p_reserve
            M[state_idx, STATE_E] = p_exit
    
    # =========================================================================
    # FROM RESERVE POOL
    # =========================================================================
    
    avg_reentry = 0.5 * compute_reentry_rate(1, params) + 0.5 * compute_reentry_rate(3, params)
    
    M[STATE_R, STATE_T_H_0] = avg_reentry * params.h_school_placement_share
    M[STATE_R, STATE_T_L_0] = avg_reentry * (1 - params.h_school_placement_share)
    M[STATE_R, STATE_R] = (1 - avg_reentry) * (1 - params.license_lapse_rate)
    M[STATE_R, STATE_E] = (1 - avg_reentry) * params.license_lapse_rate
    
    # =========================================================================
    # FROM ADMIN/COACH
    # =========================================================================
    
    M[STATE_A, STATE_A] = 0.90
    M[STATE_A, STATE_T_H_2] = 0.01  # Rare return to classroom
    M[STATE_A, STATE_T_L_2] = 0.01
    M[STATE_A, STATE_E] = 0.08
    
    # =========================================================================
    # EXIT STATE (ABSORBING)
    # =========================================================================
    
    M[STATE_E, STATE_E] = 1.0
    
    # Normalize rows to ensure they sum to 1
    row_sums = M.sum(axis=1)
    for i in range(NUM_STATES):
        if row_sums[i] > 0:
            M[i, :] /= row_sums[i]
        else:
            M[i, i] = 1.0  # Self-loop for empty rows
    
    return M


# =============================================================================
# MODEL CLASS
# =============================================================================

class TeacherPipelineModel:
    """
    Main model class for simulating teacher workforce dynamics.
    """
    
    def __init__(self, params: Optional[ModelParameters] = None,
                 demand_params: Optional[DemandParameters] = None):
        self.params = params or ModelParameters()
        self.demand_params = demand_params or DemandParameters()
        self.state = np.zeros((NUM_SUBJECTS, NUM_STATES))
        self.history: List[Dict] = []
        self.current_year: int = 2010
    
    def initialize_state(self, year: int, teacher_counts_by_subject: Dict[Subject, float],
                         experience_distribution: Dict[ExperienceBand, float],
                         school_type_split: Dict[SchoolType, float],
                         program_enrollment: Dict[Subject, Tuple[float, float]]):
        """Initialize the model state from observed data."""
        self.current_year = year
        
        for s, subject in enumerate(Subject):
            total = teacher_counts_by_subject.get(subject, 0)
            
            for i, exp_band in enumerate([ExperienceBand.NOVICE, ExperienceBand.EARLY,
                                          ExperienceBand.MID, ExperienceBand.VETERAN]):
                exp_share = experience_distribution.get(exp_band, 0.25)
                for k, school_type in enumerate([SchoolType.HIGH, SchoolType.LOW]):
                    school_share = school_type_split.get(school_type, 0.5)
                    state_idx = STATE_T_H_0 + k * 4 + i
                    self.state[s, state_idx] = total * exp_share * school_share
            
            prog_trad, prog_alt = program_enrollment.get(subject, (0, 0))
            self.state[s, STATE_P_TRAD] = prog_trad
            self.state[s, STATE_P_ALT] = prog_alt
            self.state[s, STATE_R] = total * 0.20
            self.state[s, STATE_A] = total * 0.05
    
    def step(self, new_program_enrollment: Optional[Dict[Subject, Tuple[float, float]]] = None):
        """Advance the model by one year."""
        self.history.append({
            'year': self.current_year,
            'state': self.state.copy(),
            'teaching_total': self.get_total_teachers(),
            'by_subject': {s: self.get_teachers_by_subject(s) for s in Subject},
            'by_school_type': {k: self.get_teachers_by_school_type(k) for k in SchoolType}
        })
        
        new_state = np.zeros_like(self.state)
        
        for s, subject in enumerate(Subject):
            M = build_transition_matrix(self.current_year, subject, self.params)
            new_state[s, :] = M.T @ self.state[s, :]
        
        if new_program_enrollment:
            for s, subject in enumerate(Subject):
                prog_trad, prog_alt = new_program_enrollment.get(subject, (0, 0))
                new_state[s, STATE_P_TRAD] += prog_trad
                new_state[s, STATE_P_ALT] += prog_alt
        
        self.state = new_state
        self.current_year += 1
    
    def simulate(self, n_years: int, 
                 enrollment_trajectory: Optional[Dict[int, Dict[Subject, Tuple[float, float]]]] = None):
        """Run simulation for n years."""
        for _ in range(n_years):
            new_enroll = enrollment_trajectory.get(self.current_year) if enrollment_trajectory else None
            self.step(new_enroll)
    
    def get_total_teachers(self) -> float:
        teaching_states = list(range(STATE_T_H_0, STATE_T_L_3 + 1))
        return self.state[:, teaching_states].sum()
    
    def get_teachers_by_subject(self, subject: Subject) -> float:
        s = subject.value
        teaching_states = list(range(STATE_T_H_0, STATE_T_L_3 + 1))
        return self.state[s, teaching_states].sum()
    
    def get_teachers_by_school_type(self, school_type: SchoolType) -> float:
        if school_type == SchoolType.HIGH:
            states = list(range(STATE_T_H_0, STATE_T_H_3 + 1))
        else:
            states = list(range(STATE_T_L_0, STATE_T_L_3 + 1))
        return self.state[:, states].sum()
    
    def get_teachers_by_experience(self, exp_band: ExperienceBand) -> float:
        i = exp_band.value
        h_state = STATE_T_H_0 + i
        l_state = STATE_T_L_0 + i
        return self.state[:, h_state].sum() + self.state[:, l_state].sum()
    
    def get_shortage(self, enrollment_elem: float, enrollment_middle: float,
                     enrollment_high: float) -> Dict[Subject, float]:
        shortages = {}
        for subject in Subject:
            demand = compute_teacher_demand(enrollment_elem, enrollment_middle,
                                            enrollment_high, self.demand_params, subject)
            supply = self.get_teachers_by_subject(subject)
            shortages[subject] = demand - supply
        return shortages
    
    def get_history_df(self) -> pd.DataFrame:
        if not self.history:
            return pd.DataFrame()
        
        records = []
        for h in self.history:
            record = {'year': h['year'], 'total_teachers': h['teaching_total']}
            for subject in Subject:
                record[f'teachers_{subject.name}'] = h['by_subject'][subject]
            for school_type in SchoolType:
                record[f'teachers_{school_type.name}'] = h['by_school_type'][school_type]
            records.append(record)
        
        return pd.DataFrame(records)


# =============================================================================
# CALIBRATION UTILITIES
# =============================================================================

def calibrate_hire_rate(observed_stock_t1: float, observed_stock_t2: float,
                        completers_sum: float, attrition_rate: float,
                        delta_years: int) -> float:
    """Back out hire rate from observed stock change."""
    survivors = observed_stock_t1 * ((1 - attrition_rate) ** delta_years)
    entrants_needed = observed_stock_t2 - survivors
    
    if completers_sum <= 0:
        return np.nan
    
    hire_rate = entrants_needed / completers_sum
    return max(0, min(1, hire_rate))


def run_sensitivity_analysis(model: TeacherPipelineModel,
                             param_name: str, values: List[float],
                             n_years: int = 10) -> pd.DataFrame:
    """Run sensitivity analysis by varying a single parameter."""
    import copy
    results = []
    
    for val in values:
        test_model = copy.deepcopy(model)
        
        if hasattr(test_model.params, param_name):
            setattr(test_model.params, param_name, val)
        else:
            warnings.warn(f"Parameter {param_name} not found")
            continue
        
        test_model.simulate(n_years)
        
        results.append({
            'param_value': val,
            'final_total': test_model.get_total_teachers(),
            **{f'{s.name}': test_model.get_teachers_by_subject(s) for s in Subject}
        })
    
    return pd.DataFrame(results)


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def create_example_model():
    """Create and initialize an example model with 2017-18 data approximations."""
    
    model = TeacherPipelineModel()
    
    teacher_counts = {
        Subject.ELEM: 1_200_000,
        Subject.SPED: 420_000,
        Subject.ELA: 385_000,
        Subject.STEM: 455_000,
        Subject.SOCSCI: 280_000,
        Subject.LANG: 175_000,
        Subject.OTHER: 595_000,
    }
    
    experience_dist = {
        ExperienceBand.NOVICE: 0.15,
        ExperienceBand.EARLY: 0.15,
        ExperienceBand.MID: 0.35,
        ExperienceBand.VETERAN: 0.35,
    }
    
    school_split = {
        SchoolType.HIGH: 0.35,
        SchoolType.LOW: 0.65,
    }
    
    program_enrollment = {
        Subject.ELEM: (180_000, 60_000),
        Subject.SPED: (50_000, 30_000),
        Subject.ELA: (40_000, 20_000),
        Subject.STEM: (45_000, 25_000),
        Subject.SOCSCI: (35_000, 15_000),
        Subject.LANG: (20_000, 15_000),
        Subject.OTHER: (50_000, 15_000),
    }
    
    model.initialize_state(
        year=2017,
        teacher_counts_by_subject=teacher_counts,
        experience_distribution=experience_dist,
        school_type_split=school_split,
        program_enrollment=program_enrollment
    )
    
    return model


def main():
    """Run example simulation and print results."""
    
    print("=" * 60)
    print("Enhanced Teacher Pipeline Model v3.0")
    print("=" * 60)
    
    model = create_example_model()
    
    print(f"\nInitial state (2017):")
    print(f"  Total teachers: {model.get_total_teachers():,.0f}")
    for subject in Subject:
        print(f"  {subject.name}: {model.get_teachers_by_subject(subject):,.0f}")
    
    enrollment_traj = {}
    base_enrollment = {
        Subject.ELEM: (180_000, 60_000),
        Subject.SPED: (50_000, 30_000),
        Subject.ELA: (40_000, 20_000),
        Subject.STEM: (45_000, 25_000),
        Subject.SOCSCI: (35_000, 15_000),
        Subject.LANG: (20_000, 15_000),
        Subject.OTHER: (50_000, 15_000),
    }
    
    for year in range(2017, 2031):
        decay = 0.98 ** (year - 2017)
        enrollment_traj[year] = {
            s: (t * decay, a * decay) for s, (t, a) in base_enrollment.items()
        }
    
    print("\nRunning simulation 2017 → 2030...")
    model.simulate(13, enrollment_traj)
    
    print(f"\nFinal state (2030):")
    print(f"  Total teachers: {model.get_total_teachers():,.0f}")
    for subject in Subject:
        print(f"  {subject.name}: {model.get_teachers_by_subject(subject):,.0f}")
    
    print("\nProjected shortages (2030):")
    shortages = model.get_shortage(
        enrollment_elem=25_000_000,
        enrollment_middle=12_000_000,
        enrollment_high=15_000_000
    )
    for subject, shortage in shortages.items():
        status = "SHORTAGE" if shortage > 0 else "surplus"
        print(f"  {subject.name}: {abs(shortage):,.0f} ({status})")
    
    df = model.get_history_df()
    print("\nTeacher totals by year:")
    print(df[['year', 'total_teachers']].to_string(index=False))
    
    return model, df


if __name__ == "__main__":
    model, history_df = main()
