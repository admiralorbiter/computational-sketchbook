#!/usr/bin/env python3
"""
Article Tagging Script with Efficient Global Memory

Processes summarized_output.csv, assigns article IDs, and uses OpenAI API
to analyze and tag articles with categories, tags, key people/organizations,
related articles, and notes. Uses embedding-based similarity search for
efficient related article detection.
"""

import os
import sys
import csv
import json
import time
import logging
import math
from pathlib import Path
from typing import Optional, Dict, List, Tuple
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
INPUT_CSV = Path(__file__).parent / "summarized_output.csv"
OUTPUT_CSV = Path(__file__).parent / "tagged_output.csv"
CHECKPOINT_FILE = Path(__file__).parent / "tag_checkpoint.json"

# OpenAI model configuration
EMBEDDING_MODEL = "text-embedding-3-small"
ANALYSIS_MODEL = "gpt-4o-mini"
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Similarity search configuration
TOP_K_RELATED = 10  # Number of most similar articles to consider
SIMILARITY_THRESHOLD = 0.65  # Minimum cosine similarity to consider related

# Test mode: limit number of rows to process (None = process all)
MAX_ROWS = None

# Category list
CATEGORIES = [
    "Legal & Judicial",
    "Federal Spending & Cuts",
    "Government Workforce",
    "Immigration & Border",
    "Education & Research",
    "Musk/Doge",
    "International Relations",
    "Media & Info Control",
    "Civil Rights & Democracy"
]


def load_checkpoint() -> Dict:
    """
    Load checkpoint to resume from last processed row.
    
    Returns:
        Dictionary with checkpoint data or empty dict if no checkpoint
    """
    if not CHECKPOINT_FILE.exists():
        return {"last_row": 0, "articles": {}}
    
    try:
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Error loading checkpoint: {e}")
        return {"last_row": 0, "articles": {}}


def save_checkpoint(checkpoint_data: Dict):
    """
    Save checkpoint with article data.
    
    Args:
        checkpoint_data: Dictionary with last_row and articles data
    """
    try:
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving checkpoint: {e}")


def generate_article_id(row_idx: int, checkpoint: Dict) -> str:
    """
    Generate or retrieve article ID for a row.
    
    Args:
        row_idx: Row index (0-based)
        checkpoint: Checkpoint dictionary
        
    Returns:
        Article ID in format "ART-XXXX"
    """
    articles = checkpoint.get("articles", {})
    
    # Check if ID already exists for this row
    for art_id, art_data in articles.items():
        if art_data.get("row_idx") == row_idx:
            return art_id
    
    # Generate new ID
    next_num = len(articles) + 1
    return f"ART-{next_num:04d}"


def generate_embedding(text: str, client: OpenAI) -> Optional[List[float]]:
    """
    Generate embedding vector for text using OpenAI.
    
    Args:
        text: Text to embed
        client: OpenAI client instance
        
    Returns:
        Embedding vector or None if failed
    """
    if not text or text == "Failed to fetch article content" or text.startswith("Failed"):
        return None
    
    for attempt in range(MAX_RETRIES):
        try:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=text[:8000]  # Limit to avoid token limits
            )
            return response.data[0].embedding
        except Exception as e:
            logger.warning(f"Embedding error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (2 ** attempt))
            else:
                logger.error(f"Failed to generate embedding after {MAX_RETRIES} attempts")
                return None
    
    return None


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity score (0-1)
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def find_related_articles(
    new_embedding: List[float],
    checkpoint: Dict,
    exclude_id: Optional[str] = None
) -> List[Tuple[str, float]]:
    """
    Find top-K most similar articles using cosine similarity.
    
    Args:
        new_embedding: Embedding vector of new article
        checkpoint: Checkpoint dictionary with article data
        exclude_id: Article ID to exclude from results
        
    Returns:
        List of (article_id, similarity_score) tuples, sorted by similarity
    """
    if not new_embedding:
        return []
    
    articles = checkpoint.get("articles", {})
    similarities = []
    
    for art_id, art_data in articles.items():
        if art_id == exclude_id:
            continue
        
        embedding = art_data.get("embedding")
        if not embedding:
            continue
        
        similarity = cosine_similarity(new_embedding, embedding)
        
        if similarity >= SIMILARITY_THRESHOLD:
            similarities.append((art_id, similarity))
    
    # Sort by similarity (descending) and return top-K
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:TOP_K_RELATED]


def analyze_article(
    title: str,
    date: str,
    summary: str,
    related_articles: List[Tuple[str, Dict]],
    client: OpenAI
) -> Optional[Dict[str, str]]:
    """
    Analyze article and extract metadata using OpenAI.
    
    Args:
        title: Article title
        date: Article date
        summary: Article summary
        related_articles: List of (article_id, article_data) tuples
        client: OpenAI client instance
        
    Returns:
        Dictionary with extracted metadata or None if failed
    """
    if not summary or summary == "Failed to fetch article content" or summary.startswith("Failed"):
        return None
    
    # Build related articles context
    related_context = ""
    if related_articles:
        related_context = "\n\nPreviously processed articles that may be related:\n"
        for art_id, art_data in related_articles[:5]:  # Limit to top 5 for context
            related_context += f"- {art_id}: {art_data.get('title', 'Unknown')} "
            related_context += f"({art_data.get('category', 'Unknown')})\n"
    
    prompt = f"""Analyze this article and extract the following information:

Title: {title}
Date: {date}

Summary:
{summary}
{related_context}

Please provide:
1. **Primary_Category**: Select ONE category from this list:
   - Legal & Judicial
   - Federal Spending & Cuts
   - Government Workforce
   - Immigration & Border
   - Education & Research
   - Musk/Doge
   - International Relations
   - Media & Info Control
   - Civil Rights & Democracy

2. **Tags**: Provide 3-7 comma-separated tags (mix of general and specific). Examples: "judicial oversight, federal courts, executive orders" or "immigration policy, border security, deportation"

3. **Key_People**: List all important people mentioned (comma-separated). Examples: "Donald Trump, Elon Musk, Judge Boasberg"

4. **Key_Organizations**: List all important organizations mentioned (comma-separated). Examples: "DOJ, ICE, Columbia University"

5. **Related_Articles**: From the previously processed articles listed above, provide comma-separated Article IDs (format: ART-0001,ART-0005) that are most relevant. Only include IDs that are truly related. If none are related, leave empty.

6. **Notes**: Provide 1-3 sentences analyzing implications, connections, or important context about this story.

Format your response as:
Primary_Category: [category name]
Tags: [comma-separated tags]
Key_People: [comma-separated names]
Key_Organizations: [comma-separated organizations]
Related_Articles: [comma-separated IDs or empty]
Notes: [analysis text]"""

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=ANALYSIS_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse the response
            result = {}
            current_field = None
            current_value = []
            
            for line in result_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Check if this is a field header
                if ':' in line and not line.startswith('-'):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        # Save previous field
                        if current_field:
                            result[current_field] = ' '.join(current_value).strip()
                        
                        # Start new field
                        current_field = parts[0].strip()
                        current_value = [parts[1].strip()] if parts[1].strip() else []
                        continue
                
                # Continue current field
                if current_field:
                    current_value.append(line)
            
            # Save last field
            if current_field:
                result[current_field] = ' '.join(current_value).strip()
            
            # Normalize field names
            normalized = {}
            for key, value in result.items():
                key_lower = key.lower().replace('_', '').replace('-', '').replace(' ', '')
                normalized[key_lower] = value
            
            # Map to expected field names
            return {
                "Primary_Category": normalized.get("primarycategory", normalized.get("category", "")),
                "Tags": normalized.get("tags", ""),
                "Key_People": normalized.get("keypeople", normalized.get("people", "")),
                "Key_Organizations": normalized.get("keyorganizations", normalized.get("organizations", normalized.get("orgs", ""))),
                "Related_Articles": normalized.get("relatedarticles", normalized.get("related", "")),
                "Notes": normalized.get("notes", "")
            }
            
        except Exception as e:
            logger.warning(f"OpenAI API error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (2 ** attempt))
            else:
                logger.error(f"Failed to analyze article after {MAX_RETRIES} attempts")
                return None
    
    return None


def get_processed_count() -> int:
    """
    Get number of rows already processed (existing in output CSV).
    
    Returns:
        Number of rows in output CSV (excluding header)
    """
    if not OUTPUT_CSV.exists():
        return 0
    
    try:
        with open(OUTPUT_CSV, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            return len(rows) - 1 if rows else 0  # Exclude header
    except Exception as e:
        logger.warning(f"Error reading output CSV: {e}")
        return 0


def process_csv(max_rows: Optional[int] = None):
    """
    Main function to process CSV file row by row.
    
    Args:
        max_rows: Maximum number of rows to process (None = process all)
    """
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Use command-line argument or global MAX_ROWS setting
    if max_rows is None:
        max_rows = MAX_ROWS
    
    # Load checkpoint
    checkpoint = load_checkpoint()
    checkpoint_idx = checkpoint.get("last_row", 0)
    processed_count = get_processed_count()
    
    # Use the higher of the two to avoid reprocessing
    start_idx = max(checkpoint_idx, processed_count)
    
    if start_idx > 0:
        logger.info(f"Resuming from row {start_idx} (checkpoint: {checkpoint_idx}, processed: {processed_count})")
    
    # Initialize output CSV if needed
    output_exists = OUTPUT_CSV.exists()
    output_file = open(OUTPUT_CSV, 'a', newline='', encoding='utf-8')
    writer = csv.writer(output_file)
    
    # Write header if new file
    if not output_exists:
        writer.writerow([
            'Title', 'Date', 'URL', 'Summary', 'Article_ID',
            'Primary_Category', 'Tags', 'Key_People', 'Key_Organizations',
            'Related_Articles', 'Notes'
        ])
    
    # Statistics
    stats = {
        'processed': 0,
        'skipped': 0,
        'failed_embedding': 0,
        'failed_analysis': 0
    }
    
    try:
        # Read input CSV
        with open(INPUT_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            total_rows = len(rows)
            
            # Limit rows if max_rows is set
            if max_rows is not None:
                total_rows = min(total_rows, max_rows)
                rows = rows[:total_rows]
                if start_idx >= total_rows:
                    logger.info(f"Already processed all {total_rows} rows in test mode")
                    return
            
            logger.info(f"Total rows to process: {total_rows}")
            if max_rows:
                logger.info(f"TEST MODE: Limited to {max_rows} rows")
            logger.info(f"Starting from row {start_idx + 1}")
            
            # Process each row
            rows_to_process = rows[start_idx:] if start_idx < len(rows) else []
            for idx, row in enumerate(rows_to_process, start=start_idx):
                title = row.get('Title', '').strip()
                date = row.get('Date', '').strip()
                url = row.get('URL', '').strip()
                summary = row.get('Summary', '').strip()
                
                logger.info(f"[{idx + 1}/{total_rows}] Processing: {title[:60]}...")
                
                # Generate article ID
                article_id = generate_article_id(idx, checkpoint)
                
                # Generate embedding
                embedding = generate_embedding(summary, client)
                
                if not embedding:
                    stats['failed_embedding'] += 1
                    logger.warning(f"Failed to generate embedding for row {idx + 1}")
                    # Still write row with empty metadata
                    writer.writerow([
                        title, date, url, summary, article_id,
                        "", "", "", "", "", "Failed to generate embedding"
                    ])
                    output_file.flush()
                    save_checkpoint(checkpoint)
                    continue
                
                # Find related articles
                related_similarities = find_related_articles(embedding, checkpoint, exclude_id=article_id)
                related_articles = []
                for art_id, sim_score in related_similarities:
                    art_data = checkpoint.get("articles", {}).get(art_id, {})
                    related_articles.append((art_id, art_data))
                    logger.debug(f"Found related article {art_id} (similarity: {sim_score:.3f})")
                
                # Analyze article
                analysis = analyze_article(title, date, summary, related_articles, client)
                
                if not analysis:
                    stats['failed_analysis'] += 1
                    logger.warning(f"Failed to analyze row {idx + 1}")
                    # Still save embedding for future use
                    checkpoint.setdefault("articles", {})[article_id] = {
                        "embedding": embedding,
                        "title": title,
                        "category": "",
                        "row_idx": idx
                    }
                    writer.writerow([
                        title, date, url, summary, article_id,
                        "", "", "", "", "", "Failed to analyze"
                    ])
                else:
                    stats['processed'] += 1
                    
                    # Store article data in checkpoint
                    checkpoint.setdefault("articles", {})[article_id] = {
                        "embedding": embedding,
                        "title": title,
                        "category": analysis.get("Primary_Category", ""),
                        "row_idx": idx
                    }
                    
                    # Write to output CSV
                    writer.writerow([
                        title,
                        date,
                        url,
                        summary,
                        article_id,
                        analysis.get("Primary_Category", ""),
                        analysis.get("Tags", ""),
                        analysis.get("Key_People", ""),
                        analysis.get("Key_Organizations", ""),
                        analysis.get("Related_Articles", ""),
                        analysis.get("Notes", "")
                    ])
                
                output_file.flush()
                
                # Update checkpoint
                checkpoint["last_row"] = idx
                save_checkpoint(checkpoint)
                
                # Progress update every 10 rows
                if (idx + 1) % 10 == 0:
                    logger.info(f"Progress: {idx + 1}/{total_rows} rows processed")
                
                # Small delay to avoid rate limits
                time.sleep(0.5)
    
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user. Progress saved.")
    except Exception as e:
        logger.error(f"Error processing CSV: {e}", exc_info=True)
    finally:
        output_file.close()
        
        # Print summary
        logger.info("\n" + "="*50)
        logger.info("Processing Summary:")
        logger.info(f"  Successfully processed: {stats['processed']}")
        logger.info(f"  Failed embedding: {stats['failed_embedding']}")
        logger.info(f"  Failed analysis: {stats['failed_analysis']}")
        logger.info(f"  Skipped: {stats['skipped']}")
        logger.info("="*50)


if __name__ == "__main__":
    if not INPUT_CSV.exists():
        logger.error(f"Input CSV not found: {INPUT_CSV}")
        sys.exit(1)
    
    # Check for --limit argument
    max_rows = None
    if len(sys.argv) > 1:
        if sys.argv[1] == '--limit' and len(sys.argv) > 2:
            try:
                max_rows = int(sys.argv[2])
                logger.info(f"Limiting to {max_rows} rows (test mode)")
            except ValueError:
                logger.error("Invalid limit value. Use: python tag.py [--limit N]")
                sys.exit(1)
        else:
            logger.error("Usage: python tag.py [--limit N]")
            logger.error("  --limit N  : Process only first N rows (for testing)")
            sys.exit(1)
    
    process_csv(max_rows=max_rows)

