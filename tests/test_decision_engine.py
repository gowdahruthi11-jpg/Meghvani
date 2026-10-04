"""
Phase 4B: Prototype Decision Layer Tests.

Tests:
1. probability 0.00 -> SOW_NOW
2. probability 0.29 -> SOW_NOW
3. probability 0.30 -> SOW_PART_NOW
4. probability 0.59 -> SOW_PART_NOW
5. probability 0.60 -> WAIT
6. probability 1.00 -> WAIT
7. null probability -> UNAVAILABLE
8. NaN probability -> UNAVAILABLE
9. probability below 0 -> invalid/unavailable
10. probability above 1 -> invalid/unavailable
11. raw prototype status preserved
12. calibration warning included
13. chronological evaluation warning included
14. operational flag always false
15. thresholds loaded from configuration
16. invalid threshold configuration rejected
17. reason codes deterministic
18. explanation matches decision
19. API endpoint returns correct structure
20. existing forecast endpoint still works
"""
import pytest
import math
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.ml.decision_engine import (
    PrototypeDecisionEngine,
    validate_decision_thresholds,
    get_decision_thresholds_from_config,
    REASON_LOW_RISK,
    REASON_MEDIUM_RISK,
    REASON_HIGH_RISK,
    REASON_PROTOTYPE_RAW,
    REASON_CALIBRATION_NOT_VALIDATED,
    REASON_EVALUATION_LIMITED,
    REASON_INSUFFICIENT_DATA,
    SCIENTIFIC_WARNING
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def engine():
    return PrototypeDecisionEngine()


# 1. probability 0.00 -> SOW_NOW
def test_probability_zero_decision(engine):
    res = engine.evaluate(0.00)
    assert res["decision"] == "SOW_NOW"
    assert res["probability"] == 0.00
    assert REASON_LOW_RISK in res["reason_codes"]


# 2. probability 0.29 -> SOW_NOW
def test_probability_below_low_threshold(engine):
    res = engine.evaluate(0.29)
    assert res["decision"] == "SOW_NOW"
    assert res["probability"] == 0.29
    assert REASON_LOW_RISK in res["reason_codes"]


# 3. probability 0.30 -> SOW_PART_NOW
def test_probability_boundary_low_threshold(engine):
    res = engine.evaluate(0.30)
    assert res["decision"] == "SOW_PART_NOW"
    assert res["probability"] == 0.30
    assert REASON_MEDIUM_RISK in res["reason_codes"]


# 4. probability 0.59 -> SOW_PART_NOW
def test_probability_below_high_threshold(engine):
    res = engine.evaluate(0.59)
    assert res["decision"] == "SOW_PART_NOW"
    assert res["probability"] == 0.59
    assert REASON_MEDIUM_RISK in res["reason_codes"]


# 5. probability 0.60 -> WAIT
def test_probability_boundary_high_threshold(engine):
    res = engine.evaluate(0.60)
    assert res["decision"] == "WAIT"
    assert res["probability"] == 0.60
    assert REASON_HIGH_RISK in res["reason_codes"]


# 6. probability 1.00 -> WAIT
def test_probability_one_decision(engine):
    res = engine.evaluate(1.00)
    assert res["decision"] == "WAIT"
    assert res["probability"] == 1.00
    assert REASON_HIGH_RISK in res["reason_codes"]


# 7. null probability -> UNAVAILABLE
def test_null_probability_decision(engine):
    res = engine.evaluate(None)
    assert res["decision"] == "UNAVAILABLE"
    assert res["decision_status"] == "INSUFFICIENT_DATA"
    assert res["probability"] is None
    assert REASON_INSUFFICIENT_DATA in res["reason_codes"]


# 8. NaN probability -> UNAVAILABLE
def test_nan_probability_decision(engine):
    res = engine.evaluate(float("nan"))
    assert res["decision"] == "UNAVAILABLE"
    assert res["decision_status"] == "INSUFFICIENT_DATA"
    assert res["probability"] is None
    assert REASON_INSUFFICIENT_DATA in res["reason_codes"]


# 9. probability below 0 -> invalid/unavailable
def test_negative_probability_decision(engine):
    res = engine.evaluate(-0.05)
    assert res["decision"] == "UNAVAILABLE"
    assert res["decision_status"] == "INSUFFICIENT_DATA"
    assert res["probability"] is None
    assert REASON_INSUFFICIENT_DATA in res["reason_codes"]


# 10. probability above 1 -> invalid/unavailable
def test_excessive_probability_decision(engine):
    res = engine.evaluate(1.05)
    assert res["decision"] == "UNAVAILABLE"
    assert res["decision_status"] == "INSUFFICIENT_DATA"
    assert res["probability"] is None
    assert REASON_INSUFFICIENT_DATA in res["reason_codes"]


# 11. raw prototype status preserved
def test_raw_prototype_status_preserved(engine):
    res = engine.evaluate(0.15, probability_status="RAW_PROTOTYPE")
    assert res["probability_status"] == "RAW_PROTOTYPE"
    assert REASON_PROTOTYPE_RAW in res["reason_codes"]


# 12. calibration warning included
def test_calibration_warning_included(engine):
    res = engine.evaluate(0.20, calibration_status="INSUFFICIENT_CALIBRATION_DATA")
    assert REASON_CALIBRATION_NOT_VALIDATED in res["reason_codes"]
    assert "scientific_warning" in res
    assert "uncalibrated prototype probability" in res["scientific_warning"]


# 13. chronological evaluation warning included
def test_chronological_evaluation_warning_included(engine):
    res = engine.evaluate(0.40, evaluation_status="INSUFFICIENT_EVENT_VARIATION")
    assert REASON_EVALUATION_LIMITED in res["reason_codes"]


# 14. operational flag always false
def test_operational_flag_always_false(engine):
    for p in [0.0, 0.25, 0.50, 0.75, 1.0, None, -0.1]:
        res = engine.evaluate(p)
        assert res["is_operational"] is False
        assert res["decision_status"] in ("PROTOTYPE_ONLY", "INSUFFICIENT_DATA")


# 15. thresholds loaded from configuration
def test_thresholds_loaded_from_configuration():
    thresholds = get_decision_thresholds_from_config()
    assert "low_risk_max" in thresholds
    assert "high_risk_min" in thresholds
    assert thresholds["low_risk_max"] == 0.30
    assert thresholds["high_risk_min"] == 0.60


# 16. invalid threshold configuration rejected
def test_invalid_threshold_configuration_rejected():
    with pytest.raises(ValueError):
        validate_decision_thresholds(low_risk_max=0.70, high_risk_min=0.30)

    with pytest.raises(ValueError):
        validate_decision_thresholds(low_risk_max=-0.10, high_risk_min=0.50)

    with pytest.raises(ValueError):
        validate_decision_thresholds(low_risk_max=0.30, high_risk_min=1.20)

    with pytest.raises(ValueError):
        validate_decision_thresholds(low_risk_max=0.50, high_risk_min=0.50)


# 17. reason codes deterministic
def test_reason_codes_deterministic(engine):
    res1 = engine.evaluate(0.18)
    res2 = engine.evaluate(0.18)
    assert res1["reason_codes"] == res2["reason_codes"]
    assert res1["reason_codes"] == [
        REASON_LOW_RISK,
        REASON_PROTOTYPE_RAW,
        REASON_CALIBRATION_NOT_VALIDATED,
        REASON_EVALUATION_LIMITED
    ]


# 18. explanation matches decision
def test_explanation_matches_decision(engine):
    res_low = engine.evaluate(0.10)
    assert "below the configured low-risk threshold" in res_low["explanation"]

    res_med = engine.evaluate(0.45)
    assert "moderate-risk range" in res_med["explanation"]

    res_high = engine.evaluate(0.80)
    assert "above the configured high-risk threshold" in res_high["explanation"]


# 19. API endpoint returns correct structure
def test_api_decision_endpoint(client):
    res = client.get("/api/forecast/BLK001/false-onset/decision")
    assert res.status_code == 200
    data = res.json()

    assert data["block_id"] == "BLK001"
    assert data["target"] == "FALSE_ONSET"
    assert data["horizon_days"] == 7
    assert "probability" in data
    assert data["probability_status"] == "RAW_PROTOTYPE"
    assert data["decision"] in ("SOW_NOW", "SOW_PART_NOW", "WAIT")
    assert data["decision_status"] == "PROTOTYPE_ONLY"
    assert "thresholds" in data
    assert data["thresholds"]["low_risk_max"] == 0.30
    assert data["thresholds"]["high_risk_min"] == 0.60
    assert isinstance(data["reason_codes"], list)
    assert len(data["reason_codes"]) >= 2
    assert "explanation" in data
    assert "scientific_warning" in data
    assert data["is_operational"] is False


# 20. existing forecast endpoint still works
def test_existing_forecast_endpoint_preserved(client):
    res = client.get("/api/forecast/BLK001/false-onset")
    assert res.status_code == 200
    data = res.json()

    assert data["block_id"] == "BLK001"
    assert "probability" in data
    assert "raw_probability" in data
    assert "calibrated_probability" in data
    assert data["is_operational_forecast"] is False
    assert "scientific_warning" in data
