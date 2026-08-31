"""
Comprehensive Data Exploration for Crash Data
============================================

This script performs an in-depth analysis of the crash data from the Department of Transportation,
examining patterns in crashes, severity, temporal trends, geographic distribution, and vehicle characteristics.
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

class CrashDataExplorer:
    """
    A comprehensive crash data analysis class that provides various analytical methods
    for exploring crash patterns, trends, and characteristics.
    """
    
    def __init__(self, data_path):
        """Initialize the explorer with the crash data file path."""
        self.data_path = data_path
        self.df = None
        self.loaded = False
        
    def load_data(self):
        """Load the crash data with proper data type handling."""
        print("Loading crash data...")
        print(f"File path: {self.data_path}")
        
        try:
            # Load with low_memory=False to avoid mixed types warning
            self.df = pd.read_csv(self.data_path, low_memory=False)
            self.loaded = True
            print(f"✓ Data loaded successfully!")
            print(f"Dataset shape: {self.df.shape}")
            
            # Convert date columns
            self._process_date_columns()
            
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
            # Convert time to proper format (assuming HHMM format)
            self.df['REPORT_TIME_STR'] = self.df['REPORT_TIME'].astype(str).str.zfill(4)
            self.df['REPORT_HOUR'] = self.df['REPORT_TIME_STR'].str[:2].astype(int, errors='ignore')
            
        print("✓ Date columns processed")
    
    def basic_info(self):
        """Display basic information about the dataset."""
        if not self.loaded:
            print("Please load data first using load_data()")
            return
            
        print("\n" + "="*60)
        print("BASIC DATASET INFORMATION")
        print("="*60)
        
        print(f"Dataset shape: {self.df.shape}")
        print(f"Memory usage: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        print(f"\nColumn names ({len(self.df.columns)}):")
        for i, col in enumerate(self.df.columns):
            print(f"{i+1:2d}. {col}")
        
        print(f"\nData types:")
        print(self.df.dtypes.value_counts())
        
        print(f"\nFirst few rows:")
        print(self.df.head())
        
    def data_quality_analysis(self):
        """Perform comprehensive data quality analysis."""
        if not self.loaded:
            print("Please load data first using load_data()")
            return
            
        print("\n" + "="*60)
        print("DATA QUALITY ANALYSIS")
        print("="*60)
        
        # Missing values analysis
        print("\nMissing Values Analysis:")
        missing_data = self.df.isnull().sum()
        missing_percentage = (missing_data / len(self.df)) * 100
        
        missing_df = pd.DataFrame({
            'Missing_Count': missing_data,
            'Missing_Percentage': missing_percentage
        }).sort_values('Missing_Percentage', ascending=False)
        
        print(missing_df[missing_df['Missing_Count'] > 0].head(15))
        
        # Duplicate analysis
        print(f"\nDuplicate Records:")
        duplicates = self.df.duplicated().sum()
        print(f"Total duplicate rows: {duplicates}")
        if duplicates > 0:
            print(f"Duplicate percentage: {(duplicates/len(self.df))*100:.2f}%")
            
        # Unique values in key columns
        print(f"\nUnique Values in Key Columns:")
        key_columns = ['CRASH_ID', 'REPORT_STATE', 'CITY', 'COUNTY_CODE', 'TRUCK_BUS_IND']
        for col in key_columns:
            if col in self.df.columns:
                unique_count = self.df[col].nunique()
                print(f"{col}: {unique_count:,} unique values")
        
        # Data range analysis for numeric columns
        print(f"\nNumeric Columns Summary:")
        numeric_cols = ['FATALITIES', 'INJURIES', 'VEHICLES_IN_ACCIDENT']
        for col in numeric_cols:
            if col in self.df.columns:
                print(f"\n{col}:")
                print(f"  Range: {self.df[col].min()} to {self.df[col].max()}")
                print(f"  Mean: {self.df[col].mean():.2f}")
                print(f"  Median: {self.df[col].median():.2f}")
                
    def temporal_analysis(self):
        """Analyze temporal patterns in crash data."""
        if not self.loaded:
            print("Please load data first using load_data()")
            return
            
        print("\n" + "="*60)
        print("TEMPORAL ANALYSIS")
        print("="*60)
        
        # Year-over-year trends
        if 'REPORT_DATE' in self.df.columns:
            self.df['YEAR'] = self.df['REPORT_DATE'].dt.year
            self.df['MONTH'] = self.df['REPORT_DATE'].dt.month
            self.df['DAY_OF_WEEK'] = self.df['REPORT_DATE'].dt.dayofweek
            
            print("\nCrashes by Year:")
            yearly_crashes = self.df.groupby('YEAR').size().sort_index()
            print(yearly_crashes)
            
            # Plot yearly trends
            plt.figure(figsize=(12, 6))
            yearly_crashes.plot(kind='line', marker='o')
            plt.title('Crash Trends by Year')
            plt.xlabel('Year')
            plt.ylabel('Number of Crashes')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
            
            # Monthly patterns
            print("\nCrashes by Month:")
            monthly_crashes = self.df.groupby('MONTH').size()
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            plt.figure(figsize=(12, 6))
            plt.bar(range(1, 13), monthly_crashes, color='skyblue')
            plt.title('Crash Distribution by Month')
            plt.xlabel('Month')
            plt.ylabel('Number of Crashes')
            plt.xticks(range(1, 13), month_names)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
            
            # Day of week patterns
            print("\nCrashes by Day of Week:")
            dow_crashes = self.df.groupby('DAY_OF_WEEK').size()
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            plt.figure(figsize=(10, 6))
            plt.bar(range(7), dow_crashes, color='lightcoral')
            plt.title('Crash Distribution by Day of Week')
            plt.xlabel('Day of Week')
            plt.ylabel('Number of Crashes')
            plt.xticks(range(7), day_names, rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
            
        # Time of day analysis
        if 'REPORT_HOUR' in self.df.columns:
            print("\nCrashes by Hour of Day:")
            hourly_crashes = self.df.groupby('REPORT_HOUR').size()
            
            plt.figure(figsize=(12, 6))
            plt.plot(hourly_crashes.index, hourly_crashes.values, marker='o', linewidth=2)
            plt.title('Crash Distribution by Hour of Day')
            plt.xlabel('Hour of Day')
            plt.ylabel('Number of Crashes')
            plt.grid(True, alpha=0.3)
            plt.xticks(range(0, 24))
            plt.tight_layout()
            plt.show()
    
    def geographic_analysis(self):
        """Analyze geographic patterns in crash data."""
        if not self.loaded:
            print("Please load data first using load_data()")
            return
            
        print("\n" + "="*60)
        print("GEOGRAPHIC ANALYSIS")
        print("="*60)
        
        # State-wise analysis
        if 'REPORT_STATE' in self.df.columns:
            print("\nTop 15 States by Number of Crashes:")
            state_crashes = self.df['REPORT_STATE'].value_counts().head(15)
            print(state_crashes)
            
            # Plot top states
            plt.figure(figsize=(12, 8))
            state_crashes.plot(kind='bar', color='lightgreen')
            plt.title('Top 15 States by Number of Crashes')
            plt.xlabel('State')
            plt.ylabel('Number of Crashes')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
            
        # City analysis
        if 'CITY' in self.df.columns:
            print("\nTop 15 Cities by Number of Crashes:")
            city_crashes = self.df['CITY'].value_counts().head(15)
            print(city_crashes)
            
            # Plot top cities
            plt.figure(figsize=(12, 8))
            city_crashes.plot(kind='bar', color='orange')
            plt.title('Top 15 Cities by Number of Crashes')
            plt.xlabel('City')
            plt.ylabel('Number of Crashes')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
    
    def severity_analysis(self):
        """Analyze crash severity patterns."""
        if not self.loaded:
            print("Please load data first using load_data()")
            return
            
        print("\n" + "="*60)
        print("CRASH SEVERITY ANALYSIS")
        print("="*60)
        
        # Fatality analysis
        if 'FATALITIES' in self.df.columns:
            print("\nFatality Statistics:")
            fatality_stats = self.df['FATALITIES'].describe()
            print(fatality_stats)
            
            print(f"\nCrashes with fatalities: {(self.df['FATALITIES'] > 0).sum():,}")
            print(f"Percentage of fatal crashes: {((self.df['FATALITIES'] > 0).sum()/len(self.df))*100:.2f}%")
            
            # Fatality distribution
            plt.figure(figsize=(10, 6))
            fatality_counts = self.df['FATALITIES'].value_counts().sort_index()
            plt.bar(fatality_counts.index[:10], fatality_counts.values[:10], color='red', alpha=0.7)
            plt.title('Distribution of Fatalities per Crash')
            plt.xlabel('Number of Fatalities')
            plt.ylabel('Number of Crashes')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
            
        # Injury analysis
        if 'INJURIES' in self.df.columns:
            print("\nInjury Statistics:")
            injury_stats = self.df['INJURIES'].describe()
            print(injury_stats)
            
            print(f"\nCrashes with injuries: {(self.df['INJURIES'] > 0).sum():,}")
            print(f"Percentage of injury crashes: {((self.df['INJURIES'] > 0).sum()/len(self.df))*100:.2f}%")
            
        # Vehicles involved analysis
        if 'VEHICLES_IN_ACCIDENT' in self.df.columns:
            print("\nVehicles Involved Statistics:")
            vehicle_stats = self.df['VEHICLES_IN_ACCIDENT'].describe()
            print(vehicle_stats)
            
            plt.figure(figsize=(10, 6))
            vehicle_counts = self.df['VEHICLES_IN_ACCIDENT'].value_counts().sort_index()
            plt.bar(vehicle_counts.index[:10], vehicle_counts.values[:10], color='blue', alpha=0.7)
            plt.title('Distribution of Vehicles Involved per Crash')
            plt.xlabel('Number of Vehicles')
            plt.ylabel('Number of Crashes')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
    
    def environmental_analysis(self):
        """Analyze environmental factors in crashes."""
        if not self.loaded:
            print("Please load data first using load_data()")
            return
            
        print("\n" + "="*60)
        print("ENVIRONMENTAL FACTORS ANALYSIS")
        print("="*60)
        
        # Weather conditions
        if 'WEATHER_CONDITION_ID' in self.df.columns:
            print("\nWeather Conditions:")
            weather_counts = self.df['WEATHER_CONDITION_ID'].value_counts()
            print(weather_counts.head(10))
            
            plt.figure(figsize=(10, 6))
            weather_counts.head(10).plot(kind='bar', color='lightblue')
            plt.title('Top 10 Weather Conditions in Crashes')
            plt.xlabel('Weather Condition ID')
            plt.ylabel('Number of Crashes')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
            
        # Light conditions
        if 'LIGHT_CONDITION_ID' in self.df.columns:
            print("\nLight Conditions:")
            light_counts = self.df['LIGHT_CONDITION_ID'].value_counts()
            print(light_counts.head(10))
            
            plt.figure(figsize=(10, 6))
            light_counts.head(10).plot(kind='bar', color='yellow')
            plt.title('Top 10 Light Conditions in Crashes')
            plt.xlabel('Light Condition ID')
            plt.ylabel('Number of Crashes')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
    
    def vehicle_analysis(self):
        """Analyze vehicle characteristics in crashes."""
        if not self.loaded:
            print("Please load data first using load_data()")
            return
            
        print("\n" + "="*60)
        print("VEHICLE CHARACTERISTICS ANALYSIS")
        print("="*60)
        
        # Truck vs Bus analysis
        if 'TRUCK_BUS_IND' in self.df.columns:
            print("\nTruck vs Bus Distribution:")
            truck_bus_counts = self.df['TRUCK_BUS_IND'].value_counts()
            print(truck_bus_counts)
            
            plt.figure(figsize=(8, 6))
            truck_bus_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90)
            plt.title('Distribution of Truck vs Bus Crashes')
            plt.ylabel('')
            plt.tight_layout()
            plt.show()
            
        # Vehicle configuration analysis
        if 'VEHICLE_CONFIGURATION_ID' in self.df.columns:
            print("\nVehicle Configuration:")
            config_counts = self.df['VEHICLE_CONFIGURATION_ID'].value_counts()
            print(config_counts.head(10))
            
            plt.figure(figsize=(12, 6))
            config_counts.head(10).plot(kind='bar', color='purple')
            plt.title('Top 10 Vehicle Configurations in Crashes')
            plt.xlabel('Vehicle Configuration ID')
            plt.ylabel('Number of Crashes')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
    
    def correlation_analysis(self):
        """Analyze correlations between different factors."""
        if not self.loaded:
            print("Please load data first using load_data()")
            return
            
        print("\n" + "="*60)
        print("CORRELATION ANALYSIS")
        print("="*60)
        
        # Select numeric columns for correlation analysis
        numeric_cols = ['FATALITIES', 'INJURIES', 'VEHICLES_IN_ACCIDENT', 'WEATHER_CONDITION_ID',
                       'LIGHT_CONDITION_ID', 'VEHICLE_CONFIGURATION_ID']
        
        existing_cols = [col for col in numeric_cols if col in self.df.columns]
        
        if len(existing_cols) > 1:
            corr_matrix = self.df[existing_cols].corr()
            
            plt.figure(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=0.5)
            plt.title('Correlation Matrix of Crash Factors')
            plt.tight_layout()
            plt.show()
            
            print("\nCorrelation Matrix:")
            print(corr_matrix)
    
    def summary_insights(self):
        """Generate summary insights and key findings."""
        if not self.loaded:
            print("Please load data first using load_data()")
            return
            
        print("\n" + "="*60)
        print("SUMMARY INSIGHTS")
        print("="*60)
        
        insights = []
        
        # Basic statistics
        insights.append(f"Total crashes in dataset: {len(self.df):,}")
        
        # Severity insights
        if 'FATALITIES' in self.df.columns:
            total_fatalities = self.df['FATALITIES'].sum()
            fatal_crashes = (self.df['FATALITIES'] > 0).sum()
            insights.append(f"Total fatalities: {total_fatalities:,}")
            insights.append(f"Fatal crashes: {fatal_crashes:,} ({(fatal_crashes/len(self.df))*100:.1f}%)")
            
        if 'INJURIES' in self.df.columns:
            total_injuries = self.df['INJURIES'].sum()
            injury_crashes = (self.df['INJURIES'] > 0).sum()
            insights.append(f"Total injuries: {total_injuries:,}")
            insights.append(f"Injury crashes: {injury_crashes:,} ({(injury_crashes/len(self.df))*100:.1f}%)")
            
        # Temporal insights
        if 'YEAR' in self.df.columns:
            year_range = f"{self.df['YEAR'].min()} to {self.df['YEAR'].max()}"
            insights.append(f"Data spans from {year_range}")
            
        # Geographic insights
        if 'REPORT_STATE' in self.df.columns:
            top_state = self.df['REPORT_STATE'].value_counts().index[0]
            insights.append(f"State with most crashes: {top_state}")
            
        print("\nKey Insights:")
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
        
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
    
    def run_full_analysis(self):
        """Run the complete analysis pipeline."""
        print("Starting comprehensive crash data analysis...")
        
        if not self.load_data():
            return
            
        self.basic_info()
        self.data_quality_analysis()
        self.temporal_analysis()
        self.geographic_analysis()
        self.severity_analysis()
        self.environmental_analysis()
        self.vehicle_analysis()
        self.correlation_analysis()
        self.summary_insights()


def main():
    """Main function to run the crash data exploration."""
    # Initialize the crash data explorer
    data_path = "./data/Crash_File_20250712.csv"
    explorer = CrashDataExplorer(data_path)
    
    # Run the full analysis
    explorer.run_full_analysis()


if __name__ == "__main__":
    main()
