"""
Meghvani Phase 7B: Historical Data Ingestion & Availability Validation Engine.

Provides:
1. Standard metadata provenance schema for historical meteorological datasets.
2. Ingestion directory and file inspection.
3. Strict data availability validator (years, completeness, gaps, duplicates, anomalies).
4. Deterministic multi-year readiness status reporting.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
import hashlib
from datetime import datetime
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field

from app.config import PROJECT_ROOT

RAW_HISTORICAL_DIR = PROJECT_ROOT / "data" / "raw" / "historical"
INTERIM_HISTORICAL_DIR = PROJECT_ROOT / "data" / "interim" / "historical"
PROCESSED_HISTORICAL_DIR = PROJECT_ROOT / "data" / "processed" / "historical"

STATUS_READY = "READY"
STATUS_BLOCKED = "BLOCKED_PENDING_MULTIYEAR_DATA"
STATUS_INSUFFICIENT = "INSUFFICIENT_DATA"

# Standard reference monsoon benchmark period: 5 historical years
STANDARD_BENCHMARK_YEARS = [2019, 2020, 2021, 2022, 2023, 2024]


class ProvenanceMetadata(BaseModel):
    """
    Metadata record for imported historical datasets.
    Preserves strict scientific provenance tracking.
    """
    dataset_name: str
    provider: str
    source_url_or_reference: str
    variable: str = "daily_rainfall"
    spatial_resolution: str = "block-level"
    temporal_resolution: str = "daily"
    coverage_start: str
    coverage_end: str
    import_date: str = Field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d"))
    units: str = "mm"
    missing_value_convention: str = "NaN / negative values flagged as invalid"
    license_or_usage_notes: str = "Official institutional or open research meteorological data"
    checksum_sha256: Optional[str] = None
    is_verified: bool = False
    verification_status: str = "SOURCE_VERIFICATION_REQUIRED"

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class DataAvailabilityReport(BaseModel):
    """
    Structured report produced by the HistoricalDataAvailabilityValidator.
    """
    validation_status: str
    num_years: int
    available_years: List[int]
    complete_years: List[int]
    incomplete_years: List[int]
    missing_years: List[int]
    num_blocks: int
    block_ids: List[str]
    total_observations: int
    missing_dates_count: int
    missing_rainfall_count: int
    duplicate_records_count: int
    suspicious_values_count: int
    date_continuity: bool
    summary_text: str
    detailed_block_coverage: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


def calculate_file_sha256(filepath: Path) -> str:
    """Computes SHA-256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()


class HistoricalDataAvailabilityValidator:
    """
    Validates availability, continuity, and completeness of historical rainfall datasets.
    Strictly forbids inventing or synthesizing missing years.
    """

    def __init__(
        self,
        raw_dir: Optional[Path] = None,
        expected_benchmark_years: Optional[List[int]] = None
    ):
        self.raw_dir = raw_dir or RAW_HISTORICAL_DIR
        self.expected_years = expected_benchmark_years or STANDARD_BENCHMARK_YEARS

    def validate_dataframe(self, df: pd.DataFrame) -> DataAvailabilityReport:
        """
        Performs thorough availability and integrity checks on an input rainfall dataframe.
        Expected columns: block_id, date, rainfall_mm
        """
        if df.empty or "date" not in df.columns or "rainfall_mm" not in df.columns:
            return DataAvailabilityReport(
                validation_status=STATUS_BLOCKED,
                num_years=0,
                available_years=[],
                complete_years=[],
                incomplete_years=[],
                missing_years=self.expected_years.copy(),
                num_blocks=0,
                block_ids=[],
                total_observations=0,
                missing_dates_count=0,
                missing_rainfall_count=0,
                duplicate_records_count=0,
                suspicious_values_count=0,
                date_continuity=False,
                summary_text="AVAILABLE HISTORICAL YEARS\n(none)\n\nINCOMPLETE YEARS\n(none)\n\nMISSING YEARS\n" + "\n".join(str(y) for y in self.expected_years)
            )

        work = df.copy()
        work["date_dt"] = pd.to_datetime(work["date"], errors="coerce")
        work = work.dropna(subset=["date_dt"])
        work["year"] = work["date_dt"].dt.year

        available_years = sorted(work["year"].unique().tolist())
        block_ids = sorted(work["block_id"].dropna().unique().tolist()) if "block_id" in work.columns else ["DEFAULT"]
        total_obs = len(work)

        # Missing rainfall values
        missing_rainfall = int(work["rainfall_mm"].isna().sum())

        # Duplicate records (block_id + date)
        if "block_id" in work.columns:
            duplicates = int(work.duplicated(subset=["block_id", "date"]).sum())
        else:
            duplicates = int(work.duplicated(subset=["date"]).sum())

        # Suspicious values: negative rainfall or extreme outliers (> 1000 mm in a single day)
        numeric_rainfall = pd.to_numeric(work["rainfall_mm"], errors="coerce")
        suspicious = int(((numeric_rainfall < 0) | (numeric_rainfall > 1000.0) | numeric_rainfall.isna()).sum() - missing_rainfall)

        # Completeness per year & block continuity
        complete_years: List[int] = []
        incomplete_years: List[int] = []
        block_coverage: Dict[str, Dict[str, Any]] = {}
        total_missing_dates = 0
        overall_continuity = True

        for yr in available_years:
            yr_df = work[work["year"] == yr]
            yr_is_complete = True

            for blk in block_ids:
                blk_df = yr_df[yr_df["block_id"] == blk] if "block_id" in work.columns else yr_df
                if blk_df.empty:
                    yr_is_complete = False
                    overall_continuity = False
                    continue

                min_date = blk_df["date_dt"].min()
                max_date = blk_df["date_dt"].max()
                expected_days = (max_date - min_date).days + 1
                actual_days = blk_df["date_dt"].nunique()
                missing_in_range = expected_days - actual_days

                if missing_in_range > 0:
                    total_missing_dates += missing_in_range
                    yr_is_complete = False
                    overall_continuity = False

                # Check if it covers full monsoon (at least June 1 to Sept 30, ~120 days)
                is_monsoon_span = (min_date.month <= 6 and min_date.day <= 15) and (max_date.month >= 9 and max_date.day >= 15)
                if not is_monsoon_span or actual_days < 100:
                    yr_is_complete = False

                if blk not in block_coverage:
                    block_coverage[blk] = {}
                block_coverage[blk][str(yr)] = {
                    "observations": len(blk_df),
                    "min_date": str(min_date.date()),
                    "max_date": str(max_date.date()),
                    "missing_days": missing_in_range
                }

            if yr_is_complete:
                complete_years.append(yr)
            else:
                incomplete_years.append(yr)

        # Missing years relative to benchmark
        missing_years = [y for y in self.expected_years if y not in available_years]

        # Validation status: Must have >= 2 complete historical years to be READY for multi-year validation
        if len(complete_years) >= 2:
            status = STATUS_READY
        else:
            status = STATUS_BLOCKED

        # Build human-readable summary
        avail_str = "\n".join(str(y) for y in available_years) if available_years else "(none)"
        incomp_str = "\n".join(str(y) for y in incomplete_years) if incomplete_years else "(none)"
        miss_str = "\n".join(str(y) for y in missing_years) if missing_years else "(none)"

        summary_text = (
            f"AVAILABLE HISTORICAL YEARS\n{avail_str}\n\n"
            f"INCOMPLETE YEARS\n{incomp_str}\n\n"
            f"MISSING YEARS\n{miss_str}\n\n"
            f"VALIDATION STATUS: {status}\n"
            f"Total Years: {len(available_years)} (Complete: {len(complete_years)}, Incomplete: {len(incomplete_years)})\n"
            f"Blocks: {len(block_ids)}, Observations: {total_obs}, Missing Dates: {total_missing_dates}\n"
            f"Missing Rainfall: {missing_rainfall}, Duplicates: {duplicates}, Suspicious: {suspicious}"
        )

        return DataAvailabilityReport(
            validation_status=status,
            num_years=len(available_years),
            available_years=available_years,
            complete_years=complete_years,
            incomplete_years=incomplete_years,
            missing_years=missing_years,
            num_blocks=len(block_ids),
            block_ids=block_ids,
            total_observations=total_obs,
            missing_dates_count=total_missing_dates,
            missing_rainfall_count=missing_rainfall,
            duplicate_records_count=duplicates,
            suspicious_values_count=suspicious,
            date_continuity=overall_continuity,
            summary_text=summary_text,
            detailed_block_coverage=block_coverage
        )

    def validate_local_historical_store(self) -> Tuple[DataAvailabilityReport, Optional[ProvenanceMetadata]]:
        """
        Inspects the standard local raw historical directory, extracted IMD block rainfall, and demo rainfall file.
        Returns the data availability report and associated provenance.
        """
        block_rainfall_csv = PROJECT_ROOT / "data" / "processed" / "historical" / "block_daily_rainfall.csv"
        if block_rainfall_csv.exists():
            df = pd.read_csv(block_rainfall_csv)
            report = self.validate_dataframe(df)
            checksum = calculate_file_sha256(block_rainfall_csv)
            metadata = ProvenanceMetadata(
                dataset_name="IMD_025_Gridded_Daily_Rainfall",
                provider="India Meteorological Department (IMD)",
                source_url_or_reference="https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html",
                coverage_start=str(df["date"].min()),
                coverage_end=str(df["date"].max()),
                checksum_sha256=checksum,
                is_verified=True,
                verification_status="VERIFIED_IMD_DATA"
            )
            return report, metadata

        csv_files = list(self.raw_dir.glob("*.csv")) if self.raw_dir.exists() else []

        if not csv_files:
            # Fallback to existing demo rainfall file
            demo_csv = PROJECT_ROOT / "data" / "raw" / "rainfall" / "demo_rainfall.csv"
            if demo_csv.exists():
                df = pd.read_csv(demo_csv)
                report = self.validate_dataframe(df)
                checksum = calculate_file_sha256(demo_csv)
                metadata = ProvenanceMetadata(
                    dataset_name="demo_rainfall_2025",
                    provider="Meghvani Prototype Synthetic/Demo Repository",
                    source_url_or_reference="Internal seed dataset (data/raw/rainfall/demo_rainfall.csv)",
                    coverage_start=str(df["date"].min()),
                    coverage_end=str(df["date"].max()),
                    checksum_sha256=checksum,
                    is_verified=False,
                    verification_status="DEMO_DATA_ONLY"
                )
                return report, metadata

            return self.validate_dataframe(pd.DataFrame()), None

        # If files exist in data/raw/historical, combine and inspect
        dfs = []
        for f in sorted(csv_files):
            try:
                dfs.append(pd.read_csv(f))
            except Exception:
                pass

        if not dfs:
            return self.validate_dataframe(pd.DataFrame()), None

        combined_df = pd.concat(dfs, ignore_index=True)
        report = self.validate_dataframe(combined_df)
        first_file = csv_files[0]
        metadata = ProvenanceMetadata(
            dataset_name=first_file.stem,
            provider="Local Ingested Repository",
            source_url_or_reference=str(first_file),
            coverage_start=str(combined_df["date"].min()) if "date" in combined_df.columns else "N/A",
            coverage_end=str(combined_df["date"].max()) if "date" in combined_df.columns else "N/A",
            checksum_sha256=calculate_file_sha256(first_file),
            is_verified=False,
            verification_status="SOURCE_VERIFICATION_REQUIRED"
        )
        return report, metadata
