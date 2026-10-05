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

    @classmethod
    def get_actionable_voice_advisory(
        cls,
        alert_type: str,
        crop_name: str = "Soybean",
        village_name: str = "Kalmeshwar",
        language: str = "mr-IN"
    ) -> str:
        """
        Produces an actionable, farmer-facing spoken advisory answering:
        1. WHAT IS HAPPENING?
        2. WHAT SHOULD THE FARMER DO?
        Never reads technical coefficients or internal database metrics.
        """
        lang_key = language.strip().lower()
        if "mr" in lang_key or "marathi" in lang_key or lang_key == "2":
            lang = "mr-IN"
        elif "hi" in lang_key or "hindi" in lang_key or lang_key == "1":
            lang = "hi-IN"
        elif "kn" in lang_key or "kannada" in lang_key or lang_key == "3":
            lang = "kn-IN"
        else:
            lang = "en-IN"

        # Localized crop names for speech clarity
        crops_map = {
            "mr-IN": {"soybean": "सोयाबीन", "cotton": "कापूस", "tur": "तूर", "pigeonpea": "तूर", "gram": "हरभरा"},
            "hi-IN": {"soybean": "सोयाबीन", "cotton": "कपास", "tur": "अरहर", "pigeonpea": "अरहर", "gram": "चना"},
            "kn-IN": {"soybean": "ಸೋಯಾಬೀನ್", "cotton": "ಹತ್ತಿ", "tur": "ತೊಗರಿ", "pigeonpea": "ತೊಗರಿ", "gram": "ಕಡಲೆ"},
            "en-IN": {"soybean": "Soybean", "cotton": "Cotton", "tur": "Pigeon Pea", "pigeonpea": "Pigeon Pea", "gram": "Chickpea"},
        }
        localized_crop = crops_map.get(lang, {}).get(crop_name.lower(), crop_name)

        # Actionable farmer-facing voice templates answering: What is happening + What to do
        event_key = alert_type.strip().upper()
        if "FALSE" in event_key:
            signal = "FALSE_ONSET"
        elif "HEAVY" in event_key or "RAIN" in event_key:
            signal = "HEAVY_RAIN"
        elif "BREAK" in event_key or "DRY" in event_key:
            signal = "BREAK"
        elif "REVIV" in event_key:
            signal = "REVIVAL"
        elif "ONSET" in event_key:
            signal = "ONSET"
        else:
            signal = "HEAVY_RAIN"

        actionable_templates = {
            "HEAVY_RAIN": {
                "mr-IN": "नमस्कार. मेघवाणी कडून हवामानाचा इशारा आहे. तुमच्या {village} भागात मुसळधार पावसाची शक्यता आहे. आज पेरणी करू नका. पावसाची परिस्थिती स्थिर होईपर्यंत थांबा आणि {crop} शेतातून पाण्याचा निचरा करा.",
                "hi-IN": "नमस्कार. मेघवाणी मौसम चेतावनी है। आपके {village} क्षेत्र में भारी बारिश की संभावना है। आज बुवाई न करें। बारिश की स्थिति सामान्य होने तक इंतज़ार करें और {crop} खेत में जल निकासी सुनिश्चित करें।",
                "kn-IN": "ನಮಸ್ಕಾರ. ಮೇಘವಾಣಿ ಕಡೆಯಿಂದ ಹವಾಮಾನ ಎಚ್ಚರಿಕೆ. ನಿಮ್ಮ {village} ಪ್ರದೇಶದಲ್ಲಿ ಭಾರೀ ಮಳೆಯಾಗುವ ಸಾಧ್ಯತೆಯಿದೆ. ಇಂದು ಬಿತ್ತನೆ ಮಾಡಬೇಡಿ. ಮಳೆ ಪರಿಸ್ಥಿತಿ ಸ್ಥಿರವಾಗುವವರೆಗೆ ಕಾಯಿರಿ ಮತ್ತು {crop} ಹೊಲದಿಂದ ನೀರು ಹೊರಹಾಕಿ.",
                "en-IN": "Greetings from Meghvani weather alert. Heavy rainfall is expected in your {village} area. Do not sow seeds today. Wait until rainfall conditions stabilize and clear field drainage for {crop}."
            },
            "FALSE_ONSET": {
                "mr-IN": "नमस्कार. मेघवाणी कडून हवामानाचा इशारा आहे. तुमच्या {village} भागात सुरुवातीचा पाऊस पडला असला तरी मान्सून अद्याप स्थिर झालेला नाही. आज पेरणी करू नका. नियमित पाऊस होईपर्यंत थांबा.",
                "hi-IN": "नमस्कार. मेघवाणी मौसम चेतावनी है। आपके {village} क्षेत्र में बारिश शुरू हुई है, लेकिन मानसून अभी स्थिर नहीं है। आज बुवाई न करें। लगातार बारिश होने का इंतज़ार करें।",
                "kn-IN": "ನಮಸ್ಕಾರ. ಮೇಘವಾಣಿ ಕಡೆಯಿಂದ ಹವಾಮಾನ ಎಚ್ಚರಿಕೆ. ನಿಮ್ಮ {village} ಪ್ರದೇಶದಲ್ಲಿ ಆರಂಭಿಕ ಮಳೆಯಾಗಿದ್ದರೂ ಮುಂಗಾರು ಇನ್ನೂ ಸ್ಥಿರವಾಗಿಲ್ಲ. ಇಂದು ಬಿತ್ತನೆ ಮಾಡಬೇಡಿ. ಸ್ಥಿರ ಮಳೆಗಾಗಿ ಕಾಯಿರಿ.",
                "en-IN": "Greetings from Meghvani weather alert. Rainfall has started in {village}, but the monsoon may not be stable yet. Do not sow seeds now. Wait for more consistent rainfall before sowing {crop}."
            },
            "BREAK": {
                "mr-IN": "नमस्कार. मेघवाणी कडून हवामानाचा इशारा आहे. तुमच्या {village} भागात पुढील दिवसांत पावसाचा मोठा खंड पडण्याची शक्यता आहे. पेरणी झाली नसेल तर पुढील चांगल्या पावसापर्यंत {crop} ची पेरणी पुढे ढकला.",
                "hi-IN": "नमस्कार. मेघवाणी मौसम सलाह है। आपके {village} क्षेत्र में सूखे दौर की संभावना है। यदि बुवाई नहीं हुई है, तो उपयुक्त बारिश तक {crop} की बुवाई रोकें।",
                "kn-IN": "ನಮಸ್ಕಾರ. ಮೇಘವಾಣಿ ಕಡೆಯಿಂದ ಹವಾಮಾನ ಸಲಹೆ. ನಿಮ್ಮ {village} ಪ್ರದೇಶದಲ್ಲಿ ದೀರ್ಘ ಮಳೆ ವಿರಾಮದ ಸಾಧ್ಯತೆಯಿದೆ. ಬಿತ್ತನೆ ಆಗಿಲ್ಲದಿದ್ದರೆ ಮುಂದಿನ ಮಳೆಯವರೆಗೆ {crop} ಬಿತ್ತನೆ ಮುಂದೂಡಿ.",
                "en-IN": "Greetings from Meghvani weather alert. A prolonged dry spell is expected in your {village} area. If you have not completed sowing, wait for suitable rainfall before sowing {crop}."
            },
            "REVIVAL": {
                "mr-IN": "नमस्कार. मेघवाणी कडून हवामानाचा संदेश आहे. तुमच्या {village} भागात कोरडा कालावधी संपून पाऊस पुन्हा सक्रिय होत आहे. शेतातील ओलावा तपासून {crop} पेरणीची तयारी करा.",
                "hi-IN": "नमस्कार. मेघवाणी मौसम सलाह है। आपके {village} क्षेत्र में सूखे के बाद बारिश की स्थिति सुधर रही है। खेत में नमी जांचकर {crop} की बुवाई की तैयारी करें।",
                "kn-IN": "ನಮಸ್ಕಾರ. ಮೇಘವಾಣಿ ಕಡೆಯಿಂದ ಮಾಹಿತಿ. ನಿಮ್ಮ {village} ಪ್ರದೇಶದಲ್ಲಿ ಒಣ ಅವಧಿ ಮುಗಿದು ಮಳೆ ಸುಧಾರಿಸುತ್ತಿದೆ. ಮಣ್ಣಿನ ತೇವಾಂಶ ಪರಿಶೀಲಿಸಿ {crop} ಬಿತ್ತನೆಗೆ ಸಿದ್ಧರಾಗಿ.",
                "en-IN": "Greetings from Meghvani weather alert. Rainfall conditions are improving in {village} after the dry spell. Monitor soil moisture and local rainfall before continuing sowing {crop}."
            },
            "ONSET": {
                "mr-IN": "नमस्कार. मेघवाणी कडून हवामानाचा संदेश आहे. तुमच्या {village} भागात मान्सूनचे आगमन अनुकूल ठरत आहे. जमिनीत पुरेसा ओलावा निर्माण झाल्यावर {crop} ची पेरणी सुरू करू शकता.",
                "hi-IN": "नमस्कार. मेघवाणी मौसम सूचना है। आपके {village} क्षेत्र में मानसून की शुरुआत अनुकूल हो रही है। मिट्टी में पर्याप्त नमी होने पर {crop} की बुवाई शुरू कर सकते हैं।",
                "kn-IN": "ನಮಸ್ಕಾರ. ಮೇಘವಾಣಿ ಕಡೆಯಿಂದ ಮಾಹಿತಿ. ನಿಮ್ಮ {village} ಪ್ರದೇಶದಲ್ಲಿ ಮುಂಗಾರು ಪರಿಸ್ಥಿತಿಗಳು ಆಶಾದಾಯಕವಾಗಿವೆ. ಮಣ್ಣಿನಲ್ಲಿ ಸಾಕಷ್ಟು ತೇವಾಂಶವಿದ್ದಾಗ {crop} ಬಿತ್ತನೆ ಆರಂಭಿಸಬಹುದು.",
                "en-IN": "Greetings from Meghvani weather alert. Monsoon onset conditions are becoming favorable in {village}. Rainfall conditions are improving. Farmers may consider sowing {crop} when local soil moisture is adequate."
            }
        }

        selected_dict = actionable_templates.get(signal, actionable_templates["HEAVY_RAIN"])
        template = selected_dict.get(lang, selected_dict["en-IN"])
        return template.format(village=village_name, crop=localized_crop)

