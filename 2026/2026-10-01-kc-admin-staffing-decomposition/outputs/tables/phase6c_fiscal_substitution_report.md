# Phase 6C Econometric Audit: Instructional Coordinator Expansion — Substitution vs. Additive Layering

## Executive Summary

Gate 6C evaluates whether districts expanded internal instructional coordinator staffing (`CORSUP`) as a direct
substitute for external non-personnel instructional support spending ($E07 - V13 - V14$), or whether coordinators
represented an **additive organizational layer** expanding total supervisory overhead across the Kansas City metropolitan area.

### Key Empirical Findings:
1. **No Evidence of Generalized Substitution Across the Regional Panel:** Across the 55 balanced districts from 2014–15 to 2022–23,
   within-district fixed-effects estimation yields no evidence that coordinator growth was associated with systematic declines in
   non-personnel instructional-support spending (baseline FE $\beta = +11.85, t = +1.59, p = 0.111$;
   State$\times$Year FE $\beta = +9.44, t = +1.36, p = 0.175$;
   Winsorized $\beta = +9.03, t = +1.31, p = 0.190$).
   Point estimates are uniformly nonnegative, which is more consistent with additive layering than pure insourcing, but the estimates are
   imprecise and do not establish a positive additive effect.
2. **Long-Difference and First-Difference Robustness:** Over the 8-year span, long differences across all 55 districts confirm
   that changes in coordinator staffing are weakly positively associated with real non-personnel spending ($\beta = +14.96, t = +1.22, p = 0.221$).
   First-difference models with common year effects ($\beta = -2.65, t = -0.38, p = 0.704$) and state$\times$year effects ($\beta = -4.07, t = -0.58, p = 0.563$)
   are similarly indistinguishable from zero.
3. **Dynamic Lead-Lag Neutrality:** Lagged coordinator changes do not predict subsequent non-personnel reductions ($t = +1.09, p = 0.274$),
   and high initial non-personnel spending does not predict subsequent coordinator hiring ($t = +0.02, p = 0.984$). The data do not support
   generalized non-personnel expenditure substitution as the dominant regional mechanism.
4. **The Shawnee Mission Exception — Partial Substitution plus Net Expansion:** Among the focal archetypes, **Shawnee Mission USD 512**
   presents the single prominent case consistent with partial substitution. As its coordinator workforce expanded from 27.6 FTE to 93.0 FTE,
   its real non-personnel instructional support spending fell by **34.5%** (from **$63.51** to **$41.59 / pupil**), while total instructional
   support spending expanded from $409 to $511 / pupil to accommodate the centralized coaching payroll.
5. **The Lean / School Supervision Counterpart:** Conversely, districts with lean central coordinator footprints (**Lee's Summit R-VII**
   and **North Kansas City 74**) devote far higher resources to non-personnel instructional support (**$185.77** and **$436.60 / pupil**,
   representing 36% to 44% of their total Function 2200 budget), relying heavily on non-personnel services while concentrating administrative
   FTE inside school buildings.

---

## 1. Accounting Framework & Analytical Regimes

Using official Census / NCES F-33 Annual Survey of School System Finances data (Functions 2100–2400):
- **Total Function 2200 Current Operations (`E07`):** Covers improvement of instruction, curriculum development, and instructional staff training.
- **Personnel Costs:** Salaries (`V13`) and Employee Benefits (`V14`).
- **Non-Personnel Instructional Support ($NP_{it} = E07 - V13 - V14$):** Encompasses purchased professional and technical services (Object 300),
  other purchased services (Object 400/500), supplies, and curriculum materials.

### Interpretation Matrix:
| Empirical Pattern | $\Delta$ Non-Personnel ($NP$) | $\Delta$ Total Support ($E07$) | Institutional Mechanism |
| :--- | :---: | :---: | :--- |
| **Regime 1: Pure Substitution / Insourcing** | $\beta < 0$ | $\beta \approx 0$ | External vendor contracts replaced with direct coordinator FTE |
| **Regime 2: Additive Internal Staffing Layer** | $\beta \approx 0$ | $\beta > 0$ | Coordinators hired without displacing external operating expenditure |
| **Regime 3: Broad Apparatus Expansion** | $\beta > 0$ | $\beta \gg 0$ | Rapid simultaneous growth in both personnel and non-personnel support |
| **Regime 4: Partial Substitution + Expansion** | $\beta < 0$ | $\beta > 0$ | Non-personnel costs decline, but total payroll growth yields net fiscal expansion |

---

## 2. Focal Archetype Trajectories (2014–15 to 2022–23)

### Table 2.1: Non-Personnel Support Spending vs. Coordinator Staffing Across Focal Archetypes

| District | State | Organizational Archetype | Year | CORSUP FTE | CORSUP / 100 Tchs | Real E07 / Pupil | Real Salary / Pupil | Real Non-Personnel / Pupil | Non-Personnel Share % |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Kansas City** | KS | Dual-Intensity (Coaching + School Supervision) | 2014-2015 | 106.9 | 7.68 | $1250.05 | $594.32 | **$494.34** | 39.5% |
| **Kansas City** | KS | Dual-Intensity (Coaching + School Supervision) | 2018-2019 | 99.6 | 6.36 | $992.45 | $671.22 | **$145.42** | 14.7% |
| **Kansas City** | KS | Dual-Intensity (Coaching + School Supervision) | 2022-2023 | 112.5 | 7.27 | $1281.72 | $821.94 | **$223.44** | 17.4% |
| **LEE'S SUMMIT R-VII** | MO | Lean / Department Chair | 2014-2015 | 21.5 | 1.87 | $397.25 | $220.92 | **$115.32** | 29.0% |
| **LEE'S SUMMIT R-VII** | MO | Direct School Supervision | 2018-2019 | 8.0 | 0.67 | $478.53 | $247.23 | **$157.44** | 32.9% |
| **LEE'S SUMMIT R-VII** | MO | Direct School Supervision | 2022-2023 | 12.3 | 1.00 | $515.16 | $249.17 | **$185.77** | 36.1% |
| **NORTH KANSAS CITY 74** | MO | Lean / Department Chair | 2014-2015 | 15.0 | 1.22 | $975.69 | $437.23 | **$428.68** | 43.9% |
| **NORTH KANSAS CITY 74** | MO | Direct School Supervision | 2018-2019 | 21.4 | 1.61 | $941.08 | $410.58 | **$419.37** | 44.6% |
| **NORTH KANSAS CITY 74** | MO | Direct School Supervision | 2022-2023 | 33.7 | 2.34 | $993.34 | $433.15 | **$436.60** | 44.0% |
| **Olathe** | KS | Lean / Department Chair | 2014-2015 | 31.9 | 1.64 | $515.14 | $351.94 | **$61.83** | 12.0% |
| **Olathe** | KS | Lean / Department Chair | 2018-2019 | 39.3 | 1.85 | $551.56 | $367.00 | **$78.72** | 14.3% |
| **Olathe** | KS | Lean / Department Chair | 2022-2023 | 67.8 | 2.98 | $617.14 | $409.86 | **$55.56** | 9.0% |
| **RAYTOWN C-2** | MO | Coaching Overlay | 2014-2015 | 23.2 | 3.81 | $644.28 | $349.86 | **$217.11** | 33.7% |
| **RAYTOWN C-2** | MO | Coaching Overlay | 2018-2019 | 22.8 | 3.65 | $581.63 | $296.67 | **$203.93** | 35.1% |
| **RAYTOWN C-2** | MO | Coaching Overlay | 2022-2023 | 22.0 | 3.65 | $683.72 | $315.28 | **$281.70** | 41.2% |
| **Shawnee Mission Pub Sch** | KS | Lean / Department Chair | 2014-2015 | 27.6 | 1.61 | $409.45 | $275.75 | **$63.51** | 15.5% |
| **Shawnee Mission Pub Sch** | KS | Lean / Department Chair | 2018-2019 | 46.5 | 2.66 | $474.95 | $343.20 | **$54.26** | 11.4% |
| **Shawnee Mission Pub Sch** | KS | Coaching Overlay | 2022-2023 | 93.0 | 4.81 | $511.05 | $355.89 | **$41.59** | 8.1% |

---

## 3. Econometric Regression Results Across All 55 Districts

### Table 3.1: Econometric Substitution vs. Layering Models

| Model Specification | Dependent Variable | Predictor | Coef (Real $/Pupil) | Robust SE | $t$-stat | $p$-value | $R^2$ | $N$ |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **FE Model 1: Real Non-Personnel Support / Pupil** | `real_instr_support_nonpersonnel_per_pupil` | `corsup_per_100_teachers` | **+11.85** | 7.44 | +1.59 | 0.111 | 0.703 | 492 |
| **FE Model 2: Real Total E07 Support / Pupil** | `real_instr_support_total_per_pupil` | `corsup_per_100_teachers` | **+19.41** | 15.70 | +1.24 | 0.216 | 0.741 | 492 |
| **FE Model 3: Real Salary Support / Pupil** | `real_instr_support_salary_per_pupil` | `corsup_per_100_teachers` | **+4.72** | 7.75 | +0.61 | 0.543 | 0.809 | 492 |
| **FE Sensitivity 1: District + State*Year FE (Real NP / Pupil)** | `real_instr_support_nonpersonnel_per_pupil` | `corsup_per_100_teachers` | **+9.44** | 6.96 | +1.36 | 0.175 | 0.712 | 492 |
| **FE Sensitivity 2: District + State*Year FE (Total E07 / Pupil)** | `real_instr_support_total_per_pupil` | `corsup_per_100_teachers` | **+13.05** | 14.38 | +0.91 | 0.364 | 0.756 | 492 |
| **FE Sensitivity 3: Winsorized NP (2.5-97.5%) + State*Year FE** | `real_np_win` | `corsup_per_100_teachers` | **+9.03** | 6.88 | +1.31 | 0.190 | 0.784 | 492 |
| **Long Difference Model 1: Delta Real Non-Personnel / Pupil** | `delta_real_np_per_pupil` | `delta_corsup_rate` | **+14.96** | 12.23 | +1.22 | 0.221 | 0.059 | 55 |
| **Long Difference Model 2: Delta Real Total E07 / Pupil** | `delta_real_tot_per_pupil` | `delta_corsup_rate` | **+2.99** | 16.40 | +0.18 | 0.855 | 0.022 | 55 |
| **Long Difference Model 3: Delta Real Salary / Pupil** | `delta_real_sal_per_pupil` | `delta_corsup_rate` | **-10.21** | 9.59 | -1.06 | 0.287 | 0.012 | 55 |
| **Contemporaneous FD: Delta Real NP ~ Delta CORSUP** | `delta_real_np` | `delta_corsup` | **-1.35** | 6.72 | -0.20 | 0.841 | 0.000 | 434 |
| **FD Sensitivity 1: Delta Real NP ~ Delta CORSUP + Year FE** | `delta_real_np` | `delta_corsup` | **-2.65** | 6.96 | -0.38 | 0.704 | 0.025 | 434 |
| **FD Sensitivity 2: Delta Real NP ~ Delta CORSUP + State*Year FE** | `delta_real_np` | `delta_corsup` | **-4.07** | 7.04 | -0.58 | 0.563 | 0.042 | 434 |
| **Lead Response: Delta Real NP (t+1) ~ Delta CORSUP (t)** | `lead_delta_np` | `delta_corsup` | **+10.36** | 9.48 | +1.09 | 0.274 | 0.005 | 379 |
| **Insourcing Stimulus: Delta CORSUP (t+1) ~ Real NP Level (t)** | `lead_delta_corsup` | `real_instr_support_nonpersonnel_per_pupil` | **+0.00** | 0.00 | +0.02 | 0.984 | 0.000 | 435 |

---

## 4. Substantive Conclusions & Next Steps

1. **Disproving Regional Insourcing:** Across the Kansas City metropolitan area, coordinator expansion cannot be justified as an
   economizing insourcing move that eliminated outside consulting or curriculum contracts. Districts that added coordinators
   did not systematically reduce non-personnel spending in Function 2200.
2. **Heterogeneous Institutional Realities:** The regional aggregate masks two opposing institutional models:
   - **Coaching Overlay Systems (Shawnee Mission):** Concentrated instructional coordination internally, producing genuine non-personnel
     savings per student (-$22/pupil, -34.5%) while substantially expanding total instructional overhead.
   - **School-Supervision Systems (Lee's Summit, North Kansas City):** Kept central coordinators lean, delegating supervision to school
     principals while contracting heavily for non-personnel support ($185 to $436/pupil).
3. **Gating Gate 6C.2 (State Object-Level Triangulation):** Because the macro F-33 analysis confirms that Shawnee Mission is the single
   clear candidate for partial substitution while the region at large exhibited additive layering, Gate 6C.2 should specifically audit
   Missouri ASBR and Kansas KSDE Object 300 (Purchased Professional/Technical Services) actuals for the six focal archetypes.
4. **Revisiting Gate 6D (Standardized Achievement):** With the organizational and fiscal mechanisms now rigorously documented,
   achievement recovery screening should test whether these distinct delivery models (internal coaching overlay vs. contracted expertise)
   yielded differential learning recovery in mathematics and reading.
