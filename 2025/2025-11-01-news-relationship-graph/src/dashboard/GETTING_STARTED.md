# Getting Started with News Dashboard

Your interactive news analysis dashboard is ready to use!

## 🚀 Quick Launch

### Prerequisites Check
- ✅ Backend database imported (430 articles loaded)
- ✅ Flask API running on port 5000
- ✅ React frontend dependencies installed

### Start the Application

**Open TWO terminal windows:**

#### Terminal 1: Backend Server
```bash
cd news-summaries/dashboard/backend
python app.py
```

You should see:
```
Starting News Dashboard API server...
Server will be available at http://localhost:5000
```

#### Terminal 2: Frontend Server
```bash
cd news-summaries/dashboard/frontend
npm run dev
```

You should see:
```
  VITE ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

### Open in Browser

**Navigate to:** http://localhost:5173

## 📊 Features Overview

### 1. Dashboard Homepage
- **4 Key Metrics**: Total articles, relationships, people, organizations
- **Category Pie Chart**: Visual breakdown of article topics
- **Method Distribution**: Charts showing relationship discovery methods
- **Recent Articles**: Latest 10 articles with quick preview

### 2. Network Graph
- **Interactive D3.js visualization** of article relationships
- **Zoom & Pan**: Mouse wheel to zoom, drag to pan
- **Drag Nodes**: Click and drag articles to reorganize
- **Strength Filter**: Slider to adjust minimum relationship strength
- **Color Coded**: Nodes colored by category
- **Tooltips**: Hover for article details
- **Node Size**: Larger nodes = more connections

### 3. Sequential Stories
- **Follow-up Stories**: Direct chronological progression
- **Causal Chains**: How one story causes another
- **Context**: Stories that provide background
- **Interactive Flow**: Visual arrow-based flow
- **Filter by Type**: Focus on specific relationship patterns
- **34 High-Quality Sequences**: Discovered by GPT

### 4. Timeline Analysis
- **Line Chart**: Article publication trends over time
- **Date Groupings**: See article volume by day
- **Interactive**: Hover for exact counts

### 5. Entity Network
- **Toggle**: Switch between People and Organizations
- **Top 50 List**: Most mentioned entities with article counts
- **Click to Explore**: Select any entity to see all related articles
- **Side Panel**: Detailed article list for selected entity

### 6. Article Explorer
- **Search**: Type keywords to find articles
- **Category Filter**: Dropdown to filter by topic
- **Pagination**: Browse through 50 articles at a time
- **Article Cards**: Title, summary, category, date, and link
- **Export Ready**: All articles with metadata

## 🎯 Example Explorations

### Find Related Articles
1. Go to **Network** view
2. Adjust strength slider to 0.7 (stronger connections)
3. Look for clusters of connected nodes
4. Click and drag to reorganize
5. Hover nodes for article details

### Track an Entity
1. Go to **Entities** view
2. Click on "Donald Trump" (184 articles)
3. Scroll through all related articles
4. Switch to "Organizations" tab
5. Click "DOJ" to see Justice Department coverage

### Search by Topic
1. Go to **Articles** view
2. Type "immigration" in search box
3. Filter by "Immigration & Border" category
4. Browse the matching articles
5. Click "Read more →" to open original article

### Analyze Trends
1. Go to **Timeline** view
2. Observe publication volume over time
3. Note peak activity dates
4. Cross-reference with **Dashboard** for context

## 🔍 Tips & Tricks

**Network Graph:**
- Lower strength threshold (0.3-0.4) = more connections, more complex
- Higher threshold (0.7-0.8) = only strong relationships, clearer patterns
- Nodes arrange themselves - just wait a moment for physics simulation
- Darker lines = stronger relationships

**Entity Exploration:**
- People with 100+ articles are major news drivers
- Organizations show institutional coverage
- Click multiple entities to compare coverage

**Dashboard Insights:**
- Methods show AI vs deterministic discovery
- Category distribution reveals news balance
- Recent articles show latest additions

## 🛠️ Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (need 3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Verify database exists: `ls backend/news.db`

**Frontend shows blank:**
- Check backend is running on port 5000
- Open browser console (F12) for errors
- Verify CORS enabled in Flask app
- Try refreshing page

**Data looks wrong:**
- Re-import database: `python backend/import_data.py`
- Check CSV files exist in parent directory
- Verify file paths in import script

**Network graph too slow:**
- Reduce node limit in NetworkGraph.jsx
- Increase min_strength threshold
- Consider sampling subset of relationships

## 📈 Data Quality

Your dataset contains:
- **430 articles** across 9 categories
- **41,275 relationships** discovered
- **282 unique people** identified
- **332 organizations** tracked

**Quality Metrics:**
- Average relationship strength: 0.328
- GPT-discovered relationships: 70 (highest quality)
- Embedding-based: 551 (semantic matches)
- Deterministic: 40,654 (fast, reliable)
- No standalone temporal noise (all paired with content)

## 🎉 You're All Set!

The dashboard is fully functional and ready for exploration. 
Try different views to discover insights in your news data!

