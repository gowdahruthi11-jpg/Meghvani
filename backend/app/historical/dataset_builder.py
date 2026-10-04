"""
Historical dataset builder module.
Orchestrates loading, validation, feature engineering, event detection,
and exports the ML-ready dataset.
"""
from pathlib import Path
from typing import Dict, Any, Optional, Union
import pandas as pd
import logging

from app.historical.loader import RainfallDataLoader
from app.historical.validator import RainfallValidator, ValidationReport, QUALITY_GOOD
from app.historical.features import RainfallFeatureEngineer
from app.historical.event_detector import EventDetector
from app.config import event_thresholds_config, PROJECT_ROOT

logger = logging.getLogger(__name__)

DATASET_COLUMNS = [
    "block_id",
    "date",
    "rainfall_mm",
    "rainfall_1d",
    "rainfall_3d",
    "rainfall_5d",
    "rainfall_7d",
    "rainfall_14d",
    "rainfall_30d",
    "dry_spell_days",
    "wet_spell_days",
    "rainfall_intensity_class",
    "rainfall_anomaly",
    "onset_trigger",
    "false_onset",
    "break_event",
    "heavy_rain_event",
    "revival_event",
    "onset_trigger_date",
    "false_onset_date",
    "dry_spell_start",
    "dry_spell_end",
    "dry_spell_length",
    "break_start",
    "break_end",
    "break_duration_days",
    "break_episode_id",
    "heavy_rain_date",
    "heavy_rainfall_mm",
    "revival_date",
    "revival_rainfall_mm",
    "data_quality_flag",
    "source"
]


class HistoricalDatasetBuilder:
    """
    Builds the final machine-learning-ready historical dataset.
    """

    def __init__(self, thresholds_config: Optional[Dict[str, Any]] = None):
        self.thresholds_config = thresholds_config or event_thresholds_config
        self.loader = RainfallDataLoader()
        self.validator = RainfallValidator()
        self.feature_engineer = RainfallFeatureEngineer(self.thresholds_config)
        self.detector = EventDetector(self.thresholds_config)

    def build_from_source(
        self,
        source: Union[str, Path, pd.DataFrame],
        output_csv_path: Optional[Union[str, Path]] = None,
        output_parquet_path: Optional[Union[str, Path]] = None
    ) -> Dict[str, Any]:
        """
        Runs the full end-to-end processing pipeline.
        """
        # 1. Load data
        raw_df = self.loader.load(source)

        # 2. Validate data
        validated_df, validation_report = self.validator.validate(raw_df)

        # Filter valid records for feature calculation
        # (Preserve flags on invalid rows if any)
        valid_mask = validated_df["data_quality_flag"] == QUALITY_GOOD
        valid_subset = validated_df[valid_mask].copy()

        # 3. Compute Features
        featured_df = self.feature_engineer.compute_features(valid_subset)

        # 4. Detect Events
        labeled_df = self.detector.detect_events(featured_df)

        # Merge with any invalid rows to keep a complete record of data quality
        invalid_subset = validated_df[~valid_mask].copy()
        if not invalid_subset.empty:
            for col in DATASET_COLUMNS:
                if col not in invalid_subset.columns:
                    invalid_subset[col] = None
            final_df = pd.concat([labeled_df, invalid_subset], ignore_index=True)
            final_df.sort_values(by=["block_id", "date"], inplace=True)
        else:
            final_df = labeled_df

        # Ensure all required columns exist
        for col in DATASET_COLUMNS:
            if col not in final_df.columns:
                final_df[col] = None

        final_df = final_df[DATASET_COLUMNS].copy()

        # 5. Export to CSV/Parquet if paths provided
        if output_csv_path:
            csv_path = Path(output_csv_path)
            csv_path.parent.mkdir(parents=True, exist_ok=True)
            final_df.to_csv(csv_path, index=False, encoding="utf-8")
            logger.info(f"Saved processed dataset to {csv_path}")

        if output_parquet_path:
            parquet_path = Path(output_parquet_path)
            parquet_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                final_df.to_parquet(parquet_path, index=False)
                logger.info(f"Saved processed dataset to {parquet_path}")
            except Exception as e:
                logger.warning(f"Could not save Parquet (pyarrow/fastparquet not installed): {e}")

        # 6. Generate execution summary
        break_days = int((final_df["break_event"] == 1).sum())
        break_episodes = int(final_df["break_episode_id"].dropna().nunique()) if "break_episode_id" in final_df.columns else 0

        summary = {
            "input_rows": int(len(raw_df)),
            "valid_rows": int(validation_report.rows_valid),
            "blocks_count": int(final_df["block_id"].dropna().nunique()),
            "date_range": {
                "start": str(final_df["date"].dropna().min()) if not final_df.empty else None,
                "end": str(final_df["date"].dropna().max()) if not final_df.empty else None,
            },
            "break_spell_days_count": break_days,
            "distinct_break_episodes": break_episodes,
            "events_detected": {
                "onset_triggers": int((final_df["onset_trigger"] == 1).sum()),
                "false_onsets": int((final_df["false_onset"] == 1).sum()),
                "break_spell_days_count": break_days,
                "distinct_break_episodes": break_episodes,
                "break_events": break_episodes,
                "heavy_rain_events": int((final_df["heavy_rain_event"] == 1).sum()),
                "revival_events": int((final_df["revival_event"] == 1).sum()),
            },
            "validation_report": validation_report.to_dict(),
            "csv_output": str(output_csv_path) if output_csv_path else None,
            "disclaimer": "PROTOTYPE HISTORICAL DATASET - Heuristic event detection criteria for ML feature engineering only."
        }

        return {
            "summary": summary,
            "dataframe": final_df
        }
