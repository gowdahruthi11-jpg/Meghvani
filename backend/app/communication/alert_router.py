"""
Meghvani Phase 6A: Alert Routing, Consent Verification & Communication Simulation Engine.

Enforces:
1. NO CONSENT -> NO DISPATCH (COMMUNICATION_NOT_AUTHORIZED)
2. NO VALIDATED RULE -> NO ALERT (BLOCKED_NO_VALIDATED_RULE)
3. NO FORECAST -> NO ALERT (BLOCKED_NO_FORECAST)
4. DUPLICATE SUPPRESSION -> 24h Cooldown
5. PROTOTYPE_ALERT_POLICY -> Severity-based channel routing & automatic SMS fallback
6. EXTERNAL_DISPATCH = FALSE (Pure Mock Simulation)
"""
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
import logging

from app.models.farmer import Farmer
from app.models.block import Block
from app.models.alert_log import AlertLog
from app.advisory.models import AdvisoryStatus, ValidationStatus
from app.advisory.rule_engine import AdvisoryRuleEngine
from app.advisory.rule_registry import default_rule_registry
from app.advisory.message_generator import AdvisoryMessageGenerator, FarmerAdvisoryMessage
from app.ml.model_loader import predict_block_false_onset
from app.ml.decision_engine import PrototypeDecisionEngine
from app.communication.providers.mock_sms import MockSMSProvider
from app.communication.providers.mock_whatsapp import MockWhatsAppProvider
from app.communication.providers.mock_voice import MockVoiceProvider

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    INFO = "INFO"
    IMPORTANT = "IMPORTANT"
    HIGH = "HIGH"


class DeliveryStatus(str, Enum):
    QUEUED = "QUEUED"
    SIMULATED_SENT = "SIMULATED_SENT"
    SIMULATED_FAILED = "SIMULATED_FAILED"
    FALLBACK_USED = "FALLBACK_USED"
    BLOCKED_NO_CONSENT = "BLOCKED_NO_CONSENT"
    BLOCKED_NO_VALIDATED_RULE = "BLOCKED_NO_VALIDATED_RULE"
    BLOCKED_NO_FORECAST = "BLOCKED_NO_FORECAST"
    DUPLICATE_SUPPRESSED = "DUPLICATE_SUPPRESSED"


class AlertRouter:
    """
    Simulated Alert Router and Delivery Orchestrator for Phase 6A.
    """
    POLICY_NAME = "PROTOTYPE_ALERT_POLICY"
    DEFAULT_COOLDOWN_HOURS = 24

    def __init__(
        self,
        sms_provider: Optional[MockSMSProvider] = None,
        whatsapp_provider: Optional[MockWhatsAppProvider] = None,
        voice_provider: Optional[MockVoiceProvider] = None
    ):
        self.sms_provider = sms_provider or MockSMSProvider()
        self.whatsapp_provider = whatsapp_provider or MockWhatsAppProvider()
        self.voice_provider = voice_provider or MockVoiceProvider()

    @staticmethod
    def mask_phone_number(phone: Optional[str]) -> str:
        """
        Privacy masking: masks phone number exposing only the last 4 digits.
        """
        if not phone:
            return "******"
        p = str(phone).strip()
        if len(p) <= 4:
            return "******"
        return f"******{p[-4:]}"

    @classmethod
    def determine_severity(cls, decision: str, probability: float) -> AlertSeverity:
        """
        Configurable prototype alert policy mapping decisions & probability to severity:
        - HIGH: decision is WAIT with probability >= 0.60
        - IMPORTANT: decision is WAIT (moderate) or significant change
        - INFO: decision is SOW_NOW (low risk) or routine advisory
        """
        if decision == "WAIT":
            if probability >= 0.60:
                return AlertSeverity.HIGH
            return AlertSeverity.IMPORTANT
        elif decision == "SOW_NOW":
            return AlertSeverity.INFO
        return AlertSeverity.INFO

    @classmethod
    def get_channel_plan(
        cls,
        severity: AlertSeverity,
        preference: Optional[str] = None
    ) -> List[str]:
        """
        Determines channel routing sequence based on prototype alert policy:
        - INFO: SMS
        - IMPORTANT: SMS + WhatsApp
        - HIGH: Voice + SMS
        Farmer preference is respected when specified, with SMS retained as backup.
        """
        pref = (preference or "").strip().upper()
        if pref == "ALL":
            if severity == AlertSeverity.HIGH:
                return ["VOICE", "WHATSAPP", "SMS"]
            elif severity == AlertSeverity.IMPORTANT:
                return ["WHATSAPP", "SMS"]
            return ["SMS"]

        if pref == "WHATSAPP":
            return ["WHATSAPP", "SMS"] if severity != AlertSeverity.INFO else ["WHATSAPP"]
        elif pref == "VOICE":
            return ["VOICE", "SMS"]

        # Default Prototype Routing Policy
        if severity == AlertSeverity.HIGH:
            return ["VOICE", "SMS"]
        elif severity == AlertSeverity.IMPORTANT:
            return ["SMS", "WHATSAPP"]
        else:
            return ["SMS"]

    @classmethod
    def check_duplicate(
        cls,
        db: Session,
        farmer_id: int,
        block_id: int,
        crop_id: str,
        decision: str,
        cooldown_hours: int = 24
    ) -> bool:
        """
        Checks if an identical alert has already been simulated within the cooldown period.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=cooldown_hours)
        existing = (
            db.query(AlertLog)
            .filter(
                AlertLog.farmer_id == farmer_id,
                AlertLog.block_id == block_id,
                AlertLog.crop_id == crop_id,
                AlertLog.decision == decision,
                AlertLog.status.in_([
                    DeliveryStatus.SIMULATED_SENT.value,
                    DeliveryStatus.FALLBACK_USED.value
                ]),
                AlertLog.created_at >= cutoff
            )
            .first()
        )
        return existing is not None

    def preview_alert(
        self,
        db: Session,
        farmer_id: int,
        crop_id: Optional[str] = None,
        language: Optional[str] = None,
        severity: Optional[str] = None,
        channel: Optional[str] = None,
        forecast_override: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates an alert preview without creating database logs or simulating provider dispatch.
        Supports deterministic forecast_override for historical replay / demonstration.
        """
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not farmer:
            return {
                "alert_status": "BLOCKED_FARMER_NOT_FOUND",
                "error": f"Farmer ID {farmer_id} not found",
                "is_operational": False,
                "external_dispatch": False
            }

        effective_crop = crop_id or (farmer.crop.name.lower() if farmer.crop else "soybean")
        effective_lang = AdvisoryMessageGenerator.normalize_language(language or farmer.preferred_language)

        # 1. Consent Gate Check
        if not farmer.active or not farmer.consent or not farmer.phone_number:
            return {
                "alert_status": DeliveryStatus.BLOCKED_NO_CONSENT.value,
                "reason": "Farmer has not provided mandatory consent, is inactive, or missing phone",
                "farmer_id": farmer.id,
                "language": effective_lang,
                "masked_phone": self.mask_phone_number(farmer.phone_number),
                "is_operational": False,
                "external_dispatch": False
            }

        # 2. Block lookup
        block = db.query(Block).filter(Block.id == farmer.block_id).first()
        block_str = f"BLK{farmer.block_id:03d}" if farmer.block_id else "BLK001"

        # 3. Forecast lookup
        try:
            if forecast_override is not None:
                forecast = forecast_override
            else:
                forecast = predict_block_false_onset(block_str)
            raw_prob = forecast.get("raw_probability", forecast.get("probability", 0.0))
        except Exception as e:
            return {
                "alert_status": DeliveryStatus.BLOCKED_NO_FORECAST.value,
                "reason": f"Forecast unavailable for block {block_str}: {str(e)}",
                "language": effective_lang,
                "is_operational": False,
                "external_dispatch": False
            }

        # 4. Decision lookup
        dec_engine = PrototypeDecisionEngine()
        dec = dec_engine.evaluate(
            probability=raw_prob,
            probability_status="RAW_PROTOTYPE",
            calibration_status=forecast.get("calibration_status", "INSUFFICIENT_CALIBRATION_DATA"),
            evaluation_status=forecast.get("evaluation_status", "INSUFFICIENT_EVENT_VARIATION")
        )

        # 5. Validated Agronomic Rule lookup
        adv_engine = AdvisoryRuleEngine(registry=default_rule_registry)
        adv_res = adv_engine.evaluate(
            crop_id=effective_crop,
            decision=dec["decision"],
            probability=dec["probability"],
            block_id=block_str,
            geography="Maharashtra",
            language="en"
        )

        if adv_res.advisory_status != AdvisoryStatus.RULE_MATCHED or adv_res.validation_status != ValidationStatus.VALIDATED:
            return {
                "alert_status": DeliveryStatus.BLOCKED_NO_VALIDATED_RULE.value,
                "reason": f"No validated agronomic rule exists for crop '{effective_crop}' and decision '{dec['decision']}'",
                "decision": dec["decision"],
                "probability": dec["probability"],
                "is_operational": False,
                "external_dispatch": False
            }

        # 6. Severity & Channel Plan
        eff_sev = AlertSeverity(severity.upper()) if severity and severity.upper() in AlertSeverity.__members__ else self.determine_severity(dec["decision"], dec["probability"])
        channel_plan = self.get_channel_plan(eff_sev, channel or farmer.communication_preference)

        # 7. Generate Message Preview
        primary_chan = channel_plan[0].lower() if channel_plan else "sms"
        msg_obj = AdvisoryMessageGenerator.generate_message(
            advisory_result=adv_res,
            block_id=block_str,
            crop_id=effective_crop,
            decision=dec["decision"],
            language=effective_lang,
            channel=primary_chan,
            forecast_available=True
        )

        return {
            "alert_status": "READY_FOR_SIMULATION",
            "farmer_id": farmer.id,
            "masked_phone": self.mask_phone_number(farmer.phone_number),
            "block_id": farmer.block_id,
            "crop_id": effective_crop,
            "decision": dec["decision"],
            "probability": dec["probability"],
            "severity": eff_sev.value,
            "routing_policy": self.POLICY_NAME,
            "channel_plan": channel_plan,
            "advisory_status": "VALIDATED_RULE",
            "source_institution": adv_res.source.source_institution if adv_res.source else None,
            "source_title": adv_res.source.source_title if adv_res.source else None,
            "message_preview": msg_obj.message,
            "language": effective_lang,
            "is_operational": False,
            "external_dispatch": False,
            "prototype_warning": msg_obj.prototype_warning
        }

    def simulate_dispatch(
        self,
        db: Session,
        farmer_id: int,
        crop_id: Optional[str] = None,
        language: Optional[str] = None,
        severity: Optional[str] = None,
        channel_preference: Optional[str] = None,
        force_failure_channel: Optional[str] = None,
        cooldown_hours: int = 24,
        forecast_override: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes complete simulation dispatch flow:
        - Consent check
        - Forecast & decision lookup (supports deterministic forecast_override)
        - Validated rule check
        - Duplicate suppression check
        - Channel routing & mock provider dispatch
        - Fallback simulation on failure
        - Logs audit trail to database
        """
        now = datetime.now(timezone.utc)
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not farmer:
            return {
                "status": "BLOCKED_FARMER_NOT_FOUND",
                "error": f"Farmer ID {farmer_id} not found",
                "external_dispatch": False,
                "is_operational": False
            }

        masked_phone = self.mask_phone_number(farmer.phone_number)
        effective_crop = crop_id or (farmer.crop.name.lower() if farmer.crop else "soybean")
        effective_lang = AdvisoryMessageGenerator.normalize_language(language or farmer.preferred_language)

        # 1. Consent Gate Check
        if not farmer.active or not farmer.consent or not farmer.phone_number:
            log = AlertLog(
                farmer_id=farmer.id,
                block_id=farmer.block_id or 1,
                crop_id=effective_crop,
                alert_type="ROUTINE_ADVISORY",
                risk_level="NORMAL",
                severity="INFO",
                channel="SMS",
                message="Consent missing, farmer inactive, or phone missing",
                status=DeliveryStatus.BLOCKED_NO_CONSENT.value,
                language=effective_lang,
                provider="mock_sms",
                fallback_used=False,
                reason="Farmer has not given consent, is inactive, or missing phone",
                external_dispatch=False,
                created_at=now
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            return {
                "alert_id": log.id,
                "status": DeliveryStatus.BLOCKED_NO_CONSENT.value,
                "reason": "Farmer consent is False, account is inactive, or phone missing",
                "farmer_id": farmer.id,
                "language": effective_lang,
                "masked_phone": masked_phone,
                "external_dispatch": False,
                "is_operational": False
            }

        # 2. Block & Forecast lookup
        block_str = f"BLK{farmer.block_id:03d}" if farmer.block_id else "BLK001"
        try:
            if forecast_override is not None:
                forecast = forecast_override
            else:
                forecast = predict_block_false_onset(block_str)
            raw_prob = forecast.get("raw_probability", forecast.get("probability", 0.0))
        except Exception as e:
            log = AlertLog(
                farmer_id=farmer.id,
                block_id=farmer.block_id,
                crop_id=effective_crop,
                alert_type="ROUTINE_ADVISORY",
                risk_level="NORMAL",
                severity="INFO",
                channel="SMS",
                message="Forecast unavailable",
                status=DeliveryStatus.BLOCKED_NO_FORECAST.value,
                language=effective_lang,
                provider="mock_sms",
                fallback_used=False,
                reason=f"Forecast lookup failed: {str(e)}",
                external_dispatch=False,
                created_at=now
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            return {
                "alert_id": log.id,
                "status": DeliveryStatus.BLOCKED_NO_FORECAST.value,
                "reason": f"Forecast unavailable: {str(e)}",
                "farmer_id": farmer.id,
                "masked_phone": masked_phone,
                "external_dispatch": False,
                "is_operational": False
            }

        # 3. Decision lookup
        dec_engine = PrototypeDecisionEngine()
        dec = dec_engine.evaluate(
            probability=raw_prob,
            probability_status="RAW_PROTOTYPE",
            calibration_status=forecast.get("calibration_status", "INSUFFICIENT_CALIBRATION_DATA"),
            evaluation_status=forecast.get("evaluation_status", "INSUFFICIENT_EVENT_VARIATION")
        )

        # 4. Validated Agronomic Rule lookup
        adv_engine = AdvisoryRuleEngine(registry=default_rule_registry)
        adv_res = adv_engine.evaluate(
            crop_id=effective_crop,
            decision=dec["decision"],
            probability=dec["probability"],
            block_id=block_str,
            geography="Maharashtra",
            language="en"
        )

        if adv_res.advisory_status != AdvisoryStatus.RULE_MATCHED or adv_res.validation_status != ValidationStatus.VALIDATED:
            log = AlertLog(
                farmer_id=farmer.id,
                block_id=farmer.block_id,
                crop_id=effective_crop,
                alert_type=dec["decision"],
                decision=dec["decision"],
                risk_level="NORMAL",
                severity="INFO",
                channel="SMS",
                message="No validated agronomic rule available",
                status=DeliveryStatus.BLOCKED_NO_VALIDATED_RULE.value,
                language=effective_lang,
                provider="mock_sms",
                fallback_used=False,
                reason=f"No validated rule found for crop '{effective_crop}' and decision '{dec['decision']}'",
                external_dispatch=False,
                created_at=now
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            return {
                "alert_id": log.id,
                "status": DeliveryStatus.BLOCKED_NO_VALIDATED_RULE.value,
                "reason": f"No validated agronomic rule exists for crop '{effective_crop}' and decision '{dec['decision']}'",
                "farmer_id": farmer.id,
                "decision": dec["decision"],
                "masked_phone": masked_phone,
                "external_dispatch": False,
                "is_operational": False
            }

        # 5. Duplicate Check
        if self.check_duplicate(db, farmer.id, farmer.block_id, effective_crop, dec["decision"], cooldown_hours):
            log = AlertLog(
                farmer_id=farmer.id,
                block_id=farmer.block_id,
                crop_id=effective_crop,
                alert_type=dec["decision"],
                decision=dec["decision"],
                risk_level="NORMAL",
                severity="INFO",
                channel="SMS",
                message="Duplicate alert suppressed by cooldown policy",
                status=DeliveryStatus.DUPLICATE_SUPPRESSED.value,
                language=effective_lang,
                provider="mock_sms",
                fallback_used=False,
                reason=f"Identical alert was already simulated within {cooldown_hours}h cooldown window",
                external_dispatch=False,
                created_at=now
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            return {
                "alert_id": log.id,
                "status": DeliveryStatus.DUPLICATE_SUPPRESSED.value,
                "reason": f"Identical alert suppressed within {cooldown_hours}h cooldown window",
                "farmer_id": farmer.id,
                "decision": dec["decision"],
                "masked_phone": masked_phone,
                "external_dispatch": False,
                "is_operational": False
            }

        # 6. Severity & Routing Plan
        eff_sev = AlertSeverity(severity.upper()) if severity and severity.upper() in AlertSeverity.__members__ else self.determine_severity(dec["decision"], dec["probability"])
        channel_plan = self.get_channel_plan(eff_sev, channel_preference or farmer.communication_preference)

        # 7. Execute Mock Provider Dispatch with Fallback Simulation
        dispatched_logs: List[AlertLog] = []
        overall_status = DeliveryStatus.SIMULATED_SENT.value
        fallback_used = False
        dispatches_summary: List[Dict[str, Any]] = []

        force_fail_norm = (force_failure_channel or "").strip().upper()

        for chan in channel_plan:
            chan_upper = chan.upper()
            chan_lower = chan.lower()
            msg_obj = AdvisoryMessageGenerator.generate_message(
                advisory_result=adv_res,
                block_id=block_str,
                crop_id=effective_crop,
                decision=dec["decision"],
                language=effective_lang,
                channel=chan_lower,
                forecast_available=True
            )

            # Check if this channel is forced to fail for resilience testing
            should_fail = (chan_upper == force_fail_norm)

            if chan_upper == "VOICE":
                provider_inst = MockVoiceProvider(fail_mode=should_fail)
                prov_res = provider_inst.dispatch(farmer.phone_number, msg_obj.message)
            elif chan_upper == "WHATSAPP":
                provider_inst = MockWhatsAppProvider(fail_mode=should_fail)
                prov_res = provider_inst.dispatch(farmer.phone_number, msg_obj.message)
            else:
                provider_inst = MockSMSProvider(fail_mode=should_fail)
                prov_res = provider_inst.dispatch(farmer.phone_number, msg_obj.message)

            dispatches_summary.append(prov_res)

            # If primary channel failed, trigger automated SMS Fallback
            if not prov_res.get("success", False):
                # Log failed attempt
                log_failed = AlertLog(
                    farmer_id=farmer.id,
                    block_id=farmer.block_id,
                    crop_id=effective_crop,
                    alert_type=dec["decision"],
                    decision=dec["decision"],
                    risk_level=eff_sev.value,
                    severity=eff_sev.value,
                    message_type=dec["decision"],
                    channel=chan_upper,
                    message=msg_obj.message,
                    provider_message_id=prov_res.get("provider_message_id"),
                    status=DeliveryStatus.SIMULATED_FAILED.value,
                    language=effective_lang,
                    provider=prov_res.get("provider"),
                    fallback_used=False,
                    reason=prov_res.get("error", "Simulated transmission failure"),
                    external_dispatch=False,
                    sent_at=now,
                    created_at=now
                )
                db.add(log_failed)
                dispatched_logs.append(log_failed)

                # Fallback to SMS if failed channel was not already SMS
                if chan_upper != "SMS":
                    fallback_used = True
                    overall_status = DeliveryStatus.FALLBACK_USED.value
                    sms_fallback_msg = AdvisoryMessageGenerator.generate_message(
                        advisory_result=adv_res,
                        block_id=block_str,
                        crop_id=effective_crop,
                        decision=dec["decision"],
                        language=effective_lang,
                        channel="sms",
                        forecast_available=True
                    )
                    sms_fallback_prov = MockSMSProvider(fail_mode=False)
                    fb_res = sms_fallback_prov.dispatch(farmer.phone_number, sms_fallback_msg.message)
                    dispatches_summary.append(fb_res)

                    log_fallback = AlertLog(
                        farmer_id=farmer.id,
                        block_id=farmer.block_id,
                        crop_id=effective_crop,
                        alert_type=dec["decision"],
                        decision=dec["decision"],
                        risk_level=eff_sev.value,
                        severity=eff_sev.value,
                        message_type=dec["decision"],
                        channel="SMS",
                        message=sms_fallback_msg.message,
                        provider_message_id=fb_res.get("provider_message_id"),
                        status=DeliveryStatus.FALLBACK_USED.value,
                        language=effective_lang,
                        provider=fb_res.get("provider"),
                        fallback_used=True,
                        fallback_channel=chan_upper,
                        reason=f"Automated fallback to SMS following {chan_upper} failure",
                        external_dispatch=False,
                        sent_at=now,
                        created_at=now
                    )
                    db.add(log_fallback)
                    dispatched_logs.append(log_fallback)
            else:
                # Successful simulated dispatch
                log_success = AlertLog(
                    farmer_id=farmer.id,
                    block_id=farmer.block_id,
                    crop_id=effective_crop,
                    alert_type=dec["decision"],
                    decision=dec["decision"],
                    risk_level=eff_sev.value,
                    severity=eff_sev.value,
                    message_type=dec["decision"],
                    channel=chan_upper,
                    message=msg_obj.message,
                    provider_message_id=prov_res.get("provider_message_id"),
                    status=DeliveryStatus.SIMULATED_SENT.value,
                    language=effective_lang,
                    provider=prov_res.get("provider"),
                    fallback_used=False,
                    reason="Routine prototype policy dispatch",
                    external_dispatch=False,
                    sent_at=now,
                    created_at=now
                )
                db.add(log_success)
                dispatched_logs.append(log_success)

        db.commit()
        for l in dispatched_logs:
            db.refresh(l)

        last_log = dispatched_logs[-1] if dispatched_logs else None

        return {
            "alert_id": last_log.id if last_log else None,
            "status": overall_status,
            "farmer_id": farmer.id,
            "masked_phone": masked_phone,
            "block_id": farmer.block_id,
            "crop_id": effective_crop,
            "decision": dec["decision"],
            "severity": eff_sev.value,
            "routing_policy": self.POLICY_NAME,
            "channel_plan": channel_plan,
            "fallback_used": fallback_used,
            "dispatches": dispatches_summary,
            "source_institution": adv_res.source.source_institution if adv_res.source else None,
            "source_title": adv_res.source.source_title if adv_res.source else None,
            "message": last_log.message if last_log else "",
            "language": effective_lang,
            "external_dispatch": False,
            "is_operational": False,
            "prototype_warning": "Meghvani prototype advisory — not a substitute for local agricultural expert guidance."
        }


# Singleton router instance
default_alert_router = AlertRouter()
