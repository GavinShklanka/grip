# GRIP — System Architecture Document

## Version 1.0

**Governing document:** grip-source-of-truth.md v1.0  
**Date:** April 2026  
**Role:** This document specifies the target system architecture. All implementation must conform to it. Deviations require updating this document first.

---

# 1. System Purpose

GRIP is a batch-refresh analytical platform that ingests open-source data from eight external sources, computes composite risk indices across eight domains for four Baltic states, simulates infrastructure failure cascades through a physical topology graph, produces a calibrated 30-day disruption-probability estimate, and renders all outputs through a five-view command-room dashboard with full methodological transparency.

The system runs in two modes:

**Demo mode** (`DEMO_MODE=true`): All data served from committed seed files. No external API calls. Full dashboard functional. This is the default for reviewers and portfolio evaluation.

**Live mode** (`DEMO_MODE=false`): Batch ingestion scripts pull fresh data from external APIs on manual trigger or cron schedule. Scores and forecasts recompute. Dashboard reflects updated data with freshness timestamps.

---

# 2. Primary Users and Actors

| Actor | Role | Interaction pattern | Key need |
|---|---|---|---|
| **Gavin (builder/operator)** | Runs ingestion, reviews scores, builds scenarios, validates models | Direct access to all system layers including CLI, API, notebooks, and dashboard | Full analytical transparency and reproducibility |
| **Portfolio reviewer** (hiring manager, faculty) | Evaluates the system as a finished product | Clones repo, runs demo mode, reads notebooks, browses dashboard | Clear setup instructions, working demo, visible methodology, honest limitations |
| **Analytical observer** (policy analyst, infrastructure planner) | Hypothetical end-user persona driving design decisions | Uses dashboard views to assess risk posture and run what-if scenarios | Glanceable situational awareness, drill-down on demand, clear uncertainty communication |

No actor has write access to the system through the UI. All configuration changes happen through JSON files or CLI. The dashboard is read-only with interactive scenario-building as the sole user-driven computation.

---

# 3. Core Workflows

### Workflow 1: Data Refresh (Operator)

```
Trigger: Manual CLI command or cron schedule
1. Operator runs `python -m backend.ingestion.run_all`
2. Each ingestion module (ENTSO-E, ENTSOG, GDELT, ...) fetches data for its configured time window
3. Raw data written to `data/raw/` and loaded into PostgreSQL `indicator_values` table
4. Scoring engine triggered: recomputes all domain scores from current indicator values
5. Risk model triggered: recomputes disruption probability from current feature vector
6. Alert engine triggered: evaluates all thresholds against new scores
7. Dashboard reflects new data on next page load (no push; pull on refresh)
```

**Error path:** If any ingestion module fails, it logs the error and sets a `data_quality_flag = 'stale'` on affected indicators. Scoring continues with available data. Dashboard displays a degraded-data warning for affected domains.

### Workflow 2: Morning Brief (Observer)

```
1. Open dashboard → Global Overview loads automatically
2. Scan four country cards: composite scores, deltas, top-moving domain, N-1 margin status
3. Scan alert feed: any threshold crossings since last session?
4. If alert present → click to drill into Country Detail for the affected country
5. Review domain radar chart and indicator breakdown
6. Decision: investigate further (Scenario Workspace) or close briefing
Total time target: 60–90 seconds for step 2-3, 3–5 minutes if drill-down required
```

### Workflow 3: Scenario Investigation (Analyst)

```
1. Navigate to Scenario Workspace
2. Select pre-built scenario OR build custom scenario by toggling edge states
3. System runs cascade computation: edge removal → capacity recalculation → domain score delta
4. Review side-by-side comparison: current state vs. simulated state
5. Review cascade trace: which edges were affected, in what order, with what magnitude
6. Optionally: modify scenario parameters and re-run
7. Decision: assess preparedness gaps, identify critical dependencies
```

### Workflow 4: Model Validation Review (Reviewer)

```
1. Open Methodology Panel in dashboard OR open notebook 04 directly
2. Review backtest results: for each historical event, did the model elevate risk in prior 30 days?
3. Review calibration plot: when model says X%, how often did disruption occur?
4. Review Brier score vs. naive baseline
5. Review assumptions register: what structural assumptions underpin the system?
6. Review sensitivity explorer: how sensitive are composite scores to weight changes?
7. Judgment: is this system's methodology defensible?
```

---

# 4. Functional Requirements

Each requirement is testable. The ID prefix indicates its category.

### Ingestion (ING)

| ID | Requirement | Acceptance test |
|---|---|---|
| ING-1 | The system ingests hourly cross-border electricity flow data from ENTSO-E for all five major interconnector pairs (FI↔EE, EE↔LV, LV↔LT, SE↔LT, PL↔LT). | Query `indicator_values` for `source='entso_e'` and verify hourly records exist for all five pairs for the most recent complete day. |
| ING-2 | The system ingests daily gas flow data from ENTSOG for Balticconnector, GIPL, Klaipėda LNG, and Inčukalns UGS. | Query `indicator_values` for `source='entsog'` and verify daily records for all four assets. |
| ING-3 | The system ingests weekly GDELT event counts and average tone for Baltic + Russia actor filters via BigQuery or DOC API. | Query `indicator_values` for `source='gdelt'` and verify weekly aggregated records. |
| ING-4 | The system ingests daily sanctions entity counts from OpenSanctions. | Query `indicator_values` for `source='opensanctions'` and verify daily count record. |
| ING-5 | The system ingests monthly trade volume data from Eurostat COMEXT for HS 27xx (mineral fuels) for all four focus countries. | Query `indicator_values` for `source='eurostat'` and verify monthly records. |
| ING-6 | Each ingestion module operates independently. Failure of one module does not prevent others from completing. | Kill the GDELT ingestion mid-run. Verify ENTSO-E and ENTSOG ingestion complete normally. |
| ING-7 | In demo mode, no external API calls are made. All data is served from `data/seed/`. | Run with `DEMO_MODE=true`, disconnect network, verify system starts and all endpoints return data. |

### Scoring (SCR)

| ID | Requirement | Acceptance test |
|---|---|---|
| SCR-1 | The system computes a 0–100 domain score for each of the eight domains for each of the four focus countries. | Query `domain_scores` and verify 32 records (8 domains × 4 countries) exist for the most recent scoring run. |
| SCR-2 | Domain scores are computed from indicator values using weights defined in `config/domains.json`. | Change a weight in the config file, re-run scoring, verify the output changes proportionally. |
| SCR-3 | The system computes the N-1 capacity margin for each focus country as: (total available import capacity − current demand − reserve requirement). | For Estonia during a simulated Estlink 2 outage, verify margin drops by approximately 650 MW. |
| SCR-4 | The system flags anomalies when any domain score exceeds 2 standard deviations from its 30-day rolling mean. | Inject an artificially high indicator value, re-run scoring, verify anomaly flag is set. |
| SCR-5 | Each domain score record includes a `data_coverage` field (0.0–1.0) indicating what fraction of the domain's indicators have current (non-stale) data. | Set one indicator to `stale`, verify `data_coverage` for its domain drops below 1.0. |

### Simulation (SIM)

| ID | Requirement | Acceptance test |
|---|---|---|
| SIM-1 | The system loads the infrastructure topology from `config/topology.json` as a directed graph with nodes (countries, interconnectors, facilities) and edges (connections with capacity attributes). | Load topology, verify node count matches config, verify all edge capacities are positive numbers. |
| SIM-2 | The system supports edge-state overrides: an edge can be set to `active`, `degraded` (with reduced capacity), or `offline` (zero capacity). | Set Estlink 2 to `offline`, verify its capacity is treated as 0 in all downstream calculations. |
| SIM-3 | The cascade engine recalculates available import capacity for each country after edge-state overrides are applied. | Remove Estlink 2, verify Estonia's available import capacity decreases by 650 MW. Remove Balticconnector, verify Finland-Estonia gas flow capacity drops to zero. |
| SIM-4 | The system supports pre-built scenarios loaded from `config/scenarios/*.json`. | Load `estlink2_severance.json`, verify overrides are applied correctly and cascade produces non-zero deltas. |
| SIM-5 | The system supports custom scenarios defined via API request (arbitrary combination of edge-state overrides). | POST a custom scenario removing both Estlink 1 and Estlink 2 simultaneously. Verify cascade computes Estonia's total FI import capacity as 0 MW. |
| SIM-6 | The comparator produces a delta output: for each country and domain, the difference between current state and simulated state. | Run any scenario, verify response contains `current_state` and `simulated_state` objects with matching keys and numeric differences. |

### Forecasting (FCT)

| ID | Requirement | Acceptance test |
|---|---|---|
| FCT-1 | The risk model produces P(any critical interconnector disruption within 30 days) as a float between 0.0 and 1.0. | Call `/api/forecast/risk`, verify response contains `probability` field with value in [0, 1]. |
| FCT-2 | The risk model output includes 80% and 95% confidence intervals. | Verify response contains `ci_lower_80`, `ci_upper_80`, `ci_lower_95`, `ci_upper_95`. |
| FCT-3 | The risk model output includes a `model_confidence` field with value `good`, `moderate`, or `poor` based on feature completeness and historical calibration quality. | When multiple indicators are stale, verify `model_confidence` degrades from `good` to `moderate` or `poor`. |
| FCT-4 | Rule-based alerts fire independently of the statistical model. Rules include: N-1 margin violation, 2+ interconnectors offline simultaneously, domain score exceeding critical threshold. | Simulate N-1 violation via scenario, verify alert is generated regardless of model probability. |
| FCT-5 | The backtest harness performs leave-one-out cross-validation across the six interconnector disruption events. | Run backtest, verify six iterations execute and produce per-event risk scores and a global Brier score. |

### API (API)

| ID | Requirement | Acceptance test |
|---|---|---|
| API-1 | `GET /api/state/scores` returns current domain scores for all countries. | Response is JSON array with 32+ records, each containing `country_id`, `domain_id`, `score`, `velocity`, `data_coverage`, `anomaly_flag`. |
| API-2 | `GET /api/state/margins` returns current N-1 capacity margins for all focus countries. | Response contains four records with `country_id`, `margin_mw`, `status` (green/amber/red). |
| API-3 | `GET /api/topology/graph` returns the full infrastructure graph as nodes and edges with current states. | Response is JSON with `nodes` array and `edges` array, each edge containing `capacity`, `current_flow`, `status`. |
| API-4 | `POST /api/scenario/run` accepts edge-state overrides and returns full simulated state with deltas. | POST with `{"overrides": [{"edge_id": "estlink_2", "status": "offline"}]}` returns `current_state`, `simulated_state`, `cascade_trace`. |
| API-5 | `GET /api/forecast/risk` returns current disruption probability with confidence intervals and model confidence. | Response matches FCT-1, FCT-2, FCT-3 requirements. |
| API-6 | `GET /api/meta/assumptions` returns the full assumptions register as structured JSON. | Response is array of objects with `id`, `statement`, `sensitivity`, `status`, `test_plan`. |
| API-7 | `GET /api/meta/provenance/{domain_id}/{country_id}` returns the full calculation trace for a domain score. | Response includes list of indicators with `name`, `raw_value`, `normalized_value`, `weight`, `source`, `timestamp`, `quality_flag`. |
| API-8 | All API endpoints return valid JSON with consistent error format on failure. | Send request with invalid country_id, verify 404 response with `{"error": "...", "detail": "..."}` structure. |

### Dashboard (DSH)

| ID | Requirement | Acceptance test |
|---|---|---|
| DSH-1 | The Global Overview displays four country cards ranked by composite escalation risk score. | Open dashboard. Four cards visible. Highest-risk country appears first. |
| DSH-2 | Each country card shows: composite score (number), 30-day sparkline, top-moving domain name, N-1 margin status indicator (green/amber/red). | Visual inspection of all four cards. |
| DSH-3 | The Infrastructure Topology view renders the physical network as a diagram with nodes and edges colored by status. | All 12+ edges visible. Active edges are distinct from offline edges. |
| DSH-4 | The Scenario Workspace allows selecting a pre-built scenario or manually toggling edge states, and displays the cascade result as a side-by-side comparison. | Select "Estlink 2 Severance", verify simulated state differs from current state. Toggle a custom edge, verify re-computation. |
| DSH-5 | The Methodology Panel displays the assumptions register, backtest results (Brier score, calibration plot), and sensitivity explorer. | Visual inspection. Assumptions are scrollable. Calibration plot renders. Sensitivity sliders adjust scores. |
| DSH-6 | Every displayed numeric value traces to an API endpoint. No frontend-computed analytics. | The frontend performs no score calculations, no normalization, no model inference. All analytics come from the API. |

---

# 5. Non-Functional Requirements

| ID | Category | Requirement | Measurement | Target |
|---|---|---|---|---|
| NFR-1 | **Performance** | API response time for state and topology endpoints | Measured at server, p95 | < 500ms |
| NFR-2 | **Performance** | Scenario cascade computation time | Measured at server, single scenario | < 2 seconds |
| NFR-3 | **Performance** | Full scoring recomputation time (all domains, all countries) | Measured end-to-end | < 30 seconds |
| NFR-4 | **Availability** | Demo mode functions with no network access | Test with network disabled | 100% feature coverage in demo mode |
| NFR-5 | **Reproducibility** | Given the same seed data and config files, the system produces identical scores | Run scoring twice on same data | Bit-identical output |
| NFR-6 | **Maintainability** | Adding a new indicator to an existing domain requires editing only `config/domains.json` and adding one ingestion function | Measure by executing the change | No modifications to scoring engine code |
| NFR-7 | **Maintainability** | Adding a new interconnector requires editing only `config/topology.json` | Measure by executing the change | No modifications to cascade engine code |
| NFR-8 | **Testability** | Backend test suite runs in < 60 seconds | `time pytest` | < 60s wall clock |
| NFR-9 | **Data freshness** | Every displayed value shows its data timestamp | Visual inspection of all dashboard panels | No undated values |
| NFR-10 | **Documentation** | README enables a cold-start reviewer to run the system in < 15 minutes | Time a first-run walkthrough | Clone → running dashboard in ≤ 15 min |

---

# 6. Logical Architecture

The system has five layers. Data flows strictly downward. No layer calls upward.

```
┌─────────────────────────────────────────────────────┐
│                PRESENTATION LAYER                    │
│         React dashboard (5 views)                    │
│         Reads from API only. No direct DB access.    │
│         No analytics computation.                    │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP/JSON
┌──────────────────────▼──────────────────────────────┐
│                   API LAYER                          │
│         FastAPI routes (4 groups)                     │
│         Validates requests. Serializes responses.    │
│         Delegates all computation to engines below.  │
└──────────┬───────────┬──────────┬───────────────────┘
           │           │          │
┌──────────▼──┐ ┌──────▼─────┐ ┌──▼──────────────────┐
│  SCORING    │ │ SIMULATION │ │ FORECASTING          │
│  ENGINE     │ │ ENGINE     │ │ ENGINE               │
│             │ │            │ │                      │
│ - Domain    │ │ - Topology │ │ - Feature eng.       │
│   composite │ │   graph    │ │ - Risk model (LogReg)│
│ - N-1 calc  │ │ - Cascade  │ │ - Alert rules        │
│ - Anomaly   │ │ - Override │ │ - Calibration        │
│   detection │ │ - Compare  │ │ - Backtest harness   │
└──────┬──────┘ └──────┬─────┘ └──────┬───────────────┘
       │               │              │
┌──────▼───────────────▼──────────────▼───────────────┐
│                  DATA LAYER                          │
│         PostgreSQL (indicator_values,                │
│           domain_scores, forecasts, alerts)          │
│         JSON configs (domains, topology,             │
│           thresholds, scenarios)                     │
│         Seed files (CSV/JSON in data/seed/)          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               INGESTION LAYER                        │
│         Per-source Python modules                    │
│         Batch execution (CLI or cron)                │
│         Writes to data/raw/ and PostgreSQL           │
│         Each module independent and substitutable    │
└─────────────────────────────────────────────────────┘
```

### Architecture Decision: Strict Layered (No Bypass)

**Rationale:** The dashboard must never compute analytics. The API must never access external APIs directly. The scoring engine must never know about the database schema (it receives dataframes, not connections). Each boundary is a testability boundary — you can unit-test any engine without standing up layers above or below it.

**Tradeoff:** Slightly more boilerplate (data transformation at layer boundaries). Accepted because testability and auditability matter more than code brevity for a portfolio project.

**Dependency impact:** If the database schema changes, only the data layer adapts. Engines and API remain unchanged.

**Implementation consequence:** Each engine module exposes pure functions that accept dataframes/dicts and return dataframes/dicts. No SQLAlchemy imports in engine modules.

---

# 7. Component Map

### Ingestion Layer (7 modules)

| Component | External source | Output table | Cadence | Failure mode |
|---|---|---|---|---|
| `ingestion/entso_e.py` | ENTSO-E Transparency Platform | `indicator_values` (hourly electricity flows, forced outages) | Hourly | Flag stale, continue |
| `ingestion/entsog.py` | ENTSOG Transparency Platform | `indicator_values` (daily gas flows) | Daily | Flag stale, continue |
| `ingestion/gdelt.py` | GDELT via BigQuery or DOC API | `indicator_values` (weekly event counts, tone) | Weekly | Flag stale, continue |
| `ingestion/opensanctions.py` | OpenSanctions API | `indicator_values` (daily entity counts) | Daily | Flag stale, continue |
| `ingestion/eurostat.py` | Eurostat COMEXT SDMX API | `indicator_values` (monthly trade volumes) | Monthly | Flag stale, continue |
| `ingestion/copernicus.py` | Copernicus CDS (ERA5) | `indicator_values` (weather: wind, wave, ice) | Daily | Flag stale, continue |
| `ingestion/static.py` | Manual CSV refresh (SIPRI, alliance data) | `indicator_values` (annual defense spending, exercise counts) | Manual | N/A (seed data always available) |

**Architecture Decision: One module per source, common interface**

**Rationale:** Principle P3 (isolated, substitutable). Each module implements `fetch(date_range) → DataFrame` and `load(df, db_session) → None`. The runner iterates modules and catches exceptions per-module.

**Tradeoff:** Some code duplication in boilerplate (HTTP setup, error handling). Accepted for isolation benefit.

**Dependency impact:** Adding a new source = adding one new file. No existing file is modified.

**Implementation consequence:** The runner module (`ingestion/run_all.py`) uses dynamic import or explicit registration — not hardcoded function calls.

### Scoring Engine (4 components)

| Component | Input | Output | Logic |
|---|---|---|---|
| `scoring/domain_index.py` | `indicator_values` (filtered by domain), `config/domains.json` | `domain_scores` records | For each country, for each domain: normalize indicators → apply weights → sum → clip to [0, 100]. Store score, velocity (7-day Δ), data_coverage. |
| `scoring/n1_margin.py` | `indicator_values` (electricity flows), `config/topology.json` | `margins` records per country | Sum available import capacity across active interconnectors → subtract current consumption → subtract reserve requirement (~1500 MW for Baltics) → report margin. |
| `scoring/escalation_composite.py` | `domain_scores` for domains 1–8 | `domain_scores` for domain 9 (`escalation_risk`) | Weighted average of domain scores 1–8 with velocity multiplier: `composite = Σ(w_i × score_i × (1 + α × velocity_i))` where α is a configurable momentum factor. |
| `scoring/anomaly.py` | `domain_scores` (30-day history) | `anomaly_flag` boolean per score | Z-score against 30-day rolling mean. Flag if |z| > 2.0. |

**Architecture Decision: Scoring reads config at runtime, not at import**

**Rationale:** Principle P1 (configuration over code). Weights live in JSON. Changing weights does not require restarting the server — the scoring engine re-reads config on each computation cycle.

**Tradeoff:** Slightly slower (file I/O on each run). Negligible at this data scale.

**Dependency impact:** Config format is a contract. If `domains.json` schema changes, `domain_index.py` must adapt.

**Implementation consequence:** Define a `DomainConfig` Pydantic model to validate config on load. Fail fast with a clear error if config is malformed.

### Simulation Engine (4 components)

| Component | Input | Output | Logic |
|---|---|---|---|
| `simulation/topology.py` | `config/topology.json` | NetworkX DiGraph instance | Parse JSON into graph. Nodes carry `type`, `capacity`, `demand` attributes. Edges carry `capacity_mw` (or `capacity_mcm`), `status`, `type`. |
| `simulation/cascade.py` | Graph + edge overrides | Per-country capacity deltas | Apply overrides (set edge statuses). For each country: sum inbound edge capacities where status=active → subtract demand → subtract reserve → report margin. Compute delta vs. baseline. |
| `simulation/scenario_engine.py` | Scenario definition (JSON) | Full simulated state | Load scenario → apply overrides to graph copy → run cascade → recompute domain scores with new infrastructure state → return complete state object. |
| `simulation/comparator.py` | Current state + simulated state | Delta report + cascade trace | Diff every score. Produce cascade trace: ordered list of `{edge_id, override_applied, countries_affected, margin_change}`. |

**Architecture Decision: Cascade is deterministic capacity arithmetic, not stochastic simulation**

**Rationale:** The topology is physical infrastructure with known capacities. Capacity subtraction after edge removal is an engineering fact, not a statistical estimate. This makes the output explainable, reproducible, and verifiable against historical events.

**Tradeoff:** Does not model second-order effects (price response, demand elasticity, frequency instability). Accepted because GRIP is a risk platform, not a power-flow simulator. The limitation is documented.

**Dependency impact:** The cascade engine depends only on the topology JSON and the concept of "capacity." It is agnostic to energy type (electricity or gas). Both are handled by the same arithmetic.

**Implementation consequence:** The cascade function signature is `cascade(graph: nx.DiGraph, overrides: List[Override]) → Dict[str, CountryMargin]`. Pure function. No side effects. Trivially testable.

### Forecasting Engine (5 components)

| Component | Input | Output | Logic |
|---|---|---|---|
| `forecasting/features.py` | `indicator_values`, `domain_scores`, `topology` (current outage count) | Feature matrix (one row per day) | Construct daily feature vector: GDELT event intensity, weather severity, active outage count, days since last disruption, sanctions pressure score, domain velocities, seasonal indicators (month, winter flag). |
| `forecasting/risk_model.py` | Feature matrix, event labels | Calibrated probability | Logistic regression trained on full historical window with binary labels (disruption within 30 days = 1). Outputs P(disruption) via `predict_proba`. Confidence intervals via bootstrap (1000 resamples). |
| `forecasting/alert_rules.py` | Current scores, margins, topology state | List of active alerts | Deterministic rules: N-1 violation, 2+ interconnectors offline, domain score > critical threshold, risk probability > alert threshold. Each rule produces an alert with severity, explanation, and timestamp. |
| `forecasting/calibration.py` | Historical predictions vs. outcomes | Brier score, reliability diagram data | Bin predictions into deciles, compute observed frequency per bin, compute Brier score. Return structured data for visualization. |
| `forecasting/backtest.py` | Full historical data, event register | Per-event validation results | Leave-one-out: for each of 6 events, retrain on remaining 5, generate daily risk scores for the held-out period. Report: did model elevate risk in 30 days prior? What was peak probability? |

**Architecture Decision: Logistic regression, not gradient boosting**

**Rationale:** Six positive events. Gradient boosting will overfit. Logistic regression is interpretable (feature coefficients are directly readable), calibratable (output is already a probability), and appropriate for the sample size. Feature importance is transparent.

**Tradeoff:** Lower potential accuracy ceiling. Accepted because an honest, interpretable model that a reviewer can interrogate beats a black-box model that might perform slightly better on a 6-event dataset.

**Dependency impact:** If more events accumulate over time, a future upgrade to GBM or random forest is straightforward — the feature engineering pipeline is model-agnostic.

**Implementation consequence:** Use `sklearn.linear_model.LogisticRegression` with `C=1.0` (regularized). Bootstrap CIs via `sklearn.utils.resample`. No neural networks, no deep learning, no overengineering.

### API Layer (4 route groups)

| Route group | Base path | Methods | Source engine |
|---|---|---|---|
| State | `/api/state/` | GET scores, margins, flows, alerts | Scoring engine |
| Topology | `/api/topology/` | GET graph, outages | Simulation engine (topology) |
| Scenario | `/api/scenario/` | POST run, GET prebuilt, GET compare | Simulation engine (full) |
| Forecast | `/api/forecast/` | GET risk, GET backtest | Forecasting engine |
| Meta | `/api/meta/` | GET assumptions, provenance, data-quality, methodology | All engines (read-only metadata) |

**Architecture Decision: All computation happens in engines, not in routes**

**Rationale:** Route handlers are thin: validate input → call engine function → serialize output. This means engines are testable without HTTP and the API is testable without engines (mock injection).

**Tradeoff:** Requires explicit data-transfer objects between API and engines. Minor overhead.

**Implementation consequence:** Define Pydantic response models for every endpoint. FastAPI auto-generates OpenAPI docs, which doubles as API documentation for reviewers.

### Presentation Layer (5 views)

| View | API dependencies | Key components |
|---|---|---|
| Global Overview | `/api/state/scores`, `/api/state/margins`, `/api/state/alerts` | Country cards, alert feed, system status bar |
| Infrastructure Topology | `/api/topology/graph` | SVG/React network diagram, edge status colors, click-to-inspect |
| Country Detail | `/api/state/scores/{country}`, `/api/meta/provenance/{domain}/{country}` | Radar chart, sparklines, indicator breakdown table |
| Scenario Workspace | `/api/scenario/prebuilt`, `POST /api/scenario/run` | Scenario selector, edge toggles, side-by-side comparison, cascade trace |
| Methodology & Risk | `/api/forecast/risk`, `/api/forecast/backtest`, `/api/meta/assumptions` | Risk gauge, calibration plot, assumptions register, sensitivity sliders |

**Architecture Decision: Frontend performs zero analytics**

**Rationale:** Principle DSH-6. Every number on screen comes from the API. The frontend does layout, color mapping, and interaction handling — never normalization, scoring, or model inference. This ensures the API is the single source of analytical truth, and the dashboard can be replaced without affecting analytical integrity.

**Tradeoff:** More API calls. Accepted — the data volumes are tiny (dozens of records, not thousands).

**Implementation consequence:** Use React Query (TanStack Query) for data fetching with 60-second stale time in live mode, infinite stale time in demo mode. No local state caching of analytical results.

---

# 8. Data Flow

### Batch Refresh Pipeline

```
External APIs                    Data Layer                     Engines
─────────────                    ──────────                     ───────

ENTSO-E ──fetch──► raw CSV ──► indicator_values ─┐
ENTSOG  ──fetch──► raw CSV ──► indicator_values  │
GDELT   ──fetch──► raw CSV ──► indicator_values  ├──► Scoring ──► domain_scores
OpenSanc ─fetch──► raw JSON ─► indicator_values  │                    │
Eurostat ─fetch──► raw CSV ──► indicator_values  │                    │
Copern.  ─fetch──► raw GRIB ─► indicator_values ─┘                    │
                                                                      │
                    config/topology.json ──────────► Simulation        │
                                                   (on-demand only)   │
                                                                      │
                    domain_scores + indicator_values ──► Forecasting ──► forecasts
                                                                           │
                    forecasts + domain_scores + margins ──► Alerts ────► alerts
```

### Request-Time Data Flow (API Call)

```
Browser                   FastAPI                  Engine               DB / Config
───────                   ───────                  ──────               ──────────

GET /api/state/scores
  ──────────────────►  route_handler
                         │
                         ├──► scoring.get_current_scores()
                         │         │
                         │         ├──► SELECT FROM domain_scores ◄── PostgreSQL
                         │         │    WHERE timestamp = latest
                         │         │
                         │         └──► return DataFrame
                         │
                         └──► serialize to JSON
  ◄──────────────────  200 OK + JSON


POST /api/scenario/run
  ──────────────────►  route_handler
                         │
                         ├──► validate overrides (Pydantic)
                         │
                         ├──► simulation.run_scenario(overrides)
                         │         │
                         │         ├──► topology.load_graph() ◄── config/topology.json
                         │         ├──► cascade.compute(graph, overrides)
                         │         ├──► comparator.diff(current, simulated)
                         │         │
                         │         └──► return ScenarioResult
                         │
                         └──► serialize to JSON
  ◄──────────────────  200 OK + JSON
```

---

# 9. State Transitions

### Interconnector Status States

```
          repair_complete            degradation_detected
  ┌──────────────────────────┐    ┌──────────────────────┐
  │                          │    │                      │
  ▼                          │    ▼                      │
ACTIVE ──────disruption──────► OFFLINE ◄──total_failure── DEGRADED
  ▲                                │                      ▲
  │                                │                      │
  └────────repair_complete─────────┘    partial_restore───┘
```

Each interconnector in `config/topology.json` has a `status` field: `active`, `degraded`, or `offline`. Status changes are either:
- **Observed** (from ENTSO-E outage data during ingestion) → updates `topology_state` table.
- **Simulated** (from scenario overrides) → applied to in-memory graph copy only; never persists.

### Alert Lifecycle

```
INACTIVE ──threshold_crossed──► ACTIVE ──acknowledged──► ACKNOWLEDGED ──resolved──► INACTIVE
                                  │                                                    ▲
                                  └──────────────auto_resolve (condition clears)────────┘
```

For MVP, alerts do not persist across sessions. They are recomputed on each scoring cycle. The "acknowledged" state is frontend-only (local state). This is acceptable for a single-user portfolio project.

### Scoring Cycle States

```
IDLE ──trigger──► INGESTING ──complete──► SCORING ──complete──► FORECASTING ──complete──► IDLE
                      │                      │                       │
                      ▼                      ▼                       ▼
                 (partial failure:       (always succeeds         (model error:
                  flag stale data)        with available data)     use last forecast)
```

---

# 10. External Integrations

| Integration | Protocol | Authentication | Rate limit | Failure handling |
|---|---|---|---|---|
| ENTSO-E | REST (XML) via `entsoe-py` | Email-registered API key (expires every 183 days) | ~400 requests/day (undocumented soft limit) | Retry 3× with exponential backoff. On persistent failure, flag stale. |
| ENTSOG | REST (CSV/XML) via `entsog-py` | None required | ~100 rows default (use `limit=-1`) | Retry 3×. On failure, flag stale. |
| GDELT | BigQuery SQL or DOC API (REST) | Google service account (BigQuery) or none (DOC API) | 1 TB/month (BigQuery free tier); DOC API has undocumented rate limit | Use DOC API as fallback if BigQuery quota exceeded. |
| OpenSanctions | REST (JSON) | None for public data | Undocumented; requests appear unlimited for reasonable use | Retry 3×. On failure, use last cached count. |
| Eurostat | SDMX REST | None | Undocumented; generous for programmatic access | Retry 3×. Monthly data; staleness is inherent. |
| Copernicus CDS | Python `cdsapi` | Registered API key | Queue-based; requests may take minutes to hours | Submit request, poll for completion, timeout after 30 minutes. Flag stale on timeout. |

**Architecture Decision: No external calls at request time**

**Rationale:** All external data is fetched during batch ingestion and stored locally. API endpoints serve only from the database. This eliminates external dependency from the user-facing request path, ensures consistent response times, and makes demo mode possible.

**Tradeoff:** Data is always at least one ingestion cycle old. Accepted — the fastest-updating source (ENTSO-E) is hourly, and the dashboard is not real-time.

**Dependency impact:** If any external API changes its schema or authentication, only the corresponding ingestion module needs updating. No other system component is affected.

---

# 11. Governance and Controls

### Configuration governance

All scoring weights, thresholds, topology definitions, and scenario parameters live in version-controlled JSON files. Any change to these files is a git commit with a message explaining the rationale. The `docs/assumptions-register.md` must be updated when weights or thresholds change.

### Model governance

The risk model is trained by a notebook (`04_disruption_backtest.ipynb`), not by a production pipeline. The trained model is serialized to `data/models/risk_model.joblib`. Retraining requires explicitly running the notebook and committing the new model file. There is no automated retraining.

**Rationale:** With 6 positive events, automated retraining is dangerous — a single mislabeled event could destabilize the model. Manual, auditable retraining is appropriate for this sample size.

### Claim governance

The system enforces claim boundaries at the API level:
- Scenario endpoints never return a `probability` field. They return `simulated_state` and `delta`.
- Forecast endpoints always return `confidence_intervals` alongside `probability`.
- The `/api/meta/methodology` endpoint returns the full claim-boundaries statement.

---

# 12. Error and Failure Handling

| Failure | Detection | Response | User impact |
|---|---|---|---|
| **Ingestion module fails** | Exception caught by runner | Log error. Set `data_quality_flag='stale'` on affected indicators. Continue with other modules. | Domain scores using stale indicators display reduced `data_coverage`. Dashboard shows amber data-quality indicator. |
| **Database connection lost** | SQLAlchemy exception on query | API returns 503 with `{"error": "database_unavailable"}`. | Dashboard shows "System unavailable" overlay. Demo mode is unaffected (seed data loaded at startup). |
| **Config file malformed** | Pydantic validation on load | Application refuses to start. Logs specific validation error with line number. | Operator must fix config before system starts. Fail-fast, not fail-silent. |
| **Scenario produces impossible state** (negative capacity, score > 100) | Assertion checks in cascade engine | Clip values to valid ranges. Log warning. Return result with `warnings` array in response. | Dashboard displays result with a "constrained output" indicator. |
| **Risk model returns NaN or error** | Exception in `predict_proba` | Return last valid forecast with `model_confidence='poor'` and `stale=true`. Log error. | Risk panel shows last valid score with "stale" indicator. Alert rules still function independently. |
| **Frontend cannot reach API** | Fetch error / timeout | Display "Connection lost" banner. Retain last-loaded data in local state. Retry on 30-second interval. | Dashboard remains viewable with stale data. No blank screens. |

**Architecture Decision: Degrade gracefully, never crash silently**

**Rationale:** A blank screen or an unexplained error destroys reviewer confidence. A degraded-but-explained state demonstrates engineering maturity.

**Implementation consequence:** Every API endpoint wraps its engine call in a try/except that returns a structured error response. The frontend has a global error boundary that shows a human-readable message, not a stack trace.

---

# 13. Observability, Logging, and Metrics

### Logging

| Layer | Logger | Level | Content |
|---|---|---|---|
| Ingestion | `grip.ingestion.{source}` | INFO on success, WARNING on partial failure, ERROR on total failure | Source, record count fetched, time elapsed, any staleness flags set |
| Scoring | `grip.scoring` | INFO per scoring cycle | Countries scored, domains scored, anomalies flagged, total time |
| Simulation | `grip.simulation` | INFO per scenario run | Scenario ID, overrides applied, cascade steps, computation time |
| Forecasting | `grip.forecasting` | INFO per risk computation | Features used, probability output, confidence level, any feature staleness |
| API | `grip.api` | INFO per request | Endpoint, method, status code, response time |

All logs go to stdout (structured JSON format). In Railway deployment, this is captured automatically. No file-based logging for MVP.

### Metrics (lightweight, no external tooling)

The `/api/meta/system-status` endpoint returns:

```json
{
  "last_ingestion": "2026-04-03T08:00:00Z",
  "indicators_total": 52,
  "indicators_current": 48,
  "indicators_stale": 4,
  "scoring_last_run": "2026-04-03T08:01:12Z",
  "risk_model_last_run": "2026-04-03T08:01:15Z",
  "risk_model_confidence": "good",
  "alerts_active": 1,
  "demo_mode": false
}
```

The dashboard top bar renders this as a system health indicator.

**Architecture Decision: No Prometheus, no Grafana, no external monitoring**

**Rationale:** External monitoring infrastructure is engineering overhead with zero portfolio value. Structured logging + a status endpoint is sufficient for a single-operator system. A reviewer seeing a clean status endpoint is more impressed than a reviewer seeing a Grafana dashboard for a system with one user.

**Tradeoff:** No historical performance metrics. Accepted for MVP.

---

# 14. Security, Privacy, and Trust

### API keys

API keys for external services (ENTSO-E, GDELT BigQuery, Copernicus) are stored in `.env` (gitignored) and loaded via `python-dotenv`. The `.env.example` file lists required keys with placeholder values and registration URLs.

**No API key is ever committed to the repository.**

### Data sensitivity

All data in GRIP is derived from public, open-source APIs. No personal data, no classified information, no proprietary datasets. The system processes aggregate national-level statistics and infrastructure status data. GDPR and privacy regulations are not applicable.

### Trust model

GRIP makes analytical claims. The trust architecture ensures those claims are verifiable:
- Every score traces to indicators, sources, and timestamps (Principle P6).
- Every forecast carries confidence intervals and model-performance metrics (Constraint N6).
- Every assumption is documented and sensitivity-rated (Principle P9).
- The backtest notebook is reproducible end-to-end (Principle P8).

A reviewer does not need to trust the builder. They need to follow the audit trail.

### Deployment security

Railway deployment uses HTTPS by default. No custom authentication is implemented — the dashboard is publicly accessible. This is acceptable because all data is public and the system is read-only (no user-generated data, no write endpoints except scenario computation which is stateless).

---

# 15. Scalability and Maintainability

### What scales without architectural change

| Change | Affected component | Effort |
|---|---|---|
| Add new indicator to existing domain | `config/domains.json` + one ingestion function | < 1 hour |
| Add new interconnector (e.g., Harmony Link in 2029) | `config/topology.json` | < 30 minutes |
| Add new pre-built scenario | `config/scenarios/new_scenario.json` | < 30 minutes |
| Update scoring weights based on sensitivity analysis | `config/domains.json` | < 10 minutes |
| Swap risk model (logistic regression → GBM) | `forecasting/risk_model.py` only | 1–2 hours |

### What requires architectural change

| Change | Why | Estimated effort |
|---|---|---|
| Add a second region | New ingestion modules, new topology graph, new calibration, new domain weights. Approximately 60% of the original build effort per region. | 2–3 weeks |
| Add live streaming (websockets) | Requires event-driven ingestion, push architecture for frontend, and fundamentally different data-freshness model. | 1–2 weeks + testing |
| Add user authentication | Requires auth middleware, session management, possibly a user database. | 1 week |
| Add automated scheduled ingestion in production | Requires task scheduler (Celery, APScheduler, or Railway cron), failure alerting, and retry infrastructure. | 3–5 days |

### Code maintainability signals for reviewers

- **Type hints throughout.** All function signatures carry type annotations. Pydantic models enforce runtime validation.
- **No circular imports.** The layered architecture prevents upward dependencies.
- **Config-driven behavior.** Analytical parameters are never magic numbers in code.
- **Test coverage on core logic.** Scoring, cascade, and risk model have unit tests. API has integration tests.

---

# 16. Recommended Folder and Module Structure

This is the canonical structure. It supersedes the Execution Plan's repo tree where they differ (differences are minor: this version adds Pydantic schemas, the model artifact directory, and clarifies the ingestion runner).

```
grip/
├── README.md
├── LICENSE
├── pyproject.toml
├── .env.example
├── .gitignore
├── docker-compose.yml
│
├── config/
│   ├── domains.json              # Domain definitions, indicator mappings, weights
│   ├── topology.json             # Infrastructure graph: nodes, edges, capacities
│   ├── thresholds.json           # Alert thresholds per domain and for risk score
│   └── scenarios/
│       ├── estlink2_severance.json
│       ├── balticconnector_damage.json
│       ├── multi_cable_attack.json
│       ├── lng_supply_shock.json
│       ├── sanctions_escalation.json
│       └── litpol_failure.json
│
├── data/
│   ├── seed/                     # Committed demo data
│   │   ├── entso_e_flows.csv
│   │   ├── entsog_flows.csv
│   │   ├── gdelt_events.csv
│   │   ├── sanctions_counts.csv
│   │   ├── trade_volumes.csv
│   │   ├── weather_conditions.csv
│   │   ├── disruption_events.json
│   │   └── static_indicators.csv
│   ├── models/                   # Serialized trained models (committed)
│   │   └── risk_model.joblib
│   ├── raw/                      # Downloaded data (gitignored)
│   └── processed/                # Cleaned data (gitignored)
│
├── docs/
│   ├── methodology.md
│   ├── data-dictionary.md
│   ├── infrastructure-topology.md
│   ├── backtesting-report.md
│   ├── limitations.md
│   └── assumptions-register.md
│
├── backend/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app, CORS, lifespan events
│   ├── config.py                 # Settings via pydantic-settings (loads .env)
│   ├── schemas/                  # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── state.py              # ScoreResponse, MarginResponse, AlertResponse
│   │   ├── topology.py           # GraphResponse, NodeResponse, EdgeResponse
│   │   ├── scenario.py           # ScenarioRequest, ScenarioResponse, CascadeTrace
│   │   ├── forecast.py           # RiskResponse, BacktestResponse, CalibrationResponse
│   │   └── meta.py               # AssumptionResponse, ProvenanceResponse, SystemStatus
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py             # SQLAlchemy ORM models
│   │   ├── session.py            # Engine, session factory, get_db dependency
│   │   └── seed.py               # Load seed data into DB for demo mode
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract IngestionModule interface
│   │   ├── runner.py             # Orchestrates all modules, handles failures
│   │   ├── entso_e.py
│   │   ├── entsog.py
│   │   ├── gdelt.py
│   │   ├── opensanctions.py
│   │   ├── eurostat.py
│   │   ├── copernicus.py
│   │   └── static.py
│   ├── scoring/
│   │   ├── __init__.py
│   │   ├── domain_index.py       # Per-domain composite scoring
│   │   ├── n1_margin.py          # Grid capacity margin calculation
│   │   ├── escalation_composite.py
│   │   └── anomaly.py
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── topology.py           # Load and manage NetworkX graph
│   │   ├── cascade.py            # Edge removal → capacity recalculation
│   │   ├── scenario_engine.py    # Apply overrides, run cascade, return result
│   │   └── comparator.py         # Diff current vs. simulated state
│   ├── forecasting/
│   │   ├── __init__.py
│   │   ├── features.py           # Feature engineering pipeline
│   │   ├── risk_model.py         # Logistic regression inference + bootstrap CIs
│   │   ├── alert_rules.py        # Deterministic alert triggers
│   │   ├── calibration.py        # Brier score, reliability diagram
│   │   └── backtest.py           # Leave-one-out validation harness
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes_state.py
│   │   ├── routes_topology.py
│   │   ├── routes_scenario.py
│   │   ├── routes_forecast.py
│   │   └── routes_meta.py
│   └── utils/
│       ├── __init__.py
│       ├── normalization.py      # min-max, z-score, percentile
│       ├── temporal.py           # Timestamp alignment, carry-forward
│       └── quality.py            # Data freshness scoring
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api/
│       │   └── client.js         # Axios/fetch wrapper + React Query setup
│       ├── views/
│       │   ├── GlobalOverview.jsx
│       │   ├── InfrastructureTopology.jsx
│       │   ├── CountryDetail.jsx
│       │   ├── ScenarioWorkspace.jsx
│       │   └── MethodologyRisk.jsx
│       ├── components/
│       │   ├── CountryCard.jsx
│       │   ├── RadarChart.jsx
│       │   ├── Sparkline.jsx
│       │   ├── TopologyDiagram.jsx
│       │   ├── CascadeTrace.jsx
│       │   ├── RiskGauge.jsx
│       │   ├── CalibrationPlot.jsx
│       │   ├── SensitivitySliders.jsx
│       │   ├── AlertFeed.jsx
│       │   └── SystemStatusBar.jsx
│       ├── hooks/
│       │   ├── useScores.js
│       │   ├── useTopology.js
│       │   ├── useScenario.js
│       │   └── useForecast.js
│       └── utils/
│           ├── colors.js         # Risk color scale (green → amber → red)
│           └── format.js         # Number formatting, date formatting
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_topology_construction.ipynb
│   ├── 03_scoring_calibration.ipynb
│   ├── 04_disruption_backtest.ipynb
│   └── 05_scenario_analysis.ipynb
│
└── tests/
    ├── conftest.py               # Shared fixtures (seed data, test DB, test config)
    ├── test_scoring.py
    ├── test_n1_margin.py
    ├── test_cascade.py
    ├── test_scenario.py
    ├── test_risk_model.py
    ├── test_alert_rules.py
    └── test_api.py
```

---

# 17. Implementation Sequencing

Phases from the Execution Plan are refined here with explicit dependency chains and gate criteria.

### Phase 0: Foundation (Days 1–3)

**Gate to exit:** Repo initialized, database running, seed data loaded, at least one API key confirmed.

| Task | Depends on | Produces | Blocks |
|---|---|---|---|
| Initialize repo with full folder structure | Nothing | Empty scaffold | Everything |
| Define `config/topology.json` with all nodes and edges | Nothing | Topology definition | Phase 2 |
| Define `config/domains.json` with all 8 domains and indicator mappings | Nothing | Scoring config | Phase 1 |
| Define `data/seed/disruption_events.json` with 12 events | Nothing | Backtest ground truth | Phase 3 |
| Create SQLAlchemy models (`db/models.py`) | Nothing | DB schema | Phase 0 seed loading |
| Create Pydantic schemas (`schemas/*.py`) | Nothing | API contracts | Phase 4 |
| Docker Compose: PostgreSQL | Nothing | Running DB | Phase 0 seed loading |
| Seed data loading script (`db/seed.py`) | DB models + seed CSVs | Populated demo database | Phase 1 |
| Download ENTSO-E historical flows (manual if API key pending) | Nothing | `data/seed/entso_e_flows.csv` | Phase 1 |
| Download ENTSOG historical flows (no key needed) | Nothing | `data/seed/entsog_flows.csv` | Phase 1 |
| Confirm `.env.example` with all required keys | Nothing | Onboarding documentation | Phase 4 (deployment) |

### Phase 1: Scoring Engine (Days 4–7)

**Gate to exit:** All 8 domain scores computable for all 4 countries from seed data. N-1 margins correct for known outage periods. Tests pass.

| Task | Depends on | Produces | Blocks |
|---|---|---|---|
| `scoring/domain_index.py` | `config/domains.json`, seed data in DB | Domain scores for all countries | Phase 1 (escalation composite) |
| `scoring/n1_margin.py` | `config/topology.json`, ENTSO-E flow data | Per-country margins | Phase 2 (cascade validation) |
| `scoring/escalation_composite.py` | Domain scores | Escalation risk (domain 9) | Phase 3 (features) |
| `scoring/anomaly.py` | Domain score history (30 days) | Anomaly flags | Phase 4 (alerts endpoint) |
| `utils/normalization.py` | Nothing | Normalization functions | Scoring |
| `utils/temporal.py` | Nothing | Timestamp alignment | Scoring |
| `tests/test_scoring.py`, `tests/test_n1_margin.py` | Scoring modules | Passing tests | Gate |

### Phase 2: Simulation Engine (Days 8–12)

**Gate to exit:** Estlink 2 removal scenario produces Estonia capacity deficit matching documented ~650 MW loss. Balticconnector removal produces correct gas impact. Tests pass.

| Task | Depends on | Produces | Blocks |
|---|---|---|---|
| `simulation/topology.py` | `config/topology.json` | NetworkX graph loader | Cascade |
| `simulation/cascade.py` | Topology module | Capacity arithmetic engine | Scenario engine |
| `simulation/scenario_engine.py` | Cascade + topology | Full scenario runner | API routes |
| `simulation/comparator.py` | Scenario engine | Delta report + cascade trace | Dashboard view |
| Build 6 pre-built scenario JSONs | Topology definition | `config/scenarios/*.json` | Dashboard prebuilt selector |
| `tests/test_cascade.py`, `tests/test_scenario.py` | Simulation modules | Passing tests | Gate |

### Phase 3: Forecasting Engine + Backtest (Days 13–18)

**Gate to exit:** Notebook 04 runs end-to-end. Brier score computed. Leave-one-out results documented. Risk model serialized to `data/models/risk_model.joblib`.

| Task | Depends on | Produces | Blocks |
|---|---|---|---|
| `forecasting/features.py` | Indicator values, domain scores, topology state | Feature matrix | Risk model |
| `forecasting/risk_model.py` | Feature matrix, event labels | Trained logistic regression + bootstrap CIs | API forecast endpoint |
| `forecasting/alert_rules.py` | Scores, margins, topology | Rule-based alerts | API alerts endpoint |
| `forecasting/calibration.py` | Historical predictions vs. outcomes | Brier score, reliability diagram data | Backtest notebook |
| `forecasting/backtest.py` | All forecasting components | Leave-one-out validation results | Gate |
| `notebooks/04_disruption_backtest.ipynb` | Backtest harness | Documented validation narrative | **Dashboard build cannot start until this is complete** |
| `tests/test_risk_model.py`, `tests/test_alert_rules.py` | Forecasting modules | Passing tests | Gate |

### Phase 4: API Layer (Days 19–21)

**Gate to exit:** All endpoints return valid JSON matching Pydantic schemas. Integration tests pass.

| Task | Depends on | Produces | Blocks |
|---|---|---|---|
| `main.py` (FastAPI setup, CORS, lifespan) | Nothing | Running API server | All routes |
| `api/routes_state.py` | Scoring engine | State endpoints | Dashboard Overview + Detail |
| `api/routes_topology.py` | Simulation engine (topology) | Graph endpoint | Dashboard Topology view |
| `api/routes_scenario.py` | Simulation engine (full) | Scenario endpoints | Dashboard Scenario view |
| `api/routes_forecast.py` | Forecasting engine | Risk + backtest endpoints | Dashboard Methodology view |
| `api/routes_meta.py` | All engines (read-only) | Metadata endpoints | Dashboard Methodology view |
| `tests/test_api.py` | All route modules | Passing integration tests | Gate |

### Phase 5: Dashboard (Days 22–30)

**Gate to exit:** All five views render with real data from the API. No hardcoded values. No frontend-computed analytics.

| Task | Depends on | Produces | Blocks |
|---|---|---|---|
| React project setup (Vite + Tailwind + React Query) | Nothing | Empty shell | All views |
| `views/GlobalOverview.jsx` + `CountryCard` + `AlertFeed` + `SystemStatusBar` | State endpoints | View 1 | Nothing (all views independent) |
| `views/InfrastructureTopology.jsx` + `TopologyDiagram` | Topology endpoint | View 2 | Nothing |
| `views/CountryDetail.jsx` + `RadarChart` + `Sparkline` | State + provenance endpoints | View 3 | Nothing |
| `views/ScenarioWorkspace.jsx` + `CascadeTrace` | Scenario endpoints | View 4 | Nothing |
| `views/MethodologyRisk.jsx` + `RiskGauge` + `CalibrationPlot` + `SensitivitySliders` | Forecast + meta endpoints | View 5 | Nothing |

### Phase 6: Documentation + Polish (Days 31–35)

**Gate to exit:** README enables 15-minute cold start. All docs written. Deployed to Railway.

---

# 18. Architecture Freeze, Flexibility, and Urgent Decisions

### Architecture Freeze Candidates

These decisions are made. Do not revisit them during implementation.

| Decision | Rationale | Reopening cost |
|---|---|---|
| **One region (Baltic-Nordic)** | Scope anchor. Reopening adds weeks and dilutes depth. | Project timeline doubles. |
| **PostgreSQL + JSON configs** | Data layer is defined. Switching to SQLite or MongoDB mid-build wastes migration effort. | 2–3 days of rework. |
| **FastAPI backend** | API contracts are designed around FastAPI's Pydantic integration. Switching frameworks invalidates schema work. | 3–5 days of rework. |
| **Logistic regression for risk model** | Sample size dictates method. Revisiting is a distraction. | Acceptable to swap post-backtest only if honest about the reason. |
| **Capacity arithmetic for cascade** | The simulation approach is locked. Power-flow modeling is out of scope permanently. | N/A — this is a correctness decision, not a preference. |
| **Strict layered architecture with no upward calls** | The testability and auditability guarantees depend on this. Piercing a layer boundary to save time creates technical debt that undermines the portfolio story. | Breaks the architecture. Not permitted. |
| **Scenario and forecast as separate systems (N8)** | Conflating them is the single most damaging analytical error possible. | Destroys credibility. |
| **Validation before dashboard (P10)** | The build sequence is non-negotiable. | Produces a pretty but empty product. |

### Still Flexible Areas

These can be decided during implementation without architectural impact.

| Area | Options | Decision point |
|---|---|---|
| **Frontend chart library** | Recharts, Chart.js, D3, Plotly (via react-plotly.js) | Phase 5, day 22. Pick whichever renders radar charts and sparklines cleanly. |
| **Topology diagram approach** | React Flow, custom SVG, D3 force layout (static) | Phase 5, day 24. Pick based on effort-to-quality ratio. Static SVG with positioned nodes reflecting Baltic geography is likely the best tradeoff. |
| **GDELT access method** | BigQuery vs. DOC API | Phase 0, day 1. Depends on whether BigQuery free tier is accessible. DOC API is the fallback. |
| **Bootstrap CI method for risk model** | `sklearn.utils.resample` vs. manual bootstrap vs. conformal prediction | Phase 3, day 15. Any method that produces calibrated intervals is acceptable. |
| **Alert threshold values** | Configurable in `config/thresholds.json` | Phase 3, after initial scoring results reveal score distributions. Set thresholds at meaningful percentiles. |
| **Color palette and typography** | Dark theme vs. light theme, font choices | Phase 5, last two days. Do not spend time on this before all views work with default Tailwind styling. |
| **Deployment: single Railway service vs. split** | One service (FastAPI serves React build) vs. two services (separate frontend + backend) | Phase 6. Single service is simpler and sufficient for a portfolio project. |

### Decisions That Must Not Be Deferred

These require resolution in the first 48 hours of implementation. Deferring them creates compounding ambiguity.

| Decision | Why urgent | Recommended resolution |
|---|---|---|
| **ENTSO-E API key registration** | Blocks all energy data ingestion. 3-day approval lag. | Register today. Manual CSV download as interim fallback. |
| **Seed data scope and format** | Every component depends on seed data for development and testing. Undefined seed data means every developer session starts with "what data do I have?" | Define exact CSV schemas (column names, types, date ranges) in Phase 0 before any engine code is written. Commit seed data on day 2. |
| **`config/topology.json` structure** | The simulation engine, scenario engine, and dashboard topology view all read this file. Its structure is a contract across three system layers. | Define the JSON schema (TypeScript-style interface or JSON Schema) on day 1. Lock it. |
| **`config/domains.json` structure** | The scoring engine, sensitivity explorer, and methodology panel all read this file. | Define on day 1 alongside topology. |
| **Database schema migration strategy** | Will Alembic be used, or will the schema be dropped and recreated during development? | Use Alembic from day 1. The migration history itself is a quality signal for reviewers. If that feels like overhead, drop-and-recreate is acceptable for the first week only, then switch to Alembic before Phase 4. |
| **Test fixture strategy** | Tests need seed data, a test database, and test configs. Defining these after writing tests leads to inconsistent fixtures. | Create `tests/conftest.py` with shared fixtures in Phase 0. All tests use the same seed data and test database. |

---

*End of System Architecture Document v1.0.*
