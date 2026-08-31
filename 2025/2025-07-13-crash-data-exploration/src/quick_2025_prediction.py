"""
Quick 2025 Prediction Analysis
==============================

This script focuses specifically on predicting the 2025 total based on current partial data.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def analyze_2025_prediction():
    """Analyze and predict 2025 crash totals."""
    
    print("Loading crash data...")
    df = pd.read_csv("./data/Crash_File_20250712.csv", low_memory=False)
    
    # Process dates
    df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'], format='%Y%m%d', errors='coerce')
    df['YEAR'] = df['REPORT_DATE'].dt.year
    df['MONTH'] = df['REPORT_DATE'].dt.month
    
    # Filter for recent years
    recent_df = df[df['YEAR'] >= 2015].copy()
    
    print(f"Total records 2015-2025: {len(recent_df):,}")
    
    # Current 2025 data
    data_2025 = recent_df[recent_df['YEAR'] == 2025]
    current_2025_count = len(data_2025)
    
    print(f"\nCurrent 2025 crashes: {current_2025_count:,}")
    
    # Calculate progress through year
    current_date = datetime.now()
    day_of_year = current_date.timetuple().tm_yday
    days_in_year = 366 if current_date.year % 4 == 0 else 365
    progress_through_year = day_of_year / days_in_year
    
    print(f"Current date: {current_date.strftime('%Y-%m-%d')}")
    print(f"Progress through 2025: {progress_through_year:.1%}")
    
    # Method 1: Simple linear extrapolation
    simple_prediction = int(current_2025_count / progress_through_year)
    print(f"\nMethod 1 - Simple extrapolation: {simple_prediction:,} crashes")
    
    # Method 2: Seasonal analysis
    print(f"\nMethod 2 - Seasonal Analysis:")
    
    # Get monthly averages for recent years (2020-2024) - CORRECTED
    recent_data = recent_df[recent_df['YEAR'].between(2020, 2024)]
    monthly_totals = recent_data.groupby('MONTH').size()
    monthly_avg_corrected = monthly_totals / 5  # Divide by 5 years to get per-year average
    data_2025_by_month = data_2025.groupby('MONTH').size()
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    print(f"Monthly averages (2020-2024) - per year:")
    for month in range(1, 13):
        if month in monthly_avg_corrected.index:
            print(f"  {month_names[month-1]}: {monthly_avg_corrected[month]:,.0f} crashes")
    
    print(f"\n2025 data by month so far:")
    for month in range(1, 13):
        if month in data_2025_by_month.index:
            print(f"  {month_names[month-1]}: {data_2025_by_month[month]:,.0f} crashes")
    
    # Calculate remaining months with CORRECTED averages
    current_month = datetime.now().month
    predicted_remaining = 0
    
    print(f"\nPredicting remaining months:")
    for month in range(current_month + 1, 13):
        if month in monthly_avg_corrected.index:
            month_prediction = monthly_avg_corrected[month]
            predicted_remaining += month_prediction
            print(f"  {month_names[month-1]}: {month_prediction:,.0f} crashes")
    
    seasonal_prediction = current_2025_count + predicted_remaining
    print(f"\nSeasonal prediction for 2025 total: {seasonal_prediction:,.0f} crashes")
    
    # Method 3: Recent trend average
    recent_yearly_avg = recent_df[recent_df['YEAR'].between(2020, 2024)].groupby('YEAR').size().mean()
    print(f"\nMethod 3 - Recent trend average (2020-2024): {recent_yearly_avg:,.0f} crashes")
    
    # Final prediction (use the higher of seasonal and trend)
    final_prediction = max(seasonal_prediction, recent_yearly_avg)
    print(f"\nFinal 2025 prediction: {final_prediction:,.0f} crashes")
    
    # Compare with previous years
    yearly_stats = recent_df.groupby('YEAR').size()
    print(f"\nComparison with recent years:")
    for year in range(2020, 2025):
        if year in yearly_stats.index:
            count = yearly_stats[year]
            change = ((final_prediction - count) / count) * 100
            print(f"  {year}: {count:,} crashes (2025 prediction: {change:+.1f}%)")
    
    return final_prediction

if __name__ == "__main__":
    prediction = analyze_2025_prediction()
    print(f"\nFinal 2025 prediction: {prediction:,} crashes") 