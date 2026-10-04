"""
Target engineering module for Meghvani Phase 3A.
Constructs forward-looking supervised learning target labels across configurable prediction horizons.

CRITICAL DATA LEAKAGE RULE:
Targets strictly evaluate observations occurring AFTER prediction date T (i.e. T + 1 to T + horizon_days).
Prediction date T is never included in the future target window.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

DEFAULT_HORIZONS = [7, 14, 21, 30]


def _create_single_block_future_target(
    df: pd.DataFrame,
    event_indicator_col: str,
    horizon_days: int,
    date_col: str = "date"
) -> pd.Series:
    """
    Constructs a future binary event target for a single block dataframe.
    
    Target definition:
    target = 1 if event_indicator_col == 1 for at least one observation in the window:
             (prediction_date < observation_date <= prediction_date + horizon_days)
    target = 0 otherwise.

    Current prediction date T is strictly excluded.
    Operates using calendar date arithmetic to correctly handle any date gaps.
    """
    if df.empty or event_indicator_col not in df.columns:
        return pd.Series(0, index=df.index, dtype=int)

    col = date_col if date_col in df.columns else ("date" if "date" in df.columns else "prediction_date")
    if col not in df.columns:
        return pd.Series(0, index=df.index, dtype=int)

    work_df = df.copy()
    work_df["_dt_temp"] = pd.to_datetime(work_df[col])
    orig_indices = work_df.index
    work_df.sort_values(by="_dt_temp", inplace=True)

    dates = work_df["_dt_temp"].dt.date.values
    events = (work_df[event_indicator_col].fillna(0).astype(int).values == 1)

    n = len(work_df)
    targets = np.zeros(n, dtype=int)

    for i in range(n):
        cur_date = dates[i]
        window_end_date = cur_date + timedelta(days=horizon_days)

        # Search strictly forward from i + 1: cur_date < target_date <= window_end_date
        has_event = False
        for j in range(i + 1, n):
            target_date = dates[j]
            if target_date <= cur_date:
                continue
            if target_date > window_end_date:
                break
            if events[j]:
                has_event = True
                break

        if has_event:
            targets[i] = 1

    sorted_indices = work_df.index
    res = pd.Series(targets, index=sorted_indices, dtype=int)
    return res.reindex(orig_indices)


def create_future_event_target(
    df: pd.DataFrame,
    event_indicator_col: str,
    horizon_days: int,
    date_col: str = "date"
) -> pd.Series:
    """
    Constructs a future binary event target for a dataframe (handling single or multiple blocks).
    
    Target definition:
    target = 1 if event_indicator_col == 1 for at least one observation in the window:
             (prediction_date < observation_date <= prediction_date + horizon_days)
    target = 0 otherwise.

    Current prediction date T is strictly excluded.
    Operates separately by block to ensure zero cross-block target leakage.
    Operates using calendar date arithmetic to correctly handle any date gaps.
    """
    if df.empty or event_indicator_col not in df.columns:
        return pd.Series(0, index=df.index, dtype=int)

    if "block_id" in df.columns and df["block_id"].nunique() > 1:
        res = pd.Series(0, index=df.index, dtype=int)
        for block_id, grp in df.groupby("block_id"):
            blk_targets = _create_single_block_future_target(
                grp, event_indicator_col, horizon_days, date_col=date_col
            )
            res.loc[grp.index] = blk_targets
        return res

    return _create_single_block_future_target(
        df, event_indicator_col, horizon_days, date_col=date_col
    )


def create_all_future_targets(
    df: pd.DataFrame,
    horizons: Optional[List[int]] = None,
    config: Optional[Any] = None
) -> pd.DataFrame:
    """
    Computes future target labels across all configured horizons for:
    - onset (primary onset triggers)
    - false_onset
    - break (break episode starts)
    - heavy_rain
    - revival

    Evaluated independently per block_id.
    """
    if horizons is None:
        horizons = DEFAULT_HORIZONS

    work_df = df.copy()
    date_col = "prediction_date" if "prediction_date" in work_df.columns else "date"

    # 1. Break episode start indicator:
    # Target break must represent a break episode STARTING within the future window,
    # not every individual dry day of an ongoing break.
    if "break_start" in work_df.columns and date_col in work_df.columns:
        has_break = (work_df["break_event"] == 1)
        is_start = (work_df[date_col].astype(str) == work_df["break_start"].astype(str))
        work_df["break_episode_start"] = (has_break & is_start).astype(int)
    else:
        if "block_id" in work_df.columns:
            work_df["break_episode_start"] = (
                (work_df["break_event"] == 1) & 
                (work_df.groupby("block_id")["break_event"].shift(1, fill_value=0) == 0)
            ).astype(int)
        else:
            work_df["break_episode_start"] = (
                (work_df["break_event"] == 1) & 
                (work_df["break_event"].shift(1, fill_value=0) == 0)
            ).astype(int)

    target_specs = [
        ("onset", "onset_trigger"),
        ("false_onset", "false_onset"),
        ("break", "break_episode_start"),
        ("heavy_rain", "heavy_rain_event"),
        ("revival", "revival_event"),
    ]

    for prefix, col in target_specs:
        if col not in work_df.columns:
            for h in horizons:
                work_df[f"target_{prefix}_{h}d"] = 0
            continue

        for h in horizons:
            target_col = f"target_{prefix}_{h}d"
            work_df[target_col] = create_future_event_target(
                work_df, col, h, date_col=date_col
            )

    work_df.drop(columns=["break_episode_start"], inplace=True, errors="ignore")
    return work_df

