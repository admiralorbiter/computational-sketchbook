"""
Teacher Pipeline Model - Sensitivity Analysis & Validation Framework
=====================================================================

This module provides tools for:
1. Parameter sensitivity analysis
2. Monte Carlo uncertainty quantification
3. Validation against observed data
4. Scenario comparison visualization

Designed to ensure model robustness and quantify projection uncertainty.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from itertools import product
import warnings
from concurrent.futures import ProcessPoolExecutor
import json

# Import model components (would be from teacher_pipeline_model.py)
# from teacher_pipeline_model import TeacherPipelineModel, Subject, State


# =============================================================================
# PARAMETER UNCERTAINTY SPECIFICATIONS
# =============================================================================

@dataclass
class ParameterUncertainty:
    """Specification of uncertainty for a single parameter."""
    name: str
    base_value: float
    lower_bound: float
    upper_bound: float
    distribution: str = 'uniform'  # 'uniform', 'normal', 'triangular'
    priority: str = 'high'  # 'high', 'medium', 'low'
    
    def sample(self, rng: np.random.Generator) -> float:
        """Draw a random sample from the uncertainty distribution."""
        if self.distribution == 'uniform':
            return rng.uniform(self.lower_bound, self.upper_bound)
        elif self.distribution == 'normal':
            # Truncated normal
            std = (self.upper_bound - self.lower_bound) / 4
            sample = rng.normal(self.base_value, std)
            return np.clip(sample, self.lower_bound, self.upper_bound)
        elif self.distribution == 'triangular':
            return rng.triangular(self.lower_bound, self.base_value, self.upper_bound)
        else:
            raise ValueError(f"Unknown distribution: {self.distribution}")


# Default parameter uncertainties
DEFAULT_UNCERTAINTIES = [
    # Attrition parameters
    ParameterUncertainty('baseline_attrition_2023_2025', 0.075, 0.065, 0.090, 'triangular', 'high'),
    ParameterUncertainty('stem_multiplier', 1.20, 1.05, 1.35, 'triangular', 'high'),
    ParameterUncertainty('sped_multiplier', 1.30, 1.15, 1.50, 'triangular', 'high'),
    ParameterUncertainty('elem_multiplier', 0.95, 0.85, 1.05, 'uniform', 'medium'),
    ParameterUncertainty('early_career_modifier', 1.60, 1.40, 1.80, 'triangular', 'high'),
    ParameterUncertainty('mid_career_modifier', 0.85, 0.75, 0.95, 'uniform', 'medium'),
    ParameterUncertainty('late_career_modifier', 0.90, 0.80, 1.00, 'uniform', 'medium'),
    
    # Transition parameters
    ParameterUncertainty('reentry_rate', 0.10, 0.05, 0.15, 'triangular', 'medium'),
    ParameterUncertainty('hire_rate_cap', 0.85, 0.75, 0.95, 'uniform', 'medium'),
    ParameterUncertainty('admin_transition_rate', 0.015, 0.010, 0.025, 'uniform', 'low'),
    
    # Cross-subject mobility
    ParameterUncertainty('elem_to_sped_mobility', 0.020, 0.010, 0.030, 'uniform', 'low'),
    
    # Pipeline parameters
    ParameterUncertainty('program_completion_rate', 0.75, 0.70, 0.80, 'uniform', 'medium'),
    ParameterUncertainty('licensure_pass_rate', 0.90, 0.85, 0.95, 'uniform', 'medium'),
]


# =============================================================================
# ONE-AT-A-TIME SENSITIVITY ANALYSIS
# =============================================================================

@dataclass
class SensitivityResult:
    """Result of sensitivity analysis for one parameter."""
    parameter_name: str
    base_output: float
    low_output: float
    high_output: float
    elasticity: float  # % change in output / % change in parameter
    
    @property
    def range_impact(self) -> float:
        """Absolute range of output variation."""
        return self.high_output - self.low_output


def one_at_a_time_sensitivity(
    model_func: Callable,
    base_params: Dict[str, float],
    uncertainties: List[ParameterUncertainty],
    output_metric: str = 'total_teachers',
) -> List[SensitivityResult]:
    """
    Perform one-at-a-time (OAT) sensitivity analysis.
    
    Varies each parameter while holding others at base values.
    
    Args:
        model_func: Function that takes params dict and returns outputs dict
        base_params: Dictionary of base parameter values
        uncertainties: List of parameter uncertainties to test
        output_metric: Key in output dict to analyze
    
    Returns:
        List of SensitivityResult for each parameter
    """
    results = []
    
    # Get base output
    base_output = model_func(base_params)[output_metric]
    
    for uncertainty in uncertainties:
        # Test low bound
        low_params = base_params.copy()
        low_params[uncertainty.name] = uncertainty.lower_bound
        low_output = model_func(low_params)[output_metric]
        
        # Test high bound
        high_params = base_params.copy()
        high_params[uncertainty.name] = uncertainty.upper_bound
        high_output = model_func(high_params)[output_metric]
        
        # Compute elasticity (using midpoint method)
        param_change = (uncertainty.upper_bound - uncertainty.lower_bound) / uncertainty.base_value
        output_change = (high_output - low_output) / base_output
        elasticity = output_change / param_change if param_change != 0 else 0
        
        results.append(SensitivityResult(
            parameter_name=uncertainty.name,
            base_output=base_output,
            low_output=low_output,
            high_output=high_output,
            elasticity=elasticity,
        ))
    
    # Sort by absolute elasticity
    results.sort(key=lambda r: abs(r.elasticity), reverse=True)
    
    return results


def tornado_chart_data(results: List[SensitivityResult]) -> pd.DataFrame:
    """
    Prepare data for tornado chart visualization.
    """
    data = []
    for r in results:
        data.append({
            'Parameter': r.parameter_name,
            'Low_Deviation': r.low_output - r.base_output,
            'High_Deviation': r.high_output - r.base_output,
            'Abs_Impact': abs(r.high_output - r.low_output),
            'Elasticity': r.elasticity,
        })
    return pd.DataFrame(data).sort_values('Abs_Impact', ascending=True)


# =============================================================================
# MONTE CARLO UNCERTAINTY QUANTIFICATION
# =============================================================================

@dataclass
class MonteCarloResults:
    """Results from Monte Carlo simulation."""
    
    n_simulations: int
    output_metric: str
    samples: np.ndarray
    parameter_samples: pd.DataFrame
    
    @property
    def mean(self) -> float:
        return float(np.mean(self.samples))
    
    @property
    def std(self) -> float:
        return float(np.std(self.samples))
    
    @property
    def percentile_5(self) -> float:
        return float(np.percentile(self.samples, 5))
    
    @property
    def percentile_95(self) -> float:
        return float(np.percentile(self.samples, 95))
    
    @property
    def percentile_25(self) -> float:
        return float(np.percentile(self.samples, 25))
    
    @property
    def percentile_75(self) -> float:
        return float(np.percentile(self.samples, 75))
    
    def confidence_interval(self, level: float = 0.90) -> Tuple[float, float]:
        """Return symmetric confidence interval."""
        alpha = (1 - level) / 2
        return (
            float(np.percentile(self.samples, alpha * 100)),
            float(np.percentile(self.samples, (1 - alpha) * 100))
        )
    
    def summary(self) -> Dict:
        """Summary statistics."""
        return {
            'mean': self.mean,
            'std': self.std,
            'cv': self.std / self.mean if self.mean != 0 else np.nan,
            'p5': self.percentile_5,
            'p25': self.percentile_25,
            'median': float(np.median(self.samples)),
            'p75': self.percentile_75,
            'p95': self.percentile_95,
        }


def monte_carlo_simulation(
    model_func: Callable,
    base_params: Dict[str, float],
    uncertainties: List[ParameterUncertainty],
    n_simulations: int = 1000,
    output_metric: str = 'total_teachers',
    seed: Optional[int] = None,
) -> MonteCarloResults:
    """
    Run Monte Carlo simulation to quantify output uncertainty.
    
    Args:
        model_func: Function that takes params dict and returns outputs dict
        base_params: Dictionary of base parameter values
        uncertainties: List of parameter uncertainties
        n_simulations: Number of Monte Carlo samples
        output_metric: Key in output dict to analyze
        seed: Random seed for reproducibility
    
    Returns:
        MonteCarloResults object
    """
    rng = np.random.default_rng(seed)
    
    samples = np.zeros(n_simulations)
    param_records = []
    
    for i in range(n_simulations):
        # Sample parameters
        params = base_params.copy()
        param_sample = {}
        
        for uncertainty in uncertainties:
            sampled_value = uncertainty.sample(rng)
            params[uncertainty.name] = sampled_value
            param_sample[uncertainty.name] = sampled_value
        
        param_records.append(param_sample)
        
        # Run model
        try:
            output = model_func(params)
            samples[i] = output[output_metric]
        except Exception as e:
            warnings.warn(f"Simulation {i} failed: {e}")
            samples[i] = np.nan
    
    # Remove failed simulations
    valid_mask = ~np.isnan(samples)
    
    return MonteCarloResults(
        n_simulations=int(np.sum(valid_mask)),
        output_metric=output_metric,
        samples=samples[valid_mask],
        parameter_samples=pd.DataFrame(param_records)[valid_mask.tolist()],
    )


def compute_sobol_indices(
    mc_results: MonteCarloResults,
    uncertainties: List[ParameterUncertainty],
) -> pd.DataFrame:
    """
    Compute first-order Sobol sensitivity indices from Monte Carlo samples.
    
    Uses correlation-based approximation for computational efficiency.
    
    Args:
        mc_results: Results from monte_carlo_simulation
        uncertainties: Parameter uncertainty specifications
    
    Returns:
        DataFrame with Sobol indices by parameter
    """
    results = []
    
    total_variance = np.var(mc_results.samples)
    
    for uncertainty in uncertainties:
        param_values = mc_results.parameter_samples[uncertainty.name].values
        
        # Correlation-based first-order index approximation
        correlation = np.corrcoef(param_values, mc_results.samples)[0, 1]
        first_order_approx = correlation ** 2
        
        results.append({
            'Parameter': uncertainty.name,
            'Correlation': correlation,
            'First_Order_Index': first_order_approx,
            'Priority': uncertainty.priority,
        })
    
    df = pd.DataFrame(results)
    df = df.sort_values('First_Order_Index', ascending=False)
    df['Cumulative_Explained'] = df['First_Order_Index'].cumsum()
    
    return df


# =============================================================================
# VALIDATION FRAMEWORK
# =============================================================================

@dataclass
class ValidationTarget:
    """Specification of a validation target."""
    name: str
    observed_value: float
    tolerance_abs: Optional[float] = None  # Absolute tolerance
    tolerance_pct: Optional[float] = None  # Percentage tolerance
    source: str = ''
    year: Optional[int] = None
    
    def check(self, simulated_value: float) -> Tuple[bool, float]:
        """
        Check if simulated value is within tolerance of observed.
        
        Returns:
            Tuple of (passed, error)
        """
        error = simulated_value - self.observed_value
        pct_error = error / self.observed_value if self.observed_value != 0 else np.inf
        
        if self.tolerance_abs is not None:
            passed = abs(error) <= self.tolerance_abs
        elif self.tolerance_pct is not None:
            passed = abs(pct_error) <= self.tolerance_pct
        else:
            passed = True  # No tolerance specified
        
        return passed, pct_error


# Standard validation targets
VALIDATION_TARGETS_2017_18 = [
    ValidationTarget(
        name='total_teachers',
        observed_value=3_174_000,
        tolerance_pct=0.03,
        source='NCES Digest 209.10',
        year=2017,
    ),
    ValidationTarget(
        name='elem_teachers',
        observed_value=1_413_000,
        tolerance_pct=0.05,
        source='NTPS 2017-18',
        year=2017,
    ),
    ValidationTarget(
        name='sped_teachers',
        observed_value=412_620,
        tolerance_pct=0.05,
        source='NTPS 2017-18',
        year=2017,
    ),
    ValidationTarget(
        name='stem_teachers',
        observed_value=380_880,
        tolerance_pct=0.05,
        source='NTPS 2017-18',
        year=2017,
    ),
    ValidationTarget(
        name='early_career_share',
        observed_value=0.152,
        tolerance_abs=0.02,
        source='NTPS 2017-18',
        year=2017,
    ),
    ValidationTarget(
        name='attrition_rate',
        observed_value=0.081,
        tolerance_abs=0.015,
        source='TFS 2017-18',
        year=2017,
    ),
]


@dataclass
class ValidationReport:
    """Complete validation report."""
    
    targets: List[ValidationTarget]
    simulated_values: Dict[str, float]
    results: Dict[str, Tuple[bool, float]]
    
    @property
    def n_passed(self) -> int:
        return sum(1 for passed, _ in self.results.values() if passed)
    
    @property
    def n_total(self) -> int:
        return len(self.results)
    
    @property
    def pass_rate(self) -> float:
        return self.n_passed / self.n_total if self.n_total > 0 else 0
    
    def summary_df(self) -> pd.DataFrame:
        """Create summary DataFrame."""
        data = []
        for target in self.targets:
            passed, error = self.results[target.name]
            data.append({
                'Metric': target.name,
                'Observed': target.observed_value,
                'Simulated': self.simulated_values.get(target.name, np.nan),
                'Error_Pct': error * 100,
                'Passed': passed,
                'Source': target.source,
            })
        return pd.DataFrame(data)
    
    def __str__(self) -> str:
        lines = [
            "=" * 60,
            "VALIDATION REPORT",
            "=" * 60,
            f"Passed: {self.n_passed}/{self.n_total} ({self.pass_rate*100:.1f}%)",
            "",
            self.summary_df().to_string(index=False),
            "=" * 60,
        ]
        return "\n".join(lines)


def validate_model(
    simulated_outputs: Dict[str, float],
    targets: List[ValidationTarget],
) -> ValidationReport:
    """
    Validate model outputs against observed targets.
    
    Args:
        simulated_outputs: Dictionary of simulated metric values
        targets: List of validation targets
    
    Returns:
        ValidationReport
    """
    results = {}
    
    for target in targets:
        simulated_value = simulated_outputs.get(target.name, np.nan)
        passed, error = target.check(simulated_value)
        results[target.name] = (passed, error)
    
    return ValidationReport(
        targets=targets,
        simulated_values=simulated_outputs,
        results=results,
    )


# =============================================================================
# SCENARIO COMPARISON
# =============================================================================

@dataclass
class ScenarioDefinition:
    """Full scenario definition for projection."""
    
    name: str
    description: str
    parameter_adjustments: Dict[str, float] = field(default_factory=dict)
    completer_growth_rate: float = 0.0
    demand_growth_rate: float = 0.0
    
    def apply_to_params(self, base_params: Dict[str, float]) -> Dict[str, float]:
        """Apply adjustments to base parameters."""
        params = base_params.copy()
        for key, adjustment in self.parameter_adjustments.items():
            if key in params:
                params[key] = params[key] + adjustment
            else:
                params[key] = adjustment
        return params


# Standard scenarios
STANDARD_SCENARIOS = [
    ScenarioDefinition(
        name='Baseline',
        description='Central estimates; attrition normalizes by 2025',
    ),
    ScenarioDefinition(
        name='High_Attrition',
        description='Elevated attrition persists; weak re-entry',
        parameter_adjustments={
            'baseline_attrition_2023_2025': 0.015,  # Add 1.5pp
            'reentry_rate': -0.03,  # Reduce by 3pp
            'stem_multiplier': 0.10,  # Add 10pp
        },
    ),
    ScenarioDefinition(
        name='Low_Attrition',
        description='Attrition falls below pre-pandemic; strong re-entry',
        parameter_adjustments={
            'baseline_attrition_2023_2025': -0.010,  # Reduce by 1pp
            'reentry_rate': 0.03,  # Increase by 3pp
        },
    ),
    ScenarioDefinition(
        name='STEM_Crisis',
        description='Severe STEM shortage; tech wages continue rising',
        parameter_adjustments={
            'stem_multiplier': 0.15,  # Add 15pp to multiplier
        },
        completer_growth_rate=-0.02,  # 2% annual decline in STEM completers
    ),
    ScenarioDefinition(
        name='SPED_Improvement',
        description='Policy intervention improves SPED retention',
        parameter_adjustments={
            'sped_multiplier': -0.15,  # Reduce multiplier by 15pp
        },
        completer_growth_rate=0.03,  # 3% annual increase in SPED completers
    ),
    ScenarioDefinition(
        name='Pipeline_Recovery',
        description='Enrollment rebounds post-pandemic',
        completer_growth_rate=0.02,  # 2% annual growth
    ),
]


def compare_scenarios(
    model_func: Callable,
    base_params: Dict[str, float],
    scenarios: List[ScenarioDefinition],
    projection_years: int = 10,
) -> pd.DataFrame:
    """
    Compare projections across multiple scenarios.
    
    Args:
        model_func: Function that takes params and returns time-series output
        base_params: Base parameter values
        scenarios: List of scenario definitions
        projection_years: Number of years to project
    
    Returns:
        DataFrame with projections by scenario and year
    """
    results = []
    
    for scenario in scenarios:
        params = scenario.apply_to_params(base_params)
        
        # Add scenario-specific growth rates
        params['completer_growth_rate'] = scenario.completer_growth_rate
        params['demand_growth_rate'] = scenario.demand_growth_rate
        
        # Run projection
        output = model_func(params)
        
        # Assume output has 'yearly_results' key
        for year, metrics in enumerate(output.get('yearly_results', [])):
            results.append({
                'Scenario': scenario.name,
                'Year': year,
                **metrics
            })
    
    return pd.DataFrame(results)


# =============================================================================
# REPORTING UTILITIES
# =============================================================================

def generate_sensitivity_report(
    oat_results: List[SensitivityResult],
    mc_results: MonteCarloResults,
    sobol_indices: pd.DataFrame,
) -> str:
    """Generate formatted sensitivity analysis report."""
    
    lines = [
        "=" * 70,
        "SENSITIVITY ANALYSIS REPORT",
        "=" * 70,
        "",
        "1. ONE-AT-A-TIME SENSITIVITY ANALYSIS",
        "-" * 40,
        "",
    ]
    
    # Top 5 most influential parameters
    lines.append("Top 5 Most Influential Parameters (by elasticity):")
    for i, result in enumerate(oat_results[:5], 1):
        lines.append(
            f"  {i}. {result.parameter_name}: "
            f"elasticity = {result.elasticity:.3f}, "
            f"range impact = {result.range_impact:,.0f}"
        )
    
    lines.extend([
        "",
        "2. MONTE CARLO UNCERTAINTY QUANTIFICATION",
        "-" * 40,
        f"Number of simulations: {mc_results.n_simulations}",
        f"Output metric: {mc_results.output_metric}",
        "",
        "Summary Statistics:",
        f"  Mean:   {mc_results.mean:>12,.0f}",
        f"  Std:    {mc_results.std:>12,.0f}",
        f"  CV:     {mc_results.std/mc_results.mean:>12.1%}",
        "",
        "Percentiles:",
        f"  5th:    {mc_results.percentile_5:>12,.0f}",
        f"  25th:   {mc_results.percentile_25:>12,.0f}",
        f"  50th:   {np.median(mc_results.samples):>12,.0f}",
        f"  75th:   {mc_results.percentile_75:>12,.0f}",
        f"  95th:   {mc_results.percentile_95:>12,.0f}",
        "",
        "90% Confidence Interval:",
        f"  [{mc_results.percentile_5:,.0f}, {mc_results.percentile_95:,.0f}]",
        "",
        "3. SOBOL SENSITIVITY INDICES",
        "-" * 40,
        "",
    ])
    
    lines.append(sobol_indices.to_string(index=False))
    
    lines.extend([
        "",
        "=" * 70,
    ])
    
    return "\n".join(lines)


# =============================================================================
# MAIN: EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Example model function (placeholder)
    def example_model_func(params: Dict[str, float]) -> Dict[str, float]:
        """Placeholder model function for testing."""
        base_teachers = 3_200_000
        
        # Simple linear sensitivity to parameters
        attrition_effect = params.get('baseline_attrition_2023_2025', 0.075)
        stem_effect = params.get('stem_multiplier', 1.20)
        
        total = base_teachers * (1 - attrition_effect * 2) * (2 - stem_effect * 0.1)
        
        return {
            'total_teachers': total,
            'stem_teachers': total * 0.12,
            'sped_teachers': total * 0.13,
        }
    
    # Base parameters
    base_params = {
        'baseline_attrition_2023_2025': 0.075,
        'stem_multiplier': 1.20,
        'sped_multiplier': 1.30,
        'elem_multiplier': 0.95,
        'early_career_modifier': 1.60,
        'mid_career_modifier': 0.85,
        'late_career_modifier': 0.90,
        'reentry_rate': 0.10,
        'hire_rate_cap': 0.85,
        'admin_transition_rate': 0.015,
        'elem_to_sped_mobility': 0.020,
        'program_completion_rate': 0.75,
        'licensure_pass_rate': 0.90,
    }
    
    print("Running One-at-a-Time Sensitivity Analysis...")
    oat_results = one_at_a_time_sensitivity(
        example_model_func,
        base_params,
        DEFAULT_UNCERTAINTIES,
    )
    
    print("\nRunning Monte Carlo Simulation (500 samples)...")
    mc_results = monte_carlo_simulation(
        example_model_func,
        base_params,
        DEFAULT_UNCERTAINTIES,
        n_simulations=500,
        seed=42,
    )
    
    print("\nComputing Sobol Indices...")
    sobol_indices = compute_sobol_indices(mc_results, DEFAULT_UNCERTAINTIES)
    
    # Generate report
    report = generate_sensitivity_report(oat_results, mc_results, sobol_indices)
    print(report)
    
    # Validation example
    print("\n" + "=" * 70)
    print("VALIDATION EXAMPLE")
    print("=" * 70)
    
    simulated = {
        'total_teachers': 3_150_000,
        'elem_teachers': 1_400_000,
        'sped_teachers': 420_000,
        'stem_teachers': 375_000,
        'early_career_share': 0.16,
        'attrition_rate': 0.085,
    }
    
    validation_report = validate_model(simulated, VALIDATION_TARGETS_2017_18)
    print(validation_report)
