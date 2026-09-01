import { useState, useEffect } from 'react';
import { getEntities, getEntityArticles } from '../api/client';

function EntityNetwork() {
  const [entityType, setEntityType] = useState('people');
  const [entities, setEntities] = useState([]);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [entityArticles, setEntityArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEntities();
  }, [entityType]);

  const loadEntities = async () => {
    try {
      setLoading(true);
      const response = await getEntities(entityType);
      setEntities(response.data.entities);
      setSelectedEntity(null);
      setEntityArticles([]);
    } catch (error) {
      console.error('Error loading entities:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEntityClick = async (entityName) => {
    try {
      const response = await getEntityArticles(entityType, entityName);
      setSelectedEntity(entityName);
      setEntityArticles(response.data.articles);
    } catch (error) {
      console.error('Error loading entity articles:', error);
    }
  };

  if (loading) {
    return <div className="loading">Loading entities...</div>;
  }

  return (
    <div className="entity-network">
      <h2>Entity Network</h2>
      
      <div className="entity-controls">
        <button 
          className={entityType === 'people' ? 'active' : ''}
          onClick={() => setEntityType('people')}
        >
          People
        </button>
        <button 
          className={entityType === 'orgs' ? 'active' : ''}
          onClick={() => setEntityType('orgs')}
        >
          Organizations
        </button>
      </div>

      <div className="entity-layout">
        <div className="entity-list">
          <h3>Top {entityType === 'people' ? 'People' : 'Organizations'}</h3>
          <div className="entities">
            {entities.slice(0, 50).map((entity, idx) => (
              <div 
                key={idx} 
                className={`entity-item ${selectedEntity === entity.name ? 'selected' : ''}`}
                onClick={() => handleEntityClick(entity.name)}
              >
                <span className="entity-name">{entity.name}</span>
                <span className="entity-count">{entity.article_count} articles</span>
              </div>
            ))}
          </div>
        </div>

        <div className="entity-articles">
          {selectedEntity ? (
            <>
              <h3>Articles by {selectedEntity}</h3>
              <div className="articles-list">
                {entityArticles.map(article => (
                  <div key={article.article_id} className="article-item">
                    <div className="article-title">{article.title}</div>
                    <div className="article-meta">
                      <span className="article-category">{article.category}</span>
                      <span className="article-date">{article.date}</span>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="placeholder">Select an entity to view articles</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default EntityNetwork;

