"""Temporal alignment and staleness utilities for GRIP.

Handles multi-cadence data alignment (hourly electricity, daily gas,
weekly GDELT, monthly/annual static indicators) using forward-fill.

Used by: ingestion runner, feature engineering, scoring engine.
"""

from __future__ import annotations

from datetime import datetime, timedelta
import pandas as pd


def align_timestamps(
    df: pd.DataFrame,
    target_freq: str = "D",
    time_col: str = "timestamp",
    method: str = "ffill",
) -> pd.DataFrame:
    """Resample/align a DataFrame to a target frequency.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a datetime column.
    target_freq : str
        Pandas frequency string ('D' = daily, 'H' = hourly, 'W' = weekly).
    time_col : str
        Column name containing timestamps.
    method : str
        Fill method: 'ffill' (carry forward) or 'bfill'.

    Returns
    -------
    pd.DataFrame
        Resampled DataFrame with DatetimeIndex.
    """
    if df.empty:
        return df

    result = df.copy()
    result[time_col] = pd.to_datetime(result[time_col])
    result = result.set_index(time_col)
    result = result.sort_index()

    # Resample to target frequency, applying fill method
    numeric_cols = result.select_dtypes(include="number").columns
    non_numeric_cols = [c for c in result.columns if c not in numeric_cols]

    resampled = result[numeric_cols].resample(target_freq).mean()

    if method == "ffill":
        resampled = resampled.ffill()
    elif method == "bfill":
        resampled = resampled.bfill()

    # Forward-fill non-numeric columns separately
    if non_numeric_cols:
        non_num = result[non_numeric_cols].resample(target_freq).first().ffill()
        resampled = pd.concat([resampled, non_num], axis=1)

    return resampled


def calculate_staleness(
    last_timestamp: datetime,
    now: datetime | None = None,
) -> timedelta:
    """Calculate how stale a data point is.

    Parameters
    ----------
    last_timestamp : datetime
        When the data was last updated.
    now : datetime, optional
        Current time. Defaults to utcnow().

    Returns
    -------
    timedelta
        Age of the data. Always non-negative.
    """
    if now is None:
        now = datetime.utcnow()
    delta = now - last_timestamp
    return delta if delta.total_seconds() >= 0 else timedelta(0)


def is_stale(
    last_timestamp: datetime,
    max_age: timedelta,
    now: datetime | None = None,
) -> bool:
    """Check if a data point exceeds its maximum acceptable age.

    Parameters
    ----------
    last_timestamp : datetime
        When the data was last updated.
    max_age : timedelta
        Maximum acceptable staleness.
    now : datetime, optional
        Current time. Defaults to utcnow().

    Returns
    -------
    bool
        True if data is stale (older than max_age).
    """
    return calculate_staleness(last_timestamp, now) > max_age


def get_data_cadence_max_age(cadence: str) -> timedelta:
    """Return expected max age for a given data cadence.

    Parameters
    ----------
    cadence : str
        One of: 'hourly', 'daily', 'weekly', 'monthly', 'annual'.

    Returns
    -------
    timedelta
        Acceptable max age before data is considered stale.
        Includes a grace period (2× expected cadence).
    """
    cadence_map = {
        "hourly": timedelta(hours=2),
        "daily": timedelta(days=2),
        "weekly": timedelta(weeks=2),
        "monthly": timedelta(days=60),
        "annual": timedelta(days=730),
    }
    return cadence_map.get(cadence, timedelta(days=7))
