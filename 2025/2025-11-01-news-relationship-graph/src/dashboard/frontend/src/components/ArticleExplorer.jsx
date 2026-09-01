import { useState, useEffect } from 'react';
import { getArticles, getCategories, searchArticles } from '../api/client';

function ArticleExplorer() {
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [total, setTotal] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    loadArticles();
  }, [page, selectedCategory]);

  const loadCategories = async () => {
    try {
      const response = await getCategories();
      setCategories(response.data.categories);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const loadArticles = async () => {
    try {
      setLoading(true);
      const params = {
        page,
        page_size: pageSize,
      };
      if (selectedCategory) {
        params.category = selectedCategory;
      }
      
      let response;
      if (searchQuery) {
        response = await searchArticles(searchQuery);
      } else {
        response = await getArticles(params);
      }
      
      setArticles(response.data.articles);
      setTotal(response.data.total || 0);
    } catch (error) {
      console.error('Error loading articles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    loadArticles();
  };

  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
    setPage(1);
  };

  if (loading) {
    return <div className="loading">Loading articles...</div>;
  }

  return (
    <div className="article-explorer">
      <h2>Article Explorer</h2>
      
      <div className="explorer-controls">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search articles..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch}>Search</button>
        </div>

        <div className="category-filter">
          <label>Category:</label>
          <select
            value={selectedCategory}
            onChange={(e) => handleCategoryChange(e.target.value)}
          >
            <option value="">All Categories</option>
            {categories.map(cat => (
              <option key={cat.category} value={cat.category}>
                {cat.category} ({cat.count})
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="articles-stats">
        Showing {articles.length} of {total} articles
      </div>

      <div className="articles-grid">
        {articles.map(article => (
          <div key={article.article_id} className="article-card">
            <div className="article-title">{article.title}</div>
            <div className="article-meta">
              <span className="article-category">{article.category}</span>
              <span className="article-date">{article.date}</span>
            </div>
            {article.summary && (
              <div className="article-summary">
                {article.summary.substring(0, 200)}...
              </div>
            )}
            <a href={article.url} target="_blank" rel="noopener noreferrer" className="article-link">
              Read more →
            </a>
          </div>
        ))}
      </div>

      {!searchQuery && (
        <div className="pagination">
          <button disabled={page === 1} onClick={() => setPage(page - 1)}>
            Previous
          </button>
          <span>Page {page}</span>
          <button disabled={page * pageSize >= total} onClick={() => setPage(page + 1)}>
            Next
          </button>
        </div>
      )}
    </div>
  );
}

export default ArticleExplorer;

