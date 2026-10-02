from typing import Dict, Any, Optional
from app.config import advisory_rules_config
from app.schemas.weather import ForecastOutput

class AdvisoryDecision:
    def __init__(
        self,
        decision: str,
        rule_id: str,
        message: str,
        language: str = "English",
        disclaimer: str = "DEMO ADVISORY RULE - MUST BE VALIDATED WITH ICAR/KVK"
    ):
        self.decision = decision
        self.rule_id = rule_id
        self.message = message
        self.language = language
        self.disclaimer = disclaimer

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "rule_id": self.rule_id,
            "message": self.message,
            "language": self.language,
            "disclaimer": self.disclaimer
        }


class AdvisoryService:
    """
    Deterministic rule-engine evaluating crop advisories based on meteorological signals.
    Rule sets are loaded from config/advisory_rules.yaml without hardcoded code logic.
    """
    @classmethod
    def evaluate_forecast(
        cls,
        forecast: ForecastOutput,
        crop_name: str = "Soybean",
        language: str = "English"
    ) -> AdvisoryDecision:
        rules = advisory_rules_config.get("demo_rules", [])

        # Evaluate rules in priority order
        for rule in rules:
            rule_id = rule.get("rule_id", "UNKNOWN_RULE")
            trigger_signal = rule.get("trigger_signal")
            min_prob = rule.get("min_probability", 0.0)
            max_break = rule.get("max_break_risk")
            decision = rule.get("decision", "CHECK_LOCAL_ADVICE")
            templates = rule.get("action_templates", {})

            matched = False

            if trigger_signal == "ONSET" and forecast.prob_onset is not None:
                if forecast.prob_onset >= min_prob:
                    if max_break is None or (forecast.prob_break is not None and forecast.prob_break <= max_break):
                        matched = True

            elif trigger_signal == "FALSE_ONSET" and forecast.prob_false_onset is not None:
                if forecast.prob_false_onset >= min_prob:
                    matched = True

            elif trigger_signal == "BREAK" and forecast.prob_break is not None:
                if forecast.prob_break >= min_prob:
                    matched = True

            elif trigger_signal == "HEAVY_RAIN" and forecast.prob_heavy_rain is not None:
                if forecast.prob_heavy_rain >= min_prob:
                    matched = True

            if matched:
                template = templates.get(language, templates.get("English", "Advisory for {crop}: Follow local guidance."))
                rendered_msg = template.replace("{crop}", crop_name)
                return AdvisoryDecision(
                    decision=decision,
                    rule_id=rule_id,
                    message=rendered_msg,
                    language=language
                )

        # Default fallback
        fallback_msg = f"Standard seasonal care recommended for {crop_name}. Monitor local weather conditions."
        return AdvisoryDecision(
            decision="CHECK_LOCAL_ADVICE",
            rule_id="DEFAULT_FALLBACK",
            message=fallback_msg,
            language=language
        )
