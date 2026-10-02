from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.registration_service import RegistrationService
from app.communication.mock_provider import MockMissedCallProvider
from app.schemas.registration import (
    RegistrationStartRequest,
    RegistrationMessageRequest,
    MissedCallRequest,
    RegistrationSessionRead,
    RegistrationMessageResponse,
)

router = APIRouter(prefix="/registration", tags=["Registration"])

@router.post("/start", response_model=RegistrationMessageResponse)
def start_registration(req: RegistrationStartRequest, db: Session = Depends(get_db)):
    """
    Simulates receipt of incoming MEGH SMS or web registration initiation.
    Does NOT require farmer to type their own phone number in real SMS workflow.
    """
    reply_msg, step, is_done, farmer_id = RegistrationService.start_registration(db, req.phone_number)
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
    reply_msg, step, is_done, farmer_id = RegistrationService.process_message(
        db=db,
        phone_number=req.phone_number,
        incoming_text=req.message
    )
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
    provider = MockMissedCallProvider()
    result = provider.handle_incoming_ring(req.phone_number)

    reply_msg, step, is_done, farmer_id = RegistrationService.start_registration(db, req.phone_number)
    return RegistrationMessageResponse(
        reply_message=f"[Mock Missed Call Detected from {req.phone_number}]\n" + reply_msg,
        current_step=step,
        is_completed=is_done,
        registered_farmer_id=farmer_id,
        note=result.get("note", "MISSED_CALL_TRIGGER")
    )
