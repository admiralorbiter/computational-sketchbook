#!/usr/bin/env python3
"""
Relationship Analysis Script

Analyzes the discovered relationships to assess quality, identify patterns,
and suggest improvements.
"""

import csv
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path

# Configuration
RELATIONSHIPS_CSV = Path(__file__).parent / "relationships_output.csv"
TAGGED_CSV = Path(__file__).parent / "tagged_output.csv"
RELATIONSHIPS_JSON = Path(__file__).parent / "relationships_graph.json"


def load_relationships():
    """Load relationships from CSV."""
    relationships = []
    with open(RELATIONSHIPS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            relationships.append(row)
    return relationships


def load_articles():
    """Load article metadata."""
    articles = {}
    with open(TAGGED_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            article_id = row.get('Article_ID', '').strip()
            if article_id:
                articles[article_id] = {
                    'title': row.get('Title', ''),
                    'category': row.get('Primary_Category', ''),
                    'people': [p.strip() for p in row.get('Key_People', '').split(',') if p.strip()],
                    'orgs': [o.strip() for o in row.get('Key_Organizations', '').split(',') if o.strip()]
                }
    return articles


def analyze_method_distribution(relationships):
    """Analyze distribution by method."""
    methods = Counter([r['Method'] for r in relationships])
    print("\n" + "="*60)
    print("METHOD DISTRIBUTION")
    print("="*60)
    total = len(relationships)
    for method, count in methods.most_common():
        pct = (count / total) * 100 if total > 0 else 0
        print(f"{method:20s}: {count:6d} ({pct:5.1f}%)")
    print(f"{'TOTAL':20s}: {total:6d}")


def analyze_relationship_types(relationships):
    """Analyze relationship types."""
    type_counts = Counter()
    
    for rel in relationships:
        types_str = rel.get('Relationship_Type', '')
        types = [t.strip() for t in types_str.split(',') if t.strip()]
        for t in types:
            type_counts[t] += 1
    
    print("\n" + "="*60)
    print("RELATIONSHIP TYPES")
    print("="*60)
    for rel_type, count in type_counts.most_common():
        print(f"{rel_type:30s}: {count:6d}")


def analyze_strength_distribution(relationships):
    """Analyze strength distribution."""
    strengths = []
    for rel in relationships:
        try:
            strength = float(rel.get('Strength', 0))
            strengths.append(strength)
        except:
            pass
    
    if not strengths:
        print("\nNo strength data available")
        return
    
    strengths.sort()
    n = len(strengths)
    
    print("\n" + "="*60)
    print("STRENGTH DISTRIBUTION")
    print("="*60)
    print(f"Total relationships: {n}")
    print(f"Min strength: {strengths[0]:.3f}")
    print(f"Max strength: {strengths[-1]:.3f}")
    print(f"Mean strength: {sum(strengths)/n:.3f}")
    print(f"Median strength: {strengths[n//2]:.3f}")
    
    # Strength ranges
    ranges = [
        (0.8, 1.0, "Very Strong (0.8-1.0)"),
        (0.6, 0.8, "Strong (0.6-0.8)"),
        (0.4, 0.6, "Moderate (0.4-0.6)"),
        (0.2, 0.4, "Weak (0.2-0.4)"),
        (0.0, 0.2, "Very Weak (0.0-0.2)")
    ]
    
    print("\nStrength Ranges:")
    for low, high, label in ranges:
        count = sum(1 for s in strengths if low <= s < high)
        pct = (count / n) * 100 if n > 0 else 0
        print(f"{label:25s}: {count:6d} ({pct:5.1f}%)")


def analyze_article_connectivity(relationships):
    """Analyze which articles are most/least connected."""
    article_connections = defaultdict(int)
    
    for rel in relationships:
        source = rel.get('Source_Article_ID', '')
        target = rel.get('Target_Article_ID', '')
        article_connections[source] += 1
        article_connections[target] += 1
    
    print("\n" + "="*60)
    print("ARTICLE CONNECTIVITY")
    print("="*60)
    
    # Most connected
    print(f"\nMost Connected Articles (Top 10):")
    for art_id, count in Counter(article_connections).most_common(10):
        print(f"  {art_id}: {count} connections")
    
    # Least connected
    print(f"\nLeast Connected Articles (Bottom 10):")
    for art_id, count in Counter(article_connections).most_common()[-10:]:
        print(f"  {art_id}: {count} connections")
    
    # Isolated articles
    all_articles = set(article_connections.keys())
    connected_articles = set([r.get('Source_Article_ID', '') for r in relationships] +
                            [r.get('Target_Article_ID', '') for r in relationships])
    isolated = all_articles - connected_articles
    if isolated:
        print(f"\nIsolated Articles (no relationships): {len(isolated)}")
        print(f"  Examples: {', '.join(list(isolated)[:10])}")


def analyze_people_connections(relationships):
    """Analyze people connections."""
    people_articles = defaultdict(set)
    
    for rel in relationships:
        people_str = rel.get('People_Connection', '')
        if not people_str:
            continue
        
        source = rel.get('Source_Article_ID', '')
        target = rel.get('Target_Article_ID', '')
        people = [p.strip().lower() for p in people_str.split(',') if p.strip()]
        
        for person in people:
            people_articles[person].add(source)
            people_articles[person].add(target)
    
    print("\n" + "="*60)
    print("PEOPLE CONNECTIONS")
    print("="*60)
    print(f"Unique people connecting articles: {len(people_articles)}")
    
    # Most connected people
    print(f"\nMost Connected People (Top 10):")
    people_counts = [(person, len(articles)) for person, articles in people_articles.items()]
    people_counts.sort(key=lambda x: x[1], reverse=True)
    for person, count in people_counts[:10]:
        print(f"  {person.title()}: {count} articles connected")


def analyze_org_connections(relationships):
    """Analyze organization connections."""
    org_articles = defaultdict(set)
    
    for rel in relationships:
        orgs_str = rel.get('Org_Connection', '')
        if not orgs_str:
            continue
        
        source = rel.get('Source_Article_ID', '')
        target = rel.get('Target_Article_ID', '')
        orgs = [o.strip().lower() for o in orgs_str.split(',') if o.strip()]
        
        for org in orgs:
            org_articles[org].add(source)
            org_articles[org].add(target)
    
    print("\n" + "="*60)
    print("ORGANIZATION CONNECTIONS")
    print("="*60)
    print(f"Unique organizations connecting articles: {len(org_articles)}")
    
    # Most connected orgs
    print(f"\nMost Connected Organizations (Top 10):")
    org_counts = [(org, len(articles)) for org, articles in org_articles.items()]
    org_counts.sort(key=lambda x: x[1], reverse=True)
    for org, count in org_counts[:10]:
        print(f"  {org.title()}: {count} articles connected")


def analyze_gpt_quality(relationships, articles):
    """Analyze quality of GPT-discovered relationships."""
    gpt_rels = [r for r in relationships if r.get('Method') == 'gpt_cluster']
    
    if not gpt_rels:
        print("\nNo GPT-discovered relationships found")
        return
    
    print("\n" + "="*60)
    print("GPT-DISCOVERED RELATIONSHIPS ANALYSIS")
    print("="*60)
    print(f"Total GPT relationships: {len(gpt_rels)}")
    
    # Sample some GPT relationships
    print(f"\nSample GPT-Discovered Relationships (10 examples):")
    for i, rel in enumerate(gpt_rels[:10], 1):
        source = rel.get('Source_Article_ID', '')
        target = rel.get('Target_Article_ID', '')
        rel_type = rel.get('Relationship_Type', '')
        strength = rel.get('Strength', '')
        reason = rel.get('Reason', '')[:80]
        
        source_title = articles.get(source, {}).get('title', 'Unknown')[:50]
        target_title = articles.get(target, {}).get('title', 'Unknown')[:50]
        
        print(f"\n{i}. {source} -> {target}")
        print(f"   Type: {rel_type}")
        print(f"   Strength: {strength}")
        print(f"   Source: {source_title}...")
        print(f"   Target: {target_title}...")
        print(f"   Reason: {reason}...")


def analyze_deterministic_vs_gpt(relationships):
    """Compare deterministic vs GPT relationships."""
    det_rels = [r for r in relationships if r.get('Method') == 'deterministic']
    gpt_rels = [r for r in relationships if r.get('Method') == 'gpt_cluster']
    emb_rels = [r for r in relationships if r.get('Method') == 'embedding']
    
    print("\n" + "="*60)
    print("METHOD COMPARISON")
    print("="*60)
    
    for label, rels in [("Deterministic", det_rels), ("GPT Cluster", gpt_rels), ("Embedding", emb_rels)]:
        if not rels:
            continue
        
        strengths = [float(r.get('Strength', 0)) for r in rels if r.get('Strength')]
        if strengths:
            avg_strength = sum(strengths) / len(strengths)
            print(f"\n{label}:")
            print(f"  Count: {len(rels)}")
            print(f"  Avg Strength: {avg_strength:.3f}")
            
            # Unique relationship types
            types = set()
            for rel in rels:
                rel_types = [t.strip() for t in rel.get('Relationship_Type', '').split(',') if t.strip()]
                types.update(rel_types)
            print(f"  Unique Types: {len(types)} ({', '.join(sorted(types)[:10])})")


def assess_quality(relationships, articles):
    """Overall quality assessment and recommendations."""
    print("\n" + "="*60)
    print("QUALITY ASSESSMENT & RECOMMENDATIONS")
    print("="*60)
    
    total = len(relationships)
    total_articles = len(articles)
    
    issues = []
    recommendations = []
    
    # Check for isolated articles
    connected = set()
    for rel in relationships:
        connected.add(rel.get('Source_Article_ID', ''))
        connected.add(rel.get('Target_Article_ID', ''))
    isolated = total_articles - len(connected)
    
    if isolated > 0:
        issues.append(f"{isolated} articles have no relationships")
        recommendations.append("Consider lowering similarity threshold or expanding date range for temporal proximity")
    
    # Check strength distribution
    det_strengths = [float(r.get('Strength', 0)) for r in relationships if r.get('Method') == 'deterministic']
    if det_strengths:
        weak_count = sum(1 for s in det_strengths if s < 0.2)
        if weak_count > len(det_strengths) * 0.3:
            issues.append(f"{(weak_count/len(det_strengths)*100):.1f}% of relationships have very weak strength (<0.2)")
            recommendations.append("Consider filtering out weak relationships or adjusting strength thresholds")
    
    # Check for GPT coverage
    gpt_count = sum(1 for r in relationships if 'gpt' in r.get('Method', '').lower())
    if gpt_count == 0:
        issues.append("No GPT-discovered relationships found")
        recommendations.append("Run with GPT analysis enabled to discover complex/nuanced relationships")
    
    # Temporal proximity dominance
    temp_count = sum(1 for r in relationships if 'temporal_proximity' in r.get('Relationship_Type', ''))
    if temp_count > total * 0.5:
        issues.append(f"{(temp_count/total*100):.1f}% of relationships are just temporal proximity")
        recommendations.append("Consider increasing date proximity threshold or adding more sophisticated matching")
    
    # Print issues
    if issues:
        print("\nPotential Issues:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("\n[OK] No major issues detected")
    
    # Print recommendations
    if recommendations:
        print("\nRecommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    # Overall stats
    print(f"\nOverall Statistics:")
    print(f"  Total articles: {total_articles}")
    print(f"  Total relationships: {total}")
    print(f"  Avg relationships per article: {total/total_articles:.1f}" if total_articles > 0 else "  N/A")
    
    # Coverage
    coverage = (len(connected) / total_articles * 100) if total_articles > 0 else 0
    print(f"  Article coverage: {coverage:.1f}% have relationships")
    
    print(f"\n[OK] Analysis complete!")


def main():
    """Main analysis function."""
    print("\n" + "="*60)
    print("RELATIONSHIP ANALYSIS REPORT")
    print("="*60)
    print(f"\nAnalyzing: {RELATIONSHIPS_CSV}")
    
    # Load data
    relationships = load_relationships()
    articles = load_articles()
    
    print(f"Loaded {len(relationships)} relationships from {len(articles)} articles")
    
    # Run analyses
    analyze_method_distribution(relationships)
    analyze_relationship_types(relationships)
    analyze_strength_distribution(relationships)
    analyze_article_connectivity(relationships)
    analyze_people_connections(relationships)
    analyze_org_connections(relationships)
    analyze_deterministic_vs_gpt(relationships)
    analyze_gpt_quality(relationships, articles)
    assess_quality(relationships, articles)
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

