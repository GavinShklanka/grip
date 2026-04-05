# GRIP — Product Specification & Build Plan

## Concrete Implementation Guide

**Predecessor:** GRIP Build Brief (April 2026)  
**Purpose:** Convert the six-layer architecture into buildable entities, schemas, targets, and workflow  
**Author:** Gavin Shklanka · Black Point Analytics  
**Date:** April 2026

---

## 1. Product Framing

### The wrong framing

"A geopolitical war simulation dashboard."

This framing invites scrutiny on military realism (which you cannot deliver), attracts the wrong audience (people who want tactical modeling), and positions the project as a toy pretending to be a weapon.

### The right framing

**GRIP is a cross-domain geopolitical stress-propagation platform.**

It monitors observable indicators across six interconnected systems — alliances, trade, energy, infrastructure, logistics, and strategic posture — scores their current severity, models how shocks in one system cascade into others, and surfaces the resulting compound risks through a command-room interface designed for briefing-speed situational awareness.

### Why this framing wins

For a **hiring manager**: "This candidate built a multi-source data pipeline, a dependency-propagation engine, a time-series forecasting module, a scenario simulator, and a production dashboard — integrated into one system with a validation layer." That sentence covers data engineering, predictive analytics, prescriptive analytics, systems thinking, and software architecture.

For a **faculty reviewer**: The project demonstrates composite index construction, DAG-based simulation, classification under class imbalance, sensitivity analysis, and honest uncertainty quantification. Every MBAN competency is exercised.

For **you**: The project proves you can scope, architect, build, and ship a complex analytical product end-to-end. Not a notebook. Not a dashboard skin. A system.

### One-line pitch

> GRIP models how geopolitical pressure propagates across interconnected systems — so analysts can see what breaks before it breaks.

---

## 2. Strongest MVP Definition

### What ships

**Three regions. Six layers. One historical validation case.**

| Component | MVP scope | Why this boundary |
|---|---|---|
| **Regions** | Eastern Europe (Baltic/Ukraine focus), Middle East (Hormuz/Gulf), Indo-Pacific (Taiwan Strait) | Maximum analytical diversity with minimum data-engineering overhead. Each region exercises different domain weightings. |
| **Entities** | 15–20 countries, 5–8 chokepoints, 10–15 trade corridors, 6–8 alliance blocs | Enough to demonstrate dependency modeling without drowning in data cleaning |
| **Indicators** | 40–60 total across all domains (minimum 3 per domain per region) | Sufficient for defensible composite scores; more can be added post-MVP |
| **Scenarios** | 6 pre-built + custom builder | Covers the major archetypes: maritime, energy, sanctions, corridor, communications, sovereignty |
| **Forecasting** | 30-day domain-score trajectory + escalation-probability classification | Honest about what short-horizon open-source data can support |
| **Validation** | One full backtest: Russia-Ukraine pre-invasion timeline (2021-09 to 2022-02) | The single strongest proof-of-concept you can build |
| **Dashboard** | 5 views: Overview, Regional Detail, Scenario Workspace, Forecast Panel, Methodology | Complete analytical workflow without decorative excess |
| **Data mode** | Seed data + batch refresh scripts (not live streaming) | Buildable by one person. Demo mode uses seed data; production mode runs batch scripts on schedule. |

### What does not ship in MVP

- Live streaming ingestion
- NLP sentiment pipeline on diplomatic communications
- More than 3 regions
- Mobile-responsive layout
- User authentication or multi-tenancy
- Automated alert delivery (email/Slack)
- PDF briefing export

These are real features. They are not MVP features. Attempting them before the engine is validated will produce a wide, shallow product instead of a narrow, deep one.

---

## 3. Core Entities and Schema

### Entity-Relationship Model

```
Region ──1:M──▶ Country
Country ──M:M──▶ Alliance (via country_alliance)
Country ──M:M──▶ Country (via trade_dependency)
Country ──M:M──▶ Country (via energy_dependency)
Country ──1:M──▶ Chokepoint_Exposure (via chokepoint_country)
Region  ──1:M──▶ Corridor
Region  ──1:M──▶ Domain_Score (time-series)
Country ──1:M──▶ Domain_Score (time-series)
Country ──1:M──▶ Indicator_Value (time-series)
Indicator ──M:1──▶ Domain
Scenario ──1:M──▶ Scenario_Override
Domain_Score ──1:M──▶ Forecast
```

### Table Definitions

#### `regions`

| Column | Type | Description |
|---|---|---|
| region_id | VARCHAR PK | e.g., `eastern_europe`, `middle_east`, `indo_pacific` |
| name | VARCHAR | Display name |
| description | TEXT | Strategic context summary |
| centroid_lat | FLOAT | Map center latitude |
| centroid_lon | FLOAT | Map center longitude |

#### `countries`

| Column | Type | Description |
|---|---|---|
| country_id | VARCHAR PK | ISO 3166-1 alpha-3 |
| name | VARCHAR | Common name |
| region_id | VARCHAR FK | Primary region assignment |
| gdp_usd | FLOAT | Latest GDP (for normalization) |
| population | INTEGER | Latest population |
| is_focus | BOOLEAN | Whether this country is a primary analysis target vs. context |

#### `alliances`

| Column | Type | Description |
|---|---|---|
| alliance_id | VARCHAR PK | e.g., `nato`, `quad`, `gcc`, `csto`, `aukus` |
| name | VARCHAR | Full name |
| type | ENUM | `military`, `economic`, `political`, `multilateral` |
| status | ENUM | `active`, `strained`, `suspended`, `dissolved` |

#### `country_alliance`

| Column | Type | Description |
|---|---|---|
| country_id | VARCHAR FK | |
| alliance_id | VARCHAR FK | |
| membership_status | ENUM | `full`, `partner`, `observer`, `suspended` |
| commitment_score | FLOAT | 0–100, based on spending compliance, exercise participation, voting alignment |
| as_of_date | DATE | When this score was last assessed |

#### `domains`

| Column | Type | Description |
|---|---|---|
| domain_id | VARCHAR PK | e.g., `geopolitical_tension`, `energy_dependence`, `escalation_risk` |
| name | VARCHAR | Display name |
| layer | ENUM | `descriptive`, `readiness`, `forecast`, `composite` |
| description | TEXT | What this domain measures |
| is_composite | BOOLEAN | TRUE for escalation_risk (domain 11) — derived from others |

The 11 domains, mapped to your six layers:

**Layer 1 — Live Intelligence:** `geopolitical_tension`, `alliance_alignment`, `sanctions_pressure`, `trade_dependency`, `energy_dependence`, `supply_route_disruption`, `infrastructure_vulnerability`, `comms_logistics_stress`

**Layer 3 — Strategic Readiness:** `sovereignty_pressure`, `humanitarian_continuity`, `strategic_readiness` (new — captures defense posture, mobilization strain, industrial capacity at aggregate level)

**Layer 4 — Forecasting:** `escalation_risk` (composite, derived)

#### `indicators`

| Column | Type | Description |
|---|---|---|
| indicator_id | VARCHAR PK | e.g., `acled_conflict_events_30d`, `eia_crude_import_hhi` |
| domain_id | VARCHAR FK | Which domain this feeds |
| name | VARCHAR | Human-readable name |
| source | VARCHAR | Data provider (ACLED, GDELT, EIA, etc.) |
| source_reliability | ENUM | `high`, `medium`, `low` |
| update_cadence | ENUM | `daily`, `weekly`, `monthly`, `quarterly`, `annual` |
| unit | VARCHAR | Original unit of measurement |
| direction | ENUM | `higher_is_worse`, `lower_is_worse`, `contextual` |
| normalization_method | ENUM | `minmax_5yr`, `zscore`, `percentile_rank` |
| weight_in_domain | FLOAT | Weight within its domain composite (sums to 1.0 per domain) |

#### `indicator_values`

| Column | Type | Description |
|---|---|---|
| indicator_id | VARCHAR FK | |
| country_id | VARCHAR FK | (nullable — some indicators are regional or corridor-level) |
| region_id | VARCHAR FK | (nullable) |
| timestamp | TIMESTAMP | Observation date |
| raw_value | FLOAT | As-reported value |
| normalized_value | FLOAT | 0–100 scaled value |
| data_quality_flag | ENUM | `current`, `stale`, `interpolated`, `missing` |

#### `domain_scores`

| Column | Type | Description |
|---|---|---|
| domain_id | VARCHAR FK | |
| entity_type | ENUM | `country`, `region` |
| entity_id | VARCHAR | country_id or region_id |
| timestamp | TIMESTAMP | Score date |
| score | FLOAT | 0–100 composite |
| score_30d_ago | FLOAT | For delta calculation |
| velocity | FLOAT | Rate of change (points per day, 7-day smoothed) |
| data_coverage | FLOAT | 0–1, what fraction of indicators are current |
| anomaly_flag | BOOLEAN | Score > 2 SD from 30-day rolling mean |

#### `dependency_edges`

This is the backbone of the scenario simulation engine.

| Column | Type | Description |
|---|---|---|
| edge_id | VARCHAR PK | |
| source_domain | VARCHAR FK | Domain that transmits pressure |
| target_domain | VARCHAR FK | Domain that receives pressure |
| region_id | VARCHAR FK | (nullable — some edges are global, some regional) |
| weight | FLOAT | Propagation strength (0–1) |
| lag_days | INTEGER | Estimated propagation delay |
| confidence | ENUM | `empirical`, `literature`, `expert_prior` |
| justification | TEXT | Why this edge exists and why this weight |
| decay_per_hop | FLOAT | Attenuation factor for multi-hop cascades |

#### `chokepoints`

| Column | Type | Description |
|---|---|---|
| chokepoint_id | VARCHAR PK | e.g., `hormuz`, `malacca`, `suez`, `bosporus`, `baltic_approaches` |
| name | VARCHAR | |
| type | ENUM | `maritime`, `pipeline`, `overland`, `digital` |
| latitude | FLOAT | |
| longitude | FLOAT | |
| daily_transit_volume | FLOAT | Baseline (vessels, barrels, or data throughput depending on type) |
| current_disruption_score | FLOAT | 0–100 |
| criticality_rank | INTEGER | Global importance ranking |

#### `corridors`

| Column | Type | Description |
|---|---|---|
| corridor_id | VARCHAR PK | |
| name | VARCHAR | e.g., "Northern Sea Route," "Suez–Hormuz Energy Corridor" |
| type | ENUM | `trade`, `energy`, `logistics`, `digital` |
| region_id | VARCHAR FK | |
| origin_country | VARCHAR FK | |
| destination_country | VARCHAR FK | |
| chokepoints | ARRAY | List of chokepoint_ids along this corridor |
| current_viability_score | FLOAT | 0–100 |
| alternative_available | BOOLEAN | Whether a bypass route exists |

#### `scenarios`

| Column | Type | Description |
|---|---|---|
| scenario_id | VARCHAR PK | |
| name | VARCHAR | |
| description | TEXT | |
| type | ENUM | `prebuilt`, `custom` |
| category | ENUM | `maritime`, `energy`, `sanctions`, `corridor`, `communications`, `sovereignty`, `multi_domain` |
| created_at | TIMESTAMP | |

#### `scenario_overrides`

| Column | Type | Description |
|---|---|---|
| scenario_id | VARCHAR FK | |
| override_type | ENUM | `indicator`, `domain_score`, `edge_weight`, `chokepoint_status` |
| target_id | VARCHAR | ID of the thing being overridden |
| entity_id | VARCHAR | Country or region scope |
| override_value | FLOAT | New value to inject |
| rationale | TEXT | Why this override is set to this value |

#### `forecasts`

| Column | Type | Description |
|---|---|---|
| forecast_id | VARCHAR PK | |
| domain_id | VARCHAR FK | |
| entity_type | ENUM | `country`, `region` |
| entity_id | VARCHAR | |
| generated_at | TIMESTAMP | When the forecast was produced |
| horizon_days | INTEGER | 30, 60, or 90 |
| method | ENUM | `arima`, `ets`, `gbm_classifier`, `ensemble` |
| predicted_score | FLOAT | Central estimate |
| ci_lower_80 | FLOAT | 80% confidence interval lower bound |
| ci_upper_80 | FLOAT | 80% confidence interval upper bound |
| ci_lower_95 | FLOAT | 95% confidence interval |
| ci_upper_95 | FLOAT | |
| escalation_probability | FLOAT | P(crossing critical threshold within horizon) |
| brier_score | FLOAT | (nullable — populated only after backtesting) |

#### `assumptions`

| Column | Type | Description |
|---|---|---|
| assumption_id | VARCHAR PK | |
| layer | ENUM | `scoring`, `dependency`, `forecasting`, `scenario`, `structural` |
| statement | TEXT | Plain-language assumption |
| justification | TEXT | Why this assumption is made |
| sensitivity | ENUM | `high`, `medium`, `low` | How much output changes if this assumption is wrong |
| testable | BOOLEAN | Whether backtesting can validate this |
| last_reviewed | DATE | |

---

## 4. Forecast Targets — What Can Actually Be Predicted

### Forecastable (time-series or classification targets)

These have sufficient historical data, reasonable signal-to-noise ratios, and defensible outcome definitions.

| Target | Method | Outcome variable | Realistic horizon | Data source |
|---|---|---|---|---|
| **Domain-score trajectory** | ARIMA / ETS on domain_scores time series | Continuous score (0–100) | 30 days | Internal domain_scores table |
| **Escalation-threshold crossing** | Binary classification (GBM) | Did domain score cross 70/80/90 within window? | 30 days | Historical domain_scores + indicator features |
| **Chokepoint disruption probability** | Logistic regression on disruption indicators | P(disruption_score > threshold) | 14–30 days | Transit volumes, insurance rates, incident counts |
| **Trade-volume shock** | Regression on sanctions + disruption indicators | % deviation from 12-month rolling baseline | 30–60 days | World Bank, COMTRADE, sanctions event counts |
| **Energy-price stress** | Time-series on supply-demand indicators | Probability of spot-price spike > 2 SD | 14–30 days | EIA, IEA, chokepoint status |

### Not forecastable (must remain scenario-based)

These involve human decisions, black-swan events, or systems too complex for open-source prediction.

| Item | Why it is not forecastable | Correct treatment |
|---|---|---|
| **Whether a specific country invades another** | Political decision by a small group of actors; no model can predict this from public data | Scenario: "If invasion occurs, here is the modeled cascade" |
| **Alliance dissolution or formation** | Diplomatic process, not a statistical regularity | Scenario: "If State X exits Alliance Y, here is the burden redistribution" |
| **Cyber-attack on specific infrastructure** | Adversarial, non-stationary, zero-day by definition | Descriptive: current vulnerability score. Scenario: "If grid disruption occurs in Region Z..." |
| **Sanctions package composition** | Policy decision, infinite configuration space | Scenario: "If SWIFT disconnection of State X occurs..." |
| **Communications blackout timing** | Deliberate state action or infrastructure failure | Scenario: "If undersea cable serving Region Z is severed..." |
| **Humanitarian displacement trigger point** | Compound event depending on violence, infrastructure, and governance | Descriptive: current strain score. Scenario: "At escalation level N, displacement models project M." |
| **Sovereignty-transfer events** | Territorial changes are singular political/military events | Scenario only. Never forecast. |

### Descriptive only (no prediction, no scenario — just measurement)

| Item | Why descriptive only |
|---|---|
| **Current alliance commitment scores** | Observable, not predictable at useful horizons |
| **Current defense-spending levels** | Annual reporting, no meaningful short-term forecast |
| **Current trade-dependency concentration (HHI)** | Structural, changes slowly, report as-is |
| **Current infrastructure redundancy scores** | Engineering assessment, not a time-series target |
| **Current sanctions in effect** | Binary/categorical, report current state |
| **Source-reliability ratings** | Metadata, not an analytical target |

---

## 5. Dashboard Workflow — How a User Actually Moves Through the System

This is the realistic operational workflow, not a feature list.

### Step 1: Morning Brief (Global Overview — 60 seconds)

User opens GRIP. The default view answers three questions in under one minute:

1. **What changed overnight?** → Alert feed at bottom showing any domain scores that crossed thresholds or flagged anomalies since last session.
2. **Where is risk highest?** → Region cards ranked by composite escalation-risk score, with 7-day delta arrows (↑ rising, → stable, ↓ falling).
3. **What is the system's overall data health?** → Top-bar status: last refresh timestamp, global data-coverage percentage, number of stale indicators.

The user sees three region cards. Each card shows: region name, composite score (large number), a 30-day sparkline, and the single domain driving the most change (e.g., "Energy Dependence ↑12 pts").

**No interaction required.** The overview is a read-only situation board.

### Step 2: Regional Investigation (Regional Detail — 3–5 minutes)

User clicks a region card. The detail view answers:

1. **What is the pressure profile?** → Radar chart of all 11 domain scores. A ghost overlay shows 30-day-ago values so the user sees trajectory, not just state.
2. **Which domains are moving fastest?** → Domain-score table sorted by absolute velocity. Top movers are highlighted.
3. **What raw signals are driving the scores?** → Expandable indicator table under each domain. Shows raw value, normalized value, source, freshness, and quality flag.
4. **Are any indicators stale or missing?** → Data-quality matrix (domain × indicator) with color-coded freshness.

**Key interaction:** User can click any domain to drill into its indicator composition and see exactly how the score was calculated.

### Step 3: "What If?" (Scenario Workspace — 5–15 minutes)

User navigates to the scenario workspace. Two entry points:

**Pre-built scenario:** Select from library (e.g., "Hormuz Strait Closure"). The system pre-fills overrides and immediately shows the propagated state.

**Custom scenario:** User adjusts sliders to override individual domain scores, indicator values, or chokepoint statuses. The system propagates changes through the dependency DAG in real time.

The workspace shows:

- **Left panel:** Current state (baseline).
- **Right panel:** Simulated state (with overrides applied and cascaded).
- **Center strip:** Delta highlights — which domains changed, by how much, through which propagation paths.
- **Bottom panel:** Cascade trace — a step-by-step log: "Chokepoint Hormuz disruption_score overridden to 95 → Energy Dependence (Gulf states) +28 → Trade Dependency (Asia importers) +15 → Infrastructure Vulnerability (refinery-dependent states) +9."

**Key interaction:** The cascade trace. This is GRIP's analytical differentiator. It does not just show "things got worse." It shows the propagation path and the attenuation at each step.

### Step 4: Forward Look (Forecast Panel — 2–5 minutes)

User selects a region and views forward projections:

- **Fan charts:** 30-day trajectory for each domain score, with 80% and 95% confidence intervals visibly widening over time.
- **Escalation-probability gauge:** A single number — P(any domain crosses critical threshold within 30 days) — with a color-coded severity ring.
- **Calibration context:** Small inset showing the model's historical reliability: "When this model said 60% probability, the event occurred 58% of the time." (Reliability diagram.)
- **Leading indicators:** A ranked list of indicators that historically precede escalation in this region, with their current status (flashing/normal).

**Key constraint in the UI:** The forecast panel must visually distinguish between "the model is confident and the risk is high" vs. "the model is uncertain and the risk is unknown." These are not the same. The first gets a red indicator. The second gets a grey/hatched indicator with a "LOW CONFIDENCE" label.

### Step 5: Methodology Check (Validation Panel — as needed)

Available from any view via a persistent "Methodology" tab. Contains:

- **Assumptions register:** Every structural assumption, sortable by sensitivity level.
- **Sensitivity explorer:** Select any composite score → sliders show how ±10/25% changes in each input weight alter the output.
- **Backtest results:** For the Russia-Ukraine validation case — timeline of what the model would have scored at T-90, T-60, T-30, T-14, T-7, with actual outcomes annotated.
- **Claim boundaries:** An explicit, always-visible statement of what the system does and does not claim.

---

## 6. Classification: Descriptive vs. Forecastable vs. Scenario-Based

This is the single most important analytical decision in the platform. Getting this wrong — treating a scenario as a forecast, or a description as a prediction — destroys credibility.

### Descriptive Only (Layer 1 + Layer 3)

Report current state. No forward claims.

- Alliance commitment scores and membership status
- Current sanctions lists and trade restrictions in effect
- Trade-dependency concentration indices (HHI)
- Energy import-source diversification
- Infrastructure redundancy assessments
- Defense-spending as percentage of GDP
- Chokepoint current transit volumes
- Mobilization-strain indicators (reserve-to-active ratios, conscription status)
- Industrial-capacity utilization
- Border-force deployment density (aggregate, non-operational)
- Communications-backbone redundancy

**UI treatment:** Displayed as current-state cards and tables. No trend arrows unless backed by genuine time-series data. No implied prediction.

### Forecastable (Layer 4)

Forward-looking estimates with quantified uncertainty. Every forecast must carry a confidence interval and a model-performance metric.

- Domain-score 30-day trajectories (ARIMA/ETS)
- Escalation-threshold-crossing probability (GBM classifier)
- Chokepoint disruption probability (logistic regression)
- Trade-volume deviation from baseline (regression)
- Energy-price stress probability (time-series)

**UI treatment:** Fan charts with visible confidence intervals. Never a single line. Always accompanied by a calibration-quality indicator (good/moderate/poor).

### Scenario-Based Only (Layer 2)

User-driven or pre-built what-if exploration. No probability attached to the scenario itself occurring — only to the consequences given that it occurs.

- Maritime corridor closure
- Sanctions escalation (new tranche, SWIFT disconnection)
- Energy supply shock (pipeline disruption, embargo)
- Communications failure (undersea cable, internet backbone)
- Alliance fragmentation (member withdrawal, commitment reduction)
- Sovereignty provocation (territorial incursion, airspace violation)
- Multi-country spillover (crisis in State A propagating to States B, C, D)
- Resource competition intensification (rare-earth embargo, water dispute)

**UI treatment:** Scenario workspace only. Never displayed alongside forecasts. Never given a "probability of occurrence." The system can say "if this scenario occurs, the modeled impact is X with uncertainty band Y." It cannot say "there is a Z% chance this scenario occurs."

---

## 7. What to Cut (Even If It Sounds Impressive)

| Feature | Why it sounds good | Why to cut it |
|---|---|---|
| **Real-time NLP on state media / diplomatic cables** | Sounds like real intelligence work | Requires a separate NLP pipeline, multilingual processing, and careful bias handling. It is an entire project by itself. Add post-MVP if ever. |
| **Network-graph visualization of global trade relationships** | Visually dramatic | D3 force-directed graphs are time-consuming to make interactive and readable. The dependency DAG serves the analytical purpose better. A static network diagram in the methodology panel is fine. |
| **Predictive model for specific military actions** | The most "impressive" thing to claim | Indefensible. No open-source model can predict military decisions. Attempting this destroys the project's credibility. The scenario engine is the correct tool for this space. |
| **Country-internal political instability index** | Adds analytical depth | Requires entirely different data sources (polling, protest tracking, regime-type coding) and methodologies. Scope creep. |
| **Automated PDF briefing generation** | Professional-looking feature | Engineering effort with no analytical value. Copy-paste from the dashboard is fine for MVP. |
| **Multi-user roles and authentication** | Makes it feel like a "real product" | Zero analytical value. Zero portfolio value beyond basic auth boilerplate. Cut entirely. |
| **Mobile-responsive dashboard** | Broad accessibility | The command-room metaphor is desktop-native. No one runs crisis monitoring from a phone. Cut. |
| **Live websocket streaming** | Technically impressive | Your data sources update daily at best. Simulating real-time streaming on daily data is dishonest. Batch refresh with clear timestamps is correct. |
| **More than 3 regions at MVP** | Broader coverage | Each region requires indicator research, data sourcing, dependency calibration, and validation. Three well-executed regions outperform seven shallow ones. |
| **Cyber-threat scoring module** | Timely and relevant | Requires threat-intelligence feeds that are either classified, expensive, or unreliable in open-source form. A vulnerability score based on redundancy and incident history is fine. An active-threat score is not buildable. |

---

## 8. Why This Is Stronger Than a Generic "War Simulation"

A direct comparison.

### Generic war simulation

- **Data:** Made up or loosely inspired by real numbers. No provenance.
- **Model:** "Things happen" based on rules the builder invented. No validation.
- **Output:** A map with units moving around. Visually engaging, analytically empty.
- **Claims:** Implicitly claims to simulate military outcomes. Cannot defend this.
- **Audience reaction:** "Cool demo." Then: "But does any of this mean anything?" No good answer.
- **Portfolio value:** Demonstrates frontend skills. Demonstrates nothing about analytics.
- **Risk:** Crosses into operational military modeling, which is both ethically questionable and technically indefensible without classified data.

### GRIP

- **Data:** Named sources with documented reliability, update cadence, and known gaps.
- **Model:** Composite indices with explicit weights, a dependency DAG with justified edges, forecasting models with backtested performance metrics.
- **Output:** Risk scores, propagation traces, scenario comparisons, and calibrated probability estimates — all with uncertainty quantification.
- **Claims:** Explicit about what it claims and what it does not. The assumptions register is a feature, not an afterthought.
- **Audience reaction:** "This person understands how to model complex systems, handle data quality issues, quantify uncertainty, and build a production-grade analytical tool." That is an MBAN hiring conversation.
- **Portfolio value:** Demonstrates the full analytics stack: ingestion, transformation, descriptive analytics, predictive modeling, prescriptive simulation, visualization, and methodological rigor.
- **Risk:** None. Defensive framing, consequence analysis only, no operational military content.

### The core difference

A war simulation asks: "Who wins?"  
GRIP asks: "What breaks, how fast, and what should we watch?"

The first question is unanswerable with public data. The second is answerable, useful, and defensible. GRIP is stronger because it asks the right question.

---

## 9. Implementation Priority Order

Build in this sequence. Do not skip ahead.

| Phase | What | Duration estimate | Why this order |
|---|---|---|---|
| **1** | Schema + seed data for 1 region (Eastern Europe) | 3–4 days | You cannot build anything without data. Seed data lets you develop and demo without waiting for API integration. |
| **2** | Domain-scoring engine | 2–3 days | The core analytical primitive. Everything downstream depends on this. |
| **3** | Dependency DAG + propagation engine | 3–4 days | GRIP's differentiator. Build and test this thoroughly. |
| **4** | Scenario engine (pre-built + custom) | 2–3 days | Wraps the propagation engine in a user-facing interface. |
| **5** | Time-series forecasting (ARIMA on domain scores) | 2 days | Straightforward extension of the scoring engine. |
| **6** | Escalation classifier + backtesting | 3–4 days | The hardest analytical component. Requires careful treatment of class imbalance and calibration. |
| **7** | API layer (FastAPI) | 2 days | Expose everything built in Phases 1–6 as endpoints. |
| **8** | Dashboard — Overview + Regional Detail | 3–4 days | Now you have real data and real endpoints to display. |
| **9** | Dashboard — Scenario Workspace | 2–3 days | The interactive centerpiece. |
| **10** | Dashboard — Forecast Panel + Methodology Panel | 2–3 days | Completes the analytical workflow. |
| **11** | Seed data for regions 2 and 3 | 2–3 days | Expand coverage using the established pipeline. |
| **12** | Historical backtest (Russia-Ukraine 2021–22) | 3–4 days | The credibility anchor. Do this before polishing anything. |
| **13** | Documentation: methodology.md, limitations.md, assumptions register | 2 days | Not optional. This is part of the product. |
| **14** | Polish: color system, typography, interaction refinement | 2–3 days | Last. Only after everything works. |

**Total estimated build time: 30–40 focused days.**

This is aggressive but buildable for one person who has already architected the system (which you now have).

---

## 10. Schema Summary — Entity Count at MVP

| Entity | Count | Source |
|---|---|---|
| Regions | 3 | Manually defined |
| Countries | 15–20 | Selected per region |
| Alliances | 6–8 | Manually defined |
| Domains | 11 | Fixed |
| Indicators | 40–60 | Sourced per domain |
| Dependency edges | 30–50 | Calibrated per region |
| Chokepoints | 5–8 | Manually defined |
| Corridors | 10–15 | Manually defined |
| Pre-built scenarios | 6 | Manually authored |
| Assumptions | 25–40 | Documented during build |
| Historical data depth | 3–5 years | Per indicator, varies by source |

---

*End of product specification.*
