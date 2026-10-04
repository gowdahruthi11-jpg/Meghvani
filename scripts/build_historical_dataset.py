#!/usr/bin/env python3
"""
CLI Script: Build Historical Rainfall Feature and Event Dataset for Meghvani Phase 2.
"""
import argparse
import sys
from pathlib import Path

# Add backend to sys.path so app imports work
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.historical.dataset_builder import HistoricalDatasetBuilder

def main():
    parser = argparse.ArgumentParser(
        description="Meghvani Historical Rainfall Pipeline & Event Detection Engine"
    )
    parser.add_argument(
        "--input",
        "-i",
        default=str(PROJECT_ROOT / "data" / "raw" / "rainfall" / "demo_rainfall.csv"),
        help="Path to raw rainfall CSV input file"
    )
    parser.add_argument(
        "--output",
        "-o",
        default=str(PROJECT_ROOT / "data" / "processed" / "historical_events.csv"),
        help="Path to processed output CSV file"
    )
    parser.add_argument(
        "--parquet",
        action="store_true",
        help="Also export parquet format if pyarrow is installed"
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    parquet_path = output_path.with_suffix(".parquet") if args.parquet else None

    print("==================================================")
    print("MEGHVANI HISTORICAL DATA PIPELINE (PHASE 2)")
    print("==================================================")
    print(f"Reading input from: {input_path}")

    if not input_path.exists():
        print(f"ERROR: Input file does not exist: {input_path}")
        sys.exit(1)

    builder = HistoricalDatasetBuilder()
    try:
        result = builder.build_from_source(
            source=input_path,
            output_csv_path=output_path,
            output_parquet_path=parquet_path
        )
    except Exception as e:
        print(f"ERROR during dataset generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    summary = result["summary"]
    events = summary["events_detected"]

    print("\nProcessing Complete!")
    print(f"Input rows:          {summary['input_rows']}")
    print(f"Valid rows:          {summary['valid_rows']}")
    print(f"Blocks:              {summary['blocks_count']}")
    print(f"Date range:          {summary['date_range']['start']} to {summary['date_range']['end']}")
    print("")
    print(f"Primary onset triggers:  {events['onset_triggers']}")
    print(f"False onsets:            {events['false_onsets']}")
    print(f"Break spell days:        {events.get('break_spell_days_count', summary.get('break_spell_days_count', 0))}")
    print(f"Distinct break episodes: {events.get('distinct_break_episodes', summary.get('distinct_break_episodes', 0))}")
    print(f"Heavy rain events:       {events['heavy_rain_events']}")
    print(f"Revival events:          {events['revival_events']}")
    print("")
    print(f"CSV Output:          {output_path} ({output_path.stat().st_size} bytes)")
    if parquet_path and parquet_path.exists():
        print(f"Parquet Output:      {parquet_path} ({parquet_path.stat().st_size} bytes)")
    print("==================================================")
    print("NOTE: " + summary["disclaimer"])
    print("==================================================")

if __name__ == "__main__":
    main()
