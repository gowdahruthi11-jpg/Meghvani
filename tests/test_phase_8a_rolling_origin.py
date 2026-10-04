"""
Meghvani Phase 8A: Rolling-Origin Evaluation Test Suite & Regressions.

Covers:
1. Rolling-origin splits structure (2020 uses 2019; 2021 uses 2019-2020; etc.)
2. 2019 handled cleanly as earliest year without prior data
3. Temporal precedence (evaluation year strictly excluded from training and calibration)
4. Block-level results preservation (BLK001, BLK002, BLK003)
5. Horizon-level results preservation (7D, 14D, 21D, 30D)
6. Rolling-origin summary API endpoint
7. Phase 7A demo regression check (demo replay works without modification)
8. Phase 7B multi-year gate regression
9. Phase 7C IMD data ingestion regression
10. Scientific boundaries & non-operational safeguards
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.config import PROJECT_ROOT
from app.ml.rolling_origin import RollingOriginEvaluator
from app.historical.imd_ingestion import IMDIngestionManager, GATE_READY


@pytest.fixture
def client():
    return TestClient(app)


# 1 & 2. Rolling-origin splits structure & 2019 handling
def test_rolling_origin_split_structure():
    evaluator = RollingOriginEvaluator()
    df = evaluator.load_dataset()
    assert not df.empty

    res_7d = evaluator.evaluate_rolling_origin(df, horizon_days=7)
    assert res_7d["status"] == "READY"
    year_results = res_7d["year_results"]

    # Exactly 6 years (2019..2024)
    assert len(year_results) == 6

    # 2019 has no prior training
    yr_2019 = [r for r in year_results if r["evaluation_year"] == 2019][0]
    assert yr_2019["status"] == "NO_PRIOR_TRAINING_DATA"
    assert len(yr_2019["training_years"]) == 0

    # 2020 trained on 2019
    yr_2020 = [r for r in year_results if r["evaluation_year"] == 2020][0]
    assert yr_2020["training_years"] == [2019]
    assert yr_2020["calibration_status"] == "INSUFFICIENT_CALIBRATION_DATA"

    # 2021 trained on 2019, calibrated on 2020
    yr_2021 = [r for r in year_results if r["evaluation_year"] == 2021][0]
    assert yr_2021["training_years"] == [2019]
    assert yr_2021["calibration_years"] == [2020]
    assert yr_2021["calibration_status"] == "CALIBRATED"

    # 2024 trained on 2019..2022, calibrated on 2023
    yr_2024 = [r for r in year_results if r["evaluation_year"] == 2024][0]
    assert yr_2024["training_years"] == [2019, 2020, 2021, 2022]
    assert yr_2024["calibration_years"] == [2023]
    assert yr_2024["calibration_status"] == "CALIBRATED"


# 3. Temporal precedence
def test_temporal_precedence_in_rolling_origin():
    evaluator = RollingOriginEvaluator()
    df = evaluator.load_dataset()
    res = evaluator.evaluate_rolling_origin(df, horizon_days=7)

    for yr in res["year_results"]:
        eval_year = yr["evaluation_year"]
        for ty in yr.get("training_years", []):
            assert ty < eval_year, f"Training year {ty} must strictly precede evaluation year {eval_year}"
        for cy in yr.get("calibration_years", []):
            assert cy < eval_year, f"Calibration year {cy} must strictly precede evaluation year {eval_year}"


# 4. Block-level results preservation
def test_block_level_evaluation_preservation():
    evaluator = RollingOriginEvaluator()
    df = evaluator.load_dataset()
    block_eval = evaluator.evaluate_block_breakdown(df, horizon_days=7)

    assert set(block_eval.keys()) == {"BLK001", "BLK002", "BLK003"}
    for b_id, b_data in block_eval.items():
        assert b_data["samples"] == 2192
        assert b_data["positive_events"] > 0
        assert "aggregate_metrics" in b_data


# 5. Horizon-level results preservation
def test_all_horizons_evaluated_separately():
    evaluator = RollingOriginEvaluator()
    df = evaluator.load_dataset()
    horizons = evaluator.evaluate_all_horizons(df)

    assert set(horizons.keys()) == {"7d", "14d", "21d", "30d"}
    for h, h_res in horizons.items():
        assert h_res["status"] == "READY"
        agg = h_res["aggregate_metrics"]
        assert agg is not None
        assert "variant_a_raw" in agg
        assert "variant_a_calibrated" in agg
        assert "variant_b_unweighted" in agg
        assert "climatology_brier" in agg


# 6. Rolling-origin summary API endpoint
def test_rolling_origin_summary_api(client):
    res = client.get("/api/validation/rolling-origin/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "READY"
    assert data["evaluation_paradigm"] == "ROLLING_ORIGIN_FORWARD_CHAINING"
    assert "horizons" in data
    assert "blocks" in data
    assert "scientific_boundaries" in data
    assert data["scientific_boundaries"]["is_operational"] is False


# 7. Phase 7A demo regression check
def test_phase_7a_demo_regression(client):
    res = client.get("/api/demo/status")
    assert res.status_code == 200
    data = res.json()
    assert data["safeguards"]["is_operational"] is False
    assert data["safeguards"]["external_dispatch"] is False


# 8. Phase 7B multi-year gate regression
def test_phase_7b_gate_regression(client):
    res = client.get("/api/validation/multiyear/gate")
    assert res.status_code == 200
    data = res.json()
    assert data["validation_gate"] == GATE_READY
    assert data["validation_status"] == "READY"


# 9. Phase 7C IMD data ingestion regression
def test_phase_7c_imd_regression():
    manager = IMDIngestionManager()
    status = manager.assess_ingestion_status()
    assert status["ingestion_status"] == "DATA_AVAILABLE"
    assert status["validation_gate"] == GATE_READY
    assert status["raw_files_found"] == 6


# 10. 2025 demo dataset preserved unmodified
def test_2025_demo_dataset_preserved():
    demo_csv = PROJECT_ROOT / "data" / "raw" / "rainfall" / "demo_rainfall.csv"
    assert demo_csv.exists()
    df_2025 = pd.read_csv(demo_csv)
    assert len(df_2025) == 366
    years = pd.to_datetime(df_2025["date"]).dt.year.unique()
    assert len(years) == 1
    assert years[0] == 2025
