from typing import Optional
from pydantic import BaseModel, ConfigDict

class VillageBase(BaseModel):
    name: str
    district: str
    state: str
    block_id: int
    pin_code: str
    latitude: float
    longitude: float
    boundary_reference: Optional[str] = None
    active: bool = True

class VillageCreate(VillageBase):
    pass

class VillageRead(VillageBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
