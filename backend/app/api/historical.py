"""
Historical rainfall and event detection API endpoints.
Provides inspection endpoints for historical dataset summaries, event queries, block timelines,
and local dataset re-processing.
"""
from typing import Optional, List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
import pandas as pd
import logging

from app.config import PROJECT_ROOT, event_thresholds_config
from app.historical.dataset_builder import HistoricalDatasetBuilder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/historical", tags=["Historical Rainfall & Events"])

DEFAULT_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "historical_events.csv"
RAW_CSV_PATH = PROJECT_ROOT / "data" / "raw" / "rainfall" / "demo_rainfall.csv"

def _load_processed_data() -> pd.DataFrame:
    """Helper to load processed historical CSV or build if missing."""
    if not DEFAULT_CSV_PATH.exists():
        if RAW_CSV_PATH.exists():
            builder = HistoricalDatasetBuilder(event_thresholds_config)
            builder.build_from_source(RAW_CSV_PATH, output_csv_path=DEFAULT_CSV_PATH)
        else:
            return pd.DataFrame()
    return pd.read_csv(DEFAULT_CSV_PATH)


@router.get("/summary")
def get_historical_summary():
    """
    Returns an aggregated statistical summary of processed historical rainfall and detected events.
    """
    df = _load_processed_data()
    if df.empty:
        return {
            "blocks": 0,
            "records": 0,
            "onset_triggers": 0,
            "false_onsets": 0,
            "break_spell_days_count": 0,
            "distinct_break_episodes": 0,
            "break_events": 0,
            "heavy_rain_events": 0,
            "revival_events": 0,
            "date_range": {"start": None, "end": None},
            "disclaimer": "PROTOTYPE EVENT SUMMARY - Heuristic detection criteria, NOT official IMD definitions."
        }

    break_days = int((df["break_event"] == 1).sum())
    break_episodes = int(df["break_episode_id"].dropna().nunique()) if "break_episode_id" in df.columns else (
        int(df.groupby(["block_id", "break_start"]).ngroups) if "break_start" in df.columns else break_days
    )

    return {
        "blocks": int(df["block_id"].dropna().nunique()),
        "records": int(len(df)),
        "onset_triggers": int((df["onset_trigger"] == 1).sum()),
        "false_onsets": int((df["false_onset"] == 1).sum()),
        "break_spell_days_count": break_days,
        "distinct_break_episodes": break_episodes,
        "break_events": break_episodes,
        "heavy_rain_events": int((df["heavy_rain_event"] == 1).sum()),
        "revival_events": int((df["revival_event"] == 1).sum()),
        "date_range": {
            "start": str(df["date"].dropna().min()),
            "end": str(df["date"].dropna().max()),
        },
        "quality_counts": df["data_quality_flag"].value_counts().to_dict(),
        "disclaimer": "PROTOTYPE HISTORICAL METRICS: Engineering heuristic definitions for ML feature generation, not official IMD monsoon criteria."
    }


@router.get("/events")
def get_historical_events(
    block_id: Optional[str] = Query(None, description="Filter by block ID (e.g. BLK001)"),
    event_type: Optional[str] = Query(None, description="Event type: onset, false_onset, break, heavy_rain, revival"),
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    limit: int = Query(200, ge=1, le=1000)
):
    """
    Query detected historical meteorological events with optional filtering.
    """
    df = _load_processed_data()
    if df.empty:
        return []

    # Filter by block_id
    if block_id:
        df = df[df["block_id"].astype(str).str.lower() == block_id.strip().lower()]

    # Filter by date range
    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]

    # Filter by event type
    if event_type:
        etype = event_type.strip().lower()
        if etype == "onset":
            df = df[df["onset_trigger"] == 1]
        elif etype == "false_onset":
            df = df[df["false_onset"] == 1]
        elif etype == "break":
            df = df[df["break_event"] == 1]
        elif etype == "heavy_rain":
            df = df[df["heavy_rain_event"] == 1]
        elif etype == "revival":
            df = df[df["revival_event"] == 1]
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event_type '{event_type}'. Valid options: onset, false_onset, break, heavy_rain, revival"
            )
    else:
        # Default: rows where at least one event occurred
        event_mask = (
            (df["onset_trigger"] == 1) |
            (df["false_onset"] == 1) |
            (df["break_event"] == 1) |
            (df["heavy_rain_event"] == 1) |
            (df["revival_event"] == 1)
        )
        df = df[event_mask]

    records = df.head(limit).fillna("").to_dict(orient="records")
    return records


@router.get("/{block_id}")
def get_block_historical_timeline(
    block_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(365, ge=1, le=1000)
):
    """
    Fetches historical rainfall time series, engineered rolling features, and detected events for a specific block.
    """
    df = _load_processed_data()
    if df.empty:
        raise HTTPException(status_code=404, detail="No historical dataset available.")

    # Match block_id case-insensitively or numeric (1 -> BLK001)
    b_id = block_id.strip().upper()
    block_mask = (df["block_id"].astype(str).str.upper() == b_id)
    if not block_mask.any() and b_id.isdigit():
        padded = f"BLK{int(b_id):03d}"
        block_mask = (df["block_id"].astype(str).str.upper() == padded)

    block_df = df[block_mask].copy()
    if block_df.empty:
        raise HTTPException(status_code=404, detail=f"No historical records found for block '{block_id}'")

    if start_date:
        block_df = block_df[block_df["date"] >= start_date]
    if end_date:
        block_df = block_df[block_df["date"] <= end_date]

    block_df.sort_values(by="date", inplace=True)
    records = block_df.head(limit).fillna("").to_dict(orient="records")

    return {
        "block_id": block_id,
        "count": len(records),
        "records": records,
        "disclaimer": "PROTOTYPE HISTORICAL TIMELINE: Heuristic event detections for engineering testing."
    }


@router.post("/process")
def trigger_historical_data_processing():
    """
    Safely triggers the local historical data ingestion and event detection engine on demo/local raw data.
    """
    if not RAW_CSV_PATH.exists():
        raise HTTPException(status_code=404, detail=f"Raw rainfall data not found at {RAW_CSV_PATH}")

    builder = HistoricalDatasetBuilder(event_thresholds_config)
    result = builder.build_from_source(
        source=RAW_CSV_PATH,
        output_csv_path=DEFAULT_CSV_PATH
    )

    return {
        "status": "SUCCESS",
        "message": "Historical rainfall data successfully validated, features engineered, and events labeled.",
        "summary": result["summary"]
    }
