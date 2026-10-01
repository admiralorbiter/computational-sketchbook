import pandas as pd
import numpy as np

# Load demand panel
df_demand = pd.read_parquet('data/processed/district_demand_year.parquet')
df_res = pd.read_csv('outputs/tables/peer_expected_staffing_residuals.csv')

# Filter to balanced 55 cohort in 2023-2024
b55_2324 = df_demand[(df_demand['is_balanced_presence_cohort_55'] == 1) & (df_demand['school_year'] == '2023-2024')].copy()
b55_1415 = df_demand[(df_demand['is_balanced_presence_cohort_55'] == 1) & (df_demand['school_year'] == '2014-2015')].copy()

print(f"2014-15 Teachers: {b55_1415['teachers_k12_fte'].sum():.2f}, Coordinators: {b55_1415['instructional_coordinators_fte'].sum():.2f}")
print(f"2023-24 Teachers: {b55_2324['teachers_k12_fte'].sum():.2f}, Coordinators: {b55_2324['instructional_coordinators_fte'].sum():.2f}")

ratio_1415 = b55_1415['instructional_coordinators_fte'].sum() / b55_1415['teachers_k12_fte'].sum()
target_coord_2324 = b55_2324['teachers_k12_fte'].sum() * ratio_1415
surplus_coord_2324 = b55_2324['instructional_coordinators_fte'].sum() - target_coord_2324

print(f"2014-15 Ratio (Coordinators / Teacher): {ratio_1415:.4f} ({ratio_1415*100:.2f} per 100 teachers)")
print(f"2023-24 Target Coordinators at 2014 ratio: {target_coord_2324:.2f}")
print(f"2023-24 Net Surplus Coordinators: {surplus_coord_2324:.2f} FTE")

# Check peer residuals in 2023-2024
sub_res = df_res[df_res['school_year'] == '2023-2024'].copy()
for model in sub_res['model_name'].unique():
    m_sub = sub_res[sub_res['model_name'] == model]
    excess = m_sub['residual_peer'].apply(lambda x: max(0, x)).sum()
    print(f"{model}: Total Positive Peer Residual (Excess FTE): {excess:.2f} FTE across {len(m_sub)} districts")
