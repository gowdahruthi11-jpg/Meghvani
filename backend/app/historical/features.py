"""
Rainfall feature engineering module.
Calculates backward-looking rolling features, spell metrics, and intensity classifications.

CRITICAL ML BOUNDARY:
All predictor features generated in this module are strictly backward-looking (history up to current date T).
No future-looking information is used, preventing future data leakage in downstream ML models.
"""
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Intensity classes
INTENSITY_ZERO = "ZERO"
INTENSITY_LIGHT = "LIGHT"
INTENSITY_MODERATE = "MODERATE"
INTENSITY_HEAVY = "HEAVY"


def calculate_dry_spell_days(series: pd.Series, dry_ceiling_mm: float = 2.5) -> pd.Series:
    """
    Reusable dry spell calculation.
    Counts consecutive consecutive days where daily rainfall is below dry_ceiling_mm.
    
    IMPORTANT SCIENTIFIC RULE:
    Missing observations (NaN / null) are strictly NOT counted as dry days.
    If an observation is missing or invalid, the dry spell streak resets.
    """
    dry_streak = []
    current_count = 0

    for val in series:
        if pd.isna(val):
            # Missing observation: do NOT treat as zero, reset streak
            current_count = 0
            dry_streak.append(0)
        elif float(val) < dry_ceiling_mm:
            current_count += 1
            dry_streak.append(current_count)
        else:
            current_count = 0
            dry_streak.append(0)

    return pd.Series(dry_streak, index=series.index)


def calculate_wet_spell_days(series: pd.Series, wet_threshold_mm: float = 2.5) -> pd.Series:
    """
    Reusable wet spell calculation.
    Counts consecutive days where daily rainfall is at or above wet_threshold_mm.
    """
    wet_streak = []
    current_count = 0

    for val in series:
        if pd.isna(val):
            current_count = 0
            wet_streak.append(0)
        elif float(val) >= wet_threshold_mm:
            current_count += 1
            wet_streak.append(current_count)
        else:
            current_count = 0
            wet_streak.append(0)

    return pd.Series(wet_streak, index=series.index)


def classify_rainfall_intensity(
    rainfall_mm: Optional[float],
    thresholds: Optional[Dict[str, Any]] = None
) -> str:
    """
    Classifies daily rainfall into prototype intensity categories.
    Engineering prototype only - NOT official IMD categorization.
    """
    if rainfall_mm is None or pd.isna(rainfall_mm):
        return "UNKNOWN"

    rf = float(rainfall_mm)
    if rf == 0.0:
        return INTENSITY_ZERO
    elif rf <= 7.5:
        return INTENSITY_LIGHT
    elif rf < 64.5:
        return INTENSITY_MODERATE
    else:
        return INTENSITY_HEAVY


class RainfallFeatureEngineer:
    """
    Generates backward-looking rolling rainfall metrics per block.
    """

    def __init__(self, thresholds_config: Optional[Dict[str, Any]] = None):
        self.thresholds_config = thresholds_config or {}
        dry_cfg = self.thresholds_config.get("thresholds", {}).get("dry_spell", {})
        self.dry_ceiling_mm = float(dry_cfg.get("daily_dry_ceiling_mm", 2.5))

    def compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes rolling rainfall aggregates, spell counters, and intensity classes.
        Input dataframe must contain: block_id, date, rainfall_mm.
        """
        if df.empty:
            return df

        work_df = df.copy()

        # Sort strictly by block_id and date
        work_df["date_dt"] = pd.to_datetime(work_df["date"])
        work_df.sort_values(by=["block_id", "date_dt"], inplace=True)

        feature_dfs = []

        # Process each block independently
        for block_id, group in work_df.groupby("block_id", sort=False):
            grp = group.copy()
            rf_series = grp["rainfall_mm"]

            # Backward-looking rolling cumulative sums (min_periods=1)
            # strictly historical: rolling up to current row
            grp["rainfall_1d"] = rf_series.round(1)
            grp["rainfall_3d"] = rf_series.rolling(window=3, min_periods=1).sum().round(1)
            grp["rainfall_5d"] = rf_series.rolling(window=5, min_periods=1).sum().round(1)
            grp["rainfall_7d"] = rf_series.rolling(window=7, min_periods=1).sum().round(1)
            grp["rainfall_14d"] = rf_series.rolling(window=14, min_periods=1).sum().round(1)
            grp["rainfall_30d"] = rf_series.rolling(window=30, min_periods=1).sum().round(1)

            # Spell calculations
            grp["dry_spell_days"] = calculate_dry_spell_days(rf_series, self.dry_ceiling_mm)
            grp["wet_spell_days"] = calculate_wet_spell_days(rf_series, self.dry_ceiling_mm)

            # Rainfall intensity categorization
            grp["rainfall_intensity_class"] = grp["rainfall_mm"].apply(classify_rainfall_intensity)

            # Rainfall anomaly (Prototype boundary: null/None until multi-decade climatology normals integrated)
            grp["rainfall_anomaly"] = None

            feature_dfs.append(grp)

        result_df = pd.concat(feature_dfs, ignore_index=True)
        result_df.drop(columns=["date_dt"], inplace=True)
        result_df.sort_values(by=["block_id", "date"], inplace=True)

        logger.info(f"Engineered rainfall features for {len(result_df)} records across {work_df['block_id'].nunique()} blocks.")
        return result_df
