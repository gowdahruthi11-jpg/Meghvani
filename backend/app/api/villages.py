from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.location_service import LocationService
from app.schemas.village import VillageRead

router = APIRouter(prefix="/villages", tags=["Villages"])

@router.get("", response_model=List[VillageRead])
def list_villages(active_only: bool = True, db: Session = Depends(get_db)):
    """
    Retrieve all registered villages.
    Villages are used for farmer targeting and local localization.
    """
    return LocationService.get_all_villages(db, active_only=active_only)

@router.get("/by-pin/{pin_code}", response_model=List[VillageRead])
def get_villages_by_pin(pin_code: str, db: Session = Depends(get_db)):
    """
    Lookup villages mapped to a 6-digit postal PIN code.
    Enables automatic Village -> Block derivation during farmer registration.
    """
    clean_pin = pin_code.strip()
    if not clean_pin.isdigit() or len(clean_pin) != 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PIN code must be exactly 6 numeric digits."
        )

    villages = LocationService.get_villages_by_pin(db, clean_pin)
    return villages
