# GRIP Limitations Register

## L1: Small Sample Size

**Impact: HIGH**

The risk model is trained and validated on only **6 energy-interconnector disruption events**.
This is insufficient for robust statistical inference:

- Leave-one-out cross-validation with N=6 has high variance
- Confidence intervals on detection rates are wide (binomial CI for 6/6: 54%–100%)
- A null model that randomly flags 60% of days as elevated would also detect ~4/6 events
- The model cannot be validated on unseen event types

**Quantified impact:** With 6 events, we cannot achieve statistical significance at the
p < 0.05 level for the detection rate. The 6/6 result, while promising, could occur by chance
with probability ~(0.6)^6 ≈ 4.7% for a random classifier with typical threshold.

**Mitigation:** Continue collecting events. Target 30+ events for meaningful ROC analysis.

---

## L2: Synthetic Seed Data

**Impact: HIGH**

The seed data is semi-synthetic, not real API pulls:
- ENTSO-E flows are modeled from historical patterns but not exact values
- GDELT event counts are approximations
- Gas flow values are estimates
- Sanctions counts are sourced from public reporting but may lag

**Quantified impact:** Unknown. The degree of distortion between synthetic and real data
has not been measured. Real data may have different noise characteristics, outlier patterns,
and temporal correlations.

**Mitigation:** Replace seed data with live ENTSO-E and ENTSOG API feeds once API keys
are provisioned. Cross-validate synthetic results against real data.

---

## L3: Feature Leakage Risk

**Impact: MEDIUM**

The `interconnectors_offline` indicator literally measures whether a cable is down.
When used in the feature matrix, this creates a circular relationship:

1. A cable goes offline (the event we're trying to predict)
2. `interconnectors_offline` increases
3. Domain scores increase
4. The model predicts elevated risk

**Quantified impact:** Labels are assigned to the 7-day window *before* events, so
strict leakage is prevented in training. However, if a partial outage precedes the
full event (e.g., degraded flow before complete severance), some leakage may occur.

**Mitigation:** Labels are strictly backward-looking. Feature timestamps are validated
against event dates. Future versions should add ablation studies removing
interconnectors_offline from the feature set.

---

## L4: Inability to Distinguish Sabotage from Technical Failure

**Impact: MEDIUM**

The model treats all disruptions equally. Of the 6 documented events:
- 2 are confirmed/suspected sabotage (Eagle S, Balticconnector)
- 2 are technical faults (Estlink 2 Jan 2024, Kiisa battery)
- 2 are suspected external damage (NordBalt, Estlink 1)

Sabotage events are exogenous shocks — they may have no structural precursor in the
energy grid data. The model can detect elevated *vulnerability* (e.g., high utilization
makes the grid fragile) but cannot detect *attacker intent*.

**Quantified impact:** If 50% of future events are pure sabotage with no precursor
signal, the model's real-world detection rate may be closer to 50-70% rather than 100%.

---

## L5: Temporal Autocorrelation

**Impact: MEDIUM**

Domain scores are highly autocorrelated: today's score ≈ yesterday's score ± small delta.
This means:
- Consecutive positive labels (7 days before each event) contain redundant information
- The effective training set is smaller than the nominal 5,844 samples
- Standard cross-validation assumptions (i.i.d. samples) are violated

**Quantified impact:** The effective sample size is approximately N/7 ≈ 835 independent
observations for 7-day autocorrelation length. Feature variance may be underestimated.

**Mitigation:** Future versions should use time-series-aware cross-validation (blocked
time-series CV) rather than random splits.

---

## L6: Class Imbalance and Poor Calibration

**Impact: MEDIUM**

Only 2.4% of training samples are positive. Despite `class_weight="balanced"`:
- The model systematically over-predicts risk (Brier = 0.2146 vs naive = 0.0234)
- Predicted probabilities cannot be interpreted as true frequencies
- Alert thresholds require manual tuning, not theoretical calibration

**Quantified impact:** The model is ~10× worse than naive on Brier score. This means
operations teams cannot rely on the numeric probability — they can only rely on
the *ranking* (higher probability = higher risk, relatively).

**Mitigation:** Apply post-hoc calibration (Platt scaling). Use the model for ranking
and alert prioritization, not for probability estimation.

---

## L7: Single-Country Focus

**Impact: LOW-MEDIUM**

The backtest primarily evaluates Estonia (EE). While domain scores are computed for
all four focus countries, the event register is dominated by Estonia-centric events
(4/6 involve Estlink cables). Cross-border cascade effects are modeled in the simulation
engine but not in the ML feature space.

**Mitigation:** Expand the event register with Latvia-specific and Lithuania-specific
disruption events. Add cross-border features (e.g., neighbor country stress levels).

---

## L8: Static Topology Configuration

**Impact: LOW**

The topology graph (nodes, edges, capacities) is loaded from a static JSON file.
Real-world capacity is dynamic:
- Thermal ratings vary with weather
- Maintenance outages reduce available capacity
- NTC (Net Transfer Capacity) values are published daily by TSOs

The static configuration represents design capacity, not real-time operational capacity.

**Mitigation:** Integrate ENTSO-E NTC publication feeds for dynamic capacity updates.
