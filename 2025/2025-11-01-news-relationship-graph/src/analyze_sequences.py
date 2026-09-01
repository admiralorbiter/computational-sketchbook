#!/usr/bin/env python3
"""
Analyze sequential news relationships to identify story arcs and causal chains.

This script extracts and visualizes the temporal and causal relationships
discovered by the GPT analysis, showing how news stories unfold over time.
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

# Paths
REL_CSV = Path(__file__).parent / "relationships_output.csv"
TAGGED_CSV = Path(__file__).parent / "tagged_output.csv"
OUTPUT_JSON = Path(__file__).parent / "story_sequences.json"

# Sequence relationship types
SEQUENCE_TYPES = ['follows_up', 'causes_chain', 'causal_chain', 'context_for']


def load_articles() -> Dict[str, Dict]:
    """Load articles with metadata."""
    articles = {}
    with open(TAGGED_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            art_id = row.get('Article_ID')
            if art_id:
                articles[art_id] = {
                    'title': row.get('Title', ''),
                    'date': row.get('Date', ''),
                    'category': row.get('Primary_Category', ''),
                }
    return articles


def parse_date(date_str: str) -> datetime:
    """Parse date string."""
    try:
        return datetime.strptime(date_str, "%m/%d/%y")
    except:
        try:
            return datetime.strptime(date_str, "%m/%d/%Y")
        except:
            return datetime(1970, 1, 1)  # Default


def load_sequence_relationships() -> List[Dict]:
    """Load only sequential relationship types."""
    sequences = []
    with open(REL_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rel_type = row.get('Relationship_Type', '')
            # Check if this is a sequence type
            if any(seq_type in rel_type for seq_type in SEQUENCE_TYPES):
                sequences.append({
                    'source': row.get('Source_Article_ID'),
                    'target': row.get('Target_Article_ID'),
                    'type': rel_type,
                    'strength': float(row.get('Strength', 0)),
                    'method': row.get('Method', ''),
                    'reason': row.get('Reason', '')
                })
    return sequences


def build_story_arcs(sequences: List[Dict], articles: Dict[str, Dict]) -> List[Dict]:
    """Build story arcs from sequence relationships."""
    # Create adjacency list
    arcs = defaultdict(list)
    
    for seq in sequences:
        source = seq['source']
        target = seq['target']
        arcs[source].append({
            'target': target,
            'type': seq['type'],
            'strength': seq['strength'],
            'reason': seq['reason']
        })
    
    # Find chains
    visited = set()
    story_arcs = []
    
    def follow_chain(start: str, chain: List[str], depth: int = 0):
        """Follow a chain recursively."""
        if depth > 10 or start in visited:  # Prevent infinite loops
            return
        
        visited.add(start)
        chain.append(start)
        
        if start in arcs:
            for next_seq in arcs[start]:
                if next_seq['target'] not in visited:
                    follow_chain(next_seq['target'], chain.copy(), depth + 1)
        
        # If we've reached a leaf, save the chain
        if depth == 0 or (start in arcs and not any(n['target'] not in visited for n in arcs[start])):
            if len(chain) >= 2:
                story_arcs.append(chain)
    
    # Start from articles with no incoming sequences
    all_targets = {seq['target'] for seq in sequences}
    starts = {seq['source'] for seq in sequences if seq['source'] not in all_targets}
    
    for start in starts:
        if start not in visited:
            follow_chain(start, [])
    
    return story_arcs


def analyze_sequences(sequences: List[Dict], articles: Dict[str, Dict]) -> Dict:
    """Analyze and organize sequence data."""
    
    print(f"\n{'='*60}")
    print("SEQUENTIAL NEWS ANALYSIS")
    print(f"{'='*60}\n")
    
    print(f"Found {len(sequences)} sequential relationships\n")
    
    # Group by type
    by_type = defaultdict(list)
    for seq in sequences:
        rel_type = seq['type']
        by_type[rel_type].append(seq)
    
    # Print breakdown
    print("Relationship Type Breakdown:")
    for rel_type, seqs in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {rel_type}: {len(seqs)} relationships")
    print()
    
    # Build story arcs
    arcs = build_story_arcs(sequences, articles)
    
    print(f"Story Arcs Found: {len(arcs)}")
    print()
    
    # Show longest chains
    arcs_by_length = sorted(arcs, key=len, reverse=True)[:20]
    
    print("Top 10 Longest Story Chains:")
    for i, arc in enumerate(arcs_by_length[:10], 1):
        print(f"\n{i}. Chain of {len(arc)} articles:")
        for art_id in arc:
            art = articles.get(art_id, {})
            title = art.get('title', 'Unknown')
            if len(title) > 60:
                title = title[:60] + '...'
            print(f"   - {art_id}: {title}")
        print()
    
    # Analyze by strength
    strong_sequences = [s for s in sequences if s['strength'] >= 0.8]
    print(f"\nStrong Sequences (strength >= 0.8): {len(strong_sequences)}")
    print("\nTop 10 Strongest Sequences:")
    
    sorted_sequences = sorted(sequences, key=lambda x: x['strength'], reverse=True)[:10]
    for i, seq in enumerate(sorted_sequences, 1):
        source_art = articles.get(seq['source'], {})
        target_art = articles.get(seq['target'], {})
        
        source_title = source_art.get('title', 'Unknown')
        if len(source_title) > 40:
            source_title = source_title[:40] + '...'
        
        target_title = target_art.get('title', 'Unknown')
        if len(target_title) > 40:
            target_title = target_title[:40] + '...'
        
        print(f"\n{i}. {seq['source']} -> {seq['target']} (strength: {seq['strength']:.2f})")
        print(f"   Type: {seq['type']}")
        print(f"   From: {source_title}")
        print(f"   To: {target_title}")
        print(f"   Reason: {seq['reason']}")
        print()
    
    # Create structured output
    output = {
        'total_sequences': len(sequences),
        'type_breakdown': {k: len(v) for k, v in by_type.items()},
        'story_arcs': arcs,
        'top_sequences': [
            {
                'source': seq['source'],
                'target': seq['target'],
                'type': seq['type'],
                'strength': seq['strength'],
                'reason': seq['reason'],
                'source_title': articles.get(seq['source'], {}).get('title', ''),
                'target_title': articles.get(seq['target'], {}).get('title', ''),
                'source_date': articles.get(seq['source'], {}).get('date', ''),
                'target_date': articles.get(seq['target'], {}).get('date', ''),
            }
            for seq in sorted(sequences, key=lambda x: x['strength'], reverse=True)[:50]
        ]
    }
    
    # Save to JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Results saved to: {OUTPUT_JSON}")
    print(f"{'='*60}\n")
    
    return output


def main():
    """Main analysis function."""
    print("Loading data...")
    articles = load_articles()
    sequences = load_sequence_relationships()
    
    print(f"Loaded {len(articles)} articles")
    print(f"Found {len(sequences)} sequential relationships\n")
    
    results = analyze_sequences(sequences, articles)
    
    return 0


if __name__ == "__main__":
    exit(main())

