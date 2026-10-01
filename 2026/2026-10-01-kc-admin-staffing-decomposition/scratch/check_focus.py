import pandas as pd

df = pd.read_csv('outputs/tables/fiscal_materiality_counterfactuals.csv')
df['nces_lea_id'] = df['nces_lea_id'].astype(str).str.zfill(7)
targets = [
    ('2011640', 'Shawnee Mission USD 512'),
    ('2007950', 'Kansas City USD 500 (KCKPS)'),
    ('2912290', 'Fort Osage R-I'),
    ('2926070', 'Raytown C-2')
]

for lea_id, label in targets:
    sub = df[df['nces_lea_id'] == lea_id].iloc[0]
    print(f"=== {label} ({sub['district_name']}, {sub['state']}) ===")
    print(f"Teachers FTE: {sub['teachers_k12_fte']}")
    print(f"CF1 Own Rollback Savings: ${sub['cf1_own_rollback_savings']:,.2f}")
    print(f"CF1 Gross Comp Equiv: ${sub['cf1_own_gross_comp_equiv']:,.2f}")
    print(f"CF1 Feasible Base Raise: ${sub['cf1_own_feasible_base_raise']:,.2f} (+{sub['cf1_own_pct_raise_on_base']:.1f}%)")
    print(f"CF1 Teachers Funded: {sub['cf1_own_teachers_funded']} FTE")
    print(f"CF2 All Supervisory Savings: ${sub['cf2_all_supervisory_savings']:,.2f}")
    print(f"CF2 All Gross Comp Equiv: ${sub['cf2_all_gross_comp_equiv']:,.2f}")
    print(f"CF2 All Feasible Base Raise: ${sub['cf2_all_feasible_base_raise']:,.2f} (+{sub['cf2_all_pct_raise_on_base']:.1f}%)\n")
