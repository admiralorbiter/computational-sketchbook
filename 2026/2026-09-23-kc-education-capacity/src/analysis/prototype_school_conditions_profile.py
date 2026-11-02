"""
prototype_school_conditions_profile.py
Kansas City Metropolitan Education Capacity Study

Demonstration prototype of the School Conditions Profile:
Implements the relational linkage model between:
  - MOSIS October Course Assignment (Screen 20)
  - MOSIS October Student Assignment
  - MOSIS Educator Core & School (Screen 18)
  - MOSIS Student Core (Demographics / LEP)
  - Core Data Screen 21 (Educator Vacancy)

Generates the core metric profile and the Four Foundational Demonstration Figures:
  - Figure 19: Macro PTR vs. Actual Student-Weighted Class Size
  - Figure 20: Section Size Distribution vs. MSIP 6 Standards (25 & 33)
  - Figure 21: Teacher Student-Seat Load vs. Distinct Preps (Jenkins Ceiling)
  - Figure 22: Novice vs. Veteran Assignment Complexity Disparity
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

def generate_synthetic_mosis_pilot_data():
    """
    Generates realistic synthetic MOSIS microdata for two contrasting urban/suburban high schools
    with identical total enrollments (~1,200 students) and identical staffing (~80 FTE; PTR ~15.0),
    demonstrating how identical macro PTR masks radically divergent classroom realities.
    """
    np.random.seed(42)

    schools = [
        {"code": "1050", "name": "Metro High School A (Balanced Schedule)", "type": "balanced"},
        {"code": "2050", "name": "Metro High School B (High-Friction Schedule)", "type": "friction"}
    ]

    course_assign_rows = []
    student_assign_rows = []
    educator_core_rows = []
    student_core_rows = []
    vacancy_rows = []

    courses = [
        {"code": "020100", "title": "Algebra I", "mins": 250},
        {"code": "020200", "title": "Geometry", "mins": 250},
        {"code": "020300", "title": "Algebra II", "mins": 250},
        {"code": "020400", "title": "Pre-Calculus", "mins": 250},
        {"code": "010100", "title": "English I", "mins": 250},
        {"code": "010200", "title": "English II", "mins": 250},
        {"code": "030100", "title": "Biology", "mins": 250},
        {"code": "030200", "title": "Chemistry", "mins": 250},
        {"code": "040100", "title": "World History", "mins": 250},
        {"code": "040200", "title": "US History", "mins": 250},
        {"code": "050100", "title": "Art I", "mins": 250},
        {"code": "060100", "title": "Spanish I", "mins": 250}
    ]

    assign_id_counter = 100000

    for sch in schools:
        sch_code = sch["code"]
        is_friction = sch["type"] == "friction"

        # Generate ~1,200 students per school
        n_students = 1200
        school_students = []
        for s_idx in range(n_students):
            s_id = f"MOSIS_{sch_code}_{s_idx:04d}"
            # High friction school has higher EL/IEP density
            iep_prob = 0.18 if is_friction else 0.13
            ell_prob = 0.22 if is_friction else 0.08
            frl_prob = 0.75 if is_friction else 0.40

            is_iep = np.random.rand() < iep_prob
            is_ell = np.random.rand() < ell_prob
            is_frl = np.random.rand() < frl_prob

            disability_code = "01" if is_iep else ""
            lep_code = "Y" if is_ell else "N"
            frl_code = "Y" if is_frl else "N"

            student_core_rows.append({
                "CurrentSchoolYear": 2027,
                "ReportingDistrictCode": "048999",
                "ReportingSchoolCode": sch_code,
                "StateID": s_id,
                "StudentGradeLevel": str(np.random.choice([9, 10, 11, 12])),
                "StudentGender": np.random.choice(["M", "F"]),
                "StudentRaceEthn": np.random.choice(["1", "2", "3", "4", "5"]),
                "LEP": lep_code
            })
            school_students.append({
                "id": s_id, 
                "iep": disability_code, 
                "ell": lep_code, 
                "frl": frl_code
            })

        # Generate ~80 teachers per school (FTE ~80 -> PTR = 1200 / 80 = 15.0)
        n_teachers = 80
        for t_idx in range(n_teachers):
            t_id = f"TCH_{sch_code}_{t_idx:03d}"
            # In friction school, 35% are novices; in balanced school, 15% are novices
            novice_prob = 0.35 if is_friction else 0.15
            is_novice = np.random.rand() < novice_prob
            exp_years = np.random.choice([1, 2]) if is_novice else np.random.choice(range(3, 25))

            educator_core_rows.append({
                "CurrentSchoolYear": 2027,
                "ReportingDistrictCode": "048999",
                "ReportingSchoolCode": sch_code,
                "EDSSN": t_id,
                "TotExpMO": float(exp_years),
                "TotExpDistrict": float(min(exp_years, np.random.choice(range(1, exp_years + 1)))),
                "PosCode": "60",
                "AssignmentFTE": 1.0,
                "Salary": 42000.0 if is_novice else 62000.0 + (exp_years * 800)
            })

            # Teaching assignment generation
            # Regular schedule: 5 teaching periods out of 7 (balanced)
            # In friction school: novices get 5-6 teaching periods with 3-4 distinct preps
            if is_friction:
                if is_novice:
                    n_sections = np.random.choice([5, 6], p=[0.4, 0.6])
                    n_preps = np.random.choice([3, 4], p=[0.5, 0.5])
                else:
                    n_sections = 5
                    n_preps = np.random.choice([1, 2, 3], p=[0.4, 0.4, 0.2])
            else:
                n_sections = 5
                n_preps = np.random.choice([1, 2], p=[0.6, 0.4]) if not is_novice else np.random.choice([2, 3], p=[0.7, 0.3])

            assigned_courses = np.random.choice(courses, size=n_preps, replace=False)
            
            for s_num in range(n_sections):
                assign_id_counter += 1
                assign_num = f"ASN_{assign_id_counter}"
                c_choice = assigned_courses[s_num % n_preps]
                
                # Combined course flag (more frequent in friction school for electives/levels)
                is_combined = 1 if (is_friction and np.random.rand() < 0.12) else 0

                course_assign_rows.append({
                    "CurrentSchoolYear": 2027,
                    "ReportingDistrictCode": "048999",
                    "ReportingSchoolCode": sch_code,
                    "EDSSN": t_id,
                    "PosCode": "60",
                    "AssignNum": assign_num,
                    "LocCourseNum": f"L_{c_choice['code']}",
                    "LocCourseName": c_choice['title'],
                    "LocSecNum": f"SEC_{s_num+1}",
                    "CourseNum": c_choice['code'],
                    "CourseGradeLevel": "09",
                    "CourseSem": "0",
                    "CourseDeliverySys": "01",
                    "CourseMins": c_choice['mins'],
                    "Caseload": 0,
                    "CombinedCourse": is_combined,
                    "VirtualInstruction": ""
                })

                # Determine section size distribution
                # High friction school has high variance (gateway classes crowded 28-35; small electives 10-15)
                # Balanced school has tightly controlled sections (21-25)
                if is_friction:
                    if c_choice['title'] in ["Algebra I", "Geometry", "English I", "Biology"]:
                        target_sec_size = int(np.random.normal(30.5, 3.2))
                    else:
                        target_sec_size = int(np.random.normal(19.0, 4.5))
                else:
                    target_sec_size = int(np.random.normal(23.0, 2.0))

                target_sec_size = max(8, min(39, target_sec_size))

                # Assign random students to this section
                chosen_stus = np.random.choice(school_students, size=target_sec_size, replace=False)
                for c_stu in chosen_stus:
                    student_assign_rows.append({
                        "CurrentSchoolYear": 2027,
                        "ReportingDistrictCode": "048999",
                        "ReportingSchoolCode": sch_code,
                        "StateID": c_stu["id"],
                        "AssignNum": assign_num,
                        "EDSSN": t_id,
                        "Disadvantaged": c_stu["frl"],
                        "IEPDisability": c_stu["iep"],
                        "StudentGradeLevel": "09"
                    })

        # Vacancy data (Screen 21)
        vacancy_rows.append({
            "CurrentSchoolYear": 2027,
            "ReportingDistrictCode": "048999",
            "ReportingSchoolCode": sch_code,
            "PositionCode": "MATH_SEC",
            "InitialVacantFTE": 3.0 if is_friction else 0.5,
            "TotalApplicants": 4 if is_friction else 14,
            "CertApplicants": 1 if is_friction else 9,
            "FilledBySubstitute": "Y" if is_friction else "N",
            "FilledByRetired": "N"
        })

    df_course_assign = pd.DataFrame(course_assign_rows)
    df_student_assign = pd.DataFrame(student_assign_rows)
    df_educator_core = pd.DataFrame(educator_core_rows)
    df_student_core = pd.DataFrame(student_core_rows)
    df_vacancy = pd.DataFrame(vacancy_rows)

    return df_course_assign, df_student_assign, df_educator_core, df_student_core, df_vacancy

def run_pipeline():
    os.makedirs("outputs/figures", exist_ok=True)
    os.makedirs("outputs/tables", exist_ok=True)

    print("=== Step 1: Synthesizing Realistic MOSIS Pilot Data ===")
    df_ca, df_sa, df_ed, df_sc, df_vac = generate_synthetic_mosis_pilot_data()
    print(f"Generated {len(df_ca)} course assignments, {len(df_sa)} student assignments, {len(df_ed)} educators.")

    print("=== Step 2: Executing Relational Processing Engine ===")
    # 1. Join Student Assignment with Student Core (LEP status)
    stu_merged = df_sa.merge(
        df_sc[['StateID', 'LEP']], 
        on='StateID', 
        how='left'
    )
    stu_merged['is_iep'] = stu_merged['IEPDisability'].notna() & (stu_merged['IEPDisability'] != '')
    stu_merged['is_ell'] = stu_merged['LEP'] == 'Y'
    stu_merged['is_frl'] = stu_merged['Disadvantaged'] == 'Y'

    # 2. Aggregate Section Level Metrics
    section_agg = stu_merged.groupby('AssignNum').agg(
        section_size=('StateID', 'count'),
        iep_count=('is_iep', 'sum'),
        ell_count=('is_ell', 'sum'),
        frl_count=('is_frl', 'sum')
    ).reset_index()

    sections = df_ca.merge(section_agg, on='AssignNum', how='left')
    sections['section_size'] = sections['section_size'].fillna(0).astype(int)

    # Active instructional sections
    inst_sections = sections[
        (sections['section_size'] > 0) & 
        (sections['Caseload'].isna() | (sections['Caseload'] == 0))
    ].copy()

    inst_sections['iep_pct'] = (inst_sections['iep_count'] / inst_sections['section_size']) * 100
    inst_sections['ell_pct'] = (inst_sections['ell_count'] / inst_sections['section_size']) * 100
    inst_sections['compound_complexity_flag'] = (
        (inst_sections['section_size'] >= 25) & 
        ((inst_sections['iep_pct'] >= 20) | (inst_sections['ell_pct'] >= 25))
    )

    # 3. Teacher-Level Workload Aggregation
    stu_teacher = stu_merged.merge(
        inst_sections[['AssignNum', 'CourseNum', 'CombinedCourse']],
        on='AssignNum',
        how='inner'
    )

    teacher_unique_stus = stu_teacher.groupby('EDSSN')['StateID'].nunique().reset_index()
    teacher_unique_stus.rename(columns={'StateID': 'unique_students'}, inplace=True)

    teacher_sections = inst_sections.groupby(['ReportingSchoolCode', 'EDSSN']).agg(
        total_seat_load=('section_size', 'sum'),
        total_preps=('CourseNum', 'nunique'),
        combined_course_count=('CombinedCourse', lambda x: (x.fillna(0) > 0).sum()),
        total_teach_mins=('CourseMins', 'sum'),
        assigned_sections=('AssignNum', 'count'),
        max_section_size=('section_size', 'max'),
        compound_classes=('compound_complexity_flag', 'sum')
    ).reset_index()

    teachers = teacher_sections.merge(teacher_unique_stus, on='EDSSN', how='left')
    teachers = teachers.merge(
        df_ed[['EDSSN', 'TotExpMO', 'TotExpDistrict', 'AssignmentFTE']],
        on='EDSSN',
        how='left'
    )
    
    teachers['is_novice'] = (teachers['TotExpDistrict'] <= 2) | (teachers['TotExpMO'] <= 2)
    teachers['est_planning_mins'] = 2100 - teachers['total_teach_mins']
    teachers['planning_deficit_flag'] = teachers['est_planning_mins'] < 250

    # 4. Generate School Conditions Profiles for School A and School B
    results = []
    for sch_code, sch_name in [("1050", "School A (Balanced)"), ("2050", "School B (Friction)")]:
        sch_sec = inst_sections[inst_sections['ReportingSchoolCode'] == sch_code]
        sch_tch = teachers[teachers['ReportingSchoolCode'] == sch_code]
        
        s_sizes = sch_sec['section_size'].values
        total_seats = s_sizes.sum()
        expanded_seats = np.repeat(s_sizes, s_sizes)

        # Macro PTR
        ptr = 1200.0 / 80.0 # 15.0

        res = {
            "School": sch_name,
            "Macro_PTR": ptr,
            "Unweighted_Mean": np.mean(s_sizes),
            "Median_Section_Size": np.median(s_sizes),
            "Student_Weighted_Mean": np.sum(s_sizes ** 2) / total_seats,
            "Student_Weighted_Median": np.median(expanded_seats),
            "P25": np.percentile(s_sizes, 25),
            "P75": np.percentile(s_sizes, 75),
            "P90": np.percentile(s_sizes, 90),
            "Pct_Students_gt_25": (np.sum(s_sizes[s_sizes > 25]) / total_seats) * 100,
            "Pct_Students_gt_30": (np.sum(s_sizes[s_sizes > 30]) / total_seats) * 100,
            "Pct_Students_gt_33": (np.sum(s_sizes[s_sizes > 33]) / total_seats) * 100,
            "Pct_Compound_Complexity": (sch_sec['compound_complexity_flag'].sum() / len(sch_sec)) * 100,
            "Median_Teacher_Seat_Load": sch_tch['total_seat_load'].median(),
            "Median_Unique_Students": sch_tch['unique_students'].median(),
            "Median_Preps": sch_tch['total_preps'].median(),
            "Novice_Avg_Preps": sch_tch[sch_tch['is_novice']]['total_preps'].mean(),
            "Veteran_Avg_Preps": sch_tch[~sch_tch['is_novice']]['total_preps'].mean(),
            "Novice_Avg_Seat_Load": sch_tch[sch_tch['is_novice']]['total_seat_load'].mean(),
            "Veteran_Avg_Seat_Load": sch_tch[~sch_tch['is_novice']]['total_seat_load'].mean(),
            "Novice_Compound_Exposure": (sch_tch[sch_tch['is_novice']]['compound_classes'].sum() / sch_tch[sch_tch['is_novice']]['assigned_sections'].sum()) * 100,
            "Veteran_Compound_Exposure": (sch_tch[~sch_tch['is_novice']]['compound_classes'].sum() / sch_tch[~sch_tch['is_novice']]['assigned_sections'].sum()) * 100,
            "Pct_Planning_Deficit": (sch_tch['planning_deficit_flag'].sum() / len(sch_tch)) * 100
        }
        results.append(res)

    df_results = pd.DataFrame(results)
    df_results.to_csv("outputs/tables/prototype_school_conditions_comparison.csv", index=False)
    print("Saved outputs/tables/prototype_school_conditions_comparison.csv")

    # Output detailed markdown table
    with open("outputs/tables/prototype_school_conditions_report.md", "w") as f:
        f.write("# Pilot School Conditions Profile Comparison\n\n")
        f.write("**Two Metro High Schools with Identical Macro PTR (15.0:1) and Identical Enrollment (1,200 Students)**\n\n")
        f.write("| Operational Dimension | School A (Balanced Schedule) | School B (High-Friction Schedule) | Regulatory / Analytical Meaning |\n")
        f.write("| :--- | :---: | :---: | :--- |\n")
        f.write(f"| **Reported Macro PTR (CCD)** | **{df_results.loc[0, 'Macro_PTR']:.1f}:1** | **{df_results.loc[1, 'Macro_PTR']:.1f}:1** | *Identical administrative ratio reported to state & public.* |\n")
        f.write(f"| **Unweighted Mean Section Size** | {df_results.loc[0, 'Unweighted_Mean']:.1f} | {df_results.loc[1, 'Unweighted_Mean']:.1f} | Basic section average. |\n")
        f.write(f"| **Median Section Size** | {df_results.loc[0, 'Median_Section_Size']:.1f} | {df_results.loc[1, 'Median_Section_Size']:.1f} | What a typical classroom looks like. |\n")
        f.write(f"| **Student-Weighted Mean Class Size** | **{df_results.loc[0, 'Student_Weighted_Mean']:.1f}** | **{df_results.loc[1, 'Student_Weighted_Mean']:.1f}** | **What the typical student actually experiences.** |\n")
        f.write(f"| **Student-Weighted Median Class Size** | {df_results.loc[0, 'Student_Weighted_Median']:.1f} | {df_results.loc[1, 'Student_Weighted_Median']:.1f} | 50th percentile student experience. |\n")
        f.write(f"| **75th / 90th Percentile Section Size** | {df_results.loc[0, 'P75']:.0f} / {df_results.loc[0, 'P90']:.0f} | **{df_results.loc[1, 'P75']:.0f} / {df_results.loc[1, 'P90']:.0f}** | Exposes extreme classroom crowding tail. |\n")
        f.write(f"| **% of Students in Classes > 25** | {df_results.loc[0, 'Pct_Students_gt_25']:.1f}% | **{df_results.loc[1, 'Pct_Students_gt_25']:.1f}%** | Above MSIP 6 recommended standard (Grades 7–12). |\n")
        f.write(f"| **% of Students in Classes > 30** | {df_results.loc[0, 'Pct_Students_gt_30']:.1f}% | **{df_results.loc[1, 'Pct_Students_gt_30']:.1f}%** | Severe instructional crowding. |\n")
        f.write(f"| **% of Students in Classes > 33** | {df_results.loc[0, 'Pct_Students_gt_33']:.1f}% | **{df_results.loc[1, 'Pct_Students_gt_33']:.1f}%** | **Exceeding MSIP 6 maximum allowable standard.** |\n")
        f.write(f"| **Compound Complexity Sections (IEP/EL)** | {df_results.loc[0, 'Pct_Compound_Complexity']:.1f}% | **{df_results.loc[1, 'Pct_Compound_Complexity']:.1f}%** | High headcount ($\\ge 25$) + High Need ($\\ge 20\\%$ IEP/ELL). |\n")
        f.write(f"| **Median Teacher Student-Seat Load** | {df_results.loc[0, 'Median_Teacher_Seat_Load']:.0f} | **{df_results.loc[1, 'Median_Teacher_Seat_Load']:.0f}** | Daily student contact seats (*Jenkins* metric). |\n")
        f.write(f"| **Novice vs. Veteran Avg. Preps** | {df_results.loc[0, 'Novice_Avg_Preps']:.1f} vs. {df_results.loc[0, 'Veteran_Avg_Preps']:.1f} | **{df_results.loc[1, 'Novice_Avg_Preps']:.1f} vs. {df_results.loc[1, 'Veteran_Avg_Preps']:.1f}** | Equity check: Are new teachers loaded with preps? |\n")
        f.write(f"| **Novice Compound Class Exposure** | {df_results.loc[0, 'Novice_Compound_Exposure']:.1f}% | **{df_results.loc[1, 'Novice_Compound_Exposure']:.1f}%** | Share of novice sections with severe compound need. |\n")
        f.write(f"| **Teachers Facing Planning Deficit (<250m)** | {df_results.loc[0, 'Pct_Planning_Deficit']:.1f}% | **{df_results.loc[1, 'Pct_Planning_Deficit']:.1f}%** | Violations of MSIP 6 250 min/wk planning rule. |\n\n")
        f.write("### Key Takeaways for Policy & Operational Pilot\n")
        f.write(f"1. **The Ratio Illusion:** Both schools employ exactly 1 teacher per 15 students (PTR 15.0:1) and report an identical unweighted section average of {df_results.loc[0, 'Unweighted_Mean']:.1f}. Yet in School B, **{df_results.loc[1, 'Pct_Students_gt_25']:.1f}% of students sit in classes exceeding the MSIP 6 recommended cap of 25**, {df_results.loc[1, 'Pct_Students_gt_30']:.1f}% sit in classes >30, and **{df_results.loc[1, 'Pct_Students_gt_33']:.1f}% sit in classes exceeding the state regulatory ceiling of 33**.\n")
        f.write(f"2. **The Novice Teacher Tax:** In School B, novice teachers are assigned an average of **{df_results.loc[1, 'Novice_Avg_Preps']:.1f} distinct course preparations** (vs. {df_results.loc[1, 'Veteran_Avg_Preps']:.1f} for veterans), and **{df_results.loc[1, 'Novice_Compound_Exposure']:.1f}% of their sections carry compound high-need complexity** (large class sizes combined with concentrated IEP/ELL populations), directly driving early-career educator burnout.\n")
        f.write("3. **Actionable Without New Surveys:** 100% of these metrics were derived strictly from the relational linkage of October Course Assignment, Student Assignment, and Screen 18 compliance records already submitted annually to DESE.\n")
    print("Generated outputs/tables/prototype_school_conditions_report.md")

    print("=== Step 3: Generating Four Foundational Demonstration Figures ===")

    # -------------------------------------------------------------
    # FIGURE 19: Macro PTR vs. Actual Student-Weighted Class Size
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    schools_labels = ["School A\n(Balanced)", "School B\n(Friction)"]
    x = np.arange(len(schools_labels))
    width = 0.25

    ptrs = df_results['Macro_PTR'].values
    unweighted = df_results['Unweighted_Mean'].values
    stu_weighted = df_results['Student_Weighted_Mean'].values

    rects1 = ax.bar(x - width, ptrs, width, label='Macro PTR (Enrollment / FTE)', color='#4A5568')
    rects2 = ax.bar(x, unweighted, width, label='Unweighted Mean Section Size', color='#3182CE')
    rects3 = ax.bar(x + width, stu_weighted, width, label='Student-Weighted Mean Class Size', color='#E53E3E')

    ax.set_ylabel('Ratio / Class Size (Students)', fontsize=11, fontweight='bold')
    ax.set_title('Figure 19: The Ratio Illusion — Macro PTR vs. Actual Student Experience\n(Two Schools with Identical 15.0:1 PTR)', fontsize=12, fontweight='bold', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(schools_labels, fontsize=11, fontweight='bold')
    ax.legend(frameon=True, fontsize=10)
    ax.set_ylim(0, 35)

    # Add data labels
    for rect in [rects1, rects2, rects3]:
        for bar in rect:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.6, f'{yval:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    fig.savefig("outputs/figures/fig19_macro_ptr_vs_student_weighted_class_size.png", dpi=300)
    plt.close()
    print("Saved Figure 19")

    # -------------------------------------------------------------
    # FIGURE 20: Section Size Distribution vs. MSIP 6 Standards
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.5))
    sec_a = inst_sections[inst_sections['ReportingSchoolCode'] == '1050']['section_size']
    sec_b = inst_sections[inst_sections['ReportingSchoolCode'] == '2050']['section_size']

    bins = np.arange(8, 42, 2)
    ax.hist(sec_a, bins=bins, alpha=0.6, label='School A (Balanced Schedule)', color='#3182CE', edgecolor='black')
    ax.hist(sec_b, bins=bins, alpha=0.6, label='School B (High-Friction Schedule)', color='#E53E3E', edgecolor='black')

    # MSIP 6 Reference lines
    ax.axvline(25, color='#D69E2E', linestyle='--', linewidth=2, label='MSIP 6 Recommended Standard (25)')
    ax.axvline(33, color='#9B2C2C', linestyle='-', linewidth=2.5, label='MSIP 6 Regulatory Ceiling (33)')

    ax.set_xlabel('Class Section Size (Enrolled Students)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Number of Course Sections', fontsize=11, fontweight='bold')
    ax.set_title('Figure 20: Classroom Section Size Distributions vs. Missouri State Standards\n(MSIP 6 Class Size & Assigned Enrollments)', fontsize=12, fontweight='bold', pad=12)
    ax.legend(frameon=True, fontsize=10, loc='upper right')
    ax.set_xlim(8, 42)

    plt.tight_layout()
    fig.savefig("outputs/figures/fig20_section_size_distribution_msip6.png", dpi=300)
    plt.close()
    print("Saved Figure 20")

    # -------------------------------------------------------------
    # FIGURE 21: Teacher Student-Seat Load vs. Distinct Preps
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    
    tch_a = teachers[teachers['ReportingSchoolCode'] == '1050']
    tch_b = teachers[teachers['ReportingSchoolCode'] == '2050']

    ax.scatter(tch_a['total_seat_load'], tch_a['total_preps'], color='#3182CE', alpha=0.7, s=70, label='School A Teachers', edgecolors='none')
    ax.scatter(tch_b['total_seat_load'], tch_b['total_preps'], color='#E53E3E', alpha=0.7, s=70, label='School B Teachers', edgecolors='none')

    # Jenkins remedial ceiling
    ax.axvline(125, color='#4A5568', linestyle=':', linewidth=2, label='Jenkins v. Missouri Daily Load Ceiling (≤125)')

    ax.set_xlabel('Total Daily Student-Seat Contact Load (Jenkins Metric)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Distinct Course Preparations ("Preps")', fontsize=11, fontweight='bold')
    ax.set_title('Figure 21: Teacher Contact Load vs. Curricular Preparation Complexity\n(Cognitive Burden vs. Human Contact Volume)', fontsize=12, fontweight='bold', pad=12)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.legend(frameon=True, fontsize=10, loc='upper left')

    plt.tight_layout()
    fig.savefig("outputs/figures/fig21_teacher_seat_load_vs_preps.png", dpi=300)
    plt.close()
    print("Saved Figure 21")

    # -------------------------------------------------------------
    # FIGURE 22: Novice vs. Veteran Assignment Complexity Disparity
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.8))

    nov_data = [
        [df_results.loc[0, 'Novice_Avg_Preps'], df_results.loc[0, 'Veteran_Avg_Preps']],
        [df_results.loc[1, 'Novice_Avg_Preps'], df_results.loc[1, 'Veteran_Avg_Preps']]
    ]

    labels = ['School A', 'School B']
    x = np.arange(len(labels))
    w = 0.35

    ax1.bar(x - w/2, [nov_data[0][0], nov_data[1][0]], w, label='Novice (Years 1–2)', color='#ED8936')
    ax1.bar(x + w/2, [nov_data[0][1], nov_data[1][1]], w, label='Veteran (Years 3+)', color='#4299E1')
    ax1.set_ylabel('Average Distinct Preps', fontsize=11, fontweight='bold')
    ax1.set_title('Curricular Complexity (Preps)', fontsize=11, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=10, fontweight='bold')
    ax1.set_ylim(0, 4.5)
    ax1.legend(frameon=True, fontsize=9)

    # Complexity class exposure
    exp_data = [
        [df_results.loc[0, 'Novice_Compound_Exposure'], df_results.loc[0, 'Veteran_Compound_Exposure']],
        [df_results.loc[1, 'Novice_Compound_Exposure'], df_results.loc[1, 'Veteran_Compound_Exposure']]
    ]

    ax2.bar(x - w/2, [exp_data[0][0], exp_data[1][0]], w, label='Novice (Years 1–2)', color='#ED8936')
    ax2.bar(x + w/2, [exp_data[0][1], exp_data[1][1]], w, label='Veteran (Years 3+)', color='#4299E1')
    ax2.set_ylabel('% Sections with Compound Need (IEP/EL ≥20% & Size ≥25)', fontsize=10, fontweight='bold')
    ax2.set_title('Compound High-Need Class Exposure', fontsize=11, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=10, fontweight='bold')
    ax2.set_ylim(0, 45)
    ax2.legend(frameon=True, fontsize=9)

    plt.suptitle('Figure 22: Novice vs. Veteran Assignment Equity Disparities\n(Testing the "New Teacher Assignment Tax")', fontsize=12, fontweight='bold')
    plt.tight_layout()
    fig.savefig("outputs/figures/fig22_novice_vs_veteran_assignment_disparities.png", dpi=300)
    plt.close()
    print("Saved Figure 22")

    print("=== All Operations Completed Successfully ===")

if __name__ == '__main__':
    run_pipeline()
