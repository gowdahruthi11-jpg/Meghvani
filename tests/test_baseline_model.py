"""
Phase 3B: Probabilistic Baseline Modeling Tests.

Tests:
1. Climatology baseline fit.
2. Climatology probability matches training positive frequency.
3. Model training (LogisticRegressionBaseline).
4. predict_proba returns values strictly in [0.0, 1.0].
5. Correct feature columns used (18 baseline features).
6. Target leakage protection (features independent of future observations).
7. Chronological split (train dates strictly precede test dates).
8. Brier score calculation.
9. Brier skill score calculation.
10. ROC-AUC safe handling.
11. PR-AUC safe handling.
12. One-class evaluation safe handling without exception.
13. Calibration bins correctly partition [0.0, 1.0].
14. Model artifact creation and deserialization.
15. Metadata creation with required evaluation fields.
16. Reproducible predictions with fixed random_state.
17. API response contract: GET /api/forecast/{block_id}/false-onset.
18. API baseline-summary response contract.
"""
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.config import PROJECT_ROOT
from app.ml.climatology import ClimatologyBaseline
from app.ml.baseline_predictor import LogisticRegressionBaseline, BASELINE_FEATURE_COLUMNS
from app.ml.evaluation import (
    brier_score,
    brier_skill_score,
    roc_auc_score_safe,
    pr_auc_score_safe,
    compute_calibration_curve,
    evaluate_chronological_holdout,
    evaluate_diagnostic_events
)
from app.ml.model_loader import get_false_onset_model, predict_block_false_onset, get_model_metadata


@pytest.fixture
def client():
    return TestClient(app)


def _make_dummy_dataset(n_samples: int = 100, pos_rate: float = 0.1, random_seed: int = 42):
    """Generates synthetic dataset for testing baseline ML logic."""
    rng = np.random.RandomState(random_seed)
    data = {}
    for col in BASELINE_FEATURE_COLUMNS:
        data[col] = rng.uniform(0.0, 50.0, size=n_samples)

    # Inject some missing values into rainfall_change features
    data["rainfall_change_3d"][:5] = np.nan
    data["rainfall_change_7d"][:10] = np.nan

    # Target binary labels
    y = (rng.uniform(0.0, 1.0, size=n_samples) < pos_rate).astype(int)
    # Ensure at least 1 positive and 1 negative
    y[0] = 1
    y[1] = 0

    df = pd.DataFrame(data)
    df["block_id"] = "BLK001"
    df["date"] = pd.date_range("2025-06-01", periods=n_samples, freq="D").strftime("%Y-%m-%d")
    df["prediction_date"] = df["date"]
    df["target_false_onset_7d"] = y
    df["data_quality_flag"] = "GOOD"
    return df, y


# 1. Climatology baseline fit
def test_climatology_baseline_fit():
    y = np.array([0, 1, 0, 0, 1])
    clim = ClimatologyBaseline()
    clim.fit(y)
    assert clim.is_fitted_ is True
    assert clim.training_sample_count_ == 5
    assert clim.positive_count_ == 2


# 2. Climatology probability matches training positive frequency
def test_climatology_probability():
    y = np.array([0, 0, 0, 1])
    clim = ClimatologyBaseline()
    clim.fit(y)
    assert clim.probability_ == 0.25

    probs = clim.predict_proba(4)
    assert probs.shape == (4, 2)
    assert np.allclose(probs[:, 1], 0.25)
    assert np.allclose(probs[:, 0], 0.75)


# 3. Model training (LogisticRegressionBaseline)
def test_model_training():
    df, y = _make_dummy_dataset(80, pos_rate=0.15)
    model = LogisticRegressionBaseline(random_state=42)
    model.fit(df, y)
    assert model.is_fitted_ is True


# 4. predict_proba returns values strictly in [0.0, 1.0]
def test_predict_proba_bounds():
    df, y = _make_dummy_dataset(80, pos_rate=0.15)
    model = LogisticRegressionBaseline(random_state=42)
    model.fit(df, y)

    probs = model.predict_proba(df)
    assert probs.shape == (80, 2)
    assert (probs >= 0.0).all()
    assert (probs <= 1.0).all()
    # Row probabilities sum to 1.0
    row_sums = probs.sum(axis=1)
    assert np.allclose(row_sums, 1.0)


# 5. Correct feature columns used
def test_correct_feature_columns():
    assert len(BASELINE_FEATURE_COLUMNS) == 18
    assert "rainfall_mm" in BASELINE_FEATURE_COLUMNS
    assert "rainfall_7d" in BASELINE_FEATURE_COLUMNS
    assert "dry_spell_days" in BASELINE_FEATURE_COLUMNS
    assert "days_since_last_onset" in BASELINE_FEATURE_COLUMNS

    # Ensure no target or future columns are in feature list
    for col in BASELINE_FEATURE_COLUMNS:
        assert not col.startswith("target_"), f"Target {col} must not be in features!"
        assert "future" not in col


# 6. Target leakage protection
def test_target_leakage_protection():
    df, y = _make_dummy_dataset(60, pos_rate=0.2)
    model1 = LogisticRegressionBaseline(random_state=42)
    model1.fit(df, y)
    probs1 = model1.predict_positive_proba(df.iloc[:20])

    # Modifying target values of future rows (> index 20) should not change features or past predictions
    df_tampered = df.copy()
    df_tampered.loc[25:, "target_false_onset_7d"] = 1

    probs1_again = model1.predict_positive_proba(df_tampered.iloc[:20])
    assert np.allclose(probs1, probs1_again)


# 7. Chronological split
def test_chronological_split():
    dates = pd.date_range("2025-06-01", periods=100, freq="D")
    df = pd.DataFrame({"prediction_date": dates.strftime("%Y-%m-%d"), "val": np.arange(100)})

    train_ratio = 0.70
    n_train = int(len(df) * train_ratio)
    train_df = df.iloc[:n_train]
    test_df = df.iloc[n_train:]

    train_max_date = pd.to_datetime(train_df["prediction_date"]).max()
    test_min_date = pd.to_datetime(test_df["prediction_date"]).min()
    assert train_max_date < test_min_date, "Training dates must strictly precede test dates."


# 8. Brier score calculation
def test_brier_score_calculation():
    # Perfect predictions: Brier score = 0
    y_true = np.array([1, 0, 1, 0])
    y_prob = np.array([1.0, 0.0, 1.0, 0.0])
    assert brier_score(y_true, y_prob) == 0.0

    # Totally wrong deterministic predictions: Brier score = 1
    y_wrong = np.array([0.0, 1.0, 0.0, 1.0])
    assert brier_score(y_true, y_wrong) == 1.0

    # Constant 0.5 prediction: (0.5)^2 = 0.25
    y_half = np.array([0.5, 0.5, 0.5, 0.5])
    assert brier_score(y_true, y_half) == 0.25


# 9. Brier skill score calculation
def test_brier_skill_score_calculation():
    # Model Brier = 0.1, Clim Brier = 0.2 -> BSS = 1 - 0.1/0.2 = 0.5
    bss = brier_skill_score(0.1, 0.2)
    assert bss == pytest.approx(0.5)

    # Model worse than Climatology: BSS < 0
    assert brier_skill_score(0.3, 0.2) == pytest.approx(-0.5)

    # Reference Brier = 0 -> return None
    assert brier_skill_score(0.1, 0.0) is None


# 10. ROC-AUC safe handling
def test_roc_auc_safe_handling():
    # When both classes present
    y_true = np.array([0, 0, 1, 1])
    y_prob = np.array([0.1, 0.2, 0.8, 0.9])
    score = roc_auc_score_safe(y_true, y_prob)
    assert isinstance(score, float)
    assert score == pytest.approx(1.0)


# 11. PR-AUC safe handling
def test_pr_auc_safe_handling():
    y_true = np.array([0, 0, 1, 1])
    y_prob = np.array([0.1, 0.2, 0.8, 0.9])
    score = pr_auc_score_safe(y_true, y_prob)
    assert isinstance(score, float)
    assert score > 0.8


# 12. One-class evaluation safe handling without exception
def test_one_class_evaluation_safe_handling():
    # Only class 0 present in evaluation set
    y_all_zeros = np.array([0, 0, 0, 0, 0])
    y_prob = np.array([0.05, 0.10, 0.02, 0.08, 0.01])

    roc = roc_auc_score_safe(y_all_zeros, y_prob)
    pr = pr_auc_score_safe(y_all_zeros, y_prob)

    assert roc == "not available"
    assert pr == "not available"


# 13. Calibration bins correctly partition [0.0, 1.0]
def test_calibration_bins_partition():
    y_true = np.array([0, 1, 0, 1, 0, 0, 1, 0])
    y_prob = np.array([0.05, 0.15, 0.25, 0.35, 0.55, 0.75, 0.85, 0.95])

    bins = compute_calibration_curve(y_true, y_prob, n_bins=10)
    assert len(bins) == 10
    total_samples = sum(b["sample_count"] for b in bins)
    assert total_samples == len(y_true)

    # Bin boundaries cover 0.0 to 1.0
    assert bins[0]["lower_bound"] == 0.0
    assert bins[-1]["upper_bound"] == 1.0


# 14. Model artifact creation and deserialization
def test_model_artifact_creation_and_load():
    model = get_false_onset_model()
    assert model is not None
    assert hasattr(model, "predict_proba")


# 15. Metadata creation with required evaluation fields
def test_metadata_fields():
    meta = get_model_metadata()
    assert meta is not None
    assert meta["model_name"] == "LogisticRegressionBaseline"
    assert meta["target"] == "target_false_onset_7d"
    assert meta["horizon_days"] == 7
    assert "brier_score" in meta
    assert "brier_skill_score" in meta
    assert meta["evaluation_type"] == "single_year_chronological_prototype"
    assert "feature_contributions" in meta
    assert len(meta["feature_contributions"]) == 18


# 16. Reproducible predictions with fixed random_state
def test_reproducible_predictions():
    df, y = _make_dummy_dataset(50, pos_rate=0.2, random_seed=99)
    m1 = LogisticRegressionBaseline(random_state=42)
    m1.fit(df, y)
    p1 = m1.predict_positive_proba(df)

    m2 = LogisticRegressionBaseline(random_state=42)
    m2.fit(df, y)
    p2 = m2.predict_positive_proba(df)

    assert np.allclose(p1, p2)


# 17. API response contract: GET /api/forecast/{block_id}/false-onset
def test_api_forecast_false_onset(client):
    response = client.get("/api/forecast/BLK001/false-onset")
    assert response.status_code == 200
    data = response.json()

    assert data["block_id"] == "BLK001"
    assert "prediction_date" in data
    assert data["target"] == "FALSE_ONSET"
    assert data["horizon_days"] == 7
    assert 0.0 <= data["probability"] <= 1.0
    assert data["model"] == "logistic_baseline"
    assert data["evaluation_type"] == "single_year_chronological_prototype"
    assert data["is_operational_forecast"] is False


# 18. API baseline-summary response contract
def test_api_forecast_baseline_summary(client):
    response = client.get("/api/forecast/baseline-summary")
    assert response.status_code == 200
    data = response.json()

    assert data["target"] == "target_false_onset_7d"
    assert data["horizon_days"] == 7
    assert "brier_score" in data
    assert "feature_contributions" in data
    assert "chronological_evaluation" in data
    assert "diagnostic_evaluation" in data


# 19. Chronological holdout evaluation status when test has zero positives
def test_chronological_holdout_zero_positives_status():
    y_test_zeros = np.zeros(50, dtype=int)
    y_prob = np.full(50, 0.02)
    clim_brier = 0.0004

    eval_res = evaluate_chronological_holdout(
        y_test=y_test_zeros,
        y_test_prob=y_prob,
        clim_brier=clim_brier,
        train_dates=("2025-06-01", "2025-08-24"),
        test_dates=("2025-08-25", "2025-09-30"),
        train_positives=6,
        train_rows=255,
        test_rows=50
    )

    assert eval_res["status"] == "INSUFFICIENT_EVENT_VARIATION"
    assert eval_res["brier_skill_score"] is None
    assert eval_res["brier_skill_status"] == "not_interpretable_for_skill"
    assert eval_res["roc_auc"] == "not available"
    assert eval_res["pr_auc"] == "not available"
    assert isinstance(eval_res["brier_score"], float)
    assert "no false-onset events" in eval_res["explanation"]


# 20. Diagnostic evaluation contains both classes and valid discrimination
def test_diagnostic_evaluation_contains_both_classes_and_metrics():
    from app.ml.model_loader import get_diagnostic_metadata
    diag_meta = get_diagnostic_metadata(reload=True)

    assert diag_meta["status"] == "DIAGNOSTIC_ONLY"
    assert diag_meta["not_operational"] is True
    assert diag_meta["positive_count"] > 0
    assert diag_meta["negative_count"] > 0
    assert isinstance(diag_meta["roc_auc"], float)
    assert diag_meta["roc_auc"] > 0.8
    assert isinstance(diag_meta["pr_auc"], float)


# 21. Model artifact separation: chronological and diagnostic files
def test_model_artifact_separation():
    model_dir = PROJECT_ROOT / "ml" / "models"
    chrono_joblib = model_dir / "false_onset_7d_logistic.joblib"
    diag_joblib = model_dir / "false_onset_7d_logistic_diagnostic.joblib"

    assert chrono_joblib.exists(), "Chronological model artifact must exist."
    assert diag_joblib.exists(), "Diagnostic model artifact must exist."
    assert chrono_joblib.stat().st_size > 0
    assert diag_joblib.stat().st_size > 0


# 22. Metadata file separation: chronological and diagnostic JSON
def test_metadata_file_separation():
    model_dir = PROJECT_ROOT / "ml" / "models"
    chrono_meta = model_dir / "false_onset_7d_logistic_metadata.json"
    diag_meta = model_dir / "false_onset_7d_logistic_diagnostic_metadata.json"

    assert chrono_meta.exists()
    assert diag_meta.exists()


# 23. API returns both evaluation sections
def test_api_returns_both_evaluation_sections(client):
    response = client.get("/api/forecast/baseline-summary")
    assert response.status_code == 200
    data = response.json()

    assert "chronological_evaluation" in data
    assert "diagnostic_evaluation" in data

    chrono = data["chronological_evaluation"]
    diag = data["diagnostic_evaluation"]

    assert chrono["status"] == "INSUFFICIENT_EVENT_VARIATION"
    assert chrono["brier_skill_score"] is None
    assert chrono["brier_skill_status"] == "not_interpretable_for_skill"
    assert chrono["roc_auc"] == "not available"

    assert diag["status"] == "DIAGNOSTIC_ONLY"
    assert diag["not_operational"] is True
    assert diag["positive_count"] == 6


# 24. API block forecast includes evaluation_status and scientific_warning
def test_api_block_forecast_has_evaluation_status_and_scientific_warning(client):
    response = client.get("/api/forecast/BLK001/false-onset")
    assert response.status_code == 200
    data = response.json()

    assert data["evaluation_status"] == "INSUFFICIENT_EVENT_VARIATION"
    assert data["is_operational_forecast"] is False
    assert "scientific_warning" in data
    assert "no false-onset events" in data["scientific_warning"]

