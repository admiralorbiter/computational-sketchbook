#!/usr/bin/env python3
"""
Article Summarization Script

Processes a CSV file with article URLs, fetches article content,
and generates summaries using OpenAI API. Saves progress incrementally
to prevent data loss on interruption.
"""

import os
import sys
import csv
import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Tuple
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# Try to load .env file from root directory
try:
    from dotenv import load_dotenv
    # Look for .env in the project root (parent of news-summaries directory)
    root_dir = Path(__file__).parent.parent
    env_path = root_dir / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded .env from {env_path}")
    else:
        # Also try current directory
        load_dotenv()
except ImportError:
    # python-dotenv not installed, skip
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
INPUT_CSV = Path(__file__).parent / "Research and References - Current Events.csv"
OUTPUT_CSV = Path(__file__).parent / "summarized_output.csv"
CHECKPOINT_FILE = Path(__file__).parent / "checkpoint.json"

# OpenAI model configuration
MODEL = "gpt-4o-mini"
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Request configuration
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 1  # seconds between article fetches

# Test mode: limit number of rows to process (None = process all)
MAX_ROWS = None  # Set to a number (e.g., 5) for testing, or use --limit argument


def fetch_article_content(url: str) -> Optional[str]:
    """
    Fetch article content from a URL and extract main text.
    
    Args:
        url: URL of the article
        
    Returns:
        Extracted article text or None if fetch failed
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Try to find main article content
        # Common article selectors
        article = None
        for selector in ['article', '[role="article"]', '.article', '.post', 
                        '.entry-content', '.article-content', 'main', '[class*="article"]',
                        '[class*="story"]', '[class*="content"]']:
            article = soup.select_one(selector)
            if article:
                break
        
        # If no article tag found, try body
        if not article:
            article = soup.find('body')
        
        if article:
            text = article.get_text(separator=' ', strip=True)
            # Clean up whitespace
            text = ' '.join(text.split())
            # Limit to reasonable length (avoid extremely long pages)
            if len(text) > 50000:
                text = text[:50000] + "..."
            return text if text else None
        
        return None
        
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        return None


def summarize_article(title: str, date: str, content: str, client: OpenAI) -> Optional[str]:
    """
    Generate summary of article using OpenAI API.
    
    Args:
        title: Article title
        date: Article date
        content: Article content
        client: OpenAI client instance
        
    Returns:
        Generated summary or None if API call failed
    """
    if not content:
        return None
    
    prompt = f"""Provide a concise summary of this article:

Title: {title}
Date: {date}

Article content:
{content}

Format your response as:
1. First, provide a 1-2 sentence brief summary
2. Then, provide 3-5 bullet points with key facts

Be concise and focus on the most important information."""

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.warning(f"OpenAI API error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (2 ** attempt))  # Exponential backoff
            else:
                logger.error(f"Failed to generate summary after {MAX_RETRIES} attempts")
                return None
    
    return None


def load_checkpoint() -> int:
    """
    Load checkpoint to resume from last processed row.
    
    Returns:
        Last processed row index (0-based), or 0 if no checkpoint
    """
    if not CHECKPOINT_FILE.exists():
        return 0
    
    try:
        with open(CHECKPOINT_FILE, 'r') as f:
            data = json.load(f)
            return data.get('last_row', 0)
    except Exception as e:
        logger.warning(f"Error loading checkpoint: {e}")
        return 0


def save_checkpoint(row_idx: int):
    """
    Save checkpoint with last processed row index.
    
    Args:
        row_idx: Last processed row index (0-based)
    """
    try:
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({'last_row': row_idx}, f)
    except Exception as e:
        logger.error(f"Error saving checkpoint: {e}")


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
    
    # Load checkpoint and verify against output CSV
    checkpoint_idx = load_checkpoint()
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
        writer.writerow(['Title', 'Date', 'URL', 'Summary'])
    
    # Statistics
    stats = {
        'processed': 0,
        'skipped': 0,
        'failed_fetch': 0,
        'failed_summary': 0
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
                
                logger.info(f"[{idx + 1}/{total_rows}] Processing: {title[:60]}...")
                
                # Fetch article content
                content = None
                if url:
                    content = fetch_article_content(url)
                    time.sleep(REQUEST_DELAY)  # Rate limiting
                    
                    if not content:
                        stats['failed_fetch'] += 1
                        summary = "Failed to fetch article content"
                    else:
                        # Generate summary
                        summary = summarize_article(title, date, content, client)
                        
                        if not summary:
                            stats['failed_summary'] += 1
                            summary = "Failed to generate summary"
                        else:
                            stats['processed'] += 1
                else:
                    stats['skipped'] += 1
                    summary = "No URL provided"
                
                # Write to output CSV immediately
                writer.writerow([title, date, url, summary])
                output_file.flush()  # Ensure data is written
                
                # Update checkpoint
                save_checkpoint(idx)
                
                # Progress update every 10 rows
                if (idx + 1) % 10 == 0:
                    logger.info(f"Progress: {idx + 1}/{total_rows} rows processed")
    
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
        logger.info(f"  Failed to fetch: {stats['failed_fetch']}")
        logger.info(f"  Failed to summarize: {stats['failed_summary']}")
        logger.info(f"  Skipped (no URL): {stats['skipped']}")
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
                logger.error("Invalid limit value. Use: python summarize.py [--limit N]")
                sys.exit(1)
        else:
            logger.error("Usage: python summarize.py [--limit N]")
            logger.error("  --limit N  : Process only first N rows (for testing)")
            sys.exit(1)
    
    process_csv(max_rows=max_rows)

