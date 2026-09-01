# News Dashboard

Interactive web dashboard for visualizing and exploring news articles, relationships, and insights from the news analysis pipeline.

## Architecture

- **Backend**: Flask API with SQLite database
- **Frontend**: React + Vite with D3.js and Recharts
- **Database**: SQLite with 430 articles, 41K+ relationships, 282 people, 332 organizations

## Backend Setup

The backend is complete and running!

### Prerequisites

```bash
pip install flask flask-cors python-dotenv
```

### Database Import

First, import the data from CSVs into SQLite:

```bash
cd news-summaries/dashboard/backend
python import_data.py
```

This creates `news.db` with:
- Articles table
- Relationships table  
- People table
- Organizations table
- Performance indexes

### Run API Server

```bash
python app.py
```

Server runs on `http://localhost:5000`

### API Endpoints

#### Statistics
- `GET /api/stats` - Dashboard statistics

#### Articles
- `GET /api/articles?page=1&page_size=50` - Paginated articles
- `GET /api/articles/<article_id>` - Single article details
- `GET /api/search?q=term` - Search articles

#### Relationships
- `GET /api/relationships` - All relationships (with filters)
  - Query params: `source_id`, `target_id`, `rel_type`, `min_strength`, `method`, `limit`

#### Network
- `GET /api/network` - Graph data (nodes + edges)
  - Query params: `limit`, `min_strength`

#### Timeline
- `GET /api/timeline` - Articles grouped by date

#### Entities
- `GET /api/entities/people` - All people
- `GET /api/entities/orgs` - All organizations  
- `GET /api/entity/<type>/<name>` - Articles for specific entity

#### Categories
- `GET /api/categories` - Category breakdown

### Example Queries

```bash
# Get statistics
curl http://localhost:5000/api/stats

# Get first 5 articles
curl "http://localhost:5000/api/articles?page=1&page_size=5"

# Search for articles
curl "http://localhost:5000/api/search?q=Trump"

# Get network graph data
curl "http://localhost:5000/api/network?min_strength=0.5"

# Get top people
curl http://localhost:5000/api/entities/people
```

## Frontend Setup

The React frontend is complete!

### Run Frontend Server

```bash
cd news-summaries/dashboard/frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

### Frontend Features

**6 Main Views:**

1. **Dashboard** - Overview with stats, charts, and recent articles
2. **Network** - Interactive D3.js force-directed graph of article relationships
3. **Timeline** - Article publication trends over time
4. **Sequences** - Sequential stories: follow-ups, causal chains, and context relationships
5. **Entities** - People and organizations with article connections
6. **Articles** - Searchable article explorer with filtering

**Interactive Features:**
- Zoom/pan on network graph
- Drag nodes to reorganize layout
- Click entities to view related articles
- Search and filter articles
- Strength threshold slider for network
- Category filtering

## Quick Start

### Start Both Servers

**Terminal 1 - Backend:**
```bash
cd news-summaries/dashboard/backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd news-summaries/dashboard/frontend
npm run dev
```

Then open: **http://localhost:5173**

## Current Status

✅ **Backend**: Complete and tested  
✅ **Frontend**: Complete and running  
✅ **Database**: 430 articles, 41K+ relationships loaded

The full dashboard is ready for exploration!

