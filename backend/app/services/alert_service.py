from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.config import communication_config
from app.models.farmer import Farmer
from app.models.alert_log import AlertLog
from app.communication.sms import get_sms_provider
from app.communication.voice import get_voice_provider
from app.communication.whatsapp import get_whatsapp_provider

class AlertService:
    """
    Orchestrates severity-based alert dispatching, multi-channel routing,
    voice retry loops, and automatic SMS fallback on unanswered voice calls.
    """

    @classmethod
    def get_routing_channels(cls, risk_level: str) -> List[str]:
        matrix = communication_config.get("routing_matrix", {})
        config_entry = matrix.get(risk_level.upper())
        if config_entry and "channels" in config_entry:
            return config_entry["channels"]
        # Default fallback
        return ["SMS"]

    @classmethod
    def dispatch_alert_to_farmer(
        cls,
        db: Session,
        farmer: Farmer,
        alert_type: str,
        risk_level: str,
        message: str,
        force_voice_no_answer: bool = False
    ) -> List[AlertLog]:
        """
        Dispatches an alert to a single farmer across channels dictated by severity risk level.
        Handles Voice call retries and SMS fallback when voice calls are unanswered.
        """
        channels = cls.get_routing_channels(risk_level)
        sms_provider = get_sms_provider()
        voice_provider = get_voice_provider(force_no_answer=force_voice_no_answer)
        whatsapp_provider = get_whatsapp_provider()

        created_logs: List[AlertLog] = []
        now = datetime.now(timezone.utc)

        voice_succeeded = False
        voice_attempted = False

        for channel in channels:
            if channel == "SMS":
                res = sms_provider.send(farmer.phone_number, message)
                log = AlertLog(
                    farmer_id=farmer.id,
                    block_id=farmer.block_id,
                    alert_type=alert_type,
                    risk_level=risk_level,
                    channel="SMS",
                    message=message,
                    provider_message_id=res.get("provider_message_id"),
                    status=res.get("status", "SIMULATED"),
                    attempt_number=1,
                    sent_at=now,
                    created_at=now
                )
                db.add(log)
                created_logs.append(log)

            elif channel == "WHATSAPP":
                res = whatsapp_provider.send(farmer.phone_number, message)
                log = AlertLog(
                    farmer_id=farmer.id,
                    block_id=farmer.block_id,
                    alert_type=alert_type,
                    risk_level=risk_level,
                    channel="WHATSAPP",
                    message=message,
                    provider_message_id=res.get("provider_message_id"),
                    status=res.get("status", "SIMULATED"),
                    attempt_number=1,
                    sent_at=now,
                    created_at=now
                )
                db.add(log)
                created_logs.append(log)

            elif channel == "VOICE":
                voice_attempted = True
                max_retries = 2
                attempt = 1
                voice_status = "NO_ANSWER"

                while attempt <= max_retries:
                    res = voice_provider.call(farmer.phone_number, message, attempt_number=attempt)
                    voice_status = res.get("status", "SIMULATED")

                    log = AlertLog(
                        farmer_id=farmer.id,
                        block_id=farmer.block_id,
                        alert_type=alert_type,
                        risk_level=risk_level,
                        channel="VOICE",
                        message=f"[Voice Call Script] {message}",
                        provider_message_id=res.get("provider_message_id"),
                        status=voice_status,
                        attempt_number=attempt,
                        sent_at=now,
                        created_at=now
                    )
                    db.add(log)
                    created_logs.append(log)

                    if voice_status != "NO_ANSWER":
                        voice_succeeded = True
                        break

                    attempt += 1

                # If voice call remained unanswered after all retries, trigger SMS fallback
                if not voice_succeeded:
                    fallback_msg = f"[Fallback SMS - Voice Unanswered] {message}"
                    sms_res = sms_provider.send(farmer.phone_number, fallback_msg)
                    fallback_log = AlertLog(
                        farmer_id=farmer.id,
                        block_id=farmer.block_id,
                        alert_type=alert_type,
                        risk_level=risk_level,
                        channel="SMS",
                        message=fallback_msg,
                        provider_message_id=sms_res.get("provider_message_id"),
                        status="SIMULATED",
                        attempt_number=1,
                        sent_at=now,
                        created_at=now
                    )
                    db.add(fallback_log)
                    created_logs.append(fallback_log)

        db.commit()
        for log in created_logs:
            db.refresh(log)

        return created_logs

    @classmethod
    def simulate_block_alert(
        cls,
        db: Session,
        block_id: int,
        alert_type: str = "ONSET",
        risk_level: str = "NORMAL",
        crop_id: Optional[int] = None,
        override_message: Optional[str] = None,
        force_voice_no_answer: bool = False
    ) -> List[AlertLog]:
        """
        Simulates broadcasting an alert to all active registered farmers in a block.
        """
        query = db.query(Farmer).filter(
            Farmer.block_id == block_id,
            Farmer.active == True
        )
        if crop_id:
            query = query.filter(Farmer.crop_id == crop_id)

        target_farmers = query.all()
        all_dispatches: List[AlertLog] = []

        default_message = (
            override_message or
            f"Meghvani Alert ({alert_type} - {risk_level} Risk): Weather event expected in your block. "
            "Please check agricultural advisories."
        )

        for farmer in target_farmers:
            logs = cls.dispatch_alert_to_farmer(
                db=db,
                farmer=farmer,
                alert_type=alert_type,
                risk_level=risk_level,
                message=default_message,
                force_voice_no_answer=force_voice_no_answer
            )
            all_dispatches.extend(logs)

        return all_dispatches
