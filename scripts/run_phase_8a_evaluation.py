"""
Meghvani Phase 8A: Probabilistic Calibration & Rolling-Origin Forecast Evaluation Runner.

Executes:
1. Climatology baseline (strictly prior historical years)
2. Variant A: Existing Raw Baseline (class_weight="balanced")
3. Variant A + Platt (Sigmoid) Calibrated
4. Variant A + Isotonic Calibrated (with small-sample event safeguards)
5. Variant B: Probability-Aligned Baseline (class_weight=None)
6. All horizons: 7D, 14D, 21D, 30D
7. Block breakdowns: BLK001, BLK002, BLK003
8. Reliability diagrams and ECE calculation
9. Persists structured JSON artifact to docs/phase_8a_evaluation_run_output.json
"""
import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ml.rolling_origin import RollingOriginEvaluator


def main():
    print("=" * 70)
    print("MEGHVANI PHASE 8A: PROBABILISTIC CALIBRATION & ROLLING-ORIGIN EVALUATION")
    print("=" * 70)

    evaluator = RollingOriginEvaluator()
    report = evaluator.generate_full_report(calibration_method="sigmoid")

    if report.get("status") != "READY":
        print(f"FAILED: Rolling origin evaluation not ready. Reason: {report.get('message')}")
        return 1

    ds = report["dataset_info"]
    print("\nDATASET & ROLLING-ORIGIN SETUP")
    print("-" * 50)
    print(f"Historical Years Available : {ds['historical_years']}")
    print(f"Monitored Blocks           : {ds['blocks']}")
    print(f"Total Prediction Rows      : {ds['total_rows']}")
    print(f"Primary Calibration Method : {report['primary_calibration_method'].upper()} (Platt scaling)")

    # 1. 7D Aggregate Results across models
    print("\n" + "=" * 70)
    print("7-DAY FORWARD HORIZON: AGGREGATE ROLLING-ORIGIN RESULTS")
    print("=" * 70)
    h7_agg = report["horizons"]["7d"]["aggregate_metrics"]
    print(f"Evaluated Samples : {h7_agg['total_evaluation_samples']} (Positive events: {h7_agg['total_positive_events']})")
    print(f"Evaluated Years   : {h7_agg['evaluation_years_evaluated']}")
    print(f"Climatology Brier : {h7_agg['climatology_brier']:.4f}")
    print("-" * 70)
    print(f"{'Model Configuration':<32} | {'Brier':<8} | {'BSS':<8} | {'ROC AUC':<8} | {'PR AUC':<8} | {'ECE':<8}")
    print("-" * 70)

    raw_a = h7_agg["variant_a_raw"]
    cal_a = h7_agg["variant_a_calibrated"]
    raw_b = h7_agg["variant_b_unweighted"]

    print(f"{'Variant A (Balanced Raw)':<32} | {raw_a['brier_score']:<8.4f} | {raw_a['brier_skill_score']:<8.4f} | {raw_a['roc_auc']:<8.4f} | {raw_a['pr_auc']:<8.4f} | {raw_a['ece']:<8.4f}")
    print(f"{'Variant A + Platt Calibrated':<32} | {cal_a['brier_score']:<8.4f} | {cal_a['brier_skill_score']:<8.4f} | {cal_a['roc_auc']:<8.4f} | {cal_a['pr_auc']:<8.4f} | {cal_a['ece']:<8.4f}")
    print(f"{'Variant B (Probability-Aligned)':<32} | {raw_b['brier_score']:<8.4f} | {raw_b['brier_skill_score']:<8.4f} | {raw_b['roc_auc']:<8.4f} | {raw_b['pr_auc']:<8.4f} | {raw_b['ece']:<8.4f}")
    print("-" * 70)

    # 2. Year-by-Year Forward-Chaining Table (7D Horizon)
    print("\n" + "=" * 70)
    print("YEAR-BY-YEAR ROLLING-ORIGIN FORWARD CHAINING (7-DAY HORIZON)")
    print("=" * 70)
    print(f"{'Eval Yr':<7} | {'Train Yrs':<11} | {'Cal Period':<10} | {'N_eval':<6} | {'Pos':<4} | {'Clim Br':<8} | {'Raw Br':<8} | {'Cal Br':<8} | {'Cal BSS':<8} | {'ROC AUC':<8} | {'Cal Status':<12}")
    print("-" * 105)

    for yr in report["horizons"]["7d"]["year_results"]:
        y_eval = yr["evaluation_year"]
        status = yr.get("status")
        if status == "NO_PRIOR_TRAINING_DATA":
            print(f"{y_eval:<7} | {'(None)':<11} | {'(None)':<10} | {yr['evaluation_rows']:<6} | {yr['positive_events']:<4} | {'N/A':<8} | {'N/A':<8} | {'N/A':<8} | {'N/A':<8} | {'N/A':<8} | {'NO_PRIOR_TRAIN':<12}")
            continue

        train_str = ",".join(str(y)[2:] for y in yr["training_years"])
        cal_str = ",".join(str(y)[2:] for y in yr["calibration_years"]) if yr["calibration_years"] else "None"
        clim_br = yr["climatology"]["brier_score"]
        raw_br = yr["variant_a_raw"]["brier_score"]
        cal_br = yr["variant_a_calibrated"]["brier_score"] if yr["variant_a_calibrated"]["brier_score"] is not None else "N/A"
        cal_bss = yr["variant_a_calibrated"]["brier_skill_score"] if yr["variant_a_calibrated"]["brier_skill_score"] is not None else "N/A"
        roc = yr["variant_a_calibrated"]["roc_auc"] if yr["variant_a_calibrated"]["roc_auc"] is not None else yr["variant_a_raw"]["roc_auc"]
        c_status = yr["variant_a_calibrated"]["calibration_status"]

        print(f"{y_eval:<7} | {train_str:<11} | {cal_str:<10} | {yr['evaluation_rows']:<6} | {yr['positive_events']:<4} | {clim_br:<8.4f} | {raw_br:<8.4f} | {cal_br if isinstance(cal_br, str) else f'{cal_br:.4f}':<8} | {cal_bss if isinstance(cal_bss, str) else f'{cal_bss:.4f}':<8} | {roc if isinstance(roc, str) else f'{roc:.4f}':<8} | {c_status:<12}")
    print("-" * 105)

    # 3. All Horizons Summary
    print("\n" + "=" * 70)
    print("ALL FORWARD HORIZONS SUMMARY (POOLED ROLLING-ORIGIN)")
    print("=" * 70)
    print(f"{'Horizon':<8} | {'Clim Brier':<11} | {'Raw A Brier':<11} | {'Raw A BSS':<10} | {'Cal A Brier':<11} | {'Cal A BSS':<10} | {'ROC AUC':<8} | {'PR AUC':<8}")
    print("-" * 88)
    for h in ["7d", "14d", "21d", "30d"]:
        h_agg = report["horizons"][h]["aggregate_metrics"]
        c_br = h_agg["climatology_brier"]
        ra = h_agg["variant_a_raw"]
        ca = h_agg["variant_a_calibrated"]
        print(f"{h.upper():<8} | {c_br:<11.4f} | {ra['brier_score']:<11.4f} | {ra['brier_skill_score']:<10.4f} | {ca['brier_score']:<11.4f} | {ca['brier_skill_score']:<10.4f} | {ca['roc_auc']:<8.4f} | {ca['pr_auc']:<8.4f}")
    print("-" * 88)

    # 4. Block Breakdown Summary
    print("\n" + "=" * 70)
    print("BLOCK-LEVEL STRATIFICATION (7-DAY HORIZON)")
    print("=" * 70)
    print(f"{'Block ID':<8} | {'Samples':<8} | {'Pos':<5} | {'Clim Br':<8} | {'Raw A Br':<9} | {'Cal A Br':<9} | {'Cal A BSS':<10} | {'ROC AUC':<8}")
    print("-" * 75)
    for blk_id, b_info in report["blocks"].items():
        agg = b_info.get("aggregate_metrics")
        if agg:
            c_br = agg["climatology_brier"]
            ra_br = agg["variant_a_raw"]["brier_score"]
            ca_br = agg["variant_a_calibrated"]["brier_score"]
            ca_bss = agg["variant_a_calibrated"]["brier_skill_score"]
            roc = agg["variant_a_calibrated"]["roc_auc"]
            print(f"{blk_id:<8} | {b_info['samples']:<8} | {b_info['positive_events']:<5} | {c_br:<8.4f} | {ra_br:<9.4f} | {ca_br:<9.4f} | {ca_bss:<10.4f} | {roc:<8.4f}")
    print("-" * 75)

    # Save artifact
    out_path = PROJECT_ROOT / "docs" / "phase_8a_evaluation_run_output.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nPersisted complete Phase 8A evaluation run output to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
