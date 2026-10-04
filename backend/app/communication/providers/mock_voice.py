"""
Meghvani Phase 6A: Mock Voice / IVR Provider.
Simulates automated outbound voice call with configurable answer or no-answer/failure.
"""
import uuid
from typing import Dict, Any
from app.communication.providers.base import BaseMockProvider

class MockVoiceProvider(BaseMockProvider):
    def __init__(self, fail_mode: bool = False):
        super().__init__(provider_name="mock_voice", fail_mode=fail_mode)

    def dispatch(self, to: str, message: str, **kwargs) -> Dict[str, Any]:
        call_id = f"MOCK-VOICE-{uuid.uuid4().hex[:12].upper()}"
        success = not self.fail_mode

        return {
            "provider": self.provider_name,
            "channel": "VOICE",
            "provider_message_id": call_id,
            "status": "SIMULATED_SENT" if success else "SIMULATED_FAILED",
            "success": success,
            "external_dispatch": False,
            "recipient_masked": f"******{to[-4:]}" if len(to) >= 4 else "******",
            "error": "Simulated voice call unanswered / line busy" if not success else None
        }
