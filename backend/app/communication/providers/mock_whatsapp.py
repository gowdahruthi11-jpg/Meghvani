"""
Meghvani Phase 6A: Mock WhatsApp Provider.
Simulates WhatsApp Cloud API transmission with configurable delivery success or failure.
"""
import uuid
from typing import Dict, Any
from app.communication.providers.base import BaseMockProvider

class MockWhatsAppProvider(BaseMockProvider):
    def __init__(self, fail_mode: bool = False):
        super().__init__(provider_name="mock_whatsapp", fail_mode=fail_mode)

    def dispatch(self, to: str, message: str, **kwargs) -> Dict[str, Any]:
        msg_id = f"MOCK-WA-{uuid.uuid4().hex[:12].upper()}"
        success = not self.fail_mode

        return {
            "provider": self.provider_name,
            "channel": "WHATSAPP",
            "provider_message_id": msg_id,
            "status": "SIMULATED_SENT" if success else "SIMULATED_FAILED",
            "success": success,
            "external_dispatch": False,
            "recipient_masked": f"******{to[-4:]}" if len(to) >= 4 else "******",
            "error": "Simulated WhatsApp delivery failure" if not success else None
        }
