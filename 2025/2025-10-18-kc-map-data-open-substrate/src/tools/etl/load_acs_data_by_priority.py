#!/usr/bin/env python3
"""
ACS Data Import by Priority

This script allows incremental import of ACS data by priority level.
Use this to import new variables without re-importing everything.

Usage:
    # Import P0 (Critical) variables
    python tools/etl/load_acs_data_by_priority.py --priority P0
    
    # Import P1 (High) variables
    python tools/etl/load_acs_data_by_priority.py --priority P1
    
    # Import all remaining
    python tools/etl/load_acs_data_by_priority.py --priority all
"""

import os
import sys
import argparse
import logging
import pandas as pd
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.etl.load_acs_data import (
    fetch_acs_batch, load_to_database, setup_logging,
    ACS_COMPUTER_INTERNET_VARIABLES,
    ACS_DETAILED_RACE_VARIABLES,
    ACS_OCCUPATION_DETAILED_VARIABLES,
    ACS_INDUSTRY_DETAILED_VARIABLES,
    ACS_COMMUTE_TIME_VARIABLES,
    ACS_MIGRATION_VARIABLES,
    ACS_MARITAL_STATUS_VARIABLES,
    ACS_FERTILITY_VARIABLES,
    ACS_GRANDPARENTS_VARIABLES,
    ACS_GROUP_QUARTERS_VARIABLES,
    ACS_SCHOOL_ENROLLMENT_VARIABLES,
    ACS_INCOME_BY_SOURCE_VARIABLES,
    KC_COUNTIES
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Priority groupings
PRIORITY_CONFIG = {
    'P0': {
        'name': 'Critical',
        'description': 'Essential variables for most analyses',
        'categories': ['computer_internet']  # Occupation and industry not available at block group level
    },
    'P1': {
        'name': 'High Value',
        'description': 'Important for detailed demographic analysis',
        'categories': ['detailed_race', 'migration', 'marital_status']
    },
    'P2': {
        'name': 'Medium Value',
        'description': 'Useful for specific analyses',
        'categories': ['fertility', 'grandparents', 'group_quarters', 'school_enrollment', 'income_by_source']
    },
    'P3': {
        'name': 'Nice-to-Have',
        'description': 'Additional detail for comprehensive analysis',
        'categories': ['commute_time']
    }
}

# Mapping from category names to variable dictionaries
CATEGORY_VARIABLES = {
    'computer_internet': ACS_COMPUTER_INTERNET_VARIABLES,
    'detailed_race': ACS_DETAILED_RACE_VARIABLES,
    'occupation_detailed': ACS_OCCUPATION_DETAILED_VARIABLES,
    'industry_detailed': ACS_INDUSTRY_DETAILED_VARIABLES,
    'commute_time': ACS_COMMUTE_TIME_VARIABLES,
    'migration': ACS_MIGRATION_VARIABLES,
    'marital_status': ACS_MARITAL_STATUS_VARIABLES,
    'fertility': ACS_FERTILITY_VARIABLES,
    'grandparents': ACS_GRANDPARENTS_VARIABLES,
    'group_quarters': ACS_GROUP_QUARTERS_VARIABLES,
    'school_enrollment': ACS_SCHOOL_ENROLLMENT_VARIABLES,
    'income_by_source': ACS_INCOME_BY_SOURCE_VARIABLES,
}


def import_by_priority(priority_level):
    """Import ACS data by priority level"""
    
    import pandas as pd
    
    logger.info(f"Starting ACS import for priority {priority_level}")
    
    if priority_level == 'all':
        categories = []
        for p in ['P0', 'P1', 'P2', 'P3']:
            categories.extend(PRIORITY_CONFIG[p]['categories'])
    elif priority_level in PRIORITY_CONFIG:
        categories = PRIORITY_CONFIG[priority_level]['categories']
    else:
        logger.error(f"Invalid priority level: {priority_level}")
        logger.info(f"Valid levels: all, P0, P1, P2, P3")
        return False
    
    logger.info(f"Importing {len(categories)} categories for priority {priority_level}")
    
    all_data = []
    
    # Fetch data for each category and county
    for category in categories:
        if category not in CATEGORY_VARIABLES:
            logger.warning(f"Unknown category: {category}")
            continue
        
        variables = CATEGORY_VARIABLES[category]
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing category: {category}")
        logger.info(f"Variables: {len(variables)}")
        logger.info(f"{'='*60}\n")
        
        for state_fips, county_fips, county_name in KC_COUNTIES:
            logger.info(f"Fetching {category} for {county_name} County...")
            
            df = fetch_acs_batch(state_fips, county_fips, variables, logger, category)
            if df is not None:
                all_data.append(df)
    
    if not all_data:
        logger.error("No data fetched")
        return False
    
    # Combine all data
    logger.info("\nCombining data from all categories and counties...")
    combined_df = pd.concat(all_data, ignore_index=True)
    
    logger.info(f"Total block groups: {len(combined_df)}")
    logger.info(f"Columns: {combined_df.columns.tolist()}")
    
    # Load to database
    load_to_database(combined_df, logger)
    
    logger.info(f"\nACS Data ETL Complete for priority {priority_level}!")
    return True


def print_status():
    """Print current import status"""
    print("\nACS Import Priority System")
    print("=" * 60)
    
    for priority, config in PRIORITY_CONFIG.items():
        print(f"\n{priority} - {config['name']}")
        print(f"  Description: {config['description']}")
        print(f"  Categories: {len(config['categories'])}")
        for cat in config['categories']:
            if cat in CATEGORY_VARIABLES:
                var_count = len(CATEGORY_VARIABLES[cat])
                print(f"    - {cat} ({var_count} variables)")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Import ACS data by priority')
    parser.add_argument(
        '--priority',
        choices=['all', 'P0', 'P1', 'P2', 'P3', 'status'],
        default='status',
        help='Priority level to import (status prints current status)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be imported without actually importing'
    )
    
    args = parser.parse_args()
    
    if args.priority == 'status':
        print_status()
        return
    
    if args.dry_run:
        print("\nDRY RUN MODE - Would import:")
        if args.priority == 'all':
            categories = []
            for p in ['P0', 'P1', 'P2', 'P3']:
                categories.extend(PRIORITY_CONFIG[p]['categories'])
        else:
            categories = PRIORITY_CONFIG[args.priority]['categories']
        
        print(f"\nPriority: {args.priority}")
        print(f"Categories: {len(categories)}")
        for cat in categories:
            if cat in CATEGORY_VARIABLES:
                var_count = len(CATEGORY_VARIABLES[cat])
                print(f"  - {cat}: {var_count} variables")
        return
    
    # Import the data
    import pandas as pd  # Import here to avoid issues if not needed
    
    success = import_by_priority(args.priority)
    
    if success:
        print(f"\nSuccessfully imported ACS data for priority {args.priority}")
    else:
        print(f"\nFailed to import ACS data for priority {args.priority}")
        sys.exit(1)


if __name__ == "__main__":
    # Import pandas here in main to avoid issues if not needed
    import pandas as pd
    main()

