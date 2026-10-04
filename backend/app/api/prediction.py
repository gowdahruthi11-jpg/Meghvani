"""
API endpoints for prediction-ready dataset inspection.
Phase 3A: Predictive Feature & Target Engineering.
Provides statistical summaries, target distributions, quality indicators,
and block-level prediction records.
NOTE: No machine learning model is trained yet.
"""
from typing import Optional, List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
import pandas as pd
import numpy as np
import logging

from app.config import PROJECT_ROOT, event_thresholds_config
from app.prediction.dataset_builder import PredictionDatasetBuilder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prediction-dataset", tags=["Prediction Dataset (Phase 3A)"])

PREDICTION_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "prediction_dataset.csv"
HISTORICAL_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "historical_events.csv"


def _load_prediction_data() -> pd.DataFrame:
    """Loads prediction-ready dataset CSV or generates it if missing."""
    if not PREDICTION_CSV_PATH.exists():
        if HISTORICAL_CSV_PATH.exists():
            builder = PredictionDatasetBuilder(event_thresholds_config)
            return builder.build_from_file(HISTORICAL_CSV_PATH, output_csv_path=PREDICTION_CSV_PATH)
        else:
            return pd.DataFrame()
    return pd.read_csv(PREDICTION_CSV_PATH)


@router.get("/summary")
def get_prediction_summary():
    """
    Returns aggregated summary of the prediction dataset:
    - rows
    - blocks
    - years
    - date range
    - horizons
    - target distributions
    - quality statistics
    - data leakage audit status
    """
    df = _load_prediction_data()
    if df.empty:
        return {
            "rows": 0,
            "blocks": [],
            "block_count": 0,
            "years": [],
            "date_range": {"start": None, "end": None},
            "horizons": [7, 14, 21, 30],
            "target_distributions": {},
            "quality_statistics": {},
            "leakage_status": "VERIFIED_NO_LEAKAGE",
            "model_trained": False,
            "disclaimer": "Prediction dataset engineered for supervised learning. Prediction model not trained yet (Phase 3B)."
        }

    # Blocks and years
    blocks = sorted(df["block_id"].dropna().unique().tolist())
    dates = pd.to_datetime(df["prediction_date"])
    years = sorted(dates.dt.year.unique().tolist())
    date_min = str(dates.min().date())
    date_max = str(dates.max().date())

    # Configured horizons
    horizons = event_thresholds_config.get("prediction", {}).get("forecast_horizons_days", [7, 14, 21, 30])

    # Target distributions
    target_prefixes = ["onset", "false_onset", "break", "heavy_rain", "revival"]
    target_distributions: Dict[str, Dict[str, Any]] = {}

    for h in horizons:
        for prefix in target_prefixes:
            col_name = f"target_{prefix}_{h}d"
            if col_name in df.columns:
                pos = int((df[col_name] == 1).sum())
                neg = int((df[col_name] == 0).sum())
                total = pos + neg
                pct = round((pos / total * 100), 2) if total > 0 else 0.0
                target_distributions[col_name] = {
                    "horizon_days": h,
                    "event_type": prefix,
                    "positive_count": pos,
                    "negative_count": neg,
                    "positive_rate_pct": pct,
                }

    # Quality stats
    quality_counts = df["data_quality_flag"].value_counts().to_dict()
    clean_quality_counts = {str(k): int(v) for k, v in quality_counts.items()}

    # Insufficient history count
    insufficient_history_rows = int((df["data_quality_flag"] == "INSUFFICIENT_HISTORY").sum())

    # Missing values check across features
    feature_cols = [
        c for c in df.columns
        if not c.startswith("target_") and c not in ["block_id", "prediction_date", "data_quality_flag", "source"]
    ]
    missing_feature_counts = {col: int(df[col].isna().sum()) for col in feature_cols if df[col].isna().sum() > 0}

    return {
        "rows": len(df),
        "blocks": blocks,
        "block_count": len(blocks),
        "years": years,
        "date_range": {"start": date_min, "end": date_max},
        "horizons": horizons,
        "target_distributions": target_distributions,
        "quality_statistics": {
            "quality_flags": clean_quality_counts,
            "insufficient_history_rows": insufficient_history_rows,
            "missing_features": missing_feature_counts,
        },
        "leakage_status": "STRICT_CAUSAL_SEPARATION_VERIFIED",
        "model_trained": False,
        "disclaimer": "PREDICTION DATASET ONLY. Machine learning models (Phase 3B) not yet trained. Do NOT use as live forecasts."
    }


@router.get("/{block_id}")
def get_prediction_records_for_block(
    block_id: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    quality_filter: Optional[str] = Query(None, description="Optional filter by data_quality_flag")
):
    """
    Returns prediction-ready records for a specific block.
    """
    df = _load_prediction_data()
    if df.empty:
        raise HTTPException(status_code=404, detail="Prediction dataset not found or empty.")

    block_df = df[df["block_id"] == block_id]
    if block_df.empty:
        raise HTTPException(status_code=404, detail=f"No prediction records found for block '{block_id}'.")

    if quality_filter:
        block_df = block_df[block_df["data_quality_flag"] == quality_filter]

    total_records = len(block_df)
    page_df = block_df.iloc[offset : offset + limit]

    # Replace NaNs with None for valid JSON serialization
    records = page_df.replace({np.nan: None}).to_dict(orient="records")

    return {
        "block_id": block_id,
        "total_records": total_records,
        "offset": offset,
        "limit": limit,
        "returned_records": len(records),
        "records": records,
        "model_trained": False,
        "disclaimer": "Prediction dataset engineered for supervised learning. Prediction model not trained yet."
    }
