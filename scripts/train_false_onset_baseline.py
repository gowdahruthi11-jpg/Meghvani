#!/usr/bin/env python3
"""
CLI Script: Train False-Onset 7-Day Probabilistic Baseline for Meghvani Phase 3B.1.
Evaluation Integrity Fix: Clearly separates chronological holdout evaluation from event-focused diagnostic evaluation.
Saves distinct chronological and diagnostic model artifacts and metadata.
"""
import sys
import json
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import joblib

# Add backend to sys.path so app imports work
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.climatology import ClimatologyBaseline
from app.ml.baseline_predictor import LogisticRegressionBaseline, BASELINE_FEATURE_COLUMNS
from app.ml.evaluation import (
    brier_score,
    brier_skill_score,
    roc_auc_score_safe,
    pr_auc_score_safe,
    compute_calibration_curve,
    evaluate_chronological_holdout,
    evaluate_diagnostic_events
)
from app.ml.calibration import ProbabilityCalibrator, STATUS_INSUFFICIENT_DATA, STATUS_CALIBRATED
from app.prediction.dataset_builder import PredictionDatasetBuilder, DEFAULT_PREDICTION_CSV


def train_false_onset_baseline(
    dataset_path: Path = DEFAULT_PREDICTION_CSV,
    model_output_dir: Path = PROJECT_ROOT / "ml" / "models",
    train_ratio: float = 0.70
):
    print("==================================================")
    print("MEGHVANI FALSE-ONSET 7-DAY BASELINE (PHASE 3B.1)")
    print("EVALUATION INTEGRITY & DIAGNOSTIC SEPARATION")
    print("==================================================")

    # 1. Load prediction dataset
    if not dataset_path.exists():
        print(f"Prediction dataset not found at {dataset_path}. Building from historical data...")
        builder = PredictionDatasetBuilder()
        builder.build_dataset(output_csv_path=dataset_path)

    df = pd.read_csv(dataset_path)
    total_rows = len(df)
    target_col = "target_false_onset_7d"

    # ==================================================
    # SECTION A: DATASET SUMMARY
    # ==================================================
    good_mask = df["data_quality_flag"] == "GOOD"
    good_rows = int(good_mask.sum())
    insufficient_rows = int((~good_mask).sum())
    total_positives = int(df[target_col].sum())
    total_negatives = int((df[target_col] == 0).sum())

    missing_feats = df[BASELINE_FEATURE_COLUMNS].isna().sum()
    missing_dict = {col: int(v) for col, v in missing_feats.items() if v > 0}

    print("\n[A. DATASET SUMMARY]")
    print(f"Total rows:                 {total_rows}")
    print(f"GOOD rows:                  {good_rows}")
    print(f"INSUFFICIENT_HISTORY rows:  {insufficient_rows} (first 30d per block)")
    print(f"Positive count (all):       {total_positives}")
    print(f"Negative count (all):       {total_negatives}")
    if missing_dict:
        print(f"Missing features:           {missing_dict} (handled via median imputation)")
    else:
        print("Missing features:           0 across all 18 features")

    # ==================================================
    # SECTION B: CHRONOLOGICAL HOLDOUT
    # ==================================================
    print("\n[B. CHRONOLOGICAL HOLDOUT EVALUATION]")
    working_df = df.copy()
    working_df["_dt"] = pd.to_datetime(working_df["prediction_date"])
    working_df.sort_values(by="_dt", inplace=True)
    working_df.reset_index(drop=True, inplace=True)

    unique_dates = working_df["_dt"].drop_duplicates().sort_values().values
    n_dates = len(unique_dates)
    cutoff_idx = int(n_dates * train_ratio)
    train_date_ceiling = unique_dates[max(0, cutoff_idx - 1)]

    train_df = working_df[working_df["_dt"] <= train_date_ceiling].copy()
    test_df = working_df[working_df["_dt"] > train_date_ceiling].copy()

    train_start = str(train_df["prediction_date"].min())
    train_end = str(train_df["prediction_date"].max())
    test_start = str(test_df["prediction_date"].min())
    test_end = str(test_df["prediction_date"].max())

    n_train = len(train_df)
    n_test = len(test_df)
    train_pos = int(train_df[target_col].sum())
    test_pos = int(test_df[target_col].sum())

    # Fit chronological baseline on training split
    y_train = train_df[target_col].values
    y_test = test_df[target_col].values
    X_train = train_df[BASELINE_FEATURE_COLUMNS]
    X_test = test_df[BASELINE_FEATURE_COLUMNS]

    clim_model = ClimatologyBaseline()
    clim_model.fit(y_train)
    clim_test_prob = clim_model.predict_positive_proba(n_test)
    clim_brier = brier_score(y_test, clim_test_prob)

    chronological_lr = LogisticRegressionBaseline(class_weight="balanced", random_state=42)
    chronological_lr.fit(X_train, y_train)
    lr_test_probs = chronological_lr.predict_positive_proba(X_test)

    # Evaluate chronological holdout with integrity check
    chrono_eval = evaluate_chronological_holdout(
        y_test=y_test,
        y_test_prob=lr_test_probs,
        clim_brier=clim_brier,
        train_dates=(train_start, train_end),
        test_dates=(test_start, test_end),
        train_positives=train_pos,
        train_rows=n_train,
        test_rows=n_test
    )

    print(f"Train dates:                {train_start} to {train_end} ({n_train} rows)")
    print(f"Test dates:                 {test_start} to {test_end} ({n_test} rows)")
    print(f"Train positives:            {train_pos}")
    print(f"Test positives:             {test_pos}")
    print(f"Brier Score (Test):         {chrono_eval['brier_score']:.4f}")
    print(f"Brier Skill Score (Test):   {chrono_eval['brier_skill_score']} ({chrono_eval['brier_skill_status']})")
    print(f"ROC-AUC (Test):             {chrono_eval['roc_auc']}")
    print(f"PR-AUC (Test):              {chrono_eval['pr_auc']}")
    print(f"Evaluation Status:          {chrono_eval['status']}")
    print(f"Explanation:                {chrono_eval['explanation']}")

    # ==================================================
    # SECTION C: DIAGNOSTIC EVENT EVALUATION
    # ==================================================
    print("\n[C. DIAGNOSTIC EVENT EVALUATION]")
    # Train separate diagnostic model on all observations containing historical events
    X_all = working_df[BASELINE_FEATURE_COLUMNS]
    y_all = working_df[target_col].values

    diagnostic_lr = LogisticRegressionBaseline(class_weight="balanced", random_state=42)
    diagnostic_lr.fit(X_all, y_all)
    diag_probs = diagnostic_lr.predict_positive_proba(X_all)

    diag_eval = evaluate_diagnostic_events(y_true=y_all, y_prob=diag_probs)

    print(f"Diagnostic rows:            {diag_eval['total_diagnostic_rows']}")
    print(f"Positive count:             {diag_eval['positive_count']}")
    print(f"Negative count:             {diag_eval['negative_count']}")
    print(f"Positive rate:              {diag_eval['positive_rate'] * 100:.2f}%")
    print(f"Brier Score (Diagnostic):   {diag_eval['brier_score']:.4f}")
    print(f"ROC-AUC (Diagnostic):       {diag_eval['roc_auc']}")
    print(f"PR-AUC (Diagnostic):        {diag_eval['pr_auc']}")
    print(f"Evaluation Status:          {diag_eval['status']} (Not Operational)")
    print(f"Explanation:                {diag_eval['explanation']}")

    print("\n--- Diagnostic Calibration Table ---")
    print(f"{'Bin Range':<12} | {'Count':<6} | {'Mean Prob':<10} | {'Obs Freq':<10}")
    print("-" * 46)
    for b in diag_eval["calibration_bins"]:
        mp = f"{b['mean_predicted_probability']:.4f}" if b['mean_predicted_probability'] is not None else "   -   "
        of = f"{b['observed_event_frequency']:.4f}" if b['observed_event_frequency'] is not None else "   -   "
        print(f"{b['bin_range']:<12} | {b['sample_count']:<6} | {mp:<10} | {of:<10}")

    # ==================================================
    # SECTION D: PROBABILITY CALIBRATION EXPERIMENT
    # ==================================================
    print("\n[D. PROTOTYPE PROBABILITY CALIBRATION EXPERIMENT]")
    calibrator = ProbabilityCalibrator(method="sigmoid")
    cal_metadata = calibrator.fit_chronological_split(
        df=working_df,
        base_estimator=chronological_lr,
        feature_columns=BASELINE_FEATURE_COLUMNS,
        target_col=target_col,
        train_ratio=0.50,
        cal_ratio=0.25
    )

    print(f"Calibration Method:         {cal_metadata['method']} (Platt scaling)")
    print(f"Calibration Status:         {cal_metadata['status']}")
    print(f"Training Period:            {cal_metadata['training_period']} (pos={cal_metadata['train_positive_count']}, rows={cal_metadata['train_row_count']})")
    print(f"Calibration Period:         {cal_metadata['calibration_period']} (pos={cal_metadata['calibration_positive_count']}, rows={cal_metadata['calibration_row_count']})")
    print(f"Evaluation Period:          {cal_metadata['evaluation_period']} (pos={cal_metadata['evaluation_positive_count']}, rows={cal_metadata['evaluation_row_count']})")
    raw_brier_str = f"{cal_metadata['raw_brier_score']:.4f}" if cal_metadata['raw_brier_score'] is not None else "not available"
    cal_brier_str = f"{cal_metadata['calibrated_brier_score']:.4f}" if cal_metadata['calibrated_brier_score'] is not None else "not available"
    print(f"Raw Brier Score:            {raw_brier_str}")
    print(f"Calibrated Brier Score:     {cal_brier_str}")
    print(f"Calibration Explanation:    {cal_metadata['explanation']}")

    # ==================================================
    # SECTION E: SCIENTIFIC LIMITATION
    # ==================================================
    scientific_warning = (
        "This is a single-year prototype dataset. The chronological test period contains zero false-onset events. "
        "Therefore the chronological evaluation does not establish verified forecast skill. "
        "The event-focused evaluation is diagnostic only and must not be interpreted as operational temporal forecast validation. "
        "Probability calibration is a prototype experiment: with only 6 positive events all in early June, "
        "subsequent calibration/evaluation periods have zero positive events, making operational calibration unvalidated."
    )
    print("\n[E. SCIENTIFIC LIMITATION]")
    print(scientific_warning)

    # Feature contributions from chronological model
    feature_contributions = chronological_lr.get_feature_contributions()
    for feat in feature_contributions:
        feat["interpretation"] = (
            f"Fitted linear weight: {feat['coefficient']:+.4f}. "
            "These coefficients indicate model association within the prototype dataset. They are not causal effects."
        )

    # Save artifacts separately
    model_output_dir.mkdir(parents=True, exist_ok=True)
    chrono_joblib_path = model_output_dir / "false_onset_7d_logistic.joblib"
    diag_joblib_path = model_output_dir / "false_onset_7d_logistic_diagnostic.joblib"
    cal_joblib_path = model_output_dir / "false_onset_7d_calibrated.joblib"

    chrono_meta_path = model_output_dir / "false_onset_7d_logistic_metadata.json"
    diag_meta_path = model_output_dir / "false_onset_7d_logistic_diagnostic_metadata.json"
    cal_meta_path = model_output_dir / "false_onset_7d_calibrated_metadata.json"

    # Save models
    joblib.dump(chronological_lr, chrono_joblib_path)
    joblib.dump(diagnostic_lr, diag_joblib_path)
    joblib.dump(calibrator, cal_joblib_path)

    # Save diagnostic metadata
    with open(diag_meta_path, "w", encoding="utf-8") as f:
        json.dump(diag_eval, f, indent=2)

    # Standalone calibrated model metadata
    standalone_cal_metadata = {
        "target": target_col,
        "horizon_days": 7,
        "base_model": "LogisticRegressionBaseline",
        "calibration_method": cal_metadata["method"],
        "training_period": cal_metadata["training_period"],
        "calibration_period": cal_metadata["calibration_period"],
        "evaluation_period": cal_metadata["evaluation_period"],
        "train_row_count": cal_metadata["train_row_count"],
        "positive_count": cal_metadata["train_positive_count"],
        "calibration_row_count": cal_metadata["calibration_row_count"],
        "calibration_positive_count": cal_metadata["calibration_positive_count"],
        "evaluation_row_count": cal_metadata["evaluation_row_count"],
        "evaluation_positive_count": cal_metadata["evaluation_positive_count"],
        "raw_brier_score": cal_metadata["raw_brier_score"],
        "calibrated_brier_score": cal_metadata["calibrated_brier_score"],
        "improvement": cal_metadata["improvement"],
        "calibration_status": cal_metadata["status"],
        "explanation": cal_metadata["explanation"],
        "scientific_warning": cal_metadata["scientific_warning"],
        "is_operational_forecast": False,
        "created_at": datetime.now().isoformat()
    }
    with open(cal_meta_path, "w", encoding="utf-8") as f:
        json.dump(standalone_cal_metadata, f, indent=2)

    # Save primary metadata containing chronological, diagnostic, and calibration sections
    metadata = {
        "model_name": "LogisticRegressionBaseline",
        "target": "target_false_onset_7d",
        "horizon_days": 7,
        "feature_names": BASELINE_FEATURE_COLUMNS,
        "evaluation_type": "single_year_chronological_prototype",
        "evaluation_status": chrono_eval["status"],
        "brier_score": chrono_eval["brier_score"],
        "brier_skill_score": chrono_eval["brier_skill_score"],
        "brier_skill_status": chrono_eval["brier_skill_status"],

        "roc_auc": chrono_eval["roc_auc"],
        "pr_auc": chrono_eval["pr_auc"],
        "chronological_evaluation": chrono_eval,
        "diagnostic_evaluation": diag_eval,
        "calibration": standalone_cal_metadata,
        "feature_contributions": feature_contributions,
        "scientific_warning": scientific_warning,
        "dataset_version": "meghvani_demo_2025_v1",
        "created_at": datetime.now().isoformat(),
        "disclaimer": (
            "PROTOTYPE BASELINE MODEL ONLY. Evaluated on a single-year chronological demo dataset. "
            "Reported metrics are prototype diagnostics and do NOT represent verified multi-year operational forecasting skill."
        )
    }

    with open(chrono_meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("\n--------------------------------")
    print(f"CHRONOLOGICAL MODEL SAVED:  {chrono_joblib_path}")
    print(f"DIAGNOSTIC MODEL SAVED:     {diag_joblib_path}")
    print(f"CALIBRATED MODEL SAVED:     {cal_joblib_path}")
    print(f"METADATA SAVED:             {chrono_meta_path}")
    print(f"DIAGNOSTIC METADATA SAVED:  {diag_meta_path}")
    print(f"CALIBRATED METADATA SAVED:  {cal_meta_path}")
    print("==================================================")
    return metadata


if __name__ == "__main__":
    train_false_onset_baseline()
