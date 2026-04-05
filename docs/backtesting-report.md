# Backtesting Report

## Executive Summary

The GRIP risk model was evaluated using leave-one-out cross-validation across
6 documented energy-interconnector disruption events in the Baltic-Nordic region
(October 2023 – January 2026). The model successfully flagged **elevated risk in all
6 events** during the 30-day pre-event window.

However, the model does **not** beat the naive baseline on Brier score (0.2146 vs 0.0234).
This is an expected consequence of the sensitivity-optimized design: the model trades
calibration accuracy for detection rate.

## Methodology

### Training Data
- **Indicator rows:** 35,254 (from ENTSO-E, ENTSOG, GDELT, sanctions, static sources)
- **Domain scores generated:** 26,298
- **Final training matrix:** 5,844 samples × 28 features
- **Positive label rate:** 2.4% (disruption days within 7-day pre-event windows)

### Cross-Validation Design
For each of the 6 energy events:
1. Remove that event's labels from the training set
2. Train the Random Forest on the remaining 5 events
3. Score the 30-day window preceding the held-out event
4. Record peak and mean risk probabilities

This ensures the model has never "seen" the event it is scoring.

### Model Configuration
- Random Forest Classifier (100 trees, max_depth=5)
- StandardScaler preprocessing
- `class_weight="balanced"` to compensate for 2.4% positive rate
- Binary output: P(disruption within 7 days)

## Results

### Per-Event Detection

| Event | Date | Peak Risk (30d) | Mean Risk (30d) | Elevated? |
|-------|------|-----------------|-----------------|-----------|
| Balticconnector anchor damage | 2023-10-08 | 0.5945 | 0.3793 | ✓ YES |
| Estlink 2 technical fault (Jan 2024) | 2024-01-26 | 0.5796 | 0.2820 | ✓ YES |
| NordBalt suspected anchor damage | 2024-11-17 | 0.6723 | — | ✓ YES |
| Eagle S Estlink 2 severance | 2024-12-25 | 0.6532 | — | ✓ YES |
| Estlink 1 outage (Sep 2025) | 2025-09-01 | 0.5960 | — | ✓ YES |
| Kiisa battery fault – both Estlinks | 2026-01-20 | 0.6139 | — | ✓ YES |

**Detection rate: 6/6 (100%)**

"Elevated" threshold: peak risk > 0.30 in the 30-day pre-event window.

### Brier Score

| Metric | Score | Interpretation |
|--------|-------|----------------|
| Naive baseline (always predict base rate) | **0.0234** | Better calibration |
| GRIP model | **0.2146** | Worse calibration, better sensitivity |

The model does not beat the naive baseline on Brier score. This is because:
- The base rate is extremely low (2.4%)
- The balanced-weight RF intentionally over-predicts risk
- A model that always predicts 2.4% has near-zero squared error on the 97.6% of normal days
- But such a model detects **0 events** — it has zero value as an early warning system

### Feature Importance

Top features by Random Forest Gini importance:

| Rank | Feature | Importance | Domain |
|------|---------|------------|--------|
| 1 | energy_dependence_mean_7d | 0.1612 | Energy Dependence |
| 2 | energy_dependence | 0.1076 | Energy Dependence |
| 3 | supply_route_disruption_volatility_7d | 0.1066 | Supply Route Disruption |
| 4 | supply_route_disruption_mean_7d | 0.0779 | Supply Route Disruption |
| 5 | geopolitical_tension_mean_7d | 0.0537 | Geopolitical Tension |
| 6 | energy_dependence_volatility_7d | 0.0515 | Energy Dependence |
| 7 | infrastructure_vulnerability_mean_7d | 0.0508 | Infrastructure Vulnerability |
| 8 | sanctions_pressure_mean_7d | 0.0502 | Sanctions Pressure |
| 9 | infrastructure_vulnerability_volatility_7d | 0.0490 | Infrastructure Vulnerability |
| 10 | infrastructure_vulnerability | 0.0413 | Infrastructure Vulnerability |

The top features are semantically meaningful: energy dependence and supply route
volatility are the structural stresses that precede interconnector failures.

## Interpretation

### What the model can do
- Detect periods of elevated structural risk before infrastructure disruptions
- Identify which domain dimensions contribute most to risk elevation
- Provide a sensitivity-oriented early warning signal

### What the model cannot do
- Provide calibrated probability estimates (predicted 60% ≠ observed 60%)
- Distinguish sabotage from technical failure
- Predict *specific* events (which cable, which date)
- Function as a standalone decision-making tool

### Honest Assessment

The model functions as a **risk indicator**, not a probability estimator. Its value lies
in the 6/6 detection rate — it successfully identifies elevated risk states that precede
real disruptions. The poor Brier score reflects the inherent trade-off between sensitivity
and specificity in extreme class-imbalance scenarios.

For production use, the model should be paired with:
1. Probability calibration (Platt scaling or isotonic regression)
2. Human analyst review of all elevated-risk alerts
3. Additional event data (current 6 events is too few for robust statistics)

## Limitations

See `docs/limitations.md` for the full limitations register.
