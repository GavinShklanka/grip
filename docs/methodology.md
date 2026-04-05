# GRIP Scoring Methodology

## Overview

The Geopolitical Resilience Intelligence Platform (GRIP) computes infrastructure risk scores
for Baltic-Nordic states (Finland, Estonia, Latvia, Lithuania) using a deterministic,
multi-domain scoring framework. Each country receives scores across **8 risk domains**
which are combined into a single **Escalation Composite Index (ECI)**.

## Architecture

```
Raw Data (ENTSO-E, ENTSOG, GDELT, sanctions, static)
    ↓
Ingestion Layer (fetch → derive indicators → load to DB)
    ↓
Indicator Values (indicator_id, country_id, timestamp, raw_value)
    ↓
Normalization (min-max to 0–100 scale)
    ↓
Domain Scoring (weighted sum per domain)
    ↓
Escalation Composite (weighted sum across domains)
    ↓
Risk Model (Random Forest → P(disruption in 7 days))
```

## The 8 Risk Domains

| Domain | Layer | Weight | Description |
|--------|-------|--------|-------------|
| energy_dependence | Descriptive | 0.20 | Import dependency and concentration risk |
| infrastructure_vulnerability | Descriptive | 0.20 | Physical fragility of critical connections |
| supply_route_disruption | Predictive | 0.15 | Anomalous flow patterns suggesting stress |
| sanctions_pressure | Descriptive | 0.10 | Sanctions escalation and enforcement gaps |
| geopolitical_tension | Predictive | 0.10 | Regional conflict and diplomatic signals |
| alliance_alignment | Descriptive | 0.10 | NATO/EU integration and defense posture |
| comms_logistics_stress | Descriptive | 0.05 | Telecom and logistics infrastructure health |
| strategic_readiness | Descriptive | 0.10 | Military readiness and reserve capacity |

## Scoring Algorithm

For each domain *d* and country *c* at timestamp *t*:

### Step 1: Normalize Indicators

Each indicator *i* in domain *d* is normalized to a 0–100 scale:

```
normalized_i = ((raw_i - min_i) / (max_i - min_i)) × 100
```

Where `min_i` and `max_i` are computed over the full available history. If an
indicator has `direction: "lower_is_worse"`, the normalized value is inverted:

```
inverted_i = 100 - normalized_i
```

### Step 2: Weighted Sum

The domain score is the weighted sum of all available indicators:

```
score_d = Σ (normalized_i × weight_i)   for all indicators i in domain d
```

### Step 3: Data Coverage

Data coverage tracks what fraction of the domain's total weight is actually
represented by available data:

```
coverage_d = Σ weight_i (for available indicators) / Σ weight_i (for all indicators)
```

A coverage of 0.60 means only 60% of the domain's weight is backed by data.
Missing indicators reduce the score conservatively — the score is penalized
by the absence of data, not inflated by imputation.

### Step 4: Velocity & Anomaly Detection

- **Velocity**: 7-day rolling mean of daily score changes (1st derivative)
- **Anomaly flag**: Set when the velocity z-score exceeds 2.0 standard deviations

## Worked Example: Energy Dependence for Estonia

### Input Indicators (Nov 15, 2024)

| Indicator | Raw Value | Min | Max | Normalized | Direction | Weight |
|-----------|-----------|-----|-----|------------|-----------|--------|
| electricity_import_ratio | 0.45 | 0.10 | 0.80 | 50.0 | higher_is_worse | 0.20 |
| gas_import_concentration | 0.85 | 0.30 | 1.00 | 78.6 | higher_is_worse | 0.15 |
| estlink_utilization | 0.54 | 0.00 | 1.00 | 54.0 | higher_is_worse | 0.15 |
| lng_utilization | 0.30 | 0.00 | 0.90 | 33.3 | higher_is_worse | 0.10 |
| interconnectors_offline | 0 | 0 | 2 | 0.0 | higher_is_worse | 0.40 |

### Computation

```
score = (50.0 × 0.20) + (78.6 × 0.15) + (54.0 × 0.15) + (33.3 × 0.10) + (0.0 × 0.40)
      = 10.0 + 11.79 + 8.10 + 3.33 + 0.0
      = 33.22
```

Coverage = (0.20 + 0.15 + 0.15 + 0.10 + 0.40) / 1.00 = **1.00** (all indicators present)

### During Estlink 2 Outage (Jan 20, 2025)

| Indicator | Raw Value | Normalized | Weight | Contribution |
|-----------|-----------|------------|--------|-------------|
| electricity_import_ratio | 0.55 | 64.3 | 0.20 | 12.86 |
| gas_import_concentration | 0.85 | 78.6 | 0.15 | 11.79 |
| estlink_utilization | 0.82 | 82.0 | 0.15 | 12.30 |
| lng_utilization | 0.30 | 33.3 | 0.10 | 3.33 |
| interconnectors_offline | 1 | 50.0 | 0.40 | 20.00 |

```
score = 12.86 + 11.79 + 12.30 + 3.33 + 20.00 = 60.28
```

**Delta: +27.06 points** — driven primarily by `interconnectors_offline` going from 0 to 1
and `estlink_utilization` spiking as remaining capacity is stressed.

## Escalation Composite Index

The ECI is a weighted average of all 8 domain scores:

```
ECI = Σ (score_d × weight_d)   for all domains d
```

Domain weights sum to 1.0. The ECI ranges from 0 (no risk) to 100 (maximum risk).

## Risk Forecasting Model

### Algorithm: Random Forest Classifier

The production model uses a **Random Forest** (100 trees, max_depth=5) rather than
logistic regression. This decision was made because:

1. RF handles nonlinear feature interactions (e.g., high energy_dependence *combined with*
   low infrastructure_vulnerability has different implications than either alone)
2. RF provided better sensitivity on the 6-event training sample, detecting all 6 events
3. Feature importance is directly inspectable via Gini importance
4. RF is more robust to the high autocorrelation in daily domain scores

### Feature Engineering

For each domain, 4 features are computed:
- Raw score (level)
- Daily velocity (1st derivative)
- 7-day rolling volatility
- 7-day rolling mean

Total: 28 features per (country, timestamp) observation.

### Label Construction

Binary labels (0 = normal, 1 = pre-disruption) are assigned to the 7 days
**before** each documented energy-interconnector disruption event. Labels are
strictly backward-looking to prevent information leakage.

### Output

The model outputs P(disruption within 7 days) ∈ [0, 1]. This probability is
sensitivity-optimized, not calibration-optimized — it should be interpreted as
a **risk indicator** rather than a precise probability estimate.
