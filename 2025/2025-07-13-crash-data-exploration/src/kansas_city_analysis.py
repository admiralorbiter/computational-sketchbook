"""
Kansas City Comprehensive Crash Analysis
========================================

This script provides an exhaustive analysis of crash data specifically for Kansas City
(both Kansas City, MO and Kansas City, KS) from multiple perspectives and breakdowns.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class KansasCityAnalyzer:
    """
    Comprehensive analyzer for Kansas City crash data with multiple perspectives.
    """
    
    def __init__(self, data_path):
        """Initialize the analyzer with the crash data file path."""
        self.data_path = data_path
        self.df = None
        self.kc_df = None
        self.loaded = False
        
    def load_data(self):
        """Load the crash data and filter for Kansas City."""
        print("Loading crash data...")
        print(f"File path: {self.data_path}")
        
        try:
            # Load with low_memory=False to avoid mixed types warning
            self.df = pd.read_csv(self.data_path, low_memory=False)
            self.loaded = True
            print(f"✓ Data loaded successfully!")
            print(f"Total dataset shape: {self.df.shape}")
            
            # Process date columns
            self._process_date_columns()
            
            # Filter for Kansas City
            self._filter_kansas_city_data()
            
        except Exception as e:
            print(f"✗ Error loading data: {e}")
            return False
            
        return True
    
    def _process_date_columns(self):
        """Process and convert date columns to proper datetime format."""
        print("\nProcessing date columns...")
        
        # Convert REPORT_DATE to datetime
        if 'REPORT_DATE' in self.df.columns:
            self.df['REPORT_DATE'] = pd.to_datetime(self.df['REPORT_DATE'], format='%Y%m%d', errors='coerce')
            
        # Convert CHANGE_DATE to datetime  
        if 'CHANGE_DATE' in self.df.columns:
            self.df['CHANGE_DATE'] = pd.to_datetime(self.df['CHANGE_DATE'], format='%Y%m%d %H%M', errors='coerce')
            
        # Process REPORT_TIME
        if 'REPORT_TIME' in self.df.columns:
            self.df['REPORT_TIME_STR'] = self.df['REPORT_TIME'].astype(str).str.zfill(4)
            self.df['REPORT_HOUR'] = self.df['REPORT_TIME_STR'].str[:2].astype(int, errors='ignore')
            
        # Add time-based columns
        self.df['YEAR'] = self.df['REPORT_DATE'].dt.year
        self.df['MONTH'] = self.df['REPORT_DATE'].dt.month
        self.df['DAY_OF_WEEK'] = self.df['REPORT_DATE'].dt.dayofweek
        self.df['DAY_NAME'] = self.df['REPORT_DATE'].dt.day_name()
        self.df['MONTH_NAME'] = self.df['REPORT_DATE'].dt.month_name()
        
        print("✓ Date columns processed")
    
    def _filter_kansas_city_data(self):
        """Filter data specifically for Kansas City (both MO and KS)."""
        print("\nFiltering for Kansas City data...")
        
        # Filter for Kansas City in multiple ways to catch all variations
        kc_filters = (
            # Primary city field
            (self.df['CITY'].str.contains('KANSAS CITY', case=False, na=False)) |
            (self.df['CITY'].str.contains('KC', case=False, na=False)) |
            # Carrier city field
            (self.df['CRASH_CARRIER_CITY'].str.contains('KANSAS CITY', case=False, na=False)) |
            (self.df['CRASH_CARRIER_CITY'].str.contains('KC', case=False, na=False))
        )
        
        self.kc_df = self.df[kc_filters].copy()
        
        print(f"✓ Kansas City data filtered: {self.kc_df.shape[0]:,} records")
        print(f"Year range: {self.kc_df['YEAR'].min()} to {self.kc_df['YEAR'].max()}")
        
        # Show breakdown by state
        if not self.kc_df.empty:
            print("\nKansas City crashes by state:")
            state_counts = self.kc_df['REPORT_STATE'].value_counts()
            for state, count in state_counts.items():
                print(f"  {state}: {count:,} crashes")
            
            # Show city variations
            print("\nCity name variations found:")
            city_variations = self.kc_df['CITY'].value_counts().head(10)
            for city, count in city_variations.items():
                if pd.notna(city):
                    print(f"  {city}: {count:,} crashes")
    
    def basic_overview(self):
        """Display basic overview of Kansas City crash data."""
        if not self.loaded or self.kc_df.empty:
            print("No Kansas City data available. Please load data first.")
            return
            
        print("\n" + "="*70)
        print("KANSAS CITY CRASH DATA OVERVIEW")
        print("="*70)
        
        print(f"Dataset shape: {self.kc_df.shape}")
        print(f"Date range: {self.kc_df['YEAR'].min()} to {self.kc_df['YEAR'].max()}")
        print(f"Total crashes: {len(self.kc_df):,}")
        
        # Basic statistics
        if 'FATALITIES' in self.kc_df.columns:
            total_fatalities = self.kc_df['FATALITIES'].sum()
            fatal_crashes = (self.kc_df['FATALITIES'] > 0).sum()
            print(f"Total fatalities: {total_fatalities:,}")
            print(f"Fatal crashes: {fatal_crashes:,} ({(fatal_crashes/len(self.kc_df))*100:.1f}%)")
            
        if 'INJURIES' in self.kc_df.columns:
            total_injuries = self.kc_df['INJURIES'].sum()
            injury_crashes = (self.kc_df['INJURIES'] > 0).sum()
            print(f"Total injuries: {total_injuries:,}")
            print(f"Injury crashes: {injury_crashes:,} ({(injury_crashes/len(self.kc_df))*100:.1f}%)")
            
        # State breakdown
        print(f"\nBreakdown by state:")
        state_breakdown = self.kc_df['REPORT_STATE'].value_counts()
        for state, count in state_breakdown.items():
            print(f"  {state}: {count:,} crashes ({(count/len(self.kc_df))*100:.1f}%)")
    
    def temporal_analysis(self):
        """Comprehensive temporal analysis of Kansas City crashes."""
        if not self.loaded or self.kc_df.empty:
            return
            
        print("\n" + "="*70)
        print("TEMPORAL ANALYSIS - KANSAS CITY")
        print("="*70)
        
        # Yearly trends
        print("\nCrashes by Year:")
        yearly_crashes = self.kc_df.groupby('YEAR').size()
        for year, count in yearly_crashes.items():
            print(f"  {year}: {count:,} crashes")
            
        # Create temporal visualizations
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        
        # 1. Yearly trends
        yearly_crashes.plot(kind='line', marker='o', ax=axes[0,0], color='blue')
        axes[0,0].set_title('Kansas City Crashes by Year')
        axes[0,0].set_xlabel('Year')
        axes[0,0].set_ylabel('Number of Crashes')
        axes[0,0].grid(True, alpha=0.3)
        
        # 2. Monthly patterns
        monthly_crashes = self.kc_df.groupby('MONTH').size()
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        axes[0,1].bar(range(1, 13), monthly_crashes, color='skyblue')
        axes[0,1].set_title('Kansas City Crashes by Month')
        axes[0,1].set_xlabel('Month')
        axes[0,1].set_ylabel('Number of Crashes')
        axes[0,1].set_xticks(range(1, 13))
        axes[0,1].set_xticklabels(month_names, rotation=45)
        axes[0,1].grid(True, alpha=0.3)
        
        # 3. Day of week patterns
        dow_crashes = self.kc_df.groupby('DAY_OF_WEEK').size()
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        axes[0,2].bar(range(7), dow_crashes, color='lightcoral')
        axes[0,2].set_title('Kansas City Crashes by Day of Week')
        axes[0,2].set_xlabel('Day of Week')
        axes[0,2].set_ylabel('Number of Crashes')
        axes[0,2].set_xticks(range(7))
        axes[0,2].set_xticklabels(day_names)
        axes[0,2].grid(True, alpha=0.3)
        
        # 4. Hourly patterns
        if 'REPORT_HOUR' in self.kc_df.columns:
            hourly_crashes = self.kc_df.groupby('REPORT_HOUR').size()
            axes[1,0].plot(hourly_crashes.index, hourly_crashes.values, marker='o', linewidth=2, color='green')
            axes[1,0].set_title('Kansas City Crashes by Hour of Day')
            axes[1,0].set_xlabel('Hour of Day')
            axes[1,0].set_ylabel('Number of Crashes')
            axes[1,0].grid(True, alpha=0.3)
            axes[1,0].set_xticks(range(0, 24, 2))
        
        # 5. Seasonal patterns (quarterly)
        self.kc_df['QUARTER'] = self.kc_df['REPORT_DATE'].dt.quarter
        quarterly_crashes = self.kc_df.groupby('QUARTER').size()
        axes[1,1].bar(['Q1', 'Q2', 'Q3', 'Q4'], quarterly_crashes, color='orange')
        axes[1,1].set_title('Kansas City Crashes by Quarter')
        axes[1,1].set_xlabel('Quarter')
        axes[1,1].set_ylabel('Number of Crashes')
        axes[1,1].grid(True, alpha=0.3)
        
        # 6. Year-over-year growth
        yearly_pct_change = yearly_crashes.pct_change() * 100
        axes[1,2].bar(yearly_pct_change.index[1:], yearly_pct_change[1:], color='purple')
        axes[1,2].set_title('Year-over-Year Change (%)')
        axes[1,2].set_xlabel('Year')
        axes[1,2].set_ylabel('Percentage Change')
        axes[1,2].grid(True, alpha=0.3)
        axes[1,2].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    def severity_analysis(self):
        """Analyze crash severity patterns in Kansas City."""
        if not self.loaded or self.kc_df.empty:
            return
            
        print("\n" + "="*70)
        print("SEVERITY ANALYSIS - KANSAS CITY")
        print("="*70)
        
        # Fatality analysis
        if 'FATALITIES' in self.kc_df.columns:
            print("\nFatality Analysis:")
            fatality_stats = self.kc_df['FATALITIES'].describe()
            print(fatality_stats)
            
            fatal_by_year = self.kc_df.groupby('YEAR')['FATALITIES'].sum()
            print(f"\nFatalities by year:")
            for year, count in fatal_by_year.items():
                print(f"  {year}: {count} fatalities")
        
        # Injury analysis
        if 'INJURIES' in self.kc_df.columns:
            print("\nInjury Analysis:")
            injury_stats = self.kc_df['INJURIES'].describe()
            print(injury_stats)
            
            injury_by_year = self.kc_df.groupby('YEAR')['INJURIES'].sum()
            print(f"\nInjuries by year:")
            for year, count in injury_by_year.items():
                print(f"  {year}: {count} injuries")
        
        # Create severity visualizations
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Fatality distribution
        if 'FATALITIES' in self.kc_df.columns:
            fatality_counts = self.kc_df['FATALITIES'].value_counts().sort_index()
            axes[0,0].bar(fatality_counts.index[:10], fatality_counts.values[:10], color='red', alpha=0.7)
            axes[0,0].set_title('Distribution of Fatalities per Crash')
            axes[0,0].set_xlabel('Number of Fatalities')
            axes[0,0].set_ylabel('Number of Crashes')
            axes[0,0].grid(True, alpha=0.3)
        
        # 2. Injury distribution  
        if 'INJURIES' in self.kc_df.columns:
            injury_counts = self.kc_df['INJURIES'].value_counts().sort_index()
            axes[0,1].bar(injury_counts.index[:10], injury_counts.values[:10], color='orange', alpha=0.7)
            axes[0,1].set_title('Distribution of Injuries per Crash')
            axes[0,1].set_xlabel('Number of Injuries')
            axes[0,1].set_ylabel('Number of Crashes')
            axes[0,1].grid(True, alpha=0.3)
        
        # 3. Vehicles involved
        if 'VEHICLES_IN_ACCIDENT' in self.kc_df.columns:
            vehicle_counts = self.kc_df['VEHICLES_IN_ACCIDENT'].value_counts().sort_index()
            axes[1,0].bar(vehicle_counts.index[:10], vehicle_counts.values[:10], color='blue', alpha=0.7)
            axes[1,0].set_title('Distribution of Vehicles Involved')
            axes[1,0].set_xlabel('Number of Vehicles')
            axes[1,0].set_ylabel('Number of Crashes')
            axes[1,0].grid(True, alpha=0.3)
        
        # 4. Severity by hour
        if 'REPORT_HOUR' in self.kc_df.columns and 'FATALITIES' in self.kc_df.columns:
            hourly_severity = self.kc_df.groupby('REPORT_HOUR')['FATALITIES'].mean()
            axes[1,1].plot(hourly_severity.index, hourly_severity.values, marker='o', color='red')
            axes[1,1].set_title('Average Fatalities per Crash by Hour')
            axes[1,1].set_xlabel('Hour of Day')
            axes[1,1].set_ylabel('Average Fatalities')
            axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def environmental_analysis(self):
        """Analyze environmental factors in Kansas City crashes."""
        if not self.loaded or self.kc_df.empty:
            return
            
        print("\n" + "="*70)
        print("ENVIRONMENTAL FACTORS ANALYSIS - KANSAS CITY")
        print("="*70)
        
        # Weather conditions
        if 'WEATHER_CONDITION_ID' in self.kc_df.columns:
            print("\nTop 10 Weather Conditions:")
            weather_counts = self.kc_df['WEATHER_CONDITION_ID'].value_counts().head(10)
            for condition, count in weather_counts.items():
                print(f"  Condition {condition}: {count:,} crashes ({(count/len(self.kc_df))*100:.1f}%)")
        
        # Light conditions
        if 'LIGHT_CONDITION_ID' in self.kc_df.columns:
            print("\nTop 10 Light Conditions:")
            light_counts = self.kc_df['LIGHT_CONDITION_ID'].value_counts().head(10)
            for condition, count in light_counts.items():
                print(f"  Condition {condition}: {count:,} crashes ({(count/len(self.kc_df))*100:.1f}%)")
        
        # Road surface conditions
        if 'ROAD_SURFACE_CONDITION_ID' in self.kc_df.columns:
            print("\nTop 10 Road Surface Conditions:")
            road_counts = self.kc_df['ROAD_SURFACE_CONDITION_ID'].value_counts().head(10)
            for condition, count in road_counts.items():
                print(f"  Condition {condition}: {count:,} crashes ({(count/len(self.kc_df))*100:.1f}%)")
        
        # Create environmental visualizations
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Weather conditions
        if 'WEATHER_CONDITION_ID' in self.kc_df.columns:
            top_weather = self.kc_df['WEATHER_CONDITION_ID'].value_counts().head(8)
            axes[0,0].bar(range(len(top_weather)), top_weather.values, color='lightblue')
            axes[0,0].set_title('Top Weather Conditions')
            axes[0,0].set_xlabel('Weather Condition ID')
            axes[0,0].set_ylabel('Number of Crashes')
            axes[0,0].set_xticks(range(len(top_weather)))
            axes[0,0].set_xticklabels(top_weather.index, rotation=45)
            axes[0,0].grid(True, alpha=0.3)
        
        # 2. Light conditions
        if 'LIGHT_CONDITION_ID' in self.kc_df.columns:
            top_light = self.kc_df['LIGHT_CONDITION_ID'].value_counts().head(8)
            axes[0,1].bar(range(len(top_light)), top_light.values, color='yellow')
            axes[0,1].set_title('Top Light Conditions')
            axes[0,1].set_xlabel('Light Condition ID')
            axes[0,1].set_ylabel('Number of Crashes')
            axes[0,1].set_xticks(range(len(top_light)))
            axes[0,1].set_xticklabels(top_light.index, rotation=45)
            axes[0,1].grid(True, alpha=0.3)
        
        # 3. Road surface conditions
        if 'ROAD_SURFACE_CONDITION_ID' in self.kc_df.columns:
            top_road = self.kc_df['ROAD_SURFACE_CONDITION_ID'].value_counts().head(8)
            axes[1,0].bar(range(len(top_road)), top_road.values, color='brown')
            axes[1,0].set_title('Top Road Surface Conditions')
            axes[1,0].set_xlabel('Road Surface Condition ID')
            axes[1,0].set_ylabel('Number of Crashes')
            axes[1,0].set_xticks(range(len(top_road)))
            axes[1,0].set_xticklabels(top_road.index, rotation=45)
            axes[1,0].grid(True, alpha=0.3)
        
        # 4. Environmental factors correlation with severity
        if all(col in self.kc_df.columns for col in ['WEATHER_CONDITION_ID', 'LIGHT_CONDITION_ID', 'FATALITIES']):
            env_severity = self.kc_df.groupby(['WEATHER_CONDITION_ID', 'LIGHT_CONDITION_ID'])['FATALITIES'].mean().unstack()
            sns.heatmap(env_severity, ax=axes[1,1], cmap='Reds', annot=True, fmt='.2f')
            axes[1,1].set_title('Average Fatalities by Weather & Light')
            axes[1,1].set_xlabel('Light Condition ID')
            axes[1,1].set_ylabel('Weather Condition ID')
        
        plt.tight_layout()
        plt.show()
    
    def vehicle_analysis(self):
        """Analyze vehicle characteristics in Kansas City crashes."""
        if not self.loaded or self.kc_df.empty:
            return
            
        print("\n" + "="*70)
        print("VEHICLE ANALYSIS - KANSAS CITY")
        print("="*70)
        
        # Truck vs Bus distribution
        if 'TRUCK_BUS_IND' in self.kc_df.columns:
            print("\nTruck vs Bus Distribution:")
            truck_bus_counts = self.kc_df['TRUCK_BUS_IND'].value_counts()
            for vehicle_type, count in truck_bus_counts.items():
                print(f"  {vehicle_type}: {count:,} crashes ({(count/len(self.kc_df))*100:.1f}%)")
        
        # Vehicle configuration
        if 'VEHICLE_CONFIGURATION_ID' in self.kc_df.columns:
            print("\nTop 10 Vehicle Configurations:")
            config_counts = self.kc_df['VEHICLE_CONFIGURATION_ID'].value_counts().head(10)
            for config, count in config_counts.items():
                print(f"  Config {config}: {count:,} crashes ({(count/len(self.kc_df))*100:.1f}%)")
        
        # GVW Rating
        if 'GVW_RATING_ID' in self.kc_df.columns:
            print("\nTop 10 GVW Ratings:")
            gvw_counts = self.kc_df['GVW_RATING_ID'].value_counts().head(10)
            for gvw, count in gvw_counts.items():
                print(f"  GVW {gvw}: {count:,} crashes ({(count/len(self.kc_df))*100:.1f}%)")
        
        # Create vehicle visualizations
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Truck vs Bus
        if 'TRUCK_BUS_IND' in self.kc_df.columns:
            truck_bus_counts = self.kc_df['TRUCK_BUS_IND'].value_counts()
            axes[0,0].pie(truck_bus_counts.values, labels=truck_bus_counts.index, autopct='%1.1f%%', startangle=90)
            axes[0,0].set_title('Truck vs Bus Distribution')
        
        # 2. Vehicle configuration
        if 'VEHICLE_CONFIGURATION_ID' in self.kc_df.columns:
            top_configs = self.kc_df['VEHICLE_CONFIGURATION_ID'].value_counts().head(8)
            axes[0,1].bar(range(len(top_configs)), top_configs.values, color='purple')
            axes[0,1].set_title('Top Vehicle Configurations')
            axes[0,1].set_xlabel('Vehicle Configuration ID')
            axes[0,1].set_ylabel('Number of Crashes')
            axes[0,1].set_xticks(range(len(top_configs)))
            axes[0,1].set_xticklabels(top_configs.index, rotation=45)
            axes[0,1].grid(True, alpha=0.3)
        
        # 3. GVW distribution
        if 'GVW_RATING_ID' in self.kc_df.columns:
            top_gvw = self.kc_df['GVW_RATING_ID'].value_counts().head(8)
            axes[1,0].bar(range(len(top_gvw)), top_gvw.values, color='green')
            axes[1,0].set_title('Top GVW Ratings')
            axes[1,0].set_xlabel('GVW Rating ID')
            axes[1,0].set_ylabel('Number of Crashes')
            axes[1,0].set_xticks(range(len(top_gvw)))
            axes[1,0].set_xticklabels(top_gvw.index, rotation=45)
            axes[1,0].grid(True, alpha=0.3)
        
        # 4. Vehicle configuration vs severity
        if 'VEHICLE_CONFIGURATION_ID' in self.kc_df.columns and 'FATALITIES' in self.kc_df.columns:
            config_severity = self.kc_df.groupby('VEHICLE_CONFIGURATION_ID')['FATALITIES'].mean().head(10)
            axes[1,1].bar(range(len(config_severity)), config_severity.values, color='red', alpha=0.7)
            axes[1,1].set_title('Average Fatalities by Vehicle Config')
            axes[1,1].set_xlabel('Vehicle Configuration ID')
            axes[1,1].set_ylabel('Average Fatalities')
            axes[1,1].set_xticks(range(len(config_severity)))
            axes[1,1].set_xticklabels(config_severity.index, rotation=45)
            axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def carrier_analysis(self):
        """Analyze carrier and company patterns in Kansas City crashes."""
        if not self.loaded or self.kc_df.empty:
            return
            
        print("\n" + "="*70)
        print("CARRIER & COMPANY ANALYSIS - KANSAS CITY")
        print("="*70)
        
        # Top carriers by crash count
        if 'CRASH_CARRIER_NAME' in self.kc_df.columns:
            print("\nTop 15 Carriers by Crash Count:")
            carrier_counts = self.kc_df['CRASH_CARRIER_NAME'].value_counts().head(15)
            for carrier, count in carrier_counts.items():
                if pd.notna(carrier):
                    print(f"  {carrier}: {count:,} crashes")
        
        # Carrier states
        if 'CRASH_CARRIER_STATE' in self.kc_df.columns:
            print("\nTop 10 Carrier States:")
            carrier_states = self.kc_df['CRASH_CARRIER_STATE'].value_counts().head(10)
            for state, count in carrier_states.items():
                if pd.notna(state):
                    print(f"  {state}: {count:,} crashes ({(count/len(self.kc_df))*100:.1f}%)")
        
        # Interstate carriers
        if 'CRASH_CARRIER_INTERSTATE' in self.kc_df.columns:
            print("\nInterstate vs Intrastate Carriers:")
            interstate_counts = self.kc_df['CRASH_CARRIER_INTERSTATE'].value_counts()
            for interstate, count in interstate_counts.items():
                print(f"  {interstate}: {count:,} crashes ({(count/len(self.kc_df))*100:.1f}%)")
        
        # Create carrier visualizations
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Top carriers
        if 'CRASH_CARRIER_NAME' in self.kc_df.columns:
            top_carriers = self.kc_df['CRASH_CARRIER_NAME'].value_counts().head(10)
            axes[0,0].barh(range(len(top_carriers)), top_carriers.values)
            axes[0,0].set_title('Top 10 Carriers by Crash Count')
            axes[0,0].set_xlabel('Number of Crashes')
            axes[0,0].set_yticks(range(len(top_carriers)))
            axes[0,0].set_yticklabels([str(x)[:30] + '...' if len(str(x)) > 30 else str(x) 
                                     for x in top_carriers.index], fontsize=8)
        
        # 2. Carrier states
        if 'CRASH_CARRIER_STATE' in self.kc_df.columns:
            top_states = self.kc_df['CRASH_CARRIER_STATE'].value_counts().head(10)
            axes[0,1].bar(range(len(top_states)), top_states.values, color='orange')
            axes[0,1].set_title('Top 10 Carrier States')
            axes[0,1].set_xlabel('State')
            axes[0,1].set_ylabel('Number of Crashes')
            axes[0,1].set_xticks(range(len(top_states)))
            axes[0,1].set_xticklabels(top_states.index, rotation=45)
            axes[0,1].grid(True, alpha=0.3)
        
        # 3. Interstate distribution
        if 'CRASH_CARRIER_INTERSTATE' in self.kc_df.columns:
            interstate_counts = self.kc_df['CRASH_CARRIER_INTERSTATE'].value_counts()
            axes[1,0].pie(interstate_counts.values, labels=interstate_counts.index, 
                         autopct='%1.1f%%', startangle=90)
            axes[1,0].set_title('Interstate vs Intrastate Carriers')
        
        # 4. Carrier severity analysis
        if 'CRASH_CARRIER_NAME' in self.kc_df.columns and 'FATALITIES' in self.kc_df.columns:
            carrier_severity = self.kc_df.groupby('CRASH_CARRIER_NAME')['FATALITIES'].mean()
            top_severe_carriers = carrier_severity.sort_values(ascending=False).head(10)
            axes[1,1].barh(range(len(top_severe_carriers)), top_severe_carriers.values, color='red')
            axes[1,1].set_title('Top 10 Carriers by Avg Fatalities')
            axes[1,1].set_xlabel('Average Fatalities per Crash')
            axes[1,1].set_yticks(range(len(top_severe_carriers)))
            axes[1,1].set_yticklabels([str(x)[:25] + '...' if len(str(x)) > 25 else str(x) 
                                     for x in top_severe_carriers.index], fontsize=8)
        
        plt.tight_layout()
        plt.show()
    
    def crash_type_analysis(self):
        """Analyze crash types and sequences in Kansas City."""
        if not self.loaded or self.kc_df.empty:
            return
            
        print("\n" + "="*70)
        print("CRASH TYPE & SEQUENCE ANALYSIS - KANSAS CITY")
        print("="*70)
        
        # Crash event sequences
        if 'CRASH_EVENT_SEQ_ID_DESC' in self.kc_df.columns:
            print("\nTop 15 Crash Event Sequences:")
            crash_events = self.kc_df['CRASH_EVENT_SEQ_ID_DESC'].value_counts().head(15)
            for event, count in crash_events.items():
                if pd.notna(event):
                    event_short = str(event)[:60] + '...' if len(str(event)) > 60 else str(event)
                    print(f"  {event_short}: {count:,} crashes")
        
        # Hazmat involvement
        if 'HAZMAT_RELEASED' in self.kc_df.columns:
            print("\nHazmat Release Distribution:")
            hazmat_counts = self.kc_df['HAZMAT_RELEASED'].value_counts()
            for hazmat, count in hazmat_counts.items():
                print(f"  {hazmat}: {count:,} crashes ({(count/len(self.kc_df))*100:.1f}%)")
        
        # Create crash type visualizations
        fig, axes = plt.subplots(2, 1, figsize=(15, 10))
        
        # 1. Top crash event sequences
        if 'CRASH_EVENT_SEQ_ID_DESC' in self.kc_df.columns:
            top_events = self.kc_df['CRASH_EVENT_SEQ_ID_DESC'].value_counts().head(10)
            axes[0].barh(range(len(top_events)), top_events.values, color='teal')
            axes[0].set_title('Top 10 Crash Event Sequences')
            axes[0].set_xlabel('Number of Crashes')
            axes[0].set_yticks(range(len(top_events)))
            event_labels = [str(x)[:50] + '...' if len(str(x)) > 50 else str(x) 
                           for x in top_events.index]
            axes[0].set_yticklabels(event_labels, fontsize=8)
        
        # 2. Hazmat releases
        if 'HAZMAT_RELEASED' in self.kc_df.columns:
            hazmat_counts = self.kc_df['HAZMAT_RELEASED'].value_counts()
            axes[1].pie(hazmat_counts.values, labels=hazmat_counts.index, 
                       autopct='%1.1f%%', startangle=90)
            axes[1].set_title('Hazmat Release Distribution')
        
        plt.tight_layout()
        plt.show()
    
    def geographic_analysis(self):
        """Analyze geographic patterns within Kansas City."""
        if not self.loaded or self.kc_df.empty:
            return
            
        print("\n" + "="*70)
        print("GEOGRAPHIC ANALYSIS - KANSAS CITY")
        print("="*70)
        
        # County analysis
        if 'COUNTY_CODE' in self.kc_df.columns:
            print("\nTop 10 Counties:")
            county_counts = self.kc_df['COUNTY_CODE'].value_counts().head(10)
            for county, count in county_counts.items():
                print(f"  County {county}: {count:,} crashes ({(count/len(self.kc_df))*100:.1f}%)")
        
        # Location patterns
        if 'LOCATION' in self.kc_df.columns:
            print("\nTop 15 Specific Locations:")
            location_counts = self.kc_df['LOCATION'].value_counts().head(15)
            for location, count in location_counts.items():
                if pd.notna(location):
                    location_short = str(location)[:60] + '...' if len(str(location)) > 60 else str(location)
                    print(f"  {location_short}: {count:,} crashes")
        
        # Access control analysis
        if 'ACCESS_CONTROL_ID' in self.kc_df.columns:
            print("\nAccess Control Distribution:")
            access_counts = self.kc_df['ACCESS_CONTROL_ID'].value_counts()
            for access, count in access_counts.items():
                print(f"  Access Control {access}: {count:,} crashes ({(count/len(self.kc_df))*100:.1f}%)")
    
    def comprehensive_summary(self):
        """Generate comprehensive summary and insights for Kansas City."""
        if not self.loaded or self.kc_df.empty:
            return
            
        print("\n" + "="*70)
        print("COMPREHENSIVE SUMMARY - KANSAS CITY CRASHES")
        print("="*70)
        
        insights = []
        
        # Basic statistics
        insights.append(f"Total Kansas City crashes analyzed: {len(self.kc_df):,}")
        insights.append(f"Data spans from {self.kc_df['YEAR'].min()} to {self.kc_df['YEAR'].max()}")
        
        # Severity insights
        if 'FATALITIES' in self.kc_df.columns:
            total_fatalities = self.kc_df['FATALITIES'].sum()
            fatal_crashes = (self.kc_df['FATALITIES'] > 0).sum()
            insights.append(f"Total fatalities: {total_fatalities:,}")
            insights.append(f"Fatal crash rate: {(fatal_crashes/len(self.kc_df))*100:.2f}%")
            
        if 'INJURIES' in self.kc_df.columns:
            total_injuries = self.kc_df['INJURIES'].sum()
            injury_crashes = (self.kc_df['INJURIES'] > 0).sum()
            insights.append(f"Total injuries: {total_injuries:,}")
            insights.append(f"Injury crash rate: {(injury_crashes/len(self.kc_df))*100:.2f}%")
        
        # Temporal insights
        peak_year = self.kc_df.groupby('YEAR').size().idxmax()
        peak_count = self.kc_df.groupby('YEAR').size().max()
        insights.append(f"Peak crash year: {peak_year} with {peak_count:,} crashes")
        
        if 'MONTH' in self.kc_df.columns:
            peak_month = self.kc_df.groupby('MONTH').size().idxmax()
            month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April',
                          5: 'May', 6: 'June', 7: 'July', 8: 'August',
                          9: 'September', 10: 'October', 11: 'November', 12: 'December'}
            insights.append(f"Peak crash month: {month_names.get(peak_month, peak_month)}")
        
        if 'DAY_OF_WEEK' in self.kc_df.columns:
            peak_dow = self.kc_df.groupby('DAY_OF_WEEK').size().idxmax()
            dow_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
                        4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
            insights.append(f"Peak crash day: {dow_names.get(peak_dow, peak_dow)}")
        
        # Vehicle insights
        if 'TRUCK_BUS_IND' in self.kc_df.columns:
            truck_pct = (self.kc_df['TRUCK_BUS_IND'] == 'T').sum() / len(self.kc_df) * 100
            insights.append(f"Truck crashes: {truck_pct:.1f}% of total")
        
        # State breakdown
        state_breakdown = self.kc_df['REPORT_STATE'].value_counts()
        for state, count in state_breakdown.items():
            insights.append(f"{state} crashes: {count:,} ({(count/len(self.kc_df))*100:.1f}%)")
        
        print("\nKey Insights:")
        for i, insight in enumerate(insights, 1):
            print(f"{i:2d}. {insight}")
        
        print("\n" + "="*70)
        print("KANSAS CITY ANALYSIS COMPLETE")
        print("="*70)
    
    def run_full_analysis(self):
        """Run the complete Kansas City analysis."""
        print("Starting comprehensive Kansas City crash analysis...")
        
        if not self.load_data():
            return
            
        if self.kc_df.empty:
            print("No Kansas City data found in the dataset.")
            return
            
        self.basic_overview()
        self.temporal_analysis()
        self.severity_analysis()
        self.environmental_analysis()
        self.vehicle_analysis()
        self.carrier_analysis()
        self.crash_type_analysis()
        self.geographic_analysis()
        self.comprehensive_summary()


def main():
    """Main function to run the Kansas City analysis."""
    # Initialize the analyzer
    data_path = "./data/Crash_File_20250712.csv"
    analyzer = KansasCityAnalyzer(data_path)
    
    # Run the full analysis
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main() 