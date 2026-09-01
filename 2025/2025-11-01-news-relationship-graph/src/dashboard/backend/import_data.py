#!/usr/bin/env python3
"""
Import CSV data into SQLite database for the news dashboard.

This script reads the tagged_output.csv and relationships_output.csv files
and imports them into a SQLite database with proper schema and indexes.
"""

import sqlite3
import csv
import json
import logging
from pathlib import Path
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent
DB_FILE = BASE_DIR / "news.db"
TAGGED_CSV = BASE_DIR.parent.parent / "tagged_output.csv"
REL_CSV = BASE_DIR.parent.parent / "relationships_output.csv"

# Database schema
SCHEMA = """
-- Articles table
CREATE TABLE IF NOT EXISTS articles (
    article_id TEXT PRIMARY KEY,
    title TEXT,
    date TEXT,
    url TEXT,
    summary TEXT,
    category TEXT,
    tags TEXT,  -- JSON array
    notes TEXT
);

-- Relationships table
CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT,
    target_id TEXT,
    rel_type TEXT,
    strength REAL,
    method TEXT,
    reason TEXT,
    people_connection TEXT,
    org_connection TEXT,
    FOREIGN KEY (source_id) REFERENCES articles(article_id),
    FOREIGN KEY (target_id) REFERENCES articles(article_id)
);

-- People table
CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT,
    person_name TEXT,
    FOREIGN KEY (article_id) REFERENCES articles(article_id)
);

-- Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT,
    org_name TEXT,
    FOREIGN KEY (article_id) REFERENCES articles(article_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_articles_date ON articles(date);
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_id);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_id);
CREATE INDEX IF NOT EXISTS idx_people_name ON people(person_name);
CREATE INDEX IF NOT EXISTS idx_orgs_name ON organizations(org_name);
"""


def create_database():
    """Create database and schema."""
    if DB_FILE.exists():
        logger.info(f"Database {DB_FILE} already exists. Deleting...")
        DB_FILE.unlink()
    
    logger.info(f"Creating database: {DB_FILE}")
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    
    # Create schema
    cursor.executescript(SCHEMA)
    conn.commit()
    
    logger.info("Database schema created successfully")
    return conn


def parse_csv_value(value: str) -> str:
    """Parse CSV value, handling quotes and newlines."""
    if not value:
        return ""
    return value.strip()


def import_articles(conn: sqlite3.Connection):
    """Import articles from tagged_output.csv."""
    logger.info("Importing articles from tagged_output.csv...")
    
    if not TAGGED_CSV.exists():
        logger.error(f"Tagged CSV not found: {TAGGED_CSV}")
        return
    
    cursor = conn.cursor()
    
    with open(TAGGED_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        article_count = 0
        seen_ids = set()
        people_records = []
        org_records = []
        
        for row in reader:
            article_id = parse_csv_value(row.get('Article_ID', ''))
            if not article_id:
                continue
            
            # Skip if already seen (duplicate handling)
            if article_id in seen_ids:
                logger.warning(f"  Skipping duplicate article_id: {article_id}")
                continue
            seen_ids.add(article_id)
            
            # Insert article
            cursor.execute("""
                INSERT INTO articles (article_id, title, date, url, summary, category, tags, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article_id,
                parse_csv_value(row.get('Title', '')),
                parse_csv_value(row.get('Date', '')),
                parse_csv_value(row.get('URL', '')),
                parse_csv_value(row.get('Summary', '')),
                parse_csv_value(row.get('Primary_Category', '')),
                parse_csv_value(row.get('Tags', '')),
                parse_csv_value(row.get('Notes', ''))
            ))
            
            # Parse people
            people_str = parse_csv_value(row.get('Key_People', ''))
            if people_str:
                people = [p.strip() for p in people_str.split(',') if p.strip()]
                for person in people:
                    people_records.append((article_id, person))
            
            # Parse organizations
            orgs_str = parse_csv_value(row.get('Key_Organizations', ''))
            if orgs_str:
                orgs = [o.strip() for o in orgs_str.split(',') if o.strip()]
                for org in orgs:
                    org_records.append((article_id, org))
            
            article_count += 1
            
            if article_count % 100 == 0:
                logger.info(f"  Imported {article_count} articles...")
    
    # Bulk insert people
    if people_records:
        cursor.executemany("""
            INSERT INTO people (article_id, person_name)
            VALUES (?, ?)
        """, people_records)
        logger.info(f"  Imported {len(people_records)} people records")
    
    # Bulk insert organizations
    if org_records:
        cursor.executemany("""
            INSERT INTO organizations (article_id, org_name)
            VALUES (?, ?)
        """, org_records)
        logger.info(f"  Imported {len(org_records)} organization records")
    
    conn.commit()
    logger.info(f"Successfully imported {article_count} articles")


def import_relationships(conn: sqlite3.Connection):
    """Import relationships from relationships_output.csv."""
    logger.info("Importing relationships from relationships_output.csv...")
    
    if not REL_CSV.exists():
        logger.error(f"Relationships CSV not found: {REL_CSV}")
        return
    
    cursor = conn.cursor()
    
    with open(REL_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        rel_count = 0
        batch_size = 1000
        batch = []
        
        for row in reader:
            source_id = parse_csv_value(row.get('Source_Article_ID', ''))
            target_id = parse_csv_value(row.get('Target_Article_ID', ''))
            
            if not source_id or not target_id:
                continue
            
            batch.append((
                source_id,
                target_id,
                parse_csv_value(row.get('Relationship_Type', '')),
                float(row.get('Strength', 0.0)),
                parse_csv_value(row.get('Method', '')),
                parse_csv_value(row.get('Reason', '')),
                parse_csv_value(row.get('People_Connection', '')),
                parse_csv_value(row.get('Org_Connection', ''))
            ))
            
            if len(batch) >= batch_size:
                cursor.executemany("""
                    INSERT INTO relationships 
                    (source_id, target_id, rel_type, strength, method, reason, people_connection, org_connection)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, batch)
                rel_count += len(batch)
                logger.info(f"  Imported {rel_count} relationships...")
                batch = []
        
        # Insert remaining batch
        if batch:
            cursor.executemany("""
                INSERT INTO relationships 
                (source_id, target_id, rel_type, strength, method, reason, people_connection, org_connection)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, batch)
            rel_count += len(batch)
    
    conn.commit()
    logger.info(f"Successfully imported {rel_count} relationships")


def main():
    """Main import function."""
    logger.info("Starting database import...")
    
    try:
        # Create database
        conn = create_database()
        
        # Import data
        import_articles(conn)
        import_relationships(conn)
        
        # Print statistics
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles")
        article_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM relationships")
        rel_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT person_name) FROM people")
        people_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT org_name) FROM organizations")
        org_count = cursor.fetchone()[0]
        
        logger.info("\n" + "="*50)
        logger.info("DATABASE IMPORT COMPLETE")
        logger.info("="*50)
        logger.info(f"Articles: {article_count}")
        logger.info(f"Relationships: {rel_count}")
        logger.info(f"Unique People: {people_count}")
        logger.info(f"Unique Organizations: {org_count}")
        logger.info("="*50)
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error during import: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

