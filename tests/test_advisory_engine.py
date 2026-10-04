"""
Meghvani Phase 5A: Advisory Rule Framework Tests.

Tests:
1. Rule model creation
2. Rule validation status
3. Rule registry registration
4. Rule lookup by crop
5. Rule lookup by decision
6. Rule lookup by crop + decision
7. No matching rule returns NO_VALIDATED_RULE
8. Unvalidated rule is not treated as validated
9. Validated rule returns RULE_MATCHED
10. Rule source metadata preserved
11. Language field preserved
12. Advisory result always contains is_operational=false
13. No rule produces no agronomic recommendation
14. API endpoint works
15. Existing forecast endpoint works
16. Existing decision endpoint works
17. No communication is triggered
18. No ML code is duplicated
19. No unsupported advisory text generated
20. Scientific integrity: no agronomic instruction without validation
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
from app.advisory.rule_registry import RuleRegistry, default_rule_registry
from app.advisory.rule_engine import AdvisoryRuleEngine
from app.advisory.validation import validate_advisory_rule, validate_rule_source


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def empty_registry():
    return RuleRegistry()


@pytest.fixture
def sample_validated_rule():
    return AdvisoryRule(
        rule_id="RULE_TEST_VALIDATED_001",
        crop_id="soybean",
        decision="SOW_NOW",
        action_type="FULL_SOWING",
        advisory_text="Validated test advisory: Sowing may proceed according to local contingency recommendations.",
        reason="Low false onset risk corroborated by soil moisture.",
        source_name="ICAR-CRIDA",
        source_institution="ICAR-CRIDA",
        source_title="Contingency Plan for Maharashtra - Vidarbha Zone 2023",
        source_document_identifier="CRIDA-CONTINGENCY-2023",
        source_reference="Contingency Plan for Maharashtra - Vidarbha Zone 2023",
        source_version="v2.1",
        source_date="2023-05",
        validation_status=ValidationStatus.VALIDATED,
        language="en",
        priority=Priority.NORMAL
    )


@pytest.fixture
def sample_unvalidated_rule():
    return AdvisoryRule(
        rule_id="RULE_TEST_UNVALIDATED_002",
        crop_id="soybean",
        decision="SOW_NOW",
        action_type="FULL_SOWING",
        advisory_text="Unvalidated demo text: Proceed with sowing.",
        reason="Demonstration rule.",
        source_name="ICAR-CRIDA",
        source_reference="Draft internal note",
        source_version="demo",
        source_date="2023-01",
        validation_status=ValidationStatus.UNVALIDATED,
        language="en",
        priority=Priority.NORMAL
    )


# 1. Rule model creation
def test_rule_model_creation():
    rule = AdvisoryRule(
        rule_id="RULE_CREATE_001",
        crop_id="cotton",
        decision="WAIT",
        action_type="DELAY_SOWING",
        advisory_text="Hold sowing until sustained moisture.",
        reason="High false onset probability.",
        source_name="ICAR-CICR Nagpur",
        source_reference="Cotton Advisory Bulletin 2024",
        source_version="1.0",
        source_date="2024-05",
        validation_status=ValidationStatus.UNVALIDATED,
        language="en",
        priority=Priority.HIGH
    )
    assert rule.rule_id == "RULE_CREATE_001"
    assert rule.crop_id == "cotton"
    assert rule.decision == "WAIT"
    assert rule.validation_status == ValidationStatus.UNVALIDATED
    assert rule.priority == Priority.HIGH


# 2. Rule validation status
def test_rule_validation_status():
    # Vague source should fail validation check
    assert validate_rule_source("Internet") is False
    assert validate_rule_source("AI knowledge") is False
    assert validate_rule_source("general farming practice") is False
    assert validate_rule_source("ICAR-CRIDA") is True

    # Rule with VALIDATED status but vague source must raise ValueError
    invalid_validated_rule = AdvisoryRule(
        rule_id="RULE_INVALID_001",
        crop_id="soybean",
        decision="SOW_NOW",
        advisory_text="Test",
        source_name="Internet",
        source_reference="Webpage",
        validation_status=ValidationStatus.VALIDATED
    )
    with pytest.raises(ValueError, match="approved, non-vague source"):
        validate_advisory_rule(invalid_validated_rule)


# 3. Rule registry registration
def test_rule_registry_registration(empty_registry, sample_unvalidated_rule):
    assert len(empty_registry.list_rules()) == 0
    empty_registry.register_rule(sample_unvalidated_rule)
    assert len(empty_registry.list_rules()) == 1
    retrieved = empty_registry.get_rule("RULE_TEST_UNVALIDATED_002")
    assert retrieved is not None
    assert retrieved.rule_id == "RULE_TEST_UNVALIDATED_002"


# 4. Rule lookup by crop
def test_rule_lookup_by_crop(empty_registry, sample_unvalidated_rule):
    empty_registry.register_rule(sample_unvalidated_rule)
    soy_rules = empty_registry.list_rules(crop_id="soybean")
    cotton_rules = empty_registry.list_rules(crop_id="cotton")
    assert len(soy_rules) == 1
    assert len(cotton_rules) == 0


# 5. Rule lookup by decision
def test_rule_lookup_by_decision(empty_registry, sample_unvalidated_rule):
    empty_registry.register_rule(sample_unvalidated_rule)
    sow_rules = empty_registry.list_rules(decision="SOW_NOW")
    wait_rules = empty_registry.list_rules(decision="WAIT")
    assert len(sow_rules) == 1
    assert len(wait_rules) == 0


# 6. Rule lookup by crop + decision
def test_rule_lookup_by_crop_and_decision(empty_registry, sample_unvalidated_rule):
    empty_registry.register_rule(sample_unvalidated_rule)
    matched = empty_registry.find_matching_rule(
        crop_id="soybean",
        decision="SOW_NOW",
        only_validated=False
    )
    assert matched is not None
    assert matched.rule_id == "RULE_TEST_UNVALIDATED_002"

    unmatched = empty_registry.find_matching_rule(
        crop_id="soybean",
        decision="WAIT",
        only_validated=False
    )
    assert unmatched is None


# 7. No matching rule returns NO_VALIDATED_RULE
def test_no_matching_rule_returns_no_validated_rule(empty_registry):
    engine = AdvisoryRuleEngine(registry=empty_registry)
    result = engine.evaluate(
        crop_id="pigeonpea",
        decision="SOW_NOW",
        probability=0.15
    )
    assert result.advisory_status == AdvisoryStatus.NO_VALIDATED_RULE
    assert result.advisory_text is None
    assert result.rule_id is None
    assert result.validation_status == ValidationStatus.UNAVAILABLE


# 8. Unvalidated rule is not treated as validated
def test_unvalidated_rule_is_not_treated_as_validated(empty_registry, sample_unvalidated_rule):
    empty_registry.register_rule(sample_unvalidated_rule)
    engine = AdvisoryRuleEngine(registry=empty_registry)

    # find_matching_rule with only_validated=True must return None
    matched = empty_registry.find_matching_rule("soybean", "SOW_NOW", only_validated=True)
    assert matched is None

    # Advisory evaluation must return NO_VALIDATED_RULE
    result = engine.evaluate("soybean", "SOW_NOW", probability=0.10)
    assert result.advisory_status == AdvisoryStatus.NO_VALIDATED_RULE
    assert result.advisory_text is None


# 9. Validated rule returns RULE_MATCHED
def test_validated_rule_returns_rule_matched(empty_registry, sample_validated_rule):
    empty_registry.register_rule(sample_validated_rule)
    engine = AdvisoryRuleEngine(registry=empty_registry)

    result = engine.evaluate("soybean", "SOW_NOW", probability=0.12)
    assert result.advisory_status == AdvisoryStatus.RULE_MATCHED
    assert result.rule_id == "RULE_TEST_VALIDATED_001"
    assert result.advisory_text is not None
    assert "Validated test advisory" in result.advisory_text
    assert result.action_type == "FULL_SOWING"


# 10. Rule source metadata preserved
def test_rule_source_metadata_preserved(empty_registry, sample_validated_rule):
    empty_registry.register_rule(sample_validated_rule)
    engine = AdvisoryRuleEngine(registry=empty_registry)

    result = engine.evaluate("soybean", "SOW_NOW")
    assert result.source is not None
    assert result.source.source_name == "ICAR-CRIDA"
    assert "Vidarbha Zone" in result.source.source_reference
    assert result.source.source_version == "v2.1"
    assert result.source.source_date == "2023-05"


# 11. Language field preserved
def test_language_field_preserved(empty_registry, sample_validated_rule):
    empty_registry.register_rule(sample_validated_rule)
    engine = AdvisoryRuleEngine(registry=empty_registry)

    result_en = engine.evaluate("soybean", "SOW_NOW", language="en")
    assert result_en.language == "en"

    # Non-existent language returns NO_VALIDATED_RULE
    result_mr = engine.evaluate("soybean", "SOW_NOW", language="mr")
    assert result_mr.advisory_status == AdvisoryStatus.NO_VALIDATED_RULE


# 12. Advisory result always contains is_operational=false
def test_advisory_result_always_contains_is_operational_false(
    empty_registry,
    sample_validated_rule,
    sample_unvalidated_rule
):
    empty_registry.register_rule(sample_validated_rule)
    engine = AdvisoryRuleEngine(registry=empty_registry)

    # Validated matched rule
    res_matched = engine.evaluate("soybean", "SOW_NOW")
    assert res_matched.is_operational is False

    # Unmatched rule
    res_unmatched = engine.evaluate("cotton", "WAIT")
    assert res_unmatched.is_operational is False


# 13. No rule produces no agronomic recommendation
def test_no_rule_produces_no_agronomic_recommendation(empty_registry):
    engine = AdvisoryRuleEngine(registry=empty_registry)
    result = engine.evaluate("soybean", "WAIT", probability=0.85)

    assert result.action_type is None
    assert result.advisory_text is None
    assert result.reason is None
    assert result.rule_id is None
    assert result.source is None
    assert result.validation_status == ValidationStatus.UNAVAILABLE


# 14. API endpoint works
def test_api_advisory_endpoint_works(client):
    # Unmatched crop returns NO_VALIDATED_RULE
    response_unmatched = client.get("/api/advisory/BLK001?crop_id=sugarcane")
    assert response_unmatched.status_code == 200
    data_unmatched = response_unmatched.json()

    assert data_unmatched["block_id"] == "BLK001"
    assert data_unmatched["crop_id"] == "sugarcane"
    assert "decision" in data_unmatched
    assert "probability" in data_unmatched
    assert data_unmatched["probability_status"] == "RAW_PROTOTYPE"
    assert data_unmatched["decision_status"] == "PROTOTYPE_ONLY"
    assert data_unmatched["advisory_status"] == "NO_VALIDATED_RULE"
    assert data_unmatched["action_type"] is None
    assert data_unmatched["advisory_text"] is None
    assert data_unmatched["rule_id"] is None
    assert data_unmatched["source"] is None
    assert data_unmatched["validation_status"] == "UNAVAILABLE"
    assert data_unmatched["language"] == "en"
    assert data_unmatched["is_operational"] is False
    assert "scientific_warning" in data_unmatched

    # Validated crop (soybean SOW_NOW) returns RULE_MATCHED
    response_matched = client.get("/api/advisory/BLK001?crop_id=soybean")
    assert response_matched.status_code == 200
    data_matched = response_matched.json()
    assert data_matched["advisory_status"] == "RULE_MATCHED"
    assert data_matched["rule_id"] == "RULE_CRIDA_MH_SOYBEAN_SOW_NOW"
    assert data_matched["action_type"] == "FULL_SOWING"
    assert data_matched["source"]["source_name"] is not None


# 15. Existing forecast endpoint works
def test_existing_forecast_endpoint_works(client):
    response = client.get("/api/forecast/BLK001/false-onset")
    assert response.status_code == 200
    data = response.json()
    assert data["block_id"] == "BLK001"
    assert "raw_probability" in data
    assert "probability" in data
    assert data["target"] in ["FALSE_ONSET", "target_false_onset_7d"]


# 16. Existing decision endpoint works
def test_existing_decision_endpoint_works(client):
    response = client.get("/api/forecast/BLK001/false-onset/decision")
    assert response.status_code == 200
    data = response.json()
    assert data["block_id"] == "BLK001"
    assert data["decision"] in ["SOW_NOW", "SOW_PART_NOW", "WAIT"]
    assert data["decision_status"] == "PROTOTYPE_ONLY"
    assert data["is_operational"] is False


# 17. No communication is triggered
def test_no_communication_is_triggered(client):
    # Verify no SMS, WhatsApp, Voice, or Alert table records are generated during advisory requests
    alerts_before = client.get("/api/alerts").json()
    response = client.get("/api/advisory/BLK001?crop_id=cotton")
    assert response.status_code == 200
    alerts_after = client.get("/api/alerts").json()

    assert len(alerts_before) == len(alerts_after)


# 18. No ML code is duplicated
def test_no_ml_code_duplicated():
    import app.advisory.rule_engine as engine_mod
    import app.advisory.rule_registry as registry_mod
    import app.advisory.models as models_mod

    for mod in [engine_mod, registry_mod, models_mod]:
        src = dir(mod)
        assert "LogisticRegression" not in src
        assert "CalibratedClassifierCV" not in src
        assert "train_model" not in src


# 19. No unsupported advisory text generated
def test_no_unsupported_advisory_text_generated():
    counts = default_rule_registry.count_rules()
    assert counts["validated_rules"] >= 6
    assert counts["review_required_rules"] >= 2
    assert counts["unvalidated_rules"] >= 3

    # For an unvalidated combination (cotton SOW_PART_NOW), no advice must be generated
    engine = AdvisoryRuleEngine(registry=default_rule_registry)
    res = engine.evaluate(crop_id="cotton", decision="SOW_PART_NOW")
    assert res.advisory_status == AdvisoryStatus.NO_VALIDATED_RULE
    assert res.advisory_text is None
    assert res.action_type is None


# 20. Scientific integrity: no agronomic instruction without validation
def test_scientific_integrity_no_agronomic_instruction_without_validation():
    """
    Explicit test:
    If no validated rule exists for crop = soybean, decision = SOW_NOW,
    advisory_text must NOT contain an agronomic instruction.
    (e.g., must NOT contain 'sow now', 'apply fertilizer', 'irrigate', 'use seed', 'spray').
    The system should return NO_VALIDATED_RULE instead.
    """
    # Evaluate with a registry lacking a validated rule for this scenario
    unvalidated_registry = RuleRegistry()
    engine = AdvisoryRuleEngine(registry=unvalidated_registry)
    res = engine.evaluate(crop_id="soybean", decision="SOW_NOW")

    assert res.advisory_status == AdvisoryStatus.NO_VALIDATED_RULE
    assert res.advisory_text is None

    # Verify no forbidden imperative advice strings
    forbidden_terms = [
        "sow now",
        "apply fertilizer",
        "irrigate",
        "use seed",
        "spray"
    ]
    warning_text = (res.scientific_warning or "").lower()
    for term in forbidden_terms:
        assert term not in warning_text, f"Forbidden term '{term}' found in warning: {warning_text}"
