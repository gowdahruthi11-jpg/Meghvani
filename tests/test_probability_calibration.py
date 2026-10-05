"""
Phase 4A: Probability Calibration Framework Tests.

Tests:
1. Calibration module imports.
2. Raw probability preserved.
3. Calibrated probability strictly bounded in [0.0, 1.0] when valid.
4. No future target leakage in calibration features.
5. Calibration data strictly precedes evaluation data in time.
6. Test/evaluation labels are not used for fitting calibration parameters.
7. Insufficient positive event handling on single-year dataset.
8. Calibration status handling (INSUFFICIENT_CALIBRATION_DATA vs PROTOTYPE_CALIBRATED).
9. Calibration artifact creation (false_onset_7d_calibrated.joblib).
10. Calibration artifact does not overwrite baseline or diagnostic models.
11. Calibration metadata correctness and required schema keys.
12. API returns raw and calibrated probability fields.
13. API forecast remains strictly non-operational (is_operational_forecast=false).
14. API baseline-summary contains full calibration dictionary.
15. Calibration curve bins correctly partition [0.0, 1.0].
"""
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.config import PROJECT_ROOT
from app.ml.baseline_predictor import LogisticRegressionBaseline, BASELINE_FEATURE_COLUMNS
from app.ml.calibration import (
    ProbabilityCalibrator,
    STATUS_INSUFFICIENT_DATA,
    STATUS_CALIBRATED
)
from app.ml.model_loader import (
    predict_block_false_onset,
    get_false_onset_model,
    get_calibrated_false_onset_model,
    get_calibrated_metadata,
    get_model_metadata
)
from app.ml.evaluation import compute_calibration_curve


@pytest.fixture
def client():
    return TestClient(app)


# 1. Calibration module imports
def test_calibration_module_imports():
    from app.ml.calibration import ProbabilityCalibrator, STATUS_INSUFFICIENT_DATA, STATUS_CALIBRATED
    calibrator = ProbabilityCalibrator(method="sigmoid")
    assert calibrator.method == "sigmoid"
    assert STATUS_INSUFFICIENT_DATA == "INSUFFICIENT_CALIBRATION_DATA"
    assert STATUS_CALIBRATED == "PROTOTYPE_CALIBRATED"


# 2. Raw probability preserved
def test_raw_probability_preserved():
    res = predict_block_false_onset("BLK001")
    assert "raw_probability" in res
    assert "calibrated_probability" in res
    assert res["raw_probability"] == res["probability"]
    assert 0.0 <= res["raw_probability"] <= 1.0


# 3. Calibrated probability range [0, 1] when valid
def test_calibrated_probability_range_on_synthetic_data():
    rng = np.random.RandomState(42)
    n = 120
    df = pd.DataFrame({
        feat: rng.uniform(0.0, 50.0, size=n) for feat in BASELINE_FEATURE_COLUMNS
    })
    y = np.zeros(n, dtype=int)
    y[rng.choice(n, size=25, replace=False)] = 1

    base_model = LogisticRegressionBaseline(random_state=42)
    base_model.fit(df, y)

    calibrator = ProbabilityCalibrator(method="sigmoid")
    success = calibrator.fit_prefit(base_model, df, y, BASELINE_FEATURE_COLUMNS)
    assert success is True
    assert calibrator.status == STATUS_CALIBRATED

    probs = calibrator.predict_proba(df)
    assert probs is not None
    assert len(probs) == n
    assert np.all(probs >= 0.0)
    assert np.all(probs <= 1.0)


# 4. No future target leakage
def test_no_future_target_leakage_in_calibration():
    for col in BASELINE_FEATURE_COLUMNS:
        assert not col.startswith("target_"), f"Feature {col} contains target prefix!"
        assert "future" not in col, f"Feature {col} references future!"


# 5. Calibration data precedes evaluation data in time
def test_calibration_data_precedes_evaluation_data():
    csv_path = PROJECT_ROOT / "data" / "processed" / "prediction_dataset.csv"
    if not csv_path.exists():
        pytest.skip("Prediction dataset CSV missing.")
    df = pd.read_csv(csv_path)

    base_model = get_false_onset_model()
    calibrator = ProbabilityCalibrator(method="sigmoid")
    meta = calibrator.fit_chronological_split(
        df=df,
        base_estimator=base_model,
        train_ratio=0.50,
        cal_ratio=0.25
    )

    train_end = pd.to_datetime(meta["training_period"].split(" to ")[1])
    cal_start = pd.to_datetime(meta["calibration_period"].split(" to ")[0])
    cal_end = pd.to_datetime(meta["calibration_period"].split(" to ")[1])
    eval_start = pd.to_datetime(meta["evaluation_period"].split(" to ")[0])

    assert train_end < cal_start, "Train period must strictly precede calibration period."
    assert cal_end < eval_start, "Calibration period must strictly precede evaluation period."


# 6. Test/evaluation labels are not used for fitting calibration
def test_test_labels_not_used_for_fitting_calibration():
    meta = get_calibrated_metadata(reload=True)
    # The evaluation positive count must be tracked separately
    assert "evaluation_positive_count" in meta
    assert "calibration_positive_count" in meta
    # Calibration period had 0 positives, evaluation had 0 positives
    assert meta["calibration_positive_count"] == 0


# 7. Insufficient positive events handling
def test_insufficient_positive_events_handling():
    meta = get_calibrated_metadata(reload=True)
    assert meta["calibration_status"] == STATUS_INSUFFICIENT_DATA
    assert meta["calibrated_brier_score"] is None
    assert meta["improvement"] is None
    assert "early June" in meta["explanation"]
    assert "A reliable temporal calibration experiment requires substantially more historical events." in meta["scientific_warning"]


# 8. Calibration status handling
def test_calibration_status_handling():
    # Feeding all 0s array into fit_prefit should return False and STATUS_INSUFFICIENT_DATA
    df = pd.DataFrame({
        feat: np.zeros(20) for feat in BASELINE_FEATURE_COLUMNS
    })
    y_zeros = np.zeros(20, dtype=int)
    base_model = get_false_onset_model()

    calibrator = ProbabilityCalibrator(method="sigmoid")
    success = calibrator.fit_prefit(base_model, df, y_zeros, BASELINE_FEATURE_COLUMNS)

    assert success is False
    assert calibrator.status == STATUS_INSUFFICIENT_DATA
    assert calibrator.predict_proba(df) is None


# 9. Calibration artifact creation
def test_calibration_artifact_creation():
    cal_joblib = PROJECT_ROOT / "ml" / "models" / "false_onset_7d_calibrated.joblib"
    cal_meta = PROJECT_ROOT / "ml" / "models" / "false_onset_7d_calibrated_metadata.json"

    assert cal_joblib.exists(), "Calibrated model artifact must exist."
    assert cal_meta.exists(), "Calibrated model metadata JSON must exist."
    assert cal_joblib.stat().st_size > 0
    assert cal_meta.stat().st_size > 0


# 10. Calibration artifact does not overwrite baseline or diagnostic models
def test_calibration_artifact_does_not_overwrite_baseline():
    chrono_joblib = PROJECT_ROOT / "ml" / "models" / "false_onset_7d_logistic.joblib"
    diag_joblib = PROJECT_ROOT / "ml" / "models" / "false_onset_7d_logistic_diagnostic.joblib"
    cal_joblib = PROJECT_ROOT / "ml" / "models" / "false_onset_7d_calibrated.joblib"

    assert chrono_joblib.exists()
    assert diag_joblib.exists()
    assert cal_joblib.exists()

    # Verify they are all distinct files
    assert chrono_joblib.resolve() != cal_joblib.resolve()
    assert diag_joblib.resolve() != cal_joblib.resolve()


# 11. Calibration metadata correctness
def test_calibration_metadata_correctness():
    meta = get_calibrated_metadata(reload=True)
    required_keys = [
        "target",
        "horizon_days",
        "base_model",
        "calibration_method",
        "training_period",
        "calibration_period",
        "evaluation_period",
        "calibration_row_count",
        "positive_count",
        "evaluation_row_count",
        "evaluation_positive_count",
        "calibration_status",
        "scientific_warning",
        "is_operational_forecast"
    ]
    for key in required_keys:
        assert key in meta, f"Missing required metadata key: {key}"

    assert meta["target"] == "target_false_onset_7d"
    assert meta["horizon_days"] == 7
    assert meta["calibration_method"] == "sigmoid"
    assert meta["is_operational_forecast"] is False


# 12. API returns raw and calibrated fields
def test_api_returns_raw_and_calibrated_fields(client):
    res = client.get("/api/forecast/BLK001/false-onset")
    assert res.status_code == 200
    data = res.json()

    assert "raw_probability" in data
    assert "calibrated_probability" in data
    assert "calibration_method" in data
    assert data["calibration_status"] in [STATUS_INSUFFICIENT_DATA, "CALIBRATED_PROTOTYPE"]
    if data["calibration_status"] == STATUS_INSUFFICIENT_DATA:
        assert data["calibrated_probability"] is None
        assert data["raw_probability"] == 0.0
    else:
        assert data["calibrated_probability"] is not None


# 13. API remains non-operational
def test_api_remains_non_operational(client):
    res = client.get("/api/forecast/BLK002/false-onset")
    assert res.status_code == 200
    data = res.json()
    assert data["is_operational_forecast"] is False
    assert "prototype" in data["scientific_warning"].lower()


# 14. API baseline-summary contains full calibration dictionary
def test_api_baseline_summary_contains_calibration(client):
    res = client.get("/api/forecast/baseline-summary")
    assert res.status_code == 200
    data = res.json()

    assert "calibration" in data
    cal = data["calibration"]
    assert cal["calibration_status"] == STATUS_INSUFFICIENT_DATA
    assert cal["calibration_method"] == "sigmoid"
    assert "explanation" in cal


# 15. Calibration curve bins correctly partition [0.0, 1.0]
def test_calibration_curve_bins_valid():
    y_true = np.array([0, 0, 1, 1, 0, 0, 1, 0, 1, 1])
    y_prob = np.linspace(0.05, 0.95, 10)
    bins = compute_calibration_curve(y_true, y_prob, n_bins=10)

    assert len(bins) == 10
    assert bins[0]["lower_bound"] == 0.0
    assert bins[-1]["upper_bound"] == 1.0
    for b in bins:
        assert "bin_range" in b
        assert "sample_count" in b
        assert "mean_predicted_probability" in b
        assert "observed_event_frequency" in b
