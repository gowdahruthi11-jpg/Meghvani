"""
Build Multi-Year Event Summary Script (Meghvani Phase 7B).

Reuses the existing Phase 2.1 EventDetector heuristics without modifying definitions or thresholds.
Summarizes events year-by-year and block-by-block, plus block-level totals per year.
Outputs: data/processed/historical/multiyear_event_summary.csv
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.historical.dataset_builder import HistoricalDatasetBuilder
from app.config import PROJECT_ROOT as ROOT_DIR

HISTORICAL_PROCESSED_CSV = ROOT_DIR / "data" / "processed" / "historical_events.csv"
MULTIYEAR_RAW_DIR = ROOT_DIR / "data" / "raw" / "historical"
OUTPUT_SUMMARY_CSV = ROOT_DIR / "data" / "processed" / "historical" / "multiyear_event_summary.csv"


BLOCK_DAILY_RAINFALL_CSV = ROOT_DIR / "data" / "processed" / "historical" / "block_daily_rainfall.csv"
MULTIYEAR_EVENTS_CSV = ROOT_DIR / "data" / "processed" / "historical" / "multiyear_historical_events.csv"


def load_all_historical_events() -> pd.DataFrame:
    """
    Loads all available processed historical event records.
    If real multi-year block daily rainfall exists, runs EventDetector on it.
    """
    if BLOCK_DAILY_RAINFALL_CSV.exists():
        builder = HistoricalDatasetBuilder()
        res = builder.build_from_source(BLOCK_DAILY_RAINFALL_CSV, output_csv_path=MULTIYEAR_EVENTS_CSV)
        return res.get("dataframe", res.get("dataset"))

    raw_files = list(MULTIYEAR_RAW_DIR.glob("*.csv")) if MULTIYEAR_RAW_DIR.exists() else []

    if raw_files:
        builder = HistoricalDatasetBuilder()
        dfs = []
        for rf in sorted(raw_files):
            try:
                res = builder.build_from_source(rf)
                dfs.append(res.get("dataframe", res.get("dataset")))
            except Exception as e:
                print(f"Warning: Failed to process raw historical file {rf}: {e}")
        if dfs:
            return pd.concat(dfs, ignore_index=True)

    if HISTORICAL_PROCESSED_CSV.exists():
        return pd.read_csv(HISTORICAL_PROCESSED_CSV)

    # Fallback to demo raw rainfall if processed does not exist
    demo_raw = ROOT_DIR / "data" / "raw" / "rainfall" / "demo_rainfall.csv"
    if demo_raw.exists():
        builder = HistoricalDatasetBuilder()
        res = builder.build_from_source(demo_raw, output_csv_path=HISTORICAL_PROCESSED_CSV)
        return res.get("dataframe", res.get("dataset"))

    return pd.DataFrame()


def generate_multiyear_event_summary(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates year-by-year and block-by-block event statistics, plus block totals for each year.
    Columns:
    - year
    - block_id
    - onset_events
    - false_onset_events
    - break_episodes
    - heavy_rain_events
    - revival_events
    - valid_rainfall_days
    - missing_rainfall_days
    """
    if events_df.empty or "date" not in events_df.columns:
        return pd.DataFrame(columns=[
            "year", "block_id", "onset_events", "false_onset_events",
            "break_episodes", "heavy_rain_events", "revival_events",
            "valid_rainfall_days", "missing_rainfall_days"
        ])

    df = events_df.copy()
    df["date_dt"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date_dt"])
    df["year"] = df["date_dt"].dt.year

    if "block_id" not in df.columns:
        df["block_id"] = "DEFAULT"

    records = []
    years = sorted(df["year"].unique())

    for yr in years:
        yr_df = df[df["year"] == yr]
        blocks = sorted(yr_df["block_id"].unique())

        yr_onset_tot = 0
        yr_fo_tot = 0
        yr_break_tot = 0
        yr_heavy_tot = 0
        yr_rev_tot = 0
        yr_valid_tot = 0
        yr_missing_tot = 0

        for blk in blocks:
            blk_df = yr_df[yr_df["block_id"] == blk]

            onset_cnt = int((blk_df.get("onset_trigger", 0) == 1).sum())
            fo_cnt = int((blk_df.get("false_onset", 0) == 1).sum())
            
            # Break episodes: count distinct episode IDs if available, else count break starts
            if "break_episode_id" in blk_df.columns:
                break_cnt = int(blk_df["break_episode_id"].dropna().nunique())
            else:
                break_cnt = int((blk_df.get("break_event", 0) == 1).sum())

            heavy_cnt = int((blk_df.get("heavy_rain_event", 0) == 1).sum())
            rev_cnt = int((blk_df.get("revival_event", 0) == 1).sum())

            valid_days = int(blk_df["rainfall_mm"].notna().sum()) if "rainfall_mm" in blk_df.columns else len(blk_df)
            missing_days = int(blk_df["rainfall_mm"].isna().sum()) if "rainfall_mm" in blk_df.columns else 0

            records.append({
                "year": yr,
                "block_id": blk,
                "onset_events": onset_cnt,
                "false_onset_events": fo_cnt,
                "break_episodes": break_cnt,
                "heavy_rain_events": heavy_cnt,
                "revival_events": rev_cnt,
                "valid_rainfall_days": valid_days,
                "missing_rainfall_days": missing_days
            })

            yr_onset_tot += onset_cnt
            yr_fo_tot += fo_cnt
            yr_break_tot += break_cnt
            yr_heavy_tot += heavy_cnt
            yr_rev_tot += rev_cnt
            yr_valid_tot += valid_days
            yr_missing_tot += missing_days

        # Add total row across blocks for this year
        records.append({
            "year": yr,
            "block_id": "ALL_BLOCKS_TOTAL",
            "onset_events": yr_onset_tot,
            "false_onset_events": yr_fo_tot,
            "break_episodes": yr_break_tot,
            "heavy_rain_events": yr_heavy_tot,
            "revival_events": yr_rev_tot,
            "valid_rainfall_days": yr_valid_tot,
            "missing_rainfall_days": yr_missing_tot
        })

    summary_df = pd.DataFrame(records)
    return summary_df


def main():
    print("Loading historical events...")
    events_df = load_all_historical_events()
    print(f"Loaded {len(events_df)} event records.")

    summary_df = generate_multiyear_event_summary(events_df)
    
    OUTPUT_SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(OUTPUT_SUMMARY_CSV, index=False)
    print(f"Multi-year event summary written to: {OUTPUT_SUMMARY_CSV}")
    print("\nSummary preview:")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
