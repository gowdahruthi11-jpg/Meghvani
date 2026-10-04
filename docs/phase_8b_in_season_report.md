# Phase 8B: In-Season Probabilistic Forecast Benchmark Report

## 1. Executive Summary
- **Evaluation Window**: Sowing-relevant period strictly restricted to **25 May – 31 July** (configurable in [`config/event_definitions.yaml`](file:///config/event_definitions.yaml)).
- **Historical Seasons**: 6 verified IMD seasons (2019–2024).
- **Evaluated Test Seasons**: 5 rolling-origin forward folds (2020, 2021, 2022, 2023, 2024).
- **Central Scientific Question**: When removing off-season winter/summer dry days, does the machine learning baseline demonstrate genuine positive forecast skill ($BSS > 0$) against meteorological baselines?
- **Plain Conclusion**: **THE MODEL DOES NOT BEAT CLIMATOLOGY**.

> [!IMPORTANT]
> **Scientific Integrity Finding**: In the sowing window (25 May – 31 July), the baseline logistic regression model DOES NOT reliably beat Day-of-Year climatology. False onsets are predominantly driven by synoptic intra-seasonal pauses (e.g. MJO phase, monsoon trough stagnation) which local 14-day antecedent rainfall features cannot capture. Climatology and persistence are strong, competitive baselines in smallholder agrometeorology.

---

## 2. Sample Size & Spatial Autocorrelation Audit

| Metric | Nominal / Evaluated | Notes |
| :--- | :--- | :--- |
| **Total In-Season Sample Days** | `1224` | 68 days × 3 blocks × 6 years |
| **Nominal Evaluated Samples ($N$)** | `1020` | 68 days × 3 blocks × 5 evaluation years |
| **In-Season Positive False Onsets** | `7` | Base rate = `0.69%` |
| **Distinct IMD 0.25° Grid Cells** | `3` | `BLK001 (21.25, 79.00)`, `BLK002 (20.75, 78.50)`, `BLK003 (21.00, 77.75)` |
| **Spatial Cross-Correlation ($ar{r}$)** | `0.6226` | High inter-block rainfall correlation |
| **Temporal Autocorrelation ($ho_1$)** | `0.2855` | Lag-1 daily persistence |
| **Effective Independent Sample Size ($N_{\text{eff}}$)** | **`303`** | Inflation factor: `4.04` |

---

## 3. In-Season Benchmark Comparison (7-Day Horizon)

| Model Architecture | Brier Score | BSS (vs Constant Clim) | ROC AUC | ECE | 95% CI (Brier) | 95% CI (BSS) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Constant Climatology (Prior Base Rate)** | 0.0096 | 0.0000 | 0.7014 | 0.0455 | [0.0023, 0.0233] | [0.0, 0.0] |
| **Day-of-Year (DOY) Climatology** | 0.0194 | -1.0237 | 0.3779 | 0.0455 | [0.0077, 0.0374] | [-1.3496, -0.3758] |
| **Persistence Baseline (Dry-Spell Length)** | 0.0096 | 0.0000 | 0.5077 | 0.0336 | [0.0025, 0.0232] | [-0.1005, 0.0931] |
| **Logistic Baseline: Variant A (Balanced Raw)** | 0.1271 | -12.2250 | 0.0608 | 0.1614 | [0.0568, 0.2101] | [-17.5178, -5.0157] |
| **Logistic Baseline: Variant A + Platt Calibrated** | 0.1273 | -12.2511 | 0.0597 | 0.1625 | [0.057, 0.2102] | [-17.5332, -5.029] |
| **Logistic Baseline: Variant B (Unweighted)** | 0.1421 | -13.7861 | 0.0804 | 0.1509 | [0.0293, 0.2834] | [-22.9769, -3.0089] |

---

## 4. Year-by-Year Forward-Chaining Fold Performance

| Evaluation Year | Training Seasons | Calibration Season | Samples | Positives | Constant Clim Brier | DOY Clim Brier | Persist Brier | Calib Model Brier |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 2019 | None (Base) | None | 204 | 21 | N/A | N/A | N/A | N/A |
| 2020 | [2019] | None | 204 | 0 | 0.0106 | 0.0421 | 0.0075 | 0.2064 |
| 2021 | [2019] | [2020] | 204 | 7 | 0.0334 | 0.0444 | 0.0353 | 0.1468 |
| 2022 | [2019, 2020] | [2021] | 204 | 0 | 0.0021 | 0.0056 | 0.0026 | 0.0013 |
| 2023 | [2019, 2020, 2021] | [2022] | 204 | 0 | 0.0012 | 0.0031 | 0.0015 | 0.2501 |
| 2024 | [2019, 2020, 2021, 2022] | [2023] | 204 | 0 | 0.0008 | 0.0020 | 0.0012 | 0.0321 |

---

## 5. Agronomic Implications
1. **Never Claim False Skill**: Off-season days must never be used to inflate forecast skill metrics or artificially suppress Brier score.
2. **Climatology as the Honest Anchor**: For sowing decisions in Vidarbha, long-term historical seasonal timings (DOY climatology) provide an indispensable, robust baseline.
3. **Decision Postures**: Agronomic recommendations must rely on certified institutional rules (ICAR/PDKV) and rainfall accumulation safeguards (e.g. >= 75–100 mm soil profile moisture) rather than uncalibrated raw model probabilities.
