"""
Model loader and inference service for Meghvani Phase 3B.
Caches and manages the trained baseline model artifact.
"""
from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging
import joblib
import pandas as pd

from app.config import PROJECT_ROOT

logger = logging.getLogger(__name__)

MODEL_DIR = PROJECT_ROOT / "ml" / "models"
MODEL_PATH = MODEL_DIR / "false_onset_7d_logistic.joblib"
METADATA_PATH = MODEL_DIR / "false_onset_7d_logistic_metadata.json"
PREDICTION_DATASET_CSV = PROJECT_ROOT / "data" / "processed" / "prediction_dataset.csv"

_CACHED_MODEL = None
_CACHED_METADATA = None


def get_false_onset_model():
    """
    Returns the loaded LogisticRegressionBaseline model, loading from disk if necessary.
    """
    global _CACHED_MODEL
    if _CACHED_MODEL is not None:
        return _CACHED_MODEL

    if not MODEL_PATH.exists():
        # Trigger on-the-fly training if dataset exists
        logger.info(f"Model artifact not found at {MODEL_PATH}. Training baseline artifact...")
        from scripts.train_false_onset_baseline import train_false_onset_baseline
        train_false_onset_baseline()

    if MODEL_PATH.exists():
        _CACHED_MODEL = joblib.load(MODEL_PATH)
        return _CACHED_MODEL
    else:
        raise FileNotFoundError(f"Baseline model artifact not found at {MODEL_PATH}.")


def get_model_metadata(reload: bool = False) -> Dict[str, Any]:
    """
    Loads model evaluation and configuration metadata from JSON.
    """
    global _CACHED_METADATA
    if reload:
        _CACHED_METADATA = None
    if _CACHED_METADATA is not None:
        return _CACHED_METADATA

    if not METADATA_PATH.exists():
        if MODEL_PATH.exists() or PREDICTION_DATASET_CSV.exists():
            from scripts.train_false_onset_baseline import train_false_onset_baseline
            train_false_onset_baseline()

    if METADATA_PATH.exists():
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            _CACHED_METADATA = json.load(f)
            return _CACHED_METADATA
    else:
        return {
            "status": "NOT_TRAINED",
            "message": "Model artifact has not been generated yet."
        }


DIAGNOSTIC_MODEL_PATH = MODEL_DIR / "false_onset_7d_logistic_diagnostic.joblib"
DIAGNOSTIC_METADATA_PATH = MODEL_DIR / "false_onset_7d_logistic_diagnostic_metadata.json"

_CACHED_DIAGNOSTIC_MODEL = None
_CACHED_DIAGNOSTIC_METADATA = None


def get_diagnostic_metadata(reload: bool = False) -> Dict[str, Any]:
    """
    Loads diagnostic evaluation metadata from JSON.
    """
    global _CACHED_DIAGNOSTIC_METADATA
    if reload:
        _CACHED_DIAGNOSTIC_METADATA = None
    if _CACHED_DIAGNOSTIC_METADATA is not None:
        return _CACHED_DIAGNOSTIC_METADATA

    if not DIAGNOSTIC_METADATA_PATH.exists():
        from scripts.train_false_onset_baseline import train_false_onset_baseline
        train_false_onset_baseline()

    if DIAGNOSTIC_METADATA_PATH.exists():
        with open(DIAGNOSTIC_METADATA_PATH, "r", encoding="utf-8") as f:
            _CACHED_DIAGNOSTIC_METADATA = json.load(f)
            return _CACHED_DIAGNOSTIC_METADATA
    else:
        return {
            "status": "NOT_TRAINED",
            "message": "Diagnostic metadata artifact has not been generated yet."
        }



def get_diagnostic_model():
    """
    Returns the loaded diagnostic LogisticRegressionBaseline model.
    Used exclusively for historical event-focused diagnostics, NEVER as an operational forecast model.
    """
    global _CACHED_DIAGNOSTIC_MODEL
    if _CACHED_DIAGNOSTIC_MODEL is not None:
        return _CACHED_DIAGNOSTIC_MODEL

    if not DIAGNOSTIC_MODEL_PATH.exists():
        from scripts.train_false_onset_baseline import train_false_onset_baseline
        train_false_onset_baseline()

    if DIAGNOSTIC_MODEL_PATH.exists():
        _CACHED_DIAGNOSTIC_MODEL = joblib.load(DIAGNOSTIC_MODEL_PATH)
        return _CACHED_DIAGNOSTIC_MODEL
    else:
        raise FileNotFoundError(f"Diagnostic model artifact not found at {DIAGNOSTIC_MODEL_PATH}.")


CALIBRATED_MODEL_PATH = MODEL_DIR / "false_onset_7d_calibrated.joblib"
CALIBRATED_METADATA_PATH = MODEL_DIR / "false_onset_7d_calibrated_metadata.json"

_CACHED_CALIBRATED_MODEL = None
_CACHED_CALIBRATED_METADATA = None


def get_calibrated_metadata(reload: bool = False) -> Dict[str, Any]:
    """
    Loads probability calibration metadata from JSON.
    """
    global _CACHED_CALIBRATED_METADATA
    if reload:
        _CACHED_CALIBRATED_METADATA = None
    if _CACHED_CALIBRATED_METADATA is not None:
        return _CACHED_CALIBRATED_METADATA

    if not CALIBRATED_METADATA_PATH.exists():
        from scripts.train_false_onset_baseline import train_false_onset_baseline
        train_false_onset_baseline()

    if CALIBRATED_METADATA_PATH.exists():
        with open(CALIBRATED_METADATA_PATH, "r", encoding="utf-8") as f:
            _CACHED_CALIBRATED_METADATA = json.load(f)
            return _CACHED_CALIBRATED_METADATA
    else:
        return {
            "status": "NOT_TRAINED",
            "message": "Calibration metadata artifact has not been generated yet."
        }


def get_calibrated_false_onset_model():
    """
    Returns the loaded probability calibrator model if available.
    Does NOT replace the chronological baseline model.
    """
    global _CACHED_CALIBRATED_MODEL
    if _CACHED_CALIBRATED_MODEL is not None:
        return _CACHED_CALIBRATED_MODEL

    if not CALIBRATED_MODEL_PATH.exists():
        from scripts.train_false_onset_baseline import train_false_onset_baseline
        train_false_onset_baseline()

    if CALIBRATED_MODEL_PATH.exists():
        _CACHED_CALIBRATED_MODEL = joblib.load(CALIBRATED_MODEL_PATH)
        return _CACHED_CALIBRATED_MODEL
    else:
        return None


def predict_block_false_onset(
    block_id: str,
    df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Generates P(False Onset 7d) probability for the most recent valid observation of a block.
    Uses the strictly chronological baseline model artifact.
    Preserves both raw_probability and calibrated_probability (if legitimately available).
    """
    if df is None:
        if not PREDICTION_DATASET_CSV.exists():
            raise FileNotFoundError("Prediction dataset not found.")
        df = pd.read_csv(PREDICTION_DATASET_CSV)

    block_df = df[df["block_id"] == block_id].sort_values(by="prediction_date")
    if block_df.empty:
        raise ValueError(f"No records found for block '{block_id}'.")

    # Use the latest observation
    latest_row = block_df.iloc[[-1]]
    prediction_date = str(latest_row["prediction_date"].values[0])

    model = get_false_onset_model()
    raw_prob = float(model.predict_positive_proba(latest_row)[0])

    # Check calibrated model
    calibrated_meta = get_calibrated_metadata()
    cal_status = calibrated_meta.get("status", "INSUFFICIENT_CALIBRATION_DATA")
    cal_method = calibrated_meta.get("method", "sigmoid")

    calibrated_prob = None
    cal_model = get_calibrated_false_onset_model()
    if cal_model is not None and getattr(cal_model, "status", None) == "PROTOTYPE_CALIBRATED":
        cal_preds = cal_model.predict_proba(latest_row)
        if cal_preds is not None and len(cal_preds) > 0:
            calibrated_prob = round(float(cal_preds[0]), 4)

    return {
        "block_id": block_id,
        "prediction_date": prediction_date,
        "target": "FALSE_ONSET",
        "horizon_days": 7,
        "raw_probability": round(raw_prob, 4),
        "calibrated_probability": calibrated_prob,
        "probability": round(raw_prob, 4),  # backwards compatibility
        "model": "logistic_baseline",
        "calibration_method": cal_method,
        "calibration_status": cal_status,
        "evaluation_type": "single_year_chronological_prototype",
        "evaluation_status": "INSUFFICIENT_EVENT_VARIATION",
        "is_operational_forecast": False,
        "scientific_warning": (
            "Calibration is a prototype experiment and has not been validated for operational forecasting. "
            "The current single-year chronological evaluation contains no false-onset events in the test period; "
            "this probability is a prototype diagnostic and is not verified operational forecast skill."
        )
    }

