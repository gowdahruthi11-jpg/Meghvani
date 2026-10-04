"""
Meghvani Phase 5B: Agronomic Source & Rule Registration Tests.

Covers:
1. Complete source metadata -> VALIDATED can be registered.
2. Missing source institution -> rejected if VALIDATED, or preserved as REVIEW_REQUIRED.
3. Missing source document -> rejected if VALIDATED, or preserved as REVIEW_REQUIRED.
4. Missing source reference -> rejected if VALIDATED, or preserved as REVIEW_REQUIRED.
5. Unvalidated rule cannot produce farmer advice.
6. REVIEW_REQUIRED rule cannot produce farmer advice.
7. VALIDATED rule can be matched.
8. Crop-specific matching works.
9. Geography-specific matching works.
10. Decision-specific matching works.
11. Existing Phase 1–5A tests remain passing.
12. No unsupported agronomic text is generated.
13. Inspection API GET /api/advisory/rules returns registered rules and supports filtering.
14. Sourced rules YAML and sources register file integrity.
"""
import pytest
from pathlib import Path
import yaml
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
from app.config import CONFIG_DIR


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def empty_registry():
    return RuleRegistry()


# 1. Complete source metadata -> VALIDATED can be registered
def test_complete_source_metadata_allows_validated_registration(empty_registry):
    rule = AdvisoryRule(
        rule_id="RULE_TEST_CRIDA_001",
        crop_id="soybean",
        geography="Maharashtra",
        decision="SOW_NOW",
        trigger_condition="Cumulative rain > 75mm with low false onset probability",
        action="FULL_SOWING",
        advisory_text="Sow soybean using certified seed on BBF system.",
        rationale="75-100mm moisture ensures uniform germination.",
        source_institution="ICAR-Central Research Institute for Dryland Agriculture (CRIDA)",
        source_title="District Agriculture Contingency Plan for District: Nagpur, Maharashtra",
        source_document_identifier="CRIDA-DACP-MH-NAGPUR-2020",
        source_version="2020.1",
        publication_date="2020-07",
        source_url_or_reference="http://agricoop.nic.in/sites/default/files/MH18-%20Nagpur.pdf",
        page_or_section="Section 2.1",
        validation_status=ValidationStatus.VALIDATED,
        language="en",
        priority=Priority.NORMAL
    )
    # Registration should succeed without error
    empty_registry.register_rule(rule)
    retrieved = empty_registry.get_rule("RULE_TEST_CRIDA_001")
    assert retrieved is not None
    assert retrieved.validation_status == ValidationStatus.VALIDATED
    assert retrieved.source_institution == "ICAR-Central Research Institute for Dryland Agriculture (CRIDA)"


# 2. Missing source institution -> rejected if VALIDATED
def test_missing_source_institution_rejected_for_validated(empty_registry):
    rule = AdvisoryRule(
        rule_id="RULE_INVALID_INSTITUTION",
        crop_id="soybean",
        geography="Maharashtra",
        decision="SOW_NOW",
        advisory_text="Test advisory",
        source_institution="",
        source_name=None,
        source_title="Some Document",
        source_document_identifier="DOC-001",
        source_url_or_reference="https://example.com",
        validation_status=ValidationStatus.VALIDATED
    )
    with pytest.raises(ValueError, match="approved, non-vague source institution"):
        validate_advisory_rule(rule)

    # Allowed as REVIEW_REQUIRED
    rule.validation_status = ValidationStatus.REVIEW_REQUIRED
    assert validate_advisory_rule(rule) is True
    empty_registry.register_rule(rule)
    assert empty_registry.get_rule("RULE_INVALID_INSTITUTION") is not None


# 3. Missing source document -> rejected if VALIDATED
def test_missing_source_document_rejected_for_validated(empty_registry):
    rule = AdvisoryRule(
        rule_id="RULE_INVALID_DOCUMENT",
        crop_id="cotton",
        geography="Maharashtra",
        decision="WAIT",
        advisory_text="Delay sowing",
        source_institution="ICAR-CICR",
        source_title="",
        source_document_identifier="",
        source_url_or_reference="https://cicr.icar.gov.in/",
        validation_status=ValidationStatus.VALIDATED
    )
    with pytest.raises(ValueError, match="identifiable source document or title"):
        validate_advisory_rule(rule)

    # Allowed as REVIEW_REQUIRED
    rule.validation_status = ValidationStatus.REVIEW_REQUIRED
    assert validate_advisory_rule(rule) is True


# 4. Missing source reference -> rejected if VALIDATED
def test_missing_source_reference_rejected_for_validated(empty_registry):
    rule = AdvisoryRule(
        rule_id="RULE_INVALID_REFERENCE",
        crop_id="pigeonpea",
        geography="Maharashtra",
        decision="WAIT",
        advisory_text="Hold sowing",
        source_institution="Dr. PDKV Akola",
        source_title="Pigeonpea Guidelines",
        source_document_identifier="PDKV-TUR-2023",
        source_url_or_reference="",
        source_reference="",
        validation_status=ValidationStatus.VALIDATED
    )
    with pytest.raises(ValueError, match="specific source document reference or URL"):
        validate_advisory_rule(rule)

    # Allowed as REVIEW_REQUIRED
    rule.validation_status = ValidationStatus.REVIEW_REQUIRED
    assert validate_advisory_rule(rule) is True


# 5. Unvalidated rule cannot produce farmer advice
def test_unvalidated_rule_cannot_produce_farmer_advice(empty_registry):
    demo_rule = AdvisoryRule(
        rule_id="RULE_DEMO_SOY_01",
        crop_id="soybean",
        geography="Maharashtra",
        decision="SOW_NOW",
        advisory_text="Unvalidated demo advice: sow now.",
        source_institution="ICAR-CRIDA",
        source_title="Draft Note",
        source_url_or_reference="http://example.com",
        validation_status=ValidationStatus.UNVALIDATED
    )
    empty_registry.register_rule(demo_rule)
    engine = AdvisoryRuleEngine(registry=empty_registry)

    result = engine.evaluate(crop_id="soybean", decision="SOW_NOW", geography="Maharashtra")
    assert result.advisory_status == AdvisoryStatus.NO_VALIDATED_RULE
    assert result.advisory_text is None
    assert result.action_type is None
    assert result.is_operational is False


# 6. REVIEW_REQUIRED rule cannot produce farmer advice
def test_review_required_rule_cannot_produce_farmer_advice(empty_registry):
    candidate_rule = AdvisoryRule(
        rule_id="RULE_CANDIDATE_01",
        crop_id="cotton",
        geography="Maharashtra",
        decision="SOW_PART_NOW",
        advisory_text="Candidate intercropping: split sow cotton.",
        source_institution="ICAR-CICR Nagpur",
        source_title="Contingency Technical Note",
        source_url_or_reference="https://cicr.icar.gov.in/",
        validation_status=ValidationStatus.REVIEW_REQUIRED
    )
    empty_registry.register_rule(candidate_rule)
    engine = AdvisoryRuleEngine(registry=empty_registry)

    result = engine.evaluate(crop_id="cotton", decision="SOW_PART_NOW", geography="Maharashtra")
    assert result.advisory_status == AdvisoryStatus.NO_VALIDATED_RULE
    assert result.advisory_text is None
    assert result.action_type is None
    assert result.is_operational is False


# 7. VALIDATED rule can be matched
def test_validated_rule_can_be_matched(empty_registry):
    validated_rule = AdvisoryRule(
        rule_id="RULE_VALIDATED_SOY_01",
        crop_id="soybean",
        geography="Maharashtra",
        decision="SOW_NOW",
        action="FULL_SOWING",
        advisory_text="Sow soybean on BBF after 75-100mm soaking rain.",
        rationale="Adequate moisture ensures uniform germination.",
        source_institution="ICAR-Central Research Institute for Dryland Agriculture (CRIDA)",
        source_title="District Agriculture Contingency Plan - Nagpur",
        source_document_identifier="CRIDA-DACP-MH-NAGPUR-2020",
        source_version="2020.1",
        publication_date="2020-07",
        source_url_or_reference="http://agricoop.nic.in/sites/default/files/MH18-%20Nagpur.pdf",
        page_or_section="Section 2.1",
        validation_status=ValidationStatus.VALIDATED
    )
    empty_registry.register_rule(validated_rule)
    engine = AdvisoryRuleEngine(registry=empty_registry)

    result = engine.evaluate(crop_id="soybean", decision="SOW_NOW", geography="Maharashtra")
    assert result.advisory_status == AdvisoryStatus.RULE_MATCHED
    assert result.advisory_text is not None
    assert "Sow soybean on BBF" in result.advisory_text
    assert result.rule_id == "RULE_VALIDATED_SOY_01"
    assert result.action_type == "FULL_SOWING"
    assert result.source is not None
    assert result.source.source_institution == "ICAR-Central Research Institute for Dryland Agriculture (CRIDA)"
    assert result.is_operational is False


# 8. Crop-specific matching works
def test_crop_specific_matching(empty_registry):
    soy_rule = AdvisoryRule(
        rule_id="RULE_SOY_01",
        crop_id="soybean",
        geography="Maharashtra",
        decision="WAIT",
        advisory_text="Defer soybean sowing.",
        source_institution="ICAR-CRIDA",
        source_title="DACP Nagpur",
        source_url_or_reference="http://agricoop.nic.in/",
        validation_status=ValidationStatus.VALIDATED
    )
    cotton_rule = AdvisoryRule(
        rule_id="RULE_COTTON_01",
        crop_id="cotton",
        geography="Maharashtra",
        decision="WAIT",
        advisory_text="Defer cotton sowing; avoid dry sowing.",
        source_institution="ICAR-CICR",
        source_title="Cotton Advisory",
        source_url_or_reference="https://cicr.icar.gov.in/",
        validation_status=ValidationStatus.VALIDATED
    )
    empty_registry.register_rule(soy_rule)
    empty_registry.register_rule(cotton_rule)
    engine = AdvisoryRuleEngine(registry=empty_registry)

    res_soy = engine.evaluate("soybean", "WAIT")
    assert res_soy.rule_id == "RULE_SOY_01"
    assert "Defer soybean" in res_soy.advisory_text

    res_cotton = engine.evaluate("cotton", "WAIT")
    assert res_cotton.rule_id == "RULE_COTTON_01"
    assert "Defer cotton" in res_cotton.advisory_text

    res_pigeonpea = engine.evaluate("pigeonpea", "WAIT")
    assert res_pigeonpea.advisory_status == AdvisoryStatus.NO_VALIDATED_RULE


# 9. Geography-specific matching works
def test_geography_specific_matching(empty_registry):
    maha_rule = AdvisoryRule(
        rule_id="RULE_MAHA_01",
        crop_id="soybean",
        geography="Maharashtra",
        decision="SOW_NOW",
        advisory_text="Vidarbha / Maharashtra sowing protocol.",
        source_institution="ICAR-CRIDA",
        source_title="DACP Maharashtra",
        source_url_or_reference="http://crida.in/",
        validation_status=ValidationStatus.VALIDATED
    )
    empty_registry.register_rule(maha_rule)
    engine = AdvisoryRuleEngine(registry=empty_registry)

    # Matches Maharashtra
    res_maha = engine.evaluate("soybean", "SOW_NOW", geography="Maharashtra")
    assert res_maha.advisory_status == AdvisoryStatus.RULE_MATCHED

    # Does not match Karnataka
    res_kar = engine.evaluate("soybean", "SOW_NOW", geography="Karnataka")
    assert res_kar.advisory_status == AdvisoryStatus.NO_VALIDATED_RULE


# 10. Decision-specific matching works
def test_decision_specific_matching(empty_registry):
    sow_rule = AdvisoryRule(
        rule_id="RULE_DEC_SOW",
        crop_id="soybean",
        geography="Maharashtra",
        decision="SOW_NOW",
        advisory_text="Sow now advisory.",
        source_institution="ICAR-CRIDA",
        source_title="DACP",
        source_url_or_reference="http://crida.in/",
        validation_status=ValidationStatus.VALIDATED
    )
    wait_rule = AdvisoryRule(
        rule_id="RULE_DEC_WAIT",
        crop_id="soybean",
        geography="Maharashtra",
        decision="WAIT",
        advisory_text="Wait advisory.",
        source_institution="ICAR-CRIDA",
        source_title="DACP",
        source_url_or_reference="http://crida.in/",
        validation_status=ValidationStatus.VALIDATED
    )
    empty_registry.register_rule(sow_rule)
    empty_registry.register_rule(wait_rule)
    engine = AdvisoryRuleEngine(registry=empty_registry)

    res_sow = engine.evaluate("soybean", "SOW_NOW")
    assert res_sow.rule_id == "RULE_DEC_SOW"

    res_wait = engine.evaluate("soybean", "WAIT")
    assert res_wait.rule_id == "RULE_DEC_WAIT"

    res_part = engine.evaluate("soybean", "SOW_PART_NOW")
    assert res_part.advisory_status == AdvisoryStatus.NO_VALIDATED_RULE


# 11. Sourced rules YAML integrity and rule count partitions
def test_agronomic_rules_yaml_integrity():
    rules_path = CONFIG_DIR / "agronomic_rules.yaml"
    assert rules_path.exists()

    reg = RuleRegistry()
    loaded_count = reg.load_from_yaml(rules_path)
    assert loaded_count >= 11

    counts = reg.count_rules()
    assert counts["validated_rules"] >= 6
    assert counts["review_required_rules"] >= 2
    assert counts["unvalidated_rules"] >= 3


# 12. No unsupported agronomic text is generated for unvalidated combinations
def test_no_unsupported_agronomic_text_generated():
    engine = AdvisoryRuleEngine(registry=default_rule_registry)
    # Check a crop that has NO validated rule for SOW_PART_NOW (e.g. cotton or pigeonpea)
    res = engine.evaluate(crop_id="cotton", decision="SOW_PART_NOW")
    assert res.advisory_status == AdvisoryStatus.NO_VALIDATED_RULE
    assert res.advisory_text is None
    assert res.action_type is None


# 13. Inspection API GET /api/advisory/rules works
def test_api_list_advisory_rules(client):
    response = client.get("/api/advisory/rules")
    assert response.status_code == 200
    rules = response.json()
    assert isinstance(rules, list)
    assert len(rules) >= 11

    # Filter by crop_id
    res_soy = client.get("/api/advisory/rules?crop_id=soybean")
    assert res_soy.status_code == 200
    for r in res_soy.json():
        assert r["crop_id"] == "soybean"

    # Filter by validation_status=VALIDATED
    res_val = client.get("/api/advisory/rules?validation_status=VALIDATED")
    assert res_val.status_code == 200
    assert len(res_val.json()) >= 6
    for r in res_val.json():
        assert r["validation_status"] == "VALIDATED"
        assert r["source_institution"] is not None

    # Filter by validation_status=REVIEW_REQUIRED
    res_rev = client.get("/api/advisory/rules?validation_status=REVIEW_REQUIRED")
    assert res_rev.status_code == 200
    assert len(res_rev.json()) >= 2


# 14. Sources register YAML file exists and is valid
def test_agronomic_sources_yaml_file_exists():
    sources_path = CONFIG_DIR / "agronomic_sources.yaml"
    assert sources_path.exists()
    with open(sources_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert "sources" in data
    assert len(data["sources"]) >= 4
    for src in data["sources"]:
        assert "source_id" in src
        assert "institution" in src
        assert "title" in src
        assert "document_identifier" in src
        assert "url_or_reference" in src


# =========================================================================
# PHASE 5B.1: SOURCE / MODEL BOUNDARY PROVENANCE TESTS
# =========================================================================

def test_source_supported_conditions_stored_separately():
    """
    Test that institutional source conditions and Meghvani decision conditions
    are stored in distinct fields on every VALIDATED rule.
    """
    validated_rules = [
        r for r in default_rule_registry.list_rules()
        if r.validation_status == ValidationStatus.VALIDATED
    ]
    assert len(validated_rules) == 6

    for r in validated_rules:
        # 1. Source supported conditions must be populated
        assert len(r.source_supported_conditions) > 0, f"Rule {r.rule_id} missing source_supported_conditions"
        for cond in r.source_supported_conditions:
            assert isinstance(cond, str)
            assert len(cond) > 10

        # 2. Meghvani decision conditions must be populated
        assert len(r.meghvani_decision_conditions) > 0, f"Rule {r.rule_id} missing meghvani_decision_conditions"
        for cond in r.meghvani_decision_conditions:
            assert isinstance(cond, str)
            assert len(cond) > 10

        # 3. Explicit boundary statement must be present
        assert r.source_vs_model_boundary is not None, f"Rule {r.rule_id} missing source_vs_model_boundary"
        assert len(r.source_vs_model_boundary) > 20


def test_source_attribution_does_not_include_prototype_threshold():
    """
    Test that institutional sources are NOT falsely credited with Meghvani's
    prototype probability thresholds (0.30, 0.60, 30%, 60%).
    """
    validated_rules = [
        r for r in default_rule_registry.list_rules()
        if r.validation_status == ValidationStatus.VALIDATED
    ]

    for r in validated_rules:
        # Check source institution and source document
        for text in [r.source_institution, r.source_title, r.source_reference, r.advisory_text, r.rationale]:
            if text:
                assert "< 0.30" not in text and "<0.30" not in text, f"Source text in {r.rule_id} falsely includes 0.30 threshold"
                assert ">= 0.60" not in text and ">=0.60" not in text, f"Source text in {r.rule_id} falsely includes 0.60 threshold"
                assert "30%" not in text, f"Source text in {r.rule_id} falsely includes 30% probability"
                assert "60%" not in text, f"Source text in {r.rule_id} falsely includes 60% probability"

        # Check source supported conditions: should NEVER cite model probability thresholds
        for s_cond in r.source_supported_conditions:
            assert "0.30" not in s_cond
            assert "0.60" not in s_cond
            assert "probability" not in s_cond.lower()

        # Meghvani decision conditions SHOULD contain the prototype threshold
        combined_meghvani_conds = " ".join(r.meghvani_decision_conditions)
        if r.decision == "SOW_NOW":
            assert "0.30" in combined_meghvani_conds or "< 0.30" in combined_meghvani_conds or "<0.30" in combined_meghvani_conds
        elif r.decision == "WAIT":
            assert "0.60" in combined_meghvani_conds or ">= 0.60" in combined_meghvani_conds or ">=0.60" in combined_meghvani_conds


def test_api_exposes_provenance_boundary(client):
    """
    Test that GET /api/advisory/rules exposes source_supported_conditions,
    meghvani_decision_conditions, and source_vs_model_boundary for review.
    """
    response = client.get("/api/advisory/rules?validation_status=VALIDATED")
    assert response.status_code == 200
    rules = response.json()
    assert len(rules) == 6

    for r in rules:
        assert "source_supported_conditions" in r
        assert isinstance(r["source_supported_conditions"], list)
        assert len(r["source_supported_conditions"]) > 0

        assert "meghvani_decision_conditions" in r
        assert isinstance(r["meghvani_decision_conditions"], list)
        assert len(r["meghvani_decision_conditions"]) > 0

        assert "source_vs_model_boundary" in r
        assert r["source_vs_model_boundary"] is not None

        assert r["source_institution"] is not None
        assert r["source_title"] is not None
        assert r["validation_status"] == "VALIDATED"


def test_advisory_evaluation_propagates_source_vs_model_boundary():
    """
    Test that evaluating an advisory attaches the source_vs_model_boundary
    to the AdvisoryResult.
    """
    engine = AdvisoryRuleEngine(registry=default_rule_registry)
    result = engine.evaluate(crop_id="soybean", decision="SOW_NOW", geography="Maharashtra")
    assert result.advisory_status == AdvisoryStatus.RULE_MATCHED
    assert result.rule_id == "RULE_CRIDA_MH_SOYBEAN_SOW_NOW"
    assert result.source_vs_model_boundary is not None
    assert "ICAR-CRIDA" in result.source_vs_model_boundary
    assert "prototype parameter" in result.source_vs_model_boundary


def test_review_required_rules_still_cannot_produce_advice():
    """
    Test that candidate contingency rules marked REVIEW_REQUIRED
    (e.g., SOW_PART_NOW for soybean/cotton) are not returned by the engine.
    """
    engine = AdvisoryRuleEngine(registry=default_rule_registry)
    result = engine.evaluate(crop_id="soybean", decision="SOW_PART_NOW", geography="Maharashtra")
    assert result.advisory_status == AdvisoryStatus.NO_VALIDATED_RULE
    assert result.advisory_text is None
    assert result.action_type is None


def test_unvalidated_rules_still_cannot_produce_advice():
    """
    Test that demonstration rules marked UNVALIDATED
    are not returned by the engine.
    """
    engine = AdvisoryRuleEngine(registry=default_rule_registry)
    for crop in ["soybean", "cotton", "pigeonpea"]:
        for dec in ["SOW_NOW", "WAIT"]:
            res = engine.evaluate(crop_id=crop, decision=dec, geography="Maharashtra")
            if res.advisory_status == AdvisoryStatus.RULE_MATCHED:
                assert res.validation_status == ValidationStatus.VALIDATED
                assert not res.rule_id.startswith("RULE_DEMO_")


def test_existing_advisory_endpoint_behavior_remains_unchanged(client):
    """
    Test that GET /api/advisory/{block_id} works seamlessly with new fields,
    returns is_operational=False, and preserves scientific warnings.
    """
    response = client.get("/api/advisory/BLK001?crop_id=soybean")
    assert response.status_code == 200
    data = response.json()
    assert data["block_id"] == "BLK001"
    assert data["crop_id"] == "soybean"
    assert data["is_operational"] is False
    assert "scientific_warning" in data
    assert "source_vs_model_boundary" in data

