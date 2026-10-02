from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.farmer_service import FarmerService
from app.schemas.farmer import FarmerCreate, FarmerRead

router = APIRouter(prefix="/farmers", tags=["Farmers"])

@router.post("", response_model=FarmerRead, status_code=status.HTTP_201_CREATED)
def create_farmer(farmer_in: FarmerCreate, db: Session = Depends(get_db)):
    """
    Direct farmer registration with explicit consent validation.
    Enforces privacy by storing consent timestamp and preventing duplicate phones.
    """
    farmer = FarmerService.create_farmer(db, farmer_in)
    return FarmerRead.from_orm_masked(farmer)

@router.get("", response_model=List[FarmerRead])
def list_farmers(limit: int = 100, active_only: bool = True, db: Session = Depends(get_db)):
    """
    List farmers for dashboard reporting. Phone numbers are strictly masked for privacy.
    """
    farmers = FarmerService.get_all_farmers(db, limit=limit, active_only=active_only)
    return [FarmerRead.from_orm_masked(f) for f in farmers]

@router.get("/{farmer_id}", response_model=FarmerRead)
def get_farmer_by_id(farmer_id: int, db: Session = Depends(get_db)):
    """
    Retrieve single farmer profile with masked phone number.
    """
    farmer = FarmerService.get_farmer_by_id(db, farmer_id)
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID {farmer_id} not found."
        )
    return FarmerRead.from_orm_masked(farmer)

@router.get("/by-phone/{phone_number}", response_model=FarmerRead)
def get_farmer_by_phone(phone_number: str, db: Session = Depends(get_db)):
    """
    Check if a farmer is registered using their phone number.
    Returns masked profile for privacy compliance.
    """
    farmer = FarmerService.get_farmer_by_phone(db, phone_number)
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No registered farmer found for phone number {phone_number}."
        )
    return FarmerRead.from_orm_masked(farmer)
