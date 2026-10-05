import random
import uuid
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from app.communication.sms import get_sms_provider
from app.communication.mock_provider import MockSMSProvider
from app.communication.twilio_sms import (
    TwilioSMSProvider,
    normalize_phone_number,
    mask_phone_number,
    verify_twilio_signature
)
from app.models.inbound_message import InboundMessage
from app.models.alert_log import AlertLog
from app.models.farmer import Farmer


def _gen_phone() -> str:
    """Generates a random, valid 10-digit Indian mobile number."""
    return f"+9198{random.randint(10000000, 99999999)}"


def test_1_inbound_megh(client: TestClient, db_session):
    """1. Test inbound SMS with body MEGH triggers LANGUAGE prompt."""
    phone = _gen_phone()
    res = client.post(
        "/api/communication/sms/incoming",
        data={"From": phone, "Body": "MEGH", "MessageSid": f"SM_{uuid.uuid4().hex}"}
    )
    assert res.status_code == 200
    assert "xml" in res.headers.get("content-type", "")

    # Check InboundMessage record
    in_msg = db_session.query(InboundMessage).filter(InboundMessage.from_phone == phone).first()
    assert in_msg is not None
    assert in_msg.registration_step_after == "LANGUAGE"
    assert "Select language" in in_msg.reply_message


def test_2_language_selection(client: TestClient, db_session):
    """2. Test language selection step in registration."""
    phone = _gen_phone()
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "MEGH"})
    
    # Select Hindi (1)
    res = client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "1"})
    assert res.status_code == 200

    in_msg = db_session.query(InboundMessage).filter(
        InboundMessage.from_phone == phone,
        InboundMessage.message_body == "1"
    ).first()
    assert in_msg is not None
    assert in_msg.registration_step_after == "PIN"
    assert "PIN code" in in_msg.reply_message


def test_3_pin_entry(client: TestClient, db_session):
    """3. Test valid PIN code submission."""
    phone = _gen_phone()
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "MEGH"})
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "1"})
    
    res = client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "441501"})
    assert res.status_code == 200

    in_msg = db_session.query(InboundMessage).filter(
        InboundMessage.from_phone == phone,
        InboundMessage.message_body == "441501"
    ).first()
    assert in_msg is not None
    assert in_msg.registration_step_after == "VILLAGE"
    assert "Kalmeshwar" in in_msg.reply_message


def test_4_village_selection(client: TestClient, db_session):
    """4. Test village selection step."""
    phone = _gen_phone()
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "MEGH"})
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "1"})
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "441501"})

    res = client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "1"})
    assert res.status_code == 200

    in_msg = db_session.query(InboundMessage).filter(
        InboundMessage.from_phone == phone,
        InboundMessage.message_body == "1",
        InboundMessage.registration_step_before == "VILLAGE"
    ).first()
    assert in_msg is not None
    assert in_msg.registration_step_after == "CROP"
    assert "main crop" in in_msg.reply_message


def test_5_crop_selection(client: TestClient, db_session):
    """5. Test crop selection step."""
    phone = _gen_phone()
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "MEGH"})
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "1"})
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "441501"})
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "1"})

    # Select crop 1 (Soybean)
    res = client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "1"})
    assert res.status_code == 200

    in_msg = db_session.query(InboundMessage).filter(
        InboundMessage.from_phone == phone,
        InboundMessage.registration_step_before == "CROP"
    ).first()
    assert in_msg is not None
    assert in_msg.registration_step_after == "CONSENT"
    assert "Reply YES to continue" in in_msg.reply_message


def test_6_consent_and_7_completion(client: TestClient, db_session):
    """6 & 7. Test consent step and farmer registration completion."""
    phone = _gen_phone()
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "MEGH"})
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "1"})
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "441501"})
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "1"})
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "1"})

    # Consent YES
    res = client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "YES"})
    assert res.status_code == 200

    in_msg = db_session.query(InboundMessage).filter(
        InboundMessage.from_phone == phone,
        InboundMessage.message_body == "YES"
    ).first()
    assert in_msg is not None
    assert in_msg.registration_step_after == "COMPLETED"
    assert in_msg.farmer_id is not None
    assert "Registration successful" in in_msg.reply_message

    # Verify farmer exists in DB
    farmer = db_session.query(Farmer).filter(Farmer.id == in_msg.farmer_id).first()
    assert farmer is not None
    assert farmer.active is True
    assert farmer.preferred_language == "Hindi"


def test_8_already_registered_farmer(client: TestClient, db_session):
    """8. Test message from an already registered farmer."""
    phone = "+919800000001"  # Seeded farmer in conftest
    res = client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "HELLO"})
    assert res.status_code == 200

    in_msg = db_session.query(InboundMessage).filter(
        InboundMessage.from_phone == phone,
        InboundMessage.message_body == "HELLO"
    ).first()
    assert in_msg is not None
    assert in_msg.registration_step_after == "ALREADY_REGISTERED"
    assert "already registered" in in_msg.reply_message.lower()


def test_9_status_command_advisory(client: TestClient, db_session):
    """9. Test STATUS keyword triggers dynamic ML prediction & XAI advisory pipeline."""
    phone = "+919800000001"  # Seeded active farmer
    res = client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "STATUS"})
    assert res.status_code == 200

    in_msg = db_session.query(InboundMessage).filter(
        InboundMessage.from_phone == phone,
        InboundMessage.message_body == "STATUS"
    ).first()
    assert in_msg is not None
    assert in_msg.registration_step_after == "STATUS"
    assert "MEGHVANI ADVISORY" in in_msg.reply_message
    assert "False onset probability:" in in_msg.reply_message
    assert "Why:" in in_msg.reply_message


def test_10_invalid_message_handling(client: TestClient, db_session):
    """10. Test invalid input during state machine preserves step without crashing."""
    phone = _gen_phone()
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "MEGH"})

    # Send invalid language code '99'
    res = client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "99"})
    assert res.status_code == 200

    in_msg = db_session.query(InboundMessage).filter(
        InboundMessage.from_phone == phone,
        InboundMessage.message_body == "99"
    ).first()
    assert in_msg is not None
    assert in_msg.registration_step_after == "LANGUAGE"
    assert "Invalid choice" in in_msg.reply_message


def test_11_duplicate_message_sid_idempotency(client: TestClient, db_session):
    """11. Test duplicate MessageSid idempotency protection."""
    phone = _gen_phone()
    sid = f"SM_IDEM_{uuid.uuid4().hex}"

    # First delivery
    res1 = client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "MEGH", "MessageSid": sid})
    assert res1.status_code == 200

    count_before = db_session.query(InboundMessage).filter(InboundMessage.provider_message_id == sid).count()
    assert count_before == 1

    # Duplicate delivery with exact same MessageSid
    res2 = client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "MEGH", "MessageSid": sid})
    assert res2.status_code == 200

    # Ensure no second entry created
    count_after = db_session.query(InboundMessage).filter(InboundMessage.provider_message_id == sid).count()
    assert count_after == 1


def test_12_invalid_twilio_signature(client: TestClient, monkeypatch):
    """12. Test rejection of invalid Twilio webhook signature in live mode with HTTP 403."""
    monkeypatch.setenv("SMS_PROVIDER", "TWILIO")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "real_secret_token_123")
    monkeypatch.setenv("SMS_WEBHOOK_VALIDATION", "true")

    # Send request with invalid signature header
    res = client.post(
        "/api/communication/sms/incoming",
        data={"From": "+919876543210", "Body": "MEGH"},
        headers={"X-Twilio-Signature": "invalid_fake_signature"}
    )
    assert res.status_code == 403
    assert "Invalid Twilio" in res.json().get("detail", "")


def test_13_mock_sms_provider():
    """13. Test MockSMSProvider is returned by default and dispatches simulated result."""
    with patch.dict("os.environ", {"SMS_PROVIDER": "MOCK"}):
        provider = get_sms_provider()
        assert isinstance(provider, MockSMSProvider)
        result = provider.send("+919876543210", "Hello Test")
        assert result["status"] == "SIMULATED"
        assert result["channel"] == "SMS"
        assert "mock-sms-" in result["provider_message_id"]


def test_14_twilio_provider_mocked_http():
    """14. Test TwilioSMSProvider sends properly formatted payload to Twilio Messages API."""
    provider = TwilioSMSProvider(
        account_sid="AC_test_account_sid_12345",
        auth_token="auth_test_token_67890",
        from_phone_number="+15551234567"
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"sid": "SM_twilio_mock_message_id"}

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        res = provider.send("+919876543210", "Test Twilio Dispatch")
        assert res["status"] == "SENT"
        assert res["provider"] == "TWILIO"
        assert res["provider_message_id"] == "SM_twilio_mock_message_id"

        # Verify call arguments
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "AC_test_account_sid_12345" in args[0]
        assert kwargs["data"]["To"] == "+919876543210"
        assert kwargs["data"]["From"] == "+15551234567"
        assert kwargs["data"]["Body"] == "Test Twilio Dispatch"


def test_15_outbound_sms_failure_clean_handling():
    """15. Test clean error response when Twilio API returns error without crashing."""
    provider = TwilioSMSProvider(
        account_sid="AC_bad_sid",
        auth_token="token",
        from_phone_number="+15551234567"
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = '{"code": 21211, "message": "The \'To\' number is not valid"}'

    with patch("httpx.Client.post", return_value=mock_resp):
        res = provider.send("invalid-phone", "Hello")
        assert res["status"] == "FAILED"
        assert res["provider"] == "TWILIO"
        assert res["provider_message_id"] is None
        assert "21211" in res["error"]


def test_16_advisory_generation_xai_content(db_session):
    """16. Test advisory generation executes ML model and includes top drivers."""
    from app.services.registration_service import RegistrationService
    farmer = db_session.query(Farmer).filter(Farmer.phone_number == "+919800000001").first()
    assert farmer is not None

    advisory_text = RegistrationService.generate_status_advisory(db_session, farmer)
    assert "MEGHVANI ADVISORY" in advisory_text
    assert "False onset probability:" in advisory_text
    assert "Why:" in advisory_text
    assert "Advice:" in advisory_text


def test_17_alert_center_logging(client: TestClient):
    """17. Test that Inbound and Outbound entries appear in timeline and summary endpoints."""
    # Send a message to populate timeline
    phone = _gen_phone()
    client.post("/api/communication/sms/incoming", data={"From": phone, "Body": "MEGH"})

    # Fetch timeline
    res = client.get("/api/communication/timeline")
    assert res.status_code == 200
    timeline = res.json()
    assert isinstance(timeline, list)
    assert len(timeline) > 0

    first_item = timeline[0]
    assert "masked_phone" in first_item
    assert "direction" in first_item
    assert first_item["direction"] in ["INBOUND", "OUTBOUND"]

    # Fetch summary
    summary_res = client.get("/api/communication/summary")
    assert summary_res.status_code == 200
    s_data = summary_res.json()
    assert "sms_received" in s_data
    assert "sms_sent" in s_data
    assert "active_farmers" in s_data


def test_18_phone_masking():
    """18. Test consistent phone number masking for privacy (******3210)."""
    assert mask_phone_number("+919876543210") == "******3210"
    assert mask_phone_number("9876543210") == "******3210"
    assert mask_phone_number("+15551234567") == "******4567"
    assert mask_phone_number(None) == "Unknown"
    assert mask_phone_number("123") == "******"


def test_19_twilio_trial_mode_template_dispatch():
    """19. Test Twilio trial mode sends predefined template with trial limitation notice."""
    provider = TwilioSMSProvider(
        account_sid="AC_test_account_sid_12345",
        auth_token="auth_test_token_67890",
        from_phone_number="+15551234567",
        trial_mode=True,
        trial_template_name="sms_2fa"
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"sid": "SM_trial_sid_001"}

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        res = provider.send("+919876543210", "Meghvani Custom Advisory")
        assert res["status"] == "SENT"
        assert res["provider"] == "TWILIO"
        assert res["provider_message_id"] == "SM_trial_sid_001"
        assert res["trial_mode"] is True
        assert "Twilio Trial restriction: custom Meghvani SMS reply not permitted." in res["trial_notice"]
        assert res["actual_message"] == "Meghvani Custom Advisory"

        # Verify call arguments contain Body = "sms_2fa" instead of custom text or TemplateName
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        assert kwargs["data"]["Body"] == "sms_2fa"
        assert "TemplateName" not in kwargs["data"]


def test_20_twilio_auto_detect_error_57206_fallback():
    """20. Test auto-fallback to trial template when Twilio returns error 57206 on custom body."""
    provider = TwilioSMSProvider(
        account_sid="AC_test_account_sid_12345",
        auth_token="auth_test_token_67890",
        from_phone_number="+15551234567",
        trial_mode=False
    )

    resp_error_57206 = MagicMock()
    resp_error_57206.status_code = 400
    resp_error_57206.text = '{"code": 57206, "message": "Invalid template name. Trial accounts can only use predefined SMS templates."}'

    resp_trial_success = MagicMock()
    resp_trial_success.status_code = 201
    resp_trial_success.json.return_value = {"sid": "SM_fallback_trial_sid"}

    with patch("httpx.Client.post", side_effect=[resp_error_57206, resp_trial_success]) as mock_post:
        res = provider.send("+919876543210", "Meghvani Hindi Language Prompt")
        assert res["status"] == "SENT"
        assert res["provider_message_id"] == "SM_fallback_trial_sid"
        assert res["trial_mode"] is True
        assert "Twilio Trial restriction: custom Meghvani SMS reply not permitted." in res["trial_notice"]
        assert res["actual_message"] == "Meghvani Hindi Language Prompt"
        assert mock_post.call_count == 2

        # Check call 1 was custom body, call 2 fell back to Body = "sms_2fa"
        call_1_kwargs = mock_post.call_args_list[0][1]
        assert call_1_kwargs["data"]["Body"] == "Meghvani Hindi Language Prompt"

        call_2_kwargs = mock_post.call_args_list[1][1]
        assert call_2_kwargs["data"]["Body"] == "sms_2fa"
        assert "TemplateName" not in call_2_kwargs["data"]


def test_21_twilio_trial_failure_no_fake_success():
    """21. Test that if trial template is also rejected by Twilio, failure is reported without faking delivery."""
    provider = TwilioSMSProvider(
        account_sid="AC_test_account_sid_12345",
        auth_token="auth_test_token_67890",
        from_phone_number="+15551234567",
        trial_mode=True
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = '{"code": 21608, "message": "The number is unverified"}'

    with patch("httpx.Client.post", return_value=mock_resp):
        res = provider.send("+919876543210", "Meghvani Advisory")
        assert res["status"] == "FAILED"
        assert res["provider_message_id"] is None
        assert "Twilio Trial restriction: custom Meghvani SMS reply not permitted." in res["error"]
        assert res["actual_message"] == "Meghvani Advisory"


def test_22_gateway_status_trial_mode(client: TestClient, monkeypatch):
    """22. Test /api/communication/status reflects LIVE SMS (TRIAL) and restriction notice."""
    monkeypatch.setenv("SMS_PROVIDER", "TWILIO")
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "AC_test_account")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "auth_test_token")
    monkeypatch.setenv("TWILIO_PHONE_NUMBER", "+17372508034")
    monkeypatch.setenv("TWILIO_TRIAL_MODE", "true")

    res = client.get("/api/communication/status")
    assert res.status_code == 200
    data = res.json()
    assert data["sms_provider"] == "TWILIO"
    assert data["mode"] == "LIVE SMS (TRIAL)"
    assert data["is_live"] is True
    assert data["is_trial_mode"] is True
    assert "Twilio Trial restriction: custom Meghvani SMS reply not permitted." in data["trial_notice"]
