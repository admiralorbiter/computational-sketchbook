import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getStats = () => client.get('/stats');
export const getArticles = (params) => client.get('/articles', { params });
export const getArticle = (id) => client.get(`/articles/${id}`);
export const searchArticles = (query) => client.get('/search', { params: { q: query } });
export const getRelationships = (params) => client.get('/relationships', { params });
export const getNetwork = (params) => client.get('/network', { params });
export const getTimeline = () => client.get('/timeline');
export const getEntities = (type) => client.get(`/entities/${type}`);
export const getEntityArticles = (type, name) => client.get(`/entity/${type}/${encodeURIComponent(name)}`);
export const getCategories = () => client.get('/categories');

export default client;

