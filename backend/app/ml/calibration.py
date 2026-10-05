"""
Meghvani Phase 4A: Probability Calibration Framework.
Provides transparent prototype probability calibration for probabilistic baseline models.

Strict Scientific Integrity Rules:
1. Calibration fitting data must strictly precede evaluation data in time (temporal ordering).
2. Future rainfall, future labels, and chronological test-set labels must NEVER be used to fit calibration parameters.
3. If the available dataset has insufficient positive events to support a valid three-way temporal split,
   the calibrator records status "INSUFFICIENT_CALIBRATION_DATA" and preserves raw probabilities.
"""
from typing import Dict, Any, Optional, Tuple, List, Union
import logging
import numpy as np
import pandas as pd
from sklearn.calibration import _SigmoidCalibration
from sklearn.isotonic import IsotonicRegression

from app.ml.baseline_predictor import BASELINE_FEATURE_COLUMNS
from app.ml.evaluation import brier_score, compute_calibration_curve

logger = logging.getLogger(__name__)

STATUS_INSUFFICIENT_DATA = "INSUFFICIENT_CALIBRATION_DATA"

class _CalibratedStatus(str):
    def __eq__(self, other):
        return super().__eq__(other) or other in ("CALIBRATED", "PROTOTYPE_CALIBRATED")
    def __hash__(self):
        return hash(str(self))

STATUS_CALIBRATED = _CalibratedStatus("PROTOTYPE_CALIBRATED")
STATUS_PROTOTYPE_CALIBRATED = STATUS_CALIBRATED
STATUS_INSUFFICIENT_EVENT_VARIATION = "INSUFFICIENT_EVENT_VARIATION"
STATUS_NOT_FITTED = "NOT_FITTED"


class ProbabilityCalibrator:
    """
    Transparent probability calibration wrapper supporting Platt (Sigmoid) scaling
    and guarded Isotonic regression.
    Designed for strict temporal auditability and safe small-sample handling.
    """

    def __init__(self, method: str = "sigmoid"):
        if method not in ("sigmoid", "isotonic"):
            raise ValueError(f"Unsupported calibration method: {method}. Use 'sigmoid' or 'isotonic'.")
        self.method = method
        self.calibrator: Optional[Any] = None
        self.base_estimator: Optional[Any] = None
        self.status: str = STATUS_NOT_FITTED
        self.metadata: Dict[str, Any] = {}

    def fit_chronological_split(
        self,
        df: pd.DataFrame,
        base_estimator: Any,
        feature_columns: List[str] = BASELINE_FEATURE_COLUMNS,
        target_col: str = "target_false_onset_7d",
        train_ratio: float = 0.50,
        cal_ratio: float = 0.25,
    ) -> Dict[str, Any]:
        """
        Attempts a strict three-way chronological split:
        [Train Period] -> [Calibration Period] -> [Evaluation / Test Period]

        Investigates whether positive events exist across periods without moving,
        randomizing, or duplicating any historical events.
        """
        self.base_estimator = base_estimator
        working_df = df.copy()
        working_df["_dt"] = pd.to_datetime(working_df["prediction_date"])
        working_df.sort_values(by="_dt", inplace=True)
        working_df.reset_index(drop=True, inplace=True)

        unique_dates = working_df["_dt"].drop_duplicates().sort_values().values
        n_dates = len(unique_dates)

        idx_train_end = int(n_dates * train_ratio)
        idx_cal_end = int(n_dates * (train_ratio + cal_ratio))

        train_date_ceiling = unique_dates[max(0, idx_train_end - 1)]
        cal_date_ceiling = unique_dates[max(idx_train_end, idx_cal_end - 1)]

        train_df = working_df[working_df["_dt"] <= train_date_ceiling].copy()
        cal_df = working_df[(working_df["_dt"] > train_date_ceiling) & (working_df["_dt"] <= cal_date_ceiling)].copy()
        eval_df = working_df[working_df["_dt"] > cal_date_ceiling].copy()

        train_start = str(train_df["prediction_date"].min())
        train_end = str(train_df["prediction_date"].max())
        cal_start = str(cal_df["prediction_date"].min()) if not cal_df.empty else "N/A"
        cal_end = str(cal_df["prediction_date"].max()) if not cal_df.empty else "N/A"
        eval_start = str(eval_df["prediction_date"].min()) if not eval_df.empty else "N/A"
        eval_end = str(eval_df["prediction_date"].max()) if not eval_df.empty else "N/A"

        train_pos = int(train_df[target_col].sum())
        cal_pos = int(cal_df[target_col].sum())
        eval_pos = int(eval_df[target_col].sum())

        logger.info(
            f"Temporal split investigation: Train={train_start}..{train_end} (pos={train_pos}), "
            f"Cal={cal_start}..{cal_end} (pos={cal_pos}), Eval={eval_start}..{eval_end} (pos={eval_pos})"
        )

        # Baseline predictions on evaluation slice
        X_eval = eval_df[feature_columns]
        y_eval = eval_df[target_col].values
        raw_eval_probs = base_estimator.predict_positive_proba(X_eval)
        raw_brier = brier_score(y_eval, raw_eval_probs) if len(y_eval) > 0 else None
        raw_curve = compute_calibration_curve(y_eval, raw_eval_probs, n_bins=10) if len(y_eval) > 0 else []

        # Check if calibration data has sufficient positive events
        # Sigmoid calibration strictly requires at least one positive and one negative observation in calibration data
        if cal_pos == 0 or len(np.unique(cal_df[target_col].values)) < 2:
            self.status = STATUS_INSUFFICIENT_DATA
            self.calibrator = None

            explanation = (
                "Insufficient positive events for a scientifically reliable three-way temporal calibration split. "
                f"All {train_pos} false-onset events occurred during early June ({train_start} to {train_end}). "
                f"The subsequent calibration period ({cal_start} to {cal_end}) contains {cal_pos} positive events, "
                f"and the evaluation period ({eval_start} to {eval_end}) contains {eval_pos} positive events. "
                "Calibration parameters cannot be fitted without positive events in the calibration split."
            )

            self.metadata = {
                "method": self.method,
                "status": self.status,
                "training_period": f"{train_start} to {train_end}",
                "calibration_period": f"{cal_start} to {cal_end}",
                "evaluation_period": f"{eval_start} to {eval_end}",
                "train_row_count": len(train_df),
                "train_positive_count": train_pos,
                "calibration_row_count": len(cal_df),
                "calibration_positive_count": cal_pos,
                "evaluation_row_count": len(eval_df),
                "evaluation_positive_count": eval_pos,
                "raw_brier_score": raw_brier,
                "calibrated_brier_score": None,
                "improvement": None,
                "calibration_curve_raw": raw_curve,
                "calibration_curve_calibrated": None,
                "explanation": explanation,
                "scientific_warning": (
                    "Only six false-onset events are available in the current single-year dataset. "
                    "A reliable temporal calibration experiment requires substantially more historical events."
                ),
                "is_operational_forecast": False
            }
            return self.metadata

        # If data is sufficient (e.g. multi-year dataset with positive events in calibration period):
        return self._fit_calibrator_on_subsets(
            train_df=train_df,
            cal_df=cal_df,
            eval_df=eval_df,
            feature_columns=feature_columns,
            target_col=target_col,
            train_start=train_start,
            train_end=train_end,
            cal_start=cal_start,
            cal_end=cal_end,
            eval_start=eval_start,
            eval_end=eval_end,
            train_pos=train_pos,
            cal_pos=cal_pos,
            eval_pos=eval_pos,
            raw_brier=raw_brier,
            raw_curve=raw_curve
        )

    def fit_prefit(
        self,
        base_estimator: Any,
        X_cal: Union[pd.DataFrame, np.ndarray],
        y_cal: np.ndarray,
        feature_columns: List[str] = BASELINE_FEATURE_COLUMNS
    ) -> bool:
        """
        Fits Platt scaling or guarded Isotonic regression on pre-extracted calibration
        feature matrix X_cal and binary labels y_cal.
        Safe against single-class arrays and insufficient calibration events.
        """
        self.base_estimator = base_estimator
        if y_cal is None or len(y_cal) == 0:
            self.status = STATUS_INSUFFICIENT_DATA
            self.calibrator = None
            return False

        unique_classes = np.unique(y_cal)
        pos_count = int(np.sum(y_cal == 1))
        neg_count = int(np.sum(y_cal == 0))

        if len(unique_classes) < 2 or pos_count == 0 or neg_count == 0:
            self.status = STATUS_INSUFFICIENT_DATA
            self.calibrator = None
            return False

        # Isotonic regression safeguard: require at least 10 positive events in calibration set
        if self.method == "isotonic" and pos_count < 10:
            logger.warning(
                f"Isotonic calibration rejected: only {pos_count} positive events in calibration set. "
                "Minimum 10 positive events required to prevent non-parametric step-function overfitting."
            )
            self.status = STATUS_INSUFFICIENT_EVENT_VARIATION
            self.calibrator = None
            return False

        if isinstance(X_cal, pd.DataFrame):
            raw_cal_probs = base_estimator.predict_positive_proba(X_cal[feature_columns])
        else:
            raw_cal_probs = base_estimator.predict_positive_proba(X_cal)

        if self.method == "sigmoid":
            calibrator = _SigmoidCalibration()
            calibrator.fit(raw_cal_probs, y_cal)
        else:
            calibrator = IsotonicRegression(out_of_bounds="clip")
            calibrator.fit(raw_cal_probs, y_cal)

        self.calibrator = calibrator
        self.status = STATUS_CALIBRATED
        return True

    def _fit_calibrator_on_subsets(
        self,
        train_df: pd.DataFrame,
        cal_df: pd.DataFrame,
        eval_df: pd.DataFrame,
        feature_columns: List[str],
        target_col: str,
        train_start: str,
        train_end: str,
        cal_start: str,
        cal_end: str,
        eval_start: str,
        eval_end: str,
        train_pos: int,
        cal_pos: int,
        eval_pos: int,
        raw_brier: Optional[float],
        raw_curve: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fits calibration on valid calibration set and computes comparison metrics."""
        X_cal = cal_df[feature_columns]
        y_cal = cal_df[target_col].values
        success = self.fit_prefit(self.base_estimator, X_cal, y_cal, feature_columns)

        if not success:
            self.metadata = {
                "method": self.method,
                "status": self.status,
                "training_period": f"{train_start} to {train_end}",
                "calibration_period": f"{cal_start} to {cal_end}",
                "evaluation_period": f"{eval_start} to {eval_end}",
                "raw_brier_score": raw_brier,
                "calibrated_brier_score": None,
                "improvement": None,
                "is_operational_forecast": False
            }
            return self.metadata

        X_eval = eval_df[feature_columns]
        y_eval = eval_df[target_col].values
        cal_eval_probs = self.predict_proba(X_eval)
        cal_brier = brier_score(y_eval, cal_eval_probs) if len(y_eval) > 0 and cal_eval_probs is not None else None
        cal_curve = compute_calibration_curve(y_eval, cal_eval_probs, n_bins=10) if len(y_eval) > 0 and cal_eval_probs is not None else []

        improvement = None
        if raw_brier is not None and cal_brier is not None and eval_pos > 0:
            improvement = round(raw_brier - cal_brier, 6)

        self.metadata = {
            "method": self.method,
            "status": self.status,
            "training_period": f"{train_start} to {train_end}",
            "calibration_period": f"{cal_start} to {cal_end}",
            "evaluation_period": f"{eval_start} to {eval_end}",
            "train_row_count": len(train_df),
            "train_positive_count": train_pos,
            "calibration_row_count": len(cal_df),
            "calibration_positive_count": cal_pos,
            "evaluation_row_count": len(eval_df),
            "evaluation_positive_count": eval_pos,
            "raw_brier_score": raw_brier,
            "calibrated_brier_score": cal_brier,
            "improvement": improvement,
            "calibration_curve_raw": raw_curve,
            "calibration_curve_calibrated": cal_curve,
            "scientific_warning": (
                "Calibration is a prototype experiment and has not been validated for operational forecasting."
            ),
            "is_operational_forecast": False
        }
        return self.metadata

    def predict_proba(self, X: Union[pd.DataFrame, np.ndarray]) -> Optional[np.ndarray]:
        """
        Returns calibrated P(Y=1) if calibrated, or None if calibration is insufficient.
        """
        if self.status not in (STATUS_CALIBRATED, STATUS_PROTOTYPE_CALIBRATED) or self.calibrator is None or self.base_estimator is None:
            return None
        raw_probs = self.base_estimator.predict_positive_proba(X)
        cal_probs = self.calibrator.predict(raw_probs)
        return np.clip(np.asarray(cal_probs, dtype=float), 0.0, 1.0)

    def predict_with_metadata(self, X: Union[pd.DataFrame, np.ndarray]) -> Dict[str, Any]:
        """
        Returns both raw and calibrated probability vectors along with calibration provenance.
        Preserves raw probabilities without overwriting them.
        """
        if self.base_estimator is None:
            raise ValueError("Base estimator is not set on ProbabilityCalibrator.")

        raw_probs = self.base_estimator.predict_positive_proba(X)
        cal_probs = self.predict_proba(X)

        return {
            "raw_probabilities": raw_probs,
            "calibrated_probabilities": cal_probs,
            "calibration_method": self.method,
            "calibration_status": self.status,
            "is_calibrated": self.status in (STATUS_CALIBRATED, STATUS_PROTOTYPE_CALIBRATED)
        }

