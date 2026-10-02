from fastapi.testclient import TestClient
from app.communication.mock_provider import MockSMSProvider, MockVoiceProvider, MockWhatsAppProvider
from app.services.alert_service import AlertService
from app.models.farmer import Farmer

def test_mock_sms_provider():
    provider = MockSMSProvider()
    res = provider.send("+919800000001", "Test SMS message")
    assert res["status"] == "SIMULATED"
    assert res["channel"] == "SMS"
    assert res["provider_message_id"].startswith("mock-sms-")

def test_mock_voice_provider_normal_and_no_answer():
    provider_normal = MockVoiceProvider(force_no_answer=False, no_answer_rate=0.0)
    res_ok = provider_normal.call("+919800000001", "Voice alert test")
    assert res_ok["status"] == "SIMULATED"

    provider_unanswered = MockVoiceProvider(force_no_answer=True)
    res_missed = provider_unanswered.call("+919800000001", "Voice alert test")
    assert res_missed["status"] == "NO_ANSWER"

def test_mock_whatsapp_provider():
    provider = MockWhatsAppProvider()
    res = provider.send("+919800000001", "Test WhatsApp advisory")
    assert res["status"] == "SIMULATED"
    assert res["channel"] == "WHATSAPP"

def test_alert_simulation_api(client: TestClient):
    payload = {
        "block_id": 1,
        "alert_type": "ONSET",
        "risk_level": "NORMAL",
        "override_message": "Test Normal Risk SMS alert"
    }
    response = client.post("/api/alerts/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_farmers_targeted"] >= 1
    assert len(data["dispatches"]) >= 1
    assert data["dispatches"][0]["channel"] == "SMS"

def test_voice_retry_and_fallback_to_sms(db_session):
    farmer = db_session.query(Farmer).filter(Farmer.id == 1).first()
    # Force voice calls to fail/no_answer to test automatic SMS fallback
    logs = AlertService.dispatch_alert_to_farmer(
        db=db_session,
        farmer=farmer,
        alert_type="HEAVY_RAIN",
        risk_level="HIGH_RISK",
        message="Critical rainfall warning",
        force_voice_no_answer=True
    )

    channels_used = [l.channel for l in logs]
    statuses = [l.status for l in logs]

    # Voice calls attempted and logged as NO_ANSWER
    assert "VOICE" in channels_used
    assert "NO_ANSWER" in statuses

    # SMS fallback was automatically dispatched
    fallback_logs = [l for l in logs if l.channel == "SMS" and "Fallback SMS" in l.message]
    assert len(fallback_logs) >= 1
    assert fallback_logs[0].status == "SIMULATED"
