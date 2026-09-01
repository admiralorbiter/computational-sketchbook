#!/usr/bin/env python3
"""
Relationship Discovery Script with Enhanced GPT Analysis

Processes tagged_output.csv to discover comprehensive relationships between articles
using multiple strategies: deterministic matching, embedding similarity, and
intelligent GPT cluster analysis.
"""

import os
import sys
import csv
import json
import time
import logging
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Set
from collections import defaultdict
from datetime import datetime, timedelta
from openai import OpenAI
import numpy as np

# Try to load .env file from root directory
try:
    from dotenv import load_dotenv
    root_dir = Path(__file__).parent.parent
    env_path = root_dir / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded .env from {env_path}")
    else:
        load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
INPUT_CSV = Path(__file__).parent / "tagged_output.csv"
OUTPUT_CSV = Path(__file__).parent / "relationships_output.csv"
OUTPUT_JSON = Path(__file__).parent / "relationships_graph.json"
CHECKPOINT_FILE = Path(__file__).parent / "relationships_checkpoint.json"
TAG_CHECKPOINT = Path(__file__).parent / "tag_checkpoint.json"

# OpenAI configuration
EMBEDDING_MODEL = "text-embedding-3-small"
ANALYSIS_MODEL = "gpt-4o-mini"
MAX_RETRIES = 3
RETRY_DELAY = 1

# Relationship thresholds
SIMILARITY_THRESHOLD = 0.60  # Minimum cosine similarity (lowered for more coverage)
DATE_PROXIMITY_DAYS = 7
CLUSTER_SIZE = 30  # Articles per cluster for GPT analysis (increased for better coverage)

# Test mode
MAX_ARTICLES = None

# Entity aliases for normalization
ENTITY_ALIASES = {
    "donald trump": ["trump", "president trump", "donald j trump"],
    "elon musk": ["musk"],
    "doj": ["department of justice", "justice department", "usdoj"],
    "ice": ["immigration and customs enforcement", "u.s. immigration and customs enforcement"],
    "white house": ["executive branch", "the white house"],
    "supreme court": ["scotus", "u.s. supreme court"],
    "fbi": ["federal bureau of investigation"],
    "cia": ["central intelligence agency"],
    "nsa": ["national security agency"],
    "hss": ["health and human services", "hhs", "department of health and human services"],
    "cdc": ["centers for disease control", "centers for disease control and prevention"],
    "fda": ["food and drug administration"],
    "nasa": ["national aeronautics and space administration"],
    "columbia university": ["columbia"],
    "heritage foundation": ["heritage"],
    "wikimedia foundation": ["wikimedia"],
}


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string (M/D/YY format)."""
    try:
        return datetime.strptime(date_str, "%m/%d/%y")
    except:
        try:
            return datetime.strptime(date_str, "%m/%d/%Y")
        except:
            return None


def normalize_entity(name: str) -> str:
    """Normalize entity name for matching with alias resolution."""
    name = name.strip()
    # Basic normalization
    name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
    name_lower = name.lower()
    
    # Check against aliases
    for canonical, alias_list in ENTITY_ALIASES.items():
        if name_lower == canonical or name_lower in alias_list:
            return canonical
    
    return name_lower


def load_checkpoint() -> Dict:
    """Load checkpoint data."""
    if not CHECKPOINT_FILE.exists():
        return {"processed_clusters": [], "relationships": {}, "last_phase": "none"}
    
    try:
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Error loading checkpoint: {e}")
        return {"processed_clusters": [], "relationships": {}, "last_phase": "none"}


def save_checkpoint(checkpoint_data: Dict):
    """Save checkpoint data."""
    try:
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving checkpoint: {e}")


def load_articles() -> Tuple[Dict[str, Dict], Dict[str, Set[str]], Dict[str, Set[str]], Dict[str, List[str]]]:
    """Load articles and build indexes."""
    articles = {}
    people_index = defaultdict(set)
    orgs_index = defaultdict(set)
    category_clusters = defaultdict(list)
    
    logger.info(f"Loading articles from {INPUT_CSV}")
    
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        
        for row in reader:
            article_id = row.get('Article_ID', '').strip()
            if not article_id or not article_id.startswith('ART-'):
                continue
            
            if MAX_ARTICLES and count >= MAX_ARTICLES:
                break
            
            title = row.get('Title', '').strip()
            date_str = row.get('Date', '').strip()
            category = row.get('Primary_Category', '').strip()
            summary = row.get('Summary', '').strip()
            people_str = row.get('Key_People', '').strip()
            orgs_str = row.get('Key_Organizations', '').strip()
            tags_str = row.get('Tags', '').strip()
            
            # Parse entities
            people = [normalize_entity(p) for p in people_str.split(',') if p.strip()] if people_str else []
            orgs = [normalize_entity(o) for o in orgs_str.split(',') if o.strip()] if orgs_str else []
            tags = [t.strip() for t in tags_str.split(',') if t.strip()] if tags_str else []
            
            # Build indexes
            for person in people:
                people_index[person].add(article_id)
            for org in orgs:
                orgs_index[org].add(article_id)
            
            if category:
                category_clusters[category].append(article_id)
            
            # Store article data
            articles[article_id] = {
                'title': title,
                'date': parse_date(date_str),
                'date_str': date_str,
                'category': category,
                'summary': summary[:500] if summary else '',  # Summary excerpt
                'summary_full': summary,
                'people': people,
                'orgs': orgs,
                'tags': tags,
                'url': row.get('URL', '').strip()
            }
            
            count += 1
    
    logger.info(f"Loaded {len(articles)} articles")
    logger.info(f"Found {len(people_index)} unique people, {len(orgs_index)} unique organizations")
    logger.info(f"Category clusters: {dict((k, len(v)) for k, v in category_clusters.items())}")
    
    return articles, dict(people_index), dict(orgs_index), dict(category_clusters)


def load_embeddings(articles: Dict[str, Dict]) -> Optional[np.ndarray]:
    """Load embeddings from tag checkpoint or generate if needed."""
    logger.info("Loading embeddings...")
    
    # Try to load from tag checkpoint
    embeddings_dict = {}
    if TAG_CHECKPOINT.exists():
        try:
            with open(TAG_CHECKPOINT, 'r') as f:
                tag_data = json.load(f)
                tag_articles = tag_data.get("articles", {})
                for art_id, art_data in tag_articles.items():
                    if art_id in articles and "embedding" in art_data:
                        embeddings_dict[art_id] = art_data["embedding"]
            logger.info(f"Loaded {len(embeddings_dict)} embeddings from checkpoint")
        except Exception as e:
            logger.warning(f"Error loading embeddings from checkpoint: {e}")
    
    # Generate missing embeddings
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.warning("No API key, skipping embedding generation")
        return None
    
    client = OpenAI(api_key=api_key)
    missing = [aid for aid in articles.keys() if aid not in embeddings_dict]
    
    if missing:
        logger.info(f"Generating {len(missing)} missing embeddings...")
        for art_id in missing[:100]:  # Limit for testing
            summary = articles[art_id].get('summary_full', '')
            if not summary or summary.startswith("Failed"):
                continue
            
            try:
                response = client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=summary[:8000]
                )
                embeddings_dict[art_id] = response.data[0].embedding
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                logger.warning(f"Error generating embedding for {art_id}: {e}")
    
    # Build matrix
    if not embeddings_dict:
        return None
    
    article_ids = list(articles.keys())
    embedding_dim = len(next(iter(embeddings_dict.values())))
    matrix = np.zeros((len(article_ids), embedding_dim))
    id_to_idx = {aid: idx for idx, aid in enumerate(article_ids)}
    
    for art_id, embedding in embeddings_dict.items():
        if art_id in id_to_idx:
            matrix[id_to_idx[art_id]] = np.array(embedding)
    
    logger.info(f"Built embedding matrix: {matrix.shape}")
    return matrix, id_to_idx


def cosine_similarity_matrix(embeddings: np.ndarray) -> np.ndarray:
    """Calculate pairwise cosine similarity matrix."""
    # Normalize vectors
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1  # Avoid division by zero
    normalized = embeddings / norms
    
    # Compute similarity matrix
    similarity = np.dot(normalized, normalized.T)
    return similarity


def find_deterministic_relationships(
    articles: Dict[str, Dict],
    people_index: Dict[str, Set[str]],
    orgs_index: Dict[str, Set[str]]
) -> Dict[Tuple[str, str], Dict]:
    """Find deterministic relationships (no API calls)."""
    logger.info("Finding deterministic relationships...")
    relationships = {}
    
    article_ids = list(articles.keys())
    
    # Entity-based relationships
    for art_id1 in article_ids:
        art1 = articles[art_id1]
        people1 = set(art1['people'])
        orgs1 = set(art1['orgs'])
        category1 = art1['category']
        tags1 = set(art1['tags'])
        date1 = art1['date']
        
        for art_id2 in article_ids:
            if art_id1 >= art_id2:  # Avoid duplicates
                continue
            
            art2 = articles[art_id2]
            people2 = set(art2['people'])
            orgs2 = set(art2['orgs'])
            category2 = art2['category']
            tags2 = set(art2['tags'])
            date2 = art2['date']
            
            rel_types = []
            strength = 0.0
            people_conn = []
            orgs_conn = []
            
            # Shared people
            shared_people = people1 & people2
            if shared_people:
                rel_types.append("shared_person")
                people_conn = list(shared_people)
                strength += len(shared_people) * 0.3
            
            # Shared organizations
            shared_orgs = orgs1 & orgs2
            if shared_orgs:
                rel_types.append("shared_organization")
                orgs_conn = list(shared_orgs)
                strength += len(shared_orgs) * 0.3
            
            # Same category
            if category1 and category1 == category2:
                rel_types.append("same_category")
                strength += 0.2
            
            # Tag overlap
            shared_tags = tags1 & tags2
            if shared_tags:
                rel_types.append("tag_overlap")
                strength += len(shared_tags) * 0.1
            
            # Date proximity (only if we have other connections)
            if date1 and date2:
                days_diff = abs((date1 - date2).days)
                if days_diff <= DATE_PROXIMITY_DAYS and len(rel_types) > 0:
                    rel_types.append("temporal_proximity")
                    strength += 0.1 * (1 - days_diff / DATE_PROXIMITY_DAYS)
            
            if rel_types:
                strength = min(strength, 1.0)
                key = tuple(sorted([art_id1, art_id2]))
                relationships[key] = {
                    'source': art_id1,
                    'target': art_id2,
                    'types': rel_types,
                    'strength': strength,
                    'method': 'deterministic',
                    'people_connection': ', '.join(people_conn),
                    'org_connection': ', '.join(orgs_conn),
                    'reason': f"Deterministic match: {', '.join(rel_types)}"
                }
    
    logger.info(f"Found {len(relationships)} deterministic relationships")
    return relationships


def find_embedding_relationships(
    articles: Dict[str, Dict],
    embeddings: Tuple[np.ndarray, Dict[str, int]]
) -> Dict[Tuple[str, str], Dict]:
    """Find relationships based on embedding similarity."""
    logger.info("Finding embedding-based relationships...")
    
    if not embeddings:
        return {}
    
    matrix, id_to_idx = embeddings
    similarity_matrix = cosine_similarity_matrix(matrix)
    
    relationships = {}
    article_ids = list(articles.keys())
    
    for i, art_id1 in enumerate(article_ids):
        idx1 = id_to_idx[art_id1]
        for j, art_id2 in enumerate(article_ids):
            if i >= j:  # Upper triangle only
                continue
            
            idx2 = id_to_idx[art_id2]
            similarity = similarity_matrix[idx1, idx2]
            
            if similarity >= SIMILARITY_THRESHOLD:
                key = tuple(sorted([art_id1, art_id2]))
                relationships[key] = {
                    'source': art_id1,
                    'target': art_id2,
                    'types': ['content_similarity'],
                    'strength': float(similarity),
                    'method': 'embedding',
                    'people_connection': '',
                    'org_connection': '',
                    'reason': f"Content similarity: {similarity:.3f}"
                }
    
    logger.info(f"Found {len(relationships)} embedding-based relationships")
    return relationships


def analyze_cluster_with_gpt(
    cluster_ids: List[str],
    articles: Dict[str, Dict],
    client: OpenAI
) -> List[Dict]:
    """Analyze a cluster of articles with GPT to find relationships."""
    if len(cluster_ids) < 2:
        return []
    
    # Build cluster context
    cluster_articles = [articles[aid] for aid in cluster_ids if aid in articles]
    if not cluster_articles:
        return []
    
    category = cluster_articles[0]['category'] if cluster_articles else 'Unknown'
    
    # Build article summaries for GPT
    articles_text = []
    for art_id, art in zip(cluster_ids, cluster_articles):
        summary = art.get('summary', '') or art.get('summary_full', '')[:200]
        articles_text.append(
            f"{art_id}: {art['title']}\n"
            f"Date: {art['date_str']}\n"
            f"Summary: {summary}\n"
            f"People: {', '.join(art['people'][:5])}\n"
            f"Organizations: {', '.join(art['orgs'][:5])}"
        )
    
    prompt = f"""Analyze relationships between these {len(cluster_ids)} articles in the "{category}" category.

Articles:
{chr(10).join(articles_text)}

Find ALL significant relationships between these articles. Consider:
- Causal chains (one article describes events that led to another)
- Follow-up reporting (sequential stories)
- Part of same story arc (hierarchical)
- Thematic connections (related themes/topics)
- Contradicting narratives (conflicting information)
- Context relationships (one provides context for another)

Return a JSON array of relationships in this format:
[
  {{
    "source_id": "ART-0001",
    "target_id": "ART-0002",
    "type": "causes_chain|follows_up|part_of_story|thematic_link|contradicts|context_for",
    "strength": 0.0-1.0,
    "reason": "Brief explanation"
  }}
]

Only include relationships that are meaningful. If no relationships found, return empty array [].

JSON:"""

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=ANALYSIS_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response (handle code blocks, extra text, etc.)
            # First, try to find JSON array
            json_match = re.search(r'(\[.*?\])', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)
            else:
                # Try JSON object with relationships key
                json_match = re.search(r'(\{.*?"relationships".*?\})', result_text, re.DOTALL)
                if json_match:
                    result_text = json_match.group(1)
                else:
                    # Try any JSON object/array
                    json_match = re.search(r'(\[.*?\]|\{.*?\})', result_text, re.DOTALL)
                    if json_match:
                        result_text = json_match.group(1)
            
            # Parse JSON
            try:
                result = json.loads(result_text)
                
                # Handle both list and dict formats
                if isinstance(result, list):
                    relationships = result
                elif isinstance(result, dict):
                    relationships = result.get('relationships', [])
                else:
                    relationships = []
                
                # Validate and convert
                valid_rels = []
                for rel in relationships:
                    if isinstance(rel, dict) and 'source_id' in rel and 'target_id' in rel:
                        valid_rels.append({
                            'source': rel['source_id'],
                            'target': rel['target_id'],
                            'types': [rel.get('type', 'thematic_link')],
                            'strength': float(rel.get('strength', 0.7)),
                            'method': 'gpt_cluster',
                            'people_connection': '',
                            'org_connection': '',
                            'reason': rel.get('reason', 'GPT-identified relationship')
                        })
                
                if valid_rels:
                    logger.info(f"GPT found {len(valid_rels)} relationships in cluster")
                return valid_rels
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse GPT JSON response: {e}")
                logger.debug(f"Response text: {result_text[:500]}")
                return []
            except Exception as e:
                logger.warning(f"Error processing GPT response: {e}")
                logger.debug(f"Response text: {result_text[:500]}")
                return []
                
        except Exception as e:
            logger.warning(f"GPT error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (2 ** attempt))
            else:
                logger.error(f"Failed to analyze cluster after {MAX_RETRIES} attempts")
                return []
    
    return []


def build_clusters(
    category_clusters: Dict[str, List[str]],
    articles: Dict[str, Dict]
) -> List[List[str]]:
    """Build article clusters for GPT analysis."""
    clusters = []
    
    for category, article_ids in category_clusters.items():
        # Split large categories into smaller clusters
        cluster_size = CLUSTER_SIZE
        for i in range(0, len(article_ids), cluster_size):
            cluster = article_ids[i:i + cluster_size]
            if len(cluster) >= 2:  # Need at least 2 articles for relationships
                clusters.append(cluster)
    
    logger.info(f"Built {len(clusters)} clusters for GPT analysis")
    return clusters


def process_relationships(
    deterministic_only: bool = False
):
    """Main function to process relationships."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key and not deterministic_only:
        logger.error("OPENAI_API_KEY not set (use --deterministic-only to skip GPT)")
        return
    
    client = OpenAI(api_key=api_key) if api_key else None
    
    # Load data
    articles, people_index, orgs_index, category_clusters = load_articles()
    
    # Load checkpoint
    checkpoint = load_checkpoint()
    # Convert string keys back to tuples
    rels_dict = checkpoint.get('relationships', {})
    all_relationships = {}
    for key_str, value in rels_dict.items():
        parts = key_str.split('_')
        if len(parts) == 2:
            all_relationships[tuple(sorted(parts))] = value
    
    # Phase 1: Deterministic relationships
    if checkpoint.get('last_phase') != 'deterministic':
        logger.info("Phase 1: Finding deterministic relationships...")
        det_rels = find_deterministic_relationships(articles, people_index, orgs_index)
        all_relationships.update(det_rels)
        checkpoint['last_phase'] = 'deterministic'
        save_checkpoint(checkpoint)
    
    if deterministic_only:
        logger.info("Deterministic-only mode, skipping GPT analysis")
    else:
        # Phase 2: Embedding relationships
        if checkpoint.get('last_phase') != 'embedding':
            logger.info("Phase 2: Finding embedding-based relationships...")
            embeddings_data = load_embeddings(articles)
            if embeddings_data:
                emb_rels = find_embedding_relationships(articles, embeddings_data)
                # Merge, preferring higher strength
                for key, rel in emb_rels.items():
                    if key not in all_relationships or rel['strength'] > all_relationships[key].get('strength', 0):
                        all_relationships[key] = rel
                checkpoint['last_phase'] = 'embedding'
                save_checkpoint(checkpoint)
        
        # Phase 3: GPT cluster analysis
        logger.info("Phase 3: GPT cluster analysis...")
        clusters = build_clusters(category_clusters, articles)
        processed_clusters = set(checkpoint.get('processed_clusters', []))
        
        for cluster_idx, cluster_ids in enumerate(clusters):
            cluster_key = f"{cluster_ids[0]}_{len(cluster_ids)}"
            
            if cluster_key in processed_clusters:
                logger.info(f"Skipping already processed cluster {cluster_idx + 1}/{len(clusters)}")
                continue
            
            logger.info(f"Analyzing cluster {cluster_idx + 1}/{len(clusters)} ({len(cluster_ids)} articles)...")
            
            gpt_rels = analyze_cluster_with_gpt(cluster_ids, articles, client)
            
            # Convert to relationship dict format
            for rel in gpt_rels:
                key = tuple(sorted([rel['source'], rel['target']]))
                # Only add if not already exists or GPT strength is higher
                if key not in all_relationships or rel['strength'] > all_relationships[key].get('strength', 0):
                    all_relationships[key] = rel
            
            processed_clusters.add(cluster_key)
            checkpoint['processed_clusters'] = list(processed_clusters)
            # Store relationships with string keys for JSON serialization
            checkpoint['relationships'] = {
                f"{k[0]}_{k[1]}": v 
                for k, v in all_relationships.items() 
                if isinstance(k, tuple)
            }
            save_checkpoint(checkpoint)
            
            time.sleep(1)  # Rate limiting
    
    # Output relationships
    logger.info(f"Found {len(all_relationships)} total relationships")
    output_relationships(all_relationships, articles)


def output_relationships(relationships: Dict, articles: Dict[str, Dict]):
    """Output relationships to CSV and JSON."""
    logger.info("Writing output files...")
    
    # CSV output
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Source_Article_ID', 'Target_Article_ID', 'Relationship_Type',
            'Strength', 'Method', 'Reason', 'People_Connection', 'Org_Connection'
        ])
        
        for key, rel in relationships.items():
            writer.writerow([
                rel['source'],
                rel['target'],
                ', '.join(rel['types']),
                f"{rel['strength']:.3f}",
                rel['method'],
                rel['reason'],
                rel.get('people_connection', ''),
                rel.get('org_connection', '')
            ])
    
    # JSON graph output
    graph = {
        'articles': {},
        'people_network': {},
        'organization_network': {}
    }
    
    for art_id, art in articles.items():
        graph['articles'][art_id] = {
            'title': art['title'],
            'date': art['date_str'],
            'category': art['category'],
            'relationships': {}
        }
    
    for key, rel in relationships.items():
        source = rel['source']
        target = rel['target']
        if source in graph['articles']:
            graph['articles'][source]['relationships'][target] = {
                'types': rel['types'],
                'strength': rel['strength'],
                'method': rel['method'],
                'reason': rel['reason']
            }
    
    # Build entity networks
    for art_id, art in articles.items():
        for person in art['people']:
            if person not in graph['people_network']:
                graph['people_network'][person] = []
            if art_id not in graph['people_network'][person]:
                graph['people_network'][person].append(art_id)
        
        for org in art['orgs']:
            if org not in graph['organization_network']:
                graph['organization_network'][org] = []
            if art_id not in graph['organization_network'][org]:
                graph['organization_network'][org].append(art_id)
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=2)
    
    logger.info(f"Wrote {len(relationships)} relationships to {OUTPUT_CSV} and {OUTPUT_JSON}")


if __name__ == "__main__":
    if not INPUT_CSV.exists():
        logger.error(f"Input CSV not found: {INPUT_CSV}")
        sys.exit(1)
    
    deterministic_only = False
    
    if len(sys.argv) > 1:
        if '--limit' in sys.argv:
            idx = sys.argv.index('--limit')
            if idx + 1 < len(sys.argv):
                try:
                    MAX_ARTICLES = int(sys.argv[idx + 1])
                    logger.info(f"Limiting to {MAX_ARTICLES} articles")
                except ValueError:
                    logger.error("Invalid limit value")
                    sys.exit(1)
        
        if '--deterministic-only' in sys.argv:
            deterministic_only = True
            logger.info("Deterministic-only mode enabled")
    
    process_relationships(deterministic_only=deterministic_only)

