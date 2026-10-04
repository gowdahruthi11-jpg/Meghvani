"""
Advisory API endpoint for Meghvani Phase 5A.
Translates prototype decisions and crop selections into structured agronomic advisories.
Strictly adheres to NO RULE = NO ADVICE.
"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query, status
import logging

from app.ml.model_loader import predict_block_false_onset
from app.ml.decision_engine import PrototypeDecisionEngine
from app.advisory.rule_engine import AdvisoryRuleEngine
from app.advisory.rule_registry import default_rule_registry
from app.advisory.models import AdvisoryResult
from app.advisory.message_generator import AdvisoryMessageGenerator, FarmerAdvisoryMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/advisory", tags=["Advisory Rule Framework (Phase 5A, 5B, 5C)"])


def _normalize_block_id(block_id: str) -> str:
    b_str = str(block_id).strip()
    if b_str.isdigit():
        return f"BLK{int(b_str):03d}"
    return b_str


@router.get("/rules")
def list_advisory_rules(
    crop_id: Optional[str] = Query(default=None, description="Filter by crop id, e.g. soybean, cotton, pigeonpea"),
    geography: Optional[str] = Query(default=None, description="Filter by geography, e.g. Maharashtra"),
    decision: Optional[str] = Query(default=None, description="Filter by decision: SOW_NOW, SOW_PART_NOW, WAIT"),
    validation_status: Optional[str] = Query(default=None, description="Filter by validation status: VALIDATED, REVIEW_REQUIRED, UNVALIDATED"),
    source_institution: Optional[str] = Query(default=None, description="Filter by source institution, e.g. ICAR-CRIDA, Dr. PDKV")
) -> List[Dict[str, Any]]:
    """
    Source and Rule Inspection endpoint (Phase 5B).
    Returns registered agronomic rules matching the filter criteria with full source traceability.
    """
    rules = default_rule_registry.list_rules(
        crop_id=crop_id,
        decision=decision,
        validation_status=validation_status,
        geography=geography,
        source_institution=source_institution
    )
    return [r.model_dump() for r in rules]


@router.get("/{block_id}/message")
def get_block_advisory_message(
    block_id: str,
    crop_id: str = Query(default="soybean", description="Crop identifier, e.g. soybean, cotton, pigeonpea"),
    geography: str = Query(default="Maharashtra", description="Target geography, e.g. Maharashtra"),
    language: str = Query(default="en", description="Language code: en, hi, mr"),
    channel: str = Query(default="sms", description="Delivery channel: sms, whatsapp, voice")
) -> Dict[str, Any]:
    """
    Farmer Advisory Message Preview Endpoint (Phase 5C).
    Converts evaluated prototype decision and validated agronomic rule into
    a localized, channel-ready message (en, hi, mr) without dispatching communication.
    """
    norm_id = _normalize_block_id(block_id)
    try:
        # 1. Obtain current prototype forecast
        forecast = predict_block_false_onset(norm_id)
        raw_prob = forecast.get("raw_probability", forecast.get("probability", 0.0))
        prob_status = "RAW_PROTOTYPE"
        cal_status = forecast.get("calibration_status", "INSUFFICIENT_CALIBRATION_DATA")
        eval_status = forecast.get("evaluation_status", "INSUFFICIENT_EVENT_VARIATION")

        # 2. Evaluate prototype decision
        decision_engine = PrototypeDecisionEngine()
        dec = decision_engine.evaluate(
            probability=raw_prob,
            probability_status=prob_status,
            calibration_status=cal_status,
            evaluation_status=eval_status
        )

        # 3. Query Advisory Rule Engine
        advisory_engine = AdvisoryRuleEngine()
        result: AdvisoryResult = advisory_engine.evaluate(
            crop_id=crop_id,
            decision=dec["decision"],
            probability=dec["probability"],
            probability_status=dec["probability_status"],
            decision_status=dec["decision_status"],
            block_id=norm_id,
            geography=geography,
            language="en"  # Underlying agronomic rules matched; localization occurs at message layer
        )

        # 4. Generate Localized Farmer Message
        farmer_msg: FarmerAdvisoryMessage = AdvisoryMessageGenerator.generate_message(
            advisory_result=result,
            block_id=norm_id,
            crop_id=crop_id,
            decision=dec["decision"],
            language=language,
            channel=channel,
            forecast_available=True
        )

        return farmer_msg.model_dump()
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
        logger.error(f"Advisory message generation failed for block {norm_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Advisory message error: {str(e)}"
        )


@router.get("/{block_id}")
def get_block_advisory(
    block_id: str,
    crop_id: str = Query(default="soybean", description="Crop identifier, e.g. soybean, cotton, pigeonpea"),
    geography: str = Query(default="Maharashtra", description="Target geography, e.g. Maharashtra"),
    language: str = Query(default="en", description="Language code")
) -> Dict[str, Any]:
    """
    Evaluates prototype decision against the Advisory Rule Registry.
    Returns structured advisory if a VALIDATED rule exists, otherwise safely returns NO_VALIDATED_RULE.
    """
    norm_id = _normalize_block_id(block_id)
    try:
        # 1. Obtain current prototype forecast
        forecast = predict_block_false_onset(norm_id)
        raw_prob = forecast.get("raw_probability", forecast.get("probability", 0.0))
        prob_status = "RAW_PROTOTYPE"
        cal_status = forecast.get("calibration_status", "INSUFFICIENT_CALIBRATION_DATA")
        eval_status = forecast.get("evaluation_status", "INSUFFICIENT_EVENT_VARIATION")

        # 2. Evaluate prototype decision
        decision_engine = PrototypeDecisionEngine()
        dec = decision_engine.evaluate(
            probability=raw_prob,
            probability_status=prob_status,
            calibration_status=cal_status,
            evaluation_status=eval_status
        )

        # 3. Query Advisory Rule Engine
        advisory_engine = AdvisoryRuleEngine()
        result: AdvisoryResult = advisory_engine.evaluate(
            crop_id=crop_id,
            decision=dec["decision"],
            probability=dec["probability"],
            probability_status=dec["probability_status"],
            decision_status=dec["decision_status"],
            block_id=norm_id,
            geography=geography,
            language=language
        )

        return result.model_dump()
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
        logger.error(f"Advisory lookup failed for block {norm_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Advisory error: {str(e)}"
        )
