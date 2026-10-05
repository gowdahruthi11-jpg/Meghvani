import os
import uuid
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.config import settings
from app.models.inbound_message import InboundMessage
from app.models.alert_log import AlertLog
from app.models.farmer import Farmer
from app.models.registration_session import RegistrationSession
from app.communication.twilio_sms import normalize_phone_number
from app.services.registration_service import RegistrationService
from app.communication.mock_provider import MockMissedCallProvider
from app.schemas.registration import (
    RegistrationStartRequest,
    RegistrationResetRequest,
    RegistrationMessageRequest,
    MissedCallRequest,
    RegistrationSessionRead,
    RegistrationMessageResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/registration", tags=["Registration"])

@router.post("/reset", response_model=RegistrationMessageResponse)
def reset_registration(req: RegistrationResetRequest, db: Session = Depends(get_db)):
    """
    Deactivates any existing active farmer record for this phone number and resets
    the registration session back to START so the user can show a fresh demo.
    """
    clean_phone = req.phone_number.strip()
    reply_msg, step, is_done, farmer_id = RegistrationService.reset_registration(db, clean_phone)
    return RegistrationMessageResponse(
        reply_message=reply_msg,
        current_step=step,
        is_completed=is_done,
        registered_farmer_id=farmer_id
    )

@router.post("/start", response_model=RegistrationMessageResponse)
def start_registration(req: RegistrationStartRequest, db: Session = Depends(get_db)):
    """
    Simulates receipt of incoming MEGH SMS or web registration initiation.
    Does NOT require farmer to type their own phone number in real SMS workflow.
    """
    clean_phone = req.phone_number.strip()
    norm_phone = normalize_phone_number(clean_phone)
    reply_msg, step, is_done, farmer_id = RegistrationService.start_registration(
        db, clean_phone, force_new=bool(getattr(req, "force_new", False))
    )

    # Synchronize transaction with InboundMessage for Alert Center timeline
    try:
        inbound_record = InboundMessage(
            provider=os.getenv("SMS_PROVIDER") or settings.sms_provider or "MOCK",
            provider_message_id=f"reg-start-{uuid.uuid4().hex[:10]}",
            from_phone=norm_phone,
            to_phone="+911800MEGHVANI",
            message_body="MEGH",
            normalized_body="MEGH",
            received_at=datetime.now(timezone.utc),
            processing_status="PROCESSED",
            registration_step_before="START",
            registration_step_after=step,
            farmer_id=farmer_id,
            reply_message=reply_msg,
            reply_status="SENT",
        )
        db.add(inbound_record)
        db.commit()
    except Exception as e:
        logger.warning(f"Could not log inbound message in start_registration: {e}")

    return RegistrationMessageResponse(
        reply_message=reply_msg,
        current_step=step,
        is_completed=is_done,
        registered_farmer_id=farmer_id
    )

@router.post("/message", response_model=RegistrationMessageResponse)
def process_incoming_message(req: RegistrationMessageRequest, db: Session = Depends(get_db)):
    """
    Core conversational SMS state-machine processor.
    Evaluates farmer's message response against current step and advances state.
    """
    clean_phone = req.phone_number.strip()
    norm_phone = normalize_phone_number(clean_phone)

    # Capture step before
    session_before = db.query(RegistrationSession).filter(
        (RegistrationSession.phone_number == clean_phone) |
        (RegistrationSession.phone_number == norm_phone)
    ).first()
    step_before = session_before.current_step if session_before else "START"

    reply_msg, step, is_done, farmer_id = RegistrationService.process_message(
        db=db,
        phone_number=clean_phone,
        incoming_text=req.message
    )

    # Synchronize transaction with InboundMessage & AlertLog for Alert Center timeline
    try:
        provider_name = os.getenv("SMS_PROVIDER") or settings.sms_provider or "MOCK"
        inbound_record = InboundMessage(
            provider=provider_name,
            provider_message_id=f"reg-msg-{uuid.uuid4().hex[:10]}",
            from_phone=norm_phone,
            to_phone="+911800MEGHVANI",
            message_body=req.message,
            normalized_body=req.message.strip().upper(),
            received_at=datetime.now(timezone.utc),
            processing_status="PROCESSED",
            registration_step_before=step_before,
            registration_step_after=step,
            farmer_id=farmer_id,
            reply_message=reply_msg,
            reply_status="SENT",
        )
        db.add(inbound_record)

        if farmer_id or is_done:
            farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first() if farmer_id else None
            alert_type = "ADVISORY_STATUS" if step == "STATUS" else ("REGISTRATION_SUCCESS" if is_done else "SMS_INTERACTION")
            risk_level = "IMPORTANT" if step == "STATUS" else "NORMAL"
            block_id = farmer.block_id if farmer else 1

            alert_log = AlertLog(
                farmer_id=farmer_id,
                block_id=block_id,
                channel="SMS",
                alert_type=alert_type,
                message=reply_msg,
                status="SENT",
                risk_level=risk_level,
                sent_at=datetime.now(timezone.utc),
                provider=provider_name
            )
            db.add(alert_log)

        db.commit()
    except Exception as e:
        logger.warning(f"Could not log message to InboundMessage / AlertLog: {e}")

    return RegistrationMessageResponse(
        reply_message=reply_msg,
        current_step=step,
        is_completed=is_done,
        registered_farmer_id=farmer_id
    )

@router.get("/{phone_number}", response_model=RegistrationSessionRead)
def get_registration_session(phone_number: str, db: Session = Depends(get_db)):
    """
    Check current state of an ongoing registration session.
    """
    session = RegistrationService.get_or_create_session(db, phone_number)
    return session

@router.post("/missed-call", response_model=RegistrationMessageResponse)
def simulate_missed_call(req: MissedCallRequest, db: Session = Depends(get_db)):
    """
    Simulates incoming missed call detection for zero-cost onboarding.
    Incoming CLI identifies the farmer, and initiates the conversational workflow.
    """
    clean_phone = req.phone_number.strip()
    norm_phone = normalize_phone_number(clean_phone)
    provider = MockMissedCallProvider()
    result = provider.handle_incoming_ring(clean_phone)

    reply_msg, step, is_done, farmer_id = RegistrationService.start_registration(db, clean_phone)

    try:
        inbound_record = InboundMessage(
            provider=os.getenv("SMS_PROVIDER") or settings.sms_provider or "MOCK",
            provider_message_id=f"reg-missed-{uuid.uuid4().hex[:10]}",
            from_phone=norm_phone,
            to_phone="+911800MEGHVANI",
            message_body="[MISSED_CALL]",
            normalized_body="[MISSED_CALL]",
            received_at=datetime.now(timezone.utc),
            processing_status="PROCESSED",
            registration_step_before="START",
            registration_step_after=step,
            farmer_id=farmer_id,
            reply_message=reply_msg,
            reply_status="SENT",
        )
        db.add(inbound_record)
        db.commit()
    except Exception as e:
        logger.warning(f"Could not log missed call: {e}")

    return RegistrationMessageResponse(
        reply_message=f"[Mock Missed Call Detected from {req.phone_number}]\n" + reply_msg,
        current_step=step,
        is_completed=is_done,
        registered_farmer_id=farmer_id,
        note=result.get("note", "MISSED_CALL_TRIGGER")
    )

