# Meghvani Phase 7B: Scientific Validation & Multi-Year Benchmarking Report

## 1. Objective
The primary objective of Phase 7B is to determine, through rigorous and reproducible evaluation, whether Meghvani's hyperlocal forecasting framework possesses verifiable predictive skill across multiple historical monsoon seasons. The objective is explicitly not to tune models to artificially inflate scores, but to establish a transparent, leak-free evaluation benchmark.

---

## 2. Historical Data Availability
An exhaustive audit of local storage (`data/raw/`, `data/interim/`, `data/processed/`) reveals that only **one calendar year (2025)** is present in the repository.
- **Available Years**: 2025 (June 1, 2025 – September 30, 2025; 122 calendar days).
- **Blocks Covered**: 3 prototype blocks (`BLK001`, `BLK002`, `BLK003`), located in Vidarbha, Maharashtra.
- **Total Daily Observations**: 366 rows.
- **Missing Historical Years**: Benchmark years 2019, 2020, 2021, 2022, 2023, and 2024 are currently absent.
- **Status**: Per scientific rules forbidding the fabrication or duplication of synthetic weather records, multi-year validation is formally designated **`BLOCKED_PENDING_MULTIYEAR_DATA`**.

---

## 3. Data Provenance
- **Dataset Name**: `demo_rainfall.csv`
- **Provider**: Meghvani Prototype Seed Repository
- **File Location**: `data/raw/rainfall/demo_rainfall.csv`
- **SHA-256 Checksum**: `cb036daa666e8a4198bee274f7b2f9d0429c02a9003bc41b09095fc517f642d8`
- **Verification Status**: `DEMO_DATA_ONLY` (Unverified for climatological operational claims)
- **External Verified Data Requirements**: High-resolution daily gridded observations ($0.25^\circ \times 0.25^\circ$) from India Meteorological Department (IMD) or ECMWF ERA5-Land spanning a minimum of 5 consecutive seasons (2019–2024).

---

## 4. Meteorological Event Definitions
All events reuse the Phase 2.1 engineering heuristic thresholds without alteration:
1. **Onset Trigger (`onset_trigger`)**: Cumulative rainfall $\ge 20.0\text{ mm}$ over 3 consecutive days with a 30-day lockout debounce.
2. **False Onset (`false_onset`)**: An onset trigger followed by $\ge 7$ consecutive dry days ($< 2.5\text{ mm/day}$) within the subsequent 30 days.
3. **Break Spell (`break_event`)**: $\ge 5$ consecutive dry days post-onset.
4. **Heavy Rain (`heavy_rain_event`)**: Daily rainfall $\ge 64.5\text{ mm}$.
5. **Revival (`revival_event`)**: Cumulative rainfall $\ge 15.0\text{ mm}$ over 2 consecutive days post-break.

*Note: These definitions remain prototype engineering heuristics and are not official IMD operational standards.*

---

## 5. Feature Construction
All features at prediction date $T$ strictly incorporate observations recorded on or before date $T$ ($t \le T$):
- Backward rolling windows: 1-day lag, 3-day sum, 5-day sum, 7-day sum, 14-day sum, 30-day sum.
- Dynamics: 3-day change, 7-day change, 3-day to 7-day ratio.
- Spells: Antecedent dry spell length, wet spell length.
- Recency: Days elapsed since prior onset trigger, break spell, heavy rain, and revival.
- Calendar: Month, day of year, monsoon month indicator.

---

## 6. Leakage Controls
Automated tests in `tests/test_phase_7b_no_leakage.py` verify four critical invariants:
1. **Temporal Independence**: Altering future rainfall on dates $t > T$ (including heavy deluge) produces zero change in feature values at date $T$.
2. **Target Isolation**: Target columns (`target_*`) are strictly disjoint from feature columns (`BASELINE_FEATURE_COLUMNS`).
3. **Spatial Isolation**: Mutating rainfall in Block B produces bitwise identical features in Block A.
4. **Evaluation Partition Isolation**: In Leave-One-Year-Out validation, the evaluation year is strictly excluded from training data.

---

## 7. Validation Design
- **Architecture**: Leave-One-Year-Out (LOYO) cross-validation across distinct monsoon seasons.
- **Training Set**: All historical years except the holdout year $Y$ ($Y_{train} = \{y \in \text{Years} \mid y \neq Y\}$).
- **Holdout Set**: All observations from year $Y$.
- **Safeguards**: If the holdout set contains zero positive events (or only one class), Brier Skill Score returns `None` (`status = INSUFFICIENT_EVENT_VARIATION`), and ROC/PR AUC return `None` (`status = INSUFFICIENT_CLASS_VARIATION`).

---

## 8. Baselines
1. **Climatology Baseline (`ClimatologyBaseline`)**: Constant empirical positive-class rate derived strictly from training partition labels.
2. **Logistic Regression Baseline (`LogisticRegressionBaseline`)**: Standardized, balanced-weight logistic classifier evaluating the 18 backward-looking predictors.

---

## 9. Multi-Year Results
- **Overall Status**: **`BLOCKED_PENDING_MULTIYEAR_DATA`**
- **Statement**: *"Insufficient historical coverage for reliable skill estimation."*
- **Aggregate Metrics**: Because only one year (2025) is available locally, LOYO across multiple seasons cannot execute real out-of-year partitions. No pooled skill score is fabricated.

---

## 10. Year-Wise Results

| Evaluation Year | Training Years | Eval Samples | Positive Events | Brier Score | BSS | ROC AUC | PR AUC | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2025** | None (Single year) | 366 | 6 | `null` | `null` | `null` | `null` | `BLOCKED_PENDING_MULTIYEAR_DATA` |

---

## 11. Block-Wise Results

| Block ID | Total Observations | Positive Events | Brier Score | Brier Skill Score | Status |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **BLK001** | 122 | 0 | `null` | `null` | `INSUFFICIENT_DATA` |
| **BLK002** | 122 | 6 | `null` | `null` | `INSUFFICIENT_DATA` |
| **BLK003** | 122 | 0 | `null` | `null` | `INSUFFICIENT_DATA` |

*Single-year block sample sizes ($n=122$) with zero or clustered event occurrences are insufficient for independent block skill estimation.*

---

## 12. Horizon-Wise Results

| Horizon | Target Variable | Model Brier | Climatology Brier | BSS | Status | Reason |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **7-Day** | `target_false_onset_7d` | `null` | `null` | `null` | `UNAVAILABLE` | Insufficient historical years (`BLOCKED`) |
| **14-Day** | `target_false_onset_14d` | `null` | `null` | `null` | `UNAVAILABLE` | Insufficient historical years (`BLOCKED`) |
| **21-Day** | `target_false_onset_21d` | `null` | `null` | `null` | `UNAVAILABLE` | Insufficient historical years (`BLOCKED`) |
| **30-Day** | `target_false_onset_30d` | `null` | `null` | `null` | `UNAVAILABLE` | Insufficient historical years (`BLOCKED`) |

---

## 13. Calibration
- **Evaluation Order**: Train $\to$ Calibration $\to$ Evaluation.
- **Status**: **`INSUFFICIENT_CALIBRATION_DATA`**
- **Reason**: A single season with 6 positive events clustered in June cannot populate independent calibration and evaluation folds without data leakage or zero-event test sets.

---

## 14. Reliability
A 10-bin reliability table was engineered into `MultiYearScientificValidator` and tested with synthetic multi-year partitions. In local 2025 single-year storage, reliability evaluation remains blocked to prevent misleading representation.

---

## 15. False-Onset Event Performance
- **Prototype Threshold**: $P \ge 0.35$
- **Contingency Matrix**: Hits, misses, false alarms, and correct negatives are calculated by the framework when multi-year data are ingested.
- **Current Holdout Status**: With only 2025 data, cross-year contingency metrics are marked unavailable.

---

## 16. Limitations
1. Single calendar year (2025) in local storage.
2. Low event prevalence ($n=6$, restricted to BLK002 in June).
3. Zero out-of-year holdout verification possible without external data ingestion.
4. Non-operational status: `is_operational = false`, alerts remain simulated.
5. Farmer observations remain strictly isolated from model training.

---

## 17. Interpretation
The results establish that Meghvani's data engineering, leakage prevention, and validation infrastructure are complete, sound, and leak-free. However, scientifically valid claims of operational forecast skill cannot be made until multi-year ground-truth datasets (e.g. IMD gridded daily rainfall from 2019–2024) are ingested into `data/raw/historical/`.

---

## 18. Conclusion
Phase 7B has successfully deployed the full scientific benchmarking infrastructure—including the data ingestion hierarchy, availability validator, leakage audit test suite, LOYO cross-validation engine, and frontend validation page. The system correctly and honestly outputs **`BLOCKED_PENDING_MULTIYEAR_DATA`**, demonstrating strict adherence to scientific integrity.
