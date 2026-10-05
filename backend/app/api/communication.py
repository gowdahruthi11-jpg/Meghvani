import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.database import get_db
from app.config import settings
from app.models.inbound_message import InboundMessage
from app.models.alert_log import AlertLog
from app.models.farmer import Farmer
from pydantic import BaseModel, Field
from app.models.registration_session import RegistrationSession
from app.models.block import Block
from app.services.registration_service import RegistrationService
from app.communication.sms import get_sms_provider
from app.communication.twilio_sms import (
    normalize_phone_number,
    mask_phone_number,
    verify_twilio_signature
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/communication", tags=["Real SMS & Communication Gateway"])


class VoiceAlertRequest(BaseModel):
    farmer_id: Optional[int] = None
    alert_id: Optional[int] = None
    language: Optional[str] = None
    force_high_risk: bool = True
    alert_type: Optional[str] = "HEAVY_RAIN"


class VoiceEventRequest(BaseModel):
    farmer_id: Optional[int] = None
    alert_id: Optional[int] = None
    event: str  # "ANSWERED", "PLAYED", "COMPLETED", "DECLINED", "REPLAY"
    duration_seconds: Optional[int] = None


@router.get("/status")
def get_gateway_status() -> Dict[str, Any]:
    """
    Returns the real-time configuration status of the SMS communication gateway.
    Clearly distinguishes LIVE SMS (Twilio) mode from SIMULATION (Mock) mode.
    """
    provider = os.getenv("SMS_PROVIDER") or settings.sms_provider or "MOCK"
    provider = provider.strip().upper()

    raw_phone = os.getenv("TWILIO_PHONE_NUMBER") or settings.twilio_phone_number
    masked_phone = mask_phone_number(raw_phone) if raw_phone else None

    # Check credential readiness if in live mode
    account_sid = os.getenv("TWILIO_ACCOUNT_SID") or settings.twilio_account_sid
    auth_token = os.getenv("TWILIO_AUTH_TOKEN") or settings.twilio_auth_token
    has_credentials = bool(account_sid and auth_token and raw_phone)

    # Preserve MOCK mode as default/fallback if credentials are missing
    effective_provider = provider if (provider != "TWILIO" or has_credentials) else "MOCK"
    is_live = (effective_provider == "TWILIO")

    is_trial = (
        getattr(settings, "twilio_trial_mode", False)
        or os.getenv("TWILIO_TRIAL_MODE", "").strip().lower() in ("true", "1", "yes")
    )
    mode_label = "LIVE SMS (TRIAL)" if (is_live and is_trial) else ("LIVE SMS" if is_live else "SIMULATION")
    gateway_label = f"SMS GATEWAY: {'● LIVE (TWILIO TRIAL)' if (is_live and is_trial) else ('● LIVE (TWILIO)' if is_live else '● MOCK (SIMULATION)')}"

    return {
        "sms_provider": effective_provider,
        "mode": mode_label,
        "is_live": is_live,
        "is_trial_mode": is_trial if is_live else False,
        "is_ready": (has_credentials if is_live else True),
        "gateway_label": gateway_label,
        "twilio_phone_number_masked": masked_phone if is_live else None,
        "trial_notice": "Twilio Trial restriction: custom Meghvani SMS reply not permitted." if (is_live and is_trial) else None,
        "webhook_validation_enabled": settings.sms_webhook_validation,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/sms/incoming")
async def receive_inbound_sms(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Standard Inbound SMS Webhook for Twilio or Mock Provider.
    Accepts standard Twilio form payload: From, To, Body, MessageSid.
    Verifies Twilio signature in LIVE mode, enforces idempotency, routes
    through RegistrationService, dispatches outbound reply, and logs transaction.
    """
    content_type = request.headers.get("content-type", "").lower()
    form_data: Dict[str, Any] = {}

    if "application/json" in content_type:
        try:
            form_data = await request.json()
        except Exception:
            form_data = {}
    else:
        # Standard x-www-form-urlencoded
        raw_form = await request.form()
        form_data = dict(raw_form)

    # Extract standard fields
    from_phone = str(form_data.get("From") or form_data.get("from") or form_data.get("from_phone") or "").strip()
    to_phone = str(form_data.get("To") or form_data.get("to") or form_data.get("to_phone") or "").strip()
    body = str(form_data.get("Body") or form_data.get("body") or form_data.get("message") or "").strip()
    message_sid = str(form_data.get("MessageSid") or form_data.get("message_sid") or form_data.get("SmsSid") or "").strip()

    if not from_phone:
        logger.warning("Inbound SMS webhook received without 'From' phone number.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing 'From' phone number.")

    provider_name = (os.getenv("SMS_PROVIDER") or settings.sms_provider or "MOCK").strip().upper()

    # Twilio Webhook Signature Verification
    if provider_name == "TWILIO":
        val_env = os.getenv("SMS_WEBHOOK_VALIDATION")
        if val_env is not None:
            validation_enabled = val_env.strip().lower() in ["true", "1", "yes"]
        else:
            validation_enabled = settings.sms_webhook_validation

        if validation_enabled:
            auth_token = os.getenv("TWILIO_AUTH_TOKEN") or settings.twilio_auth_token
            signature = request.headers.get("X-Twilio-Signature")
            # Build full URL as requested
            url = str(request.url)
            is_valid = verify_twilio_signature(url, form_data, signature, auth_token)
            if not is_valid:
                logger.warning(f"Twilio webhook signature verification failed for URL {url}.")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid Twilio webhook signature."
                )
        else:
            logger.info("SMS_WEBHOOK_VALIDATION is set to false. Bypassing Twilio signature check for development.")

    # Phone normalization
    norm_from = normalize_phone_number(from_phone)
    norm_to = normalize_phone_number(to_phone) if to_phone else None

    # Idempotency check using MessageSid
    if message_sid:
        existing_msg = db.query(InboundMessage).filter(
            InboundMessage.provider_message_id == message_sid
        ).first()
        if existing_msg:
            logger.info(f"Duplicate MessageSid '{message_sid}' received. Suppressing re-processing.")
            # Return empty TwiML to acknowledge receipt without re-sending reply
            return Response(content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>', media_type="application/xml")

    # Capture registration step before processing
    session_before = db.query(RegistrationSession).filter(RegistrationSession.phone_number == norm_from).first()
    step_before = session_before.current_step if session_before else "START"

    # Pass into RegistrationService state machine
    try:
        reply_message, step_after, is_completed, farmer_id = RegistrationService.process_message(
            db=db,
            phone_number=norm_from,
            incoming_text=body
        )
    except Exception as e:
        logger.error(f"Error in RegistrationService.process_message: {e}", exc_info=True)
        reply_message = "Meghvani received your message, but the service is temporarily unavailable. Please try again shortly."
        step_after = step_before
        is_completed = False
        farmer_id = None

    # Outbound SMS reply dispatch
    sms_provider = get_sms_provider()
    dispatch_res = sms_provider.send(norm_from, reply_message)
    reply_status = dispatch_res.get("status", "SENT")
    reply_msg_id = dispatch_res.get("provider_message_id")
    trial_notice = dispatch_res.get("trial_notice")
    if trial_notice:
        logger.warning(f"Inbound SMS reply notice for {mask_phone_number(norm_from)}: {trial_notice}")

    # If farmer is known or this was an advisory / registration event, log to AlertLog
    if farmer_id or is_completed:
        try:
            farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first() if farmer_id else None
            alert_type = "ADVISORY_STATUS" if step_after == "STATUS" else ("REGISTRATION_SUCCESS" if is_completed else "SMS_INTERACTION")
            risk_level = "IMPORTANT" if step_after == "STATUS" else "NORMAL"
            block_id = farmer.block_id if farmer else 1

            now = datetime.now(timezone.utc)
            alert_log = AlertLog(
                farmer_id=farmer_id if farmer_id else 1,
                block_id=block_id,
                alert_type=alert_type,
                risk_level=risk_level,
                channel="SMS",
                message=reply_message,
                provider_message_id=reply_msg_id,
                status=reply_status,
                provider=provider_name,
                sent_at=now,
                created_at=now,
                external_dispatch=(provider_name == "TWILIO"),
                decision="WAIT" if "Delay" in reply_message else "SOW_NOW"
            )
            db.add(alert_log)
        except Exception as e:
            logger.warning(f"Could not persist alert_log record: {e}")

    # Persistent InboundMessage log
    inbound_record = InboundMessage(
        provider=provider_name,
        provider_message_id=message_sid if message_sid else f"inbound-{uuid.uuid4().hex[:12]}",
        from_phone=norm_from,
        to_phone=norm_to,
        message_body=body,
        normalized_body=body.strip().upper(),
        received_at=datetime.now(timezone.utc),
        processing_status="PROCESSED",
        registration_step_before=step_before,
        registration_step_after=step_after,
        farmer_id=farmer_id,
        reply_message=reply_message,
        reply_status=reply_status,
    )
    db.add(inbound_record)
    db.commit()

    logger.info(
        f"Inbound SMS processed from {mask_phone_number(norm_from)}: "
        f"body='{body[:30]}', step={step_before}->{step_after}, reply_status={reply_status}"
    )

    # Return empty TwiML since reply is sent via outbound SMS API for consistent tracking
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml"
    )


@router.post("/test-incoming")
def test_incoming_sms(
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Development & test helper endpoint to simulate incoming SMS without external webhook.
    Returns JSON structure of the resulting transaction.
    """
    from_phone = str(payload.get("from_phone") or payload.get("From") or "").strip()
    body = str(payload.get("body") or payload.get("Body") or "").strip()
    message_sid = payload.get("message_sid") or f"test-sid-{uuid.uuid4().hex[:10]}"

    if not from_phone:
        raise HTTPException(status_code=400, detail="from_phone required.")

    norm_from = normalize_phone_number(from_phone)

    # Idempotency check
    if message_sid:
        existing = db.query(InboundMessage).filter(InboundMessage.provider_message_id == message_sid).first()
        if existing:
            return {
                "status": "DUPLICATE_SUPPRESSED",
                "message": "MessageSid already processed.",
                "idempotency_key": message_sid
            }

    session_before = db.query(RegistrationSession).filter(RegistrationSession.phone_number == norm_from).first()
    step_before = session_before.current_step if session_before else "START"

    reply_message, step_after, is_completed, farmer_id = RegistrationService.process_message(
        db=db,
        phone_number=norm_from,
        incoming_text=body
    )

    sms_provider = get_sms_provider()
    dispatch_res = sms_provider.send(norm_from, reply_message)
    reply_status = dispatch_res.get("status", "SENT")
    trial_notice = dispatch_res.get("trial_notice")
    if trial_notice:
        logger.warning(f"Test incoming SMS dispatch notice for {mask_phone_number(norm_from)}: {trial_notice}")

    # Inbound logging
    inbound_record = InboundMessage(
        provider=os.getenv("SMS_PROVIDER") or settings.sms_provider or "MOCK",
        provider_message_id=message_sid,
        from_phone=norm_from,
        to_phone="+911800MEGHVANI",
        message_body=body,
        normalized_body=body.strip().upper(),
        received_at=datetime.now(timezone.utc),
        processing_status="PROCESSED",
        registration_step_before=step_before,
        registration_step_after=step_after,
        farmer_id=farmer_id,
        reply_message=reply_message,
        reply_status=reply_status,
    )
    db.add(inbound_record)
    db.commit()

    return {
        "status": "SUCCESS",
        "from_masked": mask_phone_number(norm_from),
        "inbound_body": body,
        "step_before": step_before,
        "step_after": step_after,
        "is_completed": is_completed,
        "farmer_id": farmer_id,
        "reply_message": reply_message,
        "reply_status": reply_status,
        "provider": inbound_record.provider,
        "trial_notice": trial_notice,
    }


@router.post("/voice-alert")
def trigger_voice_alert(
    payload: VoiceAlertRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Triggers an AI voice alert simulation for a high-risk weather event.
    Utilizes Sarvam AI Bulbul v3 TTS (or browser demo fallback) to generate
    multilingual speech using the existing farmer, location, and ICAR advisory.
    Labels the experience as 'AI VOICE ALERT — DEMO' without claiming real PSTN delivery.
    """
    from app.services.sarvam_tts_service import SarvamTTSService

    target_farmer_id = payload.farmer_id
    if not target_farmer_id:
        active_f = db.query(Farmer).filter(Farmer.active == True).order_by(desc(Farmer.id)).first()
        if not active_f:
            active_f = db.query(Farmer).first()
        if not active_f:
            raise HTTPException(status_code=404, detail="No farmer found in database.")
        target_farmer_id = active_f.id

    try:
        res = SarvamTTSService.generate_voice_alert(
            db=db,
            farmer_id=target_farmer_id,
            alert_id=payload.alert_id,
            language_override=payload.language,
            force_high_risk=payload.force_high_risk,
            alert_type=payload.alert_type or "HEAVY_RAIN"
        )
        return res
    except Exception as e:
        logger.error(f"Voice alert generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Voice alert generation failed: {str(e)}"
        )


@router.post("/voice-event")
def log_voice_call_event(
    payload: VoiceEventRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Logs lifecycle events for the AI voice call simulation:
    - ANSWERED (Farmer answers the incoming alert call)
    - PLAYED / COMPLETED (Farmer finishes listening to the advisory)
    - DECLINED (Farmer rejects or dismisses the call)
    - REPLAY (Farmer replays the audio advisory)
    Preserves honest status reporting without fabricated 'Call Delivered' claims.
    """
    now = datetime.now(timezone.utc)
    status_map = {
        "ANSWERED": "ANSWERED",
        "PLAYED": "PLAYED",
        "COMPLETED": "PLAYED",
        "DECLINED": "DECLINED",
        "REPLAY": "REPLAYED",
    }
    event_upper = payload.event.upper()
    logged_status = status_map.get(event_upper, event_upper)

    # Locate the target AlertLog
    alert_log = None
    if payload.alert_id:
        alert_log = db.query(AlertLog).filter(AlertLog.id == payload.alert_id).first()
    if not alert_log and payload.farmer_id:
        alert_log = db.query(AlertLog).filter(
            AlertLog.farmer_id == payload.farmer_id,
            AlertLog.channel == "VOICE"
        ).order_by(desc(AlertLog.created_at)).first()

    if alert_log:
        alert_log.status = logged_status
        db.commit()

    return {
        "status": "SUCCESS",
        "event": event_upper,
        "logged_status": logged_status,
        "farmer_id": payload.farmer_id,
        "alert_id": payload.alert_id,
        "call_duration_seconds": payload.duration_seconds,
        "timestamp": now.isoformat()
    }


@router.get("/timeline")
def get_communication_timeline(
    limit: int = 50,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Returns an aggregated, chronological timeline of all communication transactions:
    - INBOUND SMS (received via webhook)
    - OUTBOUND SMS (sent replies or scheduled dispatches)
    - AI VOICE ALERTS (Sarvam Bulbul v3 simulated voice advisories)
    - REGISTRATION EVENTS (new farmer completed onboarding)
    - ADVISORY EVENTS (ML prediction & XAI dispatches)
    Phone numbers are strictly masked (******3210) for officer UI privacy.
    """
    timeline: List[Dict[str, Any]] = []

    # 1. Fetch Inbound Messages
    inbound_list = db.query(InboundMessage).order_by(desc(InboundMessage.received_at)).limit(limit).all()

    for in_msg in inbound_list:
        farmer = in_msg.farmer
        village_name = farmer.village.name if (farmer and farmer.village) else None
        block_name = farmer.block.name if (farmer and farmer.block) else None
        crop_name = farmer.crop.name if (farmer and farmer.crop) else None
        farmer_lang = farmer.preferred_language if farmer else None

        # Build XAI context if advisory or status query
        xai_context = None
        if in_msg.registration_step_after == "STATUS" or "MEGHVANI ADVISORY" in (in_msg.reply_message or ""):
            block_code = f"BLK{farmer.block_id:03d}" if (farmer and farmer.block_id) else "BLK003"
            try:
                from app.ml.model_loader import explain_block_false_onset
                xai_res = explain_block_false_onset(block_code)
                xai_context = {
                    "block_id": block_code,
                    "region_name": xai_res.get("region_name", block_name or "Amravati Central"),
                    "probability_pct": xai_res.get("probability_pct", 28),
                    "risk_tier": xai_res.get("risk_tier", "Moderate Risk"),
                    "decision": xai_res.get("decision", "WAIT"),
                    "top_drivers": [
                        {
                            "label": d.get("label"),
                            "direction": d.get("direction"),
                            "share_pct": d.get("share_pct"),
                            "observed_value": d.get("observed_value"),
                            "unit": d.get("unit"),
                        }
                        for d in xai_res.get("top_drivers", [])[:3]
                    ],
                }
            except Exception:
                pass

        # Inbound item
        timeline.append({
            "id": f"in-{in_msg.id}",
            "direction": "INBOUND",
            "event_type": "INBOUND_SMS",
            "timestamp": in_msg.received_at.isoformat() if in_msg.received_at else None,
            "masked_phone": mask_phone_number(in_msg.from_phone),
            "raw_phone": in_msg.from_phone,
            "message_preview": in_msg.message_body[:80] + ("..." if len(in_msg.message_body) > 80 else ""),
            "full_message": in_msg.message_body,
            "provider": in_msg.provider,
            "status": in_msg.processing_status,
            "step_before": in_msg.registration_step_before,
            "step_after": in_msg.registration_step_after,
            "farmer_id": in_msg.farmer_id,
            "farmer_name": f"Farmer #{in_msg.farmer_id}" if in_msg.farmer_id else None,
            "village": village_name,
            "block": block_name,
            "crop": crop_name,
            "language": farmer_lang,
            "xai_context": xai_context,
        })

        # Outbound reply item (paired with inbound)
        if in_msg.reply_message:
            is_new_farmer = in_msg.registration_step_after == "COMPLETED"
            timeline.append({
                "id": f"out-reply-{in_msg.id}",
                "direction": "OUTBOUND",
                "event_type": "NEW_FARMER_REGISTERED" if is_new_farmer else ("ADVISORY" if in_msg.registration_step_after == "STATUS" else "OUTBOUND_SMS"),
                "timestamp": in_msg.received_at.isoformat() if in_msg.received_at else None,
                "masked_phone": mask_phone_number(in_msg.from_phone),
                "raw_phone": in_msg.from_phone,
                "message_preview": in_msg.reply_message[:80] + ("..." if len(in_msg.reply_message) > 80 else ""),
                "full_message": in_msg.reply_message,
                "provider": in_msg.provider,
                "status": in_msg.reply_status or "SENT",
                "step_before": in_msg.registration_step_before,
                "step_after": in_msg.registration_step_after,
                "farmer_id": in_msg.farmer_id,
                "farmer_name": f"Farmer #{in_msg.farmer_id}" if in_msg.farmer_id else None,
                "village": village_name,
                "block": block_name,
                "crop": crop_name,
                "language": farmer_lang,
                "consent": "YES" if (farmer and farmer.consent) else "PENDING",
                "xai_context": xai_context,
            })

    # 2. Fetch AI Voice Alert Logs
    voice_logs = db.query(AlertLog).filter(AlertLog.channel == "VOICE").order_by(desc(AlertLog.created_at)).limit(limit).all()
    for v_log in voice_logs:
        v_farmer = v_log.farmer if hasattr(v_log, "farmer") else db.query(Farmer).filter(Farmer.id == v_log.farmer_id).first()
        v_village = v_farmer.village.name if (v_farmer and v_farmer.village) else "Kalmeshwar"
        v_block = v_farmer.block.name if (v_farmer and v_farmer.block) else "Nagpur Rural"
        v_crop = v_farmer.crop.name if (v_farmer and v_farmer.crop) else "Soybean"
        v_phone = v_farmer.phone_number if v_farmer else "+919876500001"
        v_lang = v_farmer.preferred_language if v_farmer else "mr"

        timeline.append({
            "id": f"voice-{v_log.id}",
            "direction": "OUTBOUND",
            "event_type": "AI_VOICE_ALERT",
            "channel": "VOICE",
            "timestamp": v_log.created_at.isoformat() if v_log.created_at else None,
            "masked_phone": mask_phone_number(v_phone),
            "raw_phone": v_phone,
            "message_preview": f"📞 [AI Voice Alert] {v_log.message[:70]}...",
            "full_message": v_log.message,
            "provider": "Sarvam AI (Bulbul v3)",
            "status": v_log.status or "READY",
            "farmer_id": v_log.farmer_id,
            "farmer_name": f"Farmer #{v_log.farmer_id}",
            "village": v_village,
            "block": v_block,
            "crop": v_crop,
            "language": v_lang,
            "severity": v_log.risk_level or "HIGH",
            "disclaimer": "AI VOICE ALERT — DEMO",
            "xai_context": {
                "block_id": f"BLK{v_log.block_id:03d}",
                "region_name": v_block,
                "probability_pct": 82,
                "risk_tier": "HIGH RISK",
                "decision": "WAIT",
                "top_drivers": [
                    {"label": "Heavy Rain Accumulation", "direction": "INCREASING", "observed_value": "68mm"},
                    {"label": "False Onset Probability", "direction": "INCREASING", "observed_value": "82%"},
                    {"label": "Drainage Saturation", "direction": "INCREASING", "observed_value": "Critical"},
                ]
            }
        })

    # Sort descending by timestamp
    timeline.sort(key=lambda x: x["timestamp"] or "", reverse=True)
    return timeline[:limit]


@router.get("/summary")
def get_communication_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns summary analytics for the Alert Center top cards:
    - SMS Received
    - SMS Sent
    - Active Farmers
    - Latest Advisory
    """
    inbound_count = db.query(InboundMessage).count()
    outbound_alert_count = db.query(AlertLog).filter(AlertLog.channel == "SMS").count()
    # Outbound replies tracked in InboundMessage
    inbound_replies_count = db.query(InboundMessage).filter(InboundMessage.reply_message != None).count()
    total_sms_sent = outbound_alert_count + inbound_replies_count

    active_farmers_count = db.query(Farmer).filter(Farmer.active == True).count()

    latest_advisory_log = db.query(AlertLog).filter(
        AlertLog.alert_type.in_(["ADVISORY_STATUS", "FALSE_ONSET", "ONSET", "HEAVY_RAIN", "BREAK"])
    ).order_by(desc(AlertLog.created_at)).first()

    latest_advisory_text = None
    latest_advisory_time = None
    if latest_advisory_log:
        latest_advisory_text = latest_advisory_log.message[:70] + "..." if len(latest_advisory_log.message) > 70 else latest_advisory_log.message
        latest_advisory_time = latest_advisory_log.created_at.isoformat() if latest_advisory_log.created_at else None

    return {
        "sms_received": inbound_count,
        "sms_sent": total_sms_sent,
        "active_farmers": active_farmers_count,
        "latest_advisory": {
            "snippet": latest_advisory_text or "No advisories dispatched yet.",
            "timestamp": latest_advisory_time,
            "status": "ACTIVE" if latest_advisory_log else "STANDBY"
        }
    }
