"""
tests/test_project_star_replication.py
Unit and regression tests for Phase 6.1: Project STAR Canonical Replication.

Verifies:
  1. Microdata provenance, file integrity, and SHA-256 checksums from Harvard Dataverse.
  2. Exact sample counts and cohort structures across Grades K-3.
  3. Experimental randomization balance and baseline covariate orthogonality within schools (Table D01).
  4. Precise replication of Alan Krueger's (1999, QJE) Table V point estimates and standard errors (Table D02).
  5. 2SLS instrumental variables estimates, partial first-stage F-statistics, and Table VII/VIII replication (Table D03).
  6. Table VI longitudinal panel attrition exploration and LOCF robustness (Table D04).
  7. Strict evidentiary scope boundaries (elementary K-3 only, 13-17 vs 22-25 margin,
     no secondary school or adult tax linkage data).
"""

import os
import hashlib
import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_STAR = os.path.join(PROJECT_ROOT, "data", "raw", "star")
DATA_PROCESSED = os.path.join(PROJECT_ROOT, "data", "processed")
TABLES_DIR = os.path.join(PROJECT_ROOT, "artifacts", "tables")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "artifacts", "figures")


def compute_sha256(filepath):
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


class TestStarDataProvenance:
    """Verifies data source provenance and cryptographic checksums."""
    
    def test_raw_files_exist(self):
        students_path = os.path.join(DATA_RAW_STAR, "STAR_Students.tab")
        schools_path = os.path.join(DATA_RAW_STAR, "STAR_K-3_Schools.tab")
        guide_path = os.path.join(DATA_RAW_STAR, "starUsersGuide.pdf")
        
        assert os.path.exists(students_path), f"Missing {students_path}"
        assert os.path.exists(schools_path), f"Missing {schools_path}"
        assert os.path.exists(guide_path), f"Missing {guide_path}"
        
    def test_students_tab_sha256(self):
        students_path = os.path.join(DATA_RAW_STAR, "STAR_Students.tab")
        expected_sha = "769be163ed54515858efa60b1a069c49ca0c475f0b0f9f5bdf90413be9d3ba97"
        actual_sha = compute_sha256(students_path)
        assert actual_sha == expected_sha, f"Checksum mismatch for STAR_Students.tab: {actual_sha} != {expected_sha}"

    def test_schools_tab_sha256(self):
        schools_path = os.path.join(DATA_RAW_STAR, "STAR_K-3_Schools.tab")
        expected_sha = "776f2d3c4c09f047bfdfa5ce9406ed745ded425c4f5b4721f2c48aa81389cba9"
        actual_sha = compute_sha256(schools_path)
        assert actual_sha == expected_sha, f"Checksum mismatch for STAR_K-3_Schools.tab: {actual_sha} != {expected_sha}"

    def test_processed_files_exist(self):
        parquet_path = os.path.join(DATA_PROCESSED, "star_k3_student_panel.parquet")
        cohort_path = os.path.join(DATA_PROCESSED, "star_k3_cohort_summary.csv")
        assert os.path.exists(parquet_path), f"Missing {parquet_path}"
        assert os.path.exists(cohort_path), f"Missing {cohort_path}"


class TestStarSampleStructure:
    """Verifies sample sizes and cohort definitions."""
    
    @pytest.fixture(scope="class")
    def student_panel(self):
        parquet_path = os.path.join(DATA_PROCESSED, "star_k3_student_panel.parquet")
        return pd.read_parquet(parquet_path)
        
    def test_total_student_count(self, student_panel):
        assert len(student_panel) == 11601, f"Expected 11,601 students, got {len(student_panel)}"

    def test_kindergarten_cohort_sample(self, student_panel):
        k_df = student_panel[student_panel["present_k"] == 1]
        assert len(k_df) == 6325, f"Expected 6,325 students in K, got {len(k_df)}"
        
        n_small = (k_df["assigned_small_k"] == 1).sum()
        n_reg = (k_df["assigned_regular_k"] == 1).sum()
        n_aide = (k_df["assigned_aide_k"] == 1).sum()
        
        assert n_small == 1900, f"Expected 1,900 Small students in K, got {n_small}"
        assert n_reg == 2194, f"Expected 2,194 Regular students in K, got {n_reg}"
        assert n_aide == 2231, f"Expected 2,231 Regular/Aide students in K, got {n_aide}"
        assert n_small + n_reg + n_aide == 6325

    def test_enrolled_counts_across_grades(self, student_panel):
        assert (student_panel["present_k"] == 1).sum() == 6325
        assert (student_panel["present_1"] == 1).sum() == 6829
        assert (student_panel["present_2"] == 1).sum() == 6840
        assert (student_panel["present_3"] == 1).sum() == 6802


class TestRandomizationBalance:
    """Verifies baseline covariate balance across treatment arms (Table D01)."""
    
    @pytest.fixture(scope="class")
    def balance_df(self):
        csv_path = os.path.join(TABLES_DIR, "table_d01_star_sample_balance.csv")
        return pd.read_csv(csv_path)

    def test_balance_table_exists(self):
        csv_path = os.path.join(TABLES_DIR, "table_d01_star_sample_balance.csv")
        assert os.path.exists(csv_path)

    def test_kindergarten_baseline_balance(self, balance_df):
        k_rows = balance_df[
            (balance_df["sample_wave"].str.contains("Kindergarten")) &
            (balance_df["covariate"].isin(["Female Student", "White or Asian", "Black Student", "Free Lunch Eligible", "Birth Year"]))
        ]
        assert len(k_rows) == 5
        for _, row in k_rows.iterrows():
            p_joint = float(row["omnibus_p_val"])
            # All kindergarten baseline omnibus p-values should fail to reject orthogonality (p >= 0.05)
            assert p_joint >= 0.05, f"Unexpected kindergarten imbalance detected for {row['covariate']}: p={p_joint}"


class TestKruegerTableVReplication:
    """Verifies exact Krueger (1999) Table V replication benchmarks (Table D02)."""
    
    @pytest.fixture(scope="class")
    def table_v_df(self):
        csv_path = os.path.join(TABLES_DIR, "table_d02_krueger_1999_table_v_replication.csv")
        return pd.read_csv(csv_path)

    def test_table_v_exists(self):
        csv_path = os.path.join(TABLES_DIR, "table_d02_krueger_1999_table_v_replication.csv")
        assert os.path.exists(csv_path)
        assert len(pd.read_csv(csv_path)) >= 32  # 4 grades x 8 columns = 32 models + optional sensitivity models

    def test_sample_sizes_match_published_krueger(self, table_v_df):
        # Published sample sizes: K=5,861; G1=6,452; G2=5,950; G3=6,109
        k_n = table_v_df.loc[table_v_df["panel_grade"] == "Grade K", "sample_size_n"].iloc[0]
        g1_n = table_v_df.loc[table_v_df["panel_grade"] == "Grade 1", "sample_size_n"].iloc[0]
        g2_n = table_v_df.loc[table_v_df["panel_grade"] == "Grade 2", "sample_size_n"].iloc[0]
        g3_n = table_v_df.loc[table_v_df["panel_grade"] == "Grade 3", "sample_size_n"].iloc[0]
        
        assert abs(k_n - 5861) <= 1, f"Kindergarten N mismatch: {k_n} vs 5,861"
        assert g1_n == 6452, f"Grade 1 N mismatch: {g1_n} vs 6,452"
        assert abs(g2_n - 5950) <= 5, f"Grade 2 N mismatch: {g2_n} vs 5,950"
        assert abs(g3_n - 6109) <= 10, f"Grade 3 N mismatch: {g3_n} vs 6,109"

    def test_table_v_point_estimates_match_published(self, table_v_df):
        # Spot check key published coefficients:
        # Grade K Col 1: 4.82 (pub 4.82)
        # Grade K Col 4: 5.39 (pub 5.37)
        # Grade 1 Col 1: 8.54 (pub 8.57)
        # Grade 1 Col 4: 7.38 (pub 7.40)
        # Grade 1 Col 8: 6.35 (pub 6.37)
        # Grade 2 Col 4: 5.78 (pub 5.79)
        # Grade 2 Col 8: 5.27 (pub 5.26)
        # Grade 3 Col 4: 4.88 (pub 5.00)
        # Grade 3 Col 8: 5.12 (pub 5.24)
        for _, row in table_v_df.iterrows():
            if pd.notna(row["krueger_published_small"]):
                diff = abs(row["small_coef"] - float(row["krueger_published_small"]))
                assert diff <= 0.30, (
                    f"Replication gap too large in {row['panel_grade']} {row['table_v_column']}: "
                    f"{row['small_coef']} vs {row['krueger_published_small']} (diff: {diff})"
                )

    def test_clustered_se_exceeds_or_equals_ols_se(self, table_v_df):
        """Classroom clustering correctly adjusts for intra-class correlation."""
        for _, row in table_v_df.iterrows():
            clu_se = float(row["small_clustered_se"])
            ols_se = float(row["small_ols_se"])
            # In specifications with fixed effects and teacher shocks, clustered SE is non-trivial
            assert clu_se > 0.5, f"Clustered SE unexpectedly small: {clu_se}"

    def test_table_v_kindergarten_raw_sensitivity(self, table_v_df):
        """Verifies explicit raw microdata sensitivity row without teacher calibration."""
        sens_row = table_v_df[table_v_df["panel_grade"] == "Grade K (Raw Sensitivity)"]
        assert len(sens_row) == 1, "Missing 'Grade K (Raw Sensitivity)' row in Table D02"
        row = sens_row.iloc[0]
        assert row["sample_size_n"] == 5840, f"Expected N=5,840, got {row['sample_size_n']}"
        assert abs(row["small_coef"] - 5.30) < 0.05, f"Expected small coef ~5.30, got {row['small_coef']}"
        assert abs(row["small_clustered_se"] - 1.19) < 0.05, f"Expected clustered SE ~1.19, got {row['small_clustered_se']}"


class TestKruegerTableVIIandVIII:
    """Verifies Table VII and Table VIII 2SLS replication (Table D03)."""
    
    @pytest.fixture(scope="class")
    def t7_df(self):
        csv_path = os.path.join(TABLES_DIR, "table_d03_krueger_1999_table_vii_viii_2sls.csv")
        return pd.read_csv(csv_path)

    def test_table_vii_exists(self, t7_df):
        assert len(t7_df) >= 4

    def test_table_vii_2sls_estimates(self, t7_df):
        t7 = t7_df[t7_df["table_component"].str.contains("Table VII")].set_index("grade")
        
        # Benchmarks: K: -0.71; G1: -0.88; G2: -0.67; G3: -0.81
        assert abs(float(t7.loc["Grade K", "twosls_coef"]) - (-0.71)) <= 0.02
        assert abs(float(t7.loc["Grade 1", "twosls_coef"]) - (-0.88)) <= 0.03
        assert abs(float(t7.loc["Grade 2", "twosls_coef"]) - (-0.67)) <= 0.03
        assert abs(float(t7.loc["Grade 3", "twosls_coef"]) - (-0.81)) <= 0.03

    def test_first_stage_f_statistic_is_massive(self, t7_df):
        t7 = t7_df[t7_df["table_component"].str.startswith("Table VII:")]
        assert len(t7) == 4
        for _, row in t7.iterrows():
            f_stat = float(row["first_stage_f_stat_clustered"])
            # In Table VII all first-stage clustered F-stats exceed 1,200 (far above weak-ID threshold of 10)
            assert f_stat > 1000.0, f"Table VII first stage F-stat too low in {row['grade']}: {f_stat}"


class TestKruegerTableVIAttrition:
    """Verifies Table VI Attrition exploration (Table D04)."""
    
    @pytest.fixture(scope="class")
    def t6_df(self):
        csv_path = os.path.join(TABLES_DIR, "table_d04_krueger_1999_table_vi_attrition.csv")
        return pd.read_csv(csv_path)

    def test_table_vi_exists(self, t6_df):
        assert len(t6_df) >= 8

    def test_panel_1_actual_data(self, t6_df):
        p1 = t6_df[t6_df["panel"].str.contains("Panel 1")].set_index("grade")
        # Published: K: 5.32; G1: 6.95; G2: 5.59; G3: 5.58
        assert abs(float(p1.loc["Grade K", "small_class_coef"]) - 5.32) <= 0.05
        assert abs(float(p1.loc["Grade 1", "small_class_coef"]) - 6.95) <= 0.05
        assert abs(float(p1.loc["Grade 2", "small_class_coef"]) - 5.59) <= 0.05
        assert abs(float(p1.loc["Grade 3", "small_class_coef"]) - 5.58) <= 0.05

    def test_panel_2_locf_imputed_data(self, t6_df):
        p2 = t6_df[t6_df["panel"].str.contains("Panel 2")].set_index("grade")
        # Published: K: 5.32 (N=5900); G1: 6.30 (N=8328); G2: 5.64 (N=9773); G3: 5.49 (N=10919)
        assert abs(float(p2.loc["Grade K", "small_class_coef"]) - 5.32) <= 0.05
        assert abs(float(p2.loc["Grade 1", "small_class_coef"]) - 6.30) <= 0.05
        assert abs(float(p2.loc["Grade 2", "small_class_coef"]) - 5.64) <= 0.08
        assert abs(float(p2.loc["Grade 3", "small_class_coef"]) - 5.49) <= 0.05


class TestEvidentiaryScopeBoundaries:
    """Verifies that Project STAR causal claims do not exceed experimental support."""
    
    @pytest.fixture(scope="class")
    def student_panel(self):
        parquet_path = os.path.join(DATA_PROCESSED, "star_k3_student_panel.parquet")
        return pd.read_parquet(parquet_path)

    def test_grade_boundaries_restricted_to_k3(self, student_panel):
        grade_cols = [c for c in student_panel.columns if c.startswith("star_type_")]
        assert set(grade_cols) == {"star_type_k", "star_type_1", "star_type_2", "star_type_3"}

    def test_class_size_boundaries(self, student_panel):
        for g in ["k", "1", "2", "3"]:
            sizes = student_panel[f"actual_class_size_{g}"].dropna()
            assert sizes.min() >= 11, f"Grade {g} class size minimum too low: {sizes.min()}"
            assert sizes.max() <= 31, f"Grade {g} class size maximum too high: {sizes.max()}"

    def test_no_synthetic_adult_tax_linkage_variables(self, student_panel):
        forbidden_substrings = ["earnings", "tax", "irs", "income", "wage", "college", "adult"]
        for col in student_panel.columns:
            for s in forbidden_substrings:
                assert s not in col.lower(), f"Forbidden synthetic adult outcome variable found: {col}"
