from typing import Optional
from pydantic import BaseModel, ConfigDict

class BlockBase(BaseModel):
    name: str
    district: str
    state: str
    latitude: float
    longitude: float
    boundary_reference: Optional[str] = None
    active: bool = True

class BlockCreate(BlockBase):
    pass

class BlockRead(BlockBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
