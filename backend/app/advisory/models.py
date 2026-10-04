"""
Meghvani Phase 5A: Advisory Rule Framework Data Models.

Defines strictly typed models for agronomic advisory rules, validation statuses,
source traceability, and advisory evaluation results.
"""
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    UNVALIDATED = "UNVALIDATED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    VALIDATED = "VALIDATED"
    UNAVAILABLE = "UNAVAILABLE"


class Priority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AdvisoryStatus(str, Enum):
    NO_VALIDATED_RULE = "NO_VALIDATED_RULE"
    RULE_MATCHED = "RULE_MATCHED"
    UNAVAILABLE = "UNAVAILABLE"


class RuleSource(BaseModel):
    source_institution: Optional[str] = None
    source_title: Optional[str] = None
    source_document_identifier: Optional[str] = None
    source_version: Optional[str] = None
    publication_date: Optional[str] = None
    source_url_or_reference: Optional[str] = None
    page_or_section: Optional[str] = None
    source_name: Optional[str] = None  # backward compat
    source_reference: Optional[str] = None  # backward compat
    source_date: Optional[str] = None  # backward compat

    def model_post_init(self, __context: Any) -> None:
        if not self.source_name and self.source_institution:
            self.source_name = self.source_institution
        if not self.source_institution and self.source_name:
            self.source_institution = self.source_name
        if not self.source_reference and self.source_url_or_reference:
            self.source_reference = self.source_url_or_reference
        if not self.source_url_or_reference and self.source_reference:
            self.source_url_or_reference = self.source_reference
        if not self.source_date and self.publication_date:
            self.source_date = self.publication_date


class AdvisoryRule(BaseModel):
    rule_id: str
    crop_id: str
    geography: str = "Maharashtra"
    decision: str  # SOW_NOW, SOW_PART_NOW, WAIT
    trigger_condition: Optional[str] = None
    action: Optional[str] = None
    action_type: Optional[str] = None
    advisory_text: str
    rationale: Optional[str] = None
    reason: Optional[str] = None
    source_institution: Optional[str] = None
    source_title: Optional[str] = None
    source_document_identifier: Optional[str] = None
    source_version: Optional[str] = None
    publication_date: Optional[str] = None
    source_url_or_reference: Optional[str] = None
    page_or_section: Optional[str] = None
    source_name: Optional[str] = None  # backward compat
    source_reference: Optional[str] = None  # backward compat
    source_date: Optional[str] = None  # backward compat
    validation_status: ValidationStatus = ValidationStatus.UNVALIDATED
    validation_notes: Optional[str] = None
    reviewed_at: Optional[str] = None
    source_supported_conditions: List[str] = Field(default_factory=list)
    meghvani_decision_conditions: List[str] = Field(default_factory=list)
    source_vs_model_boundary: Optional[str] = None
    language: str = "en"
    priority: Priority = Priority.NORMAL

    def model_post_init(self, __context: Any) -> None:
        # Synchronize alias fields
        if not self.action_type and self.action:
            self.action_type = self.action
        if not self.action and self.action_type:
            self.action = self.action_type
        if not self.reason and self.rationale:
            self.reason = self.rationale
        if not self.rationale and self.reason:
            self.rationale = self.reason
        if not self.source_name and self.source_institution:
            self.source_name = self.source_institution
        if not self.source_institution and self.source_name:
            self.source_institution = self.source_name
        if not self.source_reference and self.source_url_or_reference:
            self.source_reference = self.source_url_or_reference
        if not self.source_url_or_reference and self.source_reference:
            self.source_url_or_reference = self.source_reference
        if not self.source_date and self.publication_date:
            self.source_date = self.publication_date


class AdvisoryResult(BaseModel):
    block_id: Optional[str] = None
    crop_id: Optional[str] = None
    geography: Optional[str] = "Maharashtra"
    decision: Optional[str] = None
    probability: Optional[float] = None
    probability_status: str = "RAW_PROTOTYPE"
    decision_status: str = "PROTOTYPE_ONLY"
    advisory_status: AdvisoryStatus = AdvisoryStatus.NO_VALIDATED_RULE
    action_type: Optional[str] = None
    advisory_text: Optional[str] = None
    reason: Optional[str] = None
    rule_id: Optional[str] = None
    source: Optional[RuleSource] = None
    source_supported_conditions: List[str] = Field(default_factory=list)
    meghvani_decision_conditions: List[str] = Field(default_factory=list)
    source_vs_model_boundary: Optional[str] = None
    validation_status: ValidationStatus = ValidationStatus.UNAVAILABLE
    language: str = "en"
    is_operational: bool = False
    scientific_warning: str = (
        "The decision is a prototype output and no validated crop-specific agronomic rule is currently configured."
    )
