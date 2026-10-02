from app.communication.mock_provider import MockSMSProvider
from app.communication.base import SMSProvider

def get_sms_provider() -> SMSProvider:
    # Future: Inspect config or env var to return TwilioSMSProvider or GupshupSMSProvider
    return MockSMSProvider()
