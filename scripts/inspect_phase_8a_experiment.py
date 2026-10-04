import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

import pandas as pd
import numpy as np
from app.ml.baseline_predictor import LogisticRegressionBaseline, BASELINE_FEATURE_COLUMNS
from app.ml.climatology import ClimatologyBaseline
from app.ml.evaluation import brier_score, brier_skill_score, roc_auc_score_safe, pr_auc_score_safe, compute_calibration_curve
from sklearn.calibration import _SigmoidCalibration
from sklearn.isotonic import IsotonicRegression

df = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "historical" / "multiyear_prediction_dataset.csv")
df["year"] = pd.to_datetime(df["prediction_date"]).dt.year

print("=" * 60)
print("PHASE 8A: CLASS WEIGHT & CALIBRATION EXPERIMENT")
print("=" * 60)

for h in [7, 14, 21, 30]:
    col = f"target_false_onset_{h}d"
    pos = df[col].sum()
    print(f"Horizon {h:2d}d: pos={pos:4d}/{len(df)} ({pos/len(df)*100:.2f}%)")

# Let's inspect rolling-origin evaluation for 7-day horizon:
print("\n--- ROLLING-ORIGIN EVALUATION (7-DAY HORIZON) ---")
years = sorted(df["year"].unique())
print(f"Available years: {years}")

target_col = "target_false_onset_7d"

for eval_year in years:
    prior_years = [y for y in years if y < eval_year]
    if not prior_years:
        print(f"\nEval Year {eval_year}: No prior training years available. (Skipped)")
        continue

    # Split prior years into TRAIN and CALIBRATION if >= 2 prior years exist, else only TRAIN
    if len(prior_years) == 1:
        # e.g. eval 2020: prior is [2019] -> cannot separate calibration without intra-year split or marking INSUFFICIENT
        train_years = prior_years
        cal_years = []
    else:
        # earliest years = train, last prior year = cal
        train_years = prior_years[:-1]
        cal_years = [prior_years[-1]]

    train_df = df[df["year"].isin(train_years)]
    cal_df = df[df["year"].isin(cal_years)] if cal_years else pd.DataFrame()
    eval_df = df[df["year"] == eval_year]

    y_train = train_df[target_col].values
    y_cal = cal_df[target_col].values if not cal_df.empty else np.array([])
    y_eval = eval_df[target_col].values

    # Climatology
    clim = ClimatologyBaseline()
    clim.fit(y_train if cal_df.empty else np.concatenate([y_train, y_cal]))
    clim_probs = clim.predict_proba(len(y_eval))[:, 1]
    clim_brier = brier_score(y_eval, clim_probs)

    # Variant A: Existing Raw Baseline (class_weight="balanced")
    model_a = LogisticRegressionBaseline(class_weight="balanced")
    model_a.fit(train_df[BASELINE_FEATURE_COLUMNS], y_train)
    raw_eval_probs = model_a.predict_proba(eval_df[BASELINE_FEATURE_COLUMNS])[:, 1]
    raw_brier = brier_score(y_eval, raw_eval_probs)
    raw_bss = brier_skill_score(raw_brier, clim_brier)
    raw_roc = roc_auc_score_safe(y_eval, raw_eval_probs)
    raw_pr = pr_auc_score_safe(y_eval, raw_eval_probs)

    # Variant B: Probability-Aligned Baseline (class_weight=None)
    model_b = LogisticRegressionBaseline(class_weight=None)
    model_b.fit(train_df[BASELINE_FEATURE_COLUMNS], y_train)
    unweighted_eval_probs = model_b.predict_proba(eval_df[BASELINE_FEATURE_COLUMNS])[:, 1]
    unweighted_brier = brier_score(y_eval, unweighted_eval_probs)
    unweighted_bss = brier_skill_score(unweighted_brier, clim_brier)
    unweighted_roc = roc_auc_score_safe(y_eval, unweighted_eval_probs)
    unweighted_pr = pr_auc_score_safe(y_eval, unweighted_eval_probs)

    # Calibration of Variant A
    cal_brier = None
    cal_bss = None
    cal_roc = None
    cal_pr = None
    cal_status = "INSUFFICIENT_CALIBRATION_DATA"

    if not cal_df.empty and len(np.unique(y_cal)) >= 2:
        raw_cal_probs = model_a.predict_proba(cal_df[BASELINE_FEATURE_COLUMNS])[:, 1]
        sig = _SigmoidCalibration()
        sig.fit(raw_cal_probs, y_cal)
        cal_eval_probs = np.clip(sig.predict(raw_eval_probs), 0.0, 1.0)
        cal_brier = brier_score(y_eval, cal_eval_probs)
        cal_bss = brier_skill_score(cal_brier, clim_brier)
        cal_roc = roc_auc_score_safe(y_eval, cal_eval_probs)
        cal_pr = pr_auc_score_safe(y_eval, cal_eval_probs)
        cal_status = "CALIBRATED"

    print(f"\nEval Year {eval_year} (Train={train_years}, Cal={cal_years}, N_eval={len(y_eval)}, Pos={int(np.sum(y_eval))}):")
    print(f"  Climatology: Brier = {clim_brier:.4f} (clim rate = {clim.probability_:.4f})")
    print(f"  Variant A (Balanced Raw): Brier = {raw_brier:.4f}, BSS = {raw_bss if raw_bss is not None else 'None':.4f}, ROC = {raw_roc:.4f}, PR = {raw_pr:.4f}, Mean P = {np.mean(raw_eval_probs):.4f}")
    if cal_status == "CALIBRATED":
        print(f"  Variant A + Platt Calib : Brier = {cal_brier:.4f}, BSS = {cal_bss:.4f}, ROC = {cal_roc:.4f}, PR = {cal_pr:.4f}, Mean P = {np.mean(cal_eval_probs):.4f}")
    else:
        print(f"  Variant A + Platt Calib : {cal_status}")
    print(f"  Variant B (Unweighted)  : Brier = {unweighted_brier:.4f}, BSS = {unweighted_bss:.4f}, ROC = {unweighted_roc:.4f}, PR = {unweighted_pr:.4f}, Mean P = {np.mean(unweighted_eval_probs):.4f}")
