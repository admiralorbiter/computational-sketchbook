import sys
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

df = pd.read_parquet(PROJECT_ROOT / "data" / "processed" / "district_demand_year.parquet")
b55 = df[df["is_balanced_presence_cohort_55"]].copy()

# -------------------------------------------------------------
# Peer Expected-Level Model for CORSUP
# -------------------------------------------------------------
cor_df = b55[(b55["school_year"] >= "2014-2015") & (b55["school_year"] <= "2023-2024")].copy()
cor_df["teachers_100"] = cor_df["teachers_k12_fte"] / 100.0
cor_df["idea_100"] = cor_df["idea_count_harmonized"] / 100.0
cor_df["lep_100"] = cor_df["lep_count_harmonized"] / 100.0
cor_df["poverty_100"] = cor_df["saipe_est_population_5_17_poverty"] / 100.0

covars = ["teachers_100", "idea_100", "lep_100", "poverty_100"]
cor_df = cor_df.dropna(subset=["instructional_coordinators_fte"] + covars).copy()

# Add state*year dummies
dummies = pd.get_dummies(cor_df["state"] + "_" + cor_df["school_year"], drop_first=True, dtype=float)
X = pd.concat([cor_df[covars], dummies], axis=1)
X = sm.add_constant(X)
y = cor_df["instructional_coordinators_fte"]

model_peer = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": cor_df["nces_lea_id"]})
print("Peer Model R2:", model_peer.rsquared)
print("Coefficients:\n", model_peer.params[covars])

cor_df["pred_peer"] = model_peer.predict(X)
cor_df["residual_peer"] = cor_df["instructional_coordinators_fte"] - cor_df["pred_peer"]
sd_res = cor_df["residual_peer"].std()
cor_df["z_residual"] = cor_df["residual_peer"] / sd_res

print(f"\nResidual SD: {sd_res:.2f} FTE")

# Identify persistent outliers: z > 1.5 in 3 or more consecutive years
outlier_records = []
for lea, grp in cor_df.groupby("nces_lea_id"):
    grp = grp.sort_values("school_year")
    z_high = (grp["z_residual"] > 1.5).astype(int)
    # rolling sum of 3
    roll3 = z_high.rolling(3).sum()
    if (roll3 >= 3).any():
        dname = grp["district_name"].iloc[0]
        st = grp["state"].iloc[0]
        mean_y = grp["instructional_coordinators_fte"].mean()
        mean_pred = grp["pred_peer"].mean()
        mean_res = grp["residual_peer"].mean()
        outlier_records.append({
            "nces_lea_id": lea,
            "district_name": dname,
            "state": st,
            "mean_corsup_fte": round(mean_y, 1),
            "mean_pred_peer_fte": round(mean_pred, 1),
            "mean_residual_fte": round(mean_res, 1),
            "max_z_score": round(grp["z_residual"].max(), 2),
            "high_z_years_count": int(z_high.sum()),
        })

df_out = pd.DataFrame(outlier_records).sort_values("mean_residual_fte", ascending=False)
print("\n=== PERSISTENT PEER-LEVEL OUTLIERS (z > 1.5 SD for 3+ years) ===")
print(df_out.to_string(index=False))
