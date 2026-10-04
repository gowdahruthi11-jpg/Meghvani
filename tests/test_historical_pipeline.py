"""
Comprehensive tests for Phase 2 Historical Rainfall Pipeline and Event Detection Engine.
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from fastapi.testclient import TestClient

from app.historical.loader import RainfallDataLoader
from app.historical.validator import (
    RainfallValidator,
    QUALITY_GOOD,
    QUALITY_INVALID_DATA,
    QUALITY_DUPLICATE
)
from app.historical.features import (
    RainfallFeatureEngineer,
    calculate_dry_spell_days,
    calculate_wet_spell_days,
    classify_rainfall_intensity,
    INTENSITY_ZERO,
    INTENSITY_LIGHT,
    INTENSITY_MODERATE,
    INTENSITY_HEAVY
)
from app.historical.event_detector import EventDetector
from app.historical.dataset_builder import HistoricalDatasetBuilder, DATASET_COLUMNS
from app.main import app

client = TestClient(app)

# 1. Valid rainfall loading
def test_valid_rainfall_loading(tmp_path):
    csv_file = tmp_path / "valid.csv"
    csv_file.write_text("block_id,date,rainfall_mm\nBLK001,2025-06-01,15.2\nBLK001,2025-06-02,0.0\n")
    loader = RainfallDataLoader()
    df = loader.load(csv_file)
    assert len(df) == 2
    assert "source" in df.columns
    assert df.loc[0, "rainfall_mm"] == 15.2


# 2. Invalid date detection
def test_invalid_date_detection():
    data = pd.DataFrame([
        {"block_id": "BLK001", "date": "not-a-date", "rainfall_mm": 10.0},
        {"block_id": "BLK001", "date": "2025-06-02", "rainfall_mm": 5.0}
    ])
    validator = RainfallValidator()
    cleaned_df, report = validator.validate(data)
    assert report.invalid_dates == 1
    assert cleaned_df.loc[0, "data_quality_flag"] == QUALITY_INVALID_DATA
    assert cleaned_df.loc[1, "data_quality_flag"] == QUALITY_GOOD


# 3. Negative rainfall detection
def test_negative_rainfall_detection():
    data = pd.DataFrame([
        {"block_id": "BLK001", "date": "2025-06-01", "rainfall_mm": -5.0},
        {"block_id": "BLK001", "date": "2025-06-02", "rainfall_mm": 10.0}
    ])
    validator = RainfallValidator()
    cleaned_df, report = validator.validate(data)
    assert report.negative_rainfall_rows == 1
    assert cleaned_df.loc[0, "data_quality_flag"] == QUALITY_INVALID_DATA


# 4. Duplicate block/date detection
def test_duplicate_block_date_detection():
    data = pd.DataFrame([
        {"block_id": "BLK001", "date": "2025-06-01", "rainfall_mm": 10.0},
        {"block_id": "BLK001", "date": "2025-06-01", "rainfall_mm": 12.0}
    ])
    validator = RainfallValidator()
    cleaned_df, report = validator.validate(data)
    assert report.duplicate_rows == 1
    assert cleaned_df.loc[1, "data_quality_flag"] == QUALITY_DUPLICATE


# 5. Missing date sequence detection
def test_missing_date_detection():
    # Gap between 2025-06-01 and 2025-06-04 (2 days missing)
    data = pd.DataFrame([
        {"block_id": "BLK001", "date": "2025-06-01", "rainfall_mm": 5.0},
        {"block_id": "BLK001", "date": "2025-06-04", "rainfall_mm": 10.0}
    ])
    validator = RainfallValidator()
    _, report = validator.validate(data)
    assert report.missing_dates == 2
    assert any("2 missing calendar dates" in w for w in report.warnings)


# 6. Rolling 3-day rainfall
def test_rolling_3d_rainfall():
    data = pd.DataFrame([
        {"block_id": "BLK001", "date": "2025-06-01", "rainfall_mm": 5.0},
        {"block_id": "BLK001", "date": "2025-06-02", "rainfall_mm": 8.0},
        {"block_id": "BLK001", "date": "2025-06-03", "rainfall_mm": 10.0},
        {"block_id": "BLK001", "date": "2025-06-04", "rainfall_mm": 2.0}
    ])
    engineer = RainfallFeatureEngineer()
    res = engineer.compute_features(data)
    # Day 1: 5.0
    assert res.loc[0, "rainfall_3d"] == 5.0
    # Day 2: 5.0 + 8.0 = 13.0
    assert res.loc[1, "rainfall_3d"] == 13.0
    # Day 3: 5.0 + 8.0 + 10.0 = 23.0
    assert res.loc[2, "rainfall_3d"] == 23.0
    # Day 4: 8.0 + 10.0 + 2.0 = 20.0
    assert res.loc[3, "rainfall_3d"] == 20.0


# 7. Rolling 7-day rainfall
def test_rolling_7d_rainfall():
    rows = [{"block_id": "BLK001", "date": f"2025-06-{i+1:02d}", "rainfall_mm": 2.0} for i in range(10)]
    data = pd.DataFrame(rows)
    engineer = RainfallFeatureEngineer()
    res = engineer.compute_features(data)
    # Day 7 (index 6): 7 * 2.0 = 14.0
    assert res.loc[6, "rainfall_7d"] == 14.0
    # Day 10 (index 9): 7 * 2.0 = 14.0
    assert res.loc[9, "rainfall_7d"] == 14.0


# 8. Dry spell calculation
def test_dry_spell_calculation():
    # Sequence of rainfall: 0.0, 1.0, 2.0, 5.0, 0.0, 0.5
    # With ceiling = 2.5 mm: Dry days are < 2.5mm: True, True, True, False, True, True
    series = pd.Series([0.0, 1.0, 2.0, 5.0, 0.0, 0.5])
    dry = calculate_dry_spell_days(series, dry_ceiling_mm=2.5)
    assert list(dry) == [1, 2, 3, 0, 1, 2]


# 9. Onset trigger detection (threshold met)
def test_onset_trigger_detection():
    data = pd.DataFrame([
        {"block_id": "BLK001", "date": "2025-06-01", "rainfall_mm": 5.0},
        {"block_id": "BLK001", "date": "2025-06-02", "rainfall_mm": 8.0},
        {"block_id": "BLK001", "date": "2025-06-03", "rainfall_mm": 10.0} # 23mm >= 20mm
    ])
    detector = EventDetector()
    res = detector.detect_onset_trigger(data)
    assert res.loc[0, "onset_trigger"] == 0
    assert res.loc[1, "onset_trigger"] == 0
    assert res.loc[2, "onset_trigger"] == 1
    assert res.loc[2, "onset_trigger_date"] == "2025-06-03"


# 10. No onset when threshold not met
def test_no_onset_when_threshold_not_met():
    data = pd.DataFrame([
        {"block_id": "BLK001", "date": "2025-06-01", "rainfall_mm": 2.0},
        {"block_id": "BLK001", "date": "2025-06-02", "rainfall_mm": 3.0},
        {"block_id": "BLK001", "date": "2025-06-03", "rainfall_mm": 4.0} # 9mm < 20mm
    ])
    detector = EventDetector()
    res = detector.detect_onset_trigger(data)
    assert (res["onset_trigger"] == 0).all()


# 11. False onset detection (dry spell following onset)
def test_false_onset_detection():
    # 3 onset days (total 25mm), then 8 consecutive dry days (< 2.5mm)
    rows = [
        {"block_id": "BLK001", "date": "2025-06-01", "rainfall_mm": 5.0},
        {"block_id": "BLK001", "date": "2025-06-02", "rainfall_mm": 10.0},
        {"block_id": "BLK001", "date": "2025-06-03", "rainfall_mm": 10.0}, # onset trigger here
    ]
    # Add 8 dry days (June 4 to June 11)
    for i in range(4, 12):
        rows.append({"block_id": "BLK001", "date": f"2025-06-{i:02d}", "rainfall_mm": 0.0})

    df = pd.DataFrame(rows)
    detector = EventDetector()
    df = detector.detect_onset_trigger(df)
    df = detector.detect_false_onset(df)

    assert df.loc[2, "onset_trigger"] == 1
    assert df.loc[2, "false_onset"] == 1
    assert df.loc[2, "dry_spell_length"] >= 7
    assert df.loc[2, "dry_spell_start"] == "2025-06-04"


# 12. No false onset when dry spell is absent
def test_no_false_onset_when_dry_spell_absent():
    # 3 onset days, followed by 10 days of healthy rain (10mm each day)
    rows = [
        {"block_id": "BLK001", "date": "2025-06-01", "rainfall_mm": 8.0},
        {"block_id": "BLK001", "date": "2025-06-02", "rainfall_mm": 8.0},
        {"block_id": "BLK001", "date": "2025-06-03", "rainfall_mm": 10.0},
    ]
    for i in range(4, 14):
        rows.append({"block_id": "BLK001", "date": f"2025-06-{i:02d}", "rainfall_mm": 10.0})

    df = pd.DataFrame(rows)
    detector = EventDetector()
    df = detector.detect_onset_trigger(df)
    df = detector.detect_false_onset(df)

    assert df.loc[2, "onset_trigger"] == 1
    assert df.loc[2, "false_onset"] == 0


# 13. Break detection (consecutive dry days >= 5)
def test_break_detection():
    # 6 dry days (June 1-6)
    rows = [{"block_id": "BLK001", "date": f"2025-06-{i+1:02d}", "rainfall_mm": 0.5} for i in range(6)]
    # Day 7 rain
    rows.append({"block_id": "BLK001", "date": "2025-06-07", "rainfall_mm": 15.0})

    df = pd.DataFrame(rows)
    detector = EventDetector()
    df = detector.detect_break(df)

    assert (df.loc[0:5, "break_event"] == 1).all()
    assert df.loc[0, "break_duration_days"] == 6
    assert df.loc[6, "break_event"] == 0


# 14. Heavy rain detection
def test_heavy_rain_detection():
    data = pd.DataFrame([
        {"block_id": "BLK001", "date": "2025-06-01", "rainfall_mm": 15.0},
        {"block_id": "BLK001", "date": "2025-06-02", "rainfall_mm": 75.0} # >= 64.5mm
    ])
    detector = EventDetector()
    df = detector.detect_heavy_rain(data)
    assert df.loc[0, "heavy_rain_event"] == 0
    assert df.loc[1, "heavy_rain_event"] == 1
    assert df.loc[1, "heavy_rainfall_mm"] == 75.0


# 15. Revival detection
def test_revival_detection():
    # 5 dry days (break spell), followed by 2 days of rain summing to 20mm (>= 15mm)
    rows = [{"block_id": "BLK001", "date": f"2025-06-{i+1:02d}", "rainfall_mm": 0.0} for i in range(5)]
    rows.append({"block_id": "BLK001", "date": "2025-06-06", "rainfall_mm": 10.0})
    rows.append({"block_id": "BLK001", "date": "2025-06-07", "rainfall_mm": 10.0})

    df = pd.DataFrame(rows)
    detector = EventDetector()
    df = detector.detect_break(df)
    df = detector.detect_revival(df)

    assert df.loc[4, "break_event"] == 1
    assert df.loc[5, "revival_event"] == 1
    assert df.loc[5, "revival_rainfall_mm"] == 20.0


# 16. Missing values are not treated as zero
def test_missing_values_are_not_treated_as_zero():
    series = pd.Series([0.0, 0.0, np.nan, 0.0])
    dry = calculate_dry_spell_days(series, dry_ceiling_mm=2.5)
    # The nan must break the dry spell streak rather than being counted as a dry day!
    assert dry[0] == 1
    assert dry[1] == 2
    assert dry[2] == 0
    assert dry[3] == 1


# 17. Multiple blocks processed independently
def test_multiple_blocks_processed_independently():
    data = pd.DataFrame([
        {"block_id": "BLK001", "date": "2025-06-01", "rainfall_mm": 50.0},
        {"block_id": "BLK001", "date": "2025-06-02", "rainfall_mm": 50.0},
        {"block_id": "BLK002", "date": "2025-06-01", "rainfall_mm": 0.0},
        {"block_id": "BLK002", "date": "2025-06-02", "rainfall_mm": 0.0},
    ])
    engineer = RainfallFeatureEngineer()
    res = engineer.compute_features(data)

    blk1 = res[res["block_id"] == "BLK001"].reset_index(drop=True)
    blk2 = res[res["block_id"] == "BLK002"].reset_index(drop=True)

    assert blk1.loc[1, "rainfall_3d"] == 100.0
    assert blk2.loc[1, "rainfall_3d"] == 0.0
    assert blk1.loc[1, "dry_spell_days"] == 0
    assert blk2.loc[1, "dry_spell_days"] == 2


# 18. Historical dataset generation and export
def test_historical_dataset_generation(tmp_path):
    raw_csv = tmp_path / "raw_rain.csv"
    out_csv = tmp_path / "processed_events.csv"
    raw_csv.write_text(
        "block_id,date,rainfall_mm\n"
        "BLK001,2025-06-01,10.0\n"
        "BLK001,2025-06-02,15.0\n"
        "BLK001,2025-06-03,20.0\n"
    )
    builder = HistoricalDatasetBuilder()
    result = builder.build_from_source(raw_csv, output_csv_path=out_csv)

    assert out_csv.exists()
    assert result["summary"]["valid_rows"] == 3
    assert result["summary"]["events_detected"]["onset_triggers"] >= 1
    df = pd.read_csv(out_csv)
    for col in DATASET_COLUMNS:
        assert col in df.columns


# 19. API summary endpoint
def test_api_historical_summary():
    response = client.get("/api/historical/summary")
    assert response.status_code == 200
    data = response.json()
    assert "blocks" in data
    assert "records" in data
    assert "onset_triggers" in data
    assert "false_onsets" in data
    assert "break_events" in data
    assert "heavy_rain_events" in data
    assert "revival_events" in data
    assert "PROTOTYPE" in data["disclaimer"]


# 20. API event filtering
def test_api_historical_event_filtering():
    response = client.get("/api/historical/events?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    response_heavy = client.get("/api/historical/events?event_type=heavy_rain")
    assert response_heavy.status_code == 200
    for evt in response_heavy.json():
        assert evt["heavy_rain_event"] == 1


# 21. API block details
def test_api_historical_block_details():
    response = client.get("/api/historical/BLK001?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["block_id"] == "BLK001"
    assert len(data["records"]) <= 10


# 22. Data leakage check: features strictly backward looking
def test_data_leakage_predictor_features():
    # If we alter future row rainfall, earlier row features must remain completely unchanged
    data1 = pd.DataFrame([
        {"block_id": "BLK001", "date": "2025-06-01", "rainfall_mm": 5.0},
        {"block_id": "BLK001", "date": "2025-06-02", "rainfall_mm": 10.0},
        {"block_id": "BLK001", "date": "2025-06-03", "rainfall_mm": 20.0},
    ])
    data2 = pd.DataFrame([
        {"block_id": "BLK001", "date": "2025-06-01", "rainfall_mm": 5.0},
        {"block_id": "BLK001", "date": "2025-06-02", "rainfall_mm": 10.0},
        {"block_id": "BLK001", "date": "2025-06-03", "rainfall_mm": 500.0}, # drastically changed future row
    ])

    engineer = RainfallFeatureEngineer()
    res1 = engineer.compute_features(data1)
    res2 = engineer.compute_features(data2)

    # Days 1 and 2 must have identical predictor features
    for col in ["rainfall_1d", "rainfall_3d", "rainfall_5d", "rainfall_7d", "rainfall_14d", "dry_spell_days"]:
        assert res1.loc[0, col] == res2.loc[0, col]
        assert res1.loc[1, col] == res2.loc[1, col]


# 23. Consecutive wet days do not create repeated primary onset events
def test_consecutive_wet_days_do_not_create_repeated_primary_onset():
    # 5 consecutive rainy days with heavy cumulative rainfall
    data = pd.DataFrame([
        {"block_id": "BLK001", "date": "2025-06-01", "rainfall_mm": 5.0},
        {"block_id": "BLK001", "date": "2025-06-02", "rainfall_mm": 8.0},
        {"block_id": "BLK001", "date": "2025-06-03", "rainfall_mm": 10.0}, # onset trigger here (23mm >= 20mm)
        {"block_id": "BLK001", "date": "2025-06-04", "rainfall_mm": 15.0}, # subsequent heavy rain
        {"block_id": "BLK001", "date": "2025-06-05", "rainfall_mm": 20.0},
    ])
    detector = EventDetector()
    res = detector.detect_onset_trigger(data)
    assert res.loc[2, "onset_trigger"] == 1
    assert res.loc[3, "onset_trigger"] == 0
    assert res.loc[4, "onset_trigger"] == 0
    assert (res["onset_trigger"] == 1).sum() == 1


# 24. A qualifying onset is followed by onset lockout
def test_qualifying_onset_followed_by_lockout():
    rows = [
        {"block_id": "BLK001", "date": "2025-06-01", "rainfall_mm": 5.0},
        {"block_id": "BLK001", "date": "2025-06-02", "rainfall_mm": 8.0},
    ]
    for i in range(2, 25):
        rows.append({"block_id": "BLK001", "date": f"2025-06-{i+1:02d}", "rainfall_mm": 10.0})
    data = pd.DataFrame(rows)
    detector = EventDetector()
    res = detector.detect_onset_trigger(data)
    # Day 3 (index 2) is the first qualifying onset trigger (5 + 8 + 10 = 23mm)
    assert res.loc[2, "onset_trigger"] == 1
    # All days within lockout (days 4 through 25) must have onset_trigger == 0
    assert (res.loc[3:, "onset_trigger"] == 0).all()


# 25. Mid-season rainfall does not become repeated onset labels
def test_mid_season_rainfall_suppressed_as_onset():
    # First onset on Day 3, ongoing light showers for 35 days (past lockout), then a heavy burst
    rows = [{"block_id": "BLK001", "date": f"2025-06-{i+1:02d}", "rainfall_mm": 10.0 if i < 3 else 4.0} for i in range(30)]
    # Add July rows (days 31 to 40)
    for j in range(1, 11):
        rows.append({"block_id": "BLK001", "date": f"2025-07-{j:02d}", "rainfall_mm": 15.0 if j in [5, 6, 7] else 3.0})
    data = pd.DataFrame(rows)
    detector = EventDetector()
    res = detector.detect_onset_trigger(data)
    # The mid-season July burst (July 5-7) was NOT preceded by a dry period, so it is suppressed
    july_triggers = res[res["date"].str.startswith("2025-07")]["onset_trigger"]
    assert (july_triggers == 0).all()


# 26. Break days remain available as row-level break_event labels
def test_break_days_remain_available_as_row_level_break_event():
    rows = [{"block_id": "BLK001", "date": f"2025-06-{i+1:02d}", "rainfall_mm": 0.0} for i in range(7)]
    df = pd.DataFrame(rows)
    detector = EventDetector()
    res = detector.detect_break(df)
    assert (res["break_event"] == 1).all()
    assert (res["break_duration_days"] == 7).all()
    assert "break_episode_id" in res.columns
    assert (res["break_episode_id"] == "BLK001_BREAK_001").all()


# 27. A 9-day dry spell counts as ONE break episode
def test_nine_day_dry_spell_counts_as_one_break_episode():
    rows = [{"block_id": "BLK001", "date": f"2025-06-{i+1:02d}", "rainfall_mm": 0.0} for i in range(9)]
    df = pd.DataFrame(rows)
    detector = EventDetector()
    res = detector.detect_break(df)
    assert (res["break_event"] == 1).sum() == 9 # 9 break days
    assert res["break_episode_id"].dropna().nunique() == 1 # exactly 1 distinct episode


# 28. Multiple separate dry spells count as multiple break episodes
def test_multiple_separate_dry_spells_count_as_multiple_break_episodes():
    # Spell 1: June 1-6 (6 dry days)
    rows = [{"block_id": "BLK001", "date": f"2025-06-{i+1:02d}", "rainfall_mm": 0.0} for i in range(6)]
    # Wet interlude: June 7-10 (4 wet days)
    for i in range(6, 10):
        rows.append({"block_id": "BLK001", "date": f"2025-06-{i+1:02d}", "rainfall_mm": 20.0})
    # Spell 2: June 11-17 (7 dry days)
    for i in range(10, 17):
        rows.append({"block_id": "BLK001", "date": f"2025-06-{i+1:02d}", "rainfall_mm": 0.5})

    df = pd.DataFrame(rows)
    detector = EventDetector()
    res = detector.detect_break(df)
    assert (res["break_event"] == 1).sum() == 13 # 6 + 7 = 13 break days
    assert res["break_episode_id"].dropna().nunique() == 2 # 2 distinct episodes
    assert set(res["break_episode_id"].dropna().unique()) == {"BLK001_BREAK_001", "BLK001_BREAK_002"}


# 29. Summary returns break_spell_days_count and distinct_break_episodes
def test_summary_returns_break_days_and_distinct_episodes():
    response = client.get("/api/historical/summary")
    assert response.status_code == 200
    data = response.json()
    assert "break_spell_days_count" in data
    assert "distinct_break_episodes" in data
    assert data["break_spell_days_count"] >= data["distinct_break_episodes"]
    assert data["distinct_break_episodes"] > 0
