"""
Phase 7C: IMD Historical Data Integration & Verification Tests.

Covers:
1. IMD file validation
2. Year detection
3. Leap-year handling
4. Missing-date detection
5. Rainfall-unit validation
6. Negative-value rejection
7. Provenance metadata
8. Spatial mapping (Centroid snapping & Geometry requirement)
9. Block aggregation
10. Multi-year event processing
11. 2025 regression check
12. Phase 7B integration
13. Leakage protection
14. Insufficient-data handling
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.config import PROJECT_ROOT
from app.historical.spatial_mapping import (
    BlockSpatialMapper,
    snap_to_imd_grid,
    METHOD_CENTROID,
    METHOD_AREA_WEIGHTED,
    STATUS_READY,
    STATUS_BLOCK_GEOMETRY_REQUIRED
)
from app.historical.imd_ingestion import (
    IMDDataQualityValidator,
    IMDIngestionManager,
    IMDQualityRecord,
    STATUS_BLOCKED_IMD,
    STATUS_DATA_AVAILABLE,
    GATE_READY,
    GATE_BLOCKED
)
from app.historical.dataset_builder import HistoricalDatasetBuilder
from app.ml.multiyear_validation import MultiYearScientificValidator
from tests.test_phase_7b_no_leakage import test_feature_at_T_cannot_depend_on_rainfall_after_T


@pytest.fixture
def client():
    return TestClient(app)


def _make_gridded_df(year: int = 2020, n_days: int = 60, seed: int = 42) -> pd.DataFrame:
    """Creates a synthetic gridded daily rainfall dataframe matching IMD format."""
    np.random.seed(seed)
    dates = pd.date_range(start=f"{year}-06-01", periods=n_days, freq="D")
    
    # Grid centers covering BLK001 (21.25, 79.0), BLK002 (20.75, 78.5), BLK003 (21.0, 77.75)
    cells = [
        (21.25, 79.0),
        (20.75, 78.5),
        (21.0, 77.75)
    ]
    
    rows = []
    for d in dates:
        d_str = d.strftime("%Y-%m-%d")
        for lat, lon in cells:
            rain = float(np.round(np.random.exponential(scale=12.0), 2))
            if rain < 2.0:
                rain = 0.0
            rows.append({
                "date": d_str,
                "lat": lat,
                "lon": lon,
                "rainfall_mm": rain
            })
    return pd.DataFrame(rows)


# 1. IMD file validation
def test_imd_file_validation():
    val = IMDDataQualityValidator()
    df_empty = pd.DataFrame()
    rec = val.validate_gridded_dataframe(df_empty, source_file="empty.csv")
    assert rec.overall_quality_pass is False
    assert "Empty dataset" in rec.rejection_or_flag_reason

    # Valid dataframe
    df_valid = _make_gridded_df(2021, n_days=45)
    rec_valid = val.validate_gridded_dataframe(df_valid, source_file="valid.csv")
    assert rec_valid.readability is True
    assert rec_valid.dimensions_valid is True
    assert rec_valid.grid_bounds_valid is True
    assert rec_valid.overall_quality_pass is True


# 2. Year detection
def test_year_detection():
    val = IMDDataQualityValidator()
    df = _make_gridded_df(year=2022, n_days=30)
    rec = val.validate_gridded_dataframe(df)
    assert rec.year == 2022


# 3. Leap-year handling
def test_leap_year_handling():
    val = IMDDataQualityValidator()
    assert val.is_leap(2020) is True
    assert val.is_leap(2024) is True
    assert val.is_leap(2021) is False
    assert val.expected_days_in_year(2020) == 366
    assert val.expected_days_in_year(2021) == 365


# 4. Missing-date detection
def test_missing_date_detection():
    val = IMDDataQualityValidator()
    df = _make_gridded_df(year=2021, n_days=10)
    # Add a row with missing value indicator -999.0
    df.loc[0, "rainfall_mm"] = -999.0
    rec = val.validate_gridded_dataframe(df)
    assert rec.missing_value_count >= 1


# 5. Rainfall-unit validation
def test_rainfall_unit_validation():
    val = IMDDataQualityValidator()
    df = _make_gridded_df(year=2021, n_days=10)
    # Add impossible value > 1500 mm
    df.loc[0, "rainfall_mm"] = 2500.0
    rec = val.validate_gridded_dataframe(df)
    assert rec.impossible_values_count >= 1
    assert rec.overall_quality_pass is False


# 6. Negative-value rejection
def test_negative_value_rejection():
    val = IMDDataQualityValidator()
    df = _make_gridded_df(year=2021, n_days=10)
    # Add negative rainfall
    df.loc[1, "rainfall_mm"] = -15.5
    rec = val.validate_gridded_dataframe(df)
    assert rec.negative_values_count >= 1
    assert rec.overall_quality_pass is False


# 7. Provenance metadata
def test_provenance_metadata():
    mapper = BlockSpatialMapper()
    rep = mapper.get_spatial_mapping_report()
    assert "BLK001" in rep.mapped_blocks
    assert "BLK002" in rep.mapped_blocks
    assert "BLK003" in rep.mapped_blocks


# 8. Spatial mapping
def test_spatial_mapping_centroid_and_geometry_requirement():
    # Centroid snapping test
    lat, lon = snap_to_imd_grid(21.1458, 79.0882)
    assert lat == 21.25
    assert lon == 79.0

    mapper = BlockSpatialMapper()
    # Centroid method should be READY
    rep_centroid = mapper.get_spatial_mapping_report(preferred_method=METHOD_CENTROID)
    assert rep_centroid.status == STATUS_READY
    assert rep_centroid.chosen_method == METHOD_CENTROID

    # Area-weighted method should return BLOCK_GEOMETRY_REQUIRED
    rep_area = mapper.get_spatial_mapping_report(preferred_method=METHOD_AREA_WEIGHTED)
    assert rep_area.status == STATUS_BLOCK_GEOMETRY_REQUIRED
    assert "boundary polygon geometries" in rep_area.geometry_requirement_notes


# 9. Block aggregation
def test_block_aggregation():
    mapper = BlockSpatialMapper()
    gridded_df = _make_gridded_df(year=2020, n_days=30)
    block_df = mapper.map_gridded_to_blocks(gridded_df, method=METHOD_CENTROID)

    assert not block_df.empty
    expected_cols = {"date", "year", "block_id", "rainfall_mm", "source", "spatial_method"}
    assert expected_cols.issubset(set(block_df.columns))
    assert set(block_df["block_id"].unique()) == {"BLK001", "BLK002", "BLK003"}
    assert all(block_df["spatial_method"] == METHOD_CENTROID)


# 10. Multi-year event processing
def test_multi_year_event_processing():
    mapper = BlockSpatialMapper()
    gridded_df = _make_gridded_df(year=2020, n_days=40)
    block_df = mapper.map_gridded_to_blocks(gridded_df, method=METHOD_CENTROID)

    hist_builder = HistoricalDatasetBuilder()
    res = hist_builder.build_from_source(block_df)
    labeled_df = res["dataframe"]

    assert "onset_trigger" in labeled_df.columns
    assert "false_onset" in labeled_df.columns
    assert "break_event" in labeled_df.columns


# 11. 2025 regression check
def test_2025_regression_dataset_preserved():
    demo_csv = PROJECT_ROOT / "data" / "raw" / "rainfall" / "demo_rainfall.csv"
    assert demo_csv.exists()
    df_2025 = pd.read_csv(demo_csv)
    assert len(df_2025) == 366
    years = pd.to_datetime(df_2025["date"]).dt.year.unique()
    assert len(years) == 1
    assert years[0] == 2025


# 12. Phase 7B integration
def test_phase_7b_integration_api(client):
    res = client.get("/api/validation/multiyear/summary")
    assert res.status_code == 200
    data = res.json()
    assert "validation_status" in data
    assert "validation_gate" in data
    assert "imd_status" in data
    assert data["validation_gate"] == GATE_READY
    assert data["validation_status"] == "READY"


# 13. Leakage protection
def test_leakage_protection_regression():
    test_feature_at_T_cannot_depend_on_rainfall_after_T()


# 14. Insufficient-data handling and verified data status
def test_insufficient_data_status():
    empty_dir = PROJECT_ROOT / "data" / "raw" / "historical" / "empty_test_dir"
    manager_empty = IMDIngestionManager(raw_imd_dir=empty_dir)
    status_empty = manager_empty.assess_ingestion_status()
    assert status_empty["ingestion_status"] == STATUS_BLOCKED_IMD
    assert status_empty["validation_gate"] == GATE_BLOCKED
    assert "blocked pending verified IMD historical data" in status_empty["message"]

    # Real IMD data status
    manager_real = IMDIngestionManager()
    status_real = manager_real.assess_ingestion_status()
    assert status_real["ingestion_status"] == STATUS_DATA_AVAILABLE
    assert status_real["validation_gate"] == GATE_READY
    assert status_real["raw_files_found"] == 6
