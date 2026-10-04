"""
Meghvani Phase 5A: Advisory Rule Registry.

Maintains registered agronomic advisory rules with multi-dimensional matching
(crop_id, decision, language) and strict validation status enforcement.
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
import yaml

from app.advisory.models import AdvisoryRule, ValidationStatus, Priority
from app.advisory.validation import validate_advisory_rule
from app.config import CONFIG_DIR

logger = logging.getLogger(__name__)


class RuleRegistry:
    """
    Central registry for advisory rules. Enforces that only rules with
    validation_status == VALIDATED can be returned for operational matching.
    """

    def __init__(self):
        self._rules: Dict[str, AdvisoryRule] = {}

    def register_rule(self, rule: AdvisoryRule) -> None:
        """
        Validates and registers an advisory rule.
        """
        validate_advisory_rule(rule)
        self._rules[rule.rule_id] = rule
        logger.debug(f"Registered advisory rule: {rule.rule_id} ({rule.crop_id} / {rule.decision})")

    def get_rule(self, rule_id: str) -> Optional[AdvisoryRule]:
        """
        Retrieves a rule by its unique rule_id.
        """
        return self._rules.get(rule_id)

    def find_matching_rule(
        self,
        crop_id: str,
        decision: str,
        language: str = "en",
        geography: Optional[str] = None,
        only_validated: bool = True
    ) -> Optional[AdvisoryRule]:
        """
        Matches a rule by crop_id, decision, language, and geography.
        If only_validated=True (default), ignores any rule whose status is not VALIDATED.
        """
        norm_crop = crop_id.strip().lower()
        norm_dec = decision.strip().upper()
        norm_lang = language.strip().lower()
        norm_geo = geography.strip().lower() if geography else None

        for rule in self._rules.values():
            if (
                rule.crop_id.strip().lower() == norm_crop
                and rule.decision.strip().upper() == norm_dec
                and rule.language.strip().lower() == norm_lang
            ):
                if norm_geo:
                    rule_geo = (rule.geography or "").strip().lower()
                    if rule_geo != norm_geo and rule_geo not in ["all", "india", "national"]:
                        continue

                if only_validated and rule.validation_status != ValidationStatus.VALIDATED:
                    continue
                return rule

        return None

    def list_rules(
        self,
        crop_id: Optional[str] = None,
        decision: Optional[str] = None,
        validation_status: Optional[str] = None,
        geography: Optional[str] = None,
        source_institution: Optional[str] = None
    ) -> List[AdvisoryRule]:
        """
        Lists all registered rules with optional filters.
        """
        results = list(self._rules.values())
        if crop_id:
            results = [r for r in results if r.crop_id.lower() == crop_id.strip().lower()]
        if decision:
            results = [r for r in results if r.decision.upper() == decision.strip().upper()]
        if validation_status:
            results = [r for r in results if r.validation_status == validation_status]
        if geography:
            results = [r for r in results if (r.geography or "").lower() == geography.strip().lower()]
        if source_institution:
            results = [
                r for r in results
                if source_institution.strip().lower() in (r.source_institution or r.source_name or "").lower()
            ]
        return results

    def count_rules(self) -> Dict[str, int]:
        """
        Returns rule counts partitioned by validation status.
        """
        total = len(self._rules)
        validated = sum(1 for r in self._rules.values() if r.validation_status == ValidationStatus.VALIDATED)
        unvalidated = sum(1 for r in self._rules.values() if r.validation_status == ValidationStatus.UNVALIDATED)
        review_required = sum(1 for r in self._rules.values() if r.validation_status == ValidationStatus.REVIEW_REQUIRED)

        return {
            "total_rules": total,
            "validated_rules": validated,
            "unvalidated_rules": unvalidated,
            "review_required_rules": review_required
        }

    def load_from_yaml(self, file_path: Path) -> int:
        """
        Loads rules from an external YAML file.
        Extracts all Phase 5B source traceability and geography fields.
        """
        if not file_path.exists():
            logger.warning(f"Advisory rules file not found: {file_path}")
            return 0

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        rules_list = data.get("agronomic_rules", [])
        count = 0
        for item in rules_list:
            try:
                rule = AdvisoryRule(
                    rule_id=item["rule_id"],
                    crop_id=item["crop_id"],
                    geography=item.get("geography", "Maharashtra"),
                    decision=item["decision"],
                    trigger_condition=item.get("trigger_condition") or item.get("trigger"),
                    action=item.get("action") or item.get("action_type"),
                    action_type=item.get("action_type") or item.get("action"),
                    advisory_text=item["advisory_text"],
                    rationale=item.get("rationale") or item.get("reason"),
                    reason=item.get("reason") or item.get("rationale"),
                    source_institution=item.get("source_institution") or item.get("source_name"),
                    source_title=item.get("source_title"),
                    source_document_identifier=item.get("source_document_identifier"),
                    source_version=item.get("source_version"),
                    publication_date=item.get("publication_date") or item.get("source_date"),
                    source_url_or_reference=item.get("source_url_or_reference") or item.get("source_reference"),
                    page_or_section=item.get("page_or_section"),
                    source_name=item.get("source_name") or item.get("source_institution"),
                    source_reference=item.get("source_reference") or item.get("source_url_or_reference") or item.get("source_title"),
                    source_date=item.get("source_date") or item.get("publication_date"),
                    validation_status=ValidationStatus(item.get("validation_status", "UNVALIDATED")),
                    validation_notes=item.get("validation_notes"),
                    reviewed_at=item.get("reviewed_at"),
                    source_supported_conditions=item.get("source_supported_conditions") or [],
                    meghvani_decision_conditions=item.get("meghvani_decision_conditions") or [],
                    source_vs_model_boundary=item.get("source_vs_model_boundary"),
                    language=item.get("language", "en"),
                    priority=Priority(item.get("priority", "NORMAL"))
                )
                self.register_rule(rule)
                count += 1
            except Exception as e:
                logger.error(f"Failed to load advisory rule {item.get('rule_id')}: {e}")

        logger.info(f"Loaded {count} agronomic advisory rules from {file_path}")
        return count


# Singleton instance
default_rule_registry = RuleRegistry()

# Load data-driven rules if file exists
AGRONOMIC_RULES_YAML = CONFIG_DIR / "agronomic_rules.yaml"
if AGRONOMIC_RULES_YAML.exists():
    default_rule_registry.load_from_yaml(AGRONOMIC_RULES_YAML)
