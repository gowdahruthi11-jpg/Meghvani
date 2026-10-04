"""
Historical event detection engine for Meghvani Phase 2.
Detects prototype onset triggers, false onsets, break spells, heavy rainfall, and revivals.

SCIENTIFIC & REGULATORY BOUNDARY:
All detection criteria implemented here are engineering heuristic approximations for dataset preparation.
They are NOT official India Meteorological Department (IMD) operational meteorological standards.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
import logging

from app.config import event_definitions_config, event_thresholds_config

logger = logging.getLogger(__name__)


class EventDetector:
    """
    Applies configurable thresholds to detect meteorological events from historical rainfall features.
    Reads canonical thresholds from config/event_definitions.yaml by default.
    """

    def __init__(self, thresholds_config: Optional[Dict[str, Any]] = None):
        self.config = thresholds_config if thresholds_config is not None else (event_definitions_config or event_thresholds_config or {})
        thresh = self.config.get("thresholds", {})

        # Onset parameters
        onset_cfg = thresh.get("onset", {})
        self.onset_rainfall_mm = float(onset_cfg.get("onset_rainfall_mm", 20.0))
        self.onset_window_days = int(onset_cfg.get("onset_window_days", 3))
        self.onset_lockout_days = int(onset_cfg.get("onset_lockout_days", 30))

        # False onset parameters
        false_onset_cfg = thresh.get("false_onset", {})
        self.false_onset_dry_spell_days = int(false_onset_cfg.get("false_onset_dry_spell_days", 7))
        self.false_onset_lookahead_days = int(false_onset_cfg.get("false_onset_lookahead_days", 30))

        # Break spell parameters
        break_cfg = thresh.get("break_spell", {})
        self.break_dry_spell_days = int(break_cfg.get("break_dry_spell_days", break_cfg.get("break_dry_days_threshold", 5)))
        self.break_daily_ceiling_mm = float(break_cfg.get("daily_rainfall_ceiling_mm", 2.5))

        # Heavy rain parameters
        heavy_cfg = thresh.get("heavy_rain", {})
        self.heavy_rainfall_mm = float(heavy_cfg.get("heavy_rainfall_mm", heavy_cfg.get("heavy_rain_daily_mm", 64.5)))

        # Revival parameters
        revival_cfg = thresh.get("revival", {})
        self.revival_rainfall_mm = float(revival_cfg.get("revival_rainfall_mm", 15.0))
        self.revival_window_days = int(revival_cfg.get("revival_window_days", 2))

    def detect_events(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Runs full event detection suite across all blocks in the dataset.
        Input dataframe must contain: block_id, date, rainfall_mm, dry_spell_days, rainfall_3d (or rolling features).
        """
        if df.empty:
            return df

        work_df = df.copy()
        work_df["date_dt"] = pd.to_datetime(work_df["date"])
        work_df.sort_values(by=["block_id", "date_dt"], inplace=True)

        labeled_blocks = []

        for block_id, group in work_df.groupby("block_id", sort=False):
            grp = group.copy().reset_index(drop=True)

            # 1. Onset Trigger Detection
            grp = self.detect_onset_trigger(grp)

            # 2. Break Spell Detection
            grp = self.detect_break(grp)

            # 3. False Onset Detection (historical event label using lookahead)
            grp = self.detect_false_onset(grp)

            # 4. Heavy Rain Detection
            grp = self.detect_heavy_rain(grp)

            # 5. Revival Detection
            grp = self.detect_revival(grp)

            labeled_blocks.append(grp)

        result_df = pd.concat(labeled_blocks, ignore_index=True)
        result_df.drop(columns=["date_dt"], inplace=True, errors="ignore")
        result_df.sort_values(by=["block_id", "date"], inplace=True)
        return result_df

    def detect_onset_trigger(self, block_df: pd.DataFrame) -> pd.DataFrame:
        """
        Detects prototype primary onset triggers with configurable lockout debounce.
        Trigger occurs if cumulative rainfall over the configured onset window >= onset_rainfall_mm.
        Subsequent wet days during the lockout period (onset_lockout_days) are suppressed
        to prevent persistent rain from generating duplicate onset triggers.
        """
        df = block_df.copy()
        n = len(df)

        onset_triggers = [0] * n
        onset_dates = [None] * n

        # Window & lockout calculation
        window = self.onset_window_days
        threshold = self.onset_rainfall_mm
        lockout = self.onset_lockout_days

        lockout_until_idx = -1

        for i in range(n):
            if i < lockout_until_idx:
                continue

            start_idx = max(0, i - window + 1)
            window_slice = df.loc[start_idx:i, "rainfall_mm"]
            
            # If any value is NaN/missing, cannot declare valid trigger
            if window_slice.isna().any():
                continue

            cum_rain = window_slice.sum()
            if cum_rain >= threshold:
                # If after a previous lockout, require a pre-onset dry period (>=5 dry days)
                # to prevent ordinary mid-season wet spells from becoming new onset triggers
                if lockout_until_idx != -1:
                    pre_slice = df.loc[max(0, start_idx - 5) : start_idx - 1, "rainfall_mm"]
                    if len(pre_slice) < 5 or (pre_slice >= self.break_daily_ceiling_mm).any():
                        continue

                onset_triggers[i] = 1
                onset_dates[i] = str(df.loc[i, "date"])
                lockout_until_idx = i + lockout

        df["onset_trigger"] = onset_triggers
        df["onset_trigger_date"] = onset_dates
        return df

    def detect_false_onset(self, block_df: pd.DataFrame) -> pd.DataFrame:
        """
        Detects prototype false onset labels.
        Historical Label Logic:
        If an ONSET_TRIGGER occurs on day T, look ahead up to false_onset_lookahead_days.
        If a dry spell of >= false_onset_dry_spell_days occurs in that window, mark FALSE_ONSET = 1.
        """
        df = block_df.copy()
        n = len(df)

        false_onsets = [0] * n
        false_onset_dates = [None] * n
        dry_starts = [None] * n
        dry_ends = [None] * n
        dry_lens = [None] * n

        lookahead = self.false_onset_lookahead_days
        dry_threshold = self.false_onset_dry_spell_days
        dry_ceiling = self.break_daily_ceiling_mm

        for i in range(n):
            if df.loc[i, "onset_trigger"] == 1:
                # Look forward up to lookahead days
                future_end = min(n, i + 1 + lookahead)
                future_slice = df.loc[i + 1:future_end - 1].reset_index()

                # Find consecutive dry days in the lookahead window
                cur_dry = 0
                max_dry = 0
                best_start = None
                best_end = None
                cur_start = None

                for _, row in future_slice.iterrows():
                    rf = row["rainfall_mm"]
                    if pd.notna(rf) and float(rf) < dry_ceiling:
                        if cur_dry == 0:
                            cur_start = row["date"]
                        cur_dry += 1
                        if cur_dry > max_dry:
                            max_dry = cur_dry
                            best_start = cur_start
                            best_end = row["date"]
                    else:
                        cur_dry = 0
                        cur_start = None

                if max_dry >= dry_threshold:
                    false_onsets[i] = 1
                    false_onset_dates[i] = str(df.loc[i, "date"])
                    dry_starts[i] = str(best_start)
                    dry_ends[i] = str(best_end)
                    dry_lens[i] = int(max_dry)

        df["false_onset"] = false_onsets
        df["false_onset_date"] = false_onset_dates
        df["dry_spell_start"] = dry_starts
        df["dry_spell_end"] = dry_ends
        df["dry_spell_length"] = dry_lens
        return df

    def detect_break(self, block_df: pd.DataFrame) -> pd.DataFrame:
        """
        Detects break / prolonged dry spell events.
        A break event is marked when dry spell duration reaches or exceeds break_dry_spell_days.
        Assigns distinct break_episode_id to each contiguous break episode.
        """
        df = block_df.copy()
        n = len(df)

        break_events = [0] * n
        break_starts = [None] * n
        break_ends = [None] * n
        break_durations = [None] * n
        break_episode_ids = [None] * n

        ceiling = self.break_daily_ceiling_mm
        min_break_days = self.break_dry_spell_days
        episode_idx = 0

        # Identify contiguous spells where rainfall_mm < ceiling and not NaN
        i = 0
        while i < n:
            rf = df.loc[i, "rainfall_mm"]
            if pd.notna(rf) and float(rf) < ceiling:
                spell_start_idx = i
                while i < n and pd.notna(df.loc[i, "rainfall_mm"]) and float(df.loc[i, "rainfall_mm"]) < ceiling:
                    i += 1
                spell_end_idx = i - 1
                spell_length = spell_end_idx - spell_start_idx + 1

                if spell_length >= min_break_days:
                    episode_idx += 1
                    block_id = str(df.loc[spell_start_idx, "block_id"]) if "block_id" in df.columns else "BLK"
                    episode_id = f"{block_id}_BREAK_{episode_idx:03d}"
                    start_date = str(df.loc[spell_start_idx, "date"])
                    end_date = str(df.loc[spell_end_idx, "date"])
                    for idx in range(spell_start_idx, spell_end_idx + 1):
                        break_events[idx] = 1
                        break_starts[idx] = start_date
                        break_ends[idx] = end_date
                        break_durations[idx] = spell_length
                        break_episode_ids[idx] = episode_id
            else:
                i += 1

        df["break_event"] = break_events
        df["break_start"] = break_starts
        df["break_end"] = break_ends
        df["break_duration_days"] = break_durations
        df["break_episode_id"] = break_episode_ids
        return df

    def detect_heavy_rain(self, block_df: pd.DataFrame) -> pd.DataFrame:
        """
        Detects prototype heavy rain events (daily rainfall >= heavy_rainfall_mm).
        """
        df = block_df.copy()
        n = len(df)

        heavy_events = [0] * n
        heavy_dates = [None] * n
        heavy_amounts = [None] * n

        threshold = self.heavy_rainfall_mm

        for i in range(n):
            rf = df.loc[i, "rainfall_mm"]
            if pd.notna(rf) and float(rf) >= threshold:
                heavy_events[i] = 1
                heavy_dates[i] = str(df.loc[i, "date"])
                heavy_amounts[i] = round(float(rf), 1)

        df["heavy_rain_event"] = heavy_events
        df["heavy_rain_date"] = heavy_dates
        df["heavy_rainfall_mm"] = heavy_amounts
        return df

    def detect_revival(self, block_df: pd.DataFrame) -> pd.DataFrame:
        """
        Detects rainfall revival following a declared break spell.
        A revival is declared when rainfall resumes immediately after a break event ends,
        reaching >= revival_rainfall_mm within revival_window_days.
        """
        df = block_df.copy()
        n = len(df)

        revival_events = [0] * n
        revival_dates = [None] * n
        revival_amounts = [None] * n

        window = self.revival_window_days
        threshold = self.revival_rainfall_mm

        # Check days following a break_event transition (where day i-1 was in break_event, but day i is not)
        for i in range(1, n):
            prev_break = df.loc[i - 1, "break_event"] == 1
            cur_break = df.loc[i, "break_event"] == 0

            if prev_break and cur_break:
                # Check cumulative rain in window [i, min(n-1, i + window - 1)]
                window_end = min(n, i + window)
                window_slice = df.loc[i:window_end - 1, "rainfall_mm"]
                if not window_slice.isna().any():
                    cum_rain = window_slice.sum()
                    if cum_rain >= threshold:
                        revival_events[i] = 1
                        revival_dates[i] = str(df.loc[i, "date"])
                        revival_amounts[i] = round(float(cum_rain), 1)

        df["revival_event"] = revival_events
        df["revival_date"] = revival_dates
        df["revival_rainfall_mm"] = revival_amounts
        return df
