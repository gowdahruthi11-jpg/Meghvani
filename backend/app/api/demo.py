"""
Meghvani Phase 7A: SIH Demonstration & Verification Endpoints.
Coordinates deterministic end-to-end pipeline execution from farmer profile through validation.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.demo_service import DemoService
from app.auth import verify_officer_api_key

router = APIRouter(
    prefix="/demo",
    tags=["SIH Demonstration (Phase 7A)"],
    dependencies=[Depends(verify_officer_api_key)]
)


class DemoRunRequest(BaseModel):
    probability: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional false-onset probability override for historical replay (default: 0.20 -> SOW_NOW)"
    )
    language: str = Field(
        default="mr",
        description="Target regional language: mr (Marathi), hi (Hindi), en (English)"
    )
    observation_type: str = Field(
        default="RAIN",
        description="Demo farmer observed weather event: RAIN, DRY, or HEAVY_RAIN"
    )


@router.post("/run", status_code=status.HTTP_200_OK)
def run_sih_demo(
    payload: Optional[DemoRunRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Executes the unbroken 10-stage SIH demonstration pipeline:
    1. Farmer profile & consent verification
    2. Historical forecast replay (source='DEMO_REPLAY')
    3. Prototype decision engine (SOW_NOW / WAIT)
    4. Validated agronomic rule lookup (ICAR/PDKV)
    5. Vernacular Marathi message generation
    6. Multi-channel alert routing & mock dispatch
    7. Alert audit logging
    8. Qualitative farmer observation submission
    9. Analytical observation validation against reference rainfall
    10. Officer audit trail assembly
    """
    prob = payload.probability if payload else None
    lang = payload.language if payload else "mr"
    obs_type = payload.observation_type if payload else "RAIN"

    result = DemoService.run_demo_pipeline(
        db=db,
        probability_override=prob,
        language=lang,
        observation_type=obs_type
    )
    return result


@router.get("/status", status_code=status.HTTP_200_OK)
def get_sih_demo_status(db: Session = Depends(get_db)):
    """
    Returns current demonstration status indicators for SIH evaluation.
    """
    return DemoService.get_demo_status(db)


@router.post("/reset", status_code=status.HTTP_200_OK)
def reset_sih_demo(db: Session = Depends(get_db)):
    """
    Idempotently cleans up demo observation and alert records.
    DEMO ONLY: Does not affect operational farmer records.
    """
    return DemoService.reset_demo_data(db)
