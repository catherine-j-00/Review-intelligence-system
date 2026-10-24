import axios from 'axios';

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000' });

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token');
  if (token) config.headers.Authorization = 'Bearer ' + token;
  return config;
});

api.interceptors.response.use((r) => r, (error) => {
  const url = (error.config && error.config.url) || '';
  if (error.response && error.response.status === 401 && !url.includes('/auth/login')) {
    sessionStorage.removeItem('token');
    window.location.replace('/login');
  }
  return Promise.reject(error);
});

const get = (url) => (params = {}) => api.get(url, { params }).then((r) => r.data);

export const login = (username, password) =>
  api.post('/api/auth/login', { username, password }).then((r) => r.data);
export const getOverview = get('/api/analytics/overview');
export const getProductRankings = get('/api/analytics/products');
export const getBrandStats = get('/api/analytics/brands');
export const getMonthly = get('/api/analytics/monthly');
export const getSeasonal = get('/api/analytics/seasonal');
export const getEmotions = get('/api/analytics/emotions');
export const getSentiments = get('/api/analytics/sentiments');
export const getReviews = get('/api/reviews');
export const getBrands = get('/api/brands');
export const getCategories = get('/api/categories');
export const getProducts = get('/api/products');
export const getProductDetail = (id, params = {}) =>
  api.get('/api/analytics/products/' + id, { params }).then((r) => r.data);
export const analyzeReview = (review) =>
  api.post('/api/analyze-review', { review }).then((r) => r.data);
export const createReview = (body) => api.post('/api/reviews', body).then((r) => r.data);
export const uploadCsv = (file, isSample) => {
  const form = new FormData();
  form.append('file', file);
  form.append('is_sample', String(isSample));
  return api.post('/api/reviews/bulk', form).then((r) => r.data);
};
export const askAssistant = (question, history) =>
  api.post('/api/assistant', { question, history }).then((r) => r.data);
