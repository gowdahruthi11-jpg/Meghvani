"""
Meghvani Phase 6A: Mock SMS Provider.
Simulates SMS transmission with configurable delivery success or failure.
"""
import uuid
from typing import Dict, Any
from app.communication.providers.base import BaseMockProvider

class MockSMSProvider(BaseMockProvider):
    def __init__(self, fail_mode: bool = False):
        super().__init__(provider_name="mock_sms", fail_mode=fail_mode)

    def dispatch(self, to: str, message: str, **kwargs) -> Dict[str, Any]:
        msg_id = f"MOCK-SMS-{uuid.uuid4().hex[:12].upper()}"
        success = not self.fail_mode

        return {
            "provider": self.provider_name,
            "channel": "SMS",
            "provider_message_id": msg_id,
            "status": "SIMULATED_SENT" if success else "SIMULATED_FAILED",
            "success": success,
            "external_dispatch": False,
            "recipient_masked": f"******{to[-4:]}" if len(to) >= 4 else "******",
            "error": "Simulated SMS gateway timeout" if not success else None
        }
