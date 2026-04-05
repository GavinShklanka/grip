# GRIP Data Dictionary

## Indicator Reference

Every indicator used by the GRIP scoring engine, with source, cadence, unit, domain mapping, and known issues.

---

### Energy Dependence Domain

| ID | Name | Source | Cadence | Unit | Direction | Weight | Known Issues |
|----|------|--------|---------|------|-----------|--------|-------------|
| `electricity_import_ratio` | Electricity Import Ratio | ENTSO-E | Daily | ratio (0-1) | higher_is_worse | 0.20 | Denominator uses fixed consumption estimate (1000 MW for EE/LV/LT), not actual consumption |
| `gas_import_concentration` | Gas Import Source Concentration (HHI) | ENTSOG | Daily | HHI (0-1) | higher_is_worse | 0.15 | Only Baltic gas entry points included; does not capture internal storage |
| `estlink_utilization` | Estlink Utilization Rate | ENTSO-E | Daily | ratio (0-1) | higher_is_worse | 0.15 | Computed against *available* capacity (excluding offline cables), not total installed |
| `lng_utilization` | LNG Terminal Utilization | ENTSOG | Daily | ratio (0-1) | higher_is_worse | 0.10 | Currently only Klaipeda LNG tracked |
| `interconnectors_offline` | Interconnectors Currently Offline | ENTSO-E | Daily | count | higher_is_worse | 0.40 | Binary detection (flow=0 with capacity>0); cannot distinguish planned maintenance from forced outage |

### Infrastructure Vulnerability Domain

| ID | Name | Source | Cadence | Unit | Direction | Weight | Known Issues |
|----|------|--------|---------|------|-----------|--------|-------------|
| `interconnectors_offline` | Interconnectors Currently Offline | ENTSO-E | Daily | count | higher_is_worse | 0.35 | Shared with energy_dependence domain; dual-counted by design |
| `n1_margin_deficit` | N-1 Margin Deficit | Computed | Daily | MW | higher_is_worse | 0.35 | Depends on static topology.json capacity values; real-time NTC not available in demo |
| `submarine_cable_exposure` | Submarine Cable Exposure Ratio | Static | Weekly | ratio (0-1) | higher_is_worse | 0.15 | Currently a fixed synthetic value (0.75 for EE) |
| `days_since_last_disruption` | Days Since Last Disruption | Computed | Daily | days | lower_is_worse | 0.15 | Inverted: fewer days = higher risk. Capped at 100 days for normalization |

### Supply Route Disruption Domain

| ID | Name | Source | Cadence | Unit | Direction | Weight | Known Issues |
|----|------|--------|---------|------|-----------|--------|-------------|
| `cross_border_flow_anomaly` | Cross-Border Flow Anomaly | ENTSO-E | Daily | z-score | higher_is_worse | 0.40 | 30-day rolling window; early data points may have insufficient history |
| `gas_flow_disruption` | Gas Flow Disruption Z-Score | ENTSOG | Daily | z-score | higher_is_worse | 0.30 | Same rolling window limitation as above |
| `telecom_cable_status` | Telecom Cable Status | Static | Weekly | ratio (0-1) | lower_is_worse | 0.30 | Currently a fixed synthetic value (0.8); no real-time undersea telecom monitoring |

### Sanctions Pressure Domain

| ID | Name | Source | Cadence | Unit | Direction | Weight | Known Issues |
|----|------|--------|---------|------|-----------|--------|-------------|
| `sanctions_entity_count` | EU Sanctioned Entities Count | Sanctions CSV | Monthly | count | higher_is_worse | 0.50 | Aggregate EU count, not country-specific. Updates lag real sanctions packages |
| `shadow_fleet_count` | Shadow Fleet Vessels Estimate | Sanctions CSV | Monthly | count | higher_is_worse | 0.50 | Estimate based on open-source reporting; actual fleet size uncertain |

### Geopolitical Tension Domain

| ID | Name | Source | Cadence | Unit | Direction | Weight | Known Issues |
|----|------|--------|---------|------|-----------|--------|-------------|
| `gdelt_event_intensity` | GDELT Event Intensity | GDELT CSV | Weekly | count | higher_is_worse | 0.40 | Raw event count; does not weight by event significance |
| `gdelt_tone_avg` | GDELT Average Tone | GDELT CSV | Weekly | score (-10 to +10) | lower_is_worse | 0.30 | Inverted: more negative tone = higher risk. Noisy measure |
| `diplomatic_incident_count` | Diplomatic/Conflict Incidents | GDELT CSV | Weekly | count | higher_is_worse | 0.30 | Counts conflict events specifically from GDELT event taxonomy |

### Alliance Alignment Domain

| ID | Name | Source | Cadence | Unit | Direction | Weight | Known Issues |
|----|------|--------|---------|------|-----------|--------|-------------|
| `defense_spending_gdp_pct` | Defense Spending (% GDP) | Static CSV | Annual | percentage | lower_is_worse | 0.40 | Annual granularity; does not reflect within-year budget changes |
| `nato_exercises_count` | NATO Exercise Count | Static CSV | Annual | count | lower_is_worse | 0.30 | Counts joint exercises in Baltic region; higher = better aligned |
| `reserve_to_active_ratio` | Reserve-to-Active Military Ratio | Static CSV | Annual | ratio | lower_is_worse | 0.30 | Structural indicator; slow-moving by nature |

### Communications & Logistics Stress Domain

| ID | Name | Source | Cadence | Unit | Direction | Weight | Known Issues |
|----|------|--------|---------|------|-----------|--------|-------------|
| `telecom_cable_status` | Telecom Cable Operational Status | Static | Weekly | ratio (0-1) | lower_is_worse | 0.50 | Synthetic default; no live monitoring |
| `cross_border_flow_anomaly` | Cross-Border Flow Anomaly | ENTSO-E | Daily | z-score | higher_is_worse | 0.50 | Shared with supply_route_disruption domain |

### Strategic Readiness Domain

| ID | Name | Source | Cadence | Unit | Direction | Weight | Known Issues |
|----|------|--------|---------|------|-----------|--------|-------------|
| `defense_spending_gdp_pct` | Defense Spending (% GDP) | Static CSV | Annual | percentage | lower_is_worse | 0.35 | Shared with alliance_alignment |
| `nato_exercises_count` | NATO Exercise Count | Static CSV | Annual | count | lower_is_worse | 0.35 | Shared with alliance_alignment |
| `reserve_to_active_ratio` | Reserve-to-Active Ratio | Static CSV | Annual | ratio | lower_is_worse | 0.30 | Shared with alliance_alignment |

---

## Data Sources

| Source | Type | API/File | Cadence | Coverage |
|--------|------|----------|---------|----------|
| ENTSO-E | Electricity flows | `entsoe` Python package / CSV seed | Hourly→Daily | Jan 2022 – Dec 2025 |
| ENTSOG | Gas flows | `entsog` Python package / CSV seed | Daily | Jan 2022 – Dec 2025 |
| GDELT | Event monitoring | CSV seed | Weekly | Jan 2022 – Dec 2025 |
| EU Sanctions | Policy tracker | CSV seed | Monthly | Jan 2022 – Dec 2025 |
| Static indicators | Defense/NATO | CSV seed | Annual | 2022 – 2025 |
| Topology | Infrastructure graph | JSON config | Static | Current |
| Disruption events | Ground truth | JSON config | Event-based | 6 events |

## Country Coverage

| Country | ISO | Focus Level | Notes |
|---------|-----|-------------|-------|
| Estonia | EE | Primary focus | Most indicator coverage |
| Finland | FI | Focus | Electricity flow data |
| Latvia | LV | Focus | Gas transit data |
| Lithuania | LT | Focus | LNG + electricity data |
| Sweden | SE | Context | NordBalt connection only |
| Poland | PL | Context | LitPol Link connection only |
