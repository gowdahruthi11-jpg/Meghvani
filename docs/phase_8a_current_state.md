# Phase 8A: Current State Audit & Architectural Baseline

## 1. Executive Summary
This document records the exact state of Meghvani's machine learning, calibration, and evaluation framework as established at the completion of Phase 7C, prior to the Phase 8A probability calibration and rolling-origin enhancements.

---

## 2. Current Model Architecture

- **Implementation**: [`backend/app/ml/baseline_predictor.py`](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/ml/baseline_predictor.py)
- **Model Class**: `LogisticRegressionBaseline`
- **Scikit-Learn Pipeline**:
  1. `SimpleImputer(strategy="median")`
  2. `StandardScaler()`
  3. `LogisticRegression(class_weight="balanced", random_state=42, max_iter=1000)`
- **Class Weighting**:
  - The model currently instantiates `LogisticRegression` with `class_weight="balanced"`.
  - **Mechanisms & Effect**:
    - Target `target_false_onset_7d` is rare (~3.30% positive event prevalence across 2019–2024: 217 positive events out of 6,576 observations).
    - `class_weight="balanced"` weights positive samples by $w_1 = \frac{N}{2 \cdot N_1} \approx \frac{6576}{2 \cdot 217} \approx 15.15$, while negative samples receive $w_0 = \frac{N}{2 \cdot N_0} \approx \frac{6576}{2 \cdot 6359} \approx 0.52$.
    - This artificially inflates the predicted probabilities $P(Y=1)$ towards an average of ~0.35–0.50, distorting marginal calibration and resulting in large squared errors against binary zero targets.

---

## 3. Predictor Features (18 Feature Columns)

All 18 features are strictly backward-looking at prediction date $T$:
1. `rainfall_mm` — rainfall observed on date $T$
2. `rainfall_3d` — cumulative 3-day rainfall
3. `rainfall_5d` — cumulative 5-day rainfall
4. `rainfall_7d` — cumulative 7-day rainfall
5. `rainfall_14d` — cumulative 14-day rainfall
6. `rainfall_30d` — cumulative 30-day rainfall
7. `dry_spell_days` — consecutive days with rainfall $< 2.5\text{ mm}$
8. `wet_spell_days` — consecutive days with rainfall $\ge 2.5\text{ mm}$
9. `rainfall_change_3d` — 3-day rainfall change
10. `rainfall_change_7d` — 7-day rainfall change
11. `rainfall_ratio_3d_7d` — ratio of 3d to 7d rainfall
12. `month` — calendar month (1–12)
13. `day_of_year` — calendar day of year (1–366)
14. `monsoon_month_flag` — binary flag (1 for June–September)
15. `days_since_last_onset` — days since preceding onset trigger
16. `days_since_last_break` — days since preceding break episode
17. `days_since_last_heavy_rain` — days since preceding heavy rain ($\ge 65\text{ mm}$)
18. `days_since_last_revival` — days since preceding revival

---

## 4. Current Climatology Baseline

- **Implementation**: [`backend/app/ml/climatology.py`](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/ml/climatology.py)
- **Model Class**: `ClimatologyBaseline`
- **Formula**: Constant prediction $P(Y=1) = \bar{y}_{\text{train}} = \frac{1}{N_{\text{train}}} \sum_{i=1}^{N_{\text{train}}} y_i$.
- **Brier Score of Climatology**: For 7D target, $\bar{y} \approx 0.0319$, yielding Brier score $\approx 0.0319$.

---

## 5. Current Evaluation & Metrics Engine

- **Implementation**: [`backend/app/ml/evaluation.py`](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/ml/evaluation.py)
- **Functions**:
  - `brier_score(y_true, y_prob)`: $\frac{1}{N} \sum_{i=1}^N (p_i - y_i)^2$.
  - `brier_skill_score(brier_model, brier_reference)`: $1 - \frac{\text{Brier}_{\text{model}}}{\text{Brier}_{\text{ref}}}$.
  - `roc_auc_score_safe(y_true, y_prob)`: Safe ROC AUC handling single-class holdouts.
  - `pr_auc_score_safe(y_true, y_prob)`: Safe PR AUC (Average Precision).
  - `compute_calibration_curve(y_true, y_prob, n_bins=10)`: 10-bin reliability analysis.

---

## 6. Current Calibration Framework

- **Implementation**: [`backend/app/ml/calibration.py`](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/ml/calibration.py)
- **Wrapper**: `ProbabilityCalibrator`
- **Supported Methods**:
  - `sigmoid` (Platt scaling via `sklearn.calibration._SigmoidCalibration`)
  - `isotonic` (`sklearn.isotonic.IsotonicRegression(out_of_bounds="clip")`)
- **Limitation in Phase 4A/7B**: Previously tested primarily on single-year intra-season temporal splits where too few positive events existed in calibration periods, triggering `INSUFFICIENT_CALIBRATION_DATA`. Multi-year temporal calibration was not yet integrated into the validation runner.

---

## 7. Current Leave-One-Year-Out (LOYO) Framework

- **Implementation**: [`backend/app/ml/multiyear_validation.py`](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/ml/multiyear_validation.py)
- **Cross-Validation Scheme**: Retrospective Leave-One-Year-Out (LOYO).
  - For each held-out year $Y \in \{2019, 2020, 2021, 2022, 2023, 2024\}$:
    - Train on all other 5 years (including future years relative to $Y$, e.g., 2019 evaluated on 2020–2024).
- **Phase 7C Benchmark Results**:
  - 7D Pooled Raw Brier: 0.1979
  - 7D Climatology Brier: 0.0319
  - 7D Pooled BSS: -5.2030
  - 7D Pooled ROC AUC: 0.6996
  - 7D Pooled PR AUC: 0.0896

---

## 8. Available Historical Data Years

- Sourced from official IMD 0.25° × 0.25° gridded daily rainfall NetCDF files in `data/raw/historical/imd/`.
- **Years**: 2019, 2020, 2021, 2022, 2023, 2024 (6 full calendar years, 2,192 days per block).
- **Blocks**: BLK001 (Nagpur Rural), BLK002 (Wardha East), BLK003 (Amravati Central).
- **Total records**: 6,576 daily rows in `data/processed/historical/multiyear_prediction_dataset.csv`.

---

## 9. Key Limitations to Address in Phase 8A

1. **Retrospective Leakage in LOYO**: While LOYO does not leak evaluation samples into training, training on *future* years (e.g. training on 2024 to predict 2020) does not mimic operational real-time forecasting. A rolling-origin forward-chaining evaluation is required.
2. **Class-Weighting Probability Inflation**: The raw model uses `class_weight="balanced"`, distorting probabilities and degrading Brier score and BSS. We must compare this against an unweighted probability-aligned baseline (`class_weight=None`) and evaluate Platt/Isotonic calibration.
3. **Calibrator/Evaluator Separation**: Calibration must be fitted on temporal periods strictly preceding the evaluation year to prevent data leakage.
