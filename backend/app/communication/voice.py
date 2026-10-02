from app.communication.mock_provider import MockVoiceProvider
from app.communication.base import VoiceProvider

def get_voice_provider(force_no_answer: bool = False) -> VoiceProvider:
    # Future: Inspect config or env var to return ExotelVoiceProvider
    return MockVoiceProvider(force_no_answer=force_no_answer)
