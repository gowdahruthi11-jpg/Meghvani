"""
Tests for Phase 8B In-Season Evaluation, baselines, and bootstrap confidence intervals.
"""
import pytest
import numpy as np
import pandas as pd

from app.ml.in_season_evaluation import (
    InSeasonWindow,
    filter_in_season_data,
    DayOfYearClimatologyBaseline,
    PersistenceBaseline,
    compute_effective_sample_size,
    block_bootstrap_confidence_intervals
)


def test_in_season_window_filter():
    dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")
    df = pd.DataFrame({"prediction_date": dates, "val": range(len(dates))})
    win = InSeasonWindow(start_month=5, start_day=25, end_month=7, end_day=31)
    filtered = filter_in_season_data(df, window=win)

    # May 25 to May 31 = 7 days
    # June = 30 days
    # July = 31 days
    # Total = 68 days
    assert len(filtered) == 68
    filtered_dates = pd.to_datetime(filtered["prediction_date"])
    assert filtered_dates.min().strftime("%m-%d") == "05-25"
    assert filtered_dates.max().strftime("%m-%d") == "07-31"


def test_day_of_year_climatology_baseline():
    dates = pd.to_datetime(["2021-06-15", "2021-06-16", "2022-06-15", "2022-07-01"])
    y = np.array([1, 1, 0, 0])
    baseline = DayOfYearClimatologyBaseline(window_days=3)
    baseline.fit(dates, y)

    eval_dates = pd.to_datetime(["2023-06-15", "2023-07-01", "2023-12-01"])
    preds = baseline.predict_proba(eval_dates)
    assert len(preds) == 3
    assert np.all(preds >= 0.0) and np.all(preds <= 1.0)
    # 06-15 should have higher probability than 12-01
    assert preds[0] >= preds[2]


def test_persistence_baseline():
    spells = np.array([0, 1, 1, 2, 5, 5, 5, 7, 7])
    y = np.array([0, 0, 0, 0, 1, 1, 1, 0, 0])
    persist = PersistenceBaseline(min_samples=2)
    persist.fit(spells, y)

    preds = persist.predict_proba(np.array([5, 0, 10]))
    assert len(preds) == 3
    assert preds[0] > preds[1]  # spell 5 had all positives
    assert np.all(preds >= 0.0) and np.all(preds <= 1.0)


def test_effective_sample_size_calculation():
    # Synthetic multi-block data
    dates = pd.date_range("2024-05-25", "2024-07-31", freq="D")
    records = []
    for b in ["BLK001", "BLK002", "BLK003"]:
        for d in dates:
            records.append({
                "block_id": b,
                "prediction_date": d,
                "rainfall_mm": 5.0 + np.random.rand()
            })
    df = pd.DataFrame(records)
    ess = compute_effective_sample_size(df)

    assert ess["n_total"] == len(df)
    assert ess["distinct_imd_grid_cells"] == 3
    assert 0 < ess["n_effective"] <= ess["n_total"]
    assert "sample_size_inflation_factor" in ess


def test_block_bootstrap_confidence_intervals():
    n = 100
    df = pd.DataFrame({
        "year": np.repeat([2021, 2022], n // 2),
        "block_id": ["BLK001", "BLK002"] * (n // 2)
    })
    y = np.random.randint(0, 2, n)
    p = np.random.uniform(0, 1, n)
    clim = np.full(n, np.mean(y))

    cis = block_bootstrap_confidence_intervals(
        eval_df=df,
        y_true=y,
        probs_dict={"test_model": p},
        clim_probs=clim,
        n_bootstraps=50,
        random_seed=42
    )

    assert "test_model" in cis
    assert "brier" in cis["test_model"]
    low, high = cis["test_model"]["brier"]
    assert low is not None and high is not None
    assert low <= high
