# Meghvani Phase 7B: Current Validation State & Baseline Audit

## 1. Executive Summary & Purpose
This document provides an unvarnished, reproducible audit of the meteorological, feature engineering, modeling, and scientific validation assets currently residing in the Meghvani codebase prior to the introduction of Phase 7B multi-year scientific benchmarking infrastructure.

In strict adherence to Phase 7B scientific rules:
- No synthetic years or fabricated historical records are added.
- Existing single-year (2025) data limitations are documented transparently.
- Current validation status is cataloged without artificial tuning or inflated metrics.

---

## 2. Available Historical Data & Coverage

| Attribute | Current Repository Status |
| :--- | :--- |
| **Available Calendar Years** | **1 year only (2025)** |
| **Temporal Range** | `2025-06-01` to `2025-09-30` (122 calendar days) |
| **Blocks Covered** | **3 blocks**: `BLK001`, `BLK002`, `BLK003` |
| **Raw Data Source File** | `data/raw/rainfall/demo_rainfall.csv` |
| **Total Daily Observations** | **366 daily rows** (122 days × 3 blocks) |
| **Primary Variable** | Daily rainfall amount (`rainfall_mm`, units: mm) |
| **Metadata Tag** | `source: DEMO_DATA` |
| **Quality Flags** | `data_quality_flag: GOOD` across all 366 observations |

---

## 3. Rainfall Variables & Derived Antecedent Features

All features computed at prediction date $T$ strictly utilize daily rainfall observations recorded on or before date $T$ ($t \le T$):

1. **Daily Rainfall**: `rainfall_mm` (day $T$ rainfall in mm)
2. **Short-Term Cumulative Windows**:
   - `rainfall_1d`: 1-day lag rainfall
   - `rainfall_3d`: 3-day backward rolling sum ($\sum_{i=0}^2 R_{T-i}$)
   - `rainfall_5d`: 5-day backward rolling sum
   - `rainfall_7d`: 7-day backward rolling sum
   - `rainfall_14d`: 14-day backward rolling sum
   - `rainfall_30d`: 30-day backward rolling sum
3. **Dry & Wet Spells**:
   - `dry_spell_days`: Consecutive antecedent days with $R < 2.5\text{ mm}$
   - `wet_spell_days`: Consecutive antecedent days with $R \ge 2.5\text{ mm}$
4. **Rainfall Dynamics & Ratios**:
   - `rainfall_change_3d`: 3-day backward change
   - `rainfall_change_7d`: 7-day backward change
   - `rainfall_ratio_3d_7d`: Ratio of 3-day to 7-day rolling totals (bounded $[0, 1]$)
5. **Calendar & Seasonality**:
   - `month`: Numerical month ($1-12$)
   - `day_of_year`: Day of year ($1-366$)
   - `monsoon_month_flag`: Binary indicator ($1$ for June, July, August, September; $0$ otherwise)
6. **Antecedent Event Recency**:
   - `days_since_last_onset`: Days elapsed since prior onset trigger
   - `days_since_last_break`: Days elapsed since prior break spell
   - `days_since_last_heavy_rain`: Days elapsed since prior heavy rain event ($R \ge 64.5\text{ mm}$)
   - `days_since_last_revival`: Days elapsed since prior monsoon revival

---

## 4. Meteorological Event Definitions (Phase 2.1 Heuristics)

*Notice: These are prototype engineering heuristic thresholds and do not represent official India Meteorological Department (IMD) operational meteorological standards.*

1. **Monsoon Onset Trigger (`onset_trigger`)**:
   - Cumulative rainfall $\ge 20.0\text{ mm}$ over a 3-day rolling window (`onset_window_days = 3`).
   - Lockout debounce of 30 days (`onset_lockout_days = 30`) to suppress duplicate triggers during continuous rain.
2. **False Onset (`false_onset`)**:
   - An onset trigger followed by a dry spell $\ge 7\text{ consecutive days}$ ($R < 2.5\text{ mm/day}$) within the subsequent 30 days (`false_onset_lookahead_days = 30`).
3. **Break Spell (`break_event`)**:
   - A sequence of $\ge 5\text{ consecutive dry days}$ ($R < 2.5\text{ mm/day}$) occurring post-onset.
4. **Heavy Rain Event (`heavy_rain_event`)**:
   - Daily rainfall $R \ge 64.5\text{ mm}$ (IMD prototype threshold).
5. **Monsoon Revival (`revival_event`)**:
   - Cumulative rainfall $\ge 15.0\text{ mm}$ over 2 consecutive days (`revival_window_days = 2`) following a detected break spell.

---

## 5. Supervised Target Horizons (Phase 3A)

Target labels strictly evaluate whether a specific event occurs within a forward-looking temporal horizon from prediction date $T$:
- **7-Day Forward Horizon**: `target_false_onset_7d`, `target_onset_7d`, `target_break_7d`, `target_heavy_rain_7d`, `target_revival_7d`
- **14-Day Forward Horizon**: `target_false_onset_14d`, `target_onset_14d`, `target_break_14d`, `target_heavy_rain_14d`, `target_revival_14d`
- **21-Day Forward Horizon**: `target_false_onset_21d`, `target_onset_21d`, `target_break_21d`, `target_heavy_rain_21d`, `target_revival_21d`
- **30-Day Forward Horizon**: `target_false_onset_30d`, `target_onset_30d`, `target_break_30d`, `target_heavy_rain_30d`, `target_revival_30d`

Current primary modeling target is **`target_false_onset_7d`**.

---

## 6. Current Baseline Models & Probability Calibration

1. **Climatology Baseline (`ClimatologyPredictor`)**:
   - Outputs the empirical historical prevalence of the positive class ($P(Y=1)$) computed strictly from training split data.
2. **Logistic Regression Baseline (`LogisticRegressionBaseline`)**:
   - Median feature imputation + StandardScaler + Logistic Regression with balanced class weighting.
   - Evaluated on 18 backward-looking predictors.
3. **Probability Calibration Framework (`ProbabilityCalibrator`)**:
   - Platt (Sigmoid) scaling and Isotonic Regression wrappers.
   - Requires strict temporal partitioning: Train $\to$ Calibration $\to$ Evaluation.
   - **Current Status**: Marked `INSUFFICIENT_CALIBRATION_DATA` because the 2025 dataset does not contain sufficient positive events across the temporal split to fit a reliable calibration mapping.

---

## 7. Current Evaluation Methods & Integrity Safeguards

1. **Chronological Train/Test Split**:
   - Training period: `2025-06-01` to `2025-08-24` (85 calendar days, 255 rows).
   - Holdout evaluation period: `2025-08-25` to `2025-09-30` (37 calendar days, 111 rows).
2. **Diagnostic Evaluation Split**:
   - Evaluates diagnostic discrimination capacity on historical records containing false onsets vs non-events.
3. **Single-Class Safeguards**:
   - In chronological test period (Aug 25 – Sep 30), there are exactly **0 positive false-onset events** (all 6 false onsets occur in early June).
   - The evaluation framework gracefully reports `brier_skill_score = null` with status `INSUFFICIENT_EVENT_VARIATION`.
   - Discrimination metrics (`roc_auc`, `pr_auc`) safely return `"not available"` with status `INSUFFICIENT_CLASS_VARIATION` rather than crashing or fabricating scores.

---

## 8. Current Limitations & Gaps to Address in Phase 7B

1. **Single Year Limitation**: Only 2025 is present; inter-annual monsoon variability (El Niño, La Niña, IOD neutral years) is completely absent.
2. **Small Event Count**: Exactly 6 positive false-onset occurrences across all 3 blocks in 2025, clustered exclusively in June.
3. **Holdout Inadequacy**: Chronological holdout has 0 positive events; skill scores cannot be verified scientifically.
4. **Lack of Ingestion Layer**: No standard multi-year ingestion directory hierarchy, metadata schema, or data availability verification engine.
5. **No Leave-One-Year-Out (LOYO) Framework**: Evaluation across independent monsoon seasons has never been executed.
6. **No Block-wise and Horizon-wise Stratification**: Comprehensive breakdown across all blocks and horizons (7d, 14d, 21d, 30d) is unverified.
7. **System Operational Guardrail**: `is_operational = false`, external dispatch is disabled, and farmer feedback is strictly isolated from model training.
