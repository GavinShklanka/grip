# GRIP — Antigravity Mission Program

## Execution Sequence · v1.0

**Governing documents:** grip-source-of-truth.md, grip-system-architecture.md  
**Total missions:** 37  
**Estimated duration:** 33–38 working days  
**Rule:** No mission may begin until its prerequisites are met. No mission is "done" until its completion criteria are satisfied. No phase gate is crossed until all missions in the phase pass.

---

# Phase 1: Foundation

**Gate to exit Phase 1:** Repo initialized, configs locked, DB running with seed data, Pydantic schemas defined, test fixtures working. Zero engine code yet. The foundation must be solid before anything is built on it.

---

### M01 — Repo Scaffold

**Objective:** Create the complete directory structure with empty `__init__.py` files, config placeholders, and project metadata.

**Why it exists:** Every subsequent mission writes files into this structure. Defining it once prevents ad-hoc directory creation that drifts from the architecture.

**Prerequisites:** None. This is the first mission.

**Inputs:** Folder structure from System Architecture §16.

**Outputs:** Initialized git repo with full directory tree, `.gitignore`, `.env.example`, `pyproject.toml`, `docker-compose.yml` (PostgreSQL only), empty `README.md`.

**Files affected:**
- Every directory in the architecture tree (created)
- `pyproject.toml` (FastAPI, SQLAlchemy, pandas, numpy, scikit-learn, networkx, entsoe-py, entsog-py, httpx, python-dotenv, pydantic-settings, pytest, alembic)
- `docker-compose.yml` (PostgreSQL 16 service)
- `.gitignore` (data/raw/, data/processed/, .env, __pycache__, *.pyc, .venv/)
- `.env.example` (ENTSO_E_API_KEY, GDELT_PROJECT_ID, COPERNICUS_API_KEY, DATABASE_URL, DEMO_MODE)

**Dependencies:** None.

**Risks:** None. Pure scaffolding.

**Validation:** `find grip/ -name "*.py" | wc -l` returns expected count. `docker compose up -d` starts PostgreSQL. `pip install -e .` succeeds.

**Artifacts:** Initialized repo with first commit.

**Completion criteria:** All directories exist. PostgreSQL container starts. Python package installs. `.env.example` contains all required keys.

---

### M02 — Config Schemas

**Objective:** Define and populate `config/topology.json`, `config/domains.json`, and `config/thresholds.json` with full production content. These are contracts — they will not change structurally after this mission.

**Why it exists:** Three engine layers (scoring, simulation, dashboard) read these files. Defining them first eliminates the most common source of cross-layer breakage.

**Prerequisites:** M01.

**Inputs:**
- Infrastructure topology from Execution Plan §E3 (nodes, edges, capacities).
- Domain definitions from Source of Truth §7 (8 domains, indicator mappings).
- Historical disruption events from Baltic Research Sourcebook.

**Outputs:**
- `config/topology.json`: All nodes (4 focus countries, 4 context countries, 6 major interconnectors, 5 key facilities) with attributes. All edges with capacity, type, and current status.
- `config/domains.json`: 8 domain definitions, each with ID, name, indicator list, per-indicator weight, normalization method, and direction.
- `config/thresholds.json`: Per-domain alert thresholds (watch/warning/critical) and risk-score alert threshold.
- `config/scenarios/estlink2_severance.json` (first scenario as template for remaining five).

**Files affected:**
- `config/topology.json` (created, ~200 lines)
- `config/domains.json` (created, ~250 lines)
- `config/thresholds.json` (created, ~50 lines)
- `config/scenarios/estlink2_severance.json` (created)

**Dependencies:** None beyond M01.

**Risks:** Getting edge capacities wrong. Mitigate by cross-referencing ENTSO-E grid map and Elering/Fingrid published data.

**Validation:** JSON schema validation (manual or via Pydantic in M06). Verify node/edge counts match architecture spec. Verify all 8 domains have ≥3 indicators each. Verify domain weights sum to 1.0 per domain.

**Artifacts:** Three locked config files + one scenario template.

**Completion criteria:** Topology has ≥12 nodes and ≥12 edges. Domains have 8 entries with ≥3 indicators each. All weights sum to 1.0. Scenario template loads as valid JSON with `overrides` array.

**🔍 HUMAN REVIEW CHECKPOINT:** Config files define the analytical model. Review topology completeness, domain-indicator assignments, and weight rationale before proceeding.

---

### M03 — Database Schema

**Objective:** Define SQLAlchemy ORM models for all tables and create initial Alembic migration.

**Why it exists:** Every engine writes to or reads from the database. The schema must exist before any data loading or scoring.

**Prerequisites:** M01 (docker-compose for PostgreSQL).

**Inputs:** Entity schema from Product Spec §3, refined by System Architecture §7.

**Outputs:**
- `backend/db/models.py`: ORM models for `indicator_values`, `domain_scores`, `forecasts`, `alerts`, `topology_state`.
- `backend/db/session.py`: Engine creation, session factory, `get_db` dependency.
- `alembic/` directory with initial migration.

**Files affected:**
- `backend/db/models.py` (created)
- `backend/db/session.py` (created)
- `backend/config.py` (created — loads DATABASE_URL, DEMO_MODE from .env)
- `alembic.ini` (created)
- `alembic/env.py` (created)
- `alembic/versions/001_initial_schema.py` (created)

**Dependencies:** M01 (PostgreSQL running).

**Risks:** Schema too normalized or too denormalized. Mitigate by keeping it simple: five tables, no joins required for hot-path queries. Domain scores are pre-computed and stored flat.

**Validation:** `alembic upgrade head` succeeds. All tables created. `psql` confirms table structure matches spec.

**Artifacts:** Working database schema with migration history.

**Completion criteria:** Migration runs cleanly. All five tables exist with correct columns and types. `alembic downgrade base` and `alembic upgrade head` round-trips cleanly.

---

### M04 — Seed Data Acquisition

**Objective:** Download, clean, and format historical data into standardized CSVs for the seed data directory.

**Why it exists:** Demo mode (N14) requires committed seed data. All engine development and testing uses seed data. Without it, every development session starts with "what data do I have?"

**Prerequisites:** M02 (config files define what indicators are needed). ENTSO-E API key preferred but manual download is the fallback.

**Inputs:**
- ENTSO-E Transparency Platform: hourly cross-border flows for FI↔EE, EE↔LV, LV↔LT, SE↔LT, PL↔LT (2022-01-01 to 2026-03-31).
- ENTSOG Transparency Platform: daily flows for Balticconnector, GIPL, Klaipėda LNG, Inčukalns (2022-01-01 to 2026-03-31).
- Disruption event register: 12 events with dates, affected infrastructure, duration, severity.
- Static indicators: SIPRI defense spending, alliance data (manual CSV).

**Outputs:**
- `data/seed/entso_e_flows.csv`: Columns: `timestamp, from_country, to_country, interconnector_id, flow_mw`. Hourly. ~150K+ rows.
- `data/seed/entsog_flows.csv`: Columns: `date, point_id, flow_mcm, direction`. Daily. ~6K rows.
- `data/seed/disruption_events.json`: 12 events, each with `event_id, start_date, end_date, affected_edges[], severity, description, source_url`.
- `data/seed/static_indicators.csv`: Annual defense spending, exercise counts, alliance scores.
- `data/seed/gdelt_events.csv`: Weekly aggregated event counts and tone for Baltic region (placeholder — can be generated from BigQuery or approximated from DOC API).
- `data/seed/sanctions_counts.csv`: Daily sanctions entity counts (can be generated from OpenSanctions API or approximated).

**Files affected:** All files in `data/seed/`.

**Dependencies:** M02 (to know exactly which indicators to pull). External API access (or manual download from web interfaces).

**Risks:** ENTSO-E API key not yet approved. **Mitigation:** Use ENTSO-E web interface for manual CSV download of cross-border flows. Slower but achieves the same result. Fingrid Open Data provides FI-side flows as secondary source.

**Validation:** For each seed CSV: row count is reasonable for the date range, no null values in key columns, timestamps are continuous (no multi-day gaps), data types are correct. For disruption events JSON: 12 entries, all dates parse correctly, all `affected_edges` values exist in `topology.json`.

**Artifacts:** Complete seed data directory, committed to repo.

**Completion criteria:** `DEMO_MODE=true` data loading (M05) succeeds using only these files. Verify ENTSO-E flows show clear drops to zero during documented outage periods (spot-check Estlink 2 on 2024-12-25 and Balticconnector on 2023-10-08).

**⚠️ LONG-POLE TASK:** This is the most time-consuming foundation mission. Expect 1.5–2 days. Start immediately. If ENTSO-E API is not approved, use manual download on day 1 and switch to API for live mode later.

---

### M05 — Seed Data Loader

**Objective:** Build the script that loads seed CSVs into PostgreSQL for demo mode.

**Why it exists:** Constraint N14 — demo mode must work with no external API calls. This loader is the bridge between committed seed files and the database that engines read from.

**Prerequisites:** M03 (database schema), M04 (seed data files).

**Inputs:** Seed CSV/JSON files from `data/seed/`. SQLAlchemy models from M03.

**Outputs:**
- `backend/db/seed.py`: Script that reads all seed files and bulk-inserts into the appropriate tables. Idempotent (can be re-run safely — truncates tables first).

**Files affected:**
- `backend/db/seed.py` (created)

**Dependencies:** M03, M04.

**Risks:** CSV parsing edge cases (encoding, date formats). Mitigate by standardizing all seed CSVs to UTF-8, ISO 8601 timestamps, and explicit headers in M04.

**Validation:** Run seed loader. Query each table. Verify row counts match expectations. Verify a sample query (e.g., "Estlink 2 flow on 2024-12-25") returns the expected zero-flow record.

**Artifacts:** Working seed loader.

**Completion criteria:** `python -m backend.db.seed` populates all tables from seed data in < 30 seconds. Re-running it produces identical results (idempotent).

---

### M06 — Pydantic Response Schemas

**Objective:** Define all API request and response models as Pydantic classes.

**Why it exists:** These schemas are the contract between the API layer and the frontend. Defining them before engine code ensures engines produce data in the expected shape. FastAPI auto-generates OpenAPI docs from these, which is a portfolio asset.

**Prerequisites:** M02 (config structure), M03 (DB models — response schemas mirror stored data).

**Inputs:** API endpoint specifications from System Architecture §4 (functional requirements API-1 through API-8).

**Outputs:**
- `backend/schemas/state.py`: `ScoreResponse`, `MarginResponse`, `AlertResponse`, `FlowResponse`.
- `backend/schemas/topology.py`: `NodeResponse`, `EdgeResponse`, `GraphResponse`.
- `backend/schemas/scenario.py`: `ScenarioOverride`, `ScenarioRequest`, `CascadeStep`, `CascadeTrace`, `ScenarioResponse`.
- `backend/schemas/forecast.py`: `RiskResponse`, `BacktestEventResult`, `BacktestResponse`, `CalibrationBin`, `CalibrationResponse`.
- `backend/schemas/meta.py`: `AssumptionResponse`, `ProvenanceIndicator`, `ProvenanceResponse`, `SystemStatusResponse`.

**Files affected:** All files in `backend/schemas/`.

**Dependencies:** M02, M03.

**Risks:** Over-specifying response models that don't match what engines will actually produce. Mitigate by keeping models flat and using `Optional` fields for computed values that may not exist in early phases.

**Validation:** All Pydantic models instantiate with example data without validation errors. `mypy` or `pyright` finds no type errors.

**Artifacts:** Complete schema package.

**Completion criteria:** Every API endpoint from §4 has a corresponding response model. Models can be imported and instantiated in a test script.

---

### M07 — Test Fixtures

**Objective:** Create shared test infrastructure: conftest.py with fixtures for test database, seed data, test configs, and engine instances.

**Why it exists:** Without shared fixtures, each test file reinvents data setup. This leads to inconsistent test data and fragile tests that break when schemas change.

**Prerequisites:** M03, M04, M05, M06.

**Inputs:** Seed data, DB models, Pydantic schemas.

**Outputs:**
- `tests/conftest.py`: Fixtures for `test_db` (SQLite in-memory for speed), `seed_data` (loads subset of seed CSVs), `test_topology` (loads topology.json), `test_domains_config` (loads domains.json), `sample_scores` (pre-computed domain scores for testing).

**Files affected:**
- `tests/conftest.py` (created)

**Dependencies:** M03, M04, M05, M06.

**Risks:** Using PostgreSQL for tests is slow. Mitigate by using SQLite in-memory with the same SQLAlchemy models (test for logic, not for Postgres-specific features).

**Validation:** `pytest tests/conftest.py` imports without errors. Each fixture is usable in a trivial test that just asserts the fixture returns non-None.

**Artifacts:** Working test infrastructure.

**Completion criteria:** `pytest --co` (collect-only) finds conftest and reports fixtures available. A stub test using each fixture passes.

---

**📋 PHASE 1 GATE REVIEW**

Before proceeding to Phase 2, verify:
- [ ] All config files load as valid JSON
- [ ] Database schema runs via Alembic
- [ ] Seed data loaded, spot-check queries pass
- [ ] Pydantic schemas instantiate with example data
- [ ] Test fixtures work
- [ ] `git log` shows clean commit history with one commit per mission

---

# Phase 2: Core Build

**Gate to exit Phase 2:** All three engines (scoring, simulation, forecasting) produce correct output from seed data. Unit tests pass. Backtest notebook is complete and documents model performance.

---

### M08 — Utility Modules

**Objective:** Build normalization, temporal alignment, and data quality utility functions used by all engines.

**Why it exists:** Three engines need the same normalization functions and timestamp handling. Building these once prevents divergent implementations.

**Prerequisites:** M07 (test fixtures for testing utils).

**Inputs:** Normalization methods from Source of Truth (min-max 5yr, z-score, percentile rank). Temporal alignment logic from Architecture §7 (carry-forward for stale data).

**Outputs:**
- `backend/utils/normalization.py`: `min_max_normalize(series, baseline_min, baseline_max) → series[0,100]`, `z_score(series) → series`, `percentile_rank(value, distribution) → float[0,100]`.
- `backend/utils/temporal.py`: `align_timestamps(df, target_freq, method='forward_fill') → df`, `calculate_staleness(last_timestamp, now) → timedelta`, `is_stale(last_timestamp, max_age) → bool`.
- `backend/utils/quality.py`: `data_coverage(indicators_df, expected_count) → float[0,1]`, `freshness_score(timestamps, max_ages) → float[0,1]`.

**Files affected:** `backend/utils/normalization.py`, `backend/utils/temporal.py`, `backend/utils/quality.py`, `tests/test_utils.py`.

**Dependencies:** M07.

**Risks:** Edge cases in normalization (division by zero when min=max, NaN handling). Mitigate with explicit tests for edge cases.

**Validation:** Unit tests covering: normalization of known series produces expected output, forward-fill across gaps, staleness detection for timestamps at boundary conditions. ≥10 test cases.

**Artifacts:** Three utility modules + test file.

**Completion criteria:** All utility functions have docstrings, type hints, and passing tests. `pytest tests/test_utils.py` passes.

---

### M09 — Ingestion Base + Runner

**Objective:** Define the abstract ingestion interface and the runner that orchestrates all modules.

**Why it exists:** Architecture Principle P3 — each ingestion module implements a common interface. The runner iterates modules and isolates failures.

**Prerequisites:** M03 (DB session), M08 (temporal utils).

**Inputs:** Ingestion architecture from System Architecture §7 (component map, ingestion layer).

**Outputs:**
- `backend/ingestion/base.py`: Abstract class `IngestionModule` with methods `fetch(date_range) → DataFrame`, `transform(df) → DataFrame`, `load(df, session) → int` (returns rows loaded).
- `backend/ingestion/runner.py`: `run_all(session, date_range, modules=None)` — iterates registered modules, catches exceptions per-module, logs results, sets staleness flags on failure.

**Files affected:** `backend/ingestion/base.py`, `backend/ingestion/runner.py`.

**Dependencies:** M03, M08.

**Risks:** None. This is interface definition + orchestration logic.

**Validation:** A mock module implementing the interface can be registered with the runner and executed. Runner catches and logs a deliberately-raised exception without crashing.

**Artifacts:** Base interface + runner.

**Completion criteria:** Runner executes a mock module successfully and handles a failing mock module gracefully.

---

### M10 — ENTSO-E Ingestion

**Objective:** Build the ingestion module that pulls hourly cross-border electricity flows from the ENTSO-E Transparency Platform.

**Why it exists:** ENTSO-E data is the backbone of domains 1 (energy_dependence), 2 (infrastructure_vulnerability), and the N-1 margin calculator.

**Prerequisites:** M09 (base interface), ENTSO-E API key.

**Inputs:** ENTSO-E API via `entsoe-py`. Country codes: FI, EE, LV, LT, SE, PL. Five interconnector pairs.

**Outputs:**
- `backend/ingestion/entso_e.py`: Implements `IngestionModule`. Fetches hourly scheduled/actual cross-border flows. Also fetches forced outage data (unavailability of transmission assets).

**Files affected:** `backend/ingestion/entso_e.py`.

**Dependencies:** M09. ENTSO-E API key (or demo-mode bypass).

**Risks:** `entsoe-py` API wrapper quirks (XML parsing, rate limits, date format edge cases). Mitigate by testing against a small date range first (1 week). API key expiration (183 days) — document renewal process.

**Validation:** Fetch 7 days of FI→EE flows. Verify hourly resolution, non-null values, MW unit. Compare against ENTSO-E web interface for same period.

**Artifacts:** Working ENTSO-E ingestion module.

**Completion criteria:** Module fetches and loads 7 days of data for all 5 interconnector pairs. Rows appear in `indicator_values` with correct source tag. In demo mode, module skips API call and returns immediately.

---

### M11 — ENTSOG Ingestion

**Objective:** Build the ingestion module for daily gas flow data.

**Why it exists:** ENTSOG data feeds the gas side of energy_dependence and supply_route_disruption domains.

**Prerequisites:** M09. No API key required.

**Inputs:** ENTSOG API via `entsog-py`. Points: Balticconnector, GIPL, Klaipėda LNG, Inčukalns UGS.

**Outputs:**
- `backend/ingestion/entsog.py`: Implements `IngestionModule`. Fetches daily physical flows.

**Files affected:** `backend/ingestion/entsog.py`.

**Dependencies:** M09.

**Risks:** `entsog-py` default pagination (100 rows). Must use `limit=-1`. Documented in research sourcebook.

**Validation:** Fetch 30 days of Balticconnector flows. Verify daily resolution. Check that Oct 2023 data shows zero flow (outage period).

**Artifacts:** Working ENTSOG ingestion module.

**Completion criteria:** Module fetches and loads 30 days for all 4 gas points. Correct source tag. Demo mode bypass works.

---

### M12 — Domain Scoring Engine

**Objective:** Build the composite scoring engine that reads indicator values and config weights, and produces per-country domain scores.

**Why it exists:** Domain scores are the primary descriptive output of the system. Everything downstream (escalation composite, forecasting features, dashboard) depends on them.

**Prerequisites:** M02 (domains.json), M04/M05 (seed data in DB), M08 (normalization utils).

**Inputs:** `indicator_values` table (filtered by domain), `config/domains.json` (weights, normalization methods).

**Outputs:**
- `backend/scoring/domain_index.py`: `compute_domain_scores(indicators_df, config) → DataFrame[country_id, domain_id, score, velocity, data_coverage, anomaly_flag, timestamp]`.

**Files affected:** `backend/scoring/domain_index.py`, `tests/test_scoring.py`.

**Dependencies:** M02, M05, M08.

**Risks:** Weight misconfiguration (weights don't sum to 1.0). Mitigate with assertion check on config load. Indicator direction mismatch (higher_is_worse vs. lower_is_worse). Mitigate by reading direction from config and inverting normalization accordingly.

**Validation:** Compute scores for all countries from seed data. Verify: (1) all scores in [0, 100], (2) during known disruption periods, `infrastructure_vulnerability` and `energy_dependence` scores are measurably higher than stable periods, (3) changing a weight in config changes the output proportionally.

**Artifacts:** Scoring engine + tests.

**Completion criteria:** 32 domain scores produced (8 domains × 4 countries). Scores vary meaningfully between disruption and stable periods. Weight change test passes. `pytest tests/test_scoring.py` passes with ≥8 test cases.

**🔍 HUMAN REVIEW CHECKPOINT:** Review scoring output for known disruption periods. Do the numbers make intuitive sense? Is Estonia's infrastructure_vulnerability score elevated during Estlink 2 outage periods?

---

### M13 — N-1 Margin Calculator

**Objective:** Build the capacity margin calculator that determines how much import headroom each country has after accounting for the largest single contingency.

**Why it exists:** The N-1 margin is the single most operationally meaningful metric for Baltic grid stability post-BRELL. It is also the foundation for cascade computation (M16).

**Prerequisites:** M02 (topology.json with capacities), M10 or M05 (flow data).

**Inputs:** `config/topology.json` (edge capacities and statuses), current flow data (or seed data), country demand estimates.

**Outputs:**
- `backend/scoring/n1_margin.py`: `compute_margins(topology, current_flows, current_outages) → Dict[country_id, MarginResult]` where `MarginResult` has `available_import_mw`, `demand_mw`, `reserve_requirement_mw`, `margin_mw`, `status` (green/amber/red).

**Files affected:** `backend/scoring/n1_margin.py`, `tests/test_n1_margin.py`.

**Dependencies:** M02.

**Risks:** Demand estimates are approximate (ENTSO-E provides load data but not always for all Baltic countries at hourly granularity). Mitigate by using conservative demand estimates from seed data averages and documenting the approximation.

**Validation:** Compute margin with all interconnectors active → margin should be positive. Set Estlink 2 to offline → Estonia's margin should drop by ~650 MW. Set both Estlinks to offline → Estonia's margin should be deeply negative.

**Artifacts:** N-1 calculator + tests.

**Completion criteria:** Margins computed for all 4 countries. Status coloring is correct (green > 500 MW, amber 0–500 MW, red < 0 MW — thresholds configurable). Estlink 2 outage test produces expected impact. ≥5 test cases pass.

---

### M14 — Escalation Composite + Anomaly Detection

**Objective:** Build the composite domain (domain 9: escalation_risk) and the anomaly flagging system.

**Why it exists:** The escalation composite provides the single headline number per country. Anomaly detection drives the alert feed.

**Prerequisites:** M12 (domain scores exist to aggregate).

**Inputs:** Domain scores (8 per country), `config/domains.json` (composite weights), velocity (rate of change).

**Outputs:**
- `backend/scoring/escalation_composite.py`: `compute_escalation_risk(domain_scores, config) → DataFrame` using weighted average with velocity multiplier.
- `backend/scoring/anomaly.py`: `detect_anomalies(domain_scores_history, window=30) → DataFrame` with `anomaly_flag` boolean.

**Files affected:** `backend/scoring/escalation_composite.py`, `backend/scoring/anomaly.py`.

**Dependencies:** M12.

**Risks:** Velocity multiplier could amplify noise in volatile domains (esp. GDELT-fed geopolitical_tension). Mitigate by capping the velocity multiplier (e.g., max 1.5×) and making the cap configurable.

**Validation:** Composite score exists for all 4 countries. It responds to changes in underlying domain scores. Anomaly flags fire during known disruption periods. Anomaly flags do not fire during stable periods (no false positives in test data).

**Artifacts:** Two scoring modules.

**Completion criteria:** Domain 9 scores produced. Anomaly flags present in output. At least one anomaly flagged during a known disruption period in seed data.

---

### M15 — Topology Graph Loader

**Objective:** Build the module that loads `config/topology.json` into a NetworkX DiGraph with typed nodes and attributed edges.

**Why it exists:** The simulation engine's cascade computation operates on this graph. Scenario overrides modify copies of this graph.

**Prerequisites:** M02 (topology.json finalized).

**Inputs:** `config/topology.json`.

**Outputs:**
- `backend/simulation/topology.py`: `load_topology(config_path) → nx.DiGraph`. `get_current_state(graph) → Dict`. `apply_outages(graph, outage_register) → nx.DiGraph`.

**Files affected:** `backend/simulation/topology.py`.

**Dependencies:** M02.

**Risks:** None. Straightforward JSON-to-graph parsing.

**Validation:** Load graph, verify node count, edge count, and that all edges have `capacity` and `status` attributes. Verify `graph.neighbors('EE')` returns expected connected nodes.

**Artifacts:** Topology loader.

**Completion criteria:** Graph loads. Node/edge counts match config. Attribute access works. No orphan nodes.

---

### M16 — Cascade Engine

**Objective:** Build the capacity-arithmetic cascade computation that determines the impact of edge removal on downstream countries.

**Why it exists:** This is GRIP's analytical differentiator. It converts "edge removed" into "country X has N MW deficit" — a concrete, verifiable consequence.

**Prerequisites:** M15 (topology loader), M13 (margin calculation logic).

**Inputs:** NetworkX graph (from M15), list of edge overrides (edge_id, new_status).

**Outputs:**
- `backend/simulation/cascade.py`: `compute_cascade(graph, overrides) → CascadeResult` where `CascadeResult` contains per-country margins (before and after), delta per country, and a step-by-step trace of which overrides affected which countries.

**Files affected:** `backend/simulation/cascade.py`, `tests/test_cascade.py`.

**Dependencies:** M15, M13.

**Risks:** Double-counting capacity when an interconnector serves as both import and export in different scenarios. Mitigate by treating flow direction as a graph attribute and summing only inbound edges for import capacity.

**Validation:** Three critical tests:
1. Remove Estlink 2 → Estonia import capacity drops ~650 MW. Matches documented Dec 2024 impact.
2. Remove Balticconnector → Finland-Estonia gas capacity drops to 0 mcm. Matches documented Oct 2023 impact.
3. Remove both Estlinks → Estonia total FI import capacity = 0 MW. Matches worst-case Jan 2026 scenario (both tripped simultaneously).

**Artifacts:** Cascade engine + tests.

**Completion criteria:** All three validation tests pass within 10% of documented real-world impacts. Cascade trace is a list of steps in correct order. `pytest tests/test_cascade.py` passes with ≥6 test cases.

**🔍 HUMAN REVIEW CHECKPOINT:** Compare cascade outputs against documented event impacts. Are the numbers in the right ballpark? This is the system's credibility anchor.

---

### M17 — Scenario Engine + Comparator

**Objective:** Build the scenario runner (loads pre-built or custom overrides, runs cascade, produces full comparison) and the comparator (diffs current vs. simulated state).

**Why it exists:** Scenarios are the user-facing analytical tool. The comparator produces the side-by-side view the dashboard needs.

**Prerequisites:** M16 (cascade engine), M12 (domain scoring for re-scoring under simulation).

**Inputs:** Scenario JSON files, cascade engine, scoring engine.

**Outputs:**
- `backend/simulation/scenario_engine.py`: `run_scenario(scenario_def, current_state) → ScenarioResult` containing current_state, simulated_state, deltas, cascade_trace.
- `backend/simulation/comparator.py`: `compare_states(current, simulated) → ComparisonReport` with per-country, per-domain deltas and summary statistics.

**Files affected:** `backend/simulation/scenario_engine.py`, `backend/simulation/comparator.py`, `tests/test_scenario.py`. Also: create remaining 5 scenario JSON files in `config/scenarios/`.

**Dependencies:** M16, M12.

**Risks:** Scenario overrides conflicting with each other (e.g., two overrides targeting the same edge with different statuses). Mitigate by applying overrides in order and logging conflicts.

**Validation:** Run all 6 pre-built scenarios. Each produces non-zero deltas. Estlink 2 scenario matches M16 cascade test. Custom scenario via API-style input also works.

**Artifacts:** Scenario engine, comparator, 6 scenario JSONs, tests.

**Completion criteria:** 6 pre-built scenarios run successfully. Custom overrides accepted. Comparison report contains all expected fields. ≥5 test cases pass.

---

### M18 — Feature Engineering Pipeline

**Objective:** Build the feature construction pipeline that produces the daily feature matrix for the risk model.

**Why it exists:** The risk model (M19) cannot be trained or run without features. The feature pipeline transforms raw indicators and domain scores into the model input.

**Prerequisites:** M12 (domain scores), M15 (topology for outage count), M04 (seed data including GDELT and weather).

**Inputs:** `indicator_values`, `domain_scores`, `topology_state`, `disruption_events.json` (for `days_since_last_disruption`).

**Outputs:**
- `backend/forecasting/features.py`: `build_feature_matrix(indicators, scores, topology_state, events, date_range) → DataFrame` with columns: `date`, `gdelt_event_intensity`, `gdelt_tone_avg`, `weather_wind_max`, `weather_wave_max`, `active_outage_count`, `days_since_last_disruption`, `sanctions_pressure_score`, `energy_dependence_velocity`, `infra_vulnerability_velocity`, `month`, `is_winter`, `n1_margin_min`.

**Files affected:** `backend/forecasting/features.py`.

**Dependencies:** M12, M15, M04.

**Risks:** Feature leakage — using information from the disruption day itself to predict the disruption. Mitigate by strictly using feature values from day T-1 to predict outcome in window [T, T+30].

**Validation:** Generate feature matrix from seed data. Verify: no NaN in output (forward-fill applied), feature count matches specification, date range is continuous, no future information leakage (spot-check a disruption date).

**Artifacts:** Feature pipeline.

**Completion criteria:** Feature matrix generated for full seed data period. No NaN values. Feature columns match specification. Date indexing is correct.

---

### M19 — Risk Model

**Objective:** Train the logistic regression disruption-risk model and implement inference with bootstrap confidence intervals.

**Why it exists:** The risk score is the system's sole probabilistic claim. It is the forecast target defined in the Source of Truth.

**Prerequisites:** M18 (feature matrix), M04 (disruption event labels).

**Inputs:** Feature matrix (from M18), binary labels (disruption within 30 days = 1, else 0, derived from `disruption_events.json`).

**Outputs:**
- `backend/forecasting/risk_model.py`: `train_model(features, labels) → LogisticRegression`. `predict_risk(model, features_today) → RiskPrediction(probability, ci_lower_80, ci_upper_80, ci_lower_95, ci_upper_95, model_confidence)`. `save_model(model, path)`, `load_model(path) → LogisticRegression`.
- `data/models/risk_model.joblib` (serialized trained model).

**Files affected:** `backend/forecasting/risk_model.py`, `data/models/risk_model.joblib`, `tests/test_risk_model.py`.

**Dependencies:** M18.

**Risks:** Model does not converge (6 positive events may be insufficient). Mitigate: try `class_weight='balanced'`, reduce feature count to top 5 by univariate analysis, use regularization `C=0.1`. If model still fails, document the failure and rely on alert rules (M20). Overfitting — mitigate with leave-one-out cross-validation (M21).

**Validation:** Model produces probabilities in [0, 1]. Bootstrap CIs bracket the point estimate. Feature coefficients have interpretable signs (e.g., higher outage count → higher risk).

**Artifacts:** Trained model + inference code + tests.

**Completion criteria:** Model trains without error. Probabilities are in valid range. CIs are computed. Model serialized to disk. `load_model` + `predict_risk` round-trips correctly. ≥4 test cases pass.

---

### M20 — Alert Rules Engine

**Objective:** Build deterministic, rule-based alert triggers that operate independently of the statistical model.

**Why it exists:** The statistical model may fail (small sample). Rule-based alerts provide decision-relevant output regardless. They cover structural conditions the model can't learn from 6 events.

**Prerequisites:** M13 (N-1 margins), M12 (domain scores), M15 (topology state).

**Inputs:** Current margins, current scores, current topology state, `config/thresholds.json`.

**Outputs:**
- `backend/forecasting/alert_rules.py`: `evaluate_alerts(margins, scores, topology, thresholds) → List[Alert]`. Each `Alert` has `alert_id, severity (watch/warning/critical), rule_name, description, affected_countries, timestamp`.

Rules:
1. N-1 margin < 0 for any country → CRITICAL
2. N-1 margin < 500 MW for any country → WARNING  
3. 2+ interconnectors offline simultaneously → CRITICAL
4. Any domain score > critical threshold → WARNING
5. Risk model probability > alert threshold → WARNING

**Files affected:** `backend/forecasting/alert_rules.py`, `tests/test_alert_rules.py`.

**Dependencies:** M13, M12, M15.

**Risks:** Threshold values may be poorly calibrated initially. Mitigate by making all thresholds configurable in `thresholds.json` and adjusting after reviewing score distributions in seed data.

**Validation:** Simulate Estlink 2 outage → Rule 2 or 1 fires for Estonia. Simulate both Estlinks down → Rule 3 fires. Set a domain score above threshold → Rule 4 fires.

**Artifacts:** Alert rules engine + tests.

**Completion criteria:** All 5 rules implemented. Each rule tested individually. No false positives on stable-period seed data. Expected alerts fire during disruption periods. ≥6 test cases pass.

---

### M21 — Calibration + Backtest Harness

**Objective:** Build the leave-one-out cross-validation harness and calibration scoring.

**Why it exists:** Architecture Principle P8 and Constraint N7. The backtest is the credibility anchor. Without it, the risk model is an unvalidated claim.

**Prerequisites:** M19 (risk model), M18 (features), M04 (event register).

**Inputs:** Feature matrix, event register (6 energy-interconnector events), trained model.

**Outputs:**
- `backend/forecasting/backtest.py`: `run_leave_one_out(features, labels, events) → BacktestResult` containing per-event results (held-out event, peak risk score in prior 30 days, was risk elevated?) and aggregate Brier score.
- `backend/forecasting/calibration.py`: `compute_calibration(predictions, outcomes, n_bins=10) → CalibrationResult` containing per-bin predicted probability, observed frequency, and Brier score.

**Files affected:** `backend/forecasting/backtest.py`, `backend/forecasting/calibration.py`.

**Dependencies:** M19, M18, M04.

**Risks:** Brier score worse than naive baseline (~0.12). This is an acceptable outcome if documented honestly. The risk model becomes an "indicative signal" and the alert rules (M20) carry the decision-support load.

**Validation:** Backtest runs for all 6 events. Each iteration produces a valid risk trajectory. Brier score is a finite number. Calibration bins have valid frequencies.

**Artifacts:** Backtest harness, calibration scorer.

**Completion criteria:** Leave-one-out produces 6 per-event results. Brier score computed. Calibration data structured for visualization. Results ready for notebook M28.

---

**📋 PHASE 2 GATE REVIEW**

Before proceeding to Phase 3:
- [ ] Domain scores: 32 records (8×4), varying meaningfully between stable/disruption periods
- [ ] N-1 margins: 4 records, correct for known outage configurations
- [ ] Cascade: Estlink 2 removal matches ~650 MW documented impact
- [ ] 6 scenarios run without errors
- [ ] Risk model trained and serialized
- [ ] Alert rules fire correctly for simulated conditions
- [ ] Backtest harness runs all 6 events
- [ ] All `pytest` tests pass

---

# Phase 3: Integration

**Gate to exit Phase 3:** All API endpoints return valid JSON matching Pydantic schemas. Integration tests pass.

---

### M22 — FastAPI App Shell

**Objective:** Create the FastAPI application with CORS, lifespan events (seed data loading in demo mode), and health check endpoint.

**Prerequisites:** M05 (seed loader for demo mode), M06 (Pydantic schemas).

**Outputs:**
- `backend/main.py`: App factory with CORS middleware, lifespan handler (loads seed data + topology on startup in demo mode), `/health` endpoint.
- `backend/config.py`: Updated with all settings (DEMO_MODE, DATABASE_URL, CORS_ORIGINS).

**Completion criteria:** `uvicorn backend.main:app` starts. `GET /health` returns `{"status": "ok", "demo_mode": true}`. Seed data is loaded on startup.

---

### M23 — State API Routes

**Objective:** Wire scoring engine outputs to HTTP endpoints.

**Prerequisites:** M22, M12, M13, M14.

**Outputs:** `backend/api/routes_state.py` with endpoints: `GET /api/state/scores`, `GET /api/state/scores/{country_id}`, `GET /api/state/margins`, `GET /api/state/alerts`.

**Completion criteria:** All four endpoints return valid JSON matching Pydantic schemas from M06.

---

### M24 — Topology API Routes

**Prerequisites:** M22, M15.

**Outputs:** `backend/api/routes_topology.py` with `GET /api/topology/graph`, `GET /api/topology/outages`.

**Completion criteria:** Graph endpoint returns all nodes and edges with attributes.

---

### M25 — Scenario API Routes

**Prerequisites:** M22, M17.

**Outputs:** `backend/api/routes_scenario.py` with `POST /api/scenario/run`, `GET /api/scenario/prebuilt`, `GET /api/scenario/prebuilt/{scenario_id}`.

**Completion criteria:** POST with Estlink 2 override returns correct cascade result. Prebuilt list returns 6 scenarios.

---

### M26 — Forecast + Meta API Routes

**Prerequisites:** M22, M19, M20, M21.

**Outputs:**
- `backend/api/routes_forecast.py`: `GET /api/forecast/risk`, `GET /api/forecast/alerts`, `GET /api/forecast/backtest`.
- `backend/api/routes_meta.py`: `GET /api/meta/assumptions`, `GET /api/meta/provenance/{domain_id}/{country_id}`, `GET /api/meta/data-quality`, `GET /api/meta/system-status`.

**Completion criteria:** All endpoints return valid JSON. Risk endpoint includes confidence intervals. Backtest endpoint includes per-event results and Brier score.

---

### M27 — API Integration Tests

**Objective:** End-to-end tests that start the app, hit every endpoint, and validate response schemas.

**Prerequisites:** M22–M26.

**Outputs:** `tests/test_api.py` using `httpx.AsyncClient` with FastAPI's `TestClient`.

**Completion criteria:** Every endpoint tested. All responses validate against Pydantic schemas. Error responses (invalid country_id, malformed scenario) return correct status codes. ≥15 test cases pass.

---

# Phase 4: Validation

**Gate to exit Phase 4:** Backtest notebook complete and renders. Documentation written. All claims are documented and bounded.

---

### M28 — Backtest Notebook

**Objective:** Write the narrative backtesting notebook that is both a validation artifact and a portfolio deliverable.

**Why it exists:** Constraint N7 — validation before dashboard. Principle P8 — the notebook is a deliverable, not a worksheet. This is the single most important artifact for credibility.

**Prerequisites:** M21 (backtest harness produces results), all Phase 2 engines complete.

**Inputs:** Backtest results from M21, seed data, event register.

**Outputs:**
- `notebooks/04_disruption_backtest.ipynb`: Sections: Introduction → Data Overview → Feature Analysis → Model Training → Leave-One-Out Results (with per-event narrative) → Calibration Analysis → Brier Score vs. Baseline → Feature Importance → Limitations → Conclusions.

**Files affected:** `notebooks/04_disruption_backtest.ipynb`.

**Risks:** Model performance is poor. This is the documented-honestly outcome, not a failure of the mission. The notebook must report what happened, not what we wished happened.

**Validation:** Notebook runs end-to-end from raw seed data to final plots (`Restart Kernel and Run All` succeeds). A non-author can read it and understand the methodology, results, and limitations.

**Artifacts:** Complete, reproducible backtesting notebook.

**Completion criteria:** Runs without errors. Contains ≥3 visualizations (risk trajectory over time, calibration plot, feature importance). Contains explicit "Limitations" section. Contains Brier score with comparison to naive baseline. No code cells without markdown explanation above them.

**🔍 HUMAN REVIEW CHECKPOINT:** This is the most important review. Read the notebook as a faculty reviewer would. Are the claims honest? Are the limitations clear? Would you trust this analysis?

---

### M29 — Documentation Suite

**Objective:** Write all required docs.

**Prerequisites:** M28 (backtest results inform limitations and methodology docs).

**Outputs:**
- `docs/methodology.md`: Full scoring methodology with worked example for one domain.
- `docs/data-dictionary.md`: Every indicator with source, cadence, unit, and known issues.
- `docs/infrastructure-topology.md`: Description of the Baltic serial chain with diagram reference.
- `docs/backtesting-report.md`: Prose version of notebook 04 findings.
- `docs/limitations.md`: ≥5 specific, quantified limitations (Constraint N11).
- `docs/assumptions-register.md`: All assumptions from Source of Truth §4 with current status.

**Completion criteria:** All six docs exist, are non-empty, and contain substantive content (not placeholders). Limitations doc has ≥5 items with quantified impact.

---

# Phase 5: Polish and Hardening

**Gate to exit Phase 5:** Dashboard renders all five views with real API data. Deployed to Railway. README enables 15-minute cold start.

---

### M30–M35 — Dashboard Views (6 missions)

Each dashboard view is a separate mission. They are **safe for parallel execution** — no view depends on another.

| Mission | View | Key components | API dependencies | Estimated effort |
|---|---|---|---|---|
| M30 | React project shell + routing | App.jsx, navigation, React Query setup, color/format utils | `/health` | 0.5 days |
| M31 | Global Overview | CountryCard, AlertFeed, SystemStatusBar | `/api/state/scores`, `/api/state/margins`, `/api/state/alerts`, `/api/meta/system-status` | 1.5 days |
| M32 | Infrastructure Topology | TopologyDiagram (SVG), edge status colors, click-to-inspect | `/api/topology/graph` | 2 days |
| M33 | Country Detail | RadarChart, Sparkline, indicator breakdown | `/api/state/scores/{country}`, `/api/meta/provenance/{domain}/{country}` | 1.5 days |
| M34 | Scenario Workspace | Scenario selector, edge toggles, CascadeTrace, side-by-side | `POST /api/scenario/run`, `/api/scenario/prebuilt` | 2 days |
| M35 | Methodology & Risk | RiskGauge, CalibrationPlot, SensitivitySliders, assumptions list | `/api/forecast/risk`, `/api/forecast/backtest`, `/api/meta/assumptions` | 1.5 days |

**Completion criteria per view:** View renders with real data from API. No hardcoded values. No frontend-computed analytics (DSH-6). Responsive to data changes (modify seed data, refresh page, see update).

**🔍 HUMAN REVIEW CHECKPOINT after M31:** Review the Global Overview for visual clarity, color system, and information hierarchy before building remaining views.

---

### M36 — Visual Polish

**Objective:** Apply consistent color system, typography, spacing, and command-room aesthetic across all views.

**Why it exists:** The dashboard must look professional but not theatrical. This mission applies design consistency after all views are functionally complete.

**Prerequisites:** M30–M35 all complete.

**⚠️ REWORK RISK IF DONE TOO EARLY:** Do not start this before all five views are functionally rendering. Polishing a view that later changes structurally wastes effort.

**Completion criteria:** Consistent color scale (green → amber → red) across all views. Consistent font sizing. No Tailwind default colors visible. Dark background preferred. No decorative elements that don't convey information.

---

### M37 — Deployment

**Objective:** Deploy full-stack application to Railway.

**Prerequisites:** M30–M36 (functional dashboard), M22 (API working).

**Outputs:** Live URL serving the dashboard with demo mode data.

**Completion criteria:** URL loads dashboard. All five views render. API health check returns 200. No errors in Railway logs. Demo mode active (no external API calls from deployed instance).

---

### M38 — README + Cold-Start Verification

**Objective:** Write the README that enables a reviewer to run the system locally in 15 minutes.

**Why it exists:** Constraint N13. The README is the first thing a reviewer reads. If setup fails, they stop reading.

**Prerequisites:** Everything. This is the last mission.

**Outputs:** `README.md` with: project summary, architecture diagram (text-based), setup instructions (prerequisites, clone, env setup, docker, seed data, run backend, run frontend), demo walkthrough, link to deployed instance, link to backtest notebook, technology stack, and project structure overview.

**Validation:** Have someone who has never seen the project follow the README from scratch. They should have a running dashboard within 15 minutes.

**Completion criteria:** README exists. Setup instructions are tested. Links work. Time-to-running verified.

---

# Execution Intelligence

### Missions safe for parallel execution

| Parallel group | Missions | Rationale |
|---|---|---|
| **Config pair** | M02 + M03 | Config files and DB schema have no mutual dependency. |
| **Ingestion modules** | M10 + M11 | Each implements the same interface for a different source. No shared code. |
| **Scoring sub-modules** | M13 + M14 (after M12 completes) | N-1 margin and escalation composite read domain scores but not each other. |
| **Cascade + features** | M16 + M18 (after M12 + M15 complete) | Cascade engine and feature pipeline read topology and scores but not each other. |
| **API route groups** | M23 + M24 + M25 + M26 (after M22 completes) | Each route group is a separate file wiring a separate engine. |
| **Dashboard views** | M31 + M32 + M33 + M34 + M35 (after M30 completes) | Each view is independent. |

### Missions requiring human review

| Mission | Review focus |
|---|---|
| **M02** (configs) | Are the topology, domain definitions, and weights correct? This defines the analytical model. |
| **M12** (scoring) | Do domain scores make intuitive sense for known disruption periods? |
| **M16** (cascade) | Do cascade outputs match documented real-world impacts? |
| **M28** (backtest notebook) | Is the analysis honest, clear, and reproducible? Would a faculty reviewer accept it? |
| **M31** (Global Overview) | Is the dashboard visually clear and professionally appropriate? |

### Missions likely to create rework if done too early

| Mission | Risk | When to start |
|---|---|---|
| **M36** (visual polish) | Polishing views that change structurally wastes time. | After all 5 views functionally render. |
| **M20** (alert thresholds) | Thresholds set before seeing actual score distributions will be wrong. | After M12 produces real scores. Adjust thresholds based on observed distributions. |
| **M06** (Pydantic schemas) | Schemas defined before engines are built may not match actual output shapes. | Acceptable to define early as aspirational contracts, but expect minor revisions during M23–M26. |
| **M29** (documentation) | Methodology docs written before backtest results will need rewriting. | After M28 (backtest notebook) is complete. |

### Best checkpoints for artifact review

| Checkpoint | After mission | What to review | Decision |
|---|---|---|---|
| **CP1: Foundation locked** | M07 | Config files, DB schema, seed data quality, test fixtures | Proceed to engines or fix foundation issues |
| **CP2: Scoring validated** | M12 | Domain scores for known periods — do numbers make sense? | Adjust weights/indicators or proceed |
| **CP3: Cascade validated** | M16 | Cascade outputs vs. documented event impacts | Architecture is sound or needs revision |
| **CP4: Model assessed** | M21 | Brier score, leave-one-out results | Model is usable, or fall back to rules-only + honest documentation |
| **CP5: Backtest complete** | M28 | Full validation narrative | Proceed to dashboard, or revisit model |
| **CP6: Dashboard functional** | M35 | All 5 views rendering with real data | Proceed to polish, or fix integration issues |
| **CP7: Ship** | M38 | Full system running, README tested, deployed | Release |

---

*End of Antigravity Mission Program v1.0. Execute missions in order. Do not skip checkpoints. Do not begin Phase N+1 before Phase N gate passes.*
