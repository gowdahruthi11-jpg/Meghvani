from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

ObservationType = Literal["RAIN", "DRY", "HEAVY_RAIN"]

class FarmerObservationCreate(BaseModel):
    farmer_id: int
    block_id: int
    observation_date: date
    observation_type: ObservationType = Field(..., description="Must be RAIN, DRY, or HEAVY_RAIN")
    value: Optional[float] = Field(default=None, description="Optional rain gauge reading in mm if measured")
    source: str = "FARMER"

class FarmerObservationRead(BaseModel):
    id: int
    farmer_id: int
    block_id: int
    observation_date: date
    observation_type: str
    value: Optional[float]
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
