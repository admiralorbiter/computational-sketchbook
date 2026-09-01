# News Article Analysis Pipeline

A comprehensive pipeline for processing, summarizing, tagging, and discovering relationships in news articles using OpenAI's GPT models and embeddings.

## Overview

This pipeline processes a CSV of news articles through three stages:

1. **Summarize** - Fetch articles from URLs and generate summaries
2. **Tag** - Analyze articles and extract metadata (categories, tags, entities, relationships)
3. **Relationships** - Discover comprehensive relationships between articles

## Files

### Core Scripts

- `summarize.py` - Fetches articles from URLs and generates AI summaries
- `tag.py` - Analyzes articles and extracts metadata using embeddings and GPT
- `relationships.py` - Discovers relationships between articles using multiple strategies
- `analyze_relationships.py` - Analyzes relationship quality and provides recommendations
- `analyze_sequences.py` - Analyzes sequential story arcs and causal chains

### Data Files

- `Research and References - Current Events.csv` - **Input**: Raw article data with URLs
- `summarized_output.csv` - Summarized articles (output from `summarize.py`)
- `tagged_output.csv` - Tagged articles with metadata (output from `tag.py`)
- `relationships_output.csv` - Discovered relationships (output from `relationships.py`)
- `relationships_graph.json` - Network graph representation of relationships
- `story_sequences.json` - Sequential story arcs and causal chains
- `dashboard/` - Interactive web dashboard for visualization

### Checkpoint Files

- `checkpoint.json` - Progress for summarize.py
- `tag_checkpoint.json` - Progress and embeddings for tag.py
- `relationships_checkpoint.json` - Progress for relationships.py

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

Required packages:
- `openai` - AI API for GPT and embeddings
- `requests` - HTTP requests for fetching articles
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser backend
- `python-dotenv` - Environment variable management
- `numpy` - Numerical operations for similarity calculations

## Setup

1. Set your OpenAI API key in `.env` file in the project root:

```
OPENAI_API_KEY=your-key-here
```

2. Ensure your input CSV has these columns: `Title`, `Date`, `URL`

## Usage

### Stage 1: Summarize Articles

Generate summaries from article URLs:

```bash
# Test with 5 articles
python summarize.py --limit 5

# Process all articles
python summarize.py
```

**Output**: `summarized_output.csv`
- Adds `Summary` column with AI-generated summaries

**Features**:
- Fetches article content from URLs
- Extracts main text (removes ads, navigation)
- Generates 1-2 sentence brief + 3-5 bullet points
- Saves progress incrementally (resumable)
- Handles errors gracefully

### Stage 2: Tag Articles

Analyze articles and extract metadata:

```bash
# Test with 5 articles
python tag.py --limit 5

# Process all articles
python tag.py
```

**Output**: `tagged_output.csv`
- Adds columns: `Article_ID`, `Primary_Category`, `Tags`, `Key_People`, `Key_Organizations`, `Related_Articles`, `Notes`

**Features**:
- Assigns unique article IDs (ART-XXXX format)
- Classifies articles into 9 predefined categories
- Extracts tags (3-7 per article, general + specific)
- Identifies key people and organizations
- Uses embedding-based similarity search for related articles
- Cost-efficient: ~$0.02 per 1M tokens for embeddings

**Categories**:
- Legal & Judicial
- Federal Spending & Cuts
- Government Workforce
- Immigration & Border
- Education & Research
- Musk/Doge
- International Relations
- Media & Info Control
- Civil Rights & Democracy

### Stage 3: Discover Relationships

Discover comprehensive relationships between articles:

```bash
# Test with 20 articles
python relationships.py --limit 20

# Process all articles
python relationships.py

# Deterministic relationships only (no GPT, faster)
python relationships.py --deterministic-only
```

**Output**: 
- `relationships_output.csv` - All discovered relationships
- `relationships_graph.json` - Network graph with entity networks

**Features**:

**Deterministic Relationships** (no API calls):
- Articles sharing same people
- Articles sharing same organizations
- Articles in same category
- Articles with overlapping tags
- Articles within 7 days of each other

**Embedding-based Relationships**:
- Content similarity using cosine similarity
- Threshold: 0.65

**GPT-discovered Relationships** (cluster analysis):
- Causal chains (article A led to article B)
- Follow-up reporting (sequential stories)
- Part of larger story (hierarchical arcs)
- Thematic links
- Contradicting narratives
- Context relationships

**Methods**:
- `deterministic` - Fast, rule-based
- `embedding` - Semantic similarity
- `gpt_cluster` - AI analysis within clusters

**Relationship Types**:
- `shared_person`
- `shared_organization`
- `same_category`
- `tag_overlap`
- `temporal_proximity`
- `content_similarity`
- `causes_chain`
- `follows_up`
- `part_of_story`
- `thematic_link`
- `contradicts`
- `context_for`

## Pipeline Workflow

```
Input CSV
   ↓
[summarize.py] → Fetch articles, generate summaries
   ↓
summarized_output.csv
   ↓
[tag.py] → Generate embeddings, extract metadata, find initial relationships
   ↓
tagged_output.csv + tag_checkpoint.json (embeddings)
   ↓
[relationships.py] → Discover comprehensive relationships
   ↓
relationships_output.csv + relationships_graph.json
```

## Stage 4: Analyze Relationships

Analyze the quality and patterns in discovered relationships:

```bash
python analyze_relationships.py
```

**Output**: Comprehensive console report with statistics and recommendations

**Features**:
- Method distribution analysis (deterministic vs embedding vs GPT)
- Relationship type breakdown
- Strength distribution and quality metrics
- Article connectivity patterns
- Entity network analysis (people/organizations)
- Quality assessment and improvement recommendations

**Example Output**:
- Shows which methods discovered what percentage of relationships
- Identifies most/least connected articles
- Highlights high-quality GPT discoveries
- Provides actionable recommendations

## Advanced Features

### Checkpoint & Resume

All scripts support checkpointing:
- Save progress after each article
- Resume from interruption
- No data loss

### Test Mode

Test with limited articles:
```bash
python summarize.py --limit 5
python tag.py --limit 5
python relationships.py --limit 20
```

### Cost Management

The pipeline uses cost-effective models:
- **Embeddings**: `text-embedding-3-small` (~$0.02 per 1M tokens)
- **Analysis**: `gpt-4o-mini` (affordable yet capable)
- **Batch processing**: Cluster-based GPT analysis (1 call per 15-25 articles)

Estimated costs for 590 articles:
- Stage 1 (Summarize): ~$2-5
- Stage 2 (Tag): ~$3-8
- Stage 3 (Relationships): ~$3-8
- **Total**: ~$8-21

### Global Memory & Efficiency

**Smart similarity search**:
- Uses embeddings for semantic similarity (O(n) complexity, not O(n²))
- Only sends top-K similar articles to GPT
- Avoids sending all articles to API each time

**Clustering**:
- Groups articles by category for batch processing
- Single GPT call per cluster analyzes all internal relationships
- More efficient than pairwise analysis

**Data structures**:
- Entity indexes for fast lookups
- Embedding matrices for fast similarity calculations
- Article caches to avoid redundant processing

## Output Files

### summarized_output.csv

Columns: `Title`, `Date`, `URL`, `Summary`

### tagged_output.csv

Columns: `Title`, `Date`, `URL`, `Summary`, `Article_ID`, `Primary_Category`, `Tags`, `Key_People`, `Key_Organizations`, `Related_Articles`, `Notes`

### relationships_output.csv

Columns: `Source_Article_ID`, `Target_Article_ID`, `Relationship_Type`, `Strength`, `Method`, `Reason`, `People_Connection`, `Org_Connection`

Example:
```
ART-0001,ART-0003,"shared_person, temporal_proximity",0.386,deterministic,"Deterministic match: shared_person, temporal_proximity",elon musk,
```

### relationships_graph.json

Graph structure with:
- `articles`: Article data with relationships
- `people_network`: Person → articles mapping
- `organization_network`: Organization → articles mapping

## Tips

1. **Start small**: Use `--limit` to test with 5-20 articles first
2. **Monitor costs**: Check OpenAI usage dashboard
3. **Handle errors**: Scripts continue on errors, check logs
4. **Resume capability**: Scripts auto-resume from checkpoints
5. **Clean restarts**: Delete checkpoint files to start fresh

## Troubleshooting

**"OPENAI_API_KEY environment variable not set"**
- Create `.env` file in project root with your API key
- Or export environment variable: `export OPENAI_API_KEY=your-key`

**"Failed to fetch article content"**
- Article URL may be blocked, require auth, or be invalid
- Check URLs in input CSV

**Empty summaries**
- Some articles don't fetch properly
- Check article URLs and network connectivity
- Articles with "Failed to fetch" are skipped in later stages

**GPT parsing errors**
- Script handles JSON extraction from various formats
- Check logs for details if issues persist

## License

MIT License

