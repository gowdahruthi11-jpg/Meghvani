from typing import Optional
from pydantic import BaseModel, ConfigDict

class CropBase(BaseModel):
    name: str
    scientific_name: Optional[str] = None
    season: str = "Kharif"
    water_requirement: str
    duration_category: str
    active: bool = True

class CropCreate(CropBase):
    pass

class CropRead(CropBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
