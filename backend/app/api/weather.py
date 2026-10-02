from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.block import Block
from app.models.crop import Crop
from app.services.weather_service import WeatherService
from app.services.advisory_service import AdvisoryService
from app.schemas.weather import WeatherObservationRead, ForecastOutput

router = APIRouter(prefix="/weather", tags=["Weather & Forecasting"])

@router.get("/{block_id}", response_model=List[WeatherObservationRead])
def get_weather_for_block(
    block_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve block-scale daily weather observations.
    All data returned in Phase 1 is clearly marked source: DEMO_DATA.
    """
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block with ID {block_id} not found."
        )

    service = WeatherService()
    observations = service.get_block_weather(db, block_id, start_date, end_date)
    return observations

@router.get("/{block_id}/forecast", response_model=ForecastOutput)
def get_future_forecast_contract(block_id: int, db: Session = Depends(get_db)):
    """
    FUTURE FORECAST OUTPUT CONTRACT ENDPOINT.
    Demonstrates architectural readiness for Phase 4 ML Probabilistic Engine.
    Explicitly states forecast engine is not connected in Phase 1.
    """
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block with ID {block_id} not found."
        )

    return ForecastOutput(
        block_id=block_id,
        forecast_date=date.today(),
        horizon_days=14,
        prob_onset=None,
        prob_false_onset=None,
        prob_break=None,
        prob_revival=None,
        prob_heavy_rain=None,
        expected_break_duration=None,
        rainfall_anomaly_class=None,
        confidence=None,
        data_availability="DEMO_STUB",
        model_version=None,
        is_live_prediction=False,
        disclaimer="FORECAST ENGINE NOT CONNECTED YET. Phase 1 provides structural foundation only."
    )

@router.post("/{block_id}/advisory")
def test_crop_advisory(
    block_id: int,
    crop_id: int = Query(..., description="Crop ID to evaluate"),
    language: str = Query("English", description="Language for advisory message"),
    db: Session = Depends(get_db)
):
    """
    Tests the configurable advisory-rule engine using demo forecast inputs.
    Demonstrates sow/wait/protect decisions from config/advisory_rules.yaml.
    """
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block with ID {block_id} not found."
        )

    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop with ID {crop_id} not found."
        )

    # Demo synthetic forecast for test evaluation
    demo_forecast = ForecastOutput(
        block_id=block_id,
        forecast_date=date.today(),
        horizon_days=14,
        prob_onset=0.82,
        prob_break=0.15,
        prob_false_onset=0.10,
        prob_heavy_rain=0.20,
        is_live_prediction=False
    )

    decision = AdvisoryService.evaluate_forecast(
        forecast=demo_forecast,
        crop_name=crop.name,
        language=language
    )

    return {
        "block_name": block.name,
        "crop_name": crop.name,
        "language": language,
        "advisory": decision.to_dict(),
        "input_demo_forecast": demo_forecast.model_dump(),
        "note": "DEMO ADVISORY RULE EVALUATION"
    }
