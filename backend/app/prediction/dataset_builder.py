"""
Prediction dataset builder module for Meghvani Phase 3A.
Assembles the ML-ready dataset combining backward-looking features with forward-looking target labels.
"""
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import pandas as pd
import numpy as np
import logging

from app.prediction.features import PredictiveFeatureEngineer
from app.prediction.targets import create_all_future_targets, DEFAULT_HORIZONS
from app.prediction.splits import get_dataset_temporal_info
from app.config import PROJECT_ROOT, event_thresholds_config

logger = logging.getLogger(__name__)

PREDICTION_DATASET_COLUMNS = [
    # Identification
    "block_id",
    "prediction_date",

    # Predictive Features (Strictly on or before prediction_date)
    "rainfall_mm",
    "rainfall_3d",
    "rainfall_5d",
    "rainfall_7d",
    "rainfall_14d",
    "rainfall_30d",
    "dry_spell_days",
    "wet_spell_days",
    "rainfall_change_3d",
    "rainfall_change_7d",
    "rainfall_ratio_3d_7d",
    "month",
    "day_of_year",
    "monsoon_month_flag",
    "days_since_last_onset",
    "days_since_last_break",
    "days_since_last_heavy_rain",
    "days_since_last_revival",

    # Target Labels: Onset (Strictly after prediction_date)
    "target_onset_7d",
    "target_onset_14d",
    "target_onset_21d",
    "target_onset_30d",

    # Target Labels: False Onset
    "target_false_onset_7d",
    "target_false_onset_14d",
    "target_false_onset_21d",
    "target_false_onset_30d",

    # Target Labels: Break (Episode start)
    "target_break_7d",
    "target_break_14d",
    "target_break_21d",
    "target_break_30d",

    # Target Labels: Heavy Rain
    "target_heavy_rain_7d",
    "target_heavy_rain_14d",
    "target_heavy_rain_21d",
    "target_heavy_rain_30d",

    # Target Labels: Revival
    "target_revival_7d",
    "target_revival_14d",
    "target_revival_21d",
    "target_revival_30d",

    # Metadata
    "data_quality_flag",
    "source"
]

DEFAULT_HISTORICAL_CSV = PROJECT_ROOT / "data" / "processed" / "historical_events.csv"
DEFAULT_PREDICTION_CSV = PROJECT_ROOT / "data" / "processed" / "prediction_dataset.csv"


class PredictionDatasetBuilder:
    """
    Constructs the prediction-ready dataset for baseline forecasting models.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or event_thresholds_config
        self.feature_engineer = PredictiveFeatureEngineer(self.config)
        pred_cfg = self.config.get("prediction", {})
        self.horizons = pred_cfg.get("forecast_horizons_days", DEFAULT_HORIZONS)

    def build_from_file(
        self,
        path: Union[str, Path],
        output_csv_path: Optional[Union[str, Path]] = None
    ) -> pd.DataFrame:
        """
        Loads historical labeled events from a CSV file, constructs the prediction dataset,
        and returns the resulting DataFrame.
        """
        result = self.build_dataset(historical_source=path, output_csv_path=output_csv_path)
        return result["dataframe"]

    def build_prediction_dataset(
        self,
        df: pd.DataFrame,
        output_csv_path: Optional[Union[str, Path]] = None
    ) -> pd.DataFrame:
        """
        Constructs the prediction dataset from an in-memory DataFrame and returns the resulting DataFrame.
        """
        result = self.build_dataset(historical_source=df, output_csv_path=output_csv_path)
        return result["dataframe"]

    def build_dataset(
        self,
        historical_source: Union[str, Path, pd.DataFrame] = DEFAULT_HISTORICAL_CSV,
        output_csv_path: Optional[Union[str, Path]] = DEFAULT_PREDICTION_CSV
    ) -> Dict[str, Any]:
        """
        Loads historical labeled events, engineers backward-looking predictors,
        constructs forward target horizons, and saves the prediction dataset.
        """
        # 1. Load historical labeled dataset
        if isinstance(historical_source, pd.DataFrame):
            hist_df = historical_source.copy()
        else:
            p = Path(historical_source)
            if not p.exists():
                raise FileNotFoundError(f"Historical events file not found: {p}")
            hist_df = pd.read_csv(p)

        if hist_df.empty:
            raise ValueError("Input historical dataframe is empty.")

        # Standardize date and prediction_date
        if "prediction_date" not in hist_df.columns:
            hist_df["prediction_date"] = hist_df["date"]

        # 2. Engineer backward-looking features
        featured_df = self.feature_engineer.engineer_features(hist_df)

        # 3. Construct forward-looking targets
        targeted_df = create_all_future_targets(featured_df, horizons=self.horizons)

        # 4. Filter and arrange final columns
        for col in PREDICTION_DATASET_COLUMNS:
            if col not in targeted_df.columns:
                targeted_df[col] = None

        final_df = targeted_df[PREDICTION_DATASET_COLUMNS].copy()

        # 5. Export to CSV if path provided
        if output_csv_path:
            out_path = Path(output_csv_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            final_df.to_csv(out_path, index=False, encoding="utf-8")
            logger.info(f"Saved prediction dataset to {out_path} ({len(final_df)} rows)")

        # 6. Generate summary statistics and class distributions
        temporal_info = get_dataset_temporal_info(final_df, "prediction_date")

        target_cols = [c for c in PREDICTION_DATASET_COLUMNS if c.startswith("target_")]
        target_counts: Dict[str, Dict[str, int]] = {}
        for tc in target_cols:
            pos = int((final_df[tc] == 1).sum())
            neg = int((final_df[tc] == 0).sum())
            target_counts[tc] = {"positive": pos, "negative": neg}

        insufficient_history = int((final_df["data_quality_flag"] == "INSUFFICIENT_HISTORY").sum())
        quality_dist = final_df["data_quality_flag"].value_counts().to_dict()

        summary = {
            "rows": int(len(final_df)),
            "blocks": int(final_df["block_id"].dropna().nunique()),
            "years": temporal_info["years"],
            "total_years": temporal_info["total_years"],
            "date_range": {
                "start": temporal_info["start_date"],
                "end": temporal_info["end_date"]
            },
            "horizons": self.horizons,
            "feature_columns_count": len([c for c in PREDICTION_DATASET_COLUMNS if not c.startswith("target_") and c not in ["block_id", "prediction_date", "data_quality_flag", "source"]]),
            "target_columns_count": len(target_cols),
            "target_distributions": target_counts,
            "insufficient_history_rows": insufficient_history,
            "quality_distribution": quality_dist,
            "csv_output": str(output_csv_path) if output_csv_path else None,
            "leakage_boundary": "STRICT: Features use exclusively date <= T; targets use exclusively date > T.",
            "disclaimer": "PROTOTYPE PREDICTION DATASET - Prepared for supervised ML baseline forecasting. No forecasts generated yet."
        }

        return {
            "summary": summary,
            "dataframe": final_df
        }
