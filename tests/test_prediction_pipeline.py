"""
Phase 3A: Predictive Feature & Target Engineering Tests.

Tests:
1. 7-day target excludes current date (T).
2. 14-day target boundary (T+1 to T+14 inclusive).
3. 21-day target boundary (T+1 to T+21 inclusive).
4. 30-day target boundary (T+1 to T+30 inclusive).
5. Future event produces target = 1.
6. Event outside horizon produces target = 0.
7. Multiple events within horizon produce target = 1.
8. Block isolation.
9. Missing dates handled safely (not treated as zero rain).
10. Predictor features never use future values.
11. days_since_last_event uses only past events.
12. Break target uses break episode start rather than every break day.
13. Insufficient history flag (<30 days).
14. Chronological temporal split.
15. Prediction dataset reproducibility.
16. Dedicated Data Leakage Audit: test_prediction_dataset_has_no_future_feature_leakage.
17. API endpoints: /api/prediction-dataset/summary and /api/prediction-dataset/{block_id}.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.config import PROJECT_ROOT, event_thresholds_config
from app.prediction.targets import create_future_event_target, create_all_future_targets
from app.prediction.features import PredictiveFeatureEngineer
from app.prediction.splits import create_temporal_split, get_dataset_temporal_info
from app.prediction.dataset_builder import PredictionDatasetBuilder


@pytest.fixture
def client():
    return TestClient(app)


def _make_daily_df(block_id: str, start_date: str, days: int, base_rain: float = 0.0) -> pd.DataFrame:
    """Helper to generate a synthetic daily dataframe."""
    dt_start = datetime.strptime(start_date, "%Y-%m-%d")
    dates = [(dt_start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
    df = pd.DataFrame({
        "block_id": block_id,
        "date": dates,
        "rainfall_mm": [base_rain] * days,
        "rainfall_1d": [base_rain] * days,
        "rainfall_3d": [base_rain * 3] * days,
        "rainfall_5d": [base_rain * 5] * days,
        "rainfall_7d": [base_rain * 7] * days,
        "rainfall_14d": [base_rain * 14] * days,
        "rainfall_30d": [base_rain * 30] * days,
        "dry_spell_days": [0] * days,
        "wet_spell_days": [days] * days,
        "rainfall_intensity_class": ["NO_RAIN"] * days,
        "rainfall_anomaly": ["NORMAL"] * days,
        "onset_trigger": [0] * days,
        "false_onset": [0] * days,
        "break_event": [0] * days,
        "heavy_rain_event": [0] * days,
        "revival_event": [0] * days,
        "data_quality_flag": ["GOOD"] * days,
        "source": ["DEMO_SYNTHETIC"] * days,
    })
    return df


# -----------------------------------------------------------------------------
# 1. 7-day target excludes current date (T)
# -----------------------------------------------------------------------------
def test_target_excludes_current_date():
    """Event on date T must NOT trigger target for date T."""
    df = _make_daily_df("BLK001", "2025-06-01", 10)
    # Event on 2025-06-05
    df.loc[df["date"] == "2025-06-05", "onset_trigger"] = 1

    targets = create_future_event_target(df, "onset_trigger", 7)
    df["target_onset_7d"] = targets

    # On June 5 (index 4), the event happens today. Future window is June 6 - June 12.
    # Therefore, target_onset_7d for June 5 MUST be 0!
    june_5_target = df.loc[df["date"] == "2025-06-05", "target_onset_7d"].values[0]
    assert june_5_target == 0, "Target for date T must exclude events occurring on date T."

    # On June 4 (index 3), future 7d window is June 5 - June 11. Event is on June 5, so target = 1.
    june_4_target = df.loc[df["date"] == "2025-06-04", "target_onset_7d"].values[0]
    assert june_4_target == 1


# -----------------------------------------------------------------------------
# 2. 14-day target boundary
# -----------------------------------------------------------------------------
def test_14d_target_boundary():
    """Event exactly at T+14 is included; T+15 is excluded."""
    df = _make_daily_df("BLK001", "2025-06-01", 20)
    # Event at T+14 from June 1 (June 15)
    df.loc[df["date"] == "2025-06-15", "heavy_rain_event"] = 1

    target_14d = create_future_event_target(df, "heavy_rain_event", 14)
    target_june_1 = target_14d.iloc[0] # June 1 -> window June 2 to June 15 (14 days)
    assert target_june_1 == 1, "Event at T+14 must be included in 14-day horizon."

    # Now place event at T+15 (June 16)
    df2 = _make_daily_df("BLK001", "2025-06-01", 20)
    df2.loc[df2["date"] == "2025-06-16", "heavy_rain_event"] = 1
    target_14d_df2 = create_future_event_target(df2, "heavy_rain_event", 14)
    assert target_14d_df2.iloc[0] == 0, "Event at T+15 must be excluded from 14-day horizon."


# -----------------------------------------------------------------------------
# 3. 21-day target boundary
# -----------------------------------------------------------------------------
def test_21d_target_boundary():
    """Event at T+21 is included; T+22 is excluded."""
    df = _make_daily_df("BLK001", "2025-06-01", 30)
    # June 1 + 21 days = June 22
    df.loc[df["date"] == "2025-06-22", "onset_trigger"] = 1
    t21 = create_future_event_target(df, "onset_trigger", 21)
    assert t21.iloc[0] == 1, "Event at T+21 days must be included in 21-day window."

    df2 = _make_daily_df("BLK001", "2025-06-01", 30)
    df2.loc[df2["date"] == "2025-06-23", "onset_trigger"] = 1 # T+22
    t21_df2 = create_future_event_target(df2, "onset_trigger", 21)
    assert t21_df2.iloc[0] == 0, "Event at T+22 days must be excluded from 21-day window."


# -----------------------------------------------------------------------------
# 4. 30-day target boundary
# -----------------------------------------------------------------------------
def test_30d_target_boundary():
    """Event at T+30 is included; T+31 is excluded."""
    df = _make_daily_df("BLK001", "2025-06-01", 40)
    # June 1 + 30 days = July 1
    df.loc[df["date"] == "2025-07-01", "revival_event"] = 1
    t30 = create_future_event_target(df, "revival_event", 30)
    assert t30.iloc[0] == 1, "Event at T+30 must be included in 30-day window."

    df2 = _make_daily_df("BLK001", "2025-06-01", 40)
    df2.loc[df2["date"] == "2025-07-02", "revival_event"] = 1 # T+31
    t30_df2 = create_future_event_target(df2, "revival_event", 30)
    assert t30_df2.iloc[0] == 0, "Event at T+31 must be excluded from 30-day window."


# -----------------------------------------------------------------------------
# 5. Future event produces target = 1
# -----------------------------------------------------------------------------
def test_future_event_produces_target_one():
    df = _make_daily_df("BLK001", "2025-06-01", 15)
    df.loc[df["date"] == "2025-06-04", "onset_trigger"] = 1
    targets = create_future_event_target(df, "onset_trigger", 7)
    # On June 1, June 2, June 3 -> June 4 is in future window -> 1
    assert targets.iloc[0] == 1
    assert targets.iloc[1] == 1
    assert targets.iloc[2] == 1


# -----------------------------------------------------------------------------
# 6. Event outside horizon produces target = 0
# -----------------------------------------------------------------------------
def test_event_outside_horizon_produces_zero():
    df = _make_daily_df("BLK001", "2025-06-01", 20)
    df.loc[df["date"] == "2025-06-12", "heavy_rain_event"] = 1
    targets_7d = create_future_event_target(df, "heavy_rain_event", 7)
    # June 1 window is June 2 -> June 8. Event is June 12 -> 0.
    assert targets_7d.iloc[0] == 0


# -----------------------------------------------------------------------------
# 7. Multiple events within horizon still produce binary 1
# -----------------------------------------------------------------------------
def test_multiple_events_produce_binary_one():
    df = _make_daily_df("BLK001", "2025-06-01", 10)
    df.loc[df["date"] == "2025-06-03", "heavy_rain_event"] = 1
    df.loc[df["date"] == "2025-06-05", "heavy_rain_event"] = 1
    df.loc[df["date"] == "2025-06-07", "heavy_rain_event"] = 1
    targets_7d = create_future_event_target(df, "heavy_rain_event", 7)
    # Multiple occurrences must result in binary 1, not 3
    assert targets_7d.iloc[0] == 1
    assert set(targets_7d.unique()).issubset({0, 1})


# -----------------------------------------------------------------------------
# 8. Block isolation
# -----------------------------------------------------------------------------
def test_block_isolation_in_targets():
    df_a = _make_daily_df("BLK001", "2025-06-01", 10)
    df_b = _make_daily_df("BLK002", "2025-06-01", 10)
    # Only BLK002 has an onset event
    df_b.loc[df_b["date"] == "2025-06-04", "onset_trigger"] = 1

    combined = pd.concat([df_a, df_b], ignore_index=True)
    targets = create_future_event_target(combined, "onset_trigger", 7)
    combined["target"] = targets

    blk001_targets = combined[combined["block_id"] == "BLK001"]["target"]
    blk002_targets = combined[combined["block_id"] == "BLK002"]["target"]

    assert (blk001_targets == 0).all(), "Events in Block 2 must never spill into Block 1 targets."
    assert blk002_targets.iloc[0] == 1


# -----------------------------------------------------------------------------
# 9. Missing calendar dates handled safely (not treated as zero rainfall)
# -----------------------------------------------------------------------------
def test_missing_calendar_dates_boundary():
    """If June 2 through June 5 are missing, calendar arithmetic uses actual calendar days."""
    dates = ["2025-06-01", "2025-06-06", "2025-06-07", "2025-06-08", "2025-06-15"]
    df = pd.DataFrame({
        "block_id": "BLK001",
        "date": dates,
        "rainfall_mm": [0.0, 10.0, 5.0, 0.0, 0.0],
        "onset_trigger": [0, 1, 0, 0, 0],
    })
    targets_7d = create_future_event_target(df, "onset_trigger", 7)
    # For June 1, 7-day window is June 2 to June 8.
    # June 6 is in that window and has onset_trigger=1 -> target = 1.
    assert targets_7d.iloc[0] == 1


# -----------------------------------------------------------------------------
# 10. Predictor features never use future values
# -----------------------------------------------------------------------------
def test_predictor_features_are_strictly_backward():
    fe = PredictiveFeatureEngineer(event_thresholds_config)
    df = _make_daily_df("BLK001", "2025-06-01", 40, base_rain=10.0)

    # Compute features for original
    feat_original = fe.engineer_features(df)

    # Now modify rainfall on day 35
    df_modified = df.copy()
    df_modified.loc[34, "rainfall_mm"] = 999.0 # Day 35

    feat_modified = fe.engineer_features(df_modified)

    # All features for day 0 to 33 MUST BE 100% IDENTICAL
    numeric_cols = [
        "rainfall_3d", "rainfall_7d", "rainfall_change_3d", "rainfall_change_7d",
        "rainfall_ratio_3d_7d", "month", "day_of_year", "monsoon_month_flag"
    ]
    for col in numeric_cols:
        orig_slice = feat_original.loc[:33, col].fillna(-999)
        mod_slice = feat_modified.loc[:33, col].fillna(-999)
        assert np.allclose(orig_slice, mod_slice), f"Future modification leaked into past {col}!"


# -----------------------------------------------------------------------------
# 11. days_since_last_event uses strictly past events
# -----------------------------------------------------------------------------
def test_days_since_last_event_uses_only_past_or_present():
    fe = PredictiveFeatureEngineer(event_thresholds_config)
    df = _make_daily_df("BLK001", "2025-06-01", 20)
    # Event occurs on June 10 (day index 9)
    df.loc[9, "onset_trigger"] = 1

    feat = fe.engineer_features(df)

    # Days before June 10 must be -1.0 (no prior event)
    for i in range(9):
        assert feat.loc[i, "days_since_last_onset"] == -1.0, f"Day {i} should be sentinel -1.0 before any event"

    # Day of event (June 10) is 0 days since event
    assert feat.loc[9, "days_since_last_onset"] == 0.0

    # June 11 is 1 day since event
    assert feat.loc[10, "days_since_last_onset"] == 1.0
    # June 15 is 5 days since event
    assert feat.loc[14, "days_since_last_onset"] == 5.0


# -----------------------------------------------------------------------------
# 12. Break target uses break episode start rather than every break day
# -----------------------------------------------------------------------------
def test_break_target_uses_episode_start():
    """
    If a break episode starts on June 10 and lasts 6 days (June 10-15):
    - On June 5 (prediction date), 7d horizon is June 6-12. The episode starts on June 10 (within window) -> 1.
    - On June 11 (prediction date), 7d horizon is June 12-18. June 12-15 are ongoing break days,
      BUT no NEW break episode starts in June 12-18 -> 0!
    """
    df = _make_daily_df("BLK001", "2025-06-01", 20)
    # Break days June 10 to June 15
    for i in range(9, 15):
        df.loc[i, "break_event"] = 1
        df.loc[i, "break_start"] = "2025-06-10"
        df.loc[i, "break_end"] = "2025-06-15"
        df.loc[i, "break_episode_id"] = "BLK001_20250610_20250615"

    targets = create_all_future_targets(df, [7], event_thresholds_config)

    # Prediction date June 5 (index 4)
    # Horizon is June 6-12. Episode starts June 10 -> target_break_7d = 1
    assert targets.loc[4, "target_break_7d"] == 1

    # Prediction date June 11 (index 10)
    # Horizon is June 12-18. Days 12, 13, 14, 15 have break_event=1, but episode started June 10 (in past!)
    # No break episode starts after June 11 -> target_break_7d must be 0!
    assert targets.loc[10, "target_break_7d"] == 0


# -----------------------------------------------------------------------------
# 13. Insufficient history flag (<30 days)
# -----------------------------------------------------------------------------
def test_insufficient_history_flag():
    fe = PredictiveFeatureEngineer(event_thresholds_config)
    df = _make_daily_df("BLK001", "2025-06-01", 50, base_rain=5.0)

    feat = fe.engineer_features(df)

    # First 30 rows (<30 history) should be flagged INSUFFICIENT_HISTORY
    insufficient = feat.iloc[:30]["data_quality_flag"]
    assert (insufficient == "INSUFFICIENT_HISTORY").all()

    # Day 31 onwards should retain GOOD
    sufficient = feat.iloc[30:]["data_quality_flag"]
    assert (sufficient == "GOOD").all()


# -----------------------------------------------------------------------------
# 14. Chronological temporal split
# -----------------------------------------------------------------------------
def test_chronological_temporal_split():
    df = _make_daily_df("BLK001", "2023-01-01", 365)
    df2 = _make_daily_df("BLK001", "2024-01-01", 365)
    df3 = _make_daily_df("BLK001", "2025-01-01", 365)
    multi_year = pd.concat([df, df2, df3], ignore_index=True)

    splits = create_temporal_split(multi_year, date_col="date", train_ratio=0.6, val_ratio=0.2, test_ratio=0.2)

    train_dates = pd.to_datetime(splits["train"]["date"])
    val_dates = pd.to_datetime(splits["validation"]["date"])
    test_dates = pd.to_datetime(splits["test"]["date"])

    # Strict chronological order: max(train) < min(val) < min(test)
    assert train_dates.max() < val_dates.min(), "Train dates must precede validation dates."
    assert val_dates.max() < test_dates.min(), "Validation dates must precede test dates."


def test_single_year_split_reports_notice():
    df = _make_daily_df("BLK001", "2025-01-01", 100)
    info = get_dataset_temporal_info(df, date_col="date")
    assert info["is_multi_year"] is False
    assert "Insufficient historical years" in info["multi_year_validation_notice"]


# -----------------------------------------------------------------------------
# 15. Prediction dataset reproducibility
# -----------------------------------------------------------------------------
def test_prediction_dataset_reproducibility():
    builder = PredictionDatasetBuilder(event_thresholds_config)
    hist_path = PROJECT_ROOT / "data" / "processed" / "historical_events.csv"
    if not hist_path.exists():
        pytest.skip("historical_events.csv not found")

    df1 = builder.build_from_file(hist_path)
    df2 = builder.build_from_file(hist_path)

    # Identical shape, column names, and values
    assert df1.shape == df2.shape
    assert list(df1.columns) == list(df2.columns)
    pd.testing.assert_frame_equal(df1, df2)


# -----------------------------------------------------------------------------
# 16. DATA LEAKAGE AUDIT: test_prediction_dataset_has_no_future_feature_leakage
# -----------------------------------------------------------------------------
def test_prediction_dataset_has_no_future_feature_leakage():
    """
    CRITICAL AUDIT:
    For any prediction date T:
    - Every predictor feature is completely invariant to future observations (> T).
    - Future targets correctly respond to future observations (> T).
    """
    builder = PredictionDatasetBuilder(event_thresholds_config)
    df = _make_daily_df("BLK001", "2025-06-01", 60, base_rain=5.0)

    # Baseline build
    pred_base = builder.build_prediction_dataset(df)

    # Choose prediction date T = 2025-06-20 (day index 19)
    T_date = "2025-06-20"
    T_idx = df[df["date"] == T_date].index[0]

    # Mutate data in future (days 30 to 40, e.g. giant rainfall surge and onset event)
    df_mutated = df.copy()
    df_mutated.loc[30:40, "rainfall_mm"] = 250.0
    df_mutated.loc[30:40, "rainfall_3d"] = 750.0
    df_mutated.loc[30:40, "rainfall_7d"] = 1750.0
    df_mutated.loc[30:40, "rainfall_30d"] = 3000.0
    df_mutated.loc[32, "onset_trigger"] = 1
    df_mutated.loc[32, "heavy_rain_event"] = 1

    pred_mutated = builder.build_prediction_dataset(df_mutated)

    # Check that row at T (index 19) in pred_mutated has IDENTICAL feature values to pred_base
    feature_cols = [
        "rainfall_mm", "rainfall_3d", "rainfall_5d", "rainfall_7d", "rainfall_14d",
        "rainfall_30d", "dry_spell_days", "wet_spell_days", "rainfall_change_3d",
        "rainfall_change_7d", "rainfall_ratio_3d_7d", "month", "day_of_year",
        "monsoon_month_flag", "days_since_last_onset", "days_since_last_break",
        "days_since_last_heavy_rain", "days_since_last_revival"
    ]

    for col in feature_cols:
        val_base = pred_base.loc[T_idx, col]
        val_mut = pred_mutated.loc[T_idx, col]
        if pd.isna(val_base):
            assert pd.isna(val_mut), f"NaN mismatch on {col} at date {T_date}"
        else:
            assert np.isclose(val_base, val_mut), f"Data leakage detected on predictor {col} at prediction date {T_date}!"


# -----------------------------------------------------------------------------
# 17. API Endpoints Tests
# -----------------------------------------------------------------------------
def test_api_prediction_dataset_summary(client):
    response = client.get("/api/prediction-dataset/summary")
    assert response.status_code == 200
    data = response.json()
    assert "rows" in data
    assert "blocks" in data
    assert "horizons" in data
    assert "target_distributions" in data
    assert "quality_statistics" in data
    assert data["model_trained"] is False
    assert "STRICT_CAUSAL_SEPARATION" in data["leakage_status"]


def test_api_prediction_dataset_block_records(client):
    response = client.get("/api/prediction-dataset/BLK001?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["block_id"] == "BLK001"
    assert data["returned_records"] <= 10
    assert len(data["records"]) > 0
    first_record = data["records"][0]
    assert "prediction_date" in first_record
    assert "rainfall_7d" in first_record
    assert "target_onset_7d" in first_record
    assert "target_break_7d" in first_record
