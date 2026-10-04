from datetime import date, datetime
from typing import Optional, Literal, Union, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

ObservationType = Literal["RAIN", "DRY", "HEAVY_RAIN"]

class FarmerObservationCreate(BaseModel):
    farmer_id: int
    observation_type: str = Field(..., description="Must be RAIN, DRY, or HEAVY_RAIN")
    observation_date: date
    observation_time: Optional[str] = Field(default=None, description="Optional time e.g. 18:30")
    block_id: Optional[int] = Field(default=None, description="Block ID; inferred from farmer if omitted")
    village_id: Optional[int] = Field(default=None, description="Village ID; inferred from farmer if omitted")
    crop_id: Optional[Union[str, int]] = Field(default=None, description="Crop name or ID")
    notes: Optional[str] = Field(default=None, max_length=500, description="Short qualitative note")
    value: Optional[float] = Field(default=None, description="Optional rain gauge reading in mm")
    source: str = "FARMER"

class FarmerObservationRead(BaseModel):
    id: Optional[int] = None
    observation_id: Optional[int] = None
    farmer_id: Optional[int] = None
    block_id: Optional[int] = None
    village_id: Optional[int] = None
    observation_date: Optional[date] = None
    observation_time: Optional[str] = None
    observation_type: Optional[str] = None
    value: Optional[float] = None
    crop_id: Optional[str] = None
    notes: Optional[str] = None
    source: str = "FARMER"
    status: str = "RECORDED"
    validation_status: Optional[str] = None
    reference_rainfall_mm: Optional[float] = None
    comparison_notes: Optional[str] = None
    reason: Optional[str] = None
    is_operational: bool = False
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class FarmerObservationHistoryItem(BaseModel):
    id: int
    observation_id: int
    farmer_id: int
    masked_phone: Optional[str] = None
    block_id: int
    block_name: Optional[str] = None
    village_id: Optional[int] = None
    village_name: Optional[str] = None
    crop_id: Optional[str] = None
    observation_date: date
    observation_time: Optional[str] = None
    observation_type: str
    source: str = "FARMER"
    validation_status: Optional[str] = "PENDING_REVIEW"
    reference_rainfall_mm: Optional[float] = None
    comparison_notes: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ObservationSummaryResponse(BaseModel):
    total_observations: int
    event_distribution: Dict[str, int]
    validation_distribution: Dict[str, int]
    reference_comparisons_count: int
    agreement_rate: Optional[float] = None
    agreement_rate_pct: Optional[float] = None
    metric_description: str
    disclaimer: str
    is_operational: bool = False
