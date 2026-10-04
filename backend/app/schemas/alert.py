from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict

class AlertPreviewRequest(BaseModel):
    farmer_id: int
    crop_id: Optional[str] = None
    language: Optional[str] = "en"
    severity: Optional[str] = None
    channel: Optional[str] = None

class AlertSimulationRequest(BaseModel):
    farmer_id: Optional[int] = None
    block_id: Optional[int] = None
    alert_type: Optional[str] = "ROUTINE_ADVISORY"
    risk_level: Optional[str] = "NORMAL"
    severity: Optional[str] = None
    crop_id: Optional[Any] = None
    language: Optional[str] = None
    channel_preference: Optional[str] = None
    force_failure_channel: Optional[str] = None
    override_message: Optional[str] = None

class AlertLogRead(BaseModel):
    id: int
    farmer_id: int
    block_id: int
    alert_type: str
    risk_level: str
    channel: str
    message: str
    provider_message_id: Optional[str] = None
    status: str
    attempt_number: int = 1
    sent_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AlertLogAuditRead(BaseModel):
    id: int
    farmer_id: int
    masked_phone: Optional[str] = None
    block_id: int
    crop_id: Optional[str] = None
    decision: Optional[str] = None
    severity: Optional[str] = None
    channel: str
    status: str
    provider: Optional[str] = None
    provider_message_id: Optional[str] = None
    fallback_used: bool = False
    fallback_channel: Optional[str] = None
    message: str
    reason: Optional[str] = None
    external_dispatch: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AlertDispatchResponse(BaseModel):
    total_farmers_targeted: int
    dispatches: List[AlertLogRead]
    disclaimer: str = "PROTOTYPE ALERT DISPATCH - ALL NOTIFICATIONS SIMULATED VIA MOCK PROVIDERS"
