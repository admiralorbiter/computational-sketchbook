# Epistemic Boundaries and Measurement Limitations

Strict empirical discipline requires explicitly defining what the available federal datasets can and cannot measure. Below are the seven core epistemic boundaries governing Study A and the classroom capacity analysis.

---

## 1. School-Course Aggregates and the Lower-Bound Property

1. **Aggregation Over Sections:** CRDC collects only total course enrollment ($E$) and total number of class sections ($K$) per school-course cell. The derived measure $\bar C = E / K$ is the **school-course mean class size**.
2. **Unobservable Section Dispersion:** CRDC cannot observe within-school variation among sections. A reported 6 sections averaging 30 students could represent:
   - Six perfectly uniform sections: $(30, 30, 30, 30, 30, 30)$;
   - Or wide variance across honors, remedial, and co-taught sections: $(20, 25, 28, 32, 35, 40)$.
3. **The Lower-Bound Theorem:** By the within-cell variance decomposition $\sum s_{ij}^2 = K_i \bar s_i^2 + K_i \sigma_i^2$, whenever sections within a school differ in size ($\sigma_i^2 > 0$), the true student-experienced mean is strictly greater than the enrollment-weighted course-cell mean:
   $$\bar C_{\text{true-student}} = \bar C_{\text{enr-wt}} + \frac{\sum_i K_i \sigma_i^2}{\sum_i E_i} \ge \bar C_{\text{enr-wt}}$$
   Therefore, CRDC enrollment-weighted means represent a **mathematical lower bound** on student-experienced section size.

---

## 2. Threshold Exposure Semantics: Cell Means Do Not Bound Section Exposure

1. **Cell vs. Section Thresholds:** A school-course cell mean $\bar C_i \ge 30$ does **not** bound the proportion of individual students in classrooms $\ge 30$ in either direction:
   - *False Positive Case:* A school with two sections of [35, 25] has cell mean 30.0. 100% of enrollment is in a cell averaging $\ge 30$, but only 58% (35/60) sit in a class $\ge 30$.
   - *False Negative Case:* A school with two sections of [32, 24] has cell mean 28.0. 0% of enrollment is in a cell averaging $\ge 30$, but 57% (32/56) sit in a class $\ge 30$.
2. **Disciplinary Language Standard:** Statements such as "X% of students are in classes $\ge 30$" are strictly inadmissible. The correct terminology is:
   > *"X% of student enrollment is concentrated in school-course cells whose mean class size is $\ge 30$."*
   This serves as an index of institutional exposure to large-class environments, not an exact individual headcount.

---

## 3. Algebra I Collection Timing Mismatch (Bidirectional Bias)

1. **Survey Timing Asynchrony:** In the 2023–24 CRDC School Form, the number of Algebra I classes ($K$) is enumerated on **October 1**, while student enrollment ($E$) is explicitly enumerated on **a day at the end of the regular school year**. In contrast, Geometry and all science courses measure both $K$ and $E$ on the contemporaneous October 1 snapshot date.
2. **Bidirectional Bias Direction:** This asynchrony does **not** guarantee a downward bias:
   - *Upward Pressure:* Cumulative enrollment, semester-based block scheduling, and spring credit-recovery transfers can inflate spring enrollment relative to fall capacity.
   - *Downward Pressure:* High school dropouts, course withdrawals, and mid-year schedule changes reduce spring enrollment relative to fall seats.
3. **Methodological Safeguard:** Geometry is adopted as the primary mathematical reference course across all fixed-effects and cross-sectional benchmarks. Sensitivity models excluding Algebra I verify that substantive conclusions do not depend on Algebra I timing.

---

## 4. Longitudinal Survey Discontinuities (2013–14 & 2020–21)

1. **2013–14 Grade-Span Break:** In the 2013–14 CRDC wave, Algebra I and Geometry data collections spanned grades 7–12 combined. Beginning in 2015–16, collections separated middle school (grades 7–8) from high school (grades 9–12). Consequently, 10-year longitudinal comparisons for mathematics must use **2015–16 through 2023–24** as the primary comparable series, treating 2013–14 as an isolated earlier benchmark.
2. **2020–21 COVID-19 Disruption:** Data collected during the 2020–21 academic year reflect emergency remote instruction, hybrid scheduling, and altered grading policies. The observed 1.5–2.0 student dip must not be interpreted as a permanent secular structural shift.

---

## 5. Justification and Impact of the >60 Class-Size Truncation

1. **Exclusion Criterion:** School-course records with derived mean class size $\bar C_i > 60$ are excluded from brick-and-mortar analytical samples.
2. **Empirical Distribution:** Across all 924,846 records in the longitudinal panel, cells exceeding 60 students represent only **0.450% of active records**.
3. **Organizational Profile:** Inspection confirms these cells are almost exclusively statewide virtual charters, cyber correspondence schools, and independent study programs (e.g., Interior Distance Education of Alaska: 1,919 students in 1 class).
4. **Impact on Robustness:** Truncation alters median class sizes by $0.00$ students and 90th percentiles by $<0.08$ students, but protects quadratic weighting formulas ($\sum E_i^2 / K_i$) from extreme asymptotic distortion.

---

## 6. Strict Missingness Handling in Demographic Summations

1. **Suppression and Reserve Codes:** CRDC records negative integers (e.g., -5, -7, -9) for small-cell privacy suppression, missing data, and non-applicability.
2. **Naive Summation Bias:** Treating negative values as zero prior to summing demographic components creates substantial downward undercount bias.
3. **Strict Policy (`require_complete=True`):** In the production pipeline, any school-course record where an active demographic component is negative or missing yields a missing (`NaN`) derived total. No missing component is silently coerced to zero.

---

## 7. The 2023–24 Nonbinary Gender Classification (`_X`)

1. **Category Expansion:** The 2023–24 CRDC introduced reporting for nonbinary students (`_X`) alongside male (`_M`) and female (`_F`).
2. **Harmonization Architecture:** Pipeline extraction dynamically detects whether `_X` is reported and executes 3-way strict summation for 2023–24 while preserving 2-way summation for 2013–14 through 2021–22.
