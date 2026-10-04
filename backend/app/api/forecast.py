"""
Forecast and baseline probabilistic prediction API for Meghvani Phase 3B.
Provides endpoint for False Onset 7-Day prototype model inference and baseline metadata.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Query
import logging

from app.ml.model_loader import (
    predict_block_false_onset,
    get_model_metadata,
    predict_block_multi_event,
    get_multi_event_suite_summary
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/forecast", tags=["Baseline Forecast (Phase 3B & Multi-Event)"])


def _normalize_block_id(block_id: str) -> str:
    """Normalizes numeric or string block ID to BLKXXX format."""
    b_str = str(block_id).strip()
    if b_str.isdigit():
        return f"BLK{int(b_str):03d}"
    return b_str


@router.get("/baseline-summary")
def get_baseline_model_summary() -> Dict[str, Any]:
    """
    Returns metadata, evaluation metrics, calibration table, and linear feature contributions
    for the Phase 3B Logistic Regression baseline model.
    """
    try:
        return get_model_metadata()
    except Exception as e:
        logger.error(f"Failed to load baseline model metadata: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load model metadata: {str(e)}"
        )


@router.get("/{block_id}/false-onset")
def get_false_onset_prediction(block_id: str) -> Dict[str, Any]:
    """
    Estimates P(False Onset occurs within the next 7 days) for the specified block.
    Uses latest valid predictor observations on or before prediction date T.
    
    IMPORTANT: Prototype baseline model output only. Not an operational forecast.
    """
    norm_id = _normalize_block_id(block_id)
    try:
        result = predict_block_false_onset(norm_id)
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except FileNotFoundError as fe:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(fe)
        )
    except Exception as e:
        logger.error(f"Prediction failed for block {norm_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}"
        )


@router.get("/{block_id}/false-onset/decision")
def get_false_onset_decision(block_id: str) -> Dict[str, Any]:
    """
    Evaluates current prototype false-onset probability into a transparent decision-support result:
    SOW_NOW, SOW_PART_NOW, or WAIT.
    
    IMPORTANT: Prototype decision support only. NOT a validated agronomic recommendation.
    """
    norm_id = _normalize_block_id(block_id)
    try:
        forecast = predict_block_false_onset(norm_id)
        raw_prob = forecast.get("raw_probability", forecast.get("probability", 0.0))
        prob_status = "RAW_PROTOTYPE"
        cal_status = forecast.get("calibration_status", "INSUFFICIENT_CALIBRATION_DATA")
        eval_status = forecast.get("evaluation_status", "INSUFFICIENT_EVENT_VARIATION")

        from app.ml.decision_engine import PrototypeDecisionEngine
        engine = PrototypeDecisionEngine()
        dec = engine.evaluate(
            probability=raw_prob,
            probability_status=prob_status,
            calibration_status=cal_status,
            evaluation_status=eval_status
        )

        return {
            "block_id": norm_id,
            "prediction_date": forecast.get("prediction_date"),
            "target": forecast.get("target", "FALSE_ONSET"),
            "horizon_days": forecast.get("horizon_days", 7),
            "probability": dec["probability"],
            "probability_status": dec["probability_status"],
            "decision": dec["decision"],
            "decision_status": dec["decision_status"],
            "thresholds": dec["thresholds"],
            "reason_codes": dec["reason_codes"],
            "explanation": dec["explanation"],
            "scientific_warning": dec["scientific_warning"],
            "is_operational": dec["is_operational"]
        }
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except FileNotFoundError as fe:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(fe)
        )
    except Exception as e:
        logger.error(f"Decision evaluation failed for block {norm_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decision evaluation error: {str(e)}"
        )


@router.get("/suite-summary")
def get_multi_event_suite_summary_endpoint() -> Dict[str, Any]:
    """
    Returns metadata, Brier scores, BSS, and calibration status across all
    trained models in the multi-event prediction suite.
    """
    try:
        return get_multi_event_suite_summary()
    except Exception as e:
        logger.error(f"Failed to fetch suite summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{block_id}/multi-event")
def get_block_multi_event_prediction(
    block_id: str,
    horizon_days: int = Query(7, description="Forecast horizon in days (7 or 14)")
) -> Dict[str, Any]:
    """
    Returns calibrated multi-event probabilities for a block:
    - P(Monsoon Onset)
    - P(Monsoon Break Spell)
    - P(Heavy Rain Episode)
    - P(False Onset Warning)
    """
    norm_id = _normalize_block_id(block_id)
    try:
        return predict_block_multi_event(norm_id, horizon_days=horizon_days)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except FileNotFoundError as fe:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(fe)
        )
    except Exception as e:
        logger.error(f"Multi-event prediction failed for block {norm_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}"
        )

