"""
Rainfall data validator module.
Validates schemas, types, date integrity, duplicate detection, and missing dates.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Data Quality Flags
QUALITY_GOOD = "GOOD"
QUALITY_MISSING_DATA = "MISSING_DATA"
QUALITY_INVALID_DATA = "INVALID_DATA"
QUALITY_DUPLICATE = "DUPLICATE"
QUALITY_INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"

IMPOSSIBLE_RAINFALL_THRESHOLD_MM = 1000.0  # Daily rainfall world record ceiling check

@dataclass
class ValidationReport:
    rows_input: int = 0
    rows_valid: int = 0
    duplicate_rows: int = 0
    negative_rainfall_rows: int = 0
    invalid_dates: int = 0
    missing_dates: int = 0
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rows_input": self.rows_input,
            "rows_valid": self.rows_valid,
            "duplicate_rows": self.duplicate_rows,
            "negative_rainfall_rows": self.negative_rainfall_rows,
            "invalid_dates": self.invalid_dates,
            "missing_dates": self.missing_dates,
            "warnings": self.warnings
        }


class RainfallValidator:
    """
    Validates raw rainfall datasets for integrity, continuity, and physical limits.
    Crucial scientific principle: Missing dates are NOT converted to zero rainfall.
    """

    def validate(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, ValidationReport]:
        report = ValidationReport()
        report.rows_input = len(df)

        if df.empty:
            report.warnings.append("Input dataset is empty.")
            return df, report

        work_df = df.copy()

        # 1. Initialize data quality flag
        if "data_quality_flag" not in work_df.columns:
            work_df["data_quality_flag"] = QUALITY_GOOD

        # 2. Block ID validation: cannot be empty or null
        empty_blocks = work_df["block_id"].isna() | (work_df["block_id"].astype(str).str.strip() == "")
        if empty_blocks.any():
            count = int(empty_blocks.sum())
            report.warnings.append(f"Found {count} rows with empty or missing block_id.")
            work_df.loc[empty_blocks, "data_quality_flag"] = QUALITY_INVALID_DATA

        # 3. Date validation
        parsed_dates = pd.to_datetime(work_df["date"], errors="coerce")
        work_df["parsed_date"] = parsed_dates.dt.date
        invalid_dates = parsed_dates.isna()
        if invalid_dates.any():
            report.invalid_dates = int(invalid_dates.sum())
            report.warnings.append(f"Found {report.invalid_dates} rows with invalid dates.")
            work_df.loc[invalid_dates, "data_quality_flag"] = QUALITY_INVALID_DATA

        # 4. Rainfall numeric & physical bounds validation
        numeric_rainfall = pd.to_numeric(work_df["rainfall_mm"], errors="coerce")
        non_numeric = numeric_rainfall.isna() & ~work_df["rainfall_mm"].isna()
        if non_numeric.any():
            report.warnings.append(f"Found {int(non_numeric.sum())} non-numeric rainfall values.")
            work_df.loc[non_numeric, "data_quality_flag"] = QUALITY_INVALID_DATA

        negative_rainfall = numeric_rainfall < 0.0
        if negative_rainfall.any():
            report.negative_rainfall_rows = int(negative_rainfall.sum())
            report.warnings.append(f"Found {report.negative_rainfall_rows} rows with negative rainfall.")
            work_df.loc[negative_rainfall, "data_quality_flag"] = QUALITY_INVALID_DATA

        impossible_rainfall = numeric_rainfall > IMPOSSIBLE_RAINFALL_THRESHOLD_MM
        if impossible_rainfall.any():
            count = int(impossible_rainfall.sum())
            report.warnings.append(f"Found {count} rows with implausible rainfall > {IMPOSSIBLE_RAINFALL_THRESHOLD_MM}mm.")
            work_df.loc[impossible_rainfall, "data_quality_flag"] = QUALITY_INVALID_DATA

        work_df["clean_rainfall_mm"] = numeric_rainfall

        # 5. Duplicate detection on (block_id, parsed_date)
        valid_date_mask = ~invalid_dates & ~empty_blocks
        duplicates = work_df[valid_date_mask].duplicated(subset=["block_id", "parsed_date"], keep="first")
        if duplicates.any():
            report.duplicate_rows = int(duplicates.sum())
            dup_indices = duplicates[duplicates].index
            work_df.loc[dup_indices, "data_quality_flag"] = QUALITY_DUPLICATE
            report.warnings.append(f"Found {report.duplicate_rows} duplicate block_id + date observations.")

        # 6. Missing date sequence analysis per block
        # (CRITICAL: Do NOT fill missing dates with 0.0)
        missing_date_count = 0
        blocks = work_df.loc[valid_date_mask, "block_id"].dropna().unique()
        for b in blocks:
            b_dates = work_df.loc[(work_df["block_id"] == b) & valid_date_mask, "parsed_date"].dropna().sort_values()
            if len(b_dates) > 1:
                min_d = b_dates.min()
                max_d = b_dates.max()
                expected_days = (max_d - min_d).days + 1
                actual_days = b_dates.nunique()
                missing = expected_days - actual_days
                if missing > 0:
                    missing_date_count += missing
                    report.warnings.append(
                        f"Block {b} has {missing} missing calendar dates between {min_d} and {max_d}. Not filled with zero."
                    )

        report.missing_dates = missing_date_count

        # 7. Summary calculation
        valid_rows = (work_df["data_quality_flag"] == QUALITY_GOOD).sum()
        report.rows_valid = int(valid_rows)

        # Standardize date string format for downstream processing
        if "parsed_date" in work_df.columns:
            work_df["date"] = work_df["parsed_date"].astype(str)
            work_df.drop(columns=["parsed_date"], inplace=True)

        if "clean_rainfall_mm" in work_df.columns:
            work_df["rainfall_mm"] = work_df["clean_rainfall_mm"]
            work_df.drop(columns=["clean_rainfall_mm"], inplace=True)

        logger.info(f"Validation complete: {report.rows_valid}/{report.rows_input} rows valid.")
        return work_df, report
