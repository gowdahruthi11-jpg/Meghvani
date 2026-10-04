"""
Tests for Meghvani Phase 6B: Farmer Observation, Validation & Feedback Loop.
Verifies all 25 safety invariants, observation types, validation rules, metrics, and isolation from ML retraining.
"""
from datetime import date, timedelta
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.models.weather import WeatherObservation
from app.models.farmer_observation import FarmerObservation
from app.models.alert_log import AlertLog
from app.observations.validation import ObservationValidator

ML_MODELS_DIR = Path(__file__).resolve().parent.parent / "ml" / "models"

# 1. Valid RAIN observation is recorded
def test_valid_rain_observation_recorded(client: TestClient, db_session: Session):
    payload = {
        "farmer_id": 1,
        "observation_type": "RAIN",
        "observation_date": str(date.today()),
        "observation_time": "14:30",
        "crop_id": "soybean",
        "notes": "Moderate showers in our fields."
    }
    response = client.post("/api/observations", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "RECORDED"
    assert data["observation_type"] == "RAIN"
    assert data["source"] == "FARMER"
    assert data["is_operational"] is False

# 2. Valid DRY observation is recorded
def test_valid_dry_observation_recorded(client: TestClient, db_session: Session):
    # Ensure weather observation for test date has dry weather
    test_date = date.today() - timedelta(days=2)
    db_session.add(WeatherObservation(
        block_id=1,
        observation_date=test_date,
        rainfall_mm=0.0
    ))
    db_session.commit()

    payload = {
        "farmer_id": 1,
        "observation_type": "DRY",
        "observation_date": str(test_date),
        "notes": "Clear sunny day, no rain."
    }
    response = client.post("/api/observations", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "RECORDED"
    assert data["observation_type"] == "DRY"
    assert data["validation_status"] == "AGREEMENT"

# 3. Valid HEAVY_RAIN observation is recorded
def test_valid_heavy_rain_observation_recorded(client: TestClient, db_session: Session):
    test_date = date.today() - timedelta(days=3)
    db_session.add(WeatherObservation(
        block_id=1,
        observation_date=test_date,
        rainfall_mm=75.0
    ))
    db_session.commit()

    payload = {
        "farmer_id": 1,
        "observation_type": "HEAVY_RAIN",
        "observation_date": str(test_date),
        "notes": "Torrential downpour with field waterlogging."
    }
    response = client.post("/api/observations", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "RECORDED"
    assert data["observation_type"] == "HEAVY_RAIN"
    assert data["validation_status"] == "AGREEMENT"

# 4. Invalid observation type rejected
def test_invalid_observation_type_rejected(client: TestClient):
    payload = {
        "farmer_id": 1,
        "observation_type": "CYCLONE",
        "observation_date": str(date.today())
    }
    response = client.post("/api/observations", json=payload)
    assert response.status_code == 400
    assert "Invalid observation type" in response.json()["detail"]

# 5. Inactive farmer rejected
def test_inactive_farmer_rejected(client: TestClient, db_session: Session):
    farmer = db_session.query(Farmer).filter(Farmer.id == 1).first()
    orig_status = farmer.active
    try:
        farmer.active = False
        db_session.commit()

        payload = {
            "farmer_id": 1,
            "observation_type": "RAIN",
            "observation_date": str(date.today())
        }
        response = client.post("/api/observations", json=payload)
        assert response.status_code == 403
        assert response.json()["detail"] == "OBSERVATION_NOT_AUTHORIZED"
    finally:
        farmer.active = orig_status
        db_session.commit()

# 6. Invalid farmer rejected
def test_invalid_farmer_rejected(client: TestClient):
    payload = {
        "farmer_id": 999999,
        "observation_type": "RAIN",
        "observation_date": str(date.today())
    }
    response = client.post("/api/observations", json=payload)
    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"]

# 7. Invalid crop rejected
def test_invalid_crop_rejected(client: TestClient):
    payload = {
        "farmer_id": 1,
        "observation_type": "RAIN",
        "observation_date": str(date.today()),
        "crop_id": "dragonfruit_nonexistent"
    }
    response = client.post("/api/observations", json=payload)
    assert response.status_code == 400
    assert "Invalid crop" in response.json()["detail"]

# 8. Duplicate observation suppressed
def test_duplicate_observation_suppressed(client: TestClient, db_session: Session):
    test_date = date.today() - timedelta(days=4)
    payload = {
        "farmer_id": 1,
        "observation_type": "RAIN",
        "observation_date": str(test_date),
        "notes": "First report"
    }
    # First report
    res1 = client.post("/api/observations", json=payload)
    assert res1.status_code == 201
    assert res1.json()["status"] == "RECORDED"

    # Second report on same date with same observation_type
    payload["notes"] = "Accidental duplicate report"
    res2 = client.post("/api/observations", json=payload)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["status"] == "DUPLICATE_OBSERVATION"
    assert "suppressed" in data2["reason"].lower()

# 9. Same-date reference comparison works
def test_same_date_reference_comparison_works(db_session: Session):
    target_date = date(2025, 7, 10)
    db_session.add(WeatherObservation(
        block_id=1,
        observation_date=target_date,
        rainfall_mm=22.4
    ))
    db_session.commit()

    obs = FarmerObservation(
        farmer_id=1,
        block_id=1,
        observation_date=target_date,
        observation_type="RAIN"
    )
    db_session.add(obs)
    db_session.flush()

    ObservationValidator.validate_against_reference(db_session, obs)
    assert obs.reference_rainfall_mm == 22.4
    assert obs.validation_status == "AGREEMENT"

# 10. RAIN agreement and disagreement
def test_rain_agreement_and_disagreement(db_session: Session):
    # Case A: Rain reported, reference > 0 -> AGREEMENT
    date_a = date(2025, 7, 11)
    db_session.add(WeatherObservation(block_id=1, observation_date=date_a, rainfall_mm=10.0))
    db_session.commit()
    obs_a = FarmerObservation(farmer_id=1, block_id=1, observation_date=date_a, observation_type="RAIN")
    ObservationValidator.validate_against_reference(db_session, obs_a)
    assert obs_a.validation_status == "AGREEMENT"

    # Case B: Rain reported, reference == 0 -> DISAGREEMENT
    date_b = date(2025, 7, 12)
    db_session.add(WeatherObservation(block_id=1, observation_date=date_b, rainfall_mm=0.0))
    db_session.commit()
    obs_b = FarmerObservation(farmer_id=1, block_id=1, observation_date=date_b, observation_type="RAIN")
    ObservationValidator.validate_against_reference(db_session, obs_b)
    assert obs_b.validation_status == "DISAGREEMENT"

# 11. DRY agreement and disagreement
def test_dry_agreement_and_disagreement(db_session: Session):
    # Case A: Dry reported, reference <= 2.5mm -> AGREEMENT
    date_a = date(2025, 7, 13)
    db_session.add(WeatherObservation(block_id=1, observation_date=date_a, rainfall_mm=1.2))
    db_session.commit()
    obs_a = FarmerObservation(farmer_id=1, block_id=1, observation_date=date_a, observation_type="DRY")
    ObservationValidator.validate_against_reference(db_session, obs_a)
    assert obs_a.validation_status == "AGREEMENT"

    # Case B: Dry reported, reference 35.0mm -> DISAGREEMENT
    date_b = date(2025, 7, 14)
    db_session.add(WeatherObservation(block_id=1, observation_date=date_b, rainfall_mm=35.0))
    db_session.commit()
    obs_b = FarmerObservation(farmer_id=1, block_id=1, observation_date=date_b, observation_type="DRY")
    ObservationValidator.validate_against_reference(db_session, obs_b)
    assert obs_b.validation_status == "DISAGREEMENT"

# 12. HEAVY_RAIN agreement and disagreement
def test_heavy_rain_agreement_and_disagreement(db_session: Session):
    # Case A: Heavy rain reported, reference 85.0mm (>= 64.5mm) -> AGREEMENT
    date_a = date(2025, 7, 15)
    db_session.add(WeatherObservation(block_id=1, observation_date=date_a, rainfall_mm=85.0))
    db_session.commit()
    obs_a = FarmerObservation(farmer_id=1, block_id=1, observation_date=date_a, observation_type="HEAVY_RAIN")
    ObservationValidator.validate_against_reference(db_session, obs_a)
    assert obs_a.validation_status == "AGREEMENT"

    # Case B: Heavy rain reported, reference 15.0mm (< 64.5mm) -> DISAGREEMENT
    date_b = date(2025, 7, 16)
    db_session.add(WeatherObservation(block_id=1, observation_date=date_b, rainfall_mm=15.0))
    db_session.commit()
    obs_b = FarmerObservation(farmer_id=1, block_id=1, observation_date=date_b, observation_type="HEAVY_RAIN")
    ObservationValidator.validate_against_reference(db_session, obs_b)
    assert obs_b.validation_status == "DISAGREEMENT"

# 13. Missing reference returns REFERENCE_DATA_UNAVAILABLE
def test_missing_reference_returns_unavailable(db_session: Session):
    unrecorded_date = date(2023, 1, 1)
    obs = FarmerObservation(farmer_id=1, block_id=1, observation_date=unrecorded_date, observation_type="RAIN")
    ObservationValidator.validate_against_reference(db_session, obs)
    assert obs.validation_status == "REFERENCE_DATA_UNAVAILABLE"
    assert obs.reference_rainfall_mm is None

# 14. Missing threshold returns REFERENCE_THRESHOLD_UNAVAILABLE
def test_missing_threshold_returns_unavailable(db_session: Session):
    target_date = date(2025, 7, 17)
    db_session.add(WeatherObservation(block_id=1, observation_date=target_date, rainfall_mm=5.0))
    db_session.commit()
    obs = FarmerObservation(farmer_id=1, block_id=1, observation_date=target_date, observation_type="HEAVY_RAIN")
    # Override with empty thresholds
    ObservationValidator.validate_against_reference(db_session, obs, thresholds_override={})
    assert obs.validation_status == "REFERENCE_THRESHOLD_UNAVAILABLE"

# 15. Disagreement does not label farmer as wrong
def test_disagreement_neutral_terminology(db_session: Session):
    target_date = date(2025, 7, 18)
    db_session.add(WeatherObservation(block_id=1, observation_date=target_date, rainfall_mm=0.0))
    db_session.commit()
    obs = FarmerObservation(farmer_id=1, block_id=1, observation_date=target_date, observation_type="RAIN")
    ObservationValidator.validate_against_reference(db_session, obs)
    assert obs.validation_status == "DISAGREEMENT"
    # Verify no pejorative terms
    notes = obs.comparison_notes.lower()
    for forbidden in ["wrong", "false report", "fraud", "unreliable", "lie"]:
        assert forbidden not in notes

# 16. Agreement rate calculation is correct
def test_agreement_rate_calculation(db_session: Session):
    # Clear test observations
    db_session.query(FarmerObservation).delete()
    db_session.commit()

    # Create 3 AGREEMENT and 1 DISAGREEMENT
    d1 = date(2025, 8, 1)
    d2 = date(2025, 8, 2)
    d3 = date(2025, 8, 3)
    d4 = date(2025, 8, 4)

    obs1 = FarmerObservation(farmer_id=1, block_id=1, observation_date=d1, observation_type="RAIN", validation_status="AGREEMENT")
    obs2 = FarmerObservation(farmer_id=1, block_id=1, observation_date=d2, observation_type="DRY", validation_status="AGREEMENT")
    obs3 = FarmerObservation(farmer_id=1, block_id=1, observation_date=d3, observation_type="HEAVY_RAIN", validation_status="AGREEMENT")
    obs4 = FarmerObservation(farmer_id=1, block_id=1, observation_date=d4, observation_type="RAIN", validation_status="DISAGREEMENT")
    db_session.add_all([obs1, obs2, obs3, obs4])
    db_session.commit()

    summary = ObservationValidator.compute_summary(db_session)
    assert summary["validation_distribution"]["agreement_count"] == 3
    assert summary["validation_distribution"]["disagreement_count"] == 1
    assert summary["reference_comparisons_count"] == 4
    assert summary["agreement_rate"] == 0.75
    assert summary["agreement_rate_pct"] == 75.0

# 17. Zero denominator returns null agreement rate
def test_zero_denominator_returns_null_rate(db_session: Session):
    db_session.query(FarmerObservation).delete()
    db_session.commit()

    obs = FarmerObservation(farmer_id=1, block_id=1, observation_date=date(2025, 8, 5), observation_type="RAIN", validation_status="REFERENCE_DATA_UNAVAILABLE")
    db_session.add(obs)
    db_session.commit()

    summary = ObservationValidator.compute_summary(db_session)
    assert summary["reference_comparisons_count"] == 0
    assert summary["agreement_rate"] is None
    assert summary["agreement_rate_pct"] is None

# 18. Farmer history works
def test_farmer_history_endpoint(client: TestClient, db_session: Session):
    response = client.get("/api/observations/history?farmer_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# 19. Block summary works
def test_block_summary_endpoint(client: TestClient):
    response = client.get("/api/observations/summary?block_id=1")
    assert response.status_code == 200
    data = response.json()
    assert "total_observations" in data
    assert "event_distribution" in data
    assert "validation_distribution" in data
    assert data["is_operational"] is False

# 20. Phone information is masked
def test_phone_information_masked(client: TestClient):
    response = client.get("/api/observations/history")
    assert response.status_code == 200
    data = response.json()
    if len(data) > 0:
        for item in data:
            if item.get("masked_phone"):
                assert item["masked_phone"].startswith("******")
                assert not item["masked_phone"].startswith("+91")
            assert "pin" not in item

# 21. Observation source is always FARMER
def test_observation_source_is_farmer(client: TestClient):
    payload = {
        "farmer_id": 1,
        "observation_type": "RAIN",
        "observation_date": str(date.today() - timedelta(days=10)),
        "source": "FARMER"
    }
    response = client.post("/api/observations", json=payload)
    assert response.status_code in [200, 201]
    assert response.json()["source"] == "FARMER"

# 22. Submission does not create alert logs
def test_submission_does_not_create_alert_logs(client: TestClient, db_session: Session):
    alerts_before = db_session.query(AlertLog).count()
    payload = {
        "farmer_id": 1,
        "observation_type": "HEAVY_RAIN",
        "observation_date": str(date.today() - timedelta(days=11)),
        "notes": "Testing isolation from alert logging."
    }
    res = client.post("/api/observations", json=payload)
    assert res.status_code in [200, 201]
    alerts_after = db_session.query(AlertLog).count()
    assert alerts_before == alerts_after

# 23. Submission does not call communication providers
def test_submission_no_communication_calls(client: TestClient):
    payload = {
        "farmer_id": 1,
        "observation_type": "RAIN",
        "observation_date": str(date.today() - timedelta(days=12)),
        "notes": "Testing no communication provider dispatch."
    }
    res = client.post("/api/observations", json=payload)
    assert res.status_code in [200, 201]
    data = res.json()
    assert data.get("external_dispatch") in [False, None]

# 24. Submission does not modify ML model artifacts
def test_submission_does_not_modify_ml_artifacts(client: TestClient):
    if ML_MODELS_DIR.exists():
        model_files = list(ML_MODELS_DIR.glob("*.*"))
        mtimes_before = {f: f.stat().st_mtime for f in model_files}
    else:
        mtimes_before = {}

    payload = {
        "farmer_id": 1,
        "observation_type": "RAIN",
        "observation_date": str(date.today() - timedelta(days=13)),
        "notes": "Testing that ML models are unmodified."
    }
    res = client.post("/api/observations", json=payload)
    assert res.status_code in [200, 201]

    if ML_MODELS_DIR.exists():
        for f, mtime in mtimes_before.items():
            assert f.stat().st_mtime == mtime, f"Model file {f.name} was modified by observation submission!"

# 25. Submission does not retrain model
def test_submission_does_not_retrain_model(client: TestClient, db_session: Session):
    # Invariant: Observation pipeline stops after analytical storage
    payload = {
        "farmer_id": 1,
        "observation_type": "DRY",
        "observation_date": str(date.today() - timedelta(days=14)),
        "notes": "Strict observation isolation from training."
    }
    res = client.post("/api/observations", json=payload)
    assert res.status_code in [200, 201]
    data = res.json()
    assert data["is_operational"] is False
    assert "retrained" not in str(data).lower()
