from abc import ABC, abstractmethod
from typing import Dict, Any

class SMSProvider(ABC):
    @abstractmethod
    def send(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send an SMS notification to the given phone number."""
        pass

class VoiceProvider(ABC):
    @abstractmethod
    def call(self, phone_number: str, message: str, attempt_number: int = 1) -> Dict[str, Any]:
        """Trigger an automated voice advisory call."""
        pass

    @abstractmethod
    def check_status(self, call_id: str) -> Dict[str, Any]:
        """Query delivery / answer status of a placed voice call."""
        pass

class WhatsAppProvider(ABC):
    @abstractmethod
    def send(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send a WhatsApp message via template/session."""
        pass

class MissedCallProvider(ABC):
    @abstractmethod
    def handle_incoming_ring(self, phone_number: str) -> Dict[str, Any]:
        """Identify incoming caller from missed call webhook."""
        pass
