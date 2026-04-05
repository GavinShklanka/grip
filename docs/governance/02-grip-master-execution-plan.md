# GRIP — Master Execution Plan

## Reconciled Build Specification · v1.0

**Predecessor documents:**
1. GRIP Build Brief (this session, Doc 1)
2. GRIP Product Specification (this session, Doc 2)
3. Claude Operating Pack (imported from OpenAI session)
4. Baltic-Nordic Energy Corridor Research Sourcebook (imported from OpenAI session)

**Purpose:** Reconcile all four documents into a single, execution-grade plan. Resolve contradictions. Eliminate redundancy. Identify gaps. Produce a phased build sequence with acceptance criteria.

**Date:** April 2026

---

# A. Executive Synthesis

## What changed

The Baltic research sourcebook transforms GRIP from a well-framed but data-hypothetical platform into a concretely buildable system. Four things are now confirmed that were previously assumed:

1. **The region is decided.** The Baltic-Nordic energy corridor (Finland → Estonia → Latvia → Lithuania) has the best combination of data transparency, infrastructure legibility, and empirical disruption events of any candidate region. This is not a preference — it is the analytically strongest choice.

2. **The forecast target is decided.** Submarine interconnector disruption probability over a 30-day horizon, measured against the six confirmed energy-interconnector disruption events (2023–2026). This target has a defined outcome variable, timestamped historical episodes, and traceable precursor signals in ENTSO-E and ENTSOG flow data.

3. **The dependency graph has physical structure.** The Baltic corridor is a serial chain, not an abstract network. Finland feeds Estonia via Estlink. Estonia feeds Latvia via 330 kV lines and gas pipeline. Latvia feeds Lithuania and provides storage via Inčukalns. Lithuania connects laterally to Sweden (NordBalt), Poland (LitPol, GIPL), and global LNG (Klaipėda). This topology is the DAG. It does not need to be invented — it needs to be encoded.

4. **Backtesting is feasible.** Twelve documented infrastructure disruptions between 2022–2026 provide before/during/after signals in structured API data. The Balticconnector damage (Oct 2023), Estlink 2 severance (Dec 2024), and Kiisa battery trip (Jan 2026, both Estlinks lost simultaneously) are the cleanest validation cases. This eliminates the "how do we validate?" problem that sinks most geopolitical risk projects.

## What was wrong in the prior documents

| Prior assumption | Correction | Impact |
|---|---|---|
| MVP covers 3 regions | **1 region.** Three regions triples data-engineering work with no analytical depth gain. The Operating Pack was right to force this. | Halves build time. Doubles depth. |
| 11 generic domains, uniformly weighted | **8 active domains, regionally calibrated.** Humanitarian/continuity strain and resource competition are low-signal for Baltic NATO states. Sovereignty pressure and infrastructure vulnerability are high-signal. | Removes two domains that would produce near-zero scores and distract from the real risk structure. |
| Dependency DAG edges estimated from "historical co-movement" | **DAG is the physical infrastructure topology.** The serial chain Finland→Estonia→Latvia→Lithuania, with lateral connections, is not a statistical estimate — it is an engineering fact. Edge weights represent transmission capacity, not correlation coefficients. | Eliminates the hardest calibration problem identified in the build brief. The graph is deterministic at the topology level; only disruption probabilities are stochastic. |
| Backtesting against "one historical crisis (Russia-Ukraine 2021–22)" | **Backtesting against 12 specific infrastructure events (2022–2026) with timestamped flow data.** The Russia-Ukraine pre-invasion timeline is useful for geopolitical signal validation but the Baltic interconnector events are superior for the core forecast target. The Jan 2026 Kiisa battery trip adds an endogenous-failure case. | Validation plan is now concrete, not aspirational. |
| Data sources listed generically (ACLED, GDELT, World Bank, EIA) | **Specific APIs with Python wrappers, free tiers, update cadences, and known limitations.** ENTSO-E + ENTSOG are the backbone. GDELT via BigQuery. Copernicus for weather. AISStream for maritime. | Data-engineering scope is now estimable. No more "we'll figure out the APIs later." |

## What the Operating Pack got right

The Operating Pack's scope discipline is correct and should be treated as binding: one region, one forecast target, 4–6 scenario classes, validation-first. The prompt chain is well-sequenced but is process tooling, not product architecture — it should be used to guide Claude sessions during build, not incorporated into the system itself. The recommended forecast target (supply-route disruption probability) aligns with the research findings.

## What the Operating Pack got wrong or left vague

The Operating Pack treats the project as a "simulator" in its framing language but the strongest version of GRIP is a **monitoring and risk-assessment platform with simulation capability** — not a simulator with monitoring bolted on. The primary value is continuous situational awareness; scenario simulation is the secondary analytical layer. This distinction matters for dashboard hierarchy and data-pipeline priority.

---

# B. Confirmed Requirements

These are established by cross-referencing all four documents and are treated as fixed.

### B1. Region: Baltic-Nordic Energy Corridor

- **Countries:** Finland, Estonia, Latvia, Lithuania
- **Context countries** (not scored, but modeled as external nodes): Sweden, Poland, Russia, Germany
- **Chokepoints:** Gulf of Finland (Estlink cables, Balticconnector), Baltic Sea (NordBalt, C-Lion1), LitPol Link crossing
- **Corridors:** North-South electricity chain, North-South gas chain, East-West LNG supply (Klaipėda, Inkoo FSRUs), Poland gas/electricity interconnection (GIPL, LitPol)

### B2. Primary Forecast Target

**Probability of critical interconnector disruption within a 30-day rolling window.**

| Attribute | Definition |
|---|---|
| Target variable | Binary: did any critical interconnector (Estlink 1, Estlink 2, NordBalt, Balticconnector, LitPol Link) experience an unplanned outage of ≥24 hours within the forecast window? |
| Horizon | 30 days rolling |
| Features | AIS vessel anomaly signals (proximity, speed, AIS gaps), weather severity (Copernicus wind/wave/ice), GDELT event intensity (Baltic + Russia), diplomatic tension indicators, shadow-fleet vessel count in Baltic, prior-incident recency, seasonal factors, ongoing outage count (N-1 margin status) |
| Baseline | Naive base rate: ~6 major interconnector events in ~42 months (May 2022–Jan 2026) ≈ ~14% per 30-day window. Any model must beat this. |
| Validation | Leave-one-out cross-validation on the 6 major interconnector events (including Jan 2026 Kiisa trip). Brier score. Reliability diagram. |
| Uncertainty | 80% and 95% prediction intervals. Explicit "LOW CONFIDENCE" flag when feature coverage is poor. |

### B3. Secondary Analytical Targets (Descriptive + Scenario, Not Forecasted)

| Target | Type | Method |
|---|---|---|
| Composite energy security index per country | Descriptive, updated daily | Weighted composite (Augustis ESL model structure) |
| Grid stability margin (N-1 compliance) | Descriptive, updated hourly | ENTSO-E flow data vs. installed capacity minus outages |
| Sanctions pressure score | Descriptive, updated daily | OpenSanctions entity count + Eurostat trade volume delta |
| Cascade impact of interconnector loss | Scenario simulation | DAG propagation: remove edge, recalculate capacity margins and price impact |
| Multi-failure stress test | Scenario simulation | Remove 2+ edges simultaneously, assess grid survival |
| Alliance burden shift under stress | Descriptive + scenario | Defense spending trends + exercise frequency + commitment scores |

### B4. Scenario Classes (6)

| # | Scenario | What it models | Key override |
|---|---|---|---|
| 1 | **Submarine cable severance** | Single Estlink or NordBalt loss | Remove one cable edge; recalculate capacity margins |
| 2 | **Pipeline disruption** | Balticconnector or GIPL damage | Remove gas edge; assess storage drawdown timeline |
| 3 | **Multi-infrastructure attack** | Eagle S-style simultaneous cable + telecom damage | Remove 2–3 edges; assess compound grid stress |
| 4 | **Energy supply shock** | LNG disruption or extreme weather reducing generation | Override supply nodes; cascade through chain |
| 5 | **Sanctions escalation** | New tranche affecting Baltic transit trade or energy imports | Override trade/sanctions indicators; cascade to infrastructure stress |
| 6 | **LitPol Link failure** | Loss of sole synchronous Continental connection | Force Baltic island mode; assess frequency stability margins |

### B5. Technology Stack

| Layer | Choice | Rationale |
|---|---|---|
| Backend | **FastAPI (Python)** | Async, lightweight, good for API + data pipeline. Consistent with your existing Python/FastAPI experience (Klara). |
| Database | **PostgreSQL** | Time-series queries, JSON support for config, production-grade. SQLite acceptable for seed-data demo mode. |
| Ingestion | **Python scripts per source** with `entsoe-py`, `entsog-py`, `cdsapi`, BigQuery client, `httpx` for REST APIs | Each source is a separate module. Batch scheduling via cron or manual trigger for MVP. |
| Scoring | **Python modules** (numpy, pandas, scikit-learn) | Composite indices, classification, time-series |
| Simulation | **NetworkX** for DAG + custom propagation logic | The dependency graph is small enough (~20 nodes, ~30 edges) that NetworkX is sufficient. No need for graph databases. |
| Frontend | **React + Vite + Tailwind** | Consistent with your existing React experience. Recharts for charts. React Flow or custom SVG for the infrastructure topology diagram. |
| Deployment | **Railway** (or Vercel frontend + Railway backend) | Consistent with your Klara deployment experience. Docker optional but recommended for reproducibility. |

### B6. Defensive Boundaries (Carried Forward, Unchanged)

All boundaries from the Build Brief Section 6 remain in force. Military data enters only as aggregate strategic indicators (defense spending %, exercise frequency, reserve ratios). No unit-level, operational, or tactical content.

---

# C. Inferred Requirements

These are not explicitly stated in any source document but are logically necessary.

| # | Requirement | Basis for inference | Confidence |
|---|---|---|---|
| C1 | The DAG must support **temporal edge states** — an edge can be active, degraded, or severed, with a timestamp for each state change | The backtesting events require modeling cables as operational/damaged/repaired over time | High |
| C2 | The system needs a **"current outage register"** tracking which interconnectors are currently offline | Estlink 2 was offline for 16 of 24 months in 2024–2025; this is not an event, it is a persistent state | High |
| C3 | **Weather data must be joined to infrastructure vulnerability scoring** | Multiple disruption events involved storm conditions (anchor dragging, wave damage); Copernicus data enables this | High |
| C4 | The **shadow fleet** requires a dedicated tracking indicator | Eagle S and Yi Peng 3 were both shadow fleet or Russia-linked vessels; AISStream data can flag vessels by registry, insurance status, and behavioral anomalies | High |
| C5 | **Electricity price data** should be a consequence indicator, not a risk indicator | Price spikes are the result of disruptions, not predictors of them. Displaying post-disruption price impact validates the model's relevance. | Medium |
| C6 | The system needs a **capacity margin calculator** that runs in real-time on ENTSO-E data | Post-BRELL, the N-1 margin is the single most important operational metric for Baltic grid stability. Showing this requires continuous flow data minus known outages. | High |
| C7 | **Telecom cable damage** should be tracked alongside energy cables | The Yi Peng 3 and Eagle S events damaged telecom cables simultaneously. A "communications stress" indicator based on known cable status is warranted. | Medium |

---

# D. Missing Requirements / Ambiguities

These must be resolved before build proceeds.

| # | Gap | Impact if unresolved | Proposed resolution | Owner |
|---|---|---|---|---|
| D1 | **ENTSO-E API key approval takes ~3 days.** Has Gavin registered? | Cannot begin energy data ingestion without it. Everything downstream is blocked. | Register immediately. Use seed data from Fingrid Open Data (no approval needed) as interim fallback. | Gavin |
| D2 | **AISStream.io provides live data only — no historical archive.** How do we get AIS data for the 2023–2024 events for backtesting? | Cannot include vessel-proximity features in the backtesting classifier without historical AIS. | Use published investigation reports (vessel names, timestamps, coordinates are public) as structured event records. Do not attempt to reconstruct full AIS histories. Accept that the vessel-proximity feature will be live-only, not backtestable. Document this limitation. | Architect decision |
| D3 | **The risk model has ~6 positive energy-interconnector events in ~42 months (Oct 2023–Jan 2026).** This is still a small-sample problem. | Any standard classifier risks overfitting. | Frame the model as a **risk score** (logistic regression with calibrated probabilities), not a binary classifier. Use the 6 events for leave-one-out validation. Report Brier score and reliability diagram. Be explicit that this is an indicative model, not a validated predictor. Supplement with a rule-based alert system (e.g., "shadow fleet vessel within 5 nm of cable" triggers watch). The Jan 2026 Kiisa event adds an endogenous-failure positive case, improving model diversity. | Architect decision |
| D4 | **LitPol Link commercial capacity post-BRELL (~150 MW) vs. pre-BRELL (500 MW).** Which value should the model use as "normal"?** | Affects the N-1 margin calculation and scenario impact sizing. | Use post-BRELL values as the new baseline. Pre-BRELL values are historical context only. Document the regime change explicitly. | Data decision |
| D5 | **The Operating Pack recommends "one forecasting/risk-scoring module." The Product Spec proposed ARIMA on domain scores + GBM classifier.** Which is it? | Scope ambiguity. Building both is feasible but doubles the forecasting workload. | Build **one primary model**: the interconnector disruption risk score (logistic regression). Add ARIMA on the composite energy security index as a secondary, lightweight module only if time permits. The disruption risk score is the portfolio centerpiece; the ARIMA trend line is a commodity feature. | Scope decision: primary model only for MVP |
| D6 | **How should the "strategic readiness" layer (Layer 3) be populated?** SIPRI data is annual. Defense spending moves slowly. | Layer 3 risks being a static display with no analytical value. | Populate with the indicators that actually change: NATO exercise frequency (from GDELT event coding), border-force deployment signals (GDELT), defense-spending commitment announcements (GDELT), and alliance voting alignment (UN General Assembly roll calls via public datasets). Accept that this layer updates weekly-to-monthly, not daily. Label it accordingly. | Design decision |
| D7 | **What is the deployment target for the MVP demo?** Local only? Railway? GitHub Pages for frontend + Railway for API? | Affects Docker configuration, environment variable management, and build-script design. | Railway for full-stack (FastAPI + React), consistent with Klara deployment. GitHub Pages is insufficient — it cannot serve a Python API. | Infrastructure decision |

---

# E. Proposed System Architecture

## E1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                      │
│  Overview │ Regional │ Scenario │ Forecast │ Methodology      │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API (JSON)
┌─────────────────────▼───────────────────────────────────────┐
│                     FASTAPI BACKEND                          │
│                                                              │
│  ┌──────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐  │
│  │ State    │  │ Scenario  │  │ Forecast  │  │ Meta     │  │
│  │ Routes   │  │ Routes    │  │ Routes    │  │ Routes   │  │
│  └────┬─────┘  └─────┬─────┘  └─────┬─────┘  └────┬─────┘  │
│       │              │              │              │         │
│  ┌────▼──────────────▼──────────────▼──────────────▼─────┐  │
│  │                 ANALYTICAL ENGINE                       │  │
│  │                                                        │  │
│  │  ┌────────────┐  ┌────────────┐  ┌─────────────────┐  │  │
│  │  │ Scoring    │  │ Simulation │  │ Risk Model      │  │  │
│  │  │ Engine     │  │ Engine     │  │ (LogReg + Rules)│  │  │
│  │  │            │  │            │  │                 │  │  │
│  │  │ - Domain   │  │ - DAG      │  │ - Feature eng.  │  │  │
│  │  │   composit.│  │ - Cascade  │  │ - Calibration   │  │  │
│  │  │ - N-1 calc │  │ - Override │  │ - Brier scoring │  │  │
│  │  │ - Anomaly  │  │ - Compare  │  │ - Alert rules   │  │  │
│  │  └─────┬──────┘  └─────┬──────┘  └────────┬────────┘  │  │
│  │        │               │                   │           │  │
│  │  ┌─────▼───────────────▼───────────────────▼────────┐  │  │
│  │  │              DATA ACCESS LAYER                    │  │  │
│  │  │  PostgreSQL (time-series, scores, forecasts)      │  │  │
│  │  │  JSON configs (weights, thresholds, DAG edges)    │  │  │
│  │  └──────────────────────┬────────────────────────────┘  │  │
│  └─────────────────────────┼───────────────────────────────┘  │
└────────────────────────────┼──────────────────────────────────┘
                             │
┌────────────────────────────▼──────────────────────────────────┐
│                    INGESTION LAYER (Batch)                     │
│                                                               │
│  entsoe.py │ entsog.py │ gdelt.py │ copernicus.py │ ...      │
│  (cron or manual trigger)                                     │
└───────────────────────────────────────────────────────────────┘
```

## E2. Repository Structure

```
grip/
├── README.md
├── LICENSE
├── pyproject.toml                       # Single Python project config
├── docker-compose.yml                   # PostgreSQL + backend + frontend
├── .env.example                         # API keys template
│
├── docs/
│   ├── methodology.md                   # Scoring methodology
│   ├── data-dictionary.md               # Every indicator with source + cadence
│   ├── infrastructure-topology.md       # The physical DAG with diagrams
│   ├── backtesting-report.md            # Results of historical validation
│   ├── limitations.md                   # What the system cannot do
│   └── assumptions-register.md          # Living document, updated during build
│
├── data/
│   ├── seed/                            # Reproducible demo data (committed)
│   │   ├── entso_e_flows_2022_2026.csv
│   │   ├── entsog_flows_2022_2026.csv
│   │   ├── disruption_events.json       # The 12 backtesting anchors (2022–2026)
│   │   ├── infrastructure_topology.json # Nodes + edges of the physical DAG
│   │   └── domain_weights.json          # Default scoring weights
│   ├── raw/                             # Downloaded data (gitignored)
│   └── processed/                       # Cleaned data (gitignored)
│
├── config/
│   ├── domains.json                     # Domain definitions + indicator mappings
│   ├── topology.json                    # Infrastructure DAG: nodes, edges, capacities
│   ├── thresholds.json                  # Alert thresholds per domain
│   ├── scenarios/                       # Pre-built scenario override files
│   │   ├── estlink2_severance.json
│   │   ├── balticconnector_damage.json
│   │   ├── multi_cable_attack.json
│   │   ├── lng_supply_shock.json
│   │   ├── sanctions_escalation.json
│   │   └── litpol_failure.json
│   └── backtest/
│       └── events.json                  # Ground-truth event definitions for validation
│
├── backend/
│   ├── main.py                          # FastAPI app entry point
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── base.py                      # Abstract ingestion interface
│   │   ├── entso_e.py                   # ENTSO-E electricity flows + outages
│   │   ├── entsog.py                    # ENTSOG gas flows
│   │   ├── gdelt.py                     # GDELT event counts + tone via BigQuery
│   │   ├── opensanctions.py             # Sanctions entity tracking
│   │   ├── copernicus.py                # Weather conditions (wind, wave, ice)
│   │   ├── ais.py                       # AISStream vessel monitoring (live only)
│   │   ├── eurostat.py                  # Trade volumes
│   │   └── static.py                    # SIPRI, alliance data (manual refresh)
│   ├── scoring/
│   │   ├── __init__.py
│   │   ├── domain_index.py              # Per-domain composite scoring
│   │   ├── energy_security.py           # Augustis ESL-style composite
│   │   ├── n1_margin.py                 # Grid capacity margin calculator
│   │   ├── anomaly.py                   # Z-score anomaly detection on domain scores
│   │   └── sanctions_pressure.py        # Sanctions-specific scoring
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── topology.py                  # Infrastructure DAG (NetworkX)
│   │   ├── cascade.py                   # Edge removal → capacity recalculation
│   │   ├── scenario_engine.py           # Apply overrides, run cascade, return delta
│   │   └── comparator.py               # Side-by-side current vs. simulated state
│   ├── forecasting/
│   │   ├── __init__.py
│   │   ├── features.py                  # Feature engineering for risk model
│   │   ├── risk_model.py                # Logistic regression disruption risk score
│   │   ├── alert_rules.py               # Rule-based alert triggers (vessel proximity, etc.)
│   │   ├── calibration.py               # Brier score, reliability diagram
│   │   └── backtest.py                  # Leave-one-out validation harness
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes_state.py              # Current scores, flows, margins
│   │   ├── routes_topology.py           # Infrastructure graph data
│   │   ├── routes_scenario.py           # Run/compare scenarios
│   │   ├── routes_forecast.py           # Risk scores, alerts, confidence
│   │   └── routes_meta.py              # Assumptions, data quality, methodology
│   ├── db/
│   │   ├── models.py                    # SQLAlchemy models
│   │   ├── session.py                   # DB connection management
│   │   └── migrations/                  # Alembic migrations
│   └── utils/
│       ├── normalization.py             # Min-max, z-score, percentile functions
│       ├── temporal.py                  # Timestamp alignment, carry-forward logic
│       └── quality.py                   # Data freshness + coverage scoring
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── api/                         # API client hooks
│       │   └── client.js
│       ├── components/
│       │   ├── GlobalOverview/          # Region summary + alert feed
│       │   ├── InfrastructureMap/       # Topology diagram with live status
│       │   ├── CountryDetail/           # Per-country domain radar + sparklines
│       │   ├── EnergyPanel/             # Cross-border flows + capacity margins
│       │   ├── ScenarioWorkspace/       # Builder + cascade trace + comparison
│       │   ├── RiskPanel/               # Disruption risk score + alerts
│       │   ├── MethodologyPanel/        # Assumptions, sensitivity, backtest results
│       │   └── common/                  # Shared UI components
│       ├── hooks/
│       ├── utils/
│       └── styles/
│
├── notebooks/
│   ├── 01_data_exploration.ipynb        # Source inspection + quality assessment
│   ├── 02_topology_construction.ipynb   # Building the infrastructure DAG
│   ├── 03_scoring_calibration.ipynb     # Domain weight sensitivity analysis
│   ├── 04_disruption_backtest.ipynb     # The core validation notebook
│   └── 05_scenario_analysis.ipynb       # Pre-built scenario impact analysis
│
└── tests/
    ├── test_scoring.py
    ├── test_topology.py
    ├── test_cascade.py
    ├── test_risk_model.py
    └── test_api.py
```

## E3. The Infrastructure DAG — Concrete Definition

This replaces the abstract "dependency_edges" table from the Product Spec with the actual physical topology.

### Node Types

| Type | Examples | Attributes |
|---|---|---|
| `country` | FI, EE, LV, LT, SE, PL, RU, DE | generation_capacity_mw, consumption_mw, gas_demand_bcm |
| `interconnector` | Estlink 1, Estlink 2, NordBalt, LitPol Link, Balticconnector, GIPL, Estonia-Latvia lines | type (electric/gas), capacity, status (active/degraded/offline), vulnerability_score |
| `facility` | Klaipėda LNG, Inkoo FSRU, Inčukalns UGS, Olkiluoto 3, Narva oil shale | type, capacity, current_output, criticality |

### Edge Types

| Edge | From → To | Capacity | Current constraint |
|---|---|---|---|
| Estlink 1 | FI → EE | 358 MW | Active |
| Estlink 2 | FI → EE | 650 MW | **Operational** (repaired June 2025; returned to commercial use 25 June 2025) |
| NordBalt | SE → LT | 700 MW | Active (suspected anchor damage Jan 2025; verify current status) |

**Critical update (discovered during build planning, April 2026):** On 20 January 2026, both Estlink 1 and Estlink 2 tripped simultaneously due to a battery storage testing fault at the Kiisa facility near Tallinn. This caused a ~1,000 MW loss (20% of Baltic winter load). The LitPol Link to Poland compensated at double its rated capacity. This is a **12th backtesting event** — and uniquely, it is an endogenous grid-stability failure rather than an external attack, demonstrating that post-BRELL fragility extends beyond sabotage scenarios.
| LitPol Link | PL → LT | 500 MW (rated); ~200–365 MW commercial (2026) | Active, sole synchronous AC link. Capacity ramping post-BRELL. |
| EE-LV electric | EE → LV | ~1,400–1,600 MW (3×330 kV) | Active |
| LV-LT electric | LV → LT | ~1,200 MW | Active |
| Balticconnector | FI → EE (gas) | ~7.2 mcm/day | Active (repaired Apr 2024) |
| GIPL | PL → LT (gas) | ~6.5 mcm/day (2.4 bcm/yr) | Active |
| Klaipėda LNG | Global → LT (gas) | ~3.75 bcm/yr | Active |
| Inkoo FSRU | Global → FI (gas) | ~5 bcm/yr | Active |
| Inčukalns UGS | LV (storage) | 2.32 bcm active | Seasonal cycling |
| EE-LV gas | EE → LV | ~5.5 bcm/yr | Active |

### Cascade Logic

The simulation engine does not use abstract "propagation weights." It uses **capacity arithmetic:**

1. User removes or degrades an edge (e.g., Estlink 2 offline).
2. The engine recalculates available import capacity for each country.
3. The engine compares available capacity to demand.
4. The engine computes the **capacity deficit or margin** for each country.
5. If margin < 0, the country is in deficit. If margin < reserve requirement (~1,500 MW for Baltic grid stability), the system flags N-1 violation.
6. Price impact is estimated from historical price elasticity during past disruptions.

This is deterministic engineering math, not stochastic simulation. It is more defensible, more explainable, and more buildable than the abstract DAG propagation model in the prior spec.

---

# F. Phased Execution Plan

## Phase 0: Foundation (Days 1–3)

**Objective:** API access confirmed, seed data loaded, database schema deployed, repo initialized.

| Task | Output | Acceptance criteria | Risk |
|---|---|---|---|
| Register for ENTSO-E API key | API key in `.env` | Can query FI-EE cross-border flows | 3-day approval lag |
| Register for GDELT BigQuery | Service account JSON | Can run test query | Free tier confirmed |
| Register for Copernicus CDS | API key | Can download ERA5 Baltic subset | None |
| Register for AISStream.io | API key | Can connect WebSocket, receive Baltic AIS | None |
| Initialize repo with structure above | `grip/` on GitHub | All directories exist, README drafted | None |
| Deploy PostgreSQL (local Docker) | Running DB | Can connect, run migrations | None |
| Create SQLAlchemy models from schema | `backend/db/models.py` | All tables from Section 3 of Product Spec, adapted to Baltic | None |
| Build and load seed data | `data/seed/` populated | 2022–2026 ENTSO-E cross-border flow CSVs for FI-EE, EE-LV, LV-LT, SE-LT, PL-LT | This is the long-pole task. Pull data from ENTSO-E transparency portal manually if API is not yet approved. |
| Define infrastructure topology JSON | `config/topology.json` | All nodes and edges from E3 above, with capacities | None |
| Define disruption events JSON | `config/backtest/events.json` | 12 events with start date, end date, affected infrastructure, severity | None |

**Phase 0 deliverable:** A repo with seed data, a running database, and confirmed API access. No application code yet.

---

## Phase 1: Scoring Engine (Days 4–7)

**Objective:** Domain composite scores are computable for all 4 countries from seed data.

| Task | Output | Acceptance criteria |
|---|---|---|
| Implement `ingestion/entso_e.py` | Cross-border flow data in DB | Hourly FI→EE, EE→LV, LV→LT, SE→LT, PL→LT flows loading correctly |
| Implement `ingestion/entsog.py` | Gas flow data in DB | Daily Balticconnector, GIPL, Klaipėda, Inčukalns flows loading correctly |
| Implement `scoring/n1_margin.py` | Per-country capacity margin | Given current flows + known outages, calculate MW margin for each country. Validate against Estlink 2 outage period (should show ~65% capacity reduction FI→EE). |
| Implement `scoring/domain_index.py` | Per-country domain scores (0–100) | At least 5 domains scoring from real indicators: `energy_dependence`, `infrastructure_vulnerability`, `supply_route_disruption`, `trade_dependency`, `sanctions_pressure` |
| Implement `scoring/anomaly.py` | Anomaly flags | Scores > 2 SD from 30-day mean flagged |
| Write `tests/test_scoring.py` | Passing tests | Domain scores within expected ranges for known-good periods and known-disruption periods |

**Phase 1 deliverable:** Running scoring engine that produces daily domain scores for FI, EE, LV, LT from real data.

---

## Phase 2: Infrastructure DAG + Scenario Engine (Days 8–12)

**Objective:** Scenarios can be defined, executed, and compared.

| Task | Output | Acceptance criteria |
|---|---|---|
| Implement `simulation/topology.py` | NetworkX graph from `topology.json` | Graph loads, all edges have capacity attributes, can query neighbors and paths |
| Implement `simulation/cascade.py` | Edge-removal impact calculator | Remove Estlink 2 → returns capacity deficit for EE. Remove Balticconnector → returns gas supply impact for FI, EE. Results match documented real-world impacts. |
| Implement `simulation/scenario_engine.py` | Scenario runner | Load `scenarios/estlink2_severance.json`, apply overrides, run cascade, return full system state delta |
| Implement `simulation/comparator.py` | Side-by-side output | JSON response with current_state and simulated_state for all countries and all domains |
| Build 6 pre-built scenario files | `config/scenarios/*.json` | Each scenario has documented overrides and rationale |
| Write `tests/test_cascade.py` | Passing tests | Estlink 2 removal produces EE capacity deficit consistent with Dec 2024 event. Balticconnector removal produces FI gas supply impact consistent with Oct 2023 event. |

**Phase 2 deliverable:** Working scenario engine validated against two historical events.

---

## Phase 3: Risk Model + Backtesting (Days 13–18)

**Objective:** A calibrated disruption risk score with documented validation.

| Task | Output | Acceptance criteria |
|---|---|---|
| Implement `forecasting/features.py` | Feature matrix | Per-day feature vector: GDELT event intensity, weather severity, known outage count, days-since-last-incident, sanctions pressure score, seasonal indicators |
| Implement `forecasting/risk_model.py` | Logistic regression risk score | P(disruption within 30 days) per day. Trained on full 2022–2026 window with positive labels at the 6 major energy-interconnector events. |
| Implement `forecasting/alert_rules.py` | Rule-based alert layer | Deterministic triggers: "N-1 margin < threshold," "2+ interconnectors offline simultaneously," "shadow fleet vessel within cable proximity zone" |
| Implement `forecasting/backtest.py` | Leave-one-out validation | For each of the 6 major events: train on 5, test on 1. Report: did the model elevate risk score in the 30 days prior? |
| Implement `forecasting/calibration.py` | Brier score + reliability diagram | Quantitative performance metric. If model cannot beat naive base rate, document this honestly and rely on the rule-based layer. |
| Write `notebooks/04_disruption_backtest.ipynb` | Full backtesting narrative | The single most important notebook. Shows feature importance, model performance, calibration, and honest assessment of what works and what doesn't. |

**Phase 3 deliverable:** A risk score with documented backtesting. This is the portfolio centerpiece.

**Critical risk for Phase 3:** With only 6 positive events, the logistic regression may not converge or may overfit. The mitigation is the dual-layer approach: statistical model + rule-based alerts. If the statistical model fails, the rule-based layer still provides decision-relevant output, and the honest documentation of the statistical failure is itself analytically impressive. The Jan 2026 Kiisa event is analytically valuable because it is an endogenous failure (battery testing fault) rather than an external attack, testing whether the model can distinguish threat types.

---

## Phase 4: API Layer (Days 19–21)

**Objective:** All analytical outputs accessible via REST endpoints.

| Endpoint group | Key endpoints |
|---|---|
| `/api/state/` | `GET /scores` (all domain scores), `GET /scores/{country}`, `GET /margins` (N-1 capacity), `GET /flows` (current cross-border flows) |
| `/api/topology/` | `GET /graph` (full DAG as JSON), `GET /outages` (current infrastructure status) |
| `/api/scenario/` | `POST /run` (apply overrides, return simulated state), `GET /prebuilt` (list available), `GET /compare/{scenario_id}` (current vs. simulated) |
| `/api/forecast/` | `GET /risk` (current disruption probability), `GET /alerts` (active alerts), `GET /backtest` (validation results) |
| `/api/meta/` | `GET /assumptions`, `GET /data-quality` (freshness matrix), `GET /methodology` |

**Phase 4 deliverable:** All endpoints returning correct JSON. Tested with `pytest` + `httpx` async test client.

---

## Phase 5: Dashboard (Days 22–30)

**Objective:** Five views, each answering specific questions, each buildable in 1–2 days.

### View 1: Situation Board (Days 22–23)

**The 60-second view.** Four country cards ranked by composite risk. Each card: country name, composite score, 30-day sparkline, top-moving domain, N-1 margin status (green/amber/red). Bottom: alert feed (most recent threshold crossings). Top bar: last data refresh, data coverage %.

### View 2: Infrastructure Topology (Days 24–25)

**The GRIP differentiator view.** SVG or React Flow diagram of the physical infrastructure network. Nodes = countries + facilities. Edges = interconnectors with thickness proportional to capacity and color indicating status (green = active, amber = degraded, red = offline). Click an edge to see flow history sparkline and current utilization %. This view makes the serial-chain architecture immediately visible.

### View 3: Country Detail (Day 26)

Radar chart of domain scores for selected country. Ghost overlay of 30-day-ago values. Expandable indicator table per domain. Data-quality matrix.

### View 4: Scenario Workspace (Days 27–28)

Left: select pre-built or build custom (toggle edges on/off, adjust capacities). Right: simulated system state. Center: delta panel showing what changed and by how much. Bottom: cascade trace log.

### View 5: Risk & Methodology (Days 29–30)

Risk score gauge with confidence indicator. Alert timeline. Backtest results (the calibration plot from Phase 3, rendered as a chart). Assumptions register (scrollable, searchable). Sensitivity explorer (select any score, see weight-sensitivity sliders). Claim boundaries statement.

---

## Phase 6: Polish + Documentation (Days 31–35)

| Task | Output |
|---|---|
| Complete `docs/methodology.md` | Full scoring methodology with worked examples |
| Complete `docs/backtesting-report.md` | Narrative version of notebook 04 findings |
| Complete `docs/limitations.md` | Explicit, honest, detailed |
| Complete `docs/assumptions-register.md` | Every assumption with sensitivity rating |
| README: installation, setup, demo walkthrough | Reviewer can clone and run in <10 minutes |
| Dashboard visual polish | Consistent color system, typography, spacing. Command-room aesthetic without theatrics. |
| Deploy to Railway | Live URL | 

---

# G. Verification Plan

| What | Method | Pass criteria | When |
|---|---|---|---|
| Scoring engine accuracy | Compare domain scores during known-disruption vs. known-stable periods | Disruption periods score ≥ 20 points higher on relevant domains | Phase 1 |
| N-1 margin calculator | Compare calculated margin during Estlink 2 outage vs. documented 65% capacity reduction | Margin calculation within 10% of documented impact | Phase 1 |
| Cascade engine — Estlink 2 scenario | Run scenario, compare to documented Dec 2024 impacts | EE capacity deficit matches reported ~650 MW loss | Phase 2 |
| Cascade engine — Balticconnector scenario | Run scenario, compare to documented Oct 2023 impacts | FI gas supply impact matches 6.5-month ENTSOG zero-flow period | Phase 2 |
| Risk model — leave-one-out | For each of 6 events, did the model elevate risk in prior 30 days? | Elevated risk for ≥ 4 of 6 events (67% recall minimum) | Phase 3 |
| Risk model — calibration | Brier score on full test period | Brier score < naive base-rate Brier score (0.12 approx.) | Phase 3 |
| API correctness | `pytest` test suite against all endpoints | All tests pass, response schemas validated | Phase 4 |
| Dashboard data binding | Manual verification that displayed values match API responses | Zero discrepancies | Phase 5 |
| End-to-end backtest narrative | Notebook 04 runs from raw data to calibration plot without manual intervention | Fully reproducible | Phase 3 |

---

# H. Key Risks and Mitigation

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | **ENTSO-E API approval delayed >1 week** | Medium | High — blocks Phase 1 | Pre-download historical data from ENTSO-E web interface. Use Fingrid Open Data for FI-specific data in interim. |
| 2 | **Risk model fails to outperform base rate** | Medium | Medium — weakens forecast layer but does not kill project | Document failure honestly. Rely on rule-based alerts. Frame the backtesting notebook as a "what we learned" artifact. Honest failure analysis is more impressive than a faked success. |
| 3 | **Scope creep into additional regions or domains** | High | High — dilutes depth, extends timeline | This plan is the scope firewall. No additional regions until all 6 phases complete. |
| 4 | **Dashboard development absorbs remaining time** | High | High — displaces validation work | Phase 5 has a strict 9-day cap. If dashboard is incomplete, ship with 3 views instead of 5. Never sacrifice the backtest notebook for dashboard polish. |
| 5 | **NetworkX graph too simplistic for power-flow physics** | Low | Low — GRIP is a risk platform, not a power-systems simulator | Document that GRIP models capacity, not power flow. For actual grid stability analysis, reference ENTSO-E's own tools. This is a known and acceptable simplification. |
| 6 | **GDELT signal is too noisy for Baltic-specific risk scoring** | Medium | Medium — weakens geopolitical tension domain | Aggregate GDELT to weekly event counts and tone averages. Filter to Baltic + Russia + NATO actor codes. If signal-to-noise is poor after aggregation, downweight the domain and document why. |

---

# I. Questions That Must Be Answered Before Build Proceeds

These are blocking questions. Each must be resolved in the first 48 hours.

| # | Question | Who decides | Default if unresolved |
|---|---|---|---|
| 1 | Is ENTSO-E API registration submitted? | Gavin | Submit today. Use manual CSV download as fallback. |
| 2 | ~~Is Estlink 2 currently operational as of April 2026?~~ | **RESOLVED.** Repaired June 2025, returned to commercial use 25 June 2025. Both Estlinks tripped temporarily on 20 Jan 2026 due to Kiisa battery fault but were restored. Assume operational. | N/A |
| 3 | ~~What is the current LitPol Link commercial capacity?~~ | **RESOLVED.** Post-BRELL, commercial capacity was initially near zero (Feb 2025), gradually increasing. As of 2026: planned ~365 MW export / ~200 MW import, rising to 500/353 MW in 2027. The Jan 2026 Kiisa event demonstrated it can surge beyond rated capacity in emergencies. DC converter being decommissioned; LitPol now operates as synchronous AC. Use 200 MW import as conservative baseline for modeling. | N/A |
| 4 | Does the university provide BigQuery academic credits? | Gavin | Use GDELT DOC API (free, 3-month lookback) as alternative. Less powerful but zero-cost. |
| 5 | ~~Is the Harmony Link under construction yet?~~ | **RESOLVED.** Project was redesigned from offshore HVDC to overland 220 kV AC line (Ełk, Poland → Lithuania). Construction tenders launching 2026; completion targeted 2029–2030. Not operational. LitPol Link remains sole synchronous connection until then. **Design note:** Harmony Link being overland rather than submarine changes its vulnerability profile — less exposed to anchor-dragging but crosses the Suwałki Gap, NATO's most-discussed land chokepoint. Worth noting in scenario documentation. | N/A |
| 6 | Which deployment: Railway full-stack vs. local-only demo? | Gavin | Railway, consistent with Klara deployment experience. |
| 7 | Is this being submitted as an MBAN capstone, a portfolio project, or both? | Gavin | Treat as portfolio project with capstone-grade rigor. Adjust documentation depth accordingly. |

---

# Assumptions Register (Living Document — v1.0)

| # | Assumption | Layer | Sensitivity | Testable | Status |
|---|---|---|---|---|---|
| A1 | The Baltic serial chain topology is the correct DAG structure | Simulation | High | Yes — matches physical infrastructure maps | Confirmed (ICDS maps, ENTSO-E grid maps) |
| A2 | Post-BRELL LitPol commercial capacity is ~200–365 MW (2026), rising to ~500 MW in 2027 | Scoring | High | Yes — check ENTSO-E flow data | Confirmed via Xinhua/Litgrid Oct 2025 report |
| A3 | 6 energy-interconnector events are sufficient for leave-one-out validation | Forecasting | High | Partially — Brier score will reveal | Accepted risk; documented. Jan 2026 Kiisa event improves sample diversity. |
| A4 | GDELT event counts are a useful proxy for geopolitical tension | Scoring | Medium | Yes — backtest correlation with disruption events | Unknown; test in Phase 3 |
| A5 | Weather severity is a meaningful feature for disruption risk | Forecasting | Medium | Yes — check weather at time of each event | Unknown; test in Phase 3 |
| A6 | Domain weights can be set from literature (Augustis ESL) and adjusted via sensitivity analysis | Scoring | Medium | Yes — sensitivity analysis in Phase 1 | Assumed; validate |
| A7 | AISStream live data adds value despite lack of historical archive | Forecasting | Low (MVP) | No — live-only feature cannot be backtested | Accepted; live-only indicator, clearly labeled |
| A8 | The gas system is adequately redundant and should be weighted lower than electricity | Scoring | Medium | Yes — Balticconnector outage showed no shortages | Confirmed by Oct 2023 event outcome |
| A9 | GRIP's capacity-arithmetic cascade model is a sufficient approximation of grid behavior | Simulation | Medium | Partially — compare to documented real impacts | Accepted simplification; documented |
| A10 | Seed data from 2022–2026 provides sufficient historical depth (~4 years) for scoring baselines | Scoring | Low | Yes — check if 4-year baseline produces stable normalization | Assumed; validate in Phase 1 |

---

*End of Master Execution Plan v1.0. This document supersedes the Build Brief and Product Specification for all implementation decisions. Those documents remain valid as strategic context.*
