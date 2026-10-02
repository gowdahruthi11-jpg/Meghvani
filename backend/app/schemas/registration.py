from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class RegistrationStartRequest(BaseModel):
    phone_number: str

class RegistrationMessageRequest(BaseModel):
    phone_number: str
    message: str

class MissedCallRequest(BaseModel):
    phone_number: str

class RegistrationSessionRead(BaseModel):
    id: int
    phone_number: str
    current_step: str
    language: Optional[str] = None
    pin_code: Optional[str] = None
    selected_village_id: Optional[int] = None
    selected_block_id: Optional[int] = None
    selected_crop_id: Optional[int] = None
    consent: bool
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class RegistrationMessageResponse(BaseModel):
    reply_message: str
    current_step: str
    is_completed: bool = False
    registered_farmer_id: Optional[int] = None
    note: str = "SIMULATED SMS / CONVERSATIONAL REGISTRATION"
