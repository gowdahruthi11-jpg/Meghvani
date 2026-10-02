from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class WeatherObservationBase(BaseModel):
    block_id: int
    observation_date: date
    rainfall_mm: float = 0.0
    temperature_c: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    soil_moisture: Optional[float] = None
    source: str = "DEMO_DATA"

class WeatherObservationCreate(WeatherObservationBase):
    pass

class WeatherObservationRead(WeatherObservationBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# FUTURE FORECAST OUTPUT CONTRACT (PHASE 1 SPECIFICATION)
# Contract to be fulfilled by Phase 4 ML Probabilistic Engine
# ============================================================
class ForecastOutput(BaseModel):
    """
    Contract for block-level probabilistic monsoon and weather predictions.
    Defined in Phase 1 to guarantee architectural compatibility for Phase 4 ML.
    """
    block_id: int
    forecast_date: date
    horizon_days: int = Field(default=14, description="Forecast horizon in days (e.g., 7, 14, 28)")
    
    # Core probabilistic predictions (0.0 to 1.0)
    prob_onset: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Calibrated probability of monsoon onset trigger")
    prob_false_onset: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Risk of false onset followed by >=7 day dry spell")
    prob_break: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Probability of dry spell / break condition")
    prob_revival: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Probability of monsoon revival following break")
    prob_heavy_rain: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Probability of daily rainfall >= 64.5mm")

    # Associated metrics
    expected_break_duration: Optional[int] = Field(default=None, description="Expected duration of break spell in days")
    rainfall_anomaly_class: Optional[str] = Field(default=None, description="DEFICIENT, NORMAL, EXCESS")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Model calibration confidence score")
    data_availability: Optional[str] = Field(default="DEMO", description="Summary of input observations availability")
    model_version: Optional[str] = Field(default=None, description="Version string of deployed ML model")
    
    is_live_prediction: bool = Field(default=False, description="Explicit flag: Phase 1 engine does not emit live forecasts")
    disclaimer: str = Field(
        default="FORECAST ENGINE NOT CONNECTED YET. Phase 1 provides structural foundation only.",
        description="Clear transparency notice for SIH evaluators"
    )
