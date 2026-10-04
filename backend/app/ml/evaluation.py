"""
Evaluation metrics for probabilistic forecasting (Meghvani Phase 3B).
Includes Brier Score, Brier Skill Score, safe ROC-AUC/PR-AUC, and calibration analysis.
"""
from typing import Dict, Any, List, Optional, Union
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score


def brier_score(y_true: Union[np.ndarray, pd.Series, list], y_prob: Union[np.ndarray, pd.Series, list]) -> float:
    """
    Computes Brier Score: mean((probability - actual)^2).
    Lower is better (0 = perfect deterministic forecast).
    """
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_prob, dtype=float)

    if len(y_t) == 0:
        raise ValueError("Cannot compute Brier Score on empty array.")
    if len(y_t) != len(y_p):
        raise ValueError(f"Length mismatch: y_true ({len(y_t)}) vs y_prob ({len(y_p)}).")

    return float(np.mean((y_p - y_t) ** 2))


def brier_skill_score(brier_model: float, brier_reference: float) -> Optional[float]:
    """
    Computes Brier Skill Score (BSS) against a reference climatology baseline:
    BSS = 1.0 - (Brier_model / Brier_reference)
    BSS > 0 indicates forecast improvement over climatology.
    Returns None if reference Brier score is zero or undefined.
    """
    if brier_reference is None or np.isnan(brier_reference) or brier_reference <= 0.0:
        return None
    return float(1.0 - (brier_model / brier_reference))


def roc_auc_score_safe(
    y_true: Union[np.ndarray, pd.Series, list],
    y_prob: Union[np.ndarray, pd.Series, list]
) -> Union[float, str]:
    """
    Computes ROC-AUC strictly when both classes (0 and 1) are present in evaluation data.
    If evaluation data contains only one class, safely returns 'not available' without crashing.
    """
    y_t = np.asarray(y_true, dtype=int)
    y_p = np.asarray(y_prob, dtype=float)

    unique_classes = np.unique(y_t)
    if len(unique_classes) < 2:
        return "not available"

    try:
        return float(roc_auc_score(y_t, y_p))
    except Exception:
        return "not available"


def pr_auc_score_safe(
    y_true: Union[np.ndarray, pd.Series, list],
    y_prob: Union[np.ndarray, pd.Series, list]
) -> Union[float, str]:
    """
    Computes Precision-Recall AUC (Average Precision) strictly when both classes are present.
    If evaluation data contains only one class, safely returns 'not available'.
    """
    y_t = np.asarray(y_true, dtype=int)
    y_p = np.asarray(y_prob, dtype=float)

    unique_classes = np.unique(y_t)
    if len(unique_classes) < 2:
        return "not available"

    try:
        return float(average_precision_score(y_t, y_p))
    except Exception:
        return "not available"


def compute_calibration_curve(
    y_true: Union[np.ndarray, pd.Series, list],
    y_prob: Union[np.ndarray, pd.Series, list],
    n_bins: int = 10
) -> List[Dict[str, Any]]:
    """
    Reliability diagram analysis.
    Groups predictions into probability intervals and computes observed event frequency.
    
    Returns list of dicts for each bin:
    - bin_range: e.g. "0.0-0.1"
    - sample_count: number of predictions in bin
    - mean_predicted_probability: average predicted P(Y=1) in bin (or None if empty)
    - observed_event_frequency: empirical proportion of true positives (or None if empty)
    """
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_prob, dtype=float)

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    results: List[Dict[str, Any]] = []

    for i in range(n_bins):
        low = bin_edges[i]
        high = bin_edges[i + 1]

        # For the final bin, include right boundary 1.0
        if i == n_bins - 1:
            mask = (y_p >= low) & (y_p <= high)
        else:
            mask = (y_p >= low) & (y_p < high)

        count = int(np.sum(mask))
        bin_label = f"{low:.1f}-{high:.1f}"

        if count > 0:
            mean_prob = float(np.mean(y_p[mask]))
            obs_freq = float(np.mean(y_t[mask]))
        else:
            mean_prob = None
            obs_freq = None

        results.append({
            "bin_index": i,
            "bin_range": bin_label,
            "lower_bound": round(float(low), 2),
            "upper_bound": round(float(high), 2),
            "sample_count": count,
            "mean_predicted_probability": round(mean_prob, 4) if mean_prob is not None else None,
            "observed_event_frequency": round(obs_freq, 4) if obs_freq is not None else None
        })

    return results


def evaluate_chronological_holdout(
    y_test: Union[np.ndarray, pd.Series, list],
    y_test_prob: Union[np.ndarray, pd.Series, list],
    clim_brier: float,
    train_dates: tuple,
    test_dates: tuple,
    train_positives: int,
    train_rows: int,
    test_rows: int
) -> Dict[str, Any]:
    """
    Evaluates chronological holdout performance with scientific integrity.
    If the test target contains zero positive events (or only one class):
    flags status as INSUFFICIENT_EVENT_VARIATION, sets brier_skill_score to None,
    and returns 'not available' for discrimination metrics.
    """
    y_t = np.asarray(y_test, dtype=int)
    y_p = np.asarray(y_test_prob, dtype=float)

    test_positives = int(np.sum(y_t == 1))
    test_negatives = int(np.sum(y_t == 0))
    br = brier_score(y_t, y_p)

    has_both_classes = len(np.unique(y_t)) >= 2

    if not has_both_classes:
        status = "INSUFFICIENT_EVENT_VARIATION"
        bss = None
        bss_status = "not_interpretable_for_skill"
        roc = "not available"
        pr = "not available"
        explanation = (
            "The chronological test period contains no false-onset events. "
            "Therefore discrimination metrics such as ROC-AUC and PR-AUC cannot be computed, "
            "and the Brier/Brier Skill results should not be interpreted as verified forecast skill."
        )
    else:
        status = "EVALUATED"
        bss = brier_skill_score(br, clim_brier)
        bss_status = "interpretable"
        roc = roc_auc_score_safe(y_t, y_p)
        pr = pr_auc_score_safe(y_t, y_p)
        explanation = "Both classes present in chronological test split."

    return {
        "evaluation_type": "single_year_chronological_prototype",
        "status": status,
        "train_start": str(train_dates[0]),
        "train_end": str(train_dates[1]),
        "test_start": str(test_dates[0]),
        "test_end": str(test_dates[1]),
        "train_rows": train_rows,
        "test_rows": test_rows,
        "train_positive_count": train_positives,
        "test_positive_count": test_positives,
        "test_negative_count": test_negatives,
        "brier_score": round(br, 4),
        "brier_skill_score": round(bss, 4) if bss is not None else None,
        "brier_skill_status": bss_status,
        "roc_auc": roc if isinstance(roc, str) else round(roc, 4),
        "pr_auc": pr if isinstance(pr, str) else round(pr, 4),
        "explanation": explanation
    }


def evaluate_diagnostic_events(
    y_true: Union[np.ndarray, pd.Series, list],
    y_prob: Union[np.ndarray, pd.Series, list]
) -> Dict[str, Any]:
    """
    Evaluates historical event-focused diagnostic capacity on observations containing events.
    Explicitly labeled as diagnostic only — not an operational forecast evaluation.
    """
    y_t = np.asarray(y_true, dtype=int)
    y_p = np.asarray(y_prob, dtype=float)

    pos = int(np.sum(y_t == 1))
    neg = int(np.sum(y_t == 0))
    total = len(y_t)
    pos_rate = round(float(pos / total), 4) if total > 0 else 0.0

    br = brier_score(y_t, y_p)
    roc = roc_auc_score_safe(y_t, y_p)
    pr = pr_auc_score_safe(y_t, y_p)
    calib = compute_calibration_curve(y_t, y_p, n_bins=10)

    return {
        "evaluation_type": "single_year_historical_diagnostic",
        "status": "DIAGNOSTIC_ONLY",
        "total_diagnostic_rows": total,
        "positive_count": pos,
        "negative_count": neg,
        "positive_rate": pos_rate,
        "brier_score": round(br, 4),
        "roc_auc": roc if isinstance(roc, str) else round(roc, 4),
        "pr_auc": pr if isinstance(pr, str) else round(pr, 4),
        "calibration_bins": calib,
        "not_operational": True,
        "explanation": (
            "Diagnostic only — not a temporal forecast-skill estimate. "
            "Evaluates model capacity to separate historical false-onset events from non-events."
        )
    }


def expected_calibration_error(
    y_true: Union[np.ndarray, pd.Series, list],
    y_prob: Union[np.ndarray, pd.Series, list],
    n_bins: int = 10
) -> Optional[float]:
    """
    Computes Expected Calibration Error (ECE):
    ECE = sum_{b=1}^B (|B_b| / N) * |acc(B_b) - conf(B_b)|
    where acc(B_b) is empirical event frequency and conf(B_b) is mean predicted probability in bin b.
    Empty bins contribute 0. Returns None if array is empty.
    """
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_prob, dtype=float)

    if len(y_t) == 0:
        return None

    bins = compute_calibration_curve(y_t, y_p, n_bins=n_bins)
    total_samples = len(y_t)
    ece = 0.0

    for b in bins:
        count = b.get("sample_count", 0)
        mean_prob = b.get("mean_predicted_probability")
        obs_freq = b.get("observed_event_frequency")
        if count > 0 and mean_prob is not None and obs_freq is not None:
            weight = count / total_samples
            ece += weight * abs(obs_freq - mean_prob)

    return float(round(ece, 4))


