"""
Meghvani Phase 7B: Multi-Year Scientific Validation API Endpoints.

Provides:
- GET /api/validation/multiyear/summary
- GET /api/validation/multiyear/year/{year}
- GET /api/validation/multiyear/block/{block_id}
- GET /api/validation/multiyear/horizon/{days}
- GET /api/validation/multiyear/events
"""
from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any, Optional
import pandas as pd

from app.ml.multiyear_validation import MultiYearScientificValidator
from app.historical.multiyear_ingestion import HistoricalDataAvailabilityValidator
from app.config import PROJECT_ROOT

router = APIRouter(prefix="/validation/multiyear", tags=["Scientific Validation"])
validator = MultiYearScientificValidator()
availability_validator = HistoricalDataAvailabilityValidator()

EVENT_SUMMARY_CSV = PROJECT_ROOT / "data" / "processed" / "historical" / "multiyear_event_summary.csv"


@router.get("/summary")
def get_validation_summary() -> Dict[str, Any]:
    """
    Returns full multi-year scientific validation summary including data coverage,
    validation status (READY or BLOCKED_PENDING_MULTIYEAR_DATA), horizon evaluation,
    block breakdown, and statistical honesty warnings.
    """
    return validator.generate_full_validation_summary()


@router.get("/year/{year}")
def get_validation_for_year(year: int = Path(..., description="Calendar year, e.g. 2025")) -> Dict[str, Any]:
    """
    Returns validation results for a specific evaluation year under Leave-One-Year-Out.
    """
    summary = validator.generate_full_validation_summary()
    loyo = summary.get("loyo_7d", {})
    year_results = loyo.get("year_wise_results", [])

    matched = [r for r in year_results if r.get("evaluation_year") == year]
    if not matched:
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation results for year {year} not found. Available years: {summary['data_coverage']['available_years_list']}"
        )

    return {
        "evaluation_year": year,
        "validation_status": summary.get("validation_status"),
        "metrics": matched[0],
        "statement": summary.get("statement")
    }


@router.get("/block/{block_id}")
def get_validation_for_block(block_id: str = Path(..., description="Block ID, e.g. BLK001")) -> Dict[str, Any]:
    """
    Returns block-scale validation results. If insufficient data exist, returns INSUFFICIENT_DATA.
    """
    summary = validator.generate_full_validation_summary()
    blocks = summary.get("blocks", {})

    if block_id not in blocks:
        raise HTTPException(
            status_code=404,
            detail=f"Block {block_id} not found in historical coverage. Known blocks: {list(blocks.keys())}"
        )

    return {
        "block_id": block_id,
        "result": blocks[block_id]
    }


@router.get("/horizon/{days}")
def get_validation_for_horizon(days: int = Path(..., description="Forecast horizon in days (7, 14, 21, 30)")) -> Dict[str, Any]:
    """
    Returns validation results stratified by specific forward-looking horizon.
    """
    if days not in [7, 14, 21, 30]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid horizon {days}. Supported horizons: 7, 14, 21, 30 days."
        )

    df = validator.load_dataset()
    res = validator.evaluate_leave_one_year_out(df, horizon_days=days)
    return {
        "horizon_days": days,
        "results": res
    }


@router.get("/events")
def get_multiyear_event_summary() -> Dict[str, Any]:
    """
    Returns the year-by-year and block-by-block event summary table.
    """
    if not EVENT_SUMMARY_CSV.exists():
        return {
            "status": "UNAVAILABLE",
            "message": "Event summary not yet compiled.",
            "records": []
        }

    df = pd.read_csv(EVENT_SUMMARY_CSV)
    records = df.to_dict(orient="records")
    return {
        "status": "AVAILABLE",
        "total_records": len(records),
        "records": records
    }


@router.get("/imd/status")
def get_imd_ingestion_status() -> Dict[str, Any]:
    """
    Returns Phase 7C IMD 0.25° gridded rainfall data ingestion and quality assessment.
    """
    return validator.imd_manager.assess_ingestion_status()


@router.get("/spatial/report")
def get_spatial_mapping_report() -> Dict[str, Any]:
    """
    Returns spatial mapping analysis between 0.25° IMD grid cells and Meghvani blocks.
    Reports whether boundary polygons exist or if BLOCK_GEOMETRY_REQUIRED applies.
    """
    rep = validator.imd_manager.spatial_mapper.get_spatial_mapping_report()
    return rep.to_dict()


@router.get("/gate")
def get_validation_gate_status() -> Dict[str, Any]:
    """
    Returns critical multi-year validation gate status (MULTIYEAR_VALIDATION_READY vs MULTIYEAR_VALIDATION_BLOCKED).
    """
    summary = validator.generate_full_validation_summary()
    return {
        "validation_gate": summary.get("validation_gate", "MULTIYEAR_VALIDATION_BLOCKED"),
        "validation_status": summary.get("validation_status"),
        "statement": summary.get("statement"),
        "imd_status": summary.get("imd_status", {}).get("ingestion_status")
    }


# ============================================================================
# Phase 8A: Probability Calibration & Rolling-Origin Routers
# ============================================================================
from app.ml.rolling_origin import RollingOriginEvaluator

rolling_evaluator = RollingOriginEvaluator()
calibration_router = APIRouter(prefix="/validation/calibration", tags=["Probability Calibration"])
rolling_origin_router = APIRouter(prefix="/validation/rolling-origin", tags=["Rolling Origin Validation"])


@calibration_router.get("/summary")
def get_calibration_summary() -> Dict[str, Any]:
    """
    Returns Phase 8A probability calibration summary comparing raw, calibrated,
    and climatology forecasts under strict rolling-origin evaluation.
    """
    rep = rolling_evaluator.generate_full_report()
    return {
        "status": rep.get("status"),
        "calibration_method": rep.get("primary_calibration_method"),
        "horizons": rep.get("horizons"),
        "blocks": rep.get("blocks"),
        "class_weighting_investigation": rep.get("class_weighting_investigation"),
        "scientific_boundaries": rep.get("scientific_boundaries")
    }


@calibration_router.get("/year/{year}")
def get_calibration_for_year(year: int = Path(..., description="Evaluation year, e.g. 2024")) -> Dict[str, Any]:
    """
    Returns rolling-origin calibration and evaluation metrics for a specific evaluation year.
    """
    rep = rolling_evaluator.evaluate_rolling_origin(rolling_evaluator.load_dataset(), horizon_days=7)
    matched = [yr for yr in rep.get("year_results", []) if yr.get("evaluation_year") == year]
    if not matched:
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation results for year {year} not found. Available years: {rep.get('available_years')}"
        )
    return {
        "evaluation_year": year,
        "horizon_days": 7,
        "metrics": matched[0]
    }


@calibration_router.get("/horizon/{days}")
def get_calibration_for_horizon(days: int = Path(..., description="Forecast horizon in days (7, 14, 21, 30)")) -> Dict[str, Any]:
    """
    Returns rolling-origin calibration results for a specific forward horizon.
    """
    if days not in [7, 14, 21, 30]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid horizon {days}. Supported horizons: 7, 14, 21, 30 days."
        )
    df = rolling_evaluator.load_dataset()
    res = rolling_evaluator.evaluate_rolling_origin(df, horizon_days=days)
    return {
        "horizon_days": days,
        "results": res
    }


@calibration_router.get("/reliability")
def get_calibration_reliability_diagrams() -> Dict[str, Any]:
    """
    Returns 10-bin reliability diagrams comparing raw vs calibrated forecast probabilities.
    """
    df = rolling_evaluator.load_dataset()
    res_7d = rolling_evaluator.evaluate_rolling_origin(df, horizon_days=7)
    agg = res_7d.get("aggregate_metrics", {})
    return {
        "horizon_days": 7,
        "raw_model_reliability": agg.get("variant_a_raw", {}).get("reliability_bins", []),
        "calibrated_model_reliability": agg.get("variant_a_calibrated", {}).get("reliability_bins", []),
        "probability_aligned_reliability": agg.get("variant_b_unweighted", {}).get("reliability_bins", []),
        "ece": {
            "variant_a_raw": agg.get("variant_a_raw", {}).get("ece"),
            "variant_a_calibrated": agg.get("variant_a_calibrated", {}).get("ece"),
            "variant_b_unweighted": agg.get("variant_b_unweighted", {}).get("ece")
        }
    }


@rolling_origin_router.get("/summary")
def get_rolling_origin_summary() -> Dict[str, Any]:
    """
    Returns complete multi-year forward-chaining rolling-origin evaluation report.
    """
    return rolling_evaluator.generate_full_report()


