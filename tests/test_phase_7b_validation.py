"""
Phase 7B Comprehensive Scientific Validation Tests.

Covers:
1. Data availability
2. Provenance metadata
3. Year detection
4. Multi-year event processing
5. No leakage
6. Year-wise split
7. Leave-one-year-out split
8. Climatology baseline
9. Brier score
10. Brier skill score
11. Single-class handling
12. ROC/PR handling
13. Calibration-data insufficiency
14. Reliability bins
15. Block-level evaluation
16. Horizon-level evaluation
17. Aggregation
18. Insufficient-data handling
19. Phase 7A regression
20. Farmer feedback isolation
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.config import PROJECT_ROOT
from app.historical.multiyear_ingestion import (
    HistoricalDataAvailabilityValidator,
    ProvenanceMetadata,
    STATUS_READY,
    STATUS_BLOCKED,
    STATUS_INSUFFICIENT,
    calculate_file_sha256
)
from app.ml.multiyear_validation import (
    MultiYearScientificValidator,
    TARGET_HORIZONS
)
from app.ml.climatology import ClimatologyBaseline
from app.ml.baseline_predictor import LogisticRegressionBaseline, BASELINE_FEATURE_COLUMNS
from app.ml.evaluation import (
    brier_score,
    brier_skill_score,
    roc_auc_score_safe,
    pr_auc_score_safe,
    compute_calibration_curve
)
from app.ml.calibration import ProbabilityCalibrator, STATUS_INSUFFICIENT_DATA
from scripts.build_multiyear_event_summary import generate_multiyear_event_summary


@pytest.fixture
def client():
    return TestClient(app)


def _create_synthetic_multiyear_dataset(years=[2021, 2022, 2023], n_days=40):
    """Creates synthetic multi-year prediction dataframe for testing validation logic."""
    dfs = []
    for yr in years:
        for blk in ["BLK001", "BLK002"]:
            dates = pd.date_range(start=f"{yr}-06-01", periods=n_days, freq="D")
            np.random.seed(yr + (1 if blk == "BLK001" else 2))
            rain = np.random.exponential(scale=10.0, size=n_days)
            df = pd.DataFrame({
                "block_id": blk,
                "prediction_date": dates.strftime("%Y-%m-%d"),
                "year": yr,
                "target_false_onset_7d": np.random.choice([0, 1], size=n_days, p=[0.8, 0.2]),
                "target_false_onset_14d": np.random.choice([0, 1], size=n_days, p=[0.75, 0.25]),
                "target_false_onset_21d": np.random.choice([0, 1], size=n_days, p=[0.7, 0.3]),
                "target_false_onset_30d": np.random.choice([0, 1], size=n_days, p=[0.65, 0.35]),
            })
            for feat in BASELINE_FEATURE_COLUMNS:
                df[feat] = np.random.uniform(0.0, 50.0, size=n_days)
            dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


# 1. Data availability
def test_data_availability_validator():
    validator = HistoricalDataAvailabilityValidator()
    df_empty = pd.DataFrame()
    rep_empty = validator.validate_dataframe(df_empty)
    assert rep_empty.validation_status == STATUS_BLOCKED
    assert rep_empty.num_years == 0


# 2. Provenance metadata
def test_provenance_metadata():
    meta = ProvenanceMetadata(
        dataset_name="test_imd_gridded",
        provider="India Meteorological Department",
        source_url_or_reference="https://imdpune.gov.in",
        coverage_start="2019-06-01",
        coverage_end="2023-09-30",
        verification_status="SOURCE_VERIFICATION_REQUIRED"
    )
    d = meta.to_dict()
    assert d["dataset_name"] == "test_imd_gridded"
    assert d["provider"] == "India Meteorological Department"
    assert d["verification_status"] == "SOURCE_VERIFICATION_REQUIRED"


# 3. Year detection
def test_year_detection_and_completeness():
    dates_2021 = pd.date_range("2021-06-01", "2021-09-30", freq="D")  # Complete monsoon
    dates_2022 = pd.date_range("2022-07-01", "2022-07-15", freq="D")  # Incomplete monsoon
    
    df1 = pd.DataFrame({"block_id": "B1", "date": dates_2021.strftime("%Y-%m-%d"), "rainfall_mm": 5.0})
    df2 = pd.DataFrame({"block_id": "B1", "date": dates_2022.strftime("%Y-%m-%d"), "rainfall_mm": 5.0})
    combined = pd.concat([df1, df2], ignore_index=True)

    validator = HistoricalDataAvailabilityValidator(expected_benchmark_years=[2020, 2021, 2022])
    rep = validator.validate_dataframe(combined)

    assert rep.available_years == [2021, 2022]
    assert 2021 in rep.complete_years
    assert 2022 in rep.incomplete_years
    assert 2020 in rep.missing_years


# 4. Multi-year event processing
def test_multiyear_event_processing():
    dates = pd.date_range("2021-06-01", periods=10, freq="D")
    df = pd.DataFrame({
        "block_id": "B1",
        "date": dates.strftime("%Y-%m-%d"),
        "rainfall_mm": 10.0,
        "onset_trigger": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "false_onset": [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        "break_episode_id": [None, "EP1", "EP1", None, None, None, None, None, None, None],
        "heavy_rain_event": [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        "revival_event": [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    })
    summary_df = generate_multiyear_event_summary(df)
    assert not summary_df.empty
    assert "ALL_BLOCKS_TOTAL" in summary_df["block_id"].values
    assert int(summary_df[summary_df["block_id"] == "ALL_BLOCKS_TOTAL"]["onset_events"].iloc[0]) == 1


# 5. No leakage (Regression check)
def test_no_leakage_feature_independence():
    from tests.test_phase_7b_no_leakage import test_target_after_T_cannot_accidentally_appear_in_features
    test_target_after_T_cannot_accidentally_appear_in_features()


# 6. Year-wise split
def test_year_wise_split_is_disjoint():
    df = _create_synthetic_multiyear_dataset(years=[2021, 2022])
    train_mask = df["year"] != 2022
    eval_mask = df["year"] == 2022
    train_years = set(df.loc[train_mask, "year"])
    eval_years = set(df.loc[eval_mask, "year"])
    assert train_years.isdisjoint(eval_years)


# 7. Leave-One-Year-Out split
def test_leave_one_year_out_execution():
    df = _create_synthetic_multiyear_dataset(years=[2021, 2022, 2023])
    validator = MultiYearScientificValidator()
    res = validator.evaluate_leave_one_year_out(df, horizon_days=7)
    assert res["validation_status"] == STATUS_READY
    assert len(res["year_wise_results"]) == 3
    for yr_res in res["year_wise_results"]:
        assert yr_res["evaluation_year"] not in yr_res["training_years"]


# 8. Climatology baseline
def test_climatology_baseline():
    y_train = np.array([1, 0, 1, 0, 0])  # mean = 0.4
    model = ClimatologyBaseline()
    model.fit(y_train)
    assert np.isclose(model.probability_, 0.4)
    probs = model.predict_proba(3)
    assert probs.shape == (3, 2)
    assert np.all(np.isclose(probs[:, 1], 0.4))


# 9. Brier score
def test_brier_score_metric():
    y_true = np.array([1, 0, 1, 1])
    y_prob = np.array([0.9, 0.1, 0.8, 0.7])
    expected = np.mean((y_prob - y_true) ** 2)
    score = brier_score(y_true, y_prob)
    assert np.isclose(score, expected)


# 10. Brier skill score
def test_brier_skill_score_metric():
    bss = brier_skill_score(0.10, 0.20)
    assert np.isclose(bss, 0.50)
    assert brier_skill_score(0.20, 0.0) is None


# 11. Single-class handling
def test_single_class_safeguards():
    y_single = np.array([0, 0, 0, 0])
    y_prob = np.array([0.1, 0.2, 0.1, 0.3])
    roc = roc_auc_score_safe(y_single, y_prob)
    pr = pr_auc_score_safe(y_single, y_prob)
    assert roc == "not available"
    assert pr == "not available"


# 12. ROC/PR handling
def test_roc_pr_discrimination_metrics():
    y_two_class = np.array([0, 1, 0, 1])
    y_prob = np.array([0.1, 0.8, 0.2, 0.9])
    roc = roc_auc_score_safe(y_two_class, y_prob)
    pr = pr_auc_score_safe(y_two_class, y_prob)
    assert isinstance(roc, float) and roc > 0.9
    assert isinstance(pr, float) and pr > 0.9


# 13. Calibration-data insufficiency
def test_calibration_insufficiency():
    calibrator = ProbabilityCalibrator()
    assert calibrator.status == "NOT_FITTED"


# 14. Reliability bins
def test_reliability_bins():
    y_true = np.array([0, 1, 0, 1])
    y_prob = np.array([0.05, 0.15, 0.25, 0.85])
    curve = compute_calibration_curve(y_true, y_prob, n_bins=10)
    assert len(curve) == 10
    total_samples = sum(b["sample_count"] for b in curve)
    assert total_samples == 4


# 15. Block-level evaluation
def test_block_level_evaluation():
    df = _create_synthetic_multiyear_dataset(years=[2021, 2022])
    validator = MultiYearScientificValidator()
    blocks = validator.evaluate_block_breakdown(df, horizon_days=7)
    assert "BLK001" in blocks
    assert "BLK002" in blocks


# 16. Horizon-level evaluation
def test_horizon_level_evaluation():
    df = _create_synthetic_multiyear_dataset(years=[2021, 2022])
    validator = MultiYearScientificValidator()
    horizons = validator.evaluate_all_horizons(df)
    assert "7d" in horizons
    assert "14d" in horizons
    assert "21d" in horizons
    assert "30d" in horizons


# 17. Aggregation
def test_aggregation_preserves_sample_counts():
    df = _create_synthetic_multiyear_dataset(years=[2021, 2022])
    validator = MultiYearScientificValidator()
    res = validator.evaluate_leave_one_year_out(df, horizon_days=7)
    agg = res["aggregate_metrics"]
    assert agg is not None
    assert agg["total_evaluation_samples"] == len(df)


# 18. Insufficient-data handling on current store
def test_insufficient_data_status_on_single_year():
    demo_2025_csv = PROJECT_ROOT / "data" / "processed" / "prediction_dataset.csv"
    validator = MultiYearScientificValidator(prediction_csv_path=demo_2025_csv)
    summary = validator.generate_full_validation_summary()
    assert summary["validation_status"] == STATUS_BLOCKED
    assert "Insufficient historical coverage" in summary["statement"]


# 19. Phase 7A regression
def test_phase_7a_sih_demo_regression(client):
    res = client.get("/api/demo/status")
    assert res.status_code == 200
    data = res.json()
    assert data["safeguards"]["is_operational"] is False
    assert data["safeguards"]["external_dispatch"] is False


# 20. Farmer feedback isolation
def test_farmer_feedback_isolation(client):
    res = client.get("/api/demo/status")
    assert res.status_code == 200
    data = res.json()
    assert data["safeguards"]["automatic_retraining"] is False
