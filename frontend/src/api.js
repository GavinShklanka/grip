import axios from 'axios';

// Static mode: used in production builds (GitHub Pages) where no backend exists.
// In dev mode with the Vite proxy, we talk to the live backend.
const STATIC_MODE = import.meta.env.VITE_STATIC === 'true' ||
                    (import.meta.env.MODE === 'production' && !import.meta.env.VITE_API_URL);

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

/**
 * In static mode, map an API path to a pre-baked JSON file path.
 * e.g. '/state/scores' -> '<base>/api/state/scores.json'
 */
async function staticGet(path) {
  const base = import.meta.env.BASE_URL || '/';
  // Normalize: remove leading slash, replace remaining slashes
  const cleaned = path.replace(/^\//, '');
  const jsonPath = `${base}api/${cleaned}.json`;
  const response = await fetch(jsonPath);
  if (!response.ok) throw new Error(`Static file not found: ${jsonPath}`);
  return response.json();
}

/**
 * For POST endpoints (scenario/run), try to find pre-computed results.
 */
async function staticPost(path, payload) {
  const base = import.meta.env.BASE_URL || '/';

  // Scenario run: match by scenario_id or by override edge signatures
  if (path.includes('scenario/run')) {
    // If we have a scenario_id, try the direct result file
    if (payload?.scenario_id) {
      try {
        const resp = await fetch(`${base}api/scenario/result_${payload.scenario_id}.json`);
        if (resp.ok) return resp.json();
      } catch {}
    }

    // Try matching by override edges
    const overrides = payload?.overrides || [];
    const edgeIds = overrides.map(o => o.edge_id).filter(Boolean).sort().join('_');

    if (edgeIds) {
      try {
        const prebuiltResp = await fetch(`${base}api/scenario/prebuilt.json`);
        if (prebuiltResp.ok) {
          const prebuilt = await prebuiltResp.json();
          const scenarios = prebuilt.scenarios || prebuilt;
          for (const s of scenarios) {
            try {
              const defResp = await fetch(`${base}api/scenario/prebuilt_${s.id}.json`);
              if (!defResp.ok) continue;
              const def = await defResp.json();
              const defEdges = (def.overrides || []).map(o => o.edge_id).filter(Boolean).sort().join('_');
              if (defEdges === edgeIds) {
                const resultResp = await fetch(`${base}api/scenario/result_${s.id}.json`);
                if (resultResp.ok) return resultResp.json();
              }
            } catch {}
          }
        }
      } catch {}
    }

    // Fallback: custom scenario not pre-computed
    return {
      scenario_name: "Custom (not available in static mode)",
      applied_overrides: overrides,
      margins_before: [],
      margins_after: [],
      cascade_results: { cascade_log: [], equilibrium_steps: 0 },
      warnings: ["Custom scenarios require the live backend. Pre-built scenarios are available."]
    };
  }

  // Generic POST fallback
  return { error: "POST endpoints are not available in static mode." };
}

// ── Exported API functions ──────────────────────────────────────

// State endpoints
export const fetchScores = () =>
  STATIC_MODE ? staticGet('state/scores') : api.get('/state/scores').then(r => r.data);

export const fetchCountryScores = (id) =>
  STATIC_MODE ? staticGet(`state/scores_${id}`) : api.get(`/state/scores/${id}`).then(r => r.data);

export const fetchMargins = () =>
  STATIC_MODE ? staticGet('state/margins') : api.get('/state/margins').then(r => r.data);

export const fetchAlerts = () =>
  STATIC_MODE ? staticGet('state/alerts') : api.get('/state/alerts').then(r => r.data);

// Topology
export const fetchTopology = () =>
  STATIC_MODE ? staticGet('topology/graph') : api.get('/topology/graph').then(r => r.data);

export const fetchOutages = () =>
  STATIC_MODE ? staticGet('topology/outages') : api.get('/topology/outages').then(r => r.data);

// Scenarios
export const fetchPrebuiltScenarios = () =>
  STATIC_MODE ? staticGet('scenario/prebuilt') : api.get('/scenario/prebuilt').then(r => r.data);

export const runScenario = (payload) =>
  STATIC_MODE ? staticPost('scenario/run', payload) : api.post('/scenario/run', payload).then(r => r.data);

// Forecast
export const fetchRisk = () =>
  STATIC_MODE ? staticGet('forecast/risk') : api.get('/forecast/risk').then(r => r.data);

export const fetchBacktest = () =>
  STATIC_MODE ? staticGet('forecast/backtest') : api.get('/forecast/backtest').then(r => r.data);

// Meta
export const fetchSystemStatus = () =>
  STATIC_MODE ? staticGet('meta/system-status') : api.get('/meta/system-status').then(r => r.data);

export const fetchAssumptions = () =>
  STATIC_MODE ? staticGet('meta/assumptions') : api.get('/meta/assumptions').then(r => r.data);

export const fetchProvenance = (domain, country) =>
  STATIC_MODE ? staticGet(`meta/provenance_${domain}_${country}`) : api.get(`/meta/provenance/${domain}/${country}`).then(r => r.data);

export default api;
export { STATIC_MODE };
