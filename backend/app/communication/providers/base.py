"""
Meghvani Phase 6A: Base Mock Communication Provider Interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseMockProvider(ABC):
    """
    Abstract interface for simulated communication providers.
    Enforces prototype boundary: NEVER performs real external dispatch.
    """
    def __init__(self, provider_name: str, fail_mode: bool = False):
        self.provider_name = provider_name
        self.fail_mode = fail_mode

    def set_fail_mode(self, fail: bool):
        self.fail_mode = fail

    @abstractmethod
    def dispatch(self, to: str, message: str, **kwargs) -> Dict[str, Any]:
        """
        Simulates dispatching a message to the target recipient.
        """
        pass
