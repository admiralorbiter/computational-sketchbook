#!/usr/bin/env python3
"""
Create Block Group Aggregations Table

Creates a table to store pre-computed aggregations of various data types
by block group for fast analysis queries.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import sqlite3
from web.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_aggregations_table():
    """Create the block_group_aggregations table"""
    
    # Get database path
    current_config = config['development']
    db_path = current_config.DATABASE_URL.replace('sqlite:///', '')
    
    if not os.path.exists(db_path):
        logger.error(f"Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create the aggregations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS block_group_aggregations (
            geoid TEXT PRIMARY KEY,
            total_crime_incidents INTEGER DEFAULT 0,
            total_311_requests INTEGER DEFAULT 0,
            total_businesses INTEGER DEFAULT 0,
            total_dangerous_buildings INTEGER DEFAULT 0,
            total_landbank_properties INTEGER DEFAULT 0,
            
            -- JSON fields for breakdowns
            crime_by_type TEXT,
            crime_by_offense TEXT,
            sr_by_type TEXT,
            sr_by_issue_type TEXT,
            business_by_type TEXT,
            business_by_industry TEXT,
            
            -- Metadata
            last_computed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create indexes
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_aggregations_last_computed 
        ON block_group_aggregations(last_computed)
        """)
        
        logger.info("Successfully created block_group_aggregations table")
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error creating aggregations table: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


if __name__ == '__main__':
    success = create_aggregations_table()
    sys.exit(0 if success else 1)

