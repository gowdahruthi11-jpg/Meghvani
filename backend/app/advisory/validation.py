"""
Meghvani Phase 5A: Advisory Rule Validation and Quality Assurance.

Ensures source traceability, prevents vague or generic attributions,
and enforces that unsupported rules remain explicitly UNVALIDATED.
"""
from typing import Dict, Any, List
import logging
from app.advisory.models import AdvisoryRule, ValidationStatus

logger = logging.getLogger(__name__)

INVALID_VAGUE_SOURCES = {
    "internet",
    "ai knowledge",
    "general farming practice",
    "common sense",
    "unknown",
    "llm",
    "chatgpt",
    "generic"
}


def validate_rule_source(source_name: str) -> bool:
    """
    Validates that a source name is non-empty and not a forbidden vague attribution.
    """
    if not source_name or not source_name.strip():
        return False
    norm = source_name.strip().lower()
    for vague in INVALID_VAGUE_SOURCES:
        if vague in norm:
            return False
    return True


def validate_advisory_rule(rule: AdvisoryRule) -> bool:
    """
    Validates an advisory rule structure.
    Raises ValueError if rule violates integrity constraints.
    Enforces that a rule can be marked VALIDATED only if:
    1. The source institution is identifiable and non-vague.
    2. The exact document/guidance is identifiable.
    3. The source reference or URL is provided.
    4. Target crop and geography applicability are clear.
    """
    if not rule.rule_id or not rule.rule_id.strip():
        raise ValueError("Advisory rule must contain a non-empty rule_id.")

    if not rule.crop_id or not rule.crop_id.strip():
        raise ValueError(f"Rule {rule.rule_id} must specify a valid crop_id.")

    if not rule.geography or not rule.geography.strip():
        raise ValueError(f"Rule {rule.rule_id} must specify a valid geography.")

    valid_decisions = {"SOW_NOW", "SOW_PART_NOW", "WAIT"}
    if rule.decision not in valid_decisions:
        raise ValueError(
            f"Rule {rule.rule_id} has invalid decision '{rule.decision}'. Must be one of {valid_decisions}."
        )

    # If marked VALIDATED, source traceability must be complete, verified, and non-vague
    if rule.validation_status == ValidationStatus.VALIDATED:
        institution = rule.source_institution or rule.source_name
        if not institution or not validate_rule_source(institution):
            raise ValueError(
                f"Rule {rule.rule_id} cannot be marked VALIDATED without an approved, non-vague source institution."
            )

        document = rule.source_document_identifier or rule.source_title
        if not document or not document.strip():
            raise ValueError(
                f"Rule {rule.rule_id} cannot be marked VALIDATED without an identifiable source document or title."
            )

        reference = rule.source_url_or_reference or rule.source_reference
        if not reference or not reference.strip():
            raise ValueError(
                f"Rule {rule.rule_id} cannot be marked VALIDATED without a specific source document reference or URL."
            )

    return True
