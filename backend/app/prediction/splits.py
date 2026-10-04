"""
Temporal splitting utilities for Meghvani Phase 3A.
Implements strictly chronological and year-based train/validation/test splits.

CRITICAL TEMPORAL VALIDATION PRINCIPLE:
Random train/test splits (e.g. train_test_split with random shuffling) cause severe data leakage
in time-series weather forecasting. All splits in this module are strictly chronological.
"""
from typing import Dict, Any, Tuple, Optional, List
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class TemporalSplitResult(dict):
    """
    Container for temporal split results that supports both dictionary indexing
    (e.g., splits['train'], splits['validation'], splits['test'], splits['metadata'])
    and tuple unpacking:
    train_df, val_df, test_df, metadata = create_temporal_split(...)
    """
    def __iter__(self):
        return iter((self["train"], self["validation"], self["test"], self["metadata"]))


def get_dataset_temporal_info(df: pd.DataFrame, date_col: str = "prediction_date") -> Dict[str, Any]:
    """
    Analyzes the temporal span and unique calendar years in the dataset.
    """
    col = date_col if date_col in df.columns else ("date" if "date" in df.columns else None)
    if col is None or df.empty:
        return {
            "years": [],
            "total_years": 0,
            "is_multi_year": False,
            "multi_year_validation_notice": "Insufficient historical years for genuine multi-year validation. Dataset is empty.",
            "start_date": None,
            "end_date": None
        }

    dt_series = pd.to_datetime(df[col])
    years = sorted(dt_series.dt.year.unique().tolist())
    is_multi_year = len(years) > 1
    notice = (
        None if is_multi_year else
        f"Insufficient historical years for genuine multi-year validation. Dataset contains only {len(years)} calendar year ({years})."
    )
    return {
        "years": years,
        "total_years": len(years),
        "is_multi_year": is_multi_year,
        "multi_year_validation_notice": notice,
        "start_date": str(dt_series.min().date()),
        "end_date": str(dt_series.max().date())
    }


def create_temporal_split(
    df: pd.DataFrame,
    date_col: str = "prediction_date",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: Optional[float] = None,
    train_years: Optional[List[int]] = None,
    val_years: Optional[List[int]] = None,
    test_years: Optional[List[int]] = None
) -> TemporalSplitResult:
    """
    Creates strictly chronological Train / Validation / Test splits.
    
    If multi-year data is available and year lists are provided, splits by calendar year.
    If only a single year is present in the dataset, performs chronological date-cutoff splitting
    and explicitly records an architectural notice.
    """
    if df.empty:
        empty = pd.DataFrame()
        return TemporalSplitResult({
            "train": empty,
            "validation": empty,
            "val": empty,
            "test": empty,
            "metadata": {"warning": "Dataset is empty"}
        })

    col = date_col if date_col in df.columns else ("date" if "date" in df.columns else None)
    if col is None:
        raise ValueError(f"Date column '{date_col}' not found in dataframe.")

    work_df = df.copy()
    work_df["_sort_dt"] = pd.to_datetime(work_df[col])
    work_df.sort_values(by="_sort_dt", inplace=True)

    info = get_dataset_temporal_info(work_df, col)
    available_years = info["years"]

    metadata: Dict[str, Any] = {
        "strategy": "",
        "available_years": available_years,
        "total_years": len(available_years),
        "is_multi_year": info["is_multi_year"],
        "multi_year_validation_notice": info["multi_year_validation_notice"],
        "warning": None
    }

    # Strategy 1: Explicit multi-year split if >= 2 years and year arguments provided
    if len(available_years) >= 2 and train_years and test_years:
        metadata["strategy"] = "CALENDAR_YEAR_SPLIT"
        train_df = work_df[work_df["_sort_dt"].dt.year.isin(train_years)].copy()
        val_df = work_df[work_df["_sort_dt"].dt.year.isin(val_years or [])].copy()
        test_df = work_df[work_df["_sort_dt"].dt.year.isin(test_years)].copy()
    else:
        # Strategy 2: Single-year or ratio-based chronological cutoff
        metadata["strategy"] = "CHRONOLOGICAL_DATE_CUTOFF"
        if len(available_years) <= 1:
            metadata["warning"] = (
                "Insufficient historical years for genuine multi-year validation. "
                f"Dataset contains only {len(available_years)} calendar year ({available_years}). "
                "Split performed chronologically by date ratio for prototype testing."
            )

        unique_dates = work_df["_sort_dt"].drop_duplicates().sort_values().values
        n_dates = len(unique_dates)

        train_cutoff_idx = int(n_dates * train_ratio)
        val_cutoff_idx = int(n_dates * (train_ratio + val_ratio))

        train_date_ceiling = unique_dates[max(0, train_cutoff_idx - 1)]
        val_date_ceiling = unique_dates[max(0, val_cutoff_idx - 1)]

        train_df = work_df[work_df["_sort_dt"] <= train_date_ceiling].copy()
        val_df = work_df[(work_df["_sort_dt"] > train_date_ceiling) & (work_df["_sort_dt"] <= val_date_ceiling)].copy()
        test_df = work_df[work_df["_sort_dt"] > val_date_ceiling].copy()

    # Clean up helper column
    for d in [train_df, val_df, test_df]:
        d.drop(columns=["_sort_dt"], inplace=True, errors="ignore")

    metadata["train_rows"] = len(train_df)
    metadata["val_rows"] = len(val_df)
    metadata["test_rows"] = len(test_df)
    metadata["train_date_range"] = (
        f"{train_df[col].min()} to {train_df[col].max()}" if not train_df.empty else None
    )
    metadata["val_date_range"] = (
        f"{val_df[col].min()} to {val_df[col].max()}" if not val_df.empty else None
    )
    metadata["test_date_range"] = (
        f"{test_df[col].min()} to {test_df[col].max()}" if not test_df.empty else None
    )

    return TemporalSplitResult({
        "train": train_df,
        "validation": val_df,
        "val": val_df,
        "test": test_df,
        "metadata": metadata
    })

