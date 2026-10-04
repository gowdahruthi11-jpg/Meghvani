"""
Meghvani Phase 5A: Advisory Rule Engine.

Pure decision-to-advisory translation engine. Takes decision-support outputs
and queries the RuleRegistry for validated crop-specific agronomic rules.

CRITICAL SAFETY RULE:
NO RULE = NO ADVICE.
If no validated rule exists for the crop and decision, the engine returns
advisory_status = NO_VALIDATED_RULE with advisory_text = None.
It NEVER invents sowing dates, seed rates, or generic farming advice.
"""
from typing import Optional, Dict, Any
import logging

from app.advisory.models import (
    AdvisoryResult,
    AdvisoryStatus,
    ValidationStatus,
    RuleSource
)
from app.advisory.rule_registry import RuleRegistry, default_rule_registry
from app.advisory.templates import NO_RULE_WARNING

logger = logging.getLogger(__name__)


class AdvisoryRuleEngine:
    """
    Evaluates prototype decisions against registered agronomic rules.
    Independent from database, ML modeling, and communication providers.
    """

    def __init__(self, registry: Optional[RuleRegistry] = None):
        self.registry = registry or default_rule_registry

    def evaluate(
        self,
        crop_id: str,
        decision: str,
        probability: Optional[float] = None,
        probability_status: str = "RAW_PROTOTYPE",
        decision_status: str = "PROTOTYPE_ONLY",
        block_id: Optional[str] = None,
        geography: Optional[str] = "Maharashtra",
        language: str = "en"
    ) -> AdvisoryResult:
        """
        Translates a prototype decision, crop, and geography into a structured AdvisoryResult.
        """
        norm_crop = (crop_id or "").strip().lower()
        norm_dec = (decision or "").strip().upper()
        norm_geo = (geography or "Maharashtra").strip()

        # Handle unavailable decision inputs
        if not norm_crop or norm_dec == "UNAVAILABLE" or not norm_dec:
            return AdvisoryResult(
                block_id=block_id,
                crop_id=crop_id,
                geography=norm_geo,
                decision=decision,
                probability=probability,
                probability_status=probability_status,
                decision_status=decision_status,
                advisory_status=AdvisoryStatus.UNAVAILABLE,
                action_type=None,
                advisory_text=None,
                rule_id=None,
                source=None,
                validation_status=ValidationStatus.UNAVAILABLE,
                language=language,
                is_operational=False,
                scientific_warning="Input decision or crop is invalid or unavailable."
            )

        # Lookup in registry: ONLY VALIDATED rules can match
        matched_rule = self.registry.find_matching_rule(
            crop_id=norm_crop,
            decision=norm_dec,
            language=language,
            geography=norm_geo,
            only_validated=True
        )

        if matched_rule is None:
            # NO VALIDATED RULE FOUND -> Clean, safe return
            logger.info(f"No validated agronomic rule found for crop '{norm_crop}', geography '{norm_geo}', decision '{norm_dec}'")
            return AdvisoryResult(
                block_id=block_id,
                crop_id=norm_crop,
                geography=norm_geo,
                decision=norm_dec,
                probability=probability,
                probability_status=probability_status,
                decision_status=decision_status,
                advisory_status=AdvisoryStatus.NO_VALIDATED_RULE,
                action_type=None,
                advisory_text=None,
                rule_id=None,
                source=None,
                validation_status=ValidationStatus.UNAVAILABLE,
                language=language,
                is_operational=False,
                scientific_warning=NO_RULE_WARNING
            )

        # VALIDATED RULE FOUND
        inst = matched_rule.source_institution or matched_rule.source_name
        ref = matched_rule.source_url_or_reference or matched_rule.source_reference or matched_rule.source_title
        dt = matched_rule.publication_date or matched_rule.source_date
        return AdvisoryResult(
            block_id=block_id,
            crop_id=norm_crop,
            geography=matched_rule.geography or norm_geo,
            decision=norm_dec,
            probability=probability,
            probability_status=probability_status,
            decision_status=decision_status,
            advisory_status=AdvisoryStatus.RULE_MATCHED,
            action_type=matched_rule.action_type or matched_rule.action,
            advisory_text=matched_rule.advisory_text,
            reason=matched_rule.reason or matched_rule.rationale,
            rule_id=matched_rule.rule_id,
            source=RuleSource(
                source_institution=inst,
                source_title=matched_rule.source_title,
                source_document_identifier=matched_rule.source_document_identifier,
                source_version=matched_rule.source_version,
                publication_date=dt,
                source_url_or_reference=ref,
                page_or_section=matched_rule.page_or_section,
                source_name=inst,
                source_reference=ref,
                source_date=dt
            ),
            source_supported_conditions=matched_rule.source_supported_conditions,
            meghvani_decision_conditions=matched_rule.meghvani_decision_conditions,
            source_vs_model_boundary=matched_rule.source_vs_model_boundary,
            validation_status=matched_rule.validation_status,
            language=matched_rule.language,
            is_operational=False,
            scientific_warning=(
                "This advisory is derived from an uncalibrated prototype model and is not verified for operational dispatch."
            )
        )
