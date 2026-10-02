from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.location_service import LocationService
from app.schemas.block import BlockRead

router = APIRouter(prefix="/blocks", tags=["Blocks"])

@router.get("", response_model=List[BlockRead])
def list_blocks(active_only: bool = True, db: Session = Depends(get_db)):
    """
    Retrieve all operational forecast blocks.
    The Block is the PRIMARY prediction unit in Meghvani.
    """
    return LocationService.get_all_blocks(db, active_only=active_only)

@router.get("/{block_id}", response_model=BlockRead)
def get_block(block_id: int, db: Session = Depends(get_db)):
    """
    Retrieve detailed block metadata and coordinates.
    """
    block = LocationService.get_block_by_id(db, block_id)
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block with ID {block_id} not found."
        )
    return block
