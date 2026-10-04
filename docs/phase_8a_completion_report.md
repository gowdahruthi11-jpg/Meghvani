# Phase 8A Completion Report

## Status
COMPLETE

## Objective
The objective of Phase 8A was to:
1. Determine whether poor Brier performance in Phase 7C ($BSS = -5.2030$) was primarily caused by probability calibration / class weighting (`class_weight="balanced"` shifting base rates away from ~3.3%).
2. Implement scientifically valid probability calibration (Platt/Sigmoid scaling and guarded Isotonic regression).
3. Introduce rolling-origin / forward-chaining evaluation representing genuine real-time operational forecasting conditions.
4. Compare Climatology, Existing Raw Baseline (Variant A), Calibrated Logistic Baseline, and Probability-Aligned Baseline (Variant B).
5. Preserve all existing scientific boundaries without modifying the 2025 demo dataset or fabricating metrics.

## Data
- **Years**: 2019, 2020, 2021, 2022, 2023, 2024 (6 historical monsoon seasons)
- **Source**: India Meteorological Department (IMD) 0.25° × 0.25° daily gridded rainfall dataset
- **Blocks**: 3 blocks in Vidarbha, Maharashtra
  - BLK001 (Kalmeshwar)
  - BLK002 (Katol)
  - BLK003 (Saoner)
- **Total station-days**: 6,576
- **Total 7-day positive false-onset events**: 217 (~3.30% base rate)

## Raw Baseline
- Model: `LogisticRegressionBaseline(class_weight="balanced")` (Variant A)
- Evaluation Setup: Rolling-origin forward-chaining (2020–2024, $N = 5,481$)
- **Raw 7D Brier Score**: 0.1841
- **Climatology 7D Brier Score**: 0.0314
- **Raw 7D Brier Skill Score (BSS)**: -4.8555
- **Raw 7D ROC AUC**: 0.5957 (Discrimination metric)
- **Raw 7D PR AUC**: 0.0809 (Discrimination metric)
- **Raw Expected Calibration Error (ECE)**: 0.2370 (23.70%)
- **Mean Predicted Probability**: 0.2527 (vs 0.0325 true base rate)

## Calibration
- **Primary Method**: Platt Scaling (Sigmoid univariate calibration fitted via maximum likelihood on chronological calibration year)
- **Secondary Safeguarded Method**: Isotonic Regression (guarded by rule: requires $\ge 10$ positive events in calibration split to prevent step-function overfitting)
- **Status Across Years**:
  - 2019: `NO_PRIOR_TRAINING_DATA` (no prior training seasons)
  - 2020: `INSUFFICIENT_CALIBRATION_DATA` (single prior year used for training; no separate calibration year)
  - 2021–2024: `CALIBRATED`
- **Method Comparison**:
  - Platt (Sigmoid): Aggregate 7D Brier = **0.0373**, BSS = **-0.1860**, ECE = **0.0187 (1.87%)**
  - Isotonic: Aggregate 7D Brier = **0.0393**, BSS = **-0.2512**, ECE = **0.0269 (2.69%)**
  - *Conclusion*: Platt scaling outperforms Isotonic on small-sample meteorological calibration splits.

## Rolling-Origin
- **Evaluation Paradigm**: Forward-chaining rolling origin
  - Evaluation 2020: Train = 2019 (Cal = None)
  - Evaluation 2021: Train = 2019, Cal = 2020
  - Evaluation 2022: Train = 2019–2020, Cal = 2021
  - Evaluation 2023: Train = 2019–2021, Cal = 2022
  - Evaluation 2024: Train = 2019–2022, Cal = 2023
- **Leakage Controls**:
  - Evaluation year never enters feature scaling, model fitting, calibration fitting, or threshold selection.
  - Climatology baseline computed strictly from training seasons prior to evaluation year.
  - Farmer observations strictly quarantined from model retraining.

## Brier Results
| Horizon | Climatology Brier | Variant A Raw Brier | Variant A Calib Brier | Variant B Aligned Brier |
|:---:|:---:|:---:|:---:|:---:|
| **7 Days** | 0.0314 | 0.1841 | **0.0373** | 0.0473 |
| **14 Days** | 0.0604 | 0.2186 | **0.0669** | 0.0952 |
| **21 Days** | 0.0876 | 0.2542 | **0.0982** | 0.1294 |
| **30 Days** | 0.1199 | 0.2924 | **0.1395** | 0.1685 |

## BSS Results
| Horizon | Raw BSS (Variant A) | Calibrated BSS (Variant A) | Variant B BSS (Aligned) |
|:---:|:---:|:---:|:---:|
| **7 Days** | -4.8555 | **-0.1860** (Individual years: 2023 = **+0.0007**, 2024 = **+0.0234**) | -0.5030 |
| **14 Days** | -2.6175 | **-0.1067** | -0.5750 |
| **21 Days** | -1.9011 | **-0.1209** | -0.4764 |
| **30 Days** | -1.4396 | **-0.1643** | -0.4053 |

*Note: All negative BSS values are preserved without clipping.*

## Reliability
- **Raw Model Reliability**: Displays severe systematic overconfidence across all bins. In bin [0.9–1.0], predicted probability is 97.02% but observed event frequency is only 5.68%.
- **Calibrated Model Reliability**: 5,372 out of 5,481 predictions are mapped into bin [0.0–0.1] with mean probability 2.31% matching observed frequency of 3.18%. For high-confidence bin [0.9–1.0], observed frequency rises to 29.17%. Expected Calibration Error drops from 23.70% to 1.87%.

## ROC/PR
*Labeled as DISCRIMINATION METRICS (not accuracy or probabilistic skill)*
- **7-Day Pooled Discrimination**:
  - Variant A Raw: ROC AUC = 0.5957, PR AUC = 0.0809
  - Variant A Calibrated: ROC AUC = 0.6248, PR AUC = 0.0820
  - Variant B Aligned: ROC AUC = 0.5995, PR AUC = 0.0761
  - Year 2024 Calibrated: ROC AUC = **0.8336**, PR AUC = **0.1130**
  - Year 2022 Calibrated: ROC AUC = **0.7093**, PR AUC = **0.0888**
- **Horizon Degradation**:
  - 14 Days: ROC AUC = 0.5451
  - 21 Days: ROC AUC = 0.5085
  - 30 Days: ROC AUC = 0.4946

## Class Weight Investigation
- Hypothesis confirmed: `class_weight="balanced"` was the dominant driver of catastrophic negative BSS ($BSS < -5.0$).
- Removing balanced class weights (Variant B) directly improved raw BSS from **-4.8555** to **-0.5030** and reduced ECE from **23.70%** to **4.79%**.
- Applying Platt calibration to Variant A achieved the best probabilistic alignment: Brier **0.0373**, BSS **-0.1860**, ECE **1.87%**, while preserving ROC discrimination ($0.6248$).

## Limitations
1. Limited sample of positive false onsets ($N_{\text{pos}} = 217$ across 6 years and 3 blocks, ~3.3%).
2. Beyond 7 days, antecedent rainfall features provide negligible predictive signal (ROC AUC approaches 0.50).
3. Block-disaggregated calibrations exhibit variance due to small sample sizes when calibrated per-block.
4. Multidecadal oceanic-atmospheric indices (ENSO, IOD, MJO) are not yet integrated into the baseline feature set.

## Operational Status
`is_operational = false`  
`external_dispatch = false`  
Results are strictly for research and scientific validation benchmarking. Automated decision dispatch to farmers is not enabled.

## Tests
- **Total Test Suite**: 321 passed / 321 total (100% passing)
- **New Phase 8A Tests**:
  - `tests/test_phase_8a_calibration.py`: 19/19 passed
  - `tests/test_phase_8a_rolling_origin.py`: 10/10 passed
- **Regression**:
  - Phase 7A, 7B, 7C tests pass without regression.
  - Phase 1–6 tests pass without regression.

## System Verification
- `scripts/verify_system.py`: PASSED (exit code 0)
- All foundation subsystems verified: DB seeding, PIN mapping, farmer registration, advisory generation, simulated alert dispatch.

## Frontend Build
- `npm run build`: PASSED (exit code 0)
- Vite build completed in 15.22s, 0 TypeScript errors.
- New UI components verified: Probability Calibration & Rolling-Origin Validation sections with "RESEARCH BENCHMARK — NOT OPERATIONAL" banners.
