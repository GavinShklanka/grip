# GRIP — Working Source of Truth

## Canonical Reference · v1.0

**This document governs all implementation decisions for the GRIP project. Where any prior document (Build Brief, Product Specification, Operating Pack, Master Execution Plan) conflicts with this document, this document wins.**

**Date locked:** April 2026  
**Review trigger:** Any scope change, new data source, or architectural deviation requires an update to this document before proceeding.

---

# 1. Project Brief

GRIP is a geopolitical infrastructure risk platform focused on the Baltic-Nordic energy corridor (Finland, Estonia, Latvia, Lithuania). It monitors energy interconnectors, scores risk across eight domains, simulates infrastructure failure cascades, and produces a calibrated disruption-probability estimate — all presented through a command-room dashboard.

The platform answers three questions, in order of priority:

1. **What is the current state of Baltic energy infrastructure and the pressures acting on it?** (Descriptive)
2. **If a specific interconnector fails, what breaks downstream and how fast?** (Simulation)
3. **Based on observable signals, how likely is a critical interconnector disruption in the next 30 days?** (Forecasting)

GRIP does not predict wars, recommend military actions, or claim operational intelligence capability. It is a portfolio-grade analytical product built on open-source data with documented methodology, validated against historical events, and designed for transparency about its own limitations.

### What makes this project non-trivial

The Baltic corridor is a serial energy chain with five documented single points of failure and twelve infrastructure disruption events between 2022 and 2026. After BRELL desynchronization in February 2025, the electricity system operates with minimal redundancy — loss of any major interconnector threatens grid stability for three EU member states. The analytical challenge is modeling cross-domain pressure propagation through a physically constrained network using heterogeneous, multi-cadence open-source data, then producing risk estimates honest about their own uncertainty.

### What this project proves about the builder

End-to-end delivery of a data-intensive analytical system: multi-source ingestion pipeline, composite index construction, graph-based simulation engine, calibrated probabilistic risk model, interactive dashboard, and a validation framework that tests the system against real historical events. Every MBAN competency exercised in a single integrated product.

---

# 2. Non-Negotiable Constraints

These cannot be relaxed, deferred, or negotiated away. If any constraint cannot be met, the project scope must shrink to accommodate it — not the other way around.

### Scope constraints

| # | Constraint | Test |
|---|---|---|
| N1 | **One region only: Baltic-Nordic energy corridor.** No other regions at any phase. | The system contains data, scores, and scenarios for FI, EE, LV, LT only. Context countries (SE, PL, RU, DE) appear only as external nodes in the infrastructure graph. |
| N2 | **One primary forecast target: critical interconnector disruption probability within a 30-day rolling window.** No additional predictive models unless the primary model is validated first. | The system produces exactly one probabilistic forecast. All other analytical outputs are descriptive or scenario-based. |
| N3 | **Batch data only.** No streaming, no websockets in MVP, no sub-hourly refresh claims. | Every displayed value carries a "last updated" timestamp. No UI element implies real-time data. |
| N4 | **All data sources are free and open.** No paid APIs, no scraped paywalled content, no institutional subscriptions required to reproduce the pipeline. | A reviewer can clone the repo, obtain free API keys, and run the full pipeline without paying anything. |

### Analytical constraints

| # | Constraint | Test |
|---|---|---|
| N5 | **Every composite score has documented, adjustable weights.** No hardcoded magic numbers in scoring logic. | Weights live in `config/domains.json`, not in Python code. Changing a weight requires editing a JSON file, not source code. |
| N6 | **Every forecast carries a confidence interval.** No point estimates without uncertainty bounds. | The risk model endpoint returns `probability`, `ci_lower_80`, `ci_upper_80`, `ci_lower_95`, `ci_upper_95`, and `model_confidence` (good/moderate/poor). |
| N7 | **The system must be backtested against at least three historical disruption events before the dashboard is built.** Validation precedes visualization. | Notebook `04_disruption_backtest.ipynb` exists, runs end-to-end, and produces a Brier score and reliability diagram before any frontend code is written. |
| N8 | **Scenario simulation and forecasting are never conflated in the UI or API.** They occupy separate endpoints, separate dashboard views, and separate documentation sections. | No UI element displays a scenario result and a forecast result in the same panel without explicit labeling. The API has `/api/scenario/` and `/api/forecast/` as separate route groups. |

### Ethical constraints

| # | Constraint | Test |
|---|---|---|
| N9 | **No tactical, operational, or unit-level military content.** Military data enters only as aggregate strategic indicators (spending %, exercise frequency, posture bands). | A text search of the entire codebase and all data files for terms like "battalion," "brigade," "regiment," "targeting," "strike," "deployment," "order of battle" returns zero results. |
| N10 | **No offensive recommendations.** The system never answers "what should be attacked" or "where should forces go." It answers "what is at risk" and "what breaks if X happens." | Every scenario output describes consequences and vulnerabilities. No output describes actions to take against an adversary. |
| N11 | **The system explicitly states what it cannot do.** The methodology panel and README both contain a "Limitations" section that is not boilerplate. | The limitations section references specific known weaknesses (small-sample risk model, GDELT noise, temporal misalignment between indicators) with quantified impact where possible. |

### Quality constraints

| # | Constraint | Test |
|---|---|---|
| N12 | **Tests exist for scoring, cascade, and risk model modules.** | `pytest` runs with at least 15 test cases covering: domain score calculation, edge removal impact, scenario override application, risk model feature engineering, and API response schemas. |
| N13 | **The repo has a working README with setup instructions.** | A reviewer with Python 3.11+, Node 18+, and Docker can run the full system locally within 15 minutes of cloning. |
| N14 | **Seed data enables a complete demo without live API access.** | Setting `DEMO_MODE=true` loads all seed data and the full dashboard is functional with no external API calls. |

---

# 3. Explicit Out-of-Scope Items

These items are permanently excluded. They are not deferred — they will not be built in any phase. If a future decision reverses any of these, this document must be updated first with a written justification.

| # | Excluded item | Why excluded |
|---|---|---|
| X1 | **Additional regions** (Indo-Pacific, Middle East, Sahel, Arctic) | Each region requires its own data pipeline, domain calibration, and dependency graph. Adding a region is equivalent to building a second product. |
| X2 | **NLP sentiment pipeline on diplomatic communications or state media** | A standalone project requiring multilingual processing, bias handling, and its own validation. Zero overlap with the energy infrastructure pipeline. |
| X3 | **Country-internal political forecasting** (elections, regime change, protest prediction) | Different data sources, different methods, different validation. Scope contamination. |
| X4 | **Cyber-threat scoring** | Requires threat-intelligence feeds that are either classified, expensive, or unreliable in open-source form. A vulnerability score based on redundancy is in scope; an active-threat score is not. |
| X5 | **User authentication, multi-tenancy, or role-based access** | Zero analytical value. Zero portfolio value. Engineering overhead with no return. |
| X6 | **Mobile-responsive layout** | The command-room interface is desktop-native. No one monitors infrastructure risk from a phone. |
| X7 | **Automated alert delivery** (email, Slack, push notifications) | Requires integration infrastructure that adds complexity without analytical depth. Alerts are displayed in the dashboard. |
| X8 | **PDF briefing export** | Engineering effort with no analytical value for MVP. Copy-paste or screenshot from the dashboard is sufficient. |
| X9 | **Live websocket streaming** (including AISStream live integration in MVP) | The underlying data sources update hourly at best. Simulating real-time on batch data is dishonest. AISStream is a post-MVP enhancement only. |
| X10 | **Force-directed network graph visualization** | Time-consuming to make interactive and readable. The infrastructure topology is better served by a fixed-layout SVG diagram reflecting actual geography. |
| X11 | **Predictive models beyond the primary disruption-risk score** | One model, validated well, is worth more than three models validated poorly. ARIMA on domain scores is permitted only if the primary model passes backtesting first. |
| X12 | **Tactical military modeling of any kind** | Permanently excluded. See N9, N10. |

---

# 4. Critical Assumptions Requiring Validation

Each assumption below has a defined test and a fallback if the assumption fails.

| # | Assumption | Validation method | When to test | Fallback if false |
|---|---|---|---|---|
| A1 | **The Baltic serial-chain topology is the correct dependency structure for energy cascade modeling.** | Compare graph edges to ICDS Baltic Energy Interconnections Maps and ENTSO-E grid map. Confirm all major interconnectors are represented. | Phase 0 (before any scoring) | Revise topology. This is a fast fix since topology is in JSON config. |
| A2 | **ENTSO-E cross-border flow data shows clear, timestamped drops during known disruption events.** | Pull hourly FI→EE flow data for Dec 25, 2024. Confirm Estlink 2 flow drops to zero within hours. Repeat for Balticconnector Oct 7, 2023 in ENTSOG. | Phase 0 (data validation) | If the signal is not clean, the entire backtesting strategy collapses. Escalate immediately — this is a project-viability question. |
| A3 | **Six energy-interconnector disruption events provide sufficient positive cases for leave-one-out validation of a logistic regression risk score.** | Run leave-one-out after Phase 3. Report Brier score. Compare to naive base-rate predictor. | Phase 3 | If the model cannot beat the base rate, document the failure honestly, rely on the rule-based alert layer, and frame the backtesting notebook as "what we learned." |
| A4 | **GDELT event counts are a useful proxy for Baltic geopolitical tension.** | Compute weekly GDELT event counts filtered to Baltic + Russia actors. Correlate with known tension periods (pre-invasion 2022, cable attacks 2024). Check if signal-to-noise is tolerable. | Phase 1 (data exploration) | Downweight the geopolitical_tension domain. Increase weight on infrastructure_vulnerability and energy_dependence, which have cleaner signals. Document the decision. |
| A5 | **Capacity arithmetic (available import MW minus demand MW) is a sufficient proxy for grid stability impact in cascade simulations.** | Compare model output for Estlink 2 removal scenario against documented real-world impact (65% FI→EE capacity loss, price spikes). Check order-of-magnitude consistency. | Phase 2 (scenario validation) | Acceptable simplification as long as documented. GRIP is a risk platform, not a power-flow simulator. Reference ENTSO-E's own tools for engineering-grade analysis. |
| A6 | **Weather severity (wind, wave, ice from Copernicus ERA5) is a meaningful feature for disruption risk.** | Check weather conditions at the time and location of each historical event. Determine if storm conditions co-occurred with anchor-dragging incidents. | Phase 3 (feature analysis) | Drop weather features from the risk model if no signal. Document the finding. The model still has vessel-activity and geopolitical features. |
| A7 | **Post-BRELL LitPol Link commercial capacity is approximately 200–365 MW (2026).** | Cross-reference against ENTSO-E actual flow data for LitPol in 2026. | Phase 0 | Update topology edge capacity to match observed flows. |
| A8 | **The gas system is adequately redundant and should be weighted lower than electricity in composite scoring.** | Confirmed by Balticconnector outage Oct 2023–Apr 2024: no gas shortages occurred despite 6.5-month pipeline outage. | Already validated | N/A — this is a confirmed finding. Gas domains receive lower weight than electricity domains in the composite index. |

---

# 5. Architecture Principles

These govern every technical decision. When in doubt, apply the principle.

### P1: Configuration over code

Anything an analyst might want to adjust lives in a JSON config file, not in Python source code. This includes: domain weights, alert thresholds, infrastructure topology (nodes and edges with capacities), scenario definitions, normalization parameters, and model hyperparameters.

**Test:** A non-developer can change the weight of the `energy_dependence` domain by editing `config/domains.json` without touching any `.py` file.

### P2: Seed data enables full demo

The system must run completely from committed seed data with no external API calls. This means the repo ships with enough historical data (2022–2026 cross-border flows, event records, pre-computed scores) to demonstrate every feature.

**Test:** `DEMO_MODE=true python -m backend.main` starts the API and all endpoints return valid data.

### P3: Ingestion modules are isolated and substitutable

Each data source is a separate Python module implementing a common interface (`fetch()`, `transform()`, `load()`). Adding a new source or replacing a broken one requires writing one new file — not modifying existing modules.

**Test:** Deleting `ingestion/gdelt.py` does not break any other ingestion module or the scoring engine. The affected domain scores show a data-quality flag, not a crash.

### P4: The topology is the model

The infrastructure DAG in `config/topology.json` is the single source of truth for dependency structure. The cascade engine reads this file. Scenario overrides modify edge states in this graph. Adding a new interconnector (e.g., Harmony Link in 2029) means adding a node and edges to the JSON file.

**Test:** Adding a hypothetical edge to `topology.json` and restarting the scenario engine makes the new edge available for simulation without code changes.

### P5: Forecasts and scenarios are separate systems

The forecasting module (`forecasting/`) and the simulation module (`simulation/`) share no code paths. They read from the same data layer but produce independent outputs served by independent API routes. The frontend renders them in separate views.

**Test:** Disabling the entire forecasting module does not affect scenario simulation, and vice versa.

### P6: Every number traces to a source

For any value displayed on the dashboard, a reviewer can drill down to: the raw indicator value, the data source, the retrieval timestamp, the normalization method applied, and the weight used in the composite. The methodology panel and API both support this drill-down.

**Test:** Clicking any domain score in the UI shows the indicator breakdown. The `/api/meta/provenance/{domain}/{country}` endpoint returns the full calculation trace.

### P7: Uncertainty is visible, not hidden

Confidence intervals, data-quality flags, and model-performance metrics are first-class UI elements, not footnotes. The dashboard uses visual encoding (color, hatching, labels) to distinguish "high confidence, high risk" from "low confidence, unknown risk."

**Test:** A domain score built from three stale indicators is visually distinct from one built from three current indicators, even if the numeric scores are identical.

### P8: The backtest notebook is a deliverable, not a worksheet

Notebook `04_disruption_backtest.ipynb` is written for a reader, not just the builder. It has section headers, explanatory markdown, and a conclusions section. It runs end-to-end from raw data to calibration plot without manual intervention.

**Test:** A reviewer who has never seen the project can read the notebook and understand: what was tested, what data was used, what the model predicted, what actually happened, and what the model got wrong.

### P9: Honest failure is better than cosmetic success

If the risk model cannot beat the naive base rate, the project documents this and explains why. If GDELT is too noisy, the project says so and downgrades the domain. The assumptions register, limitations documentation, and backtest results are not afterthoughts — they are portfolio assets that demonstrate analytical maturity.

**Test:** The `docs/limitations.md` file contains at least five specific, quantified limitations with their impact on system outputs.

### P10: Build sequence is engine → validation → dashboard

No frontend code is written until the scoring engine, cascade simulator, and risk model are tested and backtested. Dashboard development begins only after the backtest notebook is complete. This order is enforced by the phased execution plan and is not negotiable.

**Test:** Git history shows backend and notebook commits before any frontend commits.

---

# 6. Glossary

Terminology must be consistent across all code, documentation, UI labels, and conversations. Where a term has been used inconsistently in prior documents, the definition below is canonical.

| Term | Definition | Not to be confused with |
|---|---|---|
| **GRIP** | Geopolitical Resilience Intelligence Platform. The project name. | Not an acronym to be expanded differently elsewhere. |
| **Corridor** | The Baltic-Nordic energy corridor: the set of interconnectors, facilities, and energy flows linking Finland, Estonia, Latvia, and Lithuania. | Not a geographic region in the general sense. The corridor is defined by infrastructure, not borders. |
| **Interconnector** | A physical energy transmission link between two countries or systems. Includes submarine power cables (Estlink 1, Estlink 2, NordBalt), gas pipelines (Balticconnector, GIPL), and overland power lines (LitPol Link, EE-LV 330 kV lines). | Not telecom cables (tracked separately as communications infrastructure). |
| **Domain** | One of eight analytical categories scored by GRIP. Each domain produces a 0–100 composite score per country. | Not a geographic area. Not a "module" (which refers to code). |
| **Domain score** | A 0–100 composite index for a single domain, for a single country, at a single point in time. Higher scores indicate greater stress or risk. | Not a probability. Not a forecast. A domain score is a descriptive measurement of current conditions. |
| **Indicator** | A single measurable quantity from a specific data source that feeds into a domain score. Example: "Estlink 2 hourly MW flow" is an indicator within the `infrastructure_vulnerability` domain. | Not a domain score (which is a weighted composite of multiple indicators). |
| **Topology** | The infrastructure dependency graph: nodes (countries, interconnectors, facilities) and edges (physical connections with capacity attributes). Stored in `config/topology.json`. | Not an abstract or statistical network. The topology represents physical infrastructure. |
| **Cascade** | The modeled downstream impact of removing or degrading one or more edges in the topology. Computed as capacity arithmetic: recalculate available import capacity minus demand for each country after edge removal. | Not a stochastic simulation. Not a time-stepped propagation model. Cascades are deterministic given the topology and current state. |
| **Scenario** | A user-defined or pre-built set of overrides applied to the topology (edge removals, capacity reductions, indicator changes). A scenario answers "what if X happens?" | Never a forecast. A scenario carries no probability of occurrence. It produces a modeled consequence given an assumed trigger. |
| **Disruption event** | An observed, historical, unplanned outage of a critical interconnector lasting ≥24 hours. The twelve documented events (2022–2026) are the backtesting ground truth. | Not a scenario (which is hypothetical). Not a forecast (which is forward-looking). |
| **Risk score** | The primary forecast output: P(any critical interconnector disruption within the next 30 days), produced by a logistic regression model with calibrated probabilities. Served from `/api/forecast/risk`. | Not a domain score (which is descriptive). Not a scenario result (which is conditional). The risk score is the only probabilistic claim the system makes. |
| **N-1 margin** | The MW capacity buffer remaining after the loss of the single largest infeed (the "N-1 criterion" from power systems engineering). For the Baltics post-BRELL, this is approximately 1,500 MW of reserve required for frequency stability. If available capacity minus demand minus reserve < 0, the system is in N-1 violation. | Not the same as "total available capacity." N-1 margin accounts for the reserve requirement. |
| **Seed data** | Pre-downloaded, committed historical data (2022–2026) that enables the full system to run in demo mode with no external API calls. Stored in `data/seed/`. | Not "sample data" or "synthetic data." Seed data is real historical data, frozen at a point in time. |
| **Backtest** | Evaluation of the risk model against historical disruption events using leave-one-out cross-validation. For each event: train on all other events, test whether the model elevated the risk score in the 30 days prior to the held-out event. | Not forward validation (which would require new events). Not a simulation (which is hypothetical). |
| **Alert** | A notification generated when a monitored condition crosses a predefined threshold. Two sources: (1) rule-based alerts (e.g., "N-1 margin violated," "2+ interconnectors offline simultaneously"), and (2) model-based alerts (risk score exceeds threshold). | Not a forecast. An alert is a threshold-crossing flag on current or projected data. |
| **Descriptive** | An analytical output that reports current state only. No forward-looking claim. Examples: domain scores, N-1 margin, sanctions count. | Always distinguish from "forecast" and "scenario" in UI labels and documentation. |
| **Strategic readiness** | Aggregate, non-operational indicators of defense posture and alliance burden. Limited to: defense spending as % GDP, NATO exercise frequency, alliance commitment scores, border-force density, industrial capacity utilization. | Never unit-level, tactical, or operational. Never force composition, deployment plans, or weapons inventories. |
| **Shadow fleet** | Vessels operating under flags of convenience with opaque ownership, expired insurance, and suspected ties to Russian sanctions evasion. Relevant as a risk indicator: shadow fleet presence near Baltic submarine cables is a documented precursor to disruption events. | Not a military term. Not an intelligence classification. GRIP tracks shadow fleet as an observable, open-source risk signal. |
| **Context country** | A country modeled as an external node in the topology graph (Sweden, Poland, Russia, Germany). Context countries are sources or sinks of energy flows but are not scored by GRIP's domain indices. | Not a focus country. Context countries do not have domain scores, risk scores, or dedicated dashboard views. |
| **Focus country** | Finland, Estonia, Latvia, or Lithuania. Fully scored, fully modeled, with dedicated dashboard views. | The only countries that receive domain scores and appear in the risk model. |

---

# 7. The Eight Domains (Canonical List)

Prior documents used 11 domains. Three have been cut for the Baltic corridor because they produce near-zero signal and distract from the system's analytical focus.

### Active domains

| # | Domain ID | Name | Primary data sources | Update cadence | Signal strength for Baltics |
|---|---|---|---|---|---|
| 1 | `energy_dependence` | Energy Dependence | ENTSO-E flows, ENTSOG flows, Klaipėda/Inkoo LNG throughput | Hourly (electricity), Daily (gas) | Very high |
| 2 | `infrastructure_vulnerability` | Infrastructure Vulnerability | ENTSO-E forced outage data, interconnector status register, N-1 margin calculation | Hourly | Very high |
| 3 | `supply_route_disruption` | Supply-Route Disruption | Chokepoint transit proxy (ENTSO-E flow volumes as proxy for corridor health), telecom cable status | Daily | High |
| 4 | `sanctions_pressure` | Sanctions & Trade Pressure | OpenSanctions entity count, Eurostat COMEXT trade volumes (HS 27xx), shadow fleet vessel count | Daily (sanctions), Monthly (trade) | High |
| 5 | `geopolitical_tension` | Geopolitical Tension | GDELT event counts and tone (Baltic + Russia actor filter), diplomatic incident proxy | Daily (aggregated weekly for scoring) | Medium (noisy) |
| 6 | `alliance_alignment` | Alliance Alignment | NATO exercise frequency (GDELT event coding), defense-spending commitments, UN GA voting alignment | Weekly to monthly | Medium |
| 7 | `comms_logistics_stress` | Communications & Logistics Stress | Telecom cable status (known outages), freight/transport indicators where available | Weekly | Medium-low |
| 8 | `strategic_readiness` | Strategic Readiness | Defense spending % GDP (SIPRI via World Bank), reserve-to-active ratios, industrial capacity indicators | Monthly to annual | Low (slow-moving) |

### Composite domain (derived)

| # | Domain ID | Name | Derived from | Method |
|---|---|---|---|---|
| 9 | `escalation_risk` | Escalation Risk | Domains 1–8 | Weighted composite of domain scores, with velocity (rate-of-change) as a multiplier. Not independently scored from raw indicators. |

### Removed domains

| Domain | Reason for removal |
|---|---|
| `humanitarian_continuity` | Baltic NATO states have no active humanitarian crisis, no significant displacement, and robust social services. This domain would score near-zero consistently, adding noise without signal. |
| `resource_competition` | The Baltics do not compete for rare earths, water, or agricultural inputs at a level that creates measurable geopolitical stress. Irrelevant for this corridor. |
| `sovereignty_pressure` | Conceptually relevant but empirically absorbed into `geopolitical_tension` and `strategic_readiness` for this region. Maintaining it as a separate domain would force thin, duplicative indicator sourcing. |

---

# 8. Contradictions Resolved

These conflicts existed across the prior four documents. Each is now settled.

| # | Contradiction | Resolution | Governing principle |
|---|---|---|---|
| 1 | **Build Brief said 3 regions. Operating Pack said 1. Execution Plan said 1.** | One region. Final. The Baltic-Nordic corridor is the project scope. Additional regions are permanently excluded (X1). | Depth over breadth. |
| 2 | **Build Brief said 11 domains. Execution Plan said 8 active.** | Eight scored domains plus one composite. Three removed for low signal. See Section 7 above. | Every domain must have at least three real indicators with tolerable signal-to-noise. |
| 3 | **Operating Pack titled the project "Strategic Crisis and Sovereignty Resilience Simulator." Execution Plan said it is not a simulator.** | GRIP is a monitoring and risk-assessment platform with simulation capability. The primary value is continuous situational awareness. Scenario simulation is secondary. The word "simulator" does not appear in the project name, README, or UI. | The primary use case (daily monitoring) drives the product hierarchy, not the secondary use case (what-if analysis). |
| 4 | **Product Spec proposed ARIMA on domain scores + GBM classifier. Operating Pack said one forecast module. Execution Plan said logistic regression.** | One primary model: logistic regression producing a calibrated disruption-probability score. ARIMA trend lines on domain scores are permitted only after the primary model passes backtesting. No GBM — logistic regression is more interpretable and appropriate for the sample size. | One model, validated well, beats three models validated poorly (N2). |
| 5 | **Build Brief described dependency-graph edges calibrated from "historical co-movement." Execution Plan described the DAG as physical infrastructure topology.** | The DAG is the physical topology. Edge weights are transmission capacities (MW, mcm/day), not correlation coefficients. Cascade logic is capacity arithmetic. No statistical edge calibration required. | The topology is the model (P4). |
| 6 | **Research sourcebook listed LitPol commercial capacity as ~150 MW. Web search found 200–365 MW for 2026.** | Use 200 MW import as conservative modeling baseline. Document that capacity is ramping and expected to reach ~350–500 MW by 2027. | Always use the most recent confirmed data. When in doubt, use the conservative estimate. |
| 7 | **Research sourcebook listed 11 backtesting events. Web search found a 12th (Kiisa battery trip, Jan 2026).** | Twelve total events. Six are energy-interconnector disruptions suitable as positive labels for the risk model. The remaining six (Nord Stream, telecom-only events, Russian electricity cutoff) are contextual events documented in the event register but not used as positive labels for the interconnector-disruption model. | The forecast target is narrowly defined (interconnector outage ≥24h). Only events matching this definition are positive labels. |
| 8 | **Various documents used "risk score," "forecast," "prediction," and "probability" interchangeably.** | Terminology is locked per the glossary. "Risk score" = the model output (a calibrated probability). "Forecast" = the analytical layer that produces the risk score. "Prediction" is not used anywhere — the system produces probability estimates, not predictions. | Words have meanings. Use the glossary. |

---

# 9. Decision Register

Decisions made during session hardening that are now binding.

| # | Decision | Rationale | Date |
|---|---|---|---|
| D1 | Primary forecast target is interconnector disruption probability (binary outcome, 30-day window). | Narrowly defined, historically observable, backtestable. Strongest portfolio signal. | Apr 2026 |
| D2 | Logistic regression is the modeling method for the risk score. | Appropriate for small sample size (6 positive events). Interpretable. Calibratable. Feature importance is transparent. | Apr 2026 |
| D3 | The cascade engine uses capacity arithmetic, not stochastic propagation. | The topology is physical infrastructure with known capacities. Deterministic math is more defensible and explainable than a statistical model pretending to be physics. | Apr 2026 |
| D4 | Dashboard development does not begin until backtest notebook is complete. | Validation before visualization. This is enforced by the phase sequence (P10) and is non-negotiable. | Apr 2026 |
| D5 | Gas domains receive lower composite weight than electricity domains. | Empirically confirmed: Balticconnector outage (Oct 2023–Apr 2024) caused zero gas shortages. Electricity interconnectors are the demonstrated vulnerability. | Apr 2026 |
| D6 | "Simulator" is not used in the project name, title, or UI labels. | The project is a monitoring and risk platform. "Simulator" implies a fidelity the system does not have and invites scrutiny it cannot withstand. | Apr 2026 |
| D7 | The word "prediction" is not used anywhere in the system. | The system produces probability estimates and scenario consequences. "Prediction" implies a certainty the methodology does not support. | Apr 2026 |
| D8 | Harmony Link is modeled as a future edge (not yet constructed). | Construction tenders launching 2026, completion 2029–2030. It appears in documentation and as a "planned" node in the topology visualization, but it carries zero capacity in all calculations. | Apr 2026 |

---

*This document is the canonical reference. All implementation work, code reviews, and documentation must be consistent with it. If reality forces a change, update this document first, then proceed.*
