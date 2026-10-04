from datetime import date, timedelta
from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.database import get_db
from app.models.farmer_observation import FarmerObservation
from app.models.farmer import Farmer
from app.models.block import Block
from app.models.village import Village
from app.models.crop import Crop
from app.schemas.observation import (
    FarmerObservationCreate,
    FarmerObservationRead,
    FarmerObservationHistoryItem,
    ObservationSummaryResponse
)
from app.observations.validation import ObservationValidator

router = APIRouter(prefix="/observations", tags=["Farmer Observations"])

VALID_OBSERVATION_TYPES = {"RAIN", "DRY", "HEAVY_RAIN"}

def mask_phone_number(phone: Optional[str]) -> Optional[str]:
    """Masks phone number to protect privacy (e.g. ******1234)."""
    if not phone:
        return None
    cleaned = "".join(filter(str.isdigit, str(phone)))
    if len(cleaned) >= 4:
        return "******" + cleaned[-4:]
    return "******"

def validate_crop(db: Session, crop_identifier: Optional[Union[str, int]]) -> Optional[str]:
    """
    Validates crop existence against database or canonical agronomic crop names.
    Returns normalized crop_id / name string, or raises HTTPException 400.
    """
    if crop_identifier is None:
        return None

    # Check if integer ID
    if isinstance(crop_identifier, int) or (isinstance(crop_identifier, str) and crop_identifier.isdigit()):
        cid = int(crop_identifier)
        crop_record = db.query(Crop).filter(Crop.id == cid).first()
        if crop_record:
            return crop_record.name.lower()

    # Check if string name
    c_str = str(crop_identifier).strip().lower()
    crop_record = db.query(Crop).filter(Crop.name.ilike(f"%{c_str}%")).first()
    if crop_record:
        return crop_record.name.lower()

    canonical_crops = {
        "soybean", "cotton", "pigeonpea", "tur", "maize", "paddy", "rice",
        "moong", "urad", "bajra", "wheat", "gram", "sorghum", "jowar"
    }
    if c_str in canonical_crops:
        return c_str

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid crop '{crop_identifier}'. Must be a registered agronomic crop."
    )

@router.post("", response_model=FarmerObservationRead, status_code=status.HTTP_201_CREATED)
def submit_observation(
    obs_in: FarmerObservationCreate,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Submits crowd ground-truth feedback (RAIN, DRY, HEAVY_RAIN).
    CRITICAL POLICY:
    - Does NOT trigger automated ML model retraining or recalibration.
    - Does NOT dispatch external alerts or contact communication providers.
    - Stored for analytical validation and bias monitoring.
    """
    # 1. Validate farmer exists
    farmer = db.query(Farmer).filter(Farmer.id == obs_in.farmer_id).first()
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID {obs_in.farmer_id} does not exist."
        )

    # 2. Consent and active farmer gate
    if not farmer.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="OBSERVATION_NOT_AUTHORIZED"
        )

    # 3. Validate observation type
    obs_type = str(obs_in.observation_type).upper().strip()
    if obs_type not in VALID_OBSERVATION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid observation type '{obs_in.observation_type}'. Must be one of: {sorted(list(VALID_OBSERVATION_TYPES))}."
        )

    # 4. Validate observation date
    today = date.today()
    if obs_in.observation_date > today + timedelta(days=1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Observation date {obs_in.observation_date} cannot be in the future."
        )

    # 5. Validate crop if supplied
    normalized_crop = validate_crop(db, obs_in.crop_id) if obs_in.crop_id is not None else None

    # 6. Resolve block and village
    block_id = obs_in.block_id or farmer.block_id
    village_id = obs_in.village_id or farmer.village_id

    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block with ID {block_id} does not exist."
        )

    # 7. Duplicate Observation Protection
    existing_duplicate = (
        db.query(FarmerObservation)
        .filter(
            FarmerObservation.farmer_id == farmer.id,
            FarmerObservation.observation_date == obs_in.observation_date,
            FarmerObservation.observation_type == obs_type
        )
        .first()
    )

    if existing_duplicate:
        # Return suppressed duplicate
        response.status_code = status.HTTP_200_OK
        return FarmerObservationRead(
            id=existing_duplicate.id,
            observation_id=existing_duplicate.id,
            farmer_id=existing_duplicate.farmer_id,
            block_id=existing_duplicate.block_id,
            village_id=existing_duplicate.village_id,
            observation_date=existing_duplicate.observation_date,
            observation_time=existing_duplicate.observation_time,
            observation_type=existing_duplicate.observation_type,
            value=existing_duplicate.value,
            crop_id=existing_duplicate.crop_id,
            notes=existing_duplicate.notes,
            source="FARMER",
            status="DUPLICATE_OBSERVATION",
            validation_status=existing_duplicate.validation_status,
            reference_rainfall_mm=existing_duplicate.reference_rainfall_mm,
            comparison_notes=existing_duplicate.comparison_notes,
            reason="Duplicate observation suppressed for the same date and type",
            is_operational=False,
            created_at=existing_duplicate.created_at
        )

    # 8. Store observation
    obs = FarmerObservation(
        farmer_id=farmer.id,
        block_id=block_id,
        village_id=village_id,
        observation_date=obs_in.observation_date,
        observation_time=obs_in.observation_time,
        observation_type=obs_type,
        value=obs_in.value,
        crop_id=normalized_crop,
        notes=obs_in.notes[:500] if obs_in.notes else None,
        source="FARMER",
        validation_status="PENDING_REVIEW"
    )
    db.add(obs)
    db.flush()

    # 9. Perform comparison against reference weather observation
    ObservationValidator.validate_against_reference(db, obs)

    db.commit()
    db.refresh(obs)

    return FarmerObservationRead(
        id=obs.id,
        observation_id=obs.id,
        farmer_id=obs.farmer_id,
        block_id=obs.block_id,
        village_id=obs.village_id,
        observation_date=obs.observation_date,
        observation_time=obs.observation_time,
        observation_type=obs.observation_type,
        value=obs.value,
        crop_id=obs.crop_id,
        notes=obs.notes,
        source="FARMER",
        status="RECORDED",
        validation_status=obs.validation_status,
        reference_rainfall_mm=obs.reference_rainfall_mm,
        comparison_notes=obs.comparison_notes,
        reason="Observation successfully recorded and validated against reference",
        is_operational=False,
        created_at=obs.created_at
    )

@router.get("/summary", response_model=ObservationSummaryResponse)
def get_observations_summary(
    block_id: Optional[int] = Query(None),
    village_id: Optional[int] = Query(None),
    crop_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Returns aggregate research and validation metrics across blocks/villages.
    """
    summary = ObservationValidator.compute_summary(
        db=db,
        block_id=block_id,
        village_id=village_id,
        crop_id=crop_id,
        start_date=start_date,
        end_date=end_date
    )
    return summary

@router.get("/history", response_model=List[FarmerObservationHistoryItem])
def get_observations_history(
    farmer_id: Optional[int] = Query(None),
    block_id: Optional[int] = Query(None),
    village_id: Optional[int] = Query(None),
    observation_type: Optional[str] = Query(None),
    validation_status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Retrieves filtered observation history for research and officer audit.
    Phone numbers are masked (******1234) and PINs are strictly omitted.
    """
    query = (
        db.query(FarmerObservation, Farmer, Block, Village)
        .join(Farmer, FarmerObservation.farmer_id == Farmer.id)
        .join(Block, FarmerObservation.block_id == Block.id)
        .outerjoin(Village, FarmerObservation.village_id == Village.id)
    )

    if farmer_id is not None:
        query = query.filter(FarmerObservation.farmer_id == farmer_id)
    if block_id is not None:
        query = query.filter(FarmerObservation.block_id == block_id)
    if village_id is not None:
        query = query.filter(FarmerObservation.village_id == village_id)
    if observation_type is not None:
        query = query.filter(FarmerObservation.observation_type == observation_type.upper().strip())
    if validation_status is not None:
        query = query.filter(FarmerObservation.validation_status == validation_status)
    if start_date is not None:
        query = query.filter(FarmerObservation.observation_date >= start_date)
    if end_date is not None:
        query = query.filter(FarmerObservation.observation_date <= end_date)

    results = query.order_by(desc(FarmerObservation.created_at)).limit(limit).all()

    items = []
    for obs, farmer, block, village in results:
        items.append(
            FarmerObservationHistoryItem(
                id=obs.id,
                observation_id=obs.id,
                farmer_id=obs.farmer_id,
                masked_phone=mask_phone_number(farmer.phone_number),
                block_id=obs.block_id,
                block_name=block.name if block else None,
                village_id=obs.village_id,
                village_name=village.name if village else None,
                crop_id=obs.crop_id,
                observation_date=obs.observation_date,
                observation_time=obs.observation_time,
                observation_type=obs.observation_type,
                source=obs.source or "FARMER",
                validation_status=obs.validation_status or "PENDING_REVIEW",
                reference_rainfall_mm=obs.reference_rainfall_mm,
                comparison_notes=obs.comparison_notes,
                notes=obs.notes,
                created_at=obs.created_at
            )
        )
    return items

@router.get("", response_model=List[FarmerObservationRead])
def list_all_observations(limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieve recent crowd observations for backward-compatible views.
    """
    records = (
        db.query(FarmerObservation)
        .order_by(FarmerObservation.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        FarmerObservationRead(
            id=r.id,
            observation_id=r.id,
            farmer_id=r.farmer_id,
            block_id=r.block_id,
            village_id=r.village_id,
            observation_date=r.observation_date,
            observation_time=r.observation_time,
            observation_type=r.observation_type,
            value=r.value,
            crop_id=r.crop_id,
            notes=r.notes,
            source=r.source or "FARMER",
            status="RECORDED",
            validation_status=r.validation_status,
            reference_rainfall_mm=r.reference_rainfall_mm,
            comparison_notes=r.comparison_notes,
            is_operational=False,
            created_at=r.created_at
        )
        for r in records
    ]

@router.get("/{block_id}", response_model=List[FarmerObservationRead])
def list_observations_by_block(block_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieve ground-truth crowd observations recorded in a specific block.
    """
    records = (
        db.query(FarmerObservation)
        .filter(FarmerObservation.block_id == block_id)
        .order_by(FarmerObservation.observation_date.desc())
        .limit(limit)
        .all()
    )
    return [
        FarmerObservationRead(
            id=r.id,
            observation_id=r.id,
            farmer_id=r.farmer_id,
            block_id=r.block_id,
            village_id=r.village_id,
            observation_date=r.observation_date,
            observation_time=r.observation_time,
            observation_type=r.observation_type,
            value=r.value,
            crop_id=r.crop_id,
            notes=r.notes,
            source=r.source or "FARMER",
            status="RECORDED",
            validation_status=r.validation_status,
            reference_rainfall_mm=r.reference_rainfall_mm,
            comparison_notes=r.comparison_notes,
            is_operational=False,
            created_at=r.created_at
        )
        for r in records
    ]
