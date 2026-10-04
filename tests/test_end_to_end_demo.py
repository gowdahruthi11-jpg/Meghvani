"""
Meghvani Phase 7A: End-to-End Demonstration and SIH Verification Tests.

Verifies:
1. Complete 10-stage pipeline connectivity
2. Deterministic demo replay boundaries (source='DEMO_REPLAY', mode='HISTORICAL_REPLAY', is_operational=False)
3. Safety invariants: external_dispatch=False, no automated retraining, no model file modifications
4. Demo API endpoints (/api/demo/run, /api/demo/status, /api/demo/reset)
"""
from datetime import date
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.models.alert_log import AlertLog
from app.models.farmer_observation import FarmerObservation
from app.services.demo_service import DemoService, DEMO_PHONE_NUMBER
from app.advisory.models import AdvisoryStatus, ValidationStatus
from app.advisory.rule_engine import AdvisoryRuleEngine
from app.advisory.rule_registry import default_rule_registry

ML_MODELS_DIR = Path(__file__).resolve().parent.parent / "ml" / "models"


# 1. Demo farmer creation & profile
def test_demo_farmer_profile(db_session: Session):
    farmer = DemoService.get_or_create_demo_farmer(db_session)
    assert farmer is not None
    assert farmer.phone_number == DEMO_PHONE_NUMBER
    assert farmer.preferred_language == "Marathi"
    assert farmer.crop_id == 1  # Soybean
    assert farmer.block_id == 1  # Nagpur Rural
    assert farmer.village_id == 1  # Kalmeshwar


# 2. Farmer consent verified
def test_demo_farmer_consent(db_session: Session):
    farmer = DemoService.get_or_create_demo_farmer(db_session)
    assert farmer.consent is True
    assert farmer.active is True
    assert farmer.consent_timestamp is not None


# 3. Forecast replay creation
def test_forecast_replay_creation():
    fixture = DemoService.get_demo_forecast_fixture("BLK001")
    assert fixture["block_id"] == "BLK001"
    assert fixture["event_type"] == "FALSE_ONSET"
    assert fixture["probability"] == 0.20
    assert fixture["horizon_days"] == 7


# 4. Forecast marked non-operational
def test_forecast_marked_non_operational():
    fixture = DemoService.get_demo_forecast_fixture("BLK001")
    assert fixture["is_operational"] is False
    assert fixture["source"] == "DEMO_REPLAY"
    assert fixture["mode"] == "HISTORICAL_REPLAY"
    assert fixture["scientific_status"] == "NON_OPERATIONAL_DEMO"


# 5. Decision engine receives forecast and 6. generates SOW_NOW
def test_decision_engine_receives_forecast(db_session: Session):
    res = DemoService.run_demo_pipeline(db_session, probability_override=0.20)
    decision = res["stages"]["3_decision"]
    assert decision["decision"] == "SOW_NOW"
    assert decision["decision_engine_status"] == "PROTOTYPE"
    assert decision["probability"] == 0.20


# 7. Validated rule is selected
def test_validated_rule_is_selected(db_session: Session):
    res = DemoService.run_demo_pipeline(db_session, probability_override=0.20)
    adv = res["stages"]["4_advisory"]
    assert adv["validation_status"] == "VALIDATED"
    assert adv["advisory_status"] == "RULE_MATCHED"
    assert "CRIDA" in adv["source_institution"] or "PDKV" in adv["source_institution"]


# 8. Unvalidated rules are rejected
def test_unvalidated_rules_rejected():
    adv_engine = AdvisoryRuleEngine(registry=default_rule_registry)
    # Query with non-validated decision or unsupported crop
    adv_res = adv_engine.evaluate(
        crop_id="dragonfruit",
        decision="SOW_NOW",
        probability=0.20,
        block_id="BLK001",
        geography="Maharashtra",
        language="en"
    )
    assert adv_res.advisory_status != AdvisoryStatus.RULE_MATCHED or adv_res.validation_status != ValidationStatus.VALIDATED


# 9. Marathi message generated
def test_marathi_message_generated(db_session: Session):
    res = DemoService.run_demo_pipeline(db_session, probability_override=0.20, language="mr")
    msg = res["stages"]["5_message"]
    assert msg["language"] == "mr"
    assert "सोयाबीन" in msg["message_text"] or "मेघवाणी" in msg["message_text"]


# 10. Alert preview works
def test_alert_preview_endpoint(client: TestClient, db_session: Session):
    farmer = DemoService.get_or_create_demo_farmer(db_session)
    payload = {
        "farmer_id": farmer.id,
        "crop_id": "soybean",
        "language": "mr",
        "severity": "INFO"
    }
    response = client.post("/api/alerts/preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["alert_status"] in ["READY_FOR_SIMULATION", "VALIDATED_RULE"]
    assert data["is_operational"] is False
    assert data["external_dispatch"] is False


# 11. Simulated alert works and 12. External dispatch remains false
def test_simulated_alert_external_dispatch_false(db_session: Session):
    res = DemoService.run_demo_pipeline(db_session)
    comm = res["stages"]["6_communication"]
    assert comm["status"] == "SIMULATED_SENT"
    assert comm["external_dispatch"] is False
    assert res["external_dispatch"] is False
    assert res["is_operational"] is False


# 13. Alert log created in database
def test_alert_log_created_in_database(db_session: Session):
    res = DemoService.run_demo_pipeline(db_session)
    alert_id = res["stages"]["6_communication"]["alert_id"]
    assert alert_id is not None
    log = db_session.query(AlertLog).filter(AlertLog.id == alert_id).first()
    assert log is not None
    assert log.status == "SIMULATED_SENT"
    assert log.external_dispatch is False


# 14. Farmer observation created (source = FARMER)
def test_farmer_observation_created(db_session: Session):
    res = DemoService.run_demo_pipeline(db_session, observation_type="RAIN")
    obs = res["stages"]["7_observation"]
    assert obs["observation_type"] == "RAIN"
    assert obs["source"] == "FARMER"


# 15. Observation validation works (AGREEMENT)
def test_observation_validation_agreement(db_session: Session):
    res = DemoService.run_demo_pipeline(db_session, observation_type="RAIN")
    obs = res["stages"]["7_observation"]
    assert obs["validation_status"] == "AGREEMENT"
    assert obs["reference_rainfall_mm"] == 15.5
    assert obs["automated_retraining_triggered"] is False


# 16. Officer can retrieve the resulting record
def test_officer_can_retrieve_demo_record(client: TestClient, db_session: Session):
    # Run demo
    client.post("/api/demo/run")
    # Query demo status
    res = client.get("/api/demo/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status_indicators"]["forecast"] == "DEMO REPLAY"
    assert data["status_indicators"]["operational"] == "NO"
    assert data["safeguards"]["external_dispatch"] is False
    assert data["safeguards"]["automatic_retraining"] is False


# 17. Demo does not modify ML artifacts
def test_demo_does_not_modify_ml_artifacts(db_session: Session):
    if ML_MODELS_DIR.exists():
        model_files = list(ML_MODELS_DIR.glob("*.*"))
        mtimes_before = {f: f.stat().st_mtime for f in model_files}
    else:
        mtimes_before = {}

    DemoService.run_demo_pipeline(db_session)

    if ML_MODELS_DIR.exists():
        for f, mtime in mtimes_before.items():
            assert f.stat().st_mtime == mtime, f"Model file {f.name} was modified by demo run!"


# 18. Demo does not call external communication providers
def test_demo_safety_no_external_communication(db_session: Session):
    res = DemoService.run_demo_pipeline(db_session)
    assert res["external_dispatch"] is False
    assert res["is_operational"] is False
    assert res["status_indicators"]["communication"] == "SIMULATED"
    assert res["status_indicators"]["external_dispatch"] == "NO"


# 19. Demo API endpoints work
def test_demo_api_endpoints(client: TestClient):
    # Test POST /api/demo/run
    run_res = client.post("/api/demo/run", json={"probability": 0.20, "language": "mr", "observation_type": "RAIN"})
    assert run_res.status_code == 200
    data = run_res.json()
    assert data["status"] == "DEMO_COMPLETED"
    assert data["stages"]["3_decision"]["decision"] == "SOW_NOW"
    assert data["is_operational"] is False

    # Test GET /api/demo/status
    status_res = client.get("/api/demo/status")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["status_indicators"]["forecast"] == "DEMO REPLAY"

    # Test POST /api/demo/reset
    reset_res = client.post("/api/demo/reset")
    assert reset_res.status_code == 200
    assert reset_res.json()["status"] == "DEMO_RESET_COMPLETED"
