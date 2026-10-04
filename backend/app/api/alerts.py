"""
Meghvani Alerts API (Phase 1 Foundation & Phase 6A Communication Simulation).

Provides:
- POST /api/alerts/preview: non-dispatched preview with routing plan and consent check
- POST /api/alerts/simulate: end-to-end simulated alert dispatch with fallback and duplicate check
- GET /api/alerts/history: privacy-conscious audit history with masked phone numbers
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.alert_log import AlertLog
from app.models.block import Block
from app.models.farmer import Farmer
from app.services.alert_service import AlertService
from app.schemas.alert import (
    AlertSimulationRequest,
    AlertPreviewRequest,
    AlertLogRead,
    AlertLogAuditRead,
    AlertDispatchResponse
)
from app.communication.alert_router import default_alert_router
from app.auth import verify_officer_api_key

router = APIRouter(prefix="/alerts", tags=["Alerts & Communication Simulation (Phase 6A)"])


@router.post("/dispatch", dependencies=[Depends(verify_officer_api_key)])
def dispatch_alert(req: AlertSimulationRequest, db: Session = Depends(get_db)):
    """
    Officer-authorized alert dispatch endpoint (Phase 8B).
    Requires X-API-Key header.
    INVARIANT 4 ENFORCED: is_operational = false and external dispatch stays disabled.
    All communications are executed via mock providers in simulation mode.
    """
    return simulate_alert(req=req, db=db)


@router.post("/preview")
def preview_alert(req: AlertPreviewRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Generates an alert preview without performing dispatch or writing to database.
    Evaluates consent, forecast, decision, validated rule, and severity routing plan.
    """
    res = default_alert_router.preview_alert(
        db=db,
        farmer_id=req.farmer_id,
        crop_id=req.crop_id,
        language=req.language,
        severity=req.severity,
        channel=req.channel
    )
    if res.get("alert_status") == "BLOCKED_FARMER_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=res.get("error")
        )
    return res


@router.post("/simulate", dependencies=[Depends(verify_officer_api_key)])
def simulate_alert(req: AlertSimulationRequest, db: Session = Depends(get_db)):
    """
    End-to-end communication simulation endpoint (Phase 6A).
    - If `farmer_id` is supplied: executes single-farmer simulation with consent gate,
      validated rule verification, duplicate prevention, mock provider execution, and fallback.
    - If `block_id` is supplied without `farmer_id`: broadcasts block-level simulation (Phase 1 compat).
    """
    # 1. Single-farmer simulation mode (Phase 6A)
    if req.farmer_id is not None:
        crop_str = str(req.crop_id) if req.crop_id is not None else None
        res = default_alert_router.simulate_dispatch(
            db=db,
            farmer_id=req.farmer_id,
            crop_id=crop_str,
            language=req.language,
            severity=req.severity or req.risk_level,
            channel_preference=req.channel_preference,
            force_failure_channel=req.force_failure_channel
        )
        if res.get("status") == "BLOCKED_FARMER_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=res.get("error")
            )
        return res

    # 2. Block-level broadcast mode (Phase 1 compat)
    if req.block_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either farmer_id or block_id must be provided."
        )

    block = db.query(Block).filter(Block.id == req.block_id).first()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block with ID {req.block_id} not found."
        )

    crop_int = None
    if req.crop_id is not None:
        try:
            crop_int = int(req.crop_id)
        except ValueError:
            crop_int = None

    logs = AlertService.simulate_block_alert(
        db=db,
        block_id=req.block_id,
        alert_type=req.alert_type or "ROUTINE_ADVISORY",
        risk_level=req.risk_level or "NORMAL",
        crop_id=crop_int,
        override_message=req.override_message
    )

    targeted_farmer_ids = set(l.farmer_id for l in logs)

    return AlertDispatchResponse(
        total_farmers_targeted=len(targeted_farmer_ids),
        dispatches=logs,
        disclaimer="PROTOTYPE ALERT DISPATCH - ALL NOTIFICATIONS SIMULATED VIA MOCK PROVIDERS"
    )


@router.get("/history", response_model=List[AlertLogAuditRead], dependencies=[Depends(verify_officer_api_key)])
def get_alert_history(
    farmer_id: Optional[int] = Query(default=None, description="Filter by farmer ID"),
    block_id: Optional[int] = Query(default=None, description="Filter by block ID"),
    crop_id: Optional[str] = Query(default=None, description="Filter by crop identifier"),
    status: Optional[str] = Query(default=None, description="Filter by simulated status"),
    channel: Optional[str] = Query(default=None, description="Filter by communication channel"),
    severity: Optional[str] = Query(default=None, description="Filter by severity level"),
    limit: int = Query(default=50, ge=1, le=200, description="Max logs to return"),
    db: Session = Depends(get_db)
):
    """
    Officer Audit View (Phase 6A).
    Returns masked alert logs with simulation provenance.
    Never exposes unmasked phone numbers.
    """
    query = db.query(AlertLog)

    if farmer_id is not None:
        query = query.filter(AlertLog.farmer_id == farmer_id)
    if block_id is not None:
        query = query.filter(AlertLog.block_id == block_id)
    if crop_id:
        query = query.filter(AlertLog.crop_id == crop_id.strip().lower())
    if status:
        query = query.filter(AlertLog.status == status.strip().upper())
    if channel:
        query = query.filter(AlertLog.channel == channel.strip().upper())
    if severity:
        query = query.filter(AlertLog.severity == severity.strip().upper())

    logs = query.order_by(AlertLog.created_at.desc()).limit(limit).all()

    # Pre-fetch farmers to construct privacy-preserving masked phone numbers
    farmer_ids = list({l.farmer_id for l in logs})
    farmers_by_id = {f.id: f for f in db.query(Farmer).filter(Farmer.id.in_(farmer_ids)).all()} if farmer_ids else {}

    results = []
    for l in logs:
        f = farmers_by_id.get(l.farmer_id)
        phone = f.phone_number if f else None
        masked = default_alert_router.mask_phone_number(phone)

        results.append(
            AlertLogAuditRead(
                id=l.id,
                farmer_id=l.farmer_id,
                masked_phone=masked,
                block_id=l.block_id,
                crop_id=l.crop_id,
                decision=l.decision or l.alert_type,
                severity=l.severity or l.risk_level,
                channel=l.channel,
                status=l.status,
                provider=l.provider,
                provider_message_id=l.provider_message_id,
                fallback_used=l.fallback_used,
                fallback_channel=l.fallback_channel,
                message=l.message,
                reason=l.reason,
                external_dispatch=False,
                created_at=l.created_at
            )
        )

    return results


@router.get("", response_model=List[AlertLogRead])
def list_alert_logs(limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieve audit trail of recent alert dispatches (Phase 1 compat).
    """
    return (
        db.query(AlertLog)
        .order_by(AlertLog.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/by-farmer/{farmer_id}", response_model=List[AlertLogRead])
def list_alerts_by_farmer(farmer_id: int, db: Session = Depends(get_db)):
    """
    Retrieve alert dispatch history for a single farmer (Phase 1 compat).
    """
    return (
        db.query(AlertLog)
        .filter(AlertLog.farmer_id == farmer_id)
        .order_by(AlertLog.created_at.desc())
        .all()
    )
