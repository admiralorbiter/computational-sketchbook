#!/usr/bin/env python3
"""
ACS Data Import - Targeted Categories

This script allows importing specific ACS data categories without re-importing everything.

Usage:
    # Import specific categories:
    python tools/etl/import_categories.py --categories health_insurance,disability

    # Import all missing configured categories:
    python tools/etl/import_categories.py --all-missing

    # List available categories:
    python tools/etl/import_categories.py --list
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import functions from main ETL script
from tools.etl.load_acs_data import (
    fetch_acs_batch, load_to_database, setup_logging,
    KC_COUNTIES,
    ACS_HEALTH_INSURANCE_VARIABLES,
    ACS_DISABILITY_VARIABLES,
    ACS_LANGUAGE_VARIABLES,
    ACS_CITIZENSHIP_VARIABLES,
    ACS_GRANDPARENTS_VARIABLES,
    ACS_SCHOOL_ENROLLMENT_VARIABLES,
    ACS_MIGRATION_VARIABLES,
    ACS_GROUP_QUARTERS_VARIABLES,
    ACS_INCOME_BY_SOURCE_VARIABLES,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Map category names to their variable dictionaries
CATEGORY_VARIABLES = {
    'health_insurance': ACS_HEALTH_INSURANCE_VARIABLES,
    'disability': ACS_DISABILITY_VARIABLES,
    'language': ACS_LANGUAGE_VARIABLES,
    'citizenship': ACS_CITIZENSHIP_VARIABLES,
    'grandparents': ACS_GRANDPARENTS_VARIABLES,
    'school_enrollment': ACS_SCHOOL_ENROLLMENT_VARIABLES,
    'migration': ACS_MIGRATION_VARIABLES,
    'group_quarters': ACS_GROUP_QUARTERS_VARIABLES,
    'income_by_source': ACS_INCOME_BY_SOURCE_VARIABLES,
}

# Categories configured to import but currently missing data
MISSING_CONFIGURED_CATEGORIES = [
    'health_insurance',
    'disability',
    'language',
    'citizenship',
]


def import_categories(category_names, logger):
    """Import specified ACS categories for all counties"""
    
    all_batches = []
    categories_imported = 0
    
    # Fetch data for each county
    for state_fips, county_fips, county_name in KC_COUNTIES:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {county_name} County, {county_fips}")
        logger.info(f"{'='*60}")
        
        county_batches = []
        
        # Fetch each requested category
        for category_name in category_names:
            if category_name not in CATEGORY_VARIABLES:
                logger.warning(f"Unknown category: {category_name}")
                continue
            
            variables = CATEGORY_VARIABLES[category_name]
            
            # Format category name for display
            display_name = category_name.replace('_', ' ').title()
            logger.info(f"Fetching {display_name} data...")
            
            df = fetch_acs_batch(state_fips, county_fips, variables, logger, display_name)
            if df is not None:
                county_batches.append(df)
                logger.info(f"[OK] {display_name} data fetched for county {county_name}")
            else:
                logger.warning(f"[X] {display_name} data failed for county {county_name}")
        
        if county_batches:
            all_batches.append(county_batches)
    
    # Load all data to database
    if all_batches:
        logger.info("\n" + "="*60)
        logger.info("Loading all data to database...")
        logger.info("="*60 + "\n")
        
        # Flatten the list of batches
        flat_batches = []
        for county_batches in all_batches:
            flat_batches.extend(county_batches)
        
        # Process all batches together as one import
        logger.info(f"\nProcessing {len(flat_batches)} batches together...")
        load_to_database(flat_batches, logger)
        
        categories_imported = len(category_names)
        logger.info(f"\n[OK] Successfully imported {categories_imported} categories!")
    else:
        logger.error("\n[X] No data fetched. Check errors above.")
    
    return categories_imported


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Import specific ACS data categories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/etl/import_categories.py --categories health_insurance,disability
  python tools/etl/import_categories.py --all-missing
  python tools/etl/import_categories.py --list
        """
    )
    
    parser.add_argument(
        '--categories',
        type=str,
        help='Comma-separated list of categories to import'
    )
    
    parser.add_argument(
        '--all-missing',
        action='store_true',
        help='Import all missing configured categories'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available categories'
    )
    
    args = parser.parse_args()
    
    logger.info("\n" + "="*60)
    logger.info("ACS Data Import - Targeted Categories")
    logger.info("="*60 + "\n")
    
    # List categories
    if args.list:
        logger.info("Available categories:")
        for category, variables in CATEGORY_VARIABLES.items():
            print(f"  - {category}")
            print(f"    ({len(variables)} variables)")
        logger.info(f"\nMissing configured categories:")
        for category in MISSING_CONFIGURED_CATEGORIES:
            print(f"  - {category}")
        return
    
    # Determine which categories to import
    if args.all_missing:
        category_names = MISSING_CONFIGURED_CATEGORIES
        logger.info(f"Importing all missing configured categories: {', '.join(category_names)}")
    elif args.categories:
        category_names = [c.strip() for c in args.categories.split(',')]
        logger.info(f"Importing categories: {', '.join(category_names)}")
    else:
        parser.print_help()
        return
    
    # Validate categories
    for category in category_names:
        if category not in CATEGORY_VARIABLES:
            logger.error(f"Unknown category: {category}")
            logger.error(f"Available categories: {', '.join(CATEGORY_VARIABLES.keys())}")
            return
    
    # Run the import
    import_categories(category_names, logger)


if __name__ == "__main__":
    main()

