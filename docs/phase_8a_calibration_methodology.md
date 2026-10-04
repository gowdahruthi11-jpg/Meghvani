# Meghvani Phase 8A: Probabilistic Calibration & Rolling-Origin Forecast Evaluation Methodology

## 1. Objective
The primary objective of Phase 8A is to scientifically investigate and correct the probability calibration failures identified in Phase 7C, while establishing a forward-chaining rolling-origin evaluation paradigm across the multi-year IMD gridded rainfall record (2019–2024) for blocks BLK001, BLK002, and BLK003.

In Phase 7C, the retrospective pooled 7-day baseline yielded:
- Model Brier Score: 0.1979
- Climatology Brier Score: 0.0319
- Brier Skill Score (BSS): -5.2030
- ROC AUC: 0.6996
- PR AUC: 0.0896

The goal is not to artificially tune models to produce positive skill, but to determine whether probability alignment and temporal calibration eliminate the severe Brier penalty caused by base-rate distortion, and to assess whether honest forward-chaining forecasts provide predictive value beyond climatology.

---

## 2. Why Calibration Is Needed
In binary forecasting of rare meteorological and agro-climatic events (e.g. false onset of monsoon occurring on only ~3.25% of eligible days), a model's raw output probabilities can be severely distorted even when the model possesses positive discrimination ability (ROC AUC ~0.60–0.83). 

When raw probabilities center around 25%–50% for events whose true frequency is ~3.3%, the mean squared probability error $(P - Y)^2$ heavily penalizes the model:
$$(0.40 - 0)^2 = 0.16 \quad \text{vs.} \quad (0.033 - 0)^2 \approx 0.0011$$
Consequently, an uncalibrated model exhibits a Brier Score 5–6 times worse than a simple naive climatological forecast ($BSS < -5.0$), rendering the probabilities unusable for operational risk estimation. Probability calibration maps uncalibrated scores to empirical probabilities matching true event likelihoods without altering score ranking.

---

## 3. Raw Probability Definition
Raw probability $P_{\text{raw}}(Y=1 \mid X)$ is defined as the direct output of the logistic sigmoid link function applied to the linear predictor:
$$P_{\text{raw}}(Y=1 \mid X) = \frac{1}{1 + \exp\left(-(\beta_0 + \sum_{j=1}^p \beta_j X_j)\right)}$$
In Phase 1–7C, the model was fitted using `class_weight="balanced"`. This variant is designated:
$$\textbf{Variant A (Existing Raw Baseline)}$$
Under `class_weight="balanced"`, the loss function weights positive instances by $w_1 = \frac{N}{2 N_1} \approx 15.4$ and negative instances by $w_0 = \frac{N}{2 N_0} \approx 0.52$. This shifts the intercept $\beta_0$ upwards, forcing the average predicted probability towards 50% regardless of the true climatological base rate.

---

## 4. Class Weighting Investigation
To isolate the impact of balanced class weights from intrinsic model predictive power, Phase 8A introduces an explicit secondary variant:
$$\textbf{Variant B (Probability-Aligned Baseline)}$$
- Model formulation: `LogisticRegressionBaseline(class_weight=None)`
- Features and solver identical to Variant A (L-BFGS, standard scaled features).
- The loss function treats all historical observations equally, preserving the natural base rate in the fitted intercept.

Comparison across the 2020–2024 rolling evaluation demonstrates:
- Variant A Raw 7D Brier: **0.1841** (BSS = -4.8555; ECE = 23.70%)
- Variant B Unweighted 7D Brier: **0.0473** (BSS = -0.5030; ECE = 4.79%)
- Variant A + Platt Calibrated 7D Brier: **0.0373** (BSS = -0.1860; ECE = 1.87%)

This confirms the hypothesis: the massive negative BSS (-5.20 in Phase 7C) was overwhelmingly driven by the intercept distortion of `class_weight="balanced"`.

---

## 5. Calibration Methods
Two calibration algorithms are implemented in `app.ml.calibration.ProbabilityCalibrator`:

### A. Platt Scaling (Sigmoid Calibration)
Fits a univariate logistic transformation over the raw model probabilities:
$$P_{\text{cal}}(Y=1 \mid P_{\text{raw}}) = \frac{1}{1 + \exp(A \cdot P_{\text{raw}} + B)}$$
Parameters $A$ and $B$ are estimated via maximum likelihood on a held-out temporal calibration set. Because Platt scaling has only 2 parameters, it is robust against overfitting on moderate sample sizes ($N \sim 1,000$).

### B. Guarded Isotonic Regression
Fits a non-parametric isotonic (monotonically non-decreasing) step function:
$$P_{\text{cal}} = \arg\min_{m \in \mathcal{M}} \sum_{i} (y_i - m(P_{\text{raw}, i}))^2$$
**Safeguard**: Isotonic regression requires sufficient sample size and event variation to prevent degenerate single-step or staircase overfitting. In Meghvani, isotonic calibration is rejected with status `INSUFFICIENT_EVENT_VARIATION` unless the calibration split contains at least **10 positive events** ($N_{\text{pos, cal}} \ge 10$).

---

## 6. Temporal Calibration Design
Cross-validation or random K-fold splits are strictly prohibited for time-series forecasting calibration due to autocorrelation and future-data leakage. 

For each rolling-origin evaluation cycle:
1. Available historical record prior to evaluation year $T_{\text{eval}}$ is partitioned chronologically into:
   - **Training Set**: Earlier historical years $[T_0, \dots, T_{\text{cal}-1}]$
   - **Calibration Set**: The most recent complete historical season $[T_{\text{cal}}]$ preceding $T_{\text{eval}}$.
2. For $T_{\text{eval}} = 2020$: Only 2019 exists. Since no separate calibration year is available, calibration status is set to `INSUFFICIENT_CALIBRATION_DATA`. Raw probabilities and climatology are evaluated.
3. For $T_{\text{eval}} = 2021$: Train = 2019, Cal = 2020.
4. For $T_{\text{eval}} = 2022$: Train = 2019–2020, Cal = 2021.
5. For $T_{\text{eval}} = 2023$: Train = 2019–2021, Cal = 2022.
6. For $T_{\text{eval}} = 2024$: Train = 2019–2022, Cal = 2023.

---

## 7. Rolling-Origin Design
Rolling-origin (forward-chaining) evaluation simulates genuine operational conditions:
- Models are trained strictly on past observed years.
- The evaluation year $T_{\text{eval}}$ is held out completely.
- Climatology is re-computed strictly from the training period $[T_0, \dots, T_{\text{eval}-1}]$; it never includes $T_{\text{eval}}$.
- Year 2019 has status `NO_PRIOR_TRAINING_DATA` as forward forecasting requires prior historical records.

---

## 8. Brier Score Methodology
The binary Brier Score measures mean squared error between forecast probability $p_i \in [0, 1]$ and binary outcome $y_i \in \{0, 1\}$:
$$\text{BS} = \frac{1}{N} \sum_{i=1}^N (p_i - y_i)^2$$
Range: $[0, 1]$, where 0 is perfect deterministic skill.

---

## 9. Brier Skill Score (BSS) Methodology
The Brier Skill Score measures the percentage improvement in Brier Score over a reference climatology baseline:
$$\text{BSS} = 1 - \frac{\text{BS}_{\text{model}}}{\text{BS}_{\text{climatology}}}$$
- $\text{BSS} > 0$: Model outperforms historical climatology.
- $\text{BSS} = 0$: Model performs identically to climatology.
- $\text{BSS} < 0$: Model performs worse than climatology (negative skill).
Negative BSS is never clipped to zero. If $\text{BS}_{\text{climatology}} == 0$, $\text{BSS}$ is recorded as `null` with explicit diagnostic metadata.

---

## 10. Reliability Analysis
Forecasts are partitioned into 10 uniform probability bins $[0.0, 0.1), [0.1, 0.2), \dots, [0.9, 1.0]$.
For each bin $k$:
- Number of forecasts: $N_k$
- Mean predicted probability: $\bar{p}_k = \frac{1}{N_k} \sum_{i \in B_k} p_i$
- Observed event frequency: $\bar{y}_k = \frac{1}{N_k} \sum_{i \in B_k} y_i$
For bins with $N_k = 0$, values are reported as `null` without fabrication.

---

## 11. Expected Calibration Error (ECE)
Expected Calibration Error weights the absolute difference between predicted probability and empirical frequency by bin sample size:
$$\text{ECE} = \sum_{k=1}^K \frac{N_k}{N} |\bar{p}_k - \bar{y}_k|$$
This provides a single interpretable metric reflecting the average calibration discrepancy.

---

## 12. ROC AUC and PR AUC Interpretation
- **ROC AUC** (Receiver Operating Characteristic Area Under Curve) measures ranking discrimination across all false-positive rates.
- **PR AUC** (Precision-Recall Area Under Curve) evaluates precision across recall thresholds, crucial for heavily imbalanced classes.
- **Crucial Scientific Distinction**: ROC AUC and PR AUC measure **DISCRIMINATION**, not calibration or forecast accuracy. Because monotonic calibration does not change sample rank order, ROC AUC remains largely unchanged after Platt scaling. Unchanged ROC AUC is expected and does not indicate calibration failure.

---

## 13. Leakage Controls
1. **Target Exclusion**: Features never include $T_{\text{eval}}$ rainfall, cumulative future rainfall, or target labels.
2. **Temporal Isolation**: Evaluated seasons never participate in parameter estimation, feature standardizer fitting, intercept fitting, or calibration mapping.
3. **Climatology Isolation**: The climatological baseline reference is computed strictly from pre-evaluation historical records.
4. **Farmer Observation Firewall**: Farmer observations and feedback loop records remain quarantined in `farmer_feedback.db` and are never fed into ML model retraining.

---

## 14. Limitations
1. **Small Positive Sample Size**: Across 2019–2024, only 217 positive 7D false-onset events occurred across all 3 blocks (out of 6,576 sample days, ~3.3%).
2. **Horizon Degradation**: Beyond 7 days (14D, 21D, 30D), ROC AUC declines towards 0.50 and 0.46, indicating that current 14-day antecedent rainfall features contain little predictive signal for multi-week false onsets.
3. **Operational Boundary**: System flag `is_operational = false` is strictly maintained. These results represent scientific benchmarking and are not approved for operational alert dispatch.
