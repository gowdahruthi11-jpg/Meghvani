from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class AlertSimulationRequest(BaseModel):
    block_id: int
    alert_type: str = "ONSET" # ONSET, FALSE_ONSET, BREAK, HEAVY_RAIN, ROUTINE_ADVISORY
    risk_level: str = "NORMAL" # NORMAL, IMPORTANT, HIGH_RISK
    crop_id: Optional[int] = None
    override_message: Optional[str] = None

class AlertLogRead(BaseModel):
    id: int
    farmer_id: int
    block_id: int
    alert_type: str
    risk_level: str
    channel: str
    message: str
    provider_message_id: Optional[str]
    status: str
    attempt_number: int
    sent_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AlertDispatchResponse(BaseModel):
    total_farmers_targeted: int
    dispatches: List[AlertLogRead]
    disclaimer: str = "PROTOTYPE ALERT DISPATCH - ALL NOTIFICATIONS SIMULATED VIA MOCK PROVIDERS"
