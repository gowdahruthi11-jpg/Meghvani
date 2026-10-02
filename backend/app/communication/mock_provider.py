import uuid
import random
from typing import Dict, Any
from app.communication.base import SMSProvider, VoiceProvider, WhatsAppProvider, MissedCallProvider

class MockSMSProvider(SMSProvider):
    """
    Simulates SMS dispatch without connecting to external telco/Twilio/Gupshup gateway.
    """
    def send(self, phone_number: str, message: str) -> Dict[str, Any]:
        msg_id = f"mock-sms-{uuid.uuid4().hex[:12]}"
        return {
            "status": "SIMULATED",
            "provider_message_id": msg_id,
            "channel": "SMS",
            "phone_number": phone_number,
            "message_snippet": message[:60] + ("..." if len(message) > 60 else ""),
            "note": "PROTOTYPE MOCK PROVIDER - No real SMS delivered."
        }


class MockVoiceProvider(VoiceProvider):
    """
    Simulates Voice call dispatch. Includes deterministic or stochastic
    simulation of unanswered calls (NO_ANSWER) to test retry and SMS fallback logic.
    """
    def __init__(self, force_no_answer: bool = False, no_answer_rate: float = 0.35):
        self.force_no_answer = force_no_answer
        self.no_answer_rate = no_answer_rate

    def call(self, phone_number: str, message: str, attempt_number: int = 1) -> Dict[str, Any]:
        call_id = f"mock-voice-{uuid.uuid4().hex[:12]}"
        
        # Simulate no-answer if forced or probabilistically on attempt 1
        is_no_answer = self.force_no_answer or (attempt_number == 1 and random.random() < self.no_answer_rate)
        status = "NO_ANSWER" if is_no_answer else "SIMULATED"

        return {
            "status": status,
            "provider_message_id": call_id,
            "channel": "VOICE",
            "phone_number": phone_number,
            "attempt_number": attempt_number,
            "note": "PROTOTYPE MOCK PROVIDER - No real Voice call placed."
        }

    def check_status(self, call_id: str) -> Dict[str, Any]:
        return {
            "provider_message_id": call_id,
            "status": "COMPLETED",
            "duration_seconds": 25,
            "note": "PROTOTYPE MOCK STATUS"
        }


class MockWhatsAppProvider(WhatsAppProvider):
    """
    Simulates WhatsApp Business Cloud API message dispatch.
    """
    def send(self, phone_number: str, message: str) -> Dict[str, Any]:
        wa_id = f"mock-wa-{uuid.uuid4().hex[:12]}"
        return {
            "status": "SIMULATED",
            "provider_message_id": wa_id,
            "channel": "WHATSAPP",
            "phone_number": phone_number,
            "note": "PROTOTYPE MOCK PROVIDER - No real WhatsApp message sent."
        }


class MockMissedCallProvider(MissedCallProvider):
    """
    Simulates incoming missed call detection for zero-cost farmer onboarding.
    Future: Connects to Exotel/Ozonetel webhook for CLI detection.
    """
    def handle_incoming_ring(self, phone_number: str) -> Dict[str, Any]:
        return {
            "registration_started": True,
            "phone_number": phone_number,
            "provider_event_id": f"mock-ring-{uuid.uuid4().hex[:8]}",
            "channel": "MISSED_CALL",
            "note": "PROTOTYPE MOCK - Inbound ring identified, SMS/IVR workflow triggered."
        }
