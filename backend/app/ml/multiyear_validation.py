"""
Meghvani Phase 7B: Multi-Year Scientific Validation & Benchmarking Engine.

Core Principles:
1. Scientific honesty over high scores: Never fabricate synthetic years or fake metrics.
2. Leave-One-Year-Out (LOYO) cross-validation across distinct monsoon seasons.
3. Strict evaluation safeguards: If evaluation holdout lacks positive events,
   BSS is returned as None (status: INSUFFICIENT_EVENT_VARIATION) and discrimination
   metrics as None (status: INSUFFICIENT_CLASS_VARIATION).
4. If fewer than 2 complete years exist, multi-year validation status is:
   BLOCKED_PENDING_MULTIYEAR_DATA.
5. All metrics preserve block-scale, horizon-scale (7d, 14d, 21d, 30d), and year-wise granularity.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import logging
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score

from app.config import PROJECT_ROOT
from app.historical.multiyear_ingestion import (
    HistoricalDataAvailabilityValidator,
    STATUS_READY,
    STATUS_BLOCKED,
    STATUS_INSUFFICIENT
)
from app.ml.baseline_predictor import LogisticRegressionBaseline, BASELINE_FEATURE_COLUMNS
from app.ml.climatology import ClimatologyBaseline
from app.ml.evaluation import brier_score, brier_skill_score, compute_calibration_curve
from app.prediction.dataset_builder import PredictionDatasetBuilder
from app.historical.imd_ingestion import IMDIngestionManager, GATE_READY, GATE_BLOCKED

logger = logging.getLogger(__name__)

DEFAULT_PREDICTION_CSV = PROJECT_ROOT / "data" / "processed" / "prediction_dataset.csv"
MULTIYEAR_PREDICTION_CSV = PROJECT_ROOT / "data" / "processed" / "historical" / "multiyear_prediction_dataset.csv"
TARGET_HORIZONS = [7, 14, 21, 30]
PROTOTYPE_CLASSIFICATION_THRESHOLD = 0.35  # Stated prototype threshold for contingency analysis


class MultiYearScientificValidator:
    """
    Executes honest, reproducible scientific validation of probabilistic forecasts
    across multiple historical monsoon years.
    """

    def __init__(
        self,
        prediction_csv_path: Optional[Path] = None,
        feature_columns: Optional[List[str]] = None,
        target_event: str = "target_false_onset"
    ):
        if prediction_csv_path is not None:
            self.csv_path = Path(prediction_csv_path)
        elif MULTIYEAR_PREDICTION_CSV.exists():
            self.csv_path = MULTIYEAR_PREDICTION_CSV
        else:
            self.csv_path = DEFAULT_PREDICTION_CSV
        self.feature_columns = feature_columns or BASELINE_FEATURE_COLUMNS
        self.target_event = target_event
        self.availability_validator = HistoricalDataAvailabilityValidator()
        self.imd_manager = IMDIngestionManager()

    def load_dataset(self) -> pd.DataFrame:
        """Loads prediction dataset and ensures year and datetime columns exist."""
        if not self.csv_path.exists():
            return pd.DataFrame()

        df = pd.read_csv(self.csv_path)
        if "prediction_date" in df.columns:
            df["prediction_dt"] = pd.to_datetime(df["prediction_date"], errors="coerce")
            df["year"] = df["prediction_dt"].dt.year
        return df

    def compute_contingency_metrics(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray,
        threshold: float = PROTOTYPE_CLASSIFICATION_THRESHOLD
    ) -> Dict[str, Any]:
        """
        Calculates hits, misses, false alarms, correct negatives, and rates
        at an explicitly stated prototype threshold.
        """
        y_t = np.asarray(y_true, dtype=int)
        y_p = np.asarray(y_prob, dtype=float)

        y_pred = (y_p >= threshold).astype(int)

        hits = int(np.sum((y_pred == 1) & (y_t == 1)))
        misses = int(np.sum((y_pred == 0) & (y_t == 1)))
        false_alarms = int(np.sum((y_pred == 1) & (y_t == 0)))
        correct_negatives = int(np.sum((y_pred == 0) & (y_t == 0)))

        total_pos = hits + misses
        total_neg = false_alarms + correct_negatives

        hit_rate = round(float(hits / total_pos), 4) if total_pos > 0 else None
        far = round(float(false_alarms / total_neg), 4) if total_neg > 0 else None
        pred_pos = hits + false_alarms
        precision = round(float(hits / pred_pos), 4) if pred_pos > 0 else None

        return {
            "prototype_threshold": threshold,
            "hits": hits,
            "misses": misses,
            "false_alarms": false_alarms,
            "correct_negatives": correct_negatives,
            "hit_rate_recall": hit_rate,
            "false_alarm_rate": far,
            "precision": precision
        }

    def evaluate_leave_one_year_out(
        self,
        df: pd.DataFrame,
        horizon_days: int = 7
    ) -> Dict[str, Any]:
        """
        Executes Leave-One-Year-Out cross-validation across all available years.
        If fewer than 2 years are available, safely returns BLOCKED_PENDING_MULTIYEAR_DATA.
        """
        if df.empty or "year" not in df.columns:
            return {
                "validation_status": STATUS_BLOCKED,
                "message": "Insufficient historical coverage for reliable skill estimation.",
                "available_years": [],
                "horizon_days": horizon_days,
                "year_wise_results": [],
                "aggregate_metrics": None
            }

        target_col = f"{self.target_event}_{horizon_days}d"
        if target_col not in df.columns:
            return {
                "validation_status": STATUS_BLOCKED,
                "message": f"Target column {target_col} not found in prediction dataset.",
                "available_years": sorted(df["year"].dropna().unique().tolist()),
                "horizon_days": horizon_days,
                "year_wise_results": [],
                "aggregate_metrics": None
            }

        years = sorted(df["year"].dropna().unique().tolist())

        if len(years) < 2:
            # Under single-year conditions, return clean BLOCKED report
            avail_rep = self.availability_validator.validate_dataframe(df.rename(columns={"prediction_date": "date"}))
            total_samples = len(df)
            pos_events = int((df[target_col] == 1).sum()) if target_col in df.columns else 0

            return {
                "validation_status": STATUS_BLOCKED,
                "message": "Insufficient historical coverage for reliable skill estimation.",
                "statistical_honesty_statement": (
                    "Current dataset contains only 1 historical year. Leave-One-Year-Out validation "
                    "cannot evaluate out-of-sample inter-annual skill without at least 2 distinct monsoon years. "
                    "Metrics are blocked to prevent misleading over-optimistic or under-specified reporting."
                ),
                "horizon_days": horizon_days,
                "target_column": target_col,
                "available_years": [int(y) for y in years],
                "year_wise_results": [{
                    "evaluation_year": int(years[0]),
                    "training_years": [],
                    "evaluation_rows": total_samples,
                    "training_rows": 0,
                    "positive_events": pos_events,
                    "negative_events": total_samples - pos_events,
                    "brier_score": None,
                    "climatology_brier": None,
                    "brier_skill_score": None,
                    "bss_status": "INSUFFICIENT_EVENT_VARIATION",
                    "roc_auc": None,
                    "pr_auc": None,
                    "discrimination_status": "INSUFFICIENT_CLASS_VARIATION",
                    "status": STATUS_BLOCKED,
                    "reason": "Single historical year available; out-of-year training partition does not exist."
                }],
                "aggregate_metrics": None
            }

        # Multi-year Leave-One-Year-Out execution
        year_results = []
        all_eval_probs = []
        all_eval_targets = []

        for eval_year in years:
            train_mask = (df["year"] != eval_year)
            eval_mask = (df["year"] == eval_year)

            train_df = df[train_mask]
            eval_df = df[eval_mask]

            train_years = sorted(train_df["year"].unique().tolist())
            n_train = len(train_df)
            n_eval = len(eval_df)

            y_train = train_df[target_col].values
            y_eval = eval_df[target_col].values
            pos_eval = int(np.sum(y_eval == 1))
            neg_eval = int(np.sum(y_eval == 0))

            # Train climatology baseline
            clim_model = ClimatologyBaseline()
            clim_model.fit(y_train)
            clim_probs = clim_model.predict_proba(n_eval)[:, 1]
            clim_brier = brier_score(y_eval, clim_probs)

            # Train logistic baseline
            log_model = LogisticRegressionBaseline()
            log_model.fit(train_df[self.feature_columns], y_train)
            model_probs = log_model.predict_proba(eval_df[self.feature_columns])[:, 1]
            mod_brier = brier_score(y_eval, model_probs)

            # Collect for pooled calculation
            all_eval_probs.extend(model_probs.tolist())
            all_eval_targets.extend(y_eval.tolist())

            # Evaluate BSS and discrimination safeguards
            has_both_classes = (pos_eval > 0) and (neg_eval > 0)
            if not has_both_classes:
                bss = None
                bss_status = "INSUFFICIENT_EVENT_VARIATION"
                roc = None
                pr = None
                discrim_status = "INSUFFICIENT_CLASS_VARIATION"
                fold_status = "INSUFFICIENT_EVENT_VARIATION"
            else:
                bss = brier_skill_score(mod_brier, clim_brier)
                bss_status = "INTERPRETABLE"
                try:
                    roc = float(roc_auc_score(y_eval, model_probs))
                except Exception:
                    roc = None
                try:
                    pr = float(average_precision_score(y_eval, model_probs))
                except Exception:
                    pr = None
                discrim_status = "DISCRIMINATION_METRIC_VALID"
                fold_status = "EVALUATED"

            # Reliability & Contingency
            rel_bins = compute_calibration_curve(y_eval, model_probs, n_bins=10)
            contingency = self.compute_contingency_metrics(y_eval, model_probs)

            year_results.append({
                "evaluation_year": int(eval_year),
                "training_years": [int(y) for y in train_years],
                "evaluation_rows": n_eval,
                "training_rows": n_train,
                "positive_events": pos_eval,
                "negative_events": neg_eval,
                "brier_score": round(mod_brier, 4) if mod_brier is not None else None,
                "climatology_brier": round(clim_brier, 4) if clim_brier is not None else None,
                "brier_skill_score": round(bss, 4) if bss is not None else None,
                "bss_status": bss_status,
                "roc_auc": round(roc, 4) if roc is not None else None,
                "pr_auc": round(pr, 4) if pr is not None else None,
                "discrimination_status": discrim_status,
                "status": fold_status,
                "reliability_bins": rel_bins,
                "contingency": contingency
            })

        # Multi-year aggregate
        pooled_targets = np.array(all_eval_targets)
        pooled_probs = np.array(all_eval_probs)
        pooled_pos = int(np.sum(pooled_targets == 1))
        pooled_neg = int(np.sum(pooled_targets == 0))
        pooled_brier = brier_score(pooled_targets, pooled_probs)

        # Pooled climatology
        pooled_clim_brier = brier_score(pooled_targets, np.full(len(pooled_targets), pooled_pos / len(pooled_targets)))
        pooled_bss = brier_skill_score(pooled_brier, pooled_clim_brier) if (pooled_pos > 0 and pooled_neg > 0) else None

        pooled_roc = float(roc_auc_score(pooled_targets, pooled_probs)) if (pooled_pos > 0 and pooled_neg > 0) else None
        pooled_pr = float(average_precision_score(pooled_targets, pooled_probs)) if (pooled_pos > 0 and pooled_neg > 0) else None

        aggregate_metrics = {
            "total_evaluation_samples": len(pooled_targets),
            "total_positive_events": pooled_pos,
            "total_negative_events": pooled_neg,
            "pooled_brier_score": round(pooled_brier, 4),
            "pooled_climatology_brier": round(pooled_clim_brier, 4),
            "pooled_brier_skill_score": round(pooled_bss, 4) if pooled_bss is not None else None,
            "pooled_roc_auc": round(pooled_roc, 4) if pooled_roc is not None else None,
            "pooled_pr_auc": round(pooled_pr, 4) if pooled_pr is not None else None,
            "pooled_reliability_bins": compute_calibration_curve(pooled_targets, pooled_probs, n_bins=10),
            "pooled_contingency": self.compute_contingency_metrics(pooled_targets, pooled_probs)
        }

        return {
            "validation_status": STATUS_READY,
            "message": "Leave-One-Year-Out validation successfully completed across available historical years.",
            "horizon_days": horizon_days,
            "target_column": target_col,
            "available_years": [int(y) for y in years],
            "year_wise_results": year_results,
            "aggregate_metrics": aggregate_metrics
        }

    def evaluate_all_horizons(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluates 7-day, 14-day, 21-day, and 30-day horizons separately.
        Does NOT average them together to hide horizon performance differences.
        """
        horizon_results = {}
        for h in TARGET_HORIZONS:
            horizon_results[f"{h}d"] = self.evaluate_leave_one_year_out(df, horizon_days=h)
        return horizon_results

    def evaluate_block_breakdown(self, df: pd.DataFrame, horizon_days: int = 7) -> Dict[str, Any]:
        """
        Preserves block-level granularity.
        Returns evaluation results stratified by block_id.
        If a block has insufficient data, marks it INSUFFICIENT_DATA.
        """
        if df.empty or "block_id" not in df.columns:
            return {}

        blocks = sorted(df["block_id"].dropna().unique().tolist())
        target_col = f"{self.target_event}_{horizon_days}d"
        results = {}

        years = sorted(df["year"].dropna().unique().tolist()) if "year" in df.columns else []

        for blk in blocks:
            blk_df = df[df["block_id"] == blk]
            n_obs = len(blk_df)
            n_pos = int((blk_df[target_col] == 1).sum()) if target_col in blk_df.columns else 0

            if len(years) < 2 or n_obs < 30:
                results[blk] = {
                    "block_id": blk,
                    "status": STATUS_INSUFFICIENT,
                    "reason": "Insufficient historical coverage or records for reliable block skill estimation.",
                    "total_samples": n_obs,
                    "positive_events": n_pos,
                    "brier_score": None,
                    "brier_skill_score": None,
                    "roc_auc": None,
                    "pr_auc": None
                }
            else:
                # Run LOYO on block subset
                blk_loyo = self.evaluate_leave_one_year_out(blk_df, horizon_days=horizon_days)
                agg = blk_loyo.get("aggregate_metrics")
                results[blk] = {
                    "block_id": blk,
                    "status": blk_loyo.get("validation_status", STATUS_INSUFFICIENT),
                    "total_samples": n_obs,
                    "positive_events": n_pos,
                    "brier_score": agg.get("pooled_brier_score") if agg else None,
                    "brier_skill_score": agg.get("pooled_brier_skill_score") if agg else None,
                    "roc_auc": agg.get("pooled_roc_auc") if agg else None,
                    "pr_auc": agg.get("pooled_pr_auc") if agg else None
                }

        return results

    def generate_full_validation_summary(self) -> Dict[str, Any]:
        """
        Builds complete multi-year scientific validation report combining:
        - Data coverage
        - Validation readiness status
        - 7d, 14d, 21d, 30d horizon analysis
        - Block-level breakdown
        - Statistical honesty warnings
        """
        df = self.load_dataset()
        avail_report, provenance = self.availability_validator.validate_local_historical_store()
        imd_assessment = self.imd_manager.assess_ingestion_status()
        years_in_df = len(df["year"].dropna().unique()) if ("year" in df.columns and not df.empty) else 0

        if avail_report.num_years < 2 or df.empty or years_in_df < 2:
            # Blocked status
            return {
                "validation_status": STATUS_BLOCKED,
                "validation_gate": GATE_BLOCKED if years_in_df < 2 else imd_assessment.get("validation_gate", GATE_BLOCKED),
                "statement": "Insufficient historical coverage for reliable skill estimation.",
                "data_coverage": {
                    "historical_years": avail_report.num_years,
                    "complete_years": len(avail_report.complete_years),
                    "incomplete_years": len(avail_report.incomplete_years),
                    "available_years_list": avail_report.available_years,
                    "blocks_count": avail_report.num_blocks,
                    "block_ids": avail_report.block_ids,
                    "total_observations": avail_report.total_observations,
                    "missing_dates_count": avail_report.missing_dates_count,
                    "missing_rainfall_count": avail_report.missing_rainfall_count,
                    "duplicate_records_count": avail_report.duplicate_records_count,
                    "suspicious_values_count": avail_report.suspicious_values_count,
                    "date_continuity": avail_report.date_continuity
                },
                "provenance": provenance.to_dict() if provenance else None,
                "imd_status": imd_assessment,
                "horizons": {
                    "7d": {"status": "UNAVAILABLE", "reason": "Insufficient historical years (BLOCKED_PENDING_MULTIYEAR_DATA)"},
                    "14d": {"status": "UNAVAILABLE", "reason": "Insufficient historical years (BLOCKED_PENDING_MULTIYEAR_DATA)"},
                    "21d": {"status": "UNAVAILABLE", "reason": "Insufficient historical years (BLOCKED_PENDING_MULTIYEAR_DATA)"},
                    "30d": {"status": "UNAVAILABLE", "reason": "Insufficient historical years (BLOCKED_PENDING_MULTIYEAR_DATA)"}
                },
                "blocks": self.evaluate_block_breakdown(df, horizon_days=7),
                "loyo_7d": self.evaluate_leave_one_year_out(df, horizon_days=7),
                "is_operational": False,
                "feedback_retraining": False
            }

        # If >= 2 years exist, evaluate all horizons
        horizons_eval = self.evaluate_all_horizons(df)
        blocks_eval = self.evaluate_block_breakdown(df, horizon_days=7)

        return {
            "validation_status": STATUS_READY,
            "validation_gate": imd_assessment.get("validation_gate", GATE_BLOCKED),
            "statement": "Multi-year historical benchmarking completed across available seasons.",
            "data_coverage": {
                "historical_years": avail_report.num_years,
                "complete_years": len(avail_report.complete_years),
                "incomplete_years": len(avail_report.incomplete_years),
                "available_years_list": avail_report.available_years,
                "blocks_count": avail_report.num_blocks,
                "block_ids": avail_report.block_ids,
                "total_observations": avail_report.total_observations,
                "missing_dates_count": avail_report.missing_dates_count,
                "missing_rainfall_count": avail_report.missing_rainfall_count,
                "duplicate_records_count": avail_report.duplicate_records_count,
                "suspicious_values_count": avail_report.suspicious_values_count,
                "date_continuity": avail_report.date_continuity
            },
            "provenance": provenance.to_dict() if provenance else None,
            "imd_status": imd_assessment,
            "horizons": horizons_eval,
            "blocks": blocks_eval,
            "loyo_7d": horizons_eval.get("7d"),
            "is_operational": False,
            "feedback_retraining": False
        }
