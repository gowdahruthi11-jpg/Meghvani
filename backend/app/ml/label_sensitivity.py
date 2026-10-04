"""
Meghvani Phase 8B: Label Sensitivity Analysis Engine.
Sweeps agrometeorological event detection thresholds:
- Onset threshold (15, 20, 25 mm)
- Dry-spell length (5, 7, 10 days)
- False-onset lookahead window (14, 21, 30 days)
Evaluates event counts across historical seasons (2019-2024) and measures resulting model skill deltas.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import json
import logging
import numpy as np
import pandas as pd

from app.config import PROJECT_ROOT, event_definitions_config
from app.historical.event_detector import EventDetector
from app.prediction.targets import create_future_event_target
from app.ml.baseline_predictor import LogisticRegressionBaseline, BASELINE_FEATURE_COLUMNS
from app.ml.evaluation import brier_score, brier_skill_score, roc_auc_score_safe

logger = logging.getLogger(__name__)

BLOCK_DAILY_RAINFALL_CSV = PROJECT_ROOT / "data" / "processed" / "historical" / "block_daily_rainfall.csv"
MULTIYEAR_PREDICTION_CSV = PROJECT_ROOT / "data" / "processed" / "historical" / "multiyear_prediction_dataset.csv"


def run_label_sensitivity_sweep(
    onset_thresholds: Optional[List[float]] = None,
    dry_spell_lengths: Optional[List[int]] = None,
    lookahead_windows: Optional[List[int]] = None,
    rainfall_csv_path: Optional[Path] = None,
    prediction_csv_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Executes 3x3x3 parameter sweep across onset, dry spell, and false-onset lookahead settings.
    """
    onsets = onset_thresholds or [15.0, 20.0, 25.0]
    dry_lens = dry_spell_lengths or [5, 7, 10]
    lookaheads = lookahead_windows or [14, 21, 30]

    rf_path = rainfall_csv_path or BLOCK_DAILY_RAINFALL_CSV
    pred_path = prediction_csv_path or MULTIYEAR_PREDICTION_CSV

    if not rf_path.exists() or not pred_path.exists():
        return {
            "status": "UNAVAILABLE",
            "message": f"Required data files not found ({rf_path} or {pred_path})."
        }

    raw_rf_df = pd.read_csv(rf_path)
    pred_df = pd.read_csv(pred_path)

    raw_rf_df["prediction_dt"] = pd.to_datetime(raw_rf_df["date"])
    raw_rf_df["year"] = raw_rf_df["prediction_dt"].dt.year
    pred_df["prediction_dt"] = pd.to_datetime(pred_df["prediction_date"])
    pred_df["year"] = pred_df["prediction_dt"].dt.year

    years = sorted(raw_rf_df["year"].unique().tolist())
    combos = []

    # In-season mask for fast evaluation
    m = pred_df["prediction_dt"].dt.month
    d = pred_df["prediction_dt"].dt.day
    in_season_mask = ((m == 5) & (d >= 25)) | (m == 6) | ((m == 7) & (d <= 31))

    # Features to use for model evaluation
    feat_cols = [c for c in BASELINE_FEATURE_COLUMNS if c in pred_df.columns]

    for onset_val in onsets:
        for dry_val in dry_lens:
            for lookahead_val in lookaheads:
                custom_config = {
                    "thresholds": {
                        "onset": {
                            "onset_rainfall_mm": float(onset_val),
                            "onset_window_days": 3,
                            "onset_lockout_days": 30
                        },
                        "false_onset": {
                            "false_onset_dry_spell_days": int(dry_val),
                            "false_onset_lookahead_days": int(lookahead_val)
                        },
                        "break_spell": {
                            "break_dry_spell_days": 5,
                            "daily_rainfall_ceiling_mm": 2.5
                        },
                        "heavy_rain": {
                            "heavy_rainfall_mm": 64.5
                        },
                        "revival": {
                            "revival_rainfall_mm": 15.0,
                            "revival_window_days": 2
                        }
                    }
                }

                detector = EventDetector(thresholds_config=custom_config)
                detected_df = detector.detect_events(raw_rf_df)

                # Merge false_onset label back into pred_df
                temp_merged = pred_df.copy()
                merge_key = ["block_id", "date"] if "date" in temp_merged.columns else ["block_id", "prediction_date"]
                right_date_col = "date"
                
                # Align dates
                temp_merged["_date_str"] = temp_merged["prediction_dt"].dt.strftime("%Y-%m-%d")
                detected_df["_date_str"] = detected_df["prediction_dt"].dt.strftime("%Y-%m-%d")
                
                label_map = detected_df.set_index(["block_id", "_date_str"])["false_onset"].to_dict()
                temp_merged["false_onset_indicator"] = [
                    label_map.get((b, d_str), 0)
                    for b, d_str in zip(temp_merged["block_id"], temp_merged["_date_str"])
                ]

                # Create 7D target
                target_col = "target_false_onset_7d"
                temp_merged[target_col] = create_future_event_target(
                    temp_merged,
                    event_indicator_col="false_onset_indicator",
                    horizon_days=7,
                    date_col="prediction_date"
                )

                # Count events per year
                event_counts_by_year = {}
                for yr in years:
                    yr_df = detected_df[detected_df["year"] == yr]
                    event_counts_by_year[int(yr)] = int(yr_df["false_onset"].sum())

                total_events = int(detected_df["false_onset"].sum())

                # Quick rolling-origin evaluation on in-season slice (evaluate 2024 with train 2019-2023)
                eval_mask = in_season_mask & (temp_merged["year"] == 2024)
                train_mask = in_season_mask & (temp_merged["year"] < 2024)

                y_train = temp_merged.loc[train_mask, target_col].values
                y_eval = temp_merged.loc[eval_mask, target_col].values
                X_train = temp_merged.loc[train_mask, feat_cols]
                X_eval = temp_merged.loc[eval_mask, feat_cols]

                clim_prob = float(np.mean(y_train)) if len(y_train) > 0 else 0.0
                clim_brier = brier_score(y_eval, np.full(len(y_eval), clim_prob))

                if len(y_train) > 0 and len(np.unique(y_train)) > 1:
                    model = LogisticRegressionBaseline(class_weight="balanced")
                    model.fit(X_train, y_train)
                    p_model = model.predict_proba(X_eval)[:, 1]
                    m_brier = brier_score(y_eval, p_model)
                    m_bss = brier_skill_score(m_brier, clim_brier) if (np.sum(y_eval == 1) > 0 and np.sum(y_eval == 0) > 0) else None
                    m_roc = roc_auc_score_safe(y_eval, p_model)
                else:
                    m_brier = clim_brier
                    m_bss = 0.0
                    m_roc = None

                combos.append({
                    "onset_rainfall_mm": onset_val,
                    "false_onset_dry_spell_days": dry_val,
                    "false_onset_lookahead_days": lookahead_val,
                    "total_false_onset_events_all_years": total_events,
                    "events_by_year": event_counts_by_year,
                    "eval_2024_positive_targets": int(np.sum(y_eval == 1)),
                    "eval_2024_climatology_brier": round(clim_brier, 4),
                    "eval_2024_model_brier": round(m_brier, 4),
                    "eval_2024_model_bss": round(m_bss, 4) if m_bss is not None else None,
                    "eval_2024_roc_auc": round(m_roc, 4) if isinstance(m_roc, (int, float)) else None
                })

    return {
        "status": "READY",
        "total_combinations_evaluated": len(combos),
        "parameter_grid": {
            "onset_thresholds": onsets,
            "dry_spell_lengths": dry_lens,
            "lookahead_windows": lookaheads
        },
        "results": combos
    }
