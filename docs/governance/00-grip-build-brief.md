# GRIP — Geopolitical Resilience Intelligence Platform

## Product Strategy & Technical Build Brief

**Author:** Gavin Shklanka · Black Point Analytics  
**Program:** MBAN 2026, Sobey School of Business, Saint Mary's University  
**Date:** April 2026  
**Classification:** Portfolio Capstone · Decision-Support System  
**Status:** Pre-build specification

---

## 0. Executive Summary

GRIP is a defensive geopolitical intelligence platform designed for crisis monitoring, resilience planning, escalation analysis, and sovereignty stress testing. It synthesizes structured open-source data into composite risk indices, dependency graphs, and scenario simulations — presented through a command-room dashboard interface.

The system answers one core question: **Given observable geopolitical signals, where are the pressure points, how fast are they moving, and what breaks if they escalate?**

GRIP does not model military operations, targeting, force deployment, or offensive strategy. It models consequences, dependencies, fragilities, and preparedness gaps at the infrastructure and strategic level.

---

## 1. Problem Statement

> Modern geopolitical risk is a **dependency-chain problem**. A sanctions package against one state propagates through energy markets, trade corridors, alliance structures, communications infrastructure, and humanitarian systems — often in non-obvious sequences and at non-linear rates.
>
> Existing public tools treat these domains in isolation: economic dashboards track sanctions; energy monitors track supply; conflict trackers count incidents. No accessible platform models the **cross-domain propagation of geopolitical pressure** as an integrated system.
>
> GRIP closes this gap by constructing a composite, dependency-aware risk model that tracks observable signals across 11 pressure domains, scores their individual and compound severity, simulates escalation pathways, and surfaces early-warning indicators — all within a defensive, consequence-analysis frame.

### What this is

A **decision-support and preparedness-assessment tool** for analysts who need to understand how geopolitical stress propagates across interconnected systems.

### What this is not

- Not a military planning system
- Not a real-time intelligence feed (it aggregates open-source data at near-real-time intervals)
- Not a prediction engine (it produces conditional risk scores and scenario outcomes, not point forecasts)
- Not a classified or proprietary system (all data sources are public)

---

## 2. Target Users and Decision Questions

### Primary User: The Builder (Gavin)

Decision questions:
- Can I design and ship a modular, data-intensive analytics platform end-to-end?
- Can I demonstrate prescriptive and predictive analytics at portfolio-grade quality?
- Can I model complex systems with defensible methodology?

### Secondary Users

| Audience | What they evaluate | Decision question they bring |
|---|---|---|
| **Government policy analyst** | Cross-domain risk propagation | "Which of our critical dependencies are most exposed to escalation in Region X?" |
| **Infrastructure resilience planner** | Chokepoint and supply-route stress | "If corridor Y degrades, what is the cascade timeline and what do we pre-position?" |
| **NGO / humanitarian coordinator** | Humanitarian consequence forecasting | "At what escalation level does displacement begin, and which corridors are still viable?" |
| **Corporate risk / supply chain analyst** | Trade-route and sanctions exposure | "How does a new sanctions tranche affect our supplier network in Region Z?" |
| **Faculty reviewer / hiring manager** | Technical depth and analytical rigor | "Does this demonstrate graduate-level applied analytics capability?" |

---

## 3. The Eleven Pressure Domains

These are the analytical dimensions GRIP monitors. Each domain is a scored index (0–100) built from observable indicators.

| # | Domain | What it measures | Example indicators |
|---|---|---|---|
| 1 | **Geopolitical Tension** | Diplomatic deterioration, rhetoric escalation, incident frequency | UN votes, ambassador recalls, diplomatic statements sentiment, border incidents |
| 2 | **Alliance Alignment** | Coalition cohesion or fragmentation | Joint exercise frequency, defense-pact commitments, voting alignment divergence |
| 3 | **Sanctions & Trade Pressure** | Economic coercion intensity and breadth | Sanctions count, trade-volume delta, tariff escalation, SWIFT disconnection events |
| 4 | **Energy Dependence** | Concentration risk in energy supply | Import-source HHI, reserve-to-consumption ratio, pipeline utilization, spot-price volatility |
| 5 | **Supply-Route Disruption** | Corridor viability and chokepoint stress | Maritime chokepoint transit volume, insurance-rate spikes, port congestion, airspace closures |
| 6 | **Critical Infrastructure Vulnerability** | Exposure of essential systems | Telecom redundancy, grid interconnection, water-system dependency, cyber-incident frequency |
| 7 | **Communications & Logistics Stress** | Information and transport network strain | Internet-backbone latency, freight-rate indices, cross-border transit delays |
| 8 | **Resource Competition** | Rivalry over critical inputs | Rare-earth concentration, agricultural-import dependency, water-scarcity indices |
| 9 | **Sovereignty Pressure** | External threats to self-governance | Territorial disputes active, foreign-base proximity, economic-leverage ratios |
| 10 | **Humanitarian & Continuity Strain** | Population-level consequence stress | Displacement forecasts, food-security indices, healthcare-system capacity, refugee-corridor viability |
| 11 | **Escalation Risk** | Composite probability of regime transition between tension levels | Compound index derived from domains 1–10 with temporal momentum weighting |

**Domain 11 is a second-order composite.** It does not have its own raw indicators — it is calculated from the trajectories and interactions of domains 1–10.

---

## 4. Platform Architecture — Six Analytical Layers

### Layer 1: Live Descriptive Intelligence

**Purpose:** Current-state awareness. "What is happening right now?"

**Components:**
- Per-domain index scores (0–100) refreshed on a defined cadence (hourly for API-fed indicators, daily for scraped/manual indicators)
- Regional and country-level aggregation
- Time-series trend lines (7-day, 30-day, 90-day)
- Anomaly flags: any domain score moving > 2 standard deviations from its 30-day rolling mean

**Data sources:** ACLED (conflict events), GDELT (media tone and event counts), World Bank / IMF (trade and economic indicators), EIA / IEA (energy), UN OCHA (humanitarian), Maritime AIS aggregates (chokepoints), IISS / SIPRI (military spending and arms transfers — aggregate only).

**Methodology:** Each domain score is a normalized weighted composite of its constituent indicators. Weights are documented, adjustable, and sensitivity-tested. Normalization uses min-max scaling against a 5-year historical baseline.

**What this layer claims:** "Based on these indicators, this is the observable state."  
**What it does not claim:** "This is the ground truth." All scores carry a data-freshness timestamp and source-coverage flag.

---

### Layer 2: Scenario Simulation

**Purpose:** Exploratory what-if analysis. "If X happens, what propagates?"

**Components:**
- User-defined scenario injection: override one or more domain scores or individual indicators
- Dependency-graph propagation: changes cascade through a directed acyclic graph (DAG) of cross-domain linkages
- Scenario comparison: side-by-side current-state vs. simulated-state
- Pre-built scenario library: "Strait of Hormuz closure," "SWIFT disconnection of State X," "Energy pipeline sabotage," "Alliance withdrawal by State Y"

**Methodology:** Cross-domain dependencies are modeled as a weighted adjacency matrix. Edge weights represent propagation strength (estimated from historical co-movement analysis and expert-informed priors). Propagation uses a damped cascade model — each hop attenuates by a configurable decay factor to prevent runaway amplification.

**What this layer claims:** "Given these assumed linkages, this is the modeled consequence."  
**What it does not claim:** "This will happen." Scenarios are exploratory tools, not forecasts.

---

### Layer 3: Forecasting & Early Warning

**Purpose:** Forward-looking risk estimation. "Where are things heading?"

**Components:**
- Per-domain 30/60/90-day risk trajectory (directional, not point-estimate)
- Composite escalation probability: likelihood of crossing defined severity thresholds
- Leading-indicator detection: which signals historically precede escalation in each domain
- Alert generation: configurable thresholds trigger watch/warning/critical notifications

**Methodology:**
- **Short-horizon (30-day):** Time-series models (ARIMA, exponential smoothing) on domain index histories. These are trend-continuation estimates, not causal predictions.
- **Medium-horizon (60–90 day):** Gradient-boosted classification of escalation probability, trained on historical episodes where domain scores crossed severity thresholds. Features include domain-score levels, velocities, accelerations, and cross-domain interaction terms.
- **Uncertainty:** All forecasts carry confidence intervals. The system distinguishes between "low uncertainty, high risk" and "high uncertainty, risk unknown" — the second is not the same as safety.

**What this layer claims:** "Based on historical patterns, this trajectory has X% probability of crossing threshold Y within Z days."  
**What it does not claim:** "This will happen by date D." No point predictions. No implied precision beyond what the model supports.

---

### Layer 4: Ranking & Prioritization

**Purpose:** Triage. "Where should attention go first?"

**Components:**
- **Regions ranked by composite risk score** (weighted average across 11 domains)
- **Domains ranked by rate-of-change** within a region (which pressure is accelerating fastest)
- **Chokepoint criticality ranking** (combines disruption probability with downstream impact breadth)
- **Dependency fragility ranking** (which bilateral or multilateral relationships have the highest single-point-of-failure exposure)

**Methodology:** Multi-criteria ranking using TOPSIS or weighted-sum aggregation with configurable weight profiles. Users can toggle between "balanced," "energy-focused," "humanitarian-focused," and "trade-focused" weighting schemes to reflect different institutional priorities.

**What this layer claims:** "Under this weighting scheme, these are the highest-priority items."  
**What it does not claim:** "This is objectively the most important thing." Rankings are weight-sensitive and the system makes this explicit.

---

### Layer 5: Dashboard & Command-Room Workflow

**Purpose:** Operational interface. "How do I use this in a briefing or monitoring session?"

**Components:** (Detailed in Section 9.)

Core UX principles:
- **Situation awareness, not decoration.** Every pixel must answer a question.
- **Glanceable severity.** Color-coding and spatial layout enable 5-second status assessment.
- **Drill-down on demand.** Top-level summary → region → domain → indicator → source.
- **Scenario workspace.** Dedicated panel for what-if construction and comparison.
- **Exportable briefing artifacts.** One-click PDF/PNG of current dashboard state for handoff.

**What this layer claims:** "This is a usable decision-support interface."  
**What it does not claim:** "This replaces a human analyst's judgment."

---

### Layer 6: Validation & Uncertainty

**Purpose:** Methodological transparency. "Why should anyone trust this?"

**Components:**
- **Data provenance panel:** For any displayed value, trace to raw source, retrieval timestamp, and transformation applied.
- **Sensitivity analysis:** For any composite score, show how it changes as individual weights or inputs shift ±10%, ±25%.
- **Historical backtesting:** For forecasting models, display calibration plots (predicted probability vs. observed frequency) and Brier scores.
- **Assumption registry:** Explicit documentation of every structural assumption in the model (e.g., "We assume sanctions propagate to energy markets within 7–21 days based on historical median").
- **Known-limitation flags:** Each domain carries a coverage score (0–100) indicating what percentage of ideal indicators are actually available.

**What this layer claims:** "Here is exactly how this number was produced, what it depends on, and where it might be wrong."  
**What it does not claim:** Certainty.

---

## 5. Scope: In vs. Out

### In Scope (MVP)

- 3–5 focus regions (e.g., Eastern Europe / Baltic, Indo-Pacific / Taiwan Strait, Middle East / Hormuz, Arctic, Sahel)
- All 11 domain indices with at least 3 real indicators each
- Cross-domain dependency DAG with documented edge weights
- Scenario simulation engine (user-defined + 5 pre-built scenarios)
- 30-day time-series forecasting per domain
- Escalation-probability classifier (historical training on at least one well-documented crisis sequence)
- Dashboard with global overview, regional detail, scenario workspace, and methodology panel
- Static data pipeline (batch-refresh, not streaming) with clear timestamps

### In Scope (Post-MVP)

- Live API ingestion (GDELT, ACLED, EIA) on automated schedule
- NLP sentiment pipeline on diplomatic communications / state media
- Network-graph visualization of alliance and trade dependencies
- Exportable briefing PDFs
- User-configurable alert thresholds
- Expanded region coverage

### Out of Scope (Permanently)

- Tactical or operational military modeling (unit positioning, force ratios, targeting, logistics optimization for military operations)
- Classified or non-public data integration
- Real-time streaming (sub-minute latency)
- Automated decision-making (the system recommends attention allocation, not actions)
- Country-internal political forecasting (election outcomes, regime-change probability)
- Cyber-offensive capability modeling
- Weapons-systems analysis

---

## 6. How "Military" Appears — and Where It Stops

| Permitted (strategic/aggregate) | Prohibited (tactical/operational) |
|---|---|
| Defense-spending trends by country | Unit deployments or order-of-battle |
| Arms-transfer volumes between states | Weapons-system specifications |
| Military-exercise frequency and scale | Exercise objectives or tactical scenarios |
| Alliance commitment indicators | Force-posture optimization |
| Conscription/mobilization signals as escalation indicators | Recruitment targeting or manpower planning |
| Nuclear-posture status (categorical: low/elevated/high) | Nuclear targeting, yield modeling, strike planning |
| Military spending as % of GDP trend | Budget allocation across branches |

**The rule:** Military data enters GRIP only as an input signal to strategic risk assessment. It is never the output. The system never answers "how should forces be deployed?" — it answers "what does this pattern of military activity imply for regional stability and infrastructure resilience?"

---

## 7. Strongest MVP Specification

### What ships first

A **React + Python** application with:

**Backend (FastAPI or Flask):**
- Data-ingestion module: batch scripts pulling from ACLED API, GDELT BigQuery (or pre-downloaded summaries), World Bank API, EIA API, and curated CSV baselines
- Index-computation engine: per-domain scoring with documented weights
- Dependency-propagation engine: adjacency-matrix cascade with configurable decay
- Scenario engine: accepts overrides, runs propagation, returns simulated state
- Forecast module: statsmodels ARIMA + scikit-learn gradient-boosted classifier for escalation probability
- API layer: RESTful endpoints serving current state, historical series, scenario results, and forecasts

**Frontend (React + Tailwind or a component library):**
- Global overview: world/region map with domain-composite heatmap overlay
- Regional detail: 11-domain radar chart + time-series sparklines + anomaly flags
- Scenario workspace: input panel + side-by-side comparison
- Methodology panel: assumption registry, sensitivity sliders, data-provenance drill-down
- Command bar / alert feed: prioritized watch items

**Data layer:**
- PostgreSQL or SQLite for structured time-series
- JSON config files for weights, thresholds, and dependency-graph edges
- Version-controlled seed data for reproducibility

### What makes it look advanced (while remaining buildable)

- The dependency DAG and cascade simulation — this is the differentiator. Most dashboards display; this one models propagation.
- Scenario comparison with uncertainty bands — shows analytical maturity.
- Sensitivity analysis on composite scores — demonstrates you understand your own model's limitations.
- Calibration plots on the forecasting module — proves you validate, not just predict.
- The assumption registry — signals intellectual honesty, which is rare and valued.

---

## 8. Repository & Application Architecture

```
grip/
├── README.md                          # Project overview, setup, methodology summary
├── LICENSE
├── docs/
│   ├── methodology.md                 # Full scoring methodology and assumptions
│   ├── data-dictionary.md             # Every indicator, source, refresh cadence
│   ├── dependency-model.md            # DAG structure, edge-weight justification
│   └── limitations.md                 # What the system cannot do and why
├── data/
│   ├── raw/                           # Unmodified source files (gitignored if large)
│   ├── processed/                     # Cleaned, normalized indicator tables
│   ├── seed/                          # Baseline data for reproducible demos
│   └── config/
│       ├── domain-weights.json        # Per-domain indicator weights
│       ├── dependency-graph.json      # Adjacency matrix with edge weights
│       ├── thresholds.json            # Alert thresholds per domain
│       └── scenarios/                 # Pre-built scenario definitions
│           ├── hormuz-closure.json
│           ├── swift-disconnect.json
│           └── ...
├── backend/
│   ├── app.py                         # FastAPI entry point
│   ├── ingestion/                     # Data-pull scripts per source
│   │   ├── acled.py
│   │   ├── gdelt.py
│   │   ├── eia.py
│   │   └── worldbank.py
│   ├── scoring/
│   │   ├── domain_index.py            # Per-domain composite scoring
│   │   └── escalation_composite.py    # Domain-11 compound scoring
│   ├── simulation/
│   │   ├── dependency_graph.py        # DAG construction and propagation
│   │   └── scenario_engine.py         # Override injection + cascade
│   ├── forecasting/
│   │   ├── timeseries.py              # ARIMA / exponential smoothing
│   │   ├── classifier.py              # Escalation-probability model
│   │   └── validation.py              # Backtesting, calibration, Brier scores
│   ├── ranking/
│   │   └── prioritization.py          # TOPSIS / weighted-sum ranking
│   └── api/
│       ├── routes_state.py            # Current-state endpoints
│       ├── routes_scenario.py         # Scenario simulation endpoints
│       ├── routes_forecast.py         # Forecast endpoints
│       └── routes_meta.py             # Methodology, provenance, sensitivity
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── GlobalOverview/        # Map + composite heatmap
│   │   │   ├── RegionalDetail/        # Radar + sparklines + anomalies
│   │   │   ├── ScenarioWorkspace/     # Simulation input + comparison
│   │   │   ├── ForecastPanel/         # Trajectory + probability + intervals
│   │   │   ├── RankingTable/          # Prioritized triage view
│   │   │   ├── MethodologyPanel/      # Assumptions, sensitivity, provenance
│   │   │   └── CommandBar/            # Alert feed + quick-nav
│   │   ├── hooks/                     # Data-fetching, state management
│   │   ├── utils/                     # Formatting, color scales, thresholds
│   │   └── styles/
│   ├── package.json
│   └── vite.config.js
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_indicator_analysis.ipynb
│   ├── 03_dependency_calibration.ipynb
│   ├── 04_forecast_validation.ipynb
│   └── 05_sensitivity_analysis.ipynb
├── tests/
│   ├── test_scoring.py
│   ├── test_propagation.py
│   ├── test_scenarios.py
│   └── test_forecasting.py
├── requirements.txt
└── docker-compose.yml                 # Optional: DB + backend + frontend
```

**Key repo-quality signals for reviewers:**
- `docs/` directory with real methodology, not just a README
- `data/config/` separates model parameters from code (auditable, adjustable)
- `notebooks/` shows the analytical work behind the engineering
- `tests/` exists and covers core logic
- Clean separation: ingestion → scoring → simulation → API → UI

---

## 9. Dashboard Views

### View 1: Global Situation Board (Default)

- **Center:** Choropleth or regional-block map. Each region colored by composite escalation-risk score. Color scale: green (stable) → amber (elevated) → red (critical).
- **Left rail:** Region ranking list sorted by composite score, with 7-day delta arrows.
- **Bottom strip:** Global alert feed — most recent threshold-crossing events, newest first.
- **Top bar:** System status (last data refresh timestamp, data-coverage %, active alerts count).

### View 2: Regional Deep-Dive

- **Center-left:** Radar chart of all 11 domain scores for the selected region. Overlaid with 30-day-ago ghost for trajectory context.
- **Center-right:** Stacked sparkline panel — one sparkline per domain, 90-day history, with anomaly markers.
- **Right panel:** Key indicators table — the 3–5 raw indicators driving the highest-scoring domains, with source links.
- **Bottom:** Leading-indicator timeline — which signals historically precede escalation in this region.

### View 3: Scenario Workspace

- **Left panel:** Scenario builder. Dropdown: select pre-built or "custom." For custom: sliders to override individual domain scores or indicators.
- **Center:** Side-by-side comparison. Current state (left) vs. simulated state (right). Radar charts, domain-score bars, and delta highlights.
- **Right panel:** Cascade trace. Step-by-step propagation log showing which domain changes triggered which downstream effects, with edge weights displayed.
- **Bottom:** Uncertainty band — for each propagated score, show the range given ±1 edge-weight standard deviation.

### View 4: Forecast & Early Warning

- **Center:** 30/60/90-day risk-trajectory charts per domain for selected region. Fan charts showing confidence intervals widening over time.
- **Right panel:** Escalation-probability gauge — current P(threshold crossing) with historical calibration context.
- **Bottom:** Alert configuration panel (for the builder's use; in portfolio mode, this shows the logic, not a live notification system).

### View 5: Methodology & Validation

- **Assumption registry:** Scrollable list of every structural assumption with justification and sensitivity flag.
- **Sensitivity explorer:** Select any composite score → interactive sliders showing how it responds to ±10/25% shifts in each input.
- **Calibration display:** For the escalation classifier — reliability diagram (predicted vs. observed), Brier score, ROC curve.
- **Data-coverage matrix:** Region × Domain grid showing indicator availability (green = full, yellow = partial, red = missing).

---

## 10. What You Are Missing as an Analyst

This section is blunt, as requested.

### Gaps to close

1. **Dependency-graph calibration is the hardest part.** You have the concept. You do not yet have a defensible method for setting edge weights. Options: (a) historical co-movement regression between domain indices, (b) structured expert elicitation documented as a Delphi process, (c) literature-anchored priors with explicit citation. You need at least one of these. "I estimated it" is not sufficient for MBAN-grade work.

2. **Base-rate problem for escalation forecasting.** Genuine geopolitical escalation events are rare. Your classifier will have a severe class-imbalance problem. You need to demonstrate awareness of this: discuss SMOTE or undersampling, use precision-recall curves instead of just accuracy, and show Brier scores. If the model can't beat a naive base-rate predictor, say so — that honesty is stronger than a bad model presented confidently.

3. **Source-reliability heterogeneity.** GDELT event counts are noisy. ACLED is curated but has coverage gaps. EIA data is solid but lagged. You must document source reliability per indicator and propagate that uncertainty into your composite scores. A domain score built on three strong indicators is not equivalent to one built on three weak indicators, even if the number is the same.

4. **Temporal alignment.** Your indicators update on different cadences (some hourly, some quarterly). When you composite them, you are mixing temporal resolutions. Document your interpolation/carry-forward strategy. "Latest available value" is acceptable if stated; it is not acceptable if hidden.

5. **You need a clear validation story.** Pick one or two historical crises (e.g., Russia-Ukraine pre-2022, Hormuz tensions 2019–2020). Backtest your model against them. Show: "Here is what the system would have scored at T-90, T-60, T-30. Here is what actually happened. Here is where the model was right and where it missed." This single exercise will do more for your credibility than any amount of dashboard polish.

6. **Scenario simulation is not the same as forecasting. You must never conflate them in the UI or documentation.** Simulation answers "what if X?" Forecasting answers "what is likely?" The first requires no probability claim. The second does. Mixing them is a common and serious analytical error.

7. **You are likely underestimating the data-engineering effort.** Pulling, cleaning, normalizing, and aligning data from 5+ heterogeneous APIs is 40–60% of the actual build time. Plan for this. The ingestion module is not a minor component — it is the foundation.

---

## 11. Claims the System Can Make vs. Must Not Make

### Can claim

- "Based on these indicators, the composite risk score for Region X is Y."
- "Domain Z has increased by N points over 30 days, crossing the elevated-risk threshold."
- "Under Scenario A, the model projects that Domain Z would propagate to Domain W with a modeled increase of M points, given the assumed dependency structure."
- "The 30-day trend-continuation estimate for Domain Z is [range] with [confidence level]."
- "The escalation classifier assigns P = X% probability of threshold-crossing within 30 days, with a historical Brier score of Y."
- "This composite score is most sensitive to Indicator K — a ±10% change in K produces a ±N change in the composite."

### Must not claim

- "War will / will not happen."
- "Country A will invade Country B."
- "This system predicts the future."
- "This score represents ground truth."
- "Military forces should be positioned at X" (or any operational recommendation).
- "Our model is validated" (without showing the validation metrics and their limitations).
- "This system is suitable for real-time crisis decision-making" (it is a portfolio project with batch data, not a production intelligence system).
- Any claim that implies certainty, omniscience, or operational authority.

---

## 12. Verdict: Is This MBAN-Grade?

**Yes — if executed with the rigor described in this brief.**

Here is the specific evaluation:

| MBAN Competency | How GRIP demonstrates it | Grade risk |
|---|---|---|
| **Data engineering** | Multi-source ingestion, cleaning, normalization, temporal alignment | Strong if the pipeline actually works end-to-end |
| **Descriptive analytics** | 11-domain composite index construction, anomaly detection, time-series visualization | Strong |
| **Predictive analytics** | Escalation-probability classifier, time-series forecasting | Medium — depends on honest treatment of base-rate problem and calibration |
| **Prescriptive analytics** | Scenario simulation, dependency-graph propagation, prioritization ranking | Strong — this is the differentiator |
| **Optimization** | TOPSIS ranking, weight-sensitivity analysis, dependency-graph structure as a constrained system | Adequate — not a pure optimization project, but optimization methods are applied |
| **Visualization / communication** | Command-room dashboard, exportable briefings, methodology transparency | Strong if dashboard is functional and not just decorative |
| **Domain expertise** | Geopolitical risk modeling, infrastructure-dependency analysis | Strong — the domain choice is ambitious and demonstrates intellectual range |
| **Methodological rigor** | Assumption registry, sensitivity analysis, backtesting, uncertainty quantification, limitation documentation | This is where GRIP either succeeds or fails. If the validation layer is real, this project is exceptional. If it's cosmetic, the project is a decorated dashboard. |

### The honest assessment

The concept is graduate-thesis-level ambitious. The MVP as specified is buildable by one person in 4–6 weeks of focused work if the data-engineering scope is managed tightly (3–5 regions, batch ingestion, seed data for demo mode). The analytical methods (composite scoring, time-series, classification, DAG propagation, TOPSIS) are all within MBAN curriculum range — but combining them into an integrated system is substantially harder than any individual assignment.

**What makes it portfolio-grade:** The dependency-propagation engine, the scenario simulator, the validation layer, and the intellectual honesty of the limitations documentation. These four elements together demonstrate systems-level analytical thinking — which is what separates a dashboard project from an intelligence platform.

**What could sink it:** Spending too much time on dashboard aesthetics and not enough on the scoring methodology, dependency calibration, and validation backtesting. The war-room look is the hook; the analytical engine is the substance.

**Final recommendation:** Build the engine first. Validate against one historical crisis. Then wrap it in the dashboard. If the engine is sound, the dashboard sells itself. If the engine is hollow, no amount of dark-mode styling will survive a competent reviewer's scrutiny.

---

## Appendix A: Terminology Discipline

| Term | GRIP usage | Prohibited usage |
|---|---|---|
| "Risk score" | Composite index derived from weighted indicators | Probability of a specific event |
| "Forecast" | Trend-continuation estimate with confidence interval | Point prediction of a dated outcome |
| "Scenario" | Hypothetical what-if with user-defined overrides | Prediction or expectation |
| "Escalation" | Crossing a defined severity threshold | Military attack or invasion |
| "Vulnerability" | Infrastructure or dependency fragility | Military weakness or exploitable gap |
| "Intelligence" | Analytical synthesis of open-source data | Classified or covert information |
| "Command room" | Monitoring and awareness interface | Operational military command |
| "Target" | Prioritized attention item | Military or attack target |
| "Asset" | Critical infrastructure or economic resource | Military asset or weapons system |

---

## Appendix B: Data Source Matrix (MVP)

| Source | Indicators served | Update cadence | API available | Reliability |
|---|---|---|---|---|
| ACLED | Conflict events, protest frequency, state violence | Weekly | Yes (free for research) | High (curated, coded) |
| GDELT | Media tone, event counts, cross-border attention | Daily | Yes (BigQuery / direct) | Medium (noisy, volume-dependent) |
| World Bank WDI | Trade volumes, GDP, military expenditure % | Quarterly / Annual | Yes | High (but lagged) |
| EIA / IEA | Energy production, consumption, reserves, trade | Monthly | Yes | High |
| UN OCHA / ReliefWeb | Displacement, food security, humanitarian access | Weekly–Monthly | Partial | High (within coverage area) |
| SIPRI | Arms transfers, military spending | Annual | Downloadable | High (but annual granularity) |
| Maritime AIS aggregates | Chokepoint transit volumes | Daily (commercial providers) | Varies | Medium-High |
| IISS Military Balance | Aggregate defense posture | Annual | No (reference publication) | High |

---

*End of build brief.*
