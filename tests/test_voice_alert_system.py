"""
Tests for Meghvani AI Voice Alert System (Sarvam Bulbul v3 integration & demo fallback).
Verifies the complete 16-point specification:
1. Heavy rain actionable advisory text
2. False onset actionable advisory text
3. Marathi advisory ("आज पेरणी करू नका")
4. Hindi advisory ("आज बुवाई न करें")
5. Kannada advisory ("ಇಂದು ಬಿತ್ತನೆ ಮಾಡಬೇಡಿ")
6. English advisory ("Do not sow seeds today")
7. Sarvam receives final advisory text (not raw coefficients or technical XAI values)
8. Sarvam response contains audio in audios[0]
9. Base64 audio is decoded and validated correctly
10. Audio is playable by frontend (data:audio/wav;base64,... URI)
11. Missing API key honest fallback (DEMO VOICE — SARVAM NOT CONNECTED)
12. Sarvam API failure handling
13. Replay does not regenerate audio (cached without calling Sarvam again)
14. Voice alert lifecycle (ANSWERED, COMPLETED/PLAYED, DECLINED, REPLAY)
15. Full API endpoint integration (/api/communication/voice-alert)
16. Alert Center timeline integration with VOICE channel
"""
import json
import base64
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from app.services.sarvam_tts_service import SarvamTTSService
from app.services.advisory_service import AdvisoryService
from app.models.farmer import Farmer
from app.models.alert_log import AlertLog


def test_1_language_mapping():
    """Verify BCP-47 language mapping for Sarvam AI Bulbul v3."""
    assert SarvamTTSService.normalize_language("mr") == ("mr-IN", "Marathi")
    assert SarvamTTSService.normalize_language("Marathi") == ("mr-IN", "Marathi")
    assert SarvamTTSService.normalize_language("2") == ("mr-IN", "Marathi")

    assert SarvamTTSService.normalize_language("hi") == ("hi-IN", "Hindi")
    assert SarvamTTSService.normalize_language("Hindi") == ("hi-IN", "Hindi")
    assert SarvamTTSService.normalize_language("1") == ("hi-IN", "Hindi")

    assert SarvamTTSService.normalize_language("kn") == ("kn-IN", "Kannada")
    assert SarvamTTSService.normalize_language("Kannada") == ("kn-IN", "Kannada")
    assert SarvamTTSService.normalize_language("3") == ("kn-IN", "Kannada")

    assert SarvamTTSService.normalize_language("en") == ("en-IN", "English")
    assert SarvamTTSService.normalize_language("English") == ("en-IN", "English")
    assert SarvamTTSService.normalize_language("4") == ("en-IN", "English")

    # Default fallback
    assert SarvamTTSService.normalize_language(None) == ("mr-IN", "Marathi")
    assert SarvamTTSService.normalize_language("unknown") == ("mr-IN", "Marathi")


def test_2_heavy_rain_actionable_advisory_text():
    """Verify Heavy Rain advisory answers What is happening + What to do."""
    text_mr = AdvisoryService.get_actionable_voice_advisory("HEAVY_RAIN", "Soybean", "Kalmeshwar", "mr-IN")
    assert "मुसळधार" in text_mr
    assert "आज पेरणी करू नका" in text_mr
    assert "पावसाची परिस्थिती स्थिर होईपर्यंत थांबा" in text_mr

    text_en = AdvisoryService.get_actionable_voice_advisory("HEAVY_RAIN", "Soybean", "Kalmeshwar", "en-IN")
    assert "Heavy rainfall is expected" in text_en
    assert "Do not sow seeds today" in text_en
    assert "Wait until rainfall conditions stabilize" in text_en


def test_3_false_onset_actionable_advisory_text():
    """Verify False Onset advisory answers What is happening + What to do."""
    text_mr = AdvisoryService.get_actionable_voice_advisory("FALSE_ONSET", "Soybean", "Kalmeshwar", "mr-IN")
    assert "मान्सून अद्याप स्थिर झालेला नाही" in text_mr
    assert "आज पेरणी करू नका" in text_mr
    assert "नियमित पाऊस होईपर्यंत थांबा" in text_mr

    text_en = AdvisoryService.get_actionable_voice_advisory("FALSE_ONSET", "Soybean", "Kalmeshwar", "en-IN")
    assert "monsoon may not be stable yet" in text_en
    assert "Do not sow seeds now" in text_en
    assert "Wait for more consistent rainfall" in text_en


def test_4_marathi_advisory_contains_action():
    """Verify Marathi farmer advisory specifically speaks 'आज पेरणी करू नका'."""
    text = AdvisoryService.get_actionable_voice_advisory("HEAVY_RAIN", "Soybean", "कळमेश्वर", "mr-IN")
    assert "आज पेरणी करू नका" in text
    assert "मेघवाणी" in text


def test_5_hindi_advisory_contains_action():
    """Verify Hindi farmer advisory speaks actionable instruction 'आज बुवाई न करें'."""
    text = AdvisoryService.get_actionable_voice_advisory("HEAVY_RAIN", "Soybean", "कलमेश्वर", "hi-IN")
    assert "आज बुवाई न करें" in text
    assert "भारी बारिश" in text


def test_6_kannada_advisory_contains_action():
    """Verify Kannada farmer advisory speaks actionable instruction 'ಇಂದು ಬಿತ್ತನೆ ಮಾಡಬೇಡಿ'."""
    text = AdvisoryService.get_actionable_voice_advisory("HEAVY_RAIN", "Soybean", "ಕಲ್ಮೇಶ್ವರ", "kn-IN")
    assert "ಇಂದು ಬಿತ್ತನೆ ಮಾಡಬೇಡಿ" in text
    assert "ಭಾರೀ ಮಳೆ" in text


def test_7_english_advisory_contains_action():
    """Verify English farmer advisory speaks 'Do not sow seeds today'."""
    text = AdvisoryService.get_actionable_voice_advisory("HEAVY_RAIN", "Soybean", "Kalmeshwar", "en-IN")
    assert "Do not sow seeds today" in text
    assert "Wait until rainfall conditions stabilize" in text


def test_8_sarvam_receives_final_advisory_text():
    """Verify Sarvam API request receives the actual actionable farmer text, NOT technical XAI values."""
    mock_response = MagicMock()
    fake_audio_base64 = base64.b64encode(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00data\x00\x00\x00\x00").decode("utf-8")
    mock_response.read.return_value = json.dumps({"audios": [fake_audio_base64]}).encode("utf-8")
    mock_response.__enter__.return_value = mock_response

    captured_payload = {}

    def fake_urlopen(req, timeout=12):
        nonlocal captured_payload
        captured_payload = json.loads(req.data.decode("utf-8"))
        return mock_response

    with patch.object(SarvamTTSService, "get_api_key", return_value="mock-key"), \
         patch("urllib.request.urlopen", side_effect=fake_urlopen):
        SarvamTTSService._audio_cache.clear()

        advisory = "तुमच्या भागात मुसळधार पावसाची शक्यता आहे. आज पेरणी करू नका."
        SarvamTTSService.synthesize_speech(advisory, language="mr-IN")

        assert captured_payload["inputs"] == [advisory]
        assert captured_payload["target_language_code"] == "mr-IN"
        assert captured_payload["model"] == "bulbul:v3"
        assert captured_payload["speaker"] == "shubh"
        assert captured_payload["speech_sample_rate"] == 24000
        assert captured_payload["output_audio_codec"] == "wav"
        assert captured_payload["pace"] in [0.9, 1.0]
        # Verify no v2-only parameters are sent
        assert "pitch" not in captured_payload
        assert "loudness" not in captured_payload
        # Verify no model coefficients or internal terms are sent
        assert "prob_onset" not in str(captured_payload)
        assert "coefficient" not in str(captured_payload)


def test_9_sarvam_response_contains_audio():
    """Verify Sarvam response audio in audios[0] is extracted and returned."""
    fake_wav_bytes = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00data\x00\x00\x00\x00extra_padding_bytes_for_validity"
    fake_audio_base64 = base64.b64encode(fake_wav_bytes).decode("utf-8")

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"audios": [fake_audio_base64]}).encode("utf-8")
    mock_response.__enter__.return_value = mock_response

    with patch.object(SarvamTTSService, "get_api_key", return_value="mock-key"), \
         patch("urllib.request.urlopen", return_value=mock_response):
        SarvamTTSService._audio_cache.clear()

        res = SarvamTTSService.synthesize_speech("आज पेरणी करू नका.", "mr-IN")
        assert res["status"] == "GENERATED"
        assert res["provider"] == "SARVAM_AI"
        assert "● AI VOICE — SARVAM BULBUL v3" in res["provider_label"]
        assert res["audio_content"] == f"data:audio/wav;base64,{fake_audio_base64}"


def test_10_base64_audio_decoding_verification():
    """Verify that corrupt or non-decodable base64 audio triggers fallback and is NOT marked GENERATED."""
    corrupt_response = MagicMock()
    corrupt_response.read.return_value = json.dumps({"audios": ["not-valid-base-64!!!"]}).encode("utf-8")
    corrupt_response.__enter__.return_value = corrupt_response

    with patch.object(SarvamTTSService, "get_api_key", return_value="mock-key"), \
         patch("urllib.request.urlopen", return_value=corrupt_response):
        SarvamTTSService._audio_cache.clear()

        res = SarvamTTSService.synthesize_speech("आज पेरणी करू नका.", "mr-IN")
        # Must mark FAILED and NOT GENERATED because valid audio was not returned
        assert res["status"] == "FAILED"
        assert res["provider"] == "DEMO_VOICE"
        assert res["audio_content"] is None


def test_11_audio_playable_format_for_frontend():
    """Verify audio URI returned is formatted as HTML5 Audio-playable data URI."""
    fake_wav_bytes = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00data\x00\x00\x00\x00extra_padding_bytes_for_validity"
    fake_audio_base64 = base64.b64encode(fake_wav_bytes).decode("utf-8")

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"audios": [fake_audio_base64]}).encode("utf-8")
    mock_response.__enter__.return_value = mock_response

    with patch.object(SarvamTTSService, "get_api_key", return_value="mock-key"), \
         patch("urllib.request.urlopen", return_value=mock_response):
        SarvamTTSService._audio_cache.clear()

        res = SarvamTTSService.synthesize_speech("Test advisory", "en-IN")
        assert res["audio_content"].startswith("data:audio/wav;base64,")
        raw_b64 = res["audio_content"].replace("data:audio/wav;base64,", "")
        decoded = base64.b64decode(raw_b64)
        assert len(decoded) > 0


def test_12_missing_api_key_honest_fallback():
    """Verify that when SARVAM_API_KEY is not configured, status is FALLBACK and honest demo label is shown."""
    with patch.object(SarvamTTSService, "get_api_key", return_value=None):
        res = SarvamTTSService.synthesize_speech("आज पेरणी करू नका.", "mr-IN")
        assert res["status"] == "FALLBACK"
        assert res["provider"] == "DEMO_VOICE"
        assert res["provider_label"] == "DEMO VOICE — SARVAM NOT CONNECTED"
        assert res["audio_content"] is None


def test_13_sarvam_api_failure_fallback():
    """Verify that HTTP error from Sarvam safely falls back without crashing."""
    with patch.object(SarvamTTSService, "get_api_key", return_value="mock-key"), \
         patch("urllib.request.urlopen", side_effect=Exception("HTTP 500 Internal Server Error")):
        SarvamTTSService._audio_cache.clear()
        res = SarvamTTSService.synthesize_speech("आज पेरणी करू नका.", "mr-IN")
        assert res["status"] == "FAILED"
        assert res["provider"] == "DEMO_VOICE"
        assert res["provider_label"] == "DEMO VOICE — SARVAM NOT CONNECTED"
        assert res["audio_content"] is None


def test_14_replay_does_not_regenerate_audio():
    """Verify that replay uses memory cache and does not make a second external call."""
    fake_wav_bytes = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00data\x00\x00\x00\x00extra_padding_bytes_for_validity"
    fake_audio_base64 = base64.b64encode(fake_wav_bytes).decode("utf-8")

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"audios": [fake_audio_base64]}).encode("utf-8")
    mock_response.__enter__.return_value = mock_response

    text = "आज पेरणी करू नका."
    lang = "mr-IN"

    with patch.object(SarvamTTSService, "get_api_key", return_value="mock-key"), \
         patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        SarvamTTSService._audio_cache.clear()

        # First generation
        res1 = SarvamTTSService.synthesize_speech(text, lang)
        assert mock_urlopen.call_count == 1
        assert res1["audio_cached"] is False

        # Replay: must return the exact same audio from cache without calling urlopen
        res2 = SarvamTTSService.synthesize_speech(text, lang)
        assert mock_urlopen.call_count == 1  # Not incremented
        assert res2["audio_cached"] is True
        assert res2["audio_content"] == res1["audio_content"]


def test_15_voice_alert_endpoint_integration(client: TestClient, db_session):
    """Verify POST /api/communication/voice-alert triggers actionable voice advisory and logs AlertLog."""
    farmer = db_session.query(Farmer).filter(Farmer.active == True).first()
    if not farmer:
        farmer = Farmer(
            phone_number="+919876540001",
            preferred_language="mr",
            pin_code="441501",
            block_id=1,
            consent=True,
            active=True
        )
        db_session.add(farmer)
        db_session.commit()
        db_session.refresh(farmer)

    payload = {
        "farmer_id": farmer.id,
        "language": "mr",
        "force_high_risk": True,
        "alert_type": "HEAVY_RAIN"
    }

    res = client.post("/api/communication/voice-alert", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["farmer_id"] == farmer.id
    assert data["risk_level"] == "HIGH"
    assert data["alert_type"] == "HEAVY_RAIN"
    assert data["language"] == "mr-IN"
    assert "आज पेरणी करू नका" in data["advisory_text"]
    assert data["call_status"] == "READY"
    assert data["alert_id"] is not None
    assert "audio_content_length" in data
    assert "audio_format" in data
    assert "audio_bytes" in data

    # Check database AlertLog
    log = db_session.query(AlertLog).filter(AlertLog.id == data["alert_id"]).first()
    assert log is not None
    assert log.channel == "VOICE"
    assert log.status == "READY"
    assert "आज पेरणी करू नका" in log.message


def test_16_voice_event_lifecycle(client: TestClient, db_session):
    """Verify voice lifecycle events (ANSWERED, PLAYED/COMPLETED, DECLINED)."""
    farmer = db_session.query(Farmer).first()

    # 1. Answer event
    res1 = client.post("/api/communication/voice-event", json={
        "farmer_id": farmer.id,
        "event": "ANSWERED",
        "duration_seconds": 0
    })
    assert res1.status_code == 200
    assert res1.json()["logged_status"] == "ANSWERED"

    # 2. Played / Completed event
    res2 = client.post("/api/communication/voice-event", json={
        "farmer_id": farmer.id,
        "event": "COMPLETED",
        "duration_seconds": 8
    })
    assert res2.status_code == 200
    assert res2.json()["logged_status"] == "PLAYED"

    # 3. Declined event
    res3 = client.post("/api/communication/voice-event", json={
        "farmer_id": farmer.id,
        "event": "DECLINED"
    })
    assert res3.status_code == 200
    assert res3.json()["logged_status"] == "DECLINED"


def test_17_alert_center_timeline_includes_voice(client: TestClient, db_session):
    """Verify that communication timeline endpoint returns voice alert items."""
    farmer = db_session.query(Farmer).first()
    client.post("/api/communication/voice-alert", json={"farmer_id": farmer.id, "language": "mr"})

    res = client.get("/api/communication/timeline?limit=20")
    assert res.status_code == 200
    timeline = res.json()

    voice_items = [t for t in timeline if t.get("channel") == "VOICE" or t.get("event_type") == "AI_VOICE_ALERT"]
    assert len(voice_items) > 0
    v_item = voice_items[0]
    assert v_item["channel"] == "VOICE"
    assert v_item["disclaimer"] == "AI VOICE ALERT — DEMO"
    assert "provider" in v_item
    assert "xai_context" in v_item
