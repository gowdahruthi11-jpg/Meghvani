"""
Meghvani Phase 5A: Advisory Rule Framework Package.
"""
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
from app.advisory.templates import get_neutral_template, NO_RULE_WARNING
from app.advisory.message_generator import (
    AdvisoryMessageGenerator,
    FarmerAdvisoryMessage,
    MessageLanguage,
    MessageChannel,
    MessageType
)

__all__ = [
    "AdvisoryRule",
    "AdvisoryResult",
    "ValidationStatus",
    "Priority",
    "AdvisoryStatus",
    "RuleSource",
    "RuleRegistry",
    "default_rule_registry",
    "AdvisoryRuleEngine",
    "validate_advisory_rule",
    "validate_rule_source",
    "get_neutral_template",
    "NO_RULE_WARNING",
    "AdvisoryMessageGenerator",
    "FarmerAdvisoryMessage",
    "MessageLanguage",
    "MessageChannel",
    "MessageType"
]
