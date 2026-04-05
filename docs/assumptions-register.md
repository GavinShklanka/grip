# GRIP Assumptions Register

## Source of Truth Reference

This register tracks all assumptions from the GRIP Source of Truth document (§4)
with their current validation status.

---

## Architecture Assumptions

| ID | Assumption | Status | Evidence | Impact if Wrong |
|----|-----------|--------|----------|-----------------|
| A1 | ENTSO-E Transparency Platform provides hourly cross-border flow data | **Validated** (demo mode) | Seed CSVs model real ENTSO-E format; live API tested | Loss of electricity indicators |
| A2 | ENTSOG provides daily gas flow data at interconnection points | **Validated** (demo mode) | Seed CSVs model real ENTSOG format | Loss of gas indicators |
| A3 | SQLite is sufficient for demo; PostgreSQL for production | **Validated** | All tests pass with SQLite; Dockerfile includes PostgreSQL | Performance issues at scale |
| A4 | Demo mode can replicate all functionality without external APIs | **Validated** | Full pipeline runs with DEMO_MODE=True | External dependency in demo |

## Scoring Assumptions

| ID | Assumption | Status | Evidence | Impact if Wrong |
|----|-----------|--------|----------|-----------------|
| S1 | Min-max normalization produces meaningful 0–100 scores | **Assumed** | Works in practice; sensitive to outliers | Score instability with extreme values |
| S2 | Linear weighted sum is appropriate for domain aggregation | **Assumed** | Standard in composite indices (HDI, WGI) | May miss nonlinear interactions |
| S3 | Missing indicators should lower scores conservatively | **Validated** | Data coverage penalty implemented; verified M12 | Overestimated scores with gaps |
| S4 | estlink_utilization should measure against available (not total) capacity | **Validated** | Fix applied M12 remediation; energy_dependence now increases during outage (+13.46) | Inverted scoring direction |
| S5 | Indicator weights in domains.json are reasonable | **Assumed** | Based on domain expertise; not empirically optimized | Suboptimal score sensitivity |
| S6 | 7-day rolling window is appropriate for velocity/anomaly detection | **Assumed** | Common in time series; not tuned | May miss faster or slower signals |

## Model Assumptions

| ID | Assumption | Status | Evidence | Impact if Wrong |
|----|-----------|--------|----------|-----------------|
| M1 | Random Forest is appropriate for this classification task | **Validated** | 6/6 detection rate; interpretable feature importance | Wrong model family |
| M2 | 7 days is an appropriate prediction horizon | **Assumed** | Balances lead time with signal clarity; not tuned | Too short to be actionable, or too long for signal |
| M3 | class_weight="balanced" compensates for class imbalance | **Partially validated** | Achieves high sensitivity but poor calibration (Brier 0.2146) | Over-prediction of risk |
| M4 | Historical disruption patterns generalize to future events | **Assumed** | Only 6 events available; unknown if future events follow same patterns | Model fails on novel event types |
| M5 | Labels assigned 7 days before events prevent leakage | **Validated** | Label construction verified; no post-event features used | Training on leaked information |

## Data Assumptions

| ID | Assumption | Status | Evidence | Impact if Wrong |
|----|-----------|--------|----------|-----------------|
| D1 | Seed data approximates real-world distributions | **Assumed** | Modeled from public reporting; not validated against API | Biased training |
| D2 | GDELT event counts correlate with geopolitical tension | **Assumed** | Standard in political science literature; noisy measure | False signals |
| D3 | Shadow fleet estimates are meaningful | **Assumed** | Based on open-source maritime intelligence; uncertain | Inaccurate sanctions pressure |
| D4 | Static indicators (annual cadence) are useful despite low temporal resolution | **Assumed** | They capture structural factors; slow-moving by design | Domains appear flat |

## Infrastructure Assumptions

| ID | Assumption | Status | Evidence | Impact if Wrong |
|----|-----------|--------|----------|-----------------|
| I1 | Topology.json capacities reflect installed capacity accurately | **Assumed** | Verified against public TSO data; static | Incorrect margins |
| I2 | N-1 criterion applies uniformly across Baltic states | **Validated** | Post-BRELL desynchronization confirmed | Wrong reserve assumptions |
| I3 | Submarine cables are the primary vulnerability | **Validated** | 5/6 documented events involve submarine infrastructure | Overemphasis on cable risk |
| I4 | 500 MW reserve per Baltic state is the correct fragmentation | **Assumed** | Simplified from 1500 MW shared requirement | Reserve arithmetic wrong |

## Governance Assumptions

| ID | Assumption | Status | Evidence | Impact if Wrong |
|----|-----------|--------|----------|-----------------|
| G1 | uncertainty is visible (P7) | **Validated** | data_coverage field exposed on all domain scores | Hidden uncertainty |
| G2 | honest failure > cosmetic success (P9) | **Validated** | Brier score honestly reported; model limitations documented | Overstated capabilities |
| G3 | Engines are pure functions (§6) | **Validated** | domain_index.py refactored to pure function; no DB imports | Untestable engines |

---

## Summary

| Status | Count |
|--------|-------|
| **Validated** | 14 |
| **Partially Validated** | 1 |
| **Assumed** | 12 |
| **Failed** | 0 |

All critical path assumptions (A1-A4, S3-S4, M5, G1-G3) are validated.
Remaining "Assumed" items are either standard analytical practices (S1, S2)
or require more data to validate (M4, D1-D4).
