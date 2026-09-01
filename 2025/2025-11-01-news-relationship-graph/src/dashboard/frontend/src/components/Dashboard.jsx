import { useState, useEffect } from 'react';
import { getStats, getCategories, getArticles } from '../api/client';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#0088fe', '#00c49f', '#ffbb28', '#ff8042', '#8884d8'];

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [categories, setCategories] = useState([]);
  const [recentArticles, setRecentArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsRes, categoriesRes, articlesRes] = await Promise.all([
        getStats(),
        getCategories(),
        getArticles({ page: 1, page_size: 10 })
      ]);
      setStats(statsRes.data);
      setCategories(categoriesRes.data.categories);
      setRecentArticles(articlesRes.data.articles);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <h2>Dashboard Overview</h2>
      
      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats?.total_articles || 0}</div>
          <div className="stat-label">Total Articles</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats?.total_relationships || 0}</div>
          <div className="stat-label">Relationships</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats?.unique_people || 0}</div>
          <div className="stat-label">People</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats?.unique_orgs || 0}</div>
          <div className="stat-label">Organizations</div>
        </div>
      </div>

      {/* Charts */}
      <div className="charts-grid">
        <div className="chart-card">
          <h3>Articles by Category</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categories}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {categories.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Method Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats?.methods || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="method" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Articles */}
      <div className="recent-articles">
        <h3>Recent Articles</h3>
        <div className="articles-list">
          {recentArticles.map(article => (
            <div key={article.article_id} className="article-item">
              <div className="article-title">{article.title}</div>
              <div className="article-meta">
                <span className="article-category">{article.category}</span>
                <span className="article-date">{article.date}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

