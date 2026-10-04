"""
tests/test_project_star_replication.py
Unit and regression tests for Phase 6: Project STAR Causal Microdata Replication.

Verifies:
  1. Microdata provenance, file integrity, and SHA-256 checksums from Harvard Dataverse.
  2. Exact sample counts and cohort structures across Grades K-3.
  3. Experimental randomization balance and baseline covariate orthogonality within schools.
  4. Precise replication of Alan Krueger's (1999, QJE) Table V Model 3 ITT point estimates.
  5. 2SLS (TOT) instrumental variables estimates and first-stage instrument strength.
  6. Grade-by-grade panel attrition and test score missingness bounds.
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

    def test_within_school_orthogonality(self, balance_df):
        cov_rows = balance_df[balance_df["covariate"].isin(["female", "white_asian", "black", "free_lunch_d_k", "birthyear"])]
        
        for _, row in cov_rows.iterrows():
            p_small = float(row["p_val_small"])
            p_aide = float(row["p_val_aide"])
            p_joint = float(row["joint_p_val"])
            
            # All p-values must exceed 0.05 (confirming no statistically significant imbalance)
            assert p_small > 0.05, f"Imbalance detected for {row['covariate']} in Small arm: p={p_small}"
            assert p_aide > 0.05, f"Imbalance detected for {row['covariate']} in Aide arm: p={p_aide}"
            assert p_joint > 0.05, f"Joint imbalance detected for {row['covariate']}: p={p_joint}"


class TestKruegerITTReplication:
    """Verifies exact Krueger (1999) Table V replication benchmarks (Table D02)."""
    
    @pytest.fixture(scope="class")
    def itt_df(self):
        csv_path = os.path.join(TABLES_DIR, "table_d02_krueger_1999_itt_replication.csv")
        return pd.read_csv(csv_path)

    def test_itt_table_exists(self):
        csv_path = os.path.join(TABLES_DIR, "table_d02_krueger_1999_itt_replication.csv")
        assert os.path.exists(csv_path)

    def test_krueger_table_v_model_3_replication(self, itt_df):
        m3_avg = itt_df[
            (itt_df["subject"] == "Average Percentile") &
            (itt_df["model_specification"] == "Model 3 (School FE + Covariates)")
        ]
        
        benchmarks = {
            "K": {"expected": 5.37, "ols_se": 0.75, "aide": 0.26},
            "1": {"expected": 7.85, "ols_se": 0.70, "aide": 1.97},
            "2": {"expected": 5.98, "ols_se": 0.76, "aide": 1.30},
            "3": {"expected": 5.10, "ols_se": 0.80, "aide": -0.16},
        }
        
        for _, row in m3_avg.iterrows():
            g = row["grade"]
            bm = benchmarks[g]
            
            # Point estimate matches published Krueger Table V within 0.01 percentile points
            assert abs(row["small_coef"] - bm["expected"]) <= 0.01, (
                f"Grade {g} Small coef mismatch: {row['small_coef']} vs {bm['expected']}"
            )
            # OLS standard error matches
            assert abs(row["small_ols_se"] - bm["ols_se"]) <= 0.02, (
                f"Grade {g} Small OLS SE mismatch: {row['small_ols_se']} vs {bm['ols_se']}"
            )
            # Aide coefficient matches
            assert abs(row["aide_coef"] - bm["aide"]) <= 0.02, (
                f"Grade {g} Aide coef mismatch: {row['aide_coef']} vs {bm['aide']}"
            )
            # All Small class ITT estimates are highly statistically significant
            assert row["small_p_val"] < 0.001

    def test_clustered_se_exceeds_ols_se(self, itt_df):
        """School-clustered standard errors must be larger than OLS SEs due to intra-school correlation."""
        m3_rows = itt_df[itt_df["model_specification"] == "Model 3 (School FE + Covariates)"]
        for _, row in m3_rows.iterrows():
            assert row["small_clustered_se"] > row["small_ols_se"], (
                f"Clustered SE ({row['small_clustered_se']}) should exceed OLS SE ({row['small_ols_se']})"
            )


class TestNoncomplianceAnd2SLS:
    """Verifies treatment switching, actual class sizes, and 2SLS estimates (Table D03)."""
    
    @pytest.fixture(scope="class")
    def noncomp_df(self):
        csv_path = os.path.join(TABLES_DIR, "table_d03_star_noncompliance_2sls_tot.csv")
        return pd.read_csv(csv_path)

    def test_table_exists(self):
        csv_path = os.path.join(TABLES_DIR, "table_d03_star_noncompliance_2sls_tot.csv")
        assert os.path.exists(csv_path)

    def test_actual_class_size_contrast(self, noncomp_df):
        size_rows = noncomp_df[noncomp_df["panel"] == "Panel B: Actual Class Size Contrast"]
        
        for _, row in size_rows.iterrows():
            small_size = float(row["stat_1_val"])
            reg_size = float(row["stat_2_val"])
            contrast = float(row["stat_4_val"])
            
            # Small class mean should be between 14.5 and 16.5
            assert 14.5 <= small_size <= 16.5, f"Unexpected small class size: {small_size}"
            # Regular class mean should be between 22.0 and 24.5
            assert 22.0 <= reg_size <= 24.5, f"Unexpected regular class size: {reg_size}"
            # Contrast should be between 6.5 and 8.5 students
            assert 6.5 <= contrast <= 8.5, f"Unexpected contrast: {contrast}"

    def test_2sls_estimates(self, noncomp_df):
        iv_rows = noncomp_df[noncomp_df["panel"] == "Panel C: 2SLS Instrumental Variables (TOT)"]
        
        # Kindergarten 2SLS per-student beta should be approx -0.71 (replicates Krueger Table VIII)
        k_iv = iv_rows[iv_rows["grade"] == "K"].iloc[0]
        beta_k = float(k_iv["stat_1_val"])
        f_stat_k = float(k_iv["stat_4_val"])
        
        assert abs(beta_k - (-0.709)) <= 0.02, f"Kindergarten 2SLS beta mismatch: {beta_k}"
        assert f_stat_k > 5000, f"First-stage F-stat too low: {f_stat_k}"


class TestAttritionAndMissingness:
    """Verifies panel attrition bounds and missing test score audits (Table D04)."""
    
    @pytest.fixture(scope="class")
    def attr_df(self):
        csv_path = os.path.join(TABLES_DIR, "table_d04_star_attrition_missingness.csv")
        return pd.read_csv(csv_path)

    def test_table_exists(self):
        csv_path = os.path.join(TABLES_DIR, "table_d04_star_attrition_missingness.csv")
        assert os.path.exists(csv_path)

    def test_differential_attrition_is_small(self, attr_df):
        attr_rows = attr_df[attr_df["panel"] == "Panel A: Cumulative Attrition from K Cohort"]
        
        for _, row in attr_rows.iterrows():
            diff = abs(float(row["differential_attrition_small_vs_reg_pp"]))
            # Differential attrition between Small and Regular must remain below 5.0 percentage points
            assert diff < 5.0, f"Differential attrition too high in {row['grade']}: {diff} pp"

    def test_missing_test_scores_balanced(self, attr_df):
        test_rows = attr_df[attr_df["panel"] == "Panel B: Missing Test Scores (Active Students)"]
        
        for _, row in test_rows.iterrows():
            diff = abs(float(row["differential_attrition_small_vs_reg_pp"]))
            # Differential test missingness between Small and Regular must be below 2.0 percentage points
            assert diff < 2.0, f"Differential test missingness too high in {row['grade']}: {diff} pp"


class TestEvidentiaryScopeBoundaries:
    """
    Verifies that Project STAR causal claims do not exceed experimental support.
    Asserts:
      - Sample is strictly early elementary grades K-3.
      - Class sizes are strictly in the elementary range (11 to 31).
      - No synthetic secondary school or adult tax earnings variables exist.
    """
    
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
