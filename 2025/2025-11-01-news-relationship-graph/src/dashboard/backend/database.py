#!/usr/bin/env python3
"""
Database utilities for news dashboard.

Provides functions for querying the SQLite database.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DB_FILE = BASE_DIR / "news.db"


def get_db_connection():
    """Get a database connection."""
    return sqlite3.connect(str(DB_FILE))


def get_articles(page: int = 1, page_size: int = 50, category: Optional[str] = None, 
                 search: Optional[str] = None) -> Tuple[List[Dict], int]:
    """
    Get paginated articles with optional filtering.
    
    Returns:
        Tuple of (articles list, total count)
    """
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build query
    where_clauses = []
    params = []
    
    if category:
        where_clauses.append("category = ?")
        params.append(category)
    
    if search:
        where_clauses.append("(title LIKE ? OR summary LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])
    
    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    # Get total count
    cursor.execute(f"SELECT COUNT(*) FROM articles{where_sql}", params)
    total = cursor.fetchone()[0]
    
    # Get paginated results
    offset = (page - 1) * page_size
    cursor.execute(f"""
        SELECT article_id, title, date, url, summary, category, tags, notes
        FROM articles
        {where_sql}
        ORDER BY date DESC
        LIMIT ? OFFSET ?
    """, params + [page_size, offset])
    
    rows = cursor.fetchall()
    articles = [dict(row) for row in rows]
    
    conn.close()
    return articles, total


def get_article(article_id: str) -> Optional[Dict]:
    """Get a single article by ID."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT article_id, title, date, url, summary, category, tags, notes
        FROM articles
        WHERE article_id = ?
    """, (article_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def get_relationships(source_id: Optional[str] = None, 
                     target_id: Optional[str] = None,
                     rel_type: Optional[str] = None,
                     min_strength: Optional[float] = None,
                     method: Optional[str] = None,
                     limit: Optional[int] = None) -> List[Dict]:
    """Get relationships with optional filters."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    where_clauses = []
    params = []
    
    if source_id:
        where_clauses.append("source_id = ?")
        params.append(source_id)
    
    if target_id:
        where_clauses.append("target_id = ?")
        params.append(target_id)
    
    if rel_type:
        where_clauses.append("rel_type LIKE ?")
        params.append(f"%{rel_type}%")
    
    if min_strength is not None:
        where_clauses.append("strength >= ?")
        params.append(min_strength)
    
    if method:
        where_clauses.append("method = ?")
        params.append(method)
    
    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    limit_sql = f" LIMIT {limit}" if limit else ""
    
    cursor.execute(f"""
        SELECT id, source_id, target_id, rel_type, strength, method, reason,
               people_connection, org_connection
        FROM relationships
        {where_sql}
        ORDER BY strength DESC
        {limit_sql}
    """, params)
    
    rows = cursor.fetchall()
    relationships = [dict(row) for row in rows]
    
    conn.close()
    return relationships


def get_network_data(limit: Optional[int] = None, 
                    min_strength: Optional[float] = None) -> Dict:
    """
    Get network graph data (nodes and edges).
    
    Returns:
        Dictionary with 'nodes' and 'edges' lists
    """
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    
    # Get articles (nodes)
    if min_strength:
        # Only get articles that have relationships above threshold
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT a.article_id, a.title, a.category, a.date
            FROM articles a
            INNER JOIN relationships r ON (a.article_id = r.source_id OR a.article_id = r.target_id)
            WHERE r.strength >= ?
        """, (min_strength,))
    else:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT article_id, title, category, date
            FROM articles
        """)
    
    nodes = []
    for row in cursor.fetchall():
        # Count connections
        cursor.execute("""
            SELECT COUNT(*) FROM relationships
            WHERE source_id = ? OR target_id = ?
        """, (row['article_id'], row['article_id']))
        connection_count = cursor.fetchone()[0]
        
        nodes.append({
            'id': row['article_id'],
            'title': row['title'],
            'category': row['category'],
            'date': row['date'],
            'connections': connection_count
        })
    
    # Get relationships (edges)
    where_clause = ""
    params = []
    if min_strength:
        where_clause = " WHERE strength >= ?"
        params = [min_strength]
    
    limit_sql = f" LIMIT {limit}" if limit else ""
    
    cursor.execute(f"""
        SELECT source_id, target_id, rel_type, strength, method
        FROM relationships
        {where_clause}
        ORDER BY strength DESC
        {limit_sql}
    """, params)
    
    edges = []
    for row in cursor.fetchall():
        edges.append({
            'source': row['source_id'],
            'target': row['target_id'],
            'type': row['rel_type'],
            'strength': row['strength'],
            'method': row['method']
        })
    
    conn.close()
    return {'nodes': nodes, 'edges': edges}


def get_timeline_data() -> List[Dict]:
    """Get article counts grouped by date."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT date, COUNT(*) as count,
               GROUP_CONCAT(DISTINCT category) as categories
        FROM articles
        WHERE date IS NOT NULL AND date != ''
        GROUP BY date
        ORDER BY date
    """)
    
    rows = cursor.fetchall()
    timeline = [dict(row) for row in rows]
    
    conn.close()
    return timeline


def get_entities(entity_type: str = 'people') -> List[Dict]:
    """
    Get all people or organizations with article counts.
    
    Args:
        entity_type: 'people' or 'orgs'
    """
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    table = 'people' if entity_type == 'people' else 'organizations'
    name_col = 'person_name' if entity_type == 'people' else 'org_name'
    
    cursor.execute(f"""
        SELECT {name_col} as name, COUNT(*) as article_count
        FROM {table}
        WHERE {name_col} IS NOT NULL AND {name_col} != ''
        GROUP BY {name_col}
        ORDER BY article_count DESC
    """)
    
    rows = cursor.fetchall()
    entities = [dict(row) for row in rows]
    
    conn.close()
    return entities


def get_entity_articles(entity_name: str, entity_type: str = 'people') -> List[Dict]:
    """
    Get all articles for a specific person or organization.
    
    Args:
        entity_name: Name of the person or organization
        entity_type: 'people' or 'orgs'
    """
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    table = 'people' if entity_type == 'people' else 'organizations'
    name_col = 'person_name' if entity_type == 'people' else 'org_name'
    
    cursor.execute(f"""
        SELECT a.article_id, a.title, a.date, a.category
        FROM articles a
        INNER JOIN {table} e ON a.article_id = e.article_id
        WHERE e.{name_col} = ?
        ORDER BY a.date DESC
    """, (entity_name,))
    
    rows = cursor.fetchall()
    articles = [dict(row) for row in rows]
    
    conn.close()
    return articles


def get_categories() -> List[Dict]:
    """Get category breakdown with counts."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM articles
        WHERE category IS NOT NULL AND category != ''
        GROUP BY category
        ORDER BY count DESC
    """)
    
    rows = cursor.fetchall()
    categories = [dict(row) for row in rows]
    
    conn.close()
    return categories


def get_stats() -> Dict:
    """Get dashboard statistics."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    stats = {}
    
    # Total articles
    cursor.execute("SELECT COUNT(*) FROM articles")
    stats['total_articles'] = cursor.fetchone()[0]
    
    # Total relationships
    cursor.execute("SELECT COUNT(*) FROM relationships")
    stats['total_relationships'] = cursor.fetchone()[0]
    
    # Unique people
    cursor.execute("SELECT COUNT(DISTINCT person_name) FROM people")
    stats['unique_people'] = cursor.fetchone()[0]
    
    # Unique organizations
    cursor.execute("SELECT COUNT(DISTINCT org_name) FROM organizations")
    stats['unique_orgs'] = cursor.fetchone()[0]
    
    # Categories
    cursor.execute("SELECT COUNT(DISTINCT category) FROM articles WHERE category != ''")
    stats['unique_categories'] = cursor.fetchone()[0]
    
    # Methods breakdown
    cursor.execute("""
        SELECT method, COUNT(*) as count, AVG(strength) as avg_strength
        FROM relationships
        GROUP BY method
    """)
    stats['methods'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return stats

