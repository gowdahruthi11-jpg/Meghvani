from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.alert_log import AlertLog
from app.models.block import Block
from app.services.alert_service import AlertService
from app.schemas.alert import AlertSimulationRequest, AlertLogRead, AlertDispatchResponse

router = APIRouter(prefix="/alerts", tags=["Alerts & Communication"])

@router.post("/simulate", response_model=AlertDispatchResponse)
def simulate_alert(req: AlertSimulationRequest, db: Session = Depends(get_db)):
    """
    Simulates broadcasting an alert to farmers in a specified block.
    Uses severity-based communication matrix (SMS, WhatsApp, Voice + retry + fallback).
    All delivery events are logged to the database.
    """
    block = db.query(Block).filter(Block.id == req.block_id).first()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block with ID {req.block_id} not found."
        )

    logs = AlertService.simulate_block_alert(
        db=db,
        block_id=req.block_id,
        alert_type=req.alert_type,
        risk_level=req.risk_level,
        crop_id=req.crop_id,
        override_message=req.override_message
    )

    # Count distinct farmers targeted
    targeted_farmer_ids = set(l.farmer_id for l in logs)

    return AlertDispatchResponse(
        total_farmers_targeted=len(targeted_farmer_ids),
        dispatches=logs,
        disclaimer="PROTOTYPE ALERT DISPATCH - ALL NOTIFICATIONS SIMULATED VIA MOCK PROVIDERS"
    )

@router.get("", response_model=List[AlertLogRead])
def list_alert_logs(limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieve audit trail of recent alert dispatches for officer dashboard.
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
    Retrieve alert dispatch history for a single farmer.
    """
    return (
        db.query(AlertLog)
        .filter(AlertLog.farmer_id == farmer_id)
        .order_by(AlertLog.created_at.desc())
        .all()
    )
