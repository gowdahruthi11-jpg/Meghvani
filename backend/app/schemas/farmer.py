from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

def mask_phone(phone: str) -> str:
    """Masks phone number for privacy preservation in dashboards and logs."""
    if not phone or len(phone) < 6:
        return "****"
    return f"{phone[:3]}****{phone[-4:]}"

class FarmerBase(BaseModel):
    phone_number: str = Field(..., description="E.164 formatted or 10-digit Indian phone number")
    preferred_language: str = "Hindi"
    pin_code: str = Field(..., min_length=6, max_length=6)
    village_id: int
    block_id: int
    crop_id: int
    communication_preference: str = "SMS"
    consent: bool = Field(..., description="Explicit consent is required")

    @field_validator("pin_code")
    @classmethod
    def validate_pin(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError("PIN code must be exactly 6 digits")
        return v

    @field_validator("consent")
    @classmethod
    def validate_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Farmer registration requires explicit consent")
        return v

class FarmerCreate(FarmerBase):
    pass

class FarmerRead(BaseModel):
    id: int
    phone_number_masked: str
    preferred_language: str
    pin_code: str
    village_id: int
    block_id: int
    crop_id: int
    communication_preference: str
    consent: bool
    consent_timestamp: Optional[datetime] = None
    created_at: datetime
    active: bool

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_masked(cls, farmer) -> "FarmerRead":
        return cls(
            id=farmer.id,
            phone_number_masked=mask_phone(farmer.phone_number),
            preferred_language=farmer.preferred_language,
            pin_code=farmer.pin_code,
            village_id=farmer.village_id,
            block_id=farmer.block_id,
            crop_id=farmer.crop_id,
            communication_preference=farmer.communication_preference,
            consent=farmer.consent,
            consent_timestamp=farmer.consent_timestamp,
            created_at=farmer.created_at,
            active=farmer.active,
        )

class FarmerFullRead(FarmerRead):
    phone_number: str
