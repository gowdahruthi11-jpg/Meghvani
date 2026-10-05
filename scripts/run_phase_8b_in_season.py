#!/usr/bin/env python3
"""
Meghvani Phase 8B: In-Season Evaluation Runner.
Executes rolling-origin benchmark restricted to sowing window (25 May to 31 July),
evaluates Constant Climatology, Day-of-Year Climatology, and Persistence baselines,
computes block-bootstrap-by-year 95% confidence intervals,
and writes structured outputs to:
- data/processed/historical/phase_8b_metrics.json
- docs/phase_8b_in_season_report.md
"""
import sys
from pathlib import Path
import json
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ml.in_season_evaluation import InSeasonRollingOriginEvaluator, InSeasonWindow


def run_benchmark():
    print("=" * 70)
    print("MEGHVANI PHASE 8B: IN-SEASON ROLLING-ORIGIN EVALUATION")
    print("SOWING WINDOW RESTRICTION (25 MAY TO 31 JULY)")
    print("=" * 70)

    evaluator = InSeasonRollingOriginEvaluator()
    results = evaluator.evaluate_in_season_benchmark(
        horizon_days=7,
        calibration_method="sigmoid",
        n_bootstraps=300
    )

    if results.get("status") != "READY":
        print(f"FAILED: {results.get('message')}")
        return 1

    agg = results["aggregate_metrics"]
    sc = results["sample_counts"]
    ess = sc["effective_sample_size"]

    print("\n[1] DATASET & SAMPLE SIZE HONESTY")
    print("-" * 50)
    print(f"Sowing Window            : {results['in_season_window']['start']} to {results['in_season_window']['end']}")
    print(f"Total In-Season Days     : {sc['total_in_season_observations']} across 6 historical seasons")
    print(f"Evaluated Test Samples   : {sc['evaluated_samples_pooled']} (Years 2020–2024, 3 blocks)")
    print(f"Positive False Onsets    : {sc['total_positive_events_in_season']} (In-Season Base Rate: {sc['base_rate'] * 100:.2f}%)")
    print(f"Distinct IMD Grid Cells  : {ess['distinct_imd_grid_cells']} (BLK001: 21.25°N, BLK002: 20.75°N, BLK003: 21.00°N)")
    print(f"Spatial Cross-Correlation: r = {ess['mean_spatial_correlation']}")
    print(f"Temporal Autocorrelation : rho_1 = {ess['mean_temporal_autocorrelation']}")
    print(f"Effective Sample Size    : N_eff = {ess['n_effective']} (vs nominal N = {ess['n_total']})")

    print("\n[2] BENCHMARK COMPARISON TABLE (7-DAY FORWARD HORIZON)")
    print("-" * 75)
    print(f"{'Model Configuration':<28} | {'Brier':<8} | {'BSS':<8} | {'ROC AUC':<8} | {'ECE':<8} | {'95% CI (Brier)':<16}")
    print("-" * 75)

    for m_key, m_name in [
        ("constant_climatology", "Constant Climatology"),
        ("doy_climatology", "Day-of-Year Climatology"),
        ("persistence", "Persistence Baseline"),
        ("variant_a_raw", "Variant A (Balanced Raw)"),
        ("variant_a_calibrated", "Variant A + Platt Calib"),
        ("variant_b_unweighted", "Variant B (Unweighted)")
    ]:
        m = agg[m_key]
        br = f"{m['brier_score']:.4f}"
        bss = f"{m['brier_skill_score_vs_constant_climatology']:.4f}" if m['brier_skill_score_vs_constant_climatology'] is not None else "0.0000"
        roc = f"{m['roc_auc']:.4f}" if m['roc_auc'] is not None else "N/A"
        ece = f"{m['ece']:.4f}" if m['ece'] is not None else "N/A"
        ci = m.get("confidence_intervals_95", {}).get("brier", (None, None))
        ci_str = f"[{ci[0]}, {ci[1]}]" if ci[0] is not None else "N/A"
        print(f"{m_name:<28} | {br:<8} | {bss:<8} | {roc:<8} | {ece:<8} | {ci_str:<16}")

    print("-" * 75)

    print("\n[3] SCIENTIFIC CONCLUSION")
    print("-" * 50)
    print(f"Beats Climatology : {'YES' if results['scientific_conclusion']['beats_climatology'] else 'NO'}")
    print(f"Assessment        : {results['scientific_conclusion']['finding']}")

    # 1. Save JSON
    json_path = PROJECT_ROOT / "data" / "processed" / "historical" / "phase_8b_metrics.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved JSON metrics to: {json_path}")

    # 2. Save Markdown Report
    doc_path = PROJECT_ROOT / "docs" / "phase_8b_in_season_report.md"
    generate_markdown_report(results, doc_path)
    print(f"Saved Markdown report to: {doc_path}")
    print("=" * 70)
    return 0


def generate_markdown_report(res: Dict[str, Any], doc_path: Path):
    agg = res["aggregate_metrics"]
    sc = res["sample_counts"]
    ess = sc["effective_sample_size"]

    md = f"""# Phase 8B: In-Season Probabilistic Forecast Benchmark Report

## 1. Executive Summary
- **Evaluation Window**: Sowing-relevant period strictly restricted to **25 May – 31 July** (configurable in [`config/event_definitions.yaml`](file:///config/event_definitions.yaml)).
- **Historical Seasons**: 6 verified IMD seasons (2019–2024).
- **Evaluated Test Seasons**: 5 rolling-origin forward folds (2020, 2021, 2022, 2023, 2024).
- **Central Scientific Question**: When removing off-season winter/summer dry days, does the machine learning baseline demonstrate genuine positive forecast skill ($BSS > 0$) against meteorological baselines?
- **Plain Conclusion**: **{'THE MODEL BEATS CONSTANT CLIMATOLOGY' if res['scientific_conclusion']['beats_climatology'] else 'THE MODEL DOES NOT BEAT CLIMATOLOGY'}**.

> [!IMPORTANT]
> **Scientific Integrity Finding**: {res['scientific_conclusion']['finding']}

---

## 2. Sample Size & Spatial Autocorrelation Audit

| Metric | Nominal / Evaluated | Notes |
| :--- | :--- | :--- |
| **Total In-Season Sample Days** | `{sc['total_in_season_observations']}` | 68 days × 3 blocks × 6 years |
| **Nominal Evaluated Samples ($N$)** | `{sc['evaluated_samples_pooled']}` | 68 days × 3 blocks × 5 evaluation years |
| **In-Season Positive False Onsets** | `{sc['total_positive_events_in_season']}` | Base rate = `{sc['base_rate'] * 100:.2f}%` |
| **Distinct IMD 0.25° Grid Cells** | `{ess['distinct_imd_grid_cells']}` | `BLK001 (21.25, 79.00)`, `BLK002 (20.75, 78.50)`, `BLK003 (21.00, 77.75)` |
| **Spatial Cross-Correlation ($\bar{{r}}$)** | `{ess['mean_spatial_correlation']}` | High inter-block rainfall correlation |
| **Temporal Autocorrelation ($\rho_1$)** | `{ess['mean_temporal_autocorrelation']}` | Lag-1 daily persistence |
| **Effective Independent Sample Size ($N_{{\\text{{eff}}}}$)** | **`{ess['n_effective']}`** | Inflation factor: `{ess['sample_size_inflation_factor']}` |

---

## 3. In-Season Benchmark Comparison (7-Day Horizon)

| Model Architecture | Brier Score | BSS (vs Constant Clim) | ROC AUC | ECE | 95% CI (Brier) | 95% CI (BSS) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for m_key, m_name in [
        ("constant_climatology", "Constant Climatology (Prior Base Rate)"),
        ("doy_climatology", "Day-of-Year (DOY) Climatology"),
        ("persistence", "Persistence Baseline (Dry-Spell Length)"),
        ("variant_a_raw", "Logistic Baseline: Variant A (Balanced Raw)"),
        ("variant_a_calibrated", "Logistic Baseline: Variant A + Platt Calibrated"),
        ("variant_b_unweighted", "Logistic Baseline: Variant B (Unweighted)")
    ]:
        m = agg[m_key]
        br = f"{m['brier_score']:.4f}"
        bss = f"{m['brier_skill_score_vs_constant_climatology']:.4f}" if m['brier_skill_score_vs_constant_climatology'] is not None else "0.0000"
        roc = f"{m['roc_auc']:.4f}" if m['roc_auc'] is not None else "N/A"
        ece = f"{m['ece']:.4f}" if m['ece'] is not None else "N/A"
        ci_br = m.get("confidence_intervals_95", {}).get("brier", (None, None))
        ci_bss = m.get("confidence_intervals_95", {}).get("bss", (None, None))
        ci_br_str = f"[{ci_br[0]}, {ci_br[1]}]" if ci_br[0] is not None else "N/A"
        ci_bss_str = f"[{ci_bss[0]}, {ci_bss[1]}]" if ci_bss[0] is not None else "N/A"
        md += f"| **{m_name}** | {br} | {bss} | {roc} | {ece} | {ci_br_str} | {ci_bss_str} |\n"

    md += """
---

## 4. Year-by-Year Forward-Chaining Fold Performance

| Evaluation Year | Training Seasons | Calibration Season | Samples | Positives | Constant Clim Brier | DOY Clim Brier | Persist Brier | Calib Model Brier |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
"""
    for yr in res["year_results"]:
        if yr.get("status") == "NO_PRIOR_TRAINING_DATA":
            md += f"| {yr['evaluation_year']} | None (Base) | None | {yr['evaluation_samples']} | {yr['positive_events']} | N/A | N/A | N/A | N/A |\n"
        else:
            md += (
                f"| {yr['evaluation_year']} | {yr['training_years']} | {yr['calibration_period']} | "
                f"{yr['evaluation_samples']} | {yr['positive_events']} | {yr['constant_climatology_brier']:.4f} | "
                f"{yr['doy_climatology_brier']:.4f} | {yr['persistence_brier']:.4f} | {yr['variant_a_cal_brier']:.4f} |\n"
            )

    md += """
---

## 5. Agronomic Implications
1. **Never Claim False Skill**: Off-season days must never be used to inflate forecast skill metrics or artificially suppress Brier score.
2. **Climatology as the Honest Anchor**: For sowing decisions in Vidarbha, long-term historical seasonal timings (DOY climatology) provide an indispensable, robust baseline.
3. **Decision Postures**: Agronomic recommendations must rely on certified institutional rules (ICAR/PDKV) and rainfall accumulation safeguards (e.g. >= 75–100 mm soil profile moisture) rather than uncalibrated raw model probabilities.
"""
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(md)


if __name__ == "__main__":
    sys.exit(run_benchmark())
