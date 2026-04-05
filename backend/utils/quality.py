"""Data quality assessment utilities for GRIP.

Measures coverage and freshness of indicator data to support
data-quality flags in domain scores and provenance drill-down.

Used by: scoring engine, API meta endpoints, dashboard quality badges.
"""

from __future__ import annotations

from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from backend.utils.temporal import calculate_staleness


def data_coverage(
    indicators_df: pd.DataFrame,
    expected_count: int,
    indicator_col: str = "indicator_id",
) -> float:
    """Fraction of expected indicators that are present and non-null.

    Parameters
    ----------
    indicators_df : pd.DataFrame
        Available indicator values (already filtered by domain/country).
    expected_count : int
        Number of indicators expected for this domain.
    indicator_col : str
        Column that identifies distinct indicators.

    Returns
    -------
    float
        Coverage ratio in [0.0, 1.0]. 1.0 = all indicators present.
    """
    if expected_count <= 0:
        return 1.0

    if indicators_df.empty:
        return 0.0

    # Count distinct indicators that have at least one non-null value
    valid_indicators = indicators_df.dropna(subset=["raw_value"])[indicator_col].nunique()
    return min(1.0, valid_indicators / expected_count)


def freshness_score(
    timestamps: list[datetime] | pd.Series,
    max_ages: list[timedelta] | timedelta,
    now: datetime | None = None,
) -> float:
    """Combined freshness score across multiple data sources.

    Parameters
    ----------
    timestamps : list or Series of datetime
        Last-updated timestamps for each data source.
    max_ages : list of timedelta or single timedelta
        Acceptable max age for each source. If single value, applied to all.
    now : datetime, optional
        Current time. Defaults to utcnow().

    Returns
    -------
    float
        Freshness score in [0.0, 1.0]. 1.0 = all sources fully fresh.
        Score degrades linearly as data ages past its max_age, flooring at 0.
    """
    if now is None:
        now = datetime.utcnow()

    if len(timestamps) == 0:
        return 0.0

    if isinstance(max_ages, timedelta):
        max_ages = [max_ages] * len(timestamps)

    scores = []
    for ts, ma in zip(timestamps, max_ages):
        if ts is None or (isinstance(ts, float) and np.isnan(ts)):
            scores.append(0.0)
            continue

        staleness = calculate_staleness(ts, now)
        max_seconds = ma.total_seconds()

        if max_seconds <= 0:
            scores.append(1.0)
            continue

        # Fresh = 1.0, stale = linear decay, very stale = 0.0
        ratio = staleness.total_seconds() / max_seconds
        if ratio <= 1.0:
            scores.append(1.0)
        elif ratio <= 2.0:
            # Linear decay from 1.0 to 0.0 between 1× and 2× max_age
            scores.append(max(0.0, 2.0 - ratio))
        else:
            scores.append(0.0)

    return float(np.mean(scores))


def assess_quality(
    coverage: float,
    freshness: float,
) -> str:
    """Classify overall data quality from coverage and freshness.

    Parameters
    ----------
    coverage : float
        Data coverage in [0, 1].
    freshness : float
        Freshness score in [0, 1].

    Returns
    -------
    str
        Quality label: 'current', 'stale', 'interpolated', or 'missing'.
    """
    combined = coverage * freshness

    if combined >= 0.8:
        return "current"
    elif combined >= 0.5:
        return "stale"
    elif combined > 0.0:
        return "interpolated"
    else:
        return "missing"
