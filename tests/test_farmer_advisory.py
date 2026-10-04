"""
Meghvani Phase 5C: Farmer Advisory & Language Layer Tests.

Comprehensive test suite verifying:
1. English SOW_NOW with validated rule.
2. Hindi SOW_NOW with validated rule.
3. Marathi SOW_NOW with validated rule.
4. English WAIT with validated rule.
5. Hindi WAIT with validated rule.
6. Marathi WAIT with validated rule.
7. SOW_PART_NOW returns NO_VALIDATED_RULE.
8. REVIEW_REQUIRED rule cannot produce advice.
9. UNVALIDATED rule cannot produce advice.
10. Missing forecast returns FORECAST_UNAVAILABLE.
11. Unsupported language safely falls back to English.
12. SMS formatting works.
13. WhatsApp formatting works.
14. Voice formatting works.
15. No unsupported agronomic text is introduced (no fertilizers, pesticides, seed rates, or irrigation volumes).
16. Source attribution remains correct.
17. Probability threshold is not attributed to institution.
18. Prototype warning remains present across all messages.
19. API GET /api/advisory/{block_id}/message returns provenance and localized channel message.
20. Existing tests remain passing.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.advisory.models import (
    AdvisoryRule,
    AdvisoryResult,
    ValidationStatus,
    Priority,
    AdvisoryStatus,
    RuleSource
)
from app.advisory.rule_registry import default_rule_registry, RuleRegistry
from app.advisory.rule_engine import AdvisoryRuleEngine
from app.advisory.message_generator import (
    AdvisoryMessageGenerator,
    FarmerAdvisoryMessage,
    MessageLanguage,
    MessageChannel,
    MessageType,
    format_for_sms,
    format_for_whatsapp,
    format_for_voice
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def engine():
    return AdvisoryRuleEngine(registry=default_rule_registry)


# 1. English SOW_NOW with validated rule
def test_english_sow_now_with_validated_rule(engine):
    res = engine.evaluate(crop_id="soybean", decision="SOW_NOW", geography="Maharashtra")
    assert res.advisory_status == AdvisoryStatus.RULE_MATCHED
    assert res.validation_status == ValidationStatus.VALIDATED

    msg = AdvisoryMessageGenerator.generate_message(
        advisory_result=res,
        crop_id="soybean",
        decision="SOW_NOW",
        language="en",
        channel="sms"
    )
    assert msg.advisory_status == "VALIDATED_RULE"
    assert msg.language == "en"
    assert msg.crop_name == "Soybean"
    assert "Meghvani update for Soybean:" in msg.message
    assert "SOW NOW" in msg.message
    assert "ICAR-Central Research Institute for Dryland Agriculture (CRIDA)" in msg.message
    assert msg.is_operational is False
    assert "prototype" in msg.prototype_warning.lower()


# 2. Hindi SOW_NOW with validated rule
def test_hindi_sow_now_with_validated_rule(engine):
    res = engine.evaluate(crop_id="soybean", decision="SOW_NOW", geography="Maharashtra")
    msg = AdvisoryMessageGenerator.generate_message(
        advisory_result=res,
        crop_id="soybean",
        decision="SOW_NOW",
        language="hi",
        channel="sms"
    )
    assert msg.advisory_status == "VALIDATED_RULE"
    assert msg.language == "hi"
    assert msg.crop_name == "सोयाबीन"
    assert "मेघवाणी अपडेट — सोयाबीन:" in msg.message
    assert "गलत मानसून शुरुआत" in msg.message
    assert "पर्याप्त वर्षा (75-100 मिमी)" in msg.message
    assert msg.is_operational is False


# 3. Marathi SOW_NOW with validated rule
def test_marathi_sow_now_with_validated_rule(engine):
    res = engine.evaluate(crop_id="soybean", decision="SOW_NOW", geography="Maharashtra")
    msg = AdvisoryMessageGenerator.generate_message(
        advisory_result=res,
        crop_id="soybean",
        decision="SOW_NOW",
        language="mr",
        channel="sms"
    )
    assert msg.advisory_status == "VALIDATED_RULE"
    assert msg.language == "mr"
    assert msg.crop_name == "सोयाबीन"
    assert "मेघवाणी अपडेट — सोयाबीन:" in msg.message
    assert "पावसाच्या सुरुवातीबाबतचा धोका" in msg.message
    assert "वाफसा स्थितीची खात्री करा" in msg.message
    assert msg.is_operational is False


# 4. English WAIT with validated rule
def test_english_wait_with_validated_rule(engine):
    res = engine.evaluate(crop_id="cotton", decision="WAIT", geography="Maharashtra")
    assert res.advisory_status == AdvisoryStatus.RULE_MATCHED
    assert res.validation_status == ValidationStatus.VALIDATED

    msg = AdvisoryMessageGenerator.generate_message(
        advisory_result=res,
        crop_id="cotton",
        decision="WAIT",
        language="en",
        channel="sms"
    )
    assert msg.advisory_status == "VALIDATED_RULE"
    assert msg.language == "en"
    assert msg.crop_name == "Cotton"
    assert "Meghvani update for Cotton:" in msg.message
    assert "delay sowing until adequate rainfall" in msg.message
    assert "ICAR-Central Institute for Cotton Research (CICR), Nagpur" in msg.message


# 5. Hindi WAIT with validated rule
def test_hindi_wait_with_validated_rule(engine):
    res = engine.evaluate(crop_id="cotton", decision="WAIT", geography="Maharashtra")
    msg = AdvisoryMessageGenerator.generate_message(
        advisory_result=res,
        crop_id="cotton",
        decision="WAIT",
        language="hi",
        channel="sms"
    )
    assert msg.advisory_status == "VALIDATED_RULE"
    assert msg.language == "hi"
    assert msg.crop_name == "कपास"
    assert "मेघवाणी अपडेट — कपास:" in msg.message
    assert "बुवाई रोकें" in msg.message
    assert "प्रतीक्षा करें" in msg.message


# 6. Marathi WAIT with validated rule
def test_marathi_wait_with_validated_rule(engine):
    res = engine.evaluate(crop_id="pigeonpea", decision="WAIT", geography="Maharashtra")
    msg = AdvisoryMessageGenerator.generate_message(
        advisory_result=res,
        crop_id="pigeonpea",
        decision="WAIT",
        language="mr",
        channel="sms"
    )
    assert msg.advisory_status == "VALIDATED_RULE"
    assert msg.language == "mr"
    assert msg.crop_name == "तूर"
    assert "मेघवाणी अपडेट — तूर:" in msg.message
    assert "पेरणी घाईने करू नका" in msg.message
    assert "प्रतीक्षा करा" in msg.message


# 7. SOW_PART_NOW returns NO_VALIDATED_RULE
def test_sow_part_now_returns_no_validated_rule(engine):
    res = engine.evaluate(crop_id="soybean", decision="SOW_PART_NOW", geography="Maharashtra")
    assert res.advisory_status == AdvisoryStatus.NO_VALIDATED_RULE

    msg = AdvisoryMessageGenerator.generate_message(
        advisory_result=res,
        crop_id="soybean",
        decision="SOW_PART_NOW",
        language="en"
    )
    assert msg.advisory_status == "NO_VALIDATED_RULE"
    assert "partial-sowing posture" in msg.message
    assert "not currently available" in msg.message
    assert msg.source_institution is None


# 8. REVIEW_REQUIRED rule cannot produce advice
def test_review_required_rule_cannot_produce_advice(engine):
    # Soybean SOW_PART_NOW has a candidate rule marked REVIEW_REQUIRED
    res = engine.evaluate(crop_id="soybean", decision="SOW_PART_NOW", geography="Maharashtra")
    assert res.advisory_status == AdvisoryStatus.NO_VALIDATED_RULE
    assert res.advisory_text is None

    msg = AdvisoryMessageGenerator.generate_message(
        advisory_result=res,
        crop_id="soybean",
        decision="SOW_PART_NOW",
        language="en"
    )
    assert msg.advisory_status == "NO_VALIDATED_RULE"
    assert "approved crop-specific agronomic rule is not currently available" in msg.message


# 9. UNVALIDATED rule cannot produce advice
def test_unvalidated_rule_cannot_produce_advice():
    custom_reg = RuleRegistry()
    demo_rule = AdvisoryRule(
        rule_id="RULE_TEST_UNVALIDATED",
        crop_id="soybean",
        geography="Maharashtra",
        decision="SOW_NOW",
        advisory_text="Unvalidated speculative advice",
        validation_status=ValidationStatus.UNVALIDATED
    )
    custom_reg.register_rule(demo_rule)
    engine = AdvisoryRuleEngine(registry=custom_reg)
    res = engine.evaluate(crop_id="soybean", decision="SOW_NOW")
    assert res.advisory_status == AdvisoryStatus.NO_VALIDATED_RULE

    msg = AdvisoryMessageGenerator.generate_message(
        advisory_result=res,
        crop_id="soybean",
        decision="SOW_NOW",
        language="en"
    )
    assert msg.advisory_status == "NO_VALIDATED_RULE"
    assert "approved crop-specific advisory is not currently available" in msg.message


# 10. Missing forecast returns FORECAST_UNAVAILABLE
def test_missing_forecast_returns_forecast_unavailable():
    msg = AdvisoryMessageGenerator.generate_message(
        forecast_available=False,
        crop_id="soybean",
        language="en"
    )
    assert msg.advisory_status == "FORECAST_UNAVAILABLE"
    assert "Meghvani forecast is currently unavailable" in msg.message
    assert msg.source_institution is None


# 11. Unsupported language safely falls back to English
def test_unsupported_language_fallback():
    assert AdvisoryMessageGenerator.normalize_language("kannada") == "en"
    assert AdvisoryMessageGenerator.normalize_language("es") == "en"
    assert AdvisoryMessageGenerator.normalize_language(None) == "en"
    assert AdvisoryMessageGenerator.normalize_language("HI") == "hi"

    msg = AdvisoryMessageGenerator.generate_message(
        forecast_available=False,
        crop_id="soybean",
        language="kannada"
    )
    assert msg.language == "en"
    assert "currently unavailable" in msg.message


# 12. SMS formatting works
def test_sms_formatting():
    formatted = format_for_sms("Sowing permitted after rain.", "Prototype advisory only.")
    assert "Sowing permitted after rain." in formatted
    assert "[Prototype advisory only.]" in formatted
    assert "*" not in formatted


# 13. WhatsApp formatting works
def test_whatsapp_formatting():
    formatted = format_for_whatsapp("Sowing permitted after rain.", "Prototype advisory only.", "Soybean", True)
    assert "🌾 *Meghvani Advisory | Soybean*" in formatted
    assert "⚠️ _Prototype advisory only._" in formatted


# 14. Voice formatting works
def test_voice_formatting():
    raw_text = "Ensure 75-100 mm rainfall from ICAR-CRIDA before SOW NOW."
    spoken = format_for_voice(raw_text, "Prototype warning.", "Soybean", "en")
    assert "75 to 100 millimeters" in spoken
    assert "ICAR CRIDA" in spoken
    assert "sow now" in spoken
    assert "-" not in spoken
    assert "This is an automated Meghvani weather and crop advisory for Soybean." in spoken


# 15. No unsupported agronomic text is introduced
def test_no_unsupported_agronomic_text_introduced(engine):
    # Verify that message generator does NOT add fertilizer, pesticide, or unbacked rates
    banned_keywords = [
        "fertilizer", "urea", "dap", "npk", "pesticide", "insecticide",
        "kg/ha", "kg per hectare", "seed rate", "litres/ha", "irrigate 50mm"
    ]
    for crop in ["soybean", "cotton", "pigeonpea"]:
        for dec in ["SOW_NOW", "WAIT"]:
            res = engine.evaluate(crop_id=crop, decision=dec, geography="Maharashtra")
            for lang in ["en", "hi", "mr"]:
                for chan in ["sms", "whatsapp", "voice"]:
                    msg = AdvisoryMessageGenerator.generate_message(
                        advisory_result=res,
                        crop_id=crop,
                        decision=dec,
                        language=lang,
                        channel=chan
                    )
                    lower_msg = msg.message.lower()
                    for kw in banned_keywords:
                        assert kw not in lower_msg, f"Banned keyword '{kw}' found in generated message for {crop}/{dec}/{lang}/{chan}"


# 16. Source attribution remains correct
def test_source_attribution_correctness(engine):
    res_soy = engine.evaluate("soybean", "SOW_NOW")
    msg_soy = AdvisoryMessageGenerator.generate_message(advisory_result=res_soy, crop_id="soybean", decision="SOW_NOW", language="en")
    assert "ICAR-Central Research Institute for Dryland Agriculture (CRIDA)" in msg_soy.message

    res_cot = engine.evaluate("cotton", "SOW_NOW")
    msg_cot = AdvisoryMessageGenerator.generate_message(advisory_result=res_cot, crop_id="cotton", decision="SOW_NOW", language="en")
    assert "ICAR-Central Institute for Cotton Research (CICR), Nagpur" in msg_cot.message

    res_pig = engine.evaluate("pigeonpea", "SOW_NOW")
    msg_pig = AdvisoryMessageGenerator.generate_message(advisory_result=res_pig, crop_id="pigeonpea", decision="SOW_NOW", language="en")
    assert "Dr. Panjabrao Deshmukh Krishi Vidyapeeth (Dr. PDKV), Akola" in msg_pig.message


# 17. Probability threshold is not attributed to institution
def test_probability_threshold_not_attributed_to_institution(engine):
    for crop in ["soybean", "cotton", "pigeonpea"]:
        for dec in ["SOW_NOW", "WAIT"]:
            res = engine.evaluate(crop, dec)
            msg = AdvisoryMessageGenerator.generate_message(advisory_result=res, crop_id=crop, decision=dec, language="en")
            # Farmer message should not claim ICAR established probability thresholds
            assert "ICAR says probability" not in msg.message
            assert "0.30" not in msg.message
            assert "0.60" not in msg.message
            assert "percent probability" not in msg.message.lower()


# 18. Prototype warning remains present
def test_prototype_warning_present(engine):
    res = engine.evaluate("soybean", "SOW_NOW")
    for lang in ["en", "hi", "mr"]:
        for chan in ["sms", "whatsapp", "voice"]:
            msg = AdvisoryMessageGenerator.generate_message(advisory_result=res, crop_id="soybean", decision="SOW_NOW", language=lang, channel=chan)
            assert msg.prototype_warning is not None
            assert len(msg.prototype_warning) > 10
            assert msg.is_operational is False


# 19. API GET /api/advisory/{block_id}/message returns provenance and localized channel message
def test_api_get_block_advisory_message(client):
    # Test valid block BLK001 in English
    res_en = client.get("/api/advisory/BLK001/message?crop_id=soybean&language=en&channel=sms")
    assert res_en.status_code == 200
    data_en = res_en.json()
    assert data_en["block_id"] == "BLK001"
    assert data_en["crop_id"] == "soybean"
    assert data_en["language"] == "en"
    assert data_en["channel"] == "sms"
    assert data_en["is_operational"] is False
    assert "message" in data_en
    assert "source_institution" in data_en

    # Test valid block in Marathi via WhatsApp
    res_mr = client.get("/api/advisory/BLK001/message?crop_id=cotton&language=mr&channel=whatsapp")
    assert res_mr.status_code == 200
    data_mr = res_mr.json()
    assert data_mr["language"] == "mr"
    assert data_mr["channel"] == "whatsapp"
    assert "🌾 *Meghvani Advisory" in data_mr["message"]

    # Test valid block in Hindi via Voice
    res_hi = client.get("/api/advisory/BLK001/message?crop_id=pigeonpea&language=hi&channel=voice")
    assert res_hi.status_code == 200
    data_hi = res_hi.json()
    assert data_hi["language"] == "hi"
    assert data_hi["channel"] == "voice"
    assert "मेघवाणी कृषि सलाह संदेश" in data_hi["message"]

    # Test invalid block ID
    res_404 = client.get("/api/advisory/INVALID_BLOCK_999/message")
    assert res_404.status_code == 404
