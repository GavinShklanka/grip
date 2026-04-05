"""Normalization utilities for GRIP scoring engine.

All normalization produces values on a 0-100 scale (domain scores)
unless otherwise noted. Higher score = greater stress/risk.

Used by: domain_index.py, escalation_composite.py, feature engineering.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def min_max_normalize(
    series: pd.Series,
    baseline_min: float | None = None,
    baseline_max: float | None = None,
) -> pd.Series:
    """Min-max normalize a Series to [0, 100].

    Parameters
    ----------
    series : pd.Series
        Raw values to normalize.
    baseline_min : float, optional
        Pre-computed minimum. If None, uses series.min().
    baseline_max : float, optional
        Pre-computed maximum. If None, uses series.max().

    Returns
    -------
    pd.Series
        Normalized values in [0, 100]. NaN propagated; constant series → 0.
    """
    s = series.astype(float)
    lo = baseline_min if baseline_min is not None else s.min()
    hi = baseline_max if baseline_max is not None else s.max()

    if hi == lo:
        # Constant series — no spread, return 0 (no stress signal)
        return pd.Series(
            np.where(s.isna(), np.nan, 0.0),
            index=series.index,
            name=series.name,
        )

    result = ((s - lo) / (hi - lo)) * 100.0
    return result.clip(0, 100)


def z_score(series: pd.Series) -> pd.Series:
    """Compute z-scores for a Series.

    Parameters
    ----------
    series : pd.Series
        Raw values.

    Returns
    -------
    pd.Series
        Z-scores. NaN propagated; constant series → 0.
    """
    s = series.astype(float)
    mean = s.mean()
    std = s.std(ddof=0)

    if std == 0 or np.isnan(std):
        return pd.Series(
            np.where(s.isna(), np.nan, 0.0),
            index=series.index,
            name=series.name,
        )

    return (s - mean) / std


def percentile_rank(value: float, distribution: pd.Series | np.ndarray) -> float:
    """Compute percentile rank of a value within a distribution.

    Parameters
    ----------
    value : float
        The value to rank.
    distribution : array-like
        Reference distribution.

    Returns
    -------
    float
        Percentile rank in [0, 100]. NaN if value is NaN or distribution is empty.
    """
    if np.isnan(value):
        return np.nan

    dist = np.asarray(distribution, dtype=float)
    dist = dist[~np.isnan(dist)]

    if len(dist) == 0:
        return np.nan

    return float(np.sum(dist <= value) / len(dist) * 100.0)


def invert_score(score: pd.Series | float) -> pd.Series | float:
    """Invert a 0-100 score (for lower_is_worse indicators).

    A raw score where lower values indicate more stress needs
    inversion so that higher normalized score = greater stress.
    """
    return 100.0 - score
