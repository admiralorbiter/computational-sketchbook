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

$$\bar C_{\text{sec-wt}} = \frac{\sum_{i=1}^M K_i \bar C_i}{\sum_{i=1}^M K_i} = \frac{\sum_{i=1}^M E_i}{\sum_{i=1}^M K_i}$$

*(Note: This is strictly section-weighted, NOT teacher-weighted. Teacher-reported class size requires survey instruments such as SASS/NTPS where individual educators report their own class rosters.)*

#### Quantity C: Enrollment-Weighted Course-Cell Mean (Lower-Bound Proxy)
Answers: **"What is the average school-course mean experienced by an enrolled student?"**
Weights each school-course cell by its student enrollment $E_i$:

$$\bar C_{\text{enr-wt}} = \frac{\sum_{i=1}^M E_i \bar C_i}{\sum_{i=1}^M E_i} = \frac{\sum_{i=1}^M \frac{E_i^2}{K_i}}{\sum_{i=1}^M E_i}$$

### 1.3 The Lower-Bound Theorem (Within-Cell Jensen's Inequality)

CRDC publishes aggregate school-course totals $(E_i, K_i)$ rather than section-by-section rosters $s_{i1}, s_{i2}, \dots, s_{iK_i}$. 

**Theorem:**  
Whenever sections within a school-course cell vary in size, the enrollment-weighted course-cell mean $\bar C_{\text{enr-wt}}$ is a strict mathematical lower bound on the true student-experienced section size $\bar C_{\text{true-student}}$.

**Proof:**  
Let school-course cell $i$ contain $K_i$ sections of sizes $s_{ij}$ for $j = 1, \dots, K_i$, with $\sum_{j=1}^{K_i} s_{ij} = E_i$.  
The cell mean is $\bar s_i = \frac{E_i}{K_i}$.  
The true student-experienced mean across all sections is:
$$\bar C_{\text{true-student}} = \frac{\sum_{i=1}^M \sum_{j=1}^{K_i} s_{ij}^2}{\sum_{i=1}^M E_i}$$

By the variance decomposition for section sizes within cell $i$:
$$\sum_{j=1}^{K_i} s_{ij}^2 = K_i \bar s_i^2 + K_i \sigma_i^2$$
where $\sigma_i^2 = \frac{1}{K_i} \sum_{j=1}^{K_i} (s_{ij} - \bar s_i)^2 \ge 0$ is the within-cell section variance.

Summing across all cells:
$$\bar C_{\text{true-student}} = \frac{\sum_{i=1}^M (K_i \bar s_i^2 + K_i \sigma_i^2)}{\sum_{i=1}^M E_i} = \frac{\sum_{i=1}^M \frac{E_i^2}{K_i}}{\sum_{i=1}^M E_i} + \frac{\sum_{i=1}^M K_i \sigma_i^2}{\sum_{i=1}^M E_i} = \bar C_{\text{enr-wt}} + \frac{\sum_{i=1}^M K_i \sigma_i^2}{\sum_{i=1}^M E_i}$$

Since $\sigma_i^2 \ge 0$ for all $i$:
$$\bar C_{\text{true-student}} \ge \bar C_{\text{enr-wt}}$$
with strict inequality whenever any school operates sections of unequal size (e.g., an honors section of 28 alongside an intervention section of 14).

### 1.4 Three Distinct Weighting Gaps
- **Gap $C - A$ ($+3.7$ to $+7.0$ students nationally):** Total gap between enrollment-weighted lower bound and unweighted cell mean. Driven jointly by cross-school enrollment concentration and section counts.
- **Gap $C - B$ ($+4.0$ to $+5.5$ students nationally):** Jensen's inequality gap between enrollment weighting and section weighting. Driven by cross-school variance in section sizes.
- **Gap $B - A$ ($-0.8$ to $+1.5$ students nationally):** Difference between section-weighted and unweighted cell mean. Driven by the correlation between school section counts and average class sizes.

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
- Standard errors are clustered at the school campus level ($s$), with degree-of-freedom scaling $c_{\text{df}} = \sqrt{\frac{N - K}{N - K - G}}$ where $G$ is the number of absorbed fixed effects;
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

## 4. Contemporary Benchmarks on Secondary Class Size

| Perspective | Data Source | Metric Definition | Target Estimand | Typical Range |
| :--- | :--- | :--- | :--- | :--- |
| **Macro Staffing Ratio** | NCES CCD (Annual) | Total Enrolled / Total FTE Teachers | Campus Resource Ratio | 14.5 – 16.5 |
| **Institutional Offering Mean** | CRDC (Biennial Census) | Unweighted Mean of Course Cells ($\bar C_{\text{cell}}$) | Average Course Offering | 13.5 – 15.5 |
| **Class Section Mean** | CRDC (Biennial Census) | Section-Weighted Mean ($\sum E / \sum K$) | Average Section Size | 14.0 – 16.5 |
| **Student-Experienced Lower Bound** | CRDC (Biennial Census) | Enrollment-Weighted Mean ($\sum E \bar C / \sum E$) | Lower-Bound Student Experience | 18.5 – 20.5 |
| **Teacher-Reported Class Size** | NCES NTPS / SASS | Self-Reported Period / Class Roster | Individual Educator Load | 22.0 – 26.0 |
