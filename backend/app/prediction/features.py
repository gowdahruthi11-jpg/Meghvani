"""
Predictive feature engineering module for Meghvani Phase 3A.
Calculates backward-looking trend, seasonal calendar, and event-recency features.

CRITICAL DATA LEAKAGE PREVENTION:
Every feature engineered in this module uses exclusively information observed on or before prediction date T.
No forward-looking shifts or future observations are accessed.
"""
from datetime import datetime, date
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
import logging

from app.historical.validator import QUALITY_GOOD, QUALITY_INSUFFICIENT_HISTORY

logger = logging.getLogger(__name__)

DEFAULT_MONSOON_MONTHS = [6, 7, 8, 9]
DEFAULT_INSUFFICIENT_HISTORY_DAYS = 30
NO_EVENT_SENTINEL = -1.0


class PredictiveFeatureEngineer:
    """
    Engineers backward-looking predictor variables for ML model inputs.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        pred_cfg = self.config.get("prediction", {})
        self.monsoon_months = pred_cfg.get("monsoon_months", DEFAULT_MONSOON_MONTHS)
        self.min_history_days = pred_cfg.get("insufficient_history_min_days", DEFAULT_INSUFFICIENT_HISTORY_DAYS)

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds trend features, calendar features, and event recency state metrics per block.
        Input dataframe must be sorted chronologically per block and contain:
        block_id, date, rainfall_mm, rainfall_3d, rainfall_5d, rainfall_7d, rainfall_14d, rainfall_30d,
        dry_spell_days, wet_spell_days, onset_trigger, break_event, heavy_rain_event, revival_event.
        """
        if df.empty:
            return df

        work_df = df.copy()
        work_df["date_dt"] = pd.to_datetime(work_df["date"])
        work_df.sort_values(by=["block_id", "date_dt"], inplace=True)

        block_subsets = []

        for block_id, grp in work_df.groupby("block_id", sort=False):
            b_df = grp.copy().reset_index(drop=True)
            dates = pd.to_datetime(b_df["date"]).dt.date.values
            n = len(b_df)

            # 1. Trend Features (Strict backward-looking shifts)
            # rainfall_change_3d: current 3d sum minus 3d sum 3 days ago
            b_df["rainfall_change_3d"] = (b_df["rainfall_3d"] - b_df["rainfall_3d"].shift(3)).round(1)
            # rainfall_change_7d: current 7d sum minus 7d sum 7 days ago
            b_df["rainfall_change_7d"] = (b_df["rainfall_7d"] - b_df["rainfall_7d"].shift(7)).round(1)
            # rainfall_ratio_3d_7d: ratio of short-term to medium-term intensity
            safe_7d = b_df["rainfall_7d"].replace(0, np.nan)
            b_df["rainfall_ratio_3d_7d"] = ((b_df["rainfall_3d"] / (safe_7d + 1e-4)).fillna(0.0)).round(3)

            # 2. Calendar Features (Deterministic date functions)
            b_df["month"] = pd.to_datetime(b_df["date"]).dt.month.astype(int)
            b_df["day_of_year"] = pd.to_datetime(b_df["date"]).dt.dayofyear.astype(int)
            b_df["monsoon_month_flag"] = b_df["month"].apply(
                lambda m: 1 if m in self.monsoon_months else 0
            ).astype(int)

            # 3. Historical Event Recency Features (Strictly on or before current row i)
            days_since_onset = [NO_EVENT_SENTINEL] * n
            days_since_break = [NO_EVENT_SENTINEL] * n
            days_since_heavy = [NO_EVENT_SENTINEL] * n
            days_since_revival = [NO_EVENT_SENTINEL] * n

            last_onset_date: Optional[date] = None
            last_break_date: Optional[date] = None
            last_heavy_date: Optional[date] = None
            last_revival_date: Optional[date] = None

            for i in range(n):
                cur_d = dates[i]

                # Update historical state if event occurs on current row i
                if b_df.loc[i, "onset_trigger"] == 1:
                    last_onset_date = cur_d
                if b_df.loc[i, "break_event"] == 1:
                    last_break_date = cur_d
                if b_df.loc[i, "heavy_rain_event"] == 1:
                    last_heavy_date = cur_d
                if b_df.loc[i, "revival_event"] == 1:
                    last_revival_date = cur_d

                # Compute elapsed days to most recent past/present event
                if last_onset_date is not None:
                    days_since_onset[i] = float((cur_d - last_onset_date).days)
                if last_break_date is not None:
                    days_since_break[i] = float((cur_d - last_break_date).days)
                if last_heavy_date is not None:
                    days_since_heavy[i] = float((cur_d - last_heavy_date).days)
                if last_revival_date is not None:
                    days_since_revival[i] = float((cur_d - last_revival_date).days)

            b_df["days_since_last_onset"] = days_since_onset
            b_df["days_since_last_break"] = days_since_break
            b_df["days_since_last_heavy_rain"] = days_since_heavy
            b_df["days_since_last_revival"] = days_since_revival

            # 4. Data Quality Flag: flag insufficient history (< min_history_days)
            if "data_quality_flag" not in b_df.columns:
                b_df["data_quality_flag"] = QUALITY_GOOD

            # The first min_history_days observations do not have a full 30d window
            for idx in range(min(n, self.min_history_days)):
                if b_df.loc[idx, "data_quality_flag"] == QUALITY_GOOD:
                    b_df.loc[idx, "data_quality_flag"] = QUALITY_INSUFFICIENT_HISTORY

            block_subsets.append(b_df)

        result_df = pd.concat(block_subsets, ignore_index=True)
        result_df.drop(columns=["date_dt"], inplace=True, errors="ignore")
        result_df.sort_values(by=["block_id", "date"], inplace=True)
        return result_df
