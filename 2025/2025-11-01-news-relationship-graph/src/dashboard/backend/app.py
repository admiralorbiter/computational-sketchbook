#!/usr/bin/env python3
"""
Flask API server for news dashboard.

Provides RESTful API endpoints for accessing article and relationship data.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

from database import (
    get_articles, get_article,
    get_relationships,
    get_network_data,
    get_timeline_data,
    get_entities, get_entity_articles,
    get_categories, get_stats
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get dashboard statistics."""
    try:
        stats = get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/articles', methods=['GET'])
def api_articles():
    """Get paginated articles with optional filtering."""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        category = request.args.get('category')
        search = request.args.get('search')
        
        articles, total = get_articles(page, page_size, category, search)
        
        return jsonify({
            'articles': articles,
            'total': total,
            'page': page,
            'page_size': page_size
        })
    except Exception as e:
        logger.error(f"Error getting articles: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/articles/<article_id>', methods=['GET'])
def api_article_detail(article_id):
    """Get a single article by ID."""
    try:
        article = get_article(article_id)
        if not article:
            return jsonify({'error': 'Article not found'}), 404
        
        return jsonify(article)
    except Exception as e:
        logger.error(f"Error getting article: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/relationships', methods=['GET'])
def api_relationships():
    """Get relationships with optional filters."""
    try:
        source_id = request.args.get('source_id')
        target_id = request.args.get('target_id')
        rel_type = request.args.get('rel_type')
        min_strength = request.args.get('min_strength')
        method = request.args.get('method')
        limit = request.args.get('limit')
        
        min_strength = float(min_strength) if min_strength else None
        limit = int(limit) if limit else None
        
        relationships = get_relationships(
            source_id, target_id, rel_type, min_strength, method, limit
        )
        
        return jsonify({'relationships': relationships})
    except Exception as e:
        logger.error(f"Error getting relationships: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/network', methods=['GET'])
def api_network():
    """Get network graph data."""
    try:
        limit = request.args.get('limit')
        min_strength = request.args.get('min_strength')
        
        limit = int(limit) if limit else None
        min_strength = float(min_strength) if min_strength else None
        
        network_data = get_network_data(limit, min_strength)
        
        return jsonify(network_data)
    except Exception as e:
        logger.error(f"Error getting network data: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/timeline', methods=['GET'])
def api_timeline():
    """Get timeline data grouped by date."""
    try:
        timeline_data = get_timeline_data()
        return jsonify({'timeline': timeline_data})
    except Exception as e:
        logger.error(f"Error getting timeline: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/entities/<entity_type>', methods=['GET'])
def api_entities(entity_type):
    """Get all people or organizations."""
    try:
        if entity_type not in ['people', 'orgs']:
            return jsonify({'error': 'Invalid entity type'}), 400
        
        entities = get_entities(entity_type)
        return jsonify({'entities': entities})
    except Exception as e:
        logger.error(f"Error getting entities: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/entity/<entity_type>/<entity_name>', methods=['GET'])
def api_entity_articles(entity_type, entity_name):
    """Get articles for a specific entity."""
    try:
        if entity_type not in ['people', 'orgs']:
            return jsonify({'error': 'Invalid entity type'}), 400
        
        articles = get_entity_articles(entity_name, entity_type)
        return jsonify({'articles': articles})
    except Exception as e:
        logger.error(f"Error getting entity articles: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/categories', methods=['GET'])
def api_categories():
    """Get category breakdown with counts."""
    try:
        categories = get_categories()
        return jsonify({'categories': categories})
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['GET'])
def api_search():
    """Search articles by title or summary."""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'articles': [], 'total': 0})
        
        articles, total = get_articles(page=1, page_size=100, search=query)
        
        return jsonify({
            'articles': articles,
            'total': total
        })
    except Exception as e:
        logger.error(f"Error searching: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'news-dashboard-api'
    })


if __name__ == '__main__':
    logger.info("Starting News Dashboard API server...")
    logger.info("Server will be available at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

