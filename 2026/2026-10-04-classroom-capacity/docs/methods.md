# Methodological Framework: Classroom Capacity and Class Size Measurement

This document details the mathematical, statistical, and econometric specifications governing Study A and the construction of the longitudinal class-size panel.

---

## 1. Class Size Estimands and Weighting Schemes

Let $s$ index schools, $c$ index courses, and $t$ index academic survey waves.

### 1.1 School-Course Mean Class Size (Course-Cell Observation)
CRDC observes the total course enrollment $E_{sct}$ and the total number of class sections $K_{sct}$ for school-course cell $i \equiv (s,c,t)$. The derived school-course mean is:

$$\bar C_{sct} = \frac{E_{sct}}{K_{sct}}$$

Valid only when $K_{sct} \ge 1$ and $E_{sct} \ge 1$. If $K_{sct} = 0$, $\bar C_{sct}$ is undefined (`NaN`). Observations with $\bar C_{sct} > 60$ represent virtual/distance-learning programs and are excluded from brick-and-mortar analytical samples.

### 1.2 The Three Distinct Weighting Schemes

#### Quantity A: Unweighted Course-Cell Mean
Answers: **"What is the average size of a school's course offering?"**
Treats each school-course offering as an equal institutional observation:

$$\bar C_{\text{cell}} = \frac{1}{M} \sum_{i=1}^M \bar C_i$$

where $M$ is the number of active school-course cells.

#### Quantity B: Section-Weighted Mean
Answers: **"What is the average size of an offered class section?"**
Weights each school-course cell by its reported section count $K_i$:

$$\bar C_{\text{sec-wt}} = \frac{\sum_{i=1}^M K_i \bar C_i}{\sum_{i=1}^M K_i} = \frac{\sum_{i=1}^M E_i}{\sum_{i=1}^M K_i} = E_K[\bar C_i]$$

*(Note: This is strictly section-weighted, NOT teacher-weighted. Teacher-reported class size requires survey instruments such as SASS/NTPS where individual educators report their own class rosters.)*

#### Quantity C: Enrollment-Weighted Course-Cell Mean (Observable Lower-Bound Proxy)
Answers: **"What is the average school-course mean experienced by an enrolled student?"**
Weights each school-course cell by its student enrollment $E_i$:

$$\bar C_{\text{enr-wt}} = \frac{\sum_{i=1}^M E_i \bar C_i}{\sum_{i=1}^M E_i} = \frac{\sum_{i=1}^M \frac{E_i^2}{K_i}}{\sum_{i=1}^M E_i} = \frac{E_K[\bar C_i^2]}{E_K[\bar C_i]}$$

### 1.3 Two Mathematically Distinct Variance Effects

A critical clarification established in Phase 3.2 is that the total gap between class-section sizes and student experiences consists of two mathematically separate variance components:

#### 1. Between-Cell Size Dispersion (Observable $C - B$ Gap):
The gap between the enrollment-weighted mean ($C$) and the section-weighted mean ($B$) reflects variance in mean section size **across school-course cells**, weighted by section counts $K_i$:

$$C - B = \frac{E_K[\bar C_i^2] - (E_K[\bar C_i])^2}{E_K[\bar C_i]} = \frac{\operatorname{Var}_K(\bar C_i)}{E_K[\bar C_i]} \ge 0$$

where $\operatorname{Var}_K(\bar C_i)$ is the section-weighted variance of cell means across schools.  
**Conceptual Meaning:** Students are disproportionately enrolled in schools and courses with larger average section sizes. This between-cell sorting mechanically drives $C$ above $B$ by $+4.0$ to $+5.5$ students (+24% to +39%) in national secondary courses.

#### 2. Within-Cell Unobserved Dispersion (The Lower-Bound Property $C_{\text{true-student}} - C$):
Let school-course cell $i$ contain $K_i$ sections of sizes $s_{ij}$ for $j = 1, \dots, K_i$, with $\sum_{j=1}^{K_i} s_{ij} = E_i$. The true student-experienced mean across all individual classroom sections is:

$$\bar C_{\text{true-student}} = \frac{\sum_{i=1}^M \sum_{j=1}^{K_i} s_{ij}^2}{\sum_{i=1}^M E_i}$$

By the within-cell section variance decomposition $\sum_{j=1}^{K_i} s_{ij}^2 = K_i \bar C_i^2 + K_i \sigma_i^2$ where $\sigma_i^2 = \frac{1}{K_i} \sum_{j=1}^{K_i} (s_{ij} - \bar C_i)^2 \ge 0$:

$$\bar C_{\text{true-student}} - C = \frac{\sum_{i=1}^M K_i \sigma_i^2}{\sum_{i=1}^M E_i} \ge 0$$

$$\therefore \bar C_{\text{true-student}} \ge \bar C_{\text{enr-wt}}$$

**Conceptual Meaning:** Unobserved section size dispersion within the same school-course cell (e.g., an honors section of 28 alongside an intervention section of 14) further shifts true student experience strictly above $C$. Thus, $\bar C_{\text{enr-wt}}$ is an **observable mathematical lower bound** on true student-experienced section size.

### 1.4 Three Distinct Weighting Gaps
- **Gap $C - A$ ($+3.7$ to $+7.0$ students nationally, +26% to +56%):** Divergence between enrollment-weighted lower bound and unweighted cell mean. Equal weighting of school-course cells produces substantially lower estimates than enrollment weighting because small, single-section rural schools receive equal weight to large multi-section suburban high schools. Neither estimand is incorrect; they answer different questions.
- **Gap $C - B$ ($+4.0$ to $+5.5$ students nationally, +24% to +39%):** Between-cell variance gap $\frac{\operatorname{Var}_K(\bar C_i)}{E_K[\bar C_i]}$.
- **Gap $B - A$ ($-0.8$ to $+1.5$ students nationally, -6% to +12%):** Difference between section-weighted and unweighted cell means, capturing the covariance between section count $K_i$ and cell mean $\bar C_i$.

---

## 2. Staffing Allocation Wedge Metrics

Pupil-teacher ratio (PTR) is an aggregate resource metric, not a measure of classroom size. In secondary schools, schedule structure mechanically drives a wedge between PTR and class size.

### 2.1 Absolute Staffing Wedge
$$\Delta_{sct} = \bar C_{sct} - \text{PTR}_{st}$$

where $\text{PTR}_{st}$ is the contemporaneous pupil-to-classroom-teacher ratio from CCD.

### 2.2 Relative Staffing Wedge Ratio
$$\Omega_{sct} = \frac{\bar C_{sct}}{\text{PTR}_{st}}$$

In a secondary departmentalized schedule where teachers teach $p$ out of $P$ daily periods (e.g., 5 of 7 periods, planning fraction $\lambda = 5/7 \approx 0.714$), mechanical scheduling alone produces $\Omega \approx 1 / \lambda = 1.40$. Non-instructional specialists, instructional coaches, and department chairs further expand this wedge.

---

## 3. Econometric Specifications

### 3.1 Interactive Within-School Course Hierarchy (School × Wave Fixed Effects)
To estimate whether foundational core courses absorb systematically larger classes than advanced electives within the exact same school building during the exact same academic year:

$$\bar C_{sct} = \alpha_{st} + \gamma_c + \epsilon_{sct}$$

where:
- $\alpha_{st}$ are school $\times$ wave fixed effects, absorbing campus scale, facility constraints, staffing formulas, and local enrollment shocks;
- $\gamma_c$ are course fixed effects estimated relative to **Geometry** as the reference course;
- Non-informative groups (school-waves offering fewer than 2 distinct courses) are strictly filtered out;
- Standard errors are clustered at the school campus level ($s$);
- An **absorbed-FE finite-sample adjustment** $c_{\text{df}} = \sqrt{\frac{N - K}{N - K - G}}$ is applied to account for the $G$ absorbed fixed-effects dimensions not subtracted by default demeaned cluster covariance;
- Statistical inference uses Student's $t$ distribution with $df = G_{\text{clusters}} - 1$.

### 3.2 Pairwise Geometry Robustness Models
To ensure results are not sensitive to network absorption across unbalanced course menus, direct pairwise models are estimated:
$$\bar C_{sct} = \alpha_{st} + \gamma_c \cdot \mathbf{1}\{c = \text{target}\} + \epsilon_{sct}$$
restricted strictly to school-waves offering **both** Geometry and the target course.

### 3.3 Course-Specific Balanced Panel Robustness
To ensure that longitudinal trajectories and post-pandemic plateaus are not artifacts of changes in school universe composition:
- **Geometry & Algebra I:** Balanced panel of schools continuously reporting the course across 5 waves (2015–16 to 2023–24), isolating the 2013–14 survey break.
- **Biology, Chemistry, Calculus, Algebra II, Physics, Advanced Math:** Balanced panel of schools continuously reporting the course across all 6 waves (2013–14 to 2023–24).

---

## 4. Contemporary Benchmarks on Secondary Class Size Across Perspectives

| Perspective | Data Source & Survey Year | Metric Definition | Target Estimand | Typical Range |
| :--- | :--- | :--- | :--- | :---: |
| **1. Macro Staffing Ratio** | NCES CCD (Annual 2023–24) | Total Enrolled / Total FTE Teachers | Campus Resource Ratio | **14.5 – 16.5** |
| **2. Institutional Offering Mean** | CRDC (2023–24 Universal Census) | Unweighted Mean of Course Cells ($\bar C_{\text{cell}}$) | Average Course Offering | **15.0 – 15.4** |
| **3. Class Section Mean** | CRDC (2023–24 Universal Census) | Section-Weighted Mean ($\sum E / \sum K$) | Average Section Size | **15.0 – 16.3** |
| **4. Student-Experienced Lower Bound** | CRDC (2023–24 Universal Census) | Enrollment-Weighted Mean ($\sum E \bar C / \sum E$) | Lower-Bound Student Experience | **19.1 – 20.3** |
| **5. Teacher-Reported Class Size** | NCES NTPS (2020–21 Survey) | Self-Reported Period / Class Roster | Individual Educator Load | **21.0 – 23.3** |
