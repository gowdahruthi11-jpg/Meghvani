from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.farmer import Farmer
from app.schemas.farmer import FarmerCreate

class FarmerService:
    @staticmethod
    def get_farmer_by_id(db: Session, farmer_id: int) -> Optional[Farmer]:
        return db.query(Farmer).filter(Farmer.id == farmer_id).first()

    @staticmethod
    def get_farmer_by_phone(db: Session, phone_number: str) -> Optional[Farmer]:
        clean_phone = phone_number.strip()
        return db.query(Farmer).filter(Farmer.phone_number == clean_phone).first()

    @staticmethod
    def get_all_farmers(db: Session, limit: int = 100, active_only: bool = True) -> List[Farmer]:
        query = db.query(Farmer)
        if active_only:
            query = query.filter(Farmer.active == True)
        return query.limit(limit).all()

    @staticmethod
    def get_farmers_by_block(
        db: Session,
        block_id: int,
        crop_id: Optional[int] = None,
        active_only: bool = True
    ) -> List[Farmer]:
        query = db.query(Farmer).filter(Farmer.block_id == block_id)
        if active_only:
            query = query.filter(Farmer.active == True)
        if crop_id:
            query = query.filter(Farmer.crop_id == crop_id)
        return query.all()

    @staticmethod
    def create_farmer(db: Session, farmer_in: FarmerCreate) -> Farmer:
        clean_phone = farmer_in.phone_number.strip()
        existing = db.query(Farmer).filter(Farmer.phone_number == clean_phone).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Farmer with phone number {clean_phone} already registered. Use status or update options."
            )

        if not farmer_in.consent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Explicit farmer consent is required for registration."
            )

        new_farmer = Farmer(
            phone_number=clean_phone,
            preferred_language=farmer_in.preferred_language,
            pin_code=farmer_in.pin_code,
            village_id=farmer_in.village_id,
            block_id=farmer_in.block_id,
            crop_id=farmer_in.crop_id,
            communication_preference=farmer_in.communication_preference,
            consent=True,
            consent_timestamp=datetime.now(timezone.utc),
            active=True
        )
        db.add(new_farmer)
        db.commit()
        db.refresh(new_farmer)
        return new_farmer

    @staticmethod
    def deactivate_farmer(db: Session, farmer_id: int) -> Optional[Farmer]:
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not farmer:
            return None
        farmer.active = False
        db.commit()
        db.refresh(farmer)
        return farmer
