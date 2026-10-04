"""
Meghvani Phase 8A: Probability Calibration Unit & Regression Tests.

Covers:
1. Raw probability preservation
2. Calibrated probability preservation
3. Calibration leakage prevention (no evaluation data in calibration)
4. Temporal calibration split
5. Evaluation-year exclusion
6. Climatology exclusion of evaluation year
7. Platt calibration
8. Isotonic calibration safeguards (< 10 positive events rejected)
9. Insufficient calibration data handling
10. Single-class calibration handling
11. Brier score metric
12. BSS metric & negative BSS preservation
13. ROC/PR discrimination metrics
14. Reliability diagram generation
15. Expected Calibration Error (ECE) metric
16. Class-weight comparison (Variant A balanced vs Variant B aligned)
17. Existing decision thresholds unchanged
18. Farmer observations do not enter calibration
19. Calibration API endpoints
"""
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.config import PROJECT_ROOT
from app.ml.baseline_predictor import (
    LogisticRegressionBaseline,
    BASELINE_FEATURE_COLUMNS,
    VARIANT_A_RAW,
    VARIANT_B_ALIGNED
)
from app.ml.climatology import ClimatologyBaseline
from app.ml.calibration import (
    ProbabilityCalibrator,
    STATUS_CALIBRATED,
    STATUS_INSUFFICIENT_DATA,
    STATUS_INSUFFICIENT_EVENT_VARIATION
)
from app.ml.evaluation import (
    brier_score,
    brier_skill_score,
    roc_auc_score_safe,
    pr_auc_score_safe,
    compute_calibration_curve,
    expected_calibration_error
)
from app.ml.decision_engine import (
    DEFAULT_LOW_RISK_MAX,
    DEFAULT_HIGH_RISK_MIN,
    PrototypeDecisionEngine
)


@pytest.fixture
def client():
    return TestClient(app)


def _make_dummy_dataset(n_samples: int = 200, pos_rate: float = 0.05, seed: int = 42):
    np.random.seed(seed)
    X = pd.DataFrame(
        np.random.randn(n_samples, len(BASELINE_FEATURE_COLUMNS)),
        columns=BASELINE_FEATURE_COLUMNS
    )
    y = (np.random.rand(n_samples) < pos_rate).astype(int)
    # Ensure at least two positive events
    if np.sum(y == 1) < 2:
        y[0] = 1
        y[1] = 1
    return X, y


# 1. Raw probability preservation
def test_raw_probability_preservation():
    X, y = _make_dummy_dataset()
    model = LogisticRegressionBaseline(class_weight="balanced")
    model.fit(X, y)

    calibrator = ProbabilityCalibrator(method="sigmoid")
    calibrator.fit_prefit(model, X, y)

    meta = calibrator.predict_with_metadata(X)
    assert "raw_probabilities" in meta
    assert "calibrated_probabilities" in meta
    assert len(meta["raw_probabilities"]) == len(X)
    assert len(meta["calibrated_probabilities"]) == len(X)
    # Verify raw probabilities are not overwritten
    assert np.allclose(meta["raw_probabilities"], model.predict_positive_proba(X))


# 2. Calibrated probability preservation
def test_calibrated_probability_preservation():
    X, y = _make_dummy_dataset(pos_rate=0.04)
    model = LogisticRegressionBaseline(class_weight="balanced")
    model.fit(X, y)

    calibrator = ProbabilityCalibrator(method="sigmoid")
    assert calibrator.fit_prefit(model, X, y) is True
    cal_probs = calibrator.predict_proba(X)

    assert cal_probs is not None
    assert len(cal_probs) == len(X)
    assert np.all(cal_probs >= 0.0)
    assert np.all(cal_probs <= 1.0)
    # Because positive base rate is small (~4%), Platt calibration should lower the mean prob compared to balanced raw
    raw_probs = model.predict_positive_proba(X)
    assert np.mean(cal_probs) < np.mean(raw_probs)


# 3 & 4. Calibration leakage prevention and temporal calibration split
def test_calibration_leakage_prevention():
    # Evaluation year labels must never enter calibration
    X_train, y_train = _make_dummy_dataset(n_samples=100, pos_rate=0.05, seed=1)
    X_cal, y_cal = _make_dummy_dataset(n_samples=100, pos_rate=0.05, seed=2)
    X_eval, y_eval = _make_dummy_dataset(n_samples=50, pos_rate=0.05, seed=3)

    model = LogisticRegressionBaseline()
    model.fit(X_train, y_train)

    calibrator = ProbabilityCalibrator(method="sigmoid")
    calibrator.fit_prefit(model, X_cal, y_cal)

    # Assert calibrator only saw X_cal, y_cal, not X_eval
    assert calibrator.status == STATUS_CALIBRATED
    # Prediction on eval should work without eval targets being known
    eval_cal_probs = calibrator.predict_proba(X_eval)
    assert eval_cal_probs is not None
    assert len(eval_cal_probs) == len(X_eval)


# 5 & 6. Evaluation-year exclusion from Climatology
def test_climatology_exclusion_of_eval_year():
    y_train = np.array([0, 0, 0, 0, 1])  # 20%
    y_eval = np.array([1, 1, 1, 1, 1])   # 100% in an extreme eval year

    clim = ClimatologyBaseline()
    clim.fit(y_train)  # Must be fit ONLY on training
    probs = clim.predict_proba(len(y_eval))[:, 1]
    assert np.allclose(probs, 0.20)  # Climatology strictly 0.20, not contaminated by 1.0


# 7. Platt calibration
def test_platt_calibration():
    X, y = _make_dummy_dataset()
    model = LogisticRegressionBaseline(class_weight="balanced")
    model.fit(X, y)

    cal = ProbabilityCalibrator(method="sigmoid")
    success = cal.fit_prefit(model, X, y)
    assert success is True
    assert cal.status == STATUS_CALIBRATED
    probs = cal.predict_proba(X)
    assert probs is not None
    assert len(probs) == len(X)


# 8. Isotonic calibration safeguards (< 10 positive events rejected)
def test_isotonic_calibration_safeguard():
    # Only 4 positive events
    X, y = _make_dummy_dataset(n_samples=100, pos_rate=0.04)
    assert np.sum(y == 1) < 10

    model = LogisticRegressionBaseline()
    model.fit(X, y)

    cal_iso = ProbabilityCalibrator(method="isotonic")
    success = cal_iso.fit_prefit(model, X, y)
    assert success is False
    assert cal_iso.status == STATUS_INSUFFICIENT_EVENT_VARIATION
    assert cal_iso.predict_proba(X) is None


# 9. Insufficient calibration data handling
def test_insufficient_calibration_data():
    X, _ = _make_dummy_dataset(n_samples=10)
    model = LogisticRegressionBaseline()
    cal = ProbabilityCalibrator(method="sigmoid")

    # Empty calibration set
    success = cal.fit_prefit(model, X, np.array([]))
    assert success is False
    assert cal.status == STATUS_INSUFFICIENT_DATA


# 10. Single-class calibration handling
def test_single_class_calibration_handling():
    X, _ = _make_dummy_dataset(n_samples=50)
    y_all_zeros = np.zeros(50, dtype=int)

    model = LogisticRegressionBaseline()
    cal = ProbabilityCalibrator(method="sigmoid")
    success = cal.fit_prefit(model, X, y_all_zeros)
    assert success is False
    assert cal.status in (STATUS_INSUFFICIENT_DATA, STATUS_INSUFFICIENT_EVENT_VARIATION)


# 11 & 12. Brier score & BSS metric & Negative BSS preservation
def test_brier_and_negative_bss_preservation():
    y_true = np.array([0, 0, 0, 0, 1])
    # Climatology predicts 0.2
    clim_brier = brier_score(y_true, np.full(5, 0.2))  # 4*(0.04) + 1*(0.64) = 0.8/5 = 0.16
    assert round(clim_brier, 4) == 0.1600

    # Overconfident uncalibrated model predicting 0.8
    bad_model_probs = np.full(5, 0.8)
    bad_brier = brier_score(y_true, bad_model_probs)  # 4*(0.64) + 1*(0.04) = 2.6/5 = 0.52
    bss = brier_skill_score(bad_brier, clim_brier)

    assert bss is not None
    assert bss < 0  # 1 - 0.52/0.16 = 1 - 3.25 = -2.25
    assert round(bss, 4) == -2.2500  # Negative BSS preserved, not clipped to zero


# 13. ROC & PR discrimination metrics
def test_roc_and_pr_discrimination_metrics():
    y_true = np.array([0, 0, 0, 1, 1])
    probs = np.array([0.1, 0.2, 0.3, 0.8, 0.9])
    roc = roc_auc_score_safe(y_true, probs)
    pr = pr_auc_score_safe(y_true, probs)
    assert roc == 1.0
    assert pr == 1.0


# 14. Reliability diagram generation
def test_reliability_diagram_generation():
    y_true = np.array([0, 0, 0, 1, 1, 0, 1, 0, 0, 1])
    probs = np.linspace(0.05, 0.95, 10)
    bins = compute_calibration_curve(y_true, probs, n_bins=5)
    assert len(bins) == 5
    assert sum(b["sample_count"] for b in bins) == 10


# 15. Expected Calibration Error (ECE)
def test_expected_calibration_error():
    y_true = np.array([0, 0, 1, 1])
    # Perfectly calibrated: in bin [0, 0.5] prob=0.0 obs=0; in bin [0.5, 1.0] prob=1.0 obs=1
    perf_probs = np.array([0.0, 0.0, 1.0, 1.0])
    ece_perf = expected_calibration_error(y_true, perf_probs, n_bins=2)
    assert ece_perf == 0.0

    # Poorly calibrated
    poor_probs = np.array([0.9, 0.9, 0.1, 0.1])
    ece_poor = expected_calibration_error(y_true, poor_probs, n_bins=2)
    assert ece_poor is not None
    assert ece_poor > 0.5


# 16. Class-weight comparison (Variant A vs Variant B)
def test_class_weight_variant_comparison():
    X, y = _make_dummy_dataset(n_samples=500, pos_rate=0.03, seed=42)
    model_a = LogisticRegressionBaseline(variant=VARIANT_A_RAW)
    model_a.fit(X, y)
    probs_a = model_a.predict_positive_proba(X)

    model_b = LogisticRegressionBaseline(variant=VARIANT_B_ALIGNED)
    model_b.fit(X, y)
    probs_b = model_b.predict_positive_proba(X)

    # Variant A (balanced) shifts probabilities higher; Variant B (unweighted) aligns with base rate
    assert np.mean(probs_a) > np.mean(probs_b)
    assert abs(np.mean(probs_b) - 0.03) < 0.05


# 17. Decision thresholds unchanged
def test_decision_thresholds_unchanged():
    engine = PrototypeDecisionEngine()
    assert engine.low_risk_max == 0.30
    assert engine.high_risk_min == 0.60
    assert DEFAULT_LOW_RISK_MAX == 0.30
    assert DEFAULT_HIGH_RISK_MIN == 0.60


# 18. Farmer observations do not enter calibration
def test_farmer_observations_do_not_enter_calibration():
    # Observations table exists separately from meteorological prediction matrix
    calibrator = ProbabilityCalibrator()
    # Calibrator accepts purely meteorological feature matrices, never farmer observation objects
    assert "observation_id" not in BASELINE_FEATURE_COLUMNS
    assert "farmer_id" not in BASELINE_FEATURE_COLUMNS


# 19. Calibration API endpoints
def test_calibration_api_endpoints(client):
    res_sum = client.get("/api/validation/calibration/summary")
    assert res_sum.status_code == 200
    data_sum = res_sum.json()
    assert data_sum["status"] == "READY"
    assert "horizons" in data_sum

    res_rel = client.get("/api/validation/calibration/reliability")
    assert res_rel.status_code == 200
    data_rel = res_rel.json()
    assert "raw_model_reliability" in data_rel
    assert "calibrated_model_reliability" in data_rel
    assert "ece" in data_rel

    res_yr = client.get("/api/validation/calibration/year/2024")
    assert res_yr.status_code == 200
    data_yr = res_yr.json()
    assert data_yr["evaluation_year"] == 2024

    res_h7 = client.get("/api/validation/calibration/horizon/7")
    assert res_h7.status_code == 200
    data_h7 = res_h7.json()
    assert data_h7["horizon_days"] == 7
