#!/usr/bin/env python3
"""
CLI Script: Train Complete Multi-Event Prediction Suite for Meghvani.
Trains and calibrates probabilistic models for:
- Monsoon Onset (7d & 14d)
- Monsoon Break Spell (7d & 14d)
- Heavy Rain Episode (7d)
- False Onset Warning (7d)

Saves calibrated joblib models and metadata artifacts to ml/models/.
"""
import sys
import json
from pathlib import Path
import pandas as pd

# Add backend to sys.path so app modules import cleanly
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ml.multi_event_suite import MultiEventPredictor, EVENT_TARGET_MAPPING
from app.prediction.dataset_builder import DEFAULT_PREDICTION_CSV, PredictionDatasetBuilder


def train_multi_event_suite(dataset_path: Path = DEFAULT_PREDICTION_CSV):
    print("==================================================")
    print("[MEGHVANI MULTI-EVENT PREDICTION SUITE TRAINING]")
    print("==================================================")

    if not dataset_path.exists():
        print(f"Dataset not found at {dataset_path}. Generating from historical pipeline...")
        builder = PredictionDatasetBuilder()
        builder.build_dataset(output_csv_path=dataset_path)

    df = pd.read_csv(dataset_path)
    print(f"Loaded dataset: {len(df)} rows across {df['block_id'].nunique()} blocks.")

    predictor = MultiEventPredictor(model_dir=PROJECT_ROOT / "ml" / "models")
    summary = {}

    for event_key, config in EVENT_TARGET_MAPPING.items():
        print(f"\n---> Training: {config['event_name']} ({config['target_col']})")
        meta = predictor.train_event(event_key=event_key, df=df)
        predictor.save_artifacts(event_key)

        metrics = meta["evaluation_metrics"]
        print(f"     Positives: {meta['positives']} | Negatives: {meta['negatives']}")
        print(f"     Brier Score (Calibrated): {metrics['brier_score_calibrated']:.4f} (Climatology: {metrics['brier_score_climatology']:.4f})")
        print(f"     Brier Skill Score (BSS):  {metrics['brier_skill_score']:.4f}")
        print(f"     ROC-AUC:                  {metrics['roc_auc']:.4f} | PR-AUC: {metrics['pr_auc']:.4f}")
        print(f"     Calibration Status:       {meta['calibration_status']}")

        summary[event_key] = {
            "name": config["event_name"],
            "target": config["target_col"],
            "horizon_days": config["horizon_days"],
            "positives": meta["positives"],
            "metrics": metrics,
            "status": meta["calibration_status"]
        }

    # Save suite summary
    summary_path = PROJECT_ROOT / "ml" / "models" / "multi_event_suite_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n==================================================")
    print(f"[OK] All {len(EVENT_TARGET_MAPPING)} Event Models Trained and Saved to ml/models/")
    print(f"Summary saved to: {summary_path}")
    print("==================================================")
    return summary


if __name__ == "__main__":
    train_multi_event_suite()
