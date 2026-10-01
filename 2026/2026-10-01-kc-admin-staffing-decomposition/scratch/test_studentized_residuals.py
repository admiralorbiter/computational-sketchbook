"""
Test studentized residuals and scale-normalized residuals for peer models.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "processed" / "district_demand_year.parquet"
df = pd.read_parquet(DATA_PATH)

def run_peer_model(dep_var, indep_vars, model_name, start_year="2014-2015", end_year="2023-2024"):
    sub = df[(df["school_year"] >= start_year) & (df["school_year"] <= end_year) & (df["is_balanced_presence_cohort_55"] == 1)].copy()
    sub["enrollment_1k"] = sub["enrollment_total"] / 1000.0
    sub["teachers_100"] = sub["teachers_k12_fte"] / 100.0
    sub = sub.dropna(subset=[dep_var] + indep_vars).copy()
    sub["state_year"] = sub["state"] + "_" + sub["school_year"]
    dummies = pd.get_dummies(sub["state_year"], drop_first=True, dtype=float)
    X = pd.concat([sub[indep_vars], dummies], axis=1)
    X = sm.add_constant(X)
    y = sub[dep_var]
    
    # Fit standard OLS to get studentized residuals
    ols_fit = sm.OLS(y, X).fit()
    infl = ols_fit.get_influence()
    sub["stud_resid"] = infl.resid_studentized_external
    sub["pred_peer"] = ols_fit.predict(X)
    sub["residual_peer"] = sub[dep_var] - sub["pred_peer"]
    sub["raw_z"] = sub["residual_peer"] / sub["residual_peer"].std()
    
    # Normalized by scale
    if "coordinator" in dep_var or "central" in dep_var:
        sub["resid_rate"] = (sub["residual_peer"] / sub["teachers_k12_fte"]) * 100.0
        rate_name = "per 100 teachers"
    elif "school" in dep_var:
        sub["resid_rate"] = sub["residual_peer"] / sub["operating_schools_count"]
        rate_name = "per school"
    else:
        sub["resid_rate"] = (sub["residual_peer"] / sub["enrollment_total"]) * 1000.0
        rate_name = "per 1k pupils"
        
    print(f"\n=== {model_name} ({dep_var}) ===")
    print(f"Independent variables: {indep_vars}")
    # Show top 5 outliers by stud_resid in 2023-24
    sub23 = sub[sub["school_year"] == "2023-2024"].sort_values("stud_resid", ascending=False)
    print("Top 5 Outliers in 2023-2024:")
    for _, r in sub23.head(5).iterrows():
        print(f"  {r['lea_name'][:25]:25s}: actual={r[dep_var]:6.1f}, pred={r['pred_peer']:6.1f}, resid={r['residual_peer']:+6.1f} FTE, raw_z={r['raw_z']:+5.2f}, stud_z={r['stud_resid']:+5.2f}, resid_rate={r['resid_rate']:+5.2f} {rate_name}")
    
    # Multi-year persistent outliers (stud_resid > 1.5 in >= 3 years)
    persistent = sub[sub["stud_resid"] > 1.5].groupby(["nces_lea_id", "lea_name", "state"]).size().reset_index(name="high_years")
    persistent = persistent[persistent["high_years"] >= 3].sort_values("high_years", ascending=False)
    print("\nPersistent Outliers (stud_z > 1.5 in >= 3 years):")
    for _, r in persistent.iterrows():
        sub_dist = sub[sub["nces_lea_id"] == r["nces_lea_id"]]
        mean_res = sub_dist["residual_peer"].mean()
        max_stud = sub_dist["stud_resid"].max()
        mean_rate = sub_dist["resid_rate"].mean()
        print(f"  {r['lea_name'][:25]:25s} ({r['state']}): {r['high_years']} yrs, mean_res={mean_res:+5.1f} FTE, max_stud_z={max_stud:+5.2f}, mean_rate={mean_rate:+5.2f} {rate_name}")

run_peer_model("school_administrators_fte", ["operating_schools_count", "enrollment_1k"], "Model 1: SCHADM (Peer)")
run_peer_model("lea_administrators_fte", ["enrollment_1k", "operating_schools_count"], "Model 2: LEAADM (Peer)")
run_peer_model("instructional_coordinators_fte", ["teachers_100"], "Model 3: CORSUP (Peer)")
run_peer_model("central_mgmt_and_coordinators_fte", ["teachers_100"], "Model 4: Combined (Peer)")

