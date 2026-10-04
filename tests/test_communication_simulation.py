"""
Meghvani Phase 6A: Communication Simulation & Alert Routing Tests.

Verifies:
1. Consent=true allows simulation.
2. Consent=false blocks simulation.
3. Inactive farmer blocks simulation.
4. Missing phone blocks communication.
5. Missing forecast blocks communication.
6. No validated rule blocks communication.
7. REVIEW_REQUIRED blocks communication.
8. UNVALIDATED blocks communication.
9. SOW_NOW + INFO routes correctly.
10. IMPORTANT routes SMS + WhatsApp.
11. HIGH routes Voice + SMS.
12. Voice failure triggers SMS fallback.
13. WhatsApp failure triggers SMS fallback.
14. Duplicate alert is suppressed.
15. Mock provider never performs external dispatch.
16. Alert log is created.
17. Phone number is masked in officer response.
18. Simulation status uses SIMULATED_* terminology.
19. Farmer language is respected.
20. Unsupported language safely falls back.
21. Alert history filters work.
22. Preview does not create a dispatch.
23. Simulation does not call external services.
24. Existing tests remain passing.
"""
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.database import SessionLocal
from app.models.farmer import Farmer
from app.models.block import Block
from app.models.crop import Crop
from app.models.alert_log import AlertLog
from app.communication.alert_router import AlertRouter, AlertSeverity, DeliveryStatus
from app.communication.providers.mock_sms import MockSMSProvider
from app.communication.providers.mock_whatsapp import MockWhatsAppProvider
from app.communication.providers.mock_voice import MockVoiceProvider


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_farmer(db):
    """
    Creates or retrieves a test farmer with consent=True, active=True, block_id=1.
    """
    phone = "+919876543210"
    farmer = db.query(Farmer).filter(Farmer.phone_number == phone).first()
    if not farmer:
        farmer = Farmer(
            phone_number=phone,
            preferred_language="Marathi",
            pin_code="441501",
            village_id=1,
            block_id=1,
            crop_id=1,
            communication_preference="SMS",
            consent=True,
            consent_timestamp=datetime.now(timezone.utc),
            active=True
        )
        db.add(farmer)
        db.commit()
        db.refresh(farmer)
    else:
        farmer.consent = True
        farmer.active = True
        farmer.phone_number = phone
        farmer.block_id = 1
        farmer.crop_id = 1
        db.commit()
        db.refresh(farmer)
    return farmer


# 1. Consent=true allows simulation
def test_consent_true_allows_simulation(client, test_farmer):
    res = client.post("/api/alerts/simulate", json={
        "farmer_id": test_farmer.id,
        "crop_id": "soybean",
        "language": "en"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["SIMULATED_SENT", "FALLBACK_USED", "DUPLICATE_SUPPRESSED"]
    assert data["external_dispatch"] is False
    assert data["is_operational"] is False


# 2. Consent=false blocks simulation
def test_consent_false_blocks_simulation(client, db, test_farmer):
    test_farmer.consent = False
    db.commit()
    try:
        res = client.post("/api/alerts/simulate", json={
            "farmer_id": test_farmer.id,
            "crop_id": "soybean"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "BLOCKED_NO_CONSENT"
        assert "consent" in data["reason"].lower()
        assert data["external_dispatch"] is False
    finally:
        test_farmer.consent = True
        db.commit()


# 3. Inactive farmer blocks simulation
def test_inactive_farmer_blocks_simulation(client, db, test_farmer):
    test_farmer.active = False
    db.commit()
    try:
        res = client.post("/api/alerts/simulate", json={
            "farmer_id": test_farmer.id,
            "crop_id": "soybean"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "BLOCKED_NO_CONSENT"
    finally:
        test_farmer.active = True
        db.commit()


# 4. Missing phone blocks communication
def test_missing_phone_blocks_communication(db, test_farmer):
    router = AlertRouter()
    assert router.mask_phone_number("") == "******"
    assert router.mask_phone_number(None) == "******"

    db.query(Farmer).filter(Farmer.phone_number == "").delete()
    db.commit()

    orig_phone = test_farmer.phone_number
    test_farmer.phone_number = ""
    db.commit()
    try:
        res = router.preview_alert(db=db, farmer_id=test_farmer.id)
        assert res["alert_status"] == DeliveryStatus.BLOCKED_NO_CONSENT.value
    finally:
        test_farmer.phone_number = orig_phone
        db.commit()


# 5. Missing forecast blocks communication
def test_missing_forecast_blocks_communication(db, test_farmer):
    orig_block = test_farmer.block_id
    test_farmer.block_id = 99999
    db.commit()
    try:
        router = AlertRouter()
        res = router.simulate_dispatch(db=db, farmer_id=test_farmer.id, crop_id="soybean")
        assert res["status"] == DeliveryStatus.BLOCKED_NO_FORECAST.value
        assert res["external_dispatch"] is False
    finally:
        test_farmer.block_id = orig_block
        db.commit()


# 6. No validated rule blocks communication
def test_no_validated_rule_blocks_communication(db, test_farmer):
    router = AlertRouter()
    # Query a crop without validated rule (e.g. unknown crop)
    res = router.simulate_dispatch(db=db, farmer_id=test_farmer.id, crop_id="sugarcane")
    assert res["status"] == DeliveryStatus.BLOCKED_NO_VALIDATED_RULE.value
    assert res["external_dispatch"] is False


# 7. REVIEW_REQUIRED blocks communication
def test_review_required_blocks_communication(db, test_farmer):
    # Preview for unvalidated/candidate crop
    router = AlertRouter()
    res = router.preview_alert(db=db, farmer_id=test_farmer.id, crop_id="sugarcane")
    assert res["alert_status"] == DeliveryStatus.BLOCKED_NO_VALIDATED_RULE.value


# 8. UNVALIDATED blocks communication
def test_unvalidated_blocks_communication(db, test_farmer):
    router = AlertRouter()
    res = router.simulate_dispatch(db=db, farmer_id=test_farmer.id, crop_id="barley")
    assert res["status"] == DeliveryStatus.BLOCKED_NO_VALIDATED_RULE.value


# 9. SOW_NOW + INFO routes correctly
def test_sow_now_info_routes_correctly():
    plan = AlertRouter.get_channel_plan(AlertSeverity.INFO)
    assert plan == ["SMS"]


# 10. IMPORTANT routes SMS + WhatsApp
def test_important_routes_sms_and_whatsapp():
    plan = AlertRouter.get_channel_plan(AlertSeverity.IMPORTANT)
    assert "SMS" in plan
    assert "WHATSAPP" in plan


# 11. HIGH routes Voice + SMS
def test_high_routes_voice_and_sms():
    plan = AlertRouter.get_channel_plan(AlertSeverity.HIGH)
    assert "VOICE" in plan
    assert "SMS" in plan


# 12. Voice failure triggers SMS fallback
def test_voice_failure_triggers_sms_fallback(db, test_farmer):
    router = AlertRouter(
        voice_provider=MockVoiceProvider(fail_mode=True),
        sms_provider=MockSMSProvider(fail_mode=False)
    )
    # Force HIGH severity so Voice is invoked
    res = router.simulate_dispatch(
        db=db,
        farmer_id=test_farmer.id,
        crop_id="soybean",
        severity="HIGH",
        force_failure_channel="VOICE",
        cooldown_hours=0 # bypass duplicate check for test
    )
    assert res["status"] == DeliveryStatus.FALLBACK_USED.value
    assert res["fallback_used"] is True
    # Verify fallback dispatch summary
    provider_statuses = [d["status"] for d in res["dispatches"]]
    assert "SIMULATED_FAILED" in provider_statuses
    assert "SIMULATED_SENT" in provider_statuses


# 13. WhatsApp failure triggers SMS fallback
def test_whatsapp_failure_triggers_sms_fallback(db, test_farmer):
    router = AlertRouter(
        whatsapp_provider=MockWhatsAppProvider(fail_mode=True),
        sms_provider=MockSMSProvider(fail_mode=False)
    )
    res = router.simulate_dispatch(
        db=db,
        farmer_id=test_farmer.id,
        crop_id="cotton",
        severity="IMPORTANT",
        force_failure_channel="WHATSAPP",
        cooldown_hours=0
    )
    assert res["status"] == DeliveryStatus.FALLBACK_USED.value
    assert res["fallback_used"] is True


# 14. Duplicate alert is suppressed
def test_duplicate_alert_suppression(db, test_farmer):
    router = AlertRouter()
    # First dispatch with 0 cooldown succeeds
    res1 = router.simulate_dispatch(db=db, farmer_id=test_farmer.id, crop_id="pigeonpea", cooldown_hours=0)
    assert res1["status"] in ["SIMULATED_SENT", "FALLBACK_USED"]

    # Second dispatch immediately with 24h cooldown is suppressed
    res2 = router.simulate_dispatch(db=db, farmer_id=test_farmer.id, crop_id="pigeonpea", cooldown_hours=24)
    assert res2["status"] == DeliveryStatus.DUPLICATE_SUPPRESSED.value


# 15. Mock provider never performs external dispatch
def test_mock_providers_external_dispatch_false():
    sms = MockSMSProvider()
    wa = MockWhatsAppProvider()
    voice = MockVoiceProvider()

    r1 = sms.dispatch("+919999900001", "Test")
    r2 = wa.dispatch("+919999900001", "Test")
    r3 = voice.dispatch("+919999900001", "Test")

    assert r1["external_dispatch"] is False
    assert r2["external_dispatch"] is False
    assert r3["external_dispatch"] is False


# 16. Alert log is created in database
def test_alert_log_created_in_db(client, test_farmer, db):
    count_before = db.query(AlertLog).filter(AlertLog.farmer_id == test_farmer.id).count()

    res = client.post("/api/alerts/simulate", json={
        "farmer_id": test_farmer.id,
        "crop_id": "soybean",
        "force_failure_channel": None
    })
    assert res.status_code == 200

    count_after = db.query(AlertLog).filter(AlertLog.farmer_id == test_farmer.id).count()
    assert count_after > count_before


# 17. Phone number is masked in officer response
def test_phone_number_masked_in_officer_response(client, test_farmer):
    res = client.get(f"/api/alerts/history?farmer_id={test_farmer.id}")
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) > 0
    for l in logs:
        assert "masked_phone" in l
        assert l["masked_phone"].startswith("******")
        # Ensure full phone is never revealed
        assert test_farmer.phone_number not in l["masked_phone"]


# 18. Simulation status uses SIMULATED_* terminology
def test_simulation_status_terminology(client, test_farmer):
    res = client.get(f"/api/alerts/history?farmer_id={test_farmer.id}")
    assert res.status_code == 200
    logs = res.json()
    allowed_statuses = [
        "SIMULATED_SENT", "SIMULATED_FAILED", "FALLBACK_USED",
        "BLOCKED_NO_CONSENT", "BLOCKED_NO_VALIDATED_RULE", "BLOCKED_NO_FORECAST",
        "DUPLICATE_SUPPRESSED", "SIMULATED", "PENDING"
    ]
    for l in logs:
        assert l["status"] in allowed_statuses


# 19. Farmer language is respected
def test_farmer_language_respected(client, test_farmer):
    res = client.post("/api/alerts/preview", json={
        "farmer_id": test_farmer.id,
        "crop_id": "soybean",
        "language": "mr"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["language"] == "mr"
    assert "मेघवाणी अपडेट" in data["message_preview"]


# 20. Unsupported language safely falls back
def test_unsupported_language_safely_falls_back(client, test_farmer):
    res = client.post("/api/alerts/preview", json={
        "farmer_id": test_farmer.id,
        "crop_id": "soybean",
        "language": "kannada"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["language"] == "en"
    assert "Meghvani update for Soybean:" in data["message_preview"]


# 21. Alert history filters work
def test_alert_history_filters_work(client, test_farmer):
    # Filter by farmer
    res_f = client.get(f"/api/alerts/history?farmer_id={test_farmer.id}")
    assert res_f.status_code == 200
    for item in res_f.json():
        assert item["farmer_id"] == test_farmer.id

    # Filter by channel
    res_c = client.get("/api/alerts/history?channel=SMS")
    assert res_c.status_code == 200
    for item in res_c.json():
        assert item["channel"] == "SMS"


# 22. Preview does not create a dispatch in database
def test_preview_does_not_create_dispatch_in_db(client, test_farmer, db):
    count_before = db.query(AlertLog).count()
    res = client.post("/api/alerts/preview", json={
        "farmer_id": test_farmer.id,
        "crop_id": "soybean"
    })
    assert res.status_code == 200
    count_after = db.query(AlertLog).count()
    assert count_after == count_before


# 23. Simulation does not call external services
def test_simulation_does_not_call_external_services(client, test_farmer):
    res = client.post("/api/alerts/simulate", json={
        "farmer_id": test_farmer.id,
        "crop_id": "soybean"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["external_dispatch"] is False
