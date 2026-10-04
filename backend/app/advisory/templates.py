"""
Meghvani Phase 5A: Neutral Advisory Templates.

System-status templates used when no validated crop-specific agronomic rule is configured.
These messages reflect system risk interpretation without conveying unsupported agronomic claims.
"""
from typing import Dict

NEUTRAL_DECISION_TEMPLATES: Dict[str, str] = {
    "SOW_NOW": "Prototype decision: SOW_NOW. Crop-specific agronomic guidance is not currently available.",
    "SOW_PART_NOW": "Prototype decision: SOW_PART_NOW. Crop-specific agronomic guidance is not currently available.",
    "WAIT": "Prototype decision: WAIT. Crop-specific agronomic guidance is not currently available.",
    "UNAVAILABLE": "Prototype decision is unavailable. Sowing guidance cannot be evaluated.",
}

NO_RULE_WARNING = (
    "The decision is a prototype output and no validated crop-specific agronomic rule is currently configured."
)


def get_neutral_template(decision: str) -> str:
    """
    Returns the neutral system status template for a given prototype decision.
    """
    return NEUTRAL_DECISION_TEMPLATES.get(
        decision,
        f"Prototype decision: {decision}. Crop-specific agronomic guidance is not currently available."
    )
