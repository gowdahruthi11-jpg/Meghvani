from app.communication.mock_provider import MockWhatsAppProvider
from app.communication.base import WhatsAppProvider

def get_whatsapp_provider() -> WhatsAppProvider:
    # Future: Inspect config or env var to return MetaWhatsAppProvider
    return MockWhatsAppProvider()
