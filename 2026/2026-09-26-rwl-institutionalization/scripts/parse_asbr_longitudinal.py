"""Parse DESE ASBR statutory Excel workbooks for Grandview C-4 into longitudinal panel.

Reads all harvested annual ASBR workbooks (2018-19 to 2023-24) from
data/raw/grandview-c4/finance/asbr/ and produces the normalized analytical dataset
in districts/grandview-c4/finance/grandview_asbr_longitudinal.csv.
"""

import os
import re
import csv
import glob
import openpyxl

RAW_DIR = os.path.abspath('2026/2026-09-26-rwl-institutionalization/data/raw/grandview-c4/finance/asbr')
OUT_CSV = os.path.abspath('2026/2026-09-26-rwl-institutionalization/districts/grandview-c4/finance/grandview_asbr_longitudinal.csv')

def parse_num(val):
    if val is None or val == '-' or val == '':
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).replace('$', '').replace(',', '').replace('(', '-').replace(')', '').strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def parse_all_asbr_workbooks():
    files = sorted(glob.glob(os.path.join(RAW_DIR, 'asbr_*.xlsx')))
    print(f'Found {len(files)} ASBR Excel workbooks.')

    records = []

    for fpath in files:
        fname = os.path.basename(fpath)
        m = re.search(r'asbr_(\d{4})_(\d{4})\.xlsx', fname)
        if not m:
            continue
        school_year = f'{m.group(1)}-{m.group(2)}'
        print(f'Parsing ASBR for {school_year} ({fname})...')

        wb = openpyxl.load_workbook(fpath, data_only=True)
        sheet = wb.active

        rec = {
            'district_code': '048-074',
            'district_name': 'Grandview C-4',
            'school_year': school_year,
            'source_file': f'data/raw/grandview-c4/finance/asbr/{fname}',
            'assessed_valuation': 0.0,
            'beginning_fund_balance_total': 0.0,
            'local_revenue_5100s': 0.0,
            'county_revenue_5200s': 0.0,
            'state_revenue_5300s': 0.0,
            'state_career_education_5332': 0.0,
            'federal_revenue_5400s': 0.0,
            'federal_perkins_career_5427': 0.0,
            'total_revenue_5899': 0.0,
            'elementary_instruction_1111': 0.0,
            'high_school_instruction_1151': 0.0,
            'career_education_1311_1391': 0.0,
            'area_career_center_fees_1921': 0.0,
            'student_activities_1411': 0.0,
            'total_instruction_1999': 0.0,
            'instructional_staff_training_2213': 0.0,
            'total_instruction_and_support_2999': 0.0,
            'total_expenditures_9999': 0.0,
            'ending_fund_balance_general_fund1': 0.0,
            'ending_fund_balance_teachers_fund2': 0.0,
            'ending_fund_balance_debt_fund3': 0.0,
            'ending_fund_balance_capital_fund4': 0.0,
            'ending_fund_balance_total_3112': 0.0,
            'grant_regime': 'direct_grant',
            'coding_method': 'primary_state_statutory_filing'
        }

        # Scan rows
        for row in sheet.iter_rows(values_only=True):
            vals = [c for c in row if c is not None]
            if not vals:
                continue

            first_val = str(vals[0]).strip()
            line_str = ' '.join(str(c) for c in vals)

            # Assessed valuation
            if 'Total Assessed Valuation' in line_str:
                m_av = re.search(r'([\d,]{7,15})', line_str)
                if m_av:
                    rec['assessed_valuation'] = parse_num(m_av.group(1))

            # Code matches
            if first_val == '3111' and 'Beginning Fund Balances' in line_str:
                # Total All Funds is typically column index corresponding to Total All Funds
                # In Part I Summary: cols are Code, Name, General, Teachers, Debt, Capital, Total All Funds
                if len(vals) >= 6:
                    rec['beginning_fund_balance_total'] = parse_num(vals[-1])
            elif first_val == '5899' and 'Total Revenue' in line_str:
                if len(vals) >= 6:
                    rec['total_revenue_5899'] = parse_num(vals[-1])
            elif first_val == '9999' and 'Expenditures' in line_str:
                if len(vals) >= 6:
                    rec['total_expenditures_9999'] = parse_num(vals[-1])
            elif first_val == '3112' and 'Ending Fund Balances' in line_str:
                if len(vals) >= 6:
                    rec['ending_fund_balance_general_fund1'] = parse_num(vals[2])
                    rec['ending_fund_balance_teachers_fund2'] = parse_num(vals[3])
                    rec['ending_fund_balance_debt_fund3'] = parse_num(vals[4])
                    rec['ending_fund_balance_capital_fund4'] = parse_num(vals[5])
                    rec['ending_fund_balance_total_3112'] = parse_num(vals[-1])

            # Revenue lines
            elif first_val == '5199':
                rec['local_revenue_5100s'] = parse_num(vals[-1])
            elif first_val == '5299':
                rec['county_revenue_5200s'] = parse_num(vals[-1])
            elif first_val == '5399':
                rec['state_revenue_5300s'] = parse_num(vals[-1])
            elif first_val == '5499':
                rec['federal_revenue_5400s'] = parse_num(vals[-1])
            elif first_val == '5332' and 'Career Education' in line_str:
                rec['state_career_education_5332'] = parse_num(vals[-1]) if len(vals) >= 3 else 0.0
            elif first_val == '5427' and 'Perkins' in line_str:
                rec['federal_perkins_career_5427'] = parse_num(vals[-1]) if len(vals) >= 3 else 0.0

            # Instruction & CTE expenditure lines (Total Instruction column or Total All Funds)
            elif first_val == '1111' and 'Elementary' in line_str:
                rec['elementary_instruction_1111'] = parse_num(vals[-1])
            elif first_val == '1151' and ('Senior High' in line_str or 'High School' in line_str):
                rec['high_school_instruction_1151'] = parse_num(vals[-1])
            elif first_val in ['1311', '1321', '1331', '1341', '1351', '1361', '1371', '1381', '1391'] or 'Career Education' in line_str:
                rec['career_education_1311_1391'] += parse_num(vals[-1])
            elif first_val == '1921' and 'Area Career Center' in line_str:
                rec['area_career_center_fees_1921'] = parse_num(vals[-1])
            elif first_val == '1411' and 'Student Activities' in line_str:
                rec['student_activities_1411'] = parse_num(vals[-1])
            elif first_val == '1999' and 'Total Instruction' in line_str:
                rec['total_instruction_1999'] = parse_num(vals[-1])
            elif first_val == '2213' and 'Instructional Staff Training' in line_str:
                rec['instructional_staff_training_2213'] = parse_num(vals[-1])
            elif first_val == '2999' and 'Total Instruction & Support' in line_str:
                rec['total_instruction_and_support_2999'] = parse_num(vals[-1])

        records.append(rec)

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    if records:
        headers = list(records[0].keys())
        with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(records)
        print(f'Wrote {len(records)} ASBR longitudinal records to {OUT_CSV}')

if __name__ == '__main__':
    parse_all_asbr_workbooks()
