"""
Phase 7B Data Leakage & Temporal Integrity Tests.

Verifies:
1. Feature at date T cannot depend on rainfall after T.
2. Target after T cannot appear in features.
3. Block information is not leaked across blocks.
4. Evaluation-year information is not used during training in LOYO splits.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.historical.dataset_builder import HistoricalDatasetBuilder
from app.prediction.dataset_builder import PredictionDatasetBuilder
from app.ml.baseline_predictor import LogisticRegressionBaseline, BASELINE_FEATURE_COLUMNS
from app.ml.multiyear_validation import MultiYearScientificValidator


def _generate_synthetic_monsoon_raw(block_id="BLK_TEST", start_date="2024-06-01", n_days=60, seed=42):
    np.random.seed(seed)
    dates = pd.date_range(start=start_date, periods=n_days, freq="D")
    rainfall = np.random.exponential(scale=10.0, size=n_days)
    rainfall[rainfall < 2.0] = 0.0  # Dry days
    return pd.DataFrame({
        "block_id": block_id,
        "date": dates.strftime("%Y-%m-%d"),
        "rainfall_mm": np.round(rainfall, 2),
        "source": "SYNTHETIC_AUDIT_FIXTURE"
    })


def _build_full_prediction_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    hist_builder = HistoricalDatasetBuilder()
    res = hist_builder.build_from_source(raw_df)
    hist_df = res["dataframe"]
    pred_builder = PredictionDatasetBuilder()
    return pred_builder.build_prediction_dataset(hist_df)


def test_feature_at_T_cannot_depend_on_rainfall_after_T():
    """
    Proves that mutating future rainfall at dates t > T has ZERO effect
    on any feature value computed at date T.
    """
    raw_base = _generate_synthetic_monsoon_raw(n_days=50, seed=123)
    pred_base = _build_full_prediction_df(raw_base)

    target_idx = 25
    test_date = pred_base.iloc[target_idx]["prediction_date"]
    row_base = pred_base[pred_base["prediction_date"] == test_date].iloc[0]

    # Mutate raw rainfall strictly on dates AFTER test_date
    raw_mutated = raw_base.copy()
    future_mask = pd.to_datetime(raw_mutated["date"]) > pd.to_datetime(test_date)
    raw_mutated.loc[future_mask, "rainfall_mm"] = 250.0  # Extreme deluge in future

    pred_mutated = _build_full_prediction_df(raw_mutated)
    row_mutated = pred_mutated[pred_mutated["prediction_date"] == test_date].iloc[0]

    # Check all baseline feature columns
    for feat in BASELINE_FEATURE_COLUMNS:
        val_base = row_base[feat]
        val_mut = row_mutated[feat]
        if pd.isna(val_base):
            assert pd.isna(val_mut), f"Feature {feat} mismatch on NaN: {val_base} vs {val_mut}"
        else:
            assert np.isclose(float(val_base), float(val_mut), atol=1e-4), (
                f"LEAKAGE DETECTED in feature '{feat}' at date {test_date}! "
                f"Base={val_base}, After future mutation={val_mut}"
            )


def test_target_after_T_cannot_accidentally_appear_in_features():
    """
    Verifies that target labels do not contaminate feature sets.
    """
    # 1. Column name check
    for feat in BASELINE_FEATURE_COLUMNS:
        assert not feat.startswith("target_"), f"Target column '{feat}' found in BASELINE_FEATURE_COLUMNS!"
        assert "false_onset" not in feat or "days_since" in feat, (
            f"Future target contaminated feature name: {feat}"
        )

    # 2. Functional check: Features and targets must be strictly disjoint sets
    raw_df = _generate_synthetic_monsoon_raw(n_days=45, seed=456)
    pred_df = _build_full_prediction_df(raw_df)

    feature_cols = [c for c in BASELINE_FEATURE_COLUMNS if c in pred_df.columns]
    target_cols = [c for c in pred_df.columns if c.startswith("target_")]

    assert len(target_cols) > 0, "No target columns produced in prediction dataset"
    assert set(feature_cols).isdisjoint(set(target_cols)), (
        f"Intersection between features and targets: {set(feature_cols) & set(target_cols)}"
    )


def test_block_information_not_leaked_across_blocks():
    """
    Proves that mutating observations in Block B cannot change features in Block A.
    """
    raw_a = _generate_synthetic_monsoon_raw(block_id="BLK_A", n_days=40, seed=1)
    raw_b = _generate_synthetic_monsoon_raw(block_id="BLK_B", n_days=40, seed=2)
    raw_combined = pd.concat([raw_a, raw_b], ignore_index=True)

    pred_base = _build_full_prediction_df(raw_combined)
    pred_a_base = pred_base[pred_base["block_id"] == "BLK_A"].sort_values("prediction_date").reset_index(drop=True)

    # Mutate Block B completely (inject 500 mm rain every day)
    raw_b_mutated = raw_b.copy()
    raw_b_mutated["rainfall_mm"] = 500.0
    raw_combined_mutated = pd.concat([raw_a, raw_b_mutated], ignore_index=True)

    pred_mutated = _build_full_prediction_df(raw_combined_mutated)
    pred_a_mutated = pred_mutated[pred_mutated["block_id"] == "BLK_A"].sort_values("prediction_date").reset_index(drop=True)

    # Features in Block A must be strictly identical
    for feat in BASELINE_FEATURE_COLUMNS:
        if feat in pred_a_base.columns:
            s_base = pred_a_base[feat]
            s_mut = pred_a_mutated[feat]
            diff = (s_base - s_mut).dropna()
            assert np.all(np.abs(diff) < 1e-4), f"Cross-block leakage detected in '{feat}'!"


def test_evaluation_year_information_not_used_during_training():
    """
    Verifies that in Leave-One-Year-Out (LOYO) cross-validation,
    the evaluation year data is strictly excluded from training set.
    """
    raw_2021 = _generate_synthetic_monsoon_raw(block_id="BLK1", start_date="2021-06-01", n_days=35, seed=10)
    raw_2022 = _generate_synthetic_monsoon_raw(block_id="BLK1", start_date="2022-06-01", n_days=35, seed=20)
    raw_2023 = _generate_synthetic_monsoon_raw(block_id="BLK1", start_date="2023-06-01", n_days=35, seed=30)

    pred_2021 = _build_full_prediction_df(raw_2021)
    pred_2022 = _build_full_prediction_df(raw_2022)
    pred_2023 = _build_full_prediction_df(raw_2023)

    combined = pd.concat([pred_2021, pred_2022, pred_2023], ignore_index=True)
    combined["year"] = pd.to_datetime(combined["prediction_date"]).dt.year

    # Ensure target has events across years
    combined["target_false_onset_7d"] = 0
    combined.loc[combined["year"] == 2021, "target_false_onset_7d"] = [1 if i % 5 == 0 else 0 for i in range(len(pred_2021))]
    combined.loc[combined["year"] == 2022, "target_false_onset_7d"] = [1 if i % 4 == 0 else 0 for i in range(len(pred_2022))]
    combined.loc[combined["year"] == 2023, "target_false_onset_7d"] = [1 if i % 6 == 0 else 0 for i in range(len(pred_2023))]

    validator = MultiYearScientificValidator()
    results = validator.evaluate_leave_one_year_out(combined, horizon_days=7)

    assert results["validation_status"] == "READY"
    year_results = results["year_wise_results"]
    assert len(year_results) == 3

    for yr_res in year_results:
        eval_year = yr_res["evaluation_year"]
        train_years = yr_res["training_years"]

        # Crucial invariant: Eval year must NEVER be in training years
        assert eval_year not in train_years, (
            f"Evaluation year {eval_year} was leaked into training years {train_years}!"
        )
        assert yr_res["evaluation_rows"] == 35
        assert yr_res["training_rows"] == 70
