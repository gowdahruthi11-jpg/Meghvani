#!/usr/bin/env python3
"""
CLI Script: Analyze Prediction-Ready Dataset for Meghvani Phase 3A.
Reports rows, blocks, temporal span, class balance per horizon, data quality, and leakage safeguards.
"""
import sys
from pathlib import Path
import pandas as pd

# Add backend to sys.path so app imports work
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.prediction.dataset_builder import PredictionDatasetBuilder, DEFAULT_PREDICTION_CSV, DEFAULT_HISTORICAL_CSV

def main():
    print("==================================================")
    print("MEGHVANI PREDICTION DATASET AUDIT (PHASE 3A)")
    print("==================================================")

    builder = PredictionDatasetBuilder()
    if not DEFAULT_PREDICTION_CSV.exists():
        print(f"Prediction dataset not found at {DEFAULT_PREDICTION_CSV}. Generating...")
        res = builder.build_dataset()
        summary = res["summary"]
        df = res["dataframe"]
    else:
        print(f"Analyzing existing prediction dataset: {DEFAULT_PREDICTION_CSV}")
        res = builder.build_dataset(historical_source=DEFAULT_HISTORICAL_CSV, output_csv_path=DEFAULT_PREDICTION_CSV)
        summary = res["summary"]
        df = res["dataframe"]

    print("\n[DATASET OVERVIEW]")
    print(f"Total Prediction Rows:       {summary['rows']}")
    print(f"Blocks Monitored:            {summary['blocks']}")
    print(f"Available Calendar Years:    {summary['years']} (Total: {summary['total_years']})")
    print(f"Observation Date Range:      {summary['date_range']['start']} to {summary['date_range']['end']}")
    print(f"Horizons Configured:         {summary['horizons']} days")
    print(f"Predictive Feature Count:    {summary['feature_columns_count']}")
    print(f"Target Label Count:          {summary['target_columns_count']}")

    print("\n[DATA QUALITY & HISTORY CHECKS]")
    print(f"Insufficient History Rows:   {summary['insufficient_history_rows']} (First 30d per block)")
    print(f"Data Quality Distribution:   {summary['quality_distribution']}")

    # Missing values check on features
    feature_cols = [c for c in df.columns if not c.startswith("target_") and c not in ["block_id", "prediction_date", "data_quality_flag", "source"]]
    missing_feats = df[feature_cols].isna().sum()
    has_missing = missing_feats[missing_feats > 0]
    if len(has_missing) > 0:
        print(f"Features with missing/NaN values: {has_missing.to_dict()}")
    else:
        print("Feature Missingness:         0 missing values across all predictive features.")

    print("\n[TARGET CLASS DISTRIBUTIONS ACROSS HORIZONS]")
    horizons = summary["horizons"]
    events = ["onset", "false_onset", "break", "heavy_rain", "revival"]

    for h in horizons:
        print(f"\n--- Horizon: {h} Days ---")
        for evt in events:
            col = f"target_{evt}_{h}d"
            dist = summary["target_distributions"].get(col, {"positive": 0, "negative": 0})
            pos = dist["positive"]
            neg = dist["negative"]
            rate = (pos / (pos + neg) * 100) if (pos + neg) > 0 else 0.0
            print(f"  {col:<24} Positives: {pos:>3} | Negatives: {neg:>3} | Pos Rate: {rate:5.1f}%")

    print("\n[TEMPORAL VALIDATION ARCHITECTURE]")
    if summary["total_years"] <= 1:
        print("NOTICE: Insufficient historical years for genuine multi-year validation.")
        print(f"Current dataset contains {summary['total_years']} calendar year ({summary['years']}).")
        print("Multi-year train/val/test splits will activate automatically when multi-year data is connected.")
    else:
        print("Multi-year historical data is present for cross-season validation.")

    print("\n==================================================")
    print("DATA LEAKAGE SAFEGUARD: " + summary["leakage_boundary"])
    print("NOTE: " + summary["disclaimer"])
    print("==================================================")

if __name__ == "__main__":
    main()
