from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.crop import Crop
from app.schemas.crop import CropRead

router = APIRouter(prefix="/crops", tags=["Crops"])

@router.get("", response_model=List[CropRead])
def list_crops(active_only: bool = True, db: Session = Depends(get_db)):
    """
    Retrieve demo Kharif crops catalogue.
    Crop traits are demo entries to be verified with ICAR/KVK guidance.
    """
    query = db.query(Crop)
    if active_only:
        query = query.filter(Crop.active == True)
    return query.all()
