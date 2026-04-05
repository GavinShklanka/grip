import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// State endpoints
export const fetchScores = () => api.get('/state/scores').then(r => r.data);
export const fetchCountryScores = (id) => api.get(`/state/scores/${id}`).then(r => r.data);
export const fetchMargins = () => api.get('/state/margins').then(r => r.data);
export const fetchAlerts = () => api.get('/state/alerts').then(r => r.data);

// Topology
export const fetchTopology = () => api.get('/topology/graph').then(r => r.data);
export const fetchOutages = () => api.get('/topology/outages').then(r => r.data);

// Scenarios
export const fetchPrebuiltScenarios = () => api.get('/scenario/prebuilt').then(r => r.data);
export const runScenario = (payload) => api.post('/scenario/run', payload).then(r => r.data);

// Forecast
export const fetchRisk = () => api.get('/forecast/risk').then(r => r.data);
export const fetchBacktest = () => api.get('/forecast/backtest').then(r => r.data);

// Meta
export const fetchSystemStatus = () => api.get('/meta/system-status').then(r => r.data);
export const fetchAssumptions = () => api.get('/meta/assumptions').then(r => r.data);
export const fetchProvenance = (domain, country) =>
  api.get(`/meta/provenance/${domain}/${country}`).then(r => r.data);

export default api;
