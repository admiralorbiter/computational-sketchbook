#!/usr/bin/env python3
"""
AI Article Summarization Script

Processes a CSV file with article URLs, fetches article content,
extracts title and date, and generates summaries, tags, and notes
using OpenAI API (gpt-5-mini). Saves progress incrementally
to prevent data loss on interruption.
"""

import os
import sys
import csv
import json
import time
import logging
import re
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# Try to load .env file from root directory
try:
    from dotenv import load_dotenv
    # Look for .env in the project root (parent of news-summaries directory)
    root_dir = Path(__file__).parent.parent.parent
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
INPUT_CSV = Path(__file__).parent / "Research and References - ai-urls.csv"
OUTPUT_CSV = Path(__file__).parent / "summarized_ai_output.csv"
CHECKPOINT_FILE = Path(__file__).parent / "checkpoint.json"

# OpenAI model configuration
MODEL = "gpt-5-mini"
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Request configuration
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 1  # seconds between article fetches

# Test mode: limit number of rows to process (None = process all)
MAX_ROWS = None  # Set to a number (e.g., 5) for testing, or use --limit argument


def fetch_article_content(url: str) -> Tuple[Optional[str], Optional[BeautifulSoup]]:
    """
    Fetch article content from a URL and extract main text, returning both
    the text content and the BeautifulSoup object for metadata extraction.
    
    Args:
        url: URL of the article
        
    Returns:
        Tuple of (extracted article text, BeautifulSoup object) or (None, None) if fetch failed
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
            return (text if text else None, soup)
        
        return (None, soup)
        
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return (None, None)
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        return (None, None)


def extract_title_and_date(url: str, content: str, soup: Optional[BeautifulSoup]) -> Tuple[str, str]:
    """
    Extract title and date from article HTML/metadata.
    
    Args:
        url: URL of the article
        content: Extracted article text content
        soup: BeautifulSoup object of the HTML page
        
    Returns:
        Tuple of (title, date) - date may be empty if not found
    """
    title = ""
    date_str = ""
    
    if soup:
        # Try to extract title
        # 1. Try <title> tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            # Clean up common suffixes like " | Site Name"
            title = re.sub(r'\s*\|\s*.*$', '', title)
            title = re.sub(r'\s*-\s*.*$', '', title, count=1)
        
        # 2. Try <h1> tag if title is empty or too generic
        if not title or len(title) < 10:
            h1_tag = soup.find('h1')
            if h1_tag:
                title = h1_tag.get_text(strip=True)
        
        # 3. Try Open Graph or Twitter meta tags
        if not title or len(title) < 10:
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                title = og_title['content'].strip()
        
        if not title or len(title) < 10:
            twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
            if twitter_title and twitter_title.get('content'):
                title = twitter_title['content'].strip()
        
        # Extract date
        # 1. Try <time> tag
        time_tag = soup.find('time')
        if time_tag:
            date_str = time_tag.get('datetime', '') or time_tag.get_text(strip=True)
        
        # 2. Try meta tags for publication date
        if not date_str:
            pub_date = soup.find('meta', property='article:published_time')
            if pub_date and pub_date.get('content'):
                date_str = pub_date['content']
        
        if not date_str:
            pub_date = soup.find('meta', attrs={'name': 'published'})
            if pub_date and pub_date.get('content'):
                date_str = pub_date['content']
        
        if not date_str:
            pub_date = soup.find('meta', attrs={'name': 'date'})
            if pub_date and pub_date.get('content'):
                date_str = pub_date['content']
        
        # 3. Try to parse date from common date patterns in text
        if not date_str and content:
            # Look for dates in formats like "January 1, 2024" or "2024-01-01"
            date_patterns = [
                r'\b(\d{4}-\d{2}-\d{2})\b',
                r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
                r'\b\d{1,2}/\d{1,2}/\d{4}\b'
            ]
            for pattern in date_patterns:
                matches = re.findall(pattern, content[:1000])  # Check first 1000 chars
                if matches:
                    date_str = matches[0]
                    break
    
    # If title still not found, use URL or a default
    if not title:
        # Try to extract from URL
        title = url.split('/')[-1].replace('-', ' ').replace('_', ' ')
        if not title or len(title) < 5:
            title = "Untitled Article"
    
    # Clean up date string
    if date_str:
        # Try to format date consistently
        try:
            # Try to parse and reformat common date formats
            date_str = date_str.strip()
            # Remove timezone info for simplicity
            date_str = re.sub(r'[Tt].*$', '', date_str)  # Remove time portion
            date_str = re.sub(r'[+\-]\d{2}:?\d{2}$', '', date_str)  # Remove timezone
        except:
            pass
    
    return (title.strip(), date_str.strip())


def generate_ai_analysis(title: str, date: str, content: str, client: OpenAI) -> Optional[Dict[str, str]]:
    """
    Generate summary, tags, and notes for article using OpenAI API.
    
    Args:
        title: Article title
        date: Article date
        content: Article content
        client: OpenAI client instance
        
    Returns:
        Dictionary with 'summary', 'tags', and 'notes' keys, or None if API call failed
    """
    if not content:
        return None
    
    prompt = f"""Analyze this AI-related article and provide the following information:

Title: {title}
Date: {date if date else "Date not available"}

Article content:
{content[:20000]}

Please provide:
1. **Summary**: Provide a concise summary with:
   - First, a 1-2 sentence brief summary
   - Then, 3-5 bullet points with key facts

2. **Tags**: Provide 3-7 comma-separated tags that are relevant to AI topics. Mix general and specific tags. Examples: "generative AI, education, ChatGPT, academic integrity, policy"

3. **Notes**: Provide 1-3 sentences analyzing implications, connections to broader AI trends, or important context about this story.

Format your response as:
Summary: [your summary here]
Tags: [comma-separated tags]
Notes: [your notes here]"""

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=1000
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
                if ':' in line and not line.startswith('-') and not line.startswith('•'):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        # Save previous field
                        if current_field:
                            result[current_field] = ' '.join(current_value).strip()
                        
                        # Start new field
                        field_name = parts[0].strip().lower()
                        if 'summary' in field_name:
                            current_field = 'summary'
                        elif 'tag' in field_name:
                            current_field = 'tags'
                        elif 'note' in field_name:
                            current_field = 'notes'
                        else:
                            current_field = None
                        
                        current_value = [parts[1].strip()] if parts[1].strip() else []
                        continue
                
                # Continue current field (including bullet points)
                if current_field:
                    current_value.append(line)
            
            # Save last field
            if current_field:
                result[current_field] = ' '.join(current_value).strip()
            
            # Ensure all fields are present
            return {
                "summary": result.get("summary", ""),
                "tags": result.get("tags", ""),
                "notes": result.get("notes", "")
            }
            
        except Exception as e:
            logger.warning(f"OpenAI API error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (2 ** attempt))  # Exponential backoff
            else:
                logger.error(f"Failed to generate analysis after {MAX_RETRIES} attempts")
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
        writer.writerow(['Title', 'Date', 'URL', 'Summary', 'Tags', 'Notes'])
    
    # Statistics
    stats = {
        'processed': 0,
        'skipped': 0,
        'failed_fetch': 0,
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
                url = row.get('URL', '').strip()
                
                if not url:
                    stats['skipped'] += 1
                    logger.warning(f"[{idx + 1}/{total_rows}] No URL provided, skipping")
                    continue
                
                logger.info(f"[{idx + 1}/{total_rows}] Processing: {url[:80]}...")
                
                # Fetch article content
                content, soup = fetch_article_content(url)
                time.sleep(REQUEST_DELAY)  # Rate limiting
                
                if not content:
                    stats['failed_fetch'] += 1
                    logger.warning(f"Failed to fetch content from {url}")
                    # Still try to extract title/date from URL
                    title, date = extract_title_and_date(url, "", soup)
                    writer.writerow([title, date, url, "Failed to fetch article content", "", ""])
                    output_file.flush()
                    save_checkpoint(idx)
                    continue
                
                # Extract title and date
                title, date = extract_title_and_date(url, content, soup)
                logger.debug(f"Extracted title: {title[:60]}...")
                if date:
                    logger.debug(f"Extracted date: {date}")
                
                # Generate AI analysis
                analysis = generate_ai_analysis(title, date, content, client)
                
                if not analysis:
                    stats['failed_analysis'] += 1
                    logger.warning(f"Failed to generate analysis for {url}")
                    summary = "Failed to generate analysis"
                    tags = ""
                    notes = ""
                else:
                    stats['processed'] += 1
                    summary = analysis.get('summary', '')
                    tags = analysis.get('tags', '')
                    notes = analysis.get('notes', '')
                
                # Write to output CSV immediately
                writer.writerow([title, date, url, summary, tags, notes])
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
        logger.info(f"  Failed to analyze: {stats['failed_analysis']}")
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
                logger.error("Invalid limit value. Use: python summarize_ai.py [--limit N]")
                sys.exit(1)
        else:
            logger.error("Usage: python summarize_ai.py [--limit N]")
            logger.error("  --limit N  : Process only first N rows (for testing)")
            sys.exit(1)
    
    process_csv(max_rows=max_rows)

