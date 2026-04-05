import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from backend.utils.normalization import (
    min_max_normalize,
    z_score,
    percentile_rank,
    invert_score,
)
from backend.utils.temporal import (
    align_timestamps,
    calculate_staleness,
    is_stale,
    get_data_cadence_max_age,
)
from backend.utils.quality import (
    data_coverage,
    freshness_score,
    assess_quality,
)


def test_min_max_normalize():
    # Normal case
    s = pd.Series([10, 20, 30])
    res = min_max_normalize(s)
    assert res.tolist() == [0.0, 50.0, 100.0]

    # With explicit baseline
    res2 = min_max_normalize(s, baseline_min=0, baseline_max=40)
    assert res2.tolist() == [25.0, 50.0, 75.0]

    # Pre-clipping if out of baseline
    s_out = pd.Series([-10, 50])
    res3 = min_max_normalize(s_out, baseline_min=0, baseline_max=40)
    assert res3.tolist() == [0.0, 100.0]

    # Constant series
    s_const = pd.Series([10, 10, 10])
    res4 = min_max_normalize(s_const)
    assert res4.tolist() == [0.0, 0.0, 0.0]

    # NaN handling
    s_nan = pd.Series([10, np.nan, 30])
    res5 = min_max_normalize(s_nan)
    assert np.isnan(res5[1])
    assert res5[0] == 0.0
    assert res5[2] == 100.0


def test_z_score():
    s = pd.Series([1, 2, 3, 4, 5])
    res = z_score(s)
    assert np.isclose(res.mean(), 0.0)
    assert np.isclose(res.std(ddof=0), 1.0)

    # Constant series
    s_const = pd.Series([1, 1, 1])
    res2 = z_score(s_const)
    assert res2.tolist() == [0.0, 0.0, 0.0]

    # NaN handling
    s_nan = pd.Series([1, np.nan, 3])
    res3 = z_score(s_nan)
    assert np.isnan(res3[1])


def test_percentile_rank():
    dist = np.array([10, 20, 30, 40, 50])
    assert percentile_rank(30, dist) == 60.0
    assert percentile_rank(10, dist) == 20.0
    assert percentile_rank(60, dist) == 100.0
    assert percentile_rank(5, dist) == 0.0

    # NaN handling
    assert np.isnan(percentile_rank(np.nan, dist))
    assert np.isnan(percentile_rank(30, []))


def test_invert_score():
    assert invert_score(20) == 80.0
    s = pd.Series([0, 50, 100])
    res = invert_score(s)
    assert res.tolist() == [100.0, 50.0, 0.0]


def test_align_timestamps():
    dates = pd.date_range("2024-01-01", "2024-01-03", freq="D")
    df = pd.DataFrame({"timestamp": dates, "val": [10, 20, 30]})

    # Resample to hourly with ffill
    res = align_timestamps(df, target_freq="h")
    assert len(res) == 49 # 3 days = 48 hours + start
    assert res.index.freqstr == "h"
    assert res["val"].iloc[1] == 10.0 # ffill

    # Handle empty
    assert align_timestamps(pd.DataFrame()).empty


def test_staleness():
    now = datetime(2024, 1, 2, 12, 0, 0)
    last_update = datetime(2024, 1, 1, 12, 0, 0) # 24 hours ago

    assert calculate_staleness(last_update, now) == timedelta(days=1)
    
    # Future timestamp shouldn't give negative staleness
    assert calculate_staleness(now, last_update) == timedelta(0)

    assert is_stale(last_update, timedelta(hours=12), now) is True
    assert is_stale(last_update, timedelta(hours=48), now) is False
    
    # Test cadence
    assert get_data_cadence_max_age("hourly") == timedelta(hours=2)


def test_data_quality():
    df = pd.DataFrame({
        "indicator_id": ["a", "b", "c", "c"], # c is duplicated
        "raw_value": [1.0, np.nan, 2.0, 3.0]
    })
    
    # Expected 3 distinct indicators. 'a' and 'c' have non-null. 'b' is null.
    # So 2 out of 3 = 0.666
    assert np.isclose(data_coverage(df, 3), 2/3)
    assert data_coverage(df, 0) == 1.0
    assert data_coverage(pd.DataFrame(), 3) == 0.0


def test_freshness_score():
    now = datetime(2024, 1, 1, 12, 0, 0)
    
    # Exactly fresh
    scores1 = freshness_score([now], timedelta(hours=1), now=now)
    assert scores1 == 1.0

    # Halfway through decay (1.5x max_age)
    ts_stale = now - timedelta(hours=1, minutes=30)
    scores2 = freshness_score([ts_stale], timedelta(hours=1), now=now)
    assert np.isclose(scores2, 0.5)

    # Completely stale (>2x max_age)
    ts_dead = now - timedelta(hours=3)
    scores3 = freshness_score([ts_dead], timedelta(hours=1), now=now)
    assert scores3 == 0.0
    
    # Mixed list
    scores4 = freshness_score([now, ts_stale, ts_dead], timedelta(hours=1), now=now)
    assert np.isclose(scores4, (1.0 + 0.5 + 0.0) / 3)


def test_assess_quality():
    assert assess_quality(1.0, 1.0) == "current" # 1.0
    assert assess_quality(1.0, 0.6) == "stale" # 0.6
    assert assess_quality(0.5, 0.5) == "interpolated" # 0.25
    assert assess_quality(0.0, 1.0) == "missing" # 0.0
