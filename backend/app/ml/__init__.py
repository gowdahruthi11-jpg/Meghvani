"""
Meghvani ML Package - Phase 3B: Probabilistic Baseline Modeling.
"""
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
from app.ml.calibration import (
    ProbabilityCalibrator,
    STATUS_INSUFFICIENT_DATA,
    STATUS_CALIBRATED
)
from app.ml.decision_engine import PrototypeDecisionEngine
from app.ml.model_loader import get_false_onset_model, predict_block_false_onset

__all__ = [
    "ClimatologyBaseline",
    "LogisticRegressionBaseline",
    "BASELINE_FEATURE_COLUMNS",
    "brier_score",
    "brier_skill_score",
    "roc_auc_score_safe",
    "pr_auc_score_safe",
    "compute_calibration_curve",
    "evaluate_chronological_holdout",
    "evaluate_diagnostic_events",
    "ProbabilityCalibrator",
    "STATUS_INSUFFICIENT_DATA",
    "STATUS_CALIBRATED",
    "PrototypeDecisionEngine",
    "get_false_onset_model",
    "predict_block_false_onset"
]

