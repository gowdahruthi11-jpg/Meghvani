import os
from app.communication.mock_provider import MockSMSProvider
from app.communication.twilio_sms import TwilioSMSProvider
from app.communication.base import SMSProvider
from app.config import settings


def get_sms_provider() -> SMSProvider:
    """
    Returns the configured SMSProvider.
    Uses environment variable SMS_PROVIDER or settings.sms_provider.
    Defaults to MockSMSProvider if unset or set to 'MOCK'.
    """
    provider_name = os.getenv("SMS_PROVIDER") or settings.sms_provider or "MOCK"
    provider_name = provider_name.strip().upper()

    if provider_name == "TWILIO":
        account_sid = os.getenv("TWILIO_ACCOUNT_SID") or settings.twilio_account_sid
        auth_token = os.getenv("TWILIO_AUTH_TOKEN") or settings.twilio_auth_token
        phone_number = os.getenv("TWILIO_PHONE_NUMBER") or settings.twilio_phone_number
        if account_sid and auth_token and phone_number:
            return TwilioSMSProvider(
                account_sid=account_sid,
                auth_token=auth_token,
                from_phone_number=phone_number,
            )
        return MockSMSProvider()

    return MockSMSProvider()
