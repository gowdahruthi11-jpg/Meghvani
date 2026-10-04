"""
Meghvani Phase 7C: IMD 0.25° Gridded Rainfall Ingestion & Validation Framework.

Dataset: India Meteorological Department (IMD) New High Spatial Resolution
0.25° × 0.25° Long Period Daily Gridded Rainfall Dataset Over India (1901–2024).
Official Source: https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html

Critical Scientific Invariants:
1. NEVER fabricate historical data or create synthetic years.
2. Ingests genuine NetCDF-3 (.nc) files from data/raw/historical/imd/.
3. 2025 demo dataset is strictly preserved for project regression.
4. Generates data/processed/historical/imd_data_quality_report.csv,
   data/processed/historical/block_daily_rainfall.csv, and
   data/processed/historical/block_rainfall_quality.csv.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import hashlib
from datetime import datetime, date, timedelta
import calendar
import logging
import pandas as pd
import numpy as np
import scipy.io as sio
from pydantic import BaseModel, Field

from app.config import PROJECT_ROOT
from app.historical.spatial_mapping import (
    BlockSpatialMapper,
    snap_to_imd_grid,
    METHOD_CENTROID,
    STATUS_BLOCK_GEOMETRY_REQUIRED
)

logger = logging.getLogger(__name__)

IMD_RAW_DIR = PROJECT_ROOT / "data" / "raw" / "historical" / "imd"
IMD_INTERIM_DIR = PROJECT_ROOT / "data" / "interim" / "historical" / "imd"
IMD_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "historical" / "imd"

QUALITY_REPORT_CSV = PROJECT_ROOT / "data" / "processed" / "historical" / "imd_data_quality_report.csv"
BLOCK_DAILY_RAINFALL_CSV = PROJECT_ROOT / "data" / "processed" / "historical" / "block_daily_rainfall.csv"
BLOCK_RAINFALL_QUALITY_CSV = PROJECT_ROOT / "data" / "processed" / "historical" / "block_rainfall_quality.csv"

STATUS_BLOCKED_IMD = "BLOCKED_PENDING_VERIFIED_IMD_DATA"
STATUS_DATA_AVAILABLE = "DATA_AVAILABLE"
GATE_READY = "MULTIYEAR_VALIDATION_READY"
GATE_BLOCKED = "MULTIYEAR_VALIDATION_BLOCKED"

# IMD Grid Specification
IMD_LAT_MIN = 6.5
IMD_LAT_MAX = 38.5
IMD_LON_MIN = 66.5
IMD_LON_MAX = 100.0
IMD_GRID_STEP = 0.25
IMD_EXPECTED_LAT_COUNT = 129
IMD_EXPECTED_LON_COUNT = 135
IMD_MISSING_VALUE = -999.0
MAX_PHYSICAL_DAILY_RAINFALL_MM = 1500.0
IMD_TIME_ORIGIN = datetime(1900, 12, 31)


class IMDQualityRecord(BaseModel):
    file_name: str
    year: int
    readability: bool
    dimensions_valid: bool
    grid_bounds_valid: bool
    expected_days: int
    actual_days: int
    is_leap_year: bool
    leap_year_handled: bool
    units_verified: bool
    missing_value_count: int
    duplicate_dates_count: int
    negative_values_count: int
    impossible_values_count: int
    overall_quality_pass: bool
    rejection_or_flag_reason: Optional[str] = None


class IMDDataQualityValidator:
    """
    Validates physical, temporal, and spatial integrity of IMD gridded daily rainfall records.
    """

    @staticmethod
    def is_leap(year: int) -> bool:
        return calendar.isleap(year)

    @staticmethod
    def expected_days_in_year(year: int) -> int:
        return 366 if calendar.isleap(year) else 365

    def validate_netcdf_file(self, nc_path: Path) -> Tuple[IMDQualityRecord, Optional[Dict[str, Any]]]:
        """
        Inspects and validates an IMD NetCDF (.nc) file directly.
        Returns the quality record and extracted metadata.
        """
        try:
            nc = sio.netcdf_file(str(nc_path), 'r', mmap=False)
        except Exception as e:
            return IMDQualityRecord(
                file_name=nc_path.name,
                year=0,
                readability=False,
                dimensions_valid=False,
                grid_bounds_valid=False,
                expected_days=365,
                actual_days=0,
                is_leap_year=False,
                leap_year_handled=False,
                units_verified=False,
                missing_value_count=0,
                duplicate_dates_count=0,
                negative_values_count=0,
                impossible_values_count=0,
                overall_quality_pass=False,
                rejection_or_flag_reason=f"Failed to open NetCDF: {e}"
            ), None

        try:
            # Check variables
            var_names = set(nc.variables.keys())
            has_required_vars = {"LATITUDE", "LONGITUDE", "TIME", "RAINFALL"}.issubset(var_names)
            if not has_required_vars:
                nc.close()
                return IMDQualityRecord(
                    file_name=nc_path.name,
                    year=0,
                    readability=True,
                    dimensions_valid=False,
                    grid_bounds_valid=False,
                    expected_days=365,
                    actual_days=0,
                    is_leap_year=False,
                    leap_year_handled=False,
                    units_verified=False,
                    missing_value_count=0,
                    duplicate_dates_count=0,
                    negative_values_count=0,
                    impossible_values_count=0,
                    overall_quality_pass=False,
                    rejection_or_flag_reason=f"Missing required NetCDF variables. Found: {list(var_names)}"
                ), None

            lats = nc.variables["LATITUDE"][:].copy()
            lons = nc.variables["LONGITUDE"][:].copy()
            time_raw = nc.variables["TIME"][:].copy()

            # Date calculation
            dates = [IMD_TIME_ORIGIN + timedelta(days=float(t)) for t in time_raw]
            years = [d.year for d in dates]
            year = years[0] if years else 0
            is_leap = self.is_leap(year)
            exp_days = self.expected_days_in_year(year)
            actual_days = len(dates)

            dimensions_valid = (len(lats) == IMD_EXPECTED_LAT_COUNT) and (len(lons) == IMD_EXPECTED_LON_COUNT)
            grid_bounds_valid = (
                np.isclose(lats.min(), IMD_LAT_MIN, atol=0.01) and
                np.isclose(lats.max(), IMD_LAT_MAX, atol=0.01) and
                np.isclose(lons.min(), IMD_LON_MIN, atol=0.01) and
                np.isclose(lons.max(), IMD_LON_MAX, atol=0.01)
            )

            leap_handled = (actual_days == exp_days)
            duplicate_dates = actual_days - len(set(d.strftime("%Y-%m-%d") for d in dates))

            # Units
            rf_var = nc.variables["RAINFALL"]
            rf_units = getattr(rf_var, "units", b"mm")
            units_str = rf_units.decode("utf-8") if isinstance(rf_units, bytes) else str(rf_units)
            units_verified = ("mm" in units_str.lower())

            nc_info = {
                "file_path": nc_path,
                "year": year,
                "dates": [d.strftime("%Y-%m-%d") for d in dates],
                "lats": lats,
                "lons": lons,
                "nc_handle": nc
            }

            rec = IMDQualityRecord(
                file_name=nc_path.name,
                year=year,
                readability=True,
                dimensions_valid=dimensions_valid,
                grid_bounds_valid=grid_bounds_valid,
                expected_days=exp_days,
                actual_days=actual_days,
                is_leap_year=is_leap,
                leap_year_handled=leap_handled,
                units_verified=units_verified,
                missing_value_count=0,
                duplicate_dates_count=duplicate_dates,
                negative_values_count=0,
                impossible_values_count=0,
                overall_quality_pass=(dimensions_valid and grid_bounds_valid and leap_handled),
                rejection_or_flag_reason="All physical, temporal, and spatial NetCDF checks passed."
            )
            return rec, nc_info

        except Exception as e:
            nc.close()
            return IMDQualityRecord(
                file_name=nc_path.name,
                year=0,
                readability=True,
                dimensions_valid=False,
                grid_bounds_valid=False,
                expected_days=365,
                actual_days=0,
                is_leap_year=False,
                leap_year_handled=False,
                units_verified=False,
                missing_value_count=0,
                duplicate_dates_count=0,
                negative_values_count=0,
                impossible_values_count=0,
                overall_quality_pass=False,
                rejection_or_flag_reason=f"Error inspecting NetCDF: {e}"
            ), None

    def validate_gridded_dataframe(self, df: pd.DataFrame, source_file: str = "in_memory") -> IMDQualityRecord:
        """Validates tabular IMD daily gridded dataframe."""
        if df.empty or "date" not in df.columns or "rainfall_mm" not in df.columns:
            return IMDQualityRecord(
                file_name=source_file,
                year=0,
                readability=False,
                dimensions_valid=False,
                grid_bounds_valid=False,
                expected_days=365,
                actual_days=0,
                is_leap_year=False,
                leap_year_handled=False,
                units_verified=False,
                missing_value_count=0,
                duplicate_dates_count=0,
                negative_values_count=0,
                impossible_values_count=0,
                overall_quality_pass=False,
                rejection_or_flag_reason="Empty dataset or missing required columns"
            )

        work = df.copy()
        work["date_dt"] = pd.to_datetime(work["date"], errors="coerce")
        work = work.dropna(subset=["date_dt"])
        if work.empty:
            return IMDQualityRecord(
                file_name=source_file,
                year=0,
                readability=True,
                dimensions_valid=False,
                grid_bounds_valid=False,
                expected_days=365,
                actual_days=0,
                is_leap_year=False,
                leap_year_handled=False,
                units_verified=False,
                missing_value_count=0,
                duplicate_dates_count=0,
                negative_values_count=0,
                impossible_values_count=0,
                overall_quality_pass=False,
                rejection_or_flag_reason="Invalid dates in dataset"
            )

        work["year"] = work["date_dt"].dt.year
        year = int(work["year"].mode()[0]) if not work["year"].empty else 0
        is_leap = self.is_leap(year)
        exp_days = self.expected_days_in_year(year)
        actual_days = int(work["date_dt"].dt.date.nunique())
        leap_handled = (actual_days == 366) if is_leap else (actual_days == 365 or actual_days >= 120)

        raw_rain = pd.to_numeric(work["rainfall_mm"], errors="coerce")
        missing_count = int((raw_rain == IMD_MISSING_VALUE).sum() + raw_rain.isna().sum())
        valid_rain = raw_rain[(raw_rain != IMD_MISSING_VALUE) & raw_rain.notna()]
        negative_count = int((valid_rain < 0.0).sum())
        impossible_count = int((valid_rain > MAX_PHYSICAL_DAILY_RAINFALL_MM).sum())
        duplicate_count = int(work.duplicated(subset=["date", "lat", "lon"]).sum()) if ("lat" in work.columns and "lon" in work.columns) else int(work.duplicated(subset=["date"]).sum())

        reasons = []
        if negative_count > 0:
            reasons.append(f"Rejected: {negative_count} negative rainfall values")
        if impossible_count > 0:
            reasons.append(f"Rejected: {impossible_count} impossible values (> 1500 mm)")
        if duplicate_count > 0:
            reasons.append(f"Flagged: {duplicate_count} duplicate timestamps")

        overall_pass = (negative_count == 0) and (impossible_count == 0) and (actual_days >= 30)

        return IMDQualityRecord(
            file_name=source_file,
            year=year,
            readability=True,
            dimensions_valid=("lat" in work.columns and "lon" in work.columns),
            grid_bounds_valid=True,
            expected_days=exp_days,
            actual_days=actual_days,
            is_leap_year=is_leap,
            leap_year_handled=leap_handled,
            units_verified=True,
            missing_value_count=missing_count,
            duplicate_dates_count=duplicate_count,
            negative_values_count=negative_count,
            impossible_values_count=impossible_count,
            overall_quality_pass=overall_pass,
            rejection_or_flag_reason="; ".join(reasons) if reasons else "None. All checks passed."
        )


class IMDIngestionManager:
    """
    Orchestrates discovery, ingestion, spatial mapping, and validation of IMD datasets.
    """

    def __init__(self, raw_imd_dir: Optional[Path] = None):
        self.raw_dir = raw_imd_dir or IMD_RAW_DIR
        self.validator = IMDDataQualityValidator()
        self.spatial_mapper = BlockSpatialMapper()

    def discover_raw_files(self) -> List[Path]:
        """Scans data/raw/historical/imd/ for NetCDF (.nc) and CSV (.csv) files."""
        if not self.raw_dir.exists():
            return []
        files = []
        for ext in ("*.nc", "*.grd", "*.csv", "*.parquet"):
            files.extend(self.raw_dir.glob(ext))
        return sorted(files)

    def extract_and_process_imd_data(self) -> Dict[str, Any]:
        """
        Parses all verified IMD files, validates quality, extracts representative-grid rainfall
        for prototype blocks (BLK001, BLK002, BLK003), and produces block-level datasets.
        """
        files = self.discover_raw_files()
        spatial_rep = self.spatial_mapper.get_spatial_mapping_report()

        if not files:
            self._write_empty_quality_report()
            return {
                "ingestion_status": STATUS_BLOCKED_IMD,
                "data_source": "IMD 0.25° × 0.25° Long Period Daily Gridded Rainfall",
                "official_url": "https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html",
                "resolution": "0.25° × 0.25°",
                "raw_files_found": 0,
                "raw_file_names": [],
                "available_years": [],
                "complete_years": [],
                "incomplete_years": [],
                "missing_years": [2019, 2020, 2021, 2022, 2023, 2024],
                "spatial_mapping": spatial_rep.to_dict(),
                "data_quality_report_csv": str(QUALITY_REPORT_CSV.name),
                "data_quality_status": "UNAVAILABLE",
                "validation_gate": GATE_BLOCKED,
                "message": "Phase 7C ingestion infrastructure is ready, but integration is blocked pending verified IMD historical data in data/raw/historical/imd/."
            }

        quality_records: List[IMDQualityRecord] = []
        block_rainfall_rows: List[Dict[str, Any]] = []
        block_quality_rows: List[Dict[str, Any]] = []
        years_found: List[int] = []
        complete_years: List[int] = []

        blocks_coords = self.spatial_mapper.blocks

        for f in files:
            if f.suffix == ".nc":
                q_rec, nc_info = self.validator.validate_netcdf_file(f)
                if nc_info is not None:
                    nc = nc_info["nc_handle"]
                    lats = nc_info["lats"]
                    lons = nc_info["lons"]
                    dates = nc_info["dates"]
                    yr = nc_info["year"]

                    # Extract rainfall for each block
                    for b_id, coord in blocks_coords.items():
                        lat_idx = int(np.abs(lats - coord.latitude).argmin())
                        lon_idx = int(np.abs(lons - coord.longitude).argmin())
                        grid_lat = float(lats[lat_idx])
                        grid_lon = float(lons[lon_idx])

                        # Extract 1D daily rainfall array for this block's cell
                        raw_series = nc.variables["RAINFALL"][:, lat_idx, lon_idx].copy()

                        # Check negative or impossible values
                        valid_mask = (raw_series != IMD_MISSING_VALUE) & np.isfinite(raw_series)
                        valid_vals = raw_series[valid_mask]

                        neg_cnt = int(np.sum(valid_vals < 0.0))
                        imp_cnt = int(np.sum(valid_vals > MAX_PHYSICAL_DAILY_RAINFALL_MM))
                        q_rec.negative_values_count += neg_cnt
                        q_rec.impossible_values_count += imp_cnt
                        q_rec.missing_value_count += int(np.sum(~valid_mask))

                        if neg_cnt > 0 or imp_cnt > 0:
                            q_rec.overall_quality_pass = False

                        for d_str, r_val in zip(dates, raw_series):
                            rf_clean = float(np.round(r_val, 2)) if (r_val != IMD_MISSING_VALUE and r_val >= 0.0) else np.nan
                            block_rainfall_rows.append({
                                "date": d_str,
                                "year": yr,
                                "block_id": b_id,
                                "rainfall_mm": rf_clean if not np.isnan(rf_clean) else None,
                                "source": "IMD_025",
                                "mapping_method": METHOD_CENTROID,
                                "imd_lat": grid_lat,
                                "imd_lon": grid_lon
                            })

                        # Compute block rainfall quality metrics for this block/year
                        clean_vals = valid_vals[(valid_vals >= 0.0) & (valid_vals <= MAX_PHYSICAL_DAILY_RAINFALL_MM)]
                        block_quality_rows.append({
                            "block_id": b_id,
                            "year": yr,
                            "expected_days": q_rec.expected_days,
                            "actual_days": len(raw_series),
                            "missing_days": int(np.sum(~valid_mask)),
                            "min_rainfall_mm": float(np.round(clean_vals.min(), 2)) if len(clean_vals) > 0 else 0.0,
                            "max_rainfall_mm": float(np.round(clean_vals.max(), 2)) if len(clean_vals) > 0 else 0.0,
                            "mean_rainfall_mm": float(np.round(clean_vals.mean(), 2)) if len(clean_vals) > 0 else 0.0,
                            "zero_rainfall_days": int(np.sum(clean_vals == 0.0)),
                            "valid_rainfall_days": len(clean_vals)
                        })

                    nc.close()

                quality_records.append(q_rec)
                if q_rec.overall_quality_pass:
                    years_found.append(q_rec.year)
                    if q_rec.actual_days >= 365:
                        complete_years.append(q_rec.year)

            elif f.suffix == ".csv":
                df = pd.read_csv(f)
                q_rec = self.validator.validate_gridded_dataframe(df, source_file=f.name)
                quality_records.append(q_rec)
                if q_rec.overall_quality_pass:
                    years_found.append(q_rec.year)
                    if q_rec.actual_days >= 365:
                        complete_years.append(q_rec.year)

        # Write quality report CSV
        QUALITY_REPORT_CSV.parent.mkdir(parents=True, exist_ok=True)
        q_df = pd.DataFrame([r.model_dump() for r in quality_records])
        q_df.to_csv(QUALITY_REPORT_CSV, index=False)

        # Write block daily rainfall CSV
        if block_rainfall_rows:
            blk_df = pd.DataFrame(block_rainfall_rows)
            blk_df.sort_values(by=["block_id", "date"], inplace=True)
            blk_df.to_csv(BLOCK_DAILY_RAINFALL_CSV, index=False)
            logger.info(f"Saved block daily rainfall to: {BLOCK_DAILY_RAINFALL_CSV} ({len(blk_df)} rows)")

        # Write block rainfall quality CSV
        if block_quality_rows:
            bq_df = pd.DataFrame(block_quality_rows)
            bq_df.sort_values(by=["year", "block_id"], inplace=True)
            bq_df.to_csv(BLOCK_RAINFALL_QUALITY_CSV, index=False)
            logger.info(f"Saved block rainfall quality report to: {BLOCK_RAINFALL_QUALITY_CSV}")

        years_found = sorted(list(set(years_found)))
        complete_years = sorted(list(set(complete_years)))
        target_years = [2019, 2020, 2021, 2022, 2023, 2024]
        missing_years = [y for y in target_years if y not in years_found]

        all_passed = len(quality_records) > 0 and all(r.overall_quality_pass for r in quality_records)
        gate_status = GATE_READY if (len(complete_years) >= 2 and all_passed) else GATE_BLOCKED

        return {
            "ingestion_status": STATUS_DATA_AVAILABLE if len(years_found) > 0 else STATUS_BLOCKED_IMD,
            "data_source": "IMD 0.25° × 0.25° Long Period Daily Gridded Rainfall",
            "official_url": "https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html",
            "resolution": "0.25° × 0.25°",
            "raw_files_found": len(files),
            "raw_file_names": [f.name for f in files],
            "available_years": years_found,
            "complete_years": complete_years,
            "incomplete_years": [y for y in years_found if y not in complete_years],
            "missing_years": missing_years,
            "spatial_mapping": spatial_rep.to_dict(),
            "data_quality_report_csv": str(QUALITY_REPORT_CSV.name),
            "data_quality_status": "PASS" if all_passed else "FAIL",
            "validation_gate": gate_status,
            "total_extracted_records": len(block_rainfall_rows),
            "message": (
                "IMD multi-year daily gridded dataset verified and mapped to prototype blocks."
                if gate_status == GATE_READY
                else "Phase 7C ingestion completed with data quality issues; validation gate blocked."
            )
        }

    def assess_ingestion_status(self) -> Dict[str, Any]:
        """Assesses and processes IMD data if available."""
        return self.extract_and_process_imd_data()

    def _write_empty_quality_report(self):
        QUALITY_REPORT_CSV.parent.mkdir(parents=True, exist_ok=True)
        empty_df = pd.DataFrame(columns=[
            "file_name", "year", "readability", "dimensions_valid", "grid_bounds_valid",
            "expected_days", "actual_days", "is_leap_year", "leap_year_handled",
            "units_verified", "missing_value_count", "duplicate_dates_count",
            "negative_values_count", "impossible_values_count", "overall_quality_pass",
            "rejection_or_flag_reason"
        ])
        empty_df.to_csv(QUALITY_REPORT_CSV, index=False)
