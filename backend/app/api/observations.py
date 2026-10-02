from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.farmer_observation import FarmerObservation
from app.models.farmer import Farmer
from app.models.block import Block
from app.schemas.observation import FarmerObservationCreate, FarmerObservationRead

router = APIRouter(prefix="/observations", tags=["Farmer Observations"])

@router.post("", response_model=FarmerObservationRead, status_code=status.HTTP_201_CREATED)
def submit_observation(obs_in: FarmerObservationCreate, db: Session = Depends(get_db)):
    """
    Submits crowd ground-truth feedback (RAIN, DRY, HEAVY_RAIN).
    CRITICAL POLICY: Does NOT trigger automated ML model retraining.
    Stored for validation, bias detection, and later calibration research.
    """
    # Validate farmer exists
    farmer = db.query(Farmer).filter(Farmer.id == obs_in.farmer_id).first()
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID {obs_in.farmer_id} does not exist."
        )

    # Validate block exists
    block = db.query(Block).filter(Block.id == obs_in.block_id).first()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block with ID {obs_in.block_id} does not exist."
        )

    obs = FarmerObservation(
        farmer_id=obs_in.farmer_id,
        block_id=obs_in.block_id,
        observation_date=obs_in.observation_date,
        observation_type=obs_in.observation_type,
        value=obs_in.value,
        source=obs_in.source or "FARMER"
    )
    db.add(obs)
    db.commit()
    db.refresh(obs)
    return obs

@router.get("", response_model=List[FarmerObservationRead])
def list_all_observations(limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieve recent crowd observations for the officer dashboard.
    """
    return (
        db.query(FarmerObservation)
        .order_by(FarmerObservation.created_at.desc())
        .limit(limit)
        .all()
    )

@router.get("/{block_id}", response_model=List[FarmerObservationRead])
def list_observations_by_block(block_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieve ground-truth crowd observations recorded in a specific block.
    """
    return (
        db.query(FarmerObservation)
        .filter(FarmerObservation.block_id == block_id)
        .order_by(FarmerObservation.observation_date.desc())
        .limit(limit)
        .all()
    )
