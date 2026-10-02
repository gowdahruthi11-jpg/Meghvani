# Meghvani Machine Learning Architecture (Phases 3–5)

## Overview
This directory houses the future machine learning infrastructure for block-scale monsoon onset and break prediction. 

**IMPORTANT**: In **Phase 1: Production-Ready Foundation**, actual ML models are intentionally **NOT IMPLEMENTED**. This architecture establishes the data interfaces, probabilistic forecast output contract, and feature layout so subsequent modeling phases can plug in directly.

## Directory Structure
- `models/`: Serialized model binaries (`.joblib`, `.pkl`) and metadata artifacts (gitignored).
- `features/`: Feature engineering pipelines (e.g. cumulative rainfall anomaly, OLR, SST indices, Madden-Julian Oscillation, soil moisture change).
- `training/`: Training scripts and cross-validation workflows across historical monsoon seasons.
- `evaluation/`: Probabilistic scoring (Brier Score, Reliability Curves, ROC-AUC) and calibration modules (Isotonic Regression, Platt Scaling).

## Forecast Output Contract
All future predictive models in Phase 4 must output data adhering to the Pydantic schema: `ForecastOutput` (`backend/app/schemas/weather.py`):
```python
class ForecastOutput(BaseModel):
    block_id: int
    forecast_date: date
    horizon_days: int # 7, 14, 28 days
    prob_onset: Optional[float]
    prob_false_onset: Optional[float]
    prob_break: Optional[float]
    prob_revival: Optional[float]
    prob_heavy_rain: Optional[float]
    expected_break_duration: Optional[int]
    rainfall_anomaly_class: Optional[str]
    confidence: Optional[float]
    data_availability: Optional[str]
    model_version: Optional[str]
    is_live_prediction: bool
    disclaimer: str
```
