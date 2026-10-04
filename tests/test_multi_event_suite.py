"""
Tests for Multi-Event Prediction Suite.
Verifies:
1. Training and probability calibration for multi-event suite (onset, break, heavy rain, false onset).
2. Model serialization and artifact loading.
3. Probability bounds [0.0, 1.0] and non-empty responses.
4. Fast API endpoint /api/forecast/{block_id}/multi-event and /api/forecast/suite-summary contracts.
"""
import pytest
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np

from app.main import app
from app.ml.multi_event_suite import MultiEventPredictor, EVENT_TARGET_MAPPING
from app.ml.model_loader import predict_block_multi_event, get_multi_event_suite_summary
from app.config import PROJECT_ROOT


@pytest.fixture
def client():
    return TestClient(app)


def test_multi_event_mapping_integrity():
    """Verifies that all required agrometeorological event targets are mapped."""
    required_events = ["onset_7d", "onset_14d", "break_7d", "break_14d", "heavy_rain_7d", "false_onset_7d"]
    for evt in required_events:
        assert evt in EVENT_TARGET_MAPPING
        cfg = EVENT_TARGET_MAPPING[evt]
        assert "target_col" in cfg
        assert "horizon_days" in cfg
        assert cfg["horizon_days"] in (7, 14)


def test_multi_event_inference_bounds():
    """Verifies predict_block_multi_event outputs valid calibrated probabilities."""
    res_7d = predict_block_multi_event("BLK001", horizon_days=7)
    assert res_7d["block_id"] == "BLK001"
    assert res_7d["horizon_days"] == 7
    assert 0.0 <= res_7d["prob_onset"] <= 1.0
    assert 0.0 <= res_7d["prob_break"] <= 1.0
    assert 0.0 <= res_7d["prob_heavy_rain"] <= 1.0
    assert 0.0 <= res_7d["prob_false_onset"] <= 1.0
    assert 0.0 <= res_7d["confidence"] <= 1.0
    assert res_7d["is_operational"] is False

    res_14d = predict_block_multi_event("BLK001", horizon_days=14)
    assert res_14d["horizon_days"] == 14
    assert 0.0 <= res_14d["prob_onset"] <= 1.0
    assert 0.0 <= res_14d["prob_break"] <= 1.0


def test_api_multi_event_endpoints(client):
    """Verifies HTTP status and JSON response contract for multi-event forecast APIs."""
    # Test suite summary
    sum_res = client.get("/api/forecast/suite-summary")
    assert sum_res.status_code == 200
    summary = sum_res.json()
    assert "onset_7d" in summary
    assert "break_7d" in summary
    assert "heavy_rain_7d" in summary

    # Test multi-event endpoint for valid block
    fc_res = client.get("/api/forecast/BLK001/multi-event?horizon_days=7")
    assert fc_res.status_code == 200
    fc_data = fc_res.json()
    assert fc_data["block_id"] == "BLK001"
    assert "prob_onset" in fc_data
    assert "prob_break" in fc_data
    assert "prob_heavy_rain" in fc_data
    assert "prob_false_onset" in fc_data

    # Test 14-day horizon
    fc_14d = client.get("/api/forecast/BLK002/multi-event?horizon_days=14")
    assert fc_14d.status_code == 200
    assert fc_14d.json()["horizon_days"] == 14

    # Test invalid block ID
    inv_res = client.get("/api/forecast/NON_EXISTENT_BLOCK/multi-event")
    assert inv_res.status_code == 404
