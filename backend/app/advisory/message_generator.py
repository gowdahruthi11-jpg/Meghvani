"""
Meghvani Phase 5C: Farmer Advisory & Language Layer.

Transforms evaluated prototype decisions and validated agronomic rules into
simple, farmer-friendly, multi-lingual messages prepared for delivery channels
(SMS, WhatsApp, Voice/IVR).

Strict Safety Boundaries:
1. The language layer is NOT an agricultural reasoning engine.
2. NO VALIDATED RULE -> NO FARMING ADVICE.
3. Language translation MUST NOT change agronomic meaning.
4. Institutional source conditions and Meghvani prototype model thresholds are strictly separated.
5. All generated messages are explicitly marked as prototype / non-operational.
6. NO communications (SMS, WhatsApp, Voice) are dispatched.
"""
from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import re
import logging

from app.advisory.models import AdvisoryResult, AdvisoryStatus, ValidationStatus

logger = logging.getLogger(__name__)


class MessageLanguage(str, Enum):
    EN = "en"
    HI = "hi"
    MR = "mr"


class MessageChannel(str, Enum):
    SMS = "sms"
    WHATSAPP = "whatsapp"
    VOICE = "voice"


class MessageType(str, Enum):
    SOW_NOW = "SOW_NOW"
    SOW_PART_NOW = "SOW_PART_NOW"
    WAIT = "WAIT"
    NO_VALIDATED_RULE = "NO_VALIDATED_RULE"
    FORECAST_UNAVAILABLE = "FORECAST_UNAVAILABLE"
    PROTOTYPE_WARNING = "PROTOTYPE_WARNING"


class FarmerAdvisoryMessage(BaseModel):
    block_id: Optional[str] = None
    crop_id: str
    crop_name: str
    decision: Optional[str] = None
    language: str
    channel: str
    advisory_status: str
    message: str
    source_institution: Optional[str] = None
    source_title: Optional[str] = None
    source_supported_conditions: List[str] = Field(default_factory=list)
    source_vs_model_boundary: Optional[str] = None
    is_operational: bool = False
    prototype_warning: str


# ---------------------------------------------------------------------------
# LOCALIZED DICTIONARIES (STRICTLY CONSTRAINED TO APPROVED NOMENCLATURE)
# ---------------------------------------------------------------------------

CROP_LOCALIZED_NAMES: Dict[str, Dict[str, str]] = {
    "soybean": {
        "en": "Soybean",
        "hi": "सोयाबीन",
        "mr": "सोयाबीन"
    },
    "cotton": {
        "en": "Cotton",
        "hi": "कपास",
        "mr": "कापूस"
    },
    "pigeonpea": {
        "en": "Pigeonpea (Tur)",
        "hi": "अरहर (तूर)",
        "mr": "तूर"
    }
}

PROTOTYPE_WARNING_TEXT: Dict[str, str] = {
    "en": "Meghvani prototype advisory — not a substitute for local agricultural expert guidance.",
    "hi": "मेघवाणी प्रोटोटाइप सलाह — स्थानीय कृषि विशेषज्ञ के मार्गदर्शन का विकल्प नहीं है।",
    "mr": "मेघवाणी प्रायोगिक सल्ला — स्थानिक कृषी तज्ज्ञांच्या मार्गदर्शनाचा पर्याय नाही."
}

# Core farmer templates by MessageType and Language
# Under NO circumstances should these templates invent fertilizer, pesticide, or new rainfall metrics.
MESSAGE_TEMPLATES: Dict[MessageType, Dict[str, str]] = {
    MessageType.SOW_NOW: {
        "en": (
            "Meghvani update for {crop}:\n"
            "Current forecast indicates low false-onset risk supporting the SOW NOW posture. "
            "Based on registered agricultural guidance from {source_institution}, "
            "ensure adequate soil moisture and rainfall (75-100 mm) before proceeding with sowing."
        ),
        "hi": (
            "मेघवाणी अपडेट — {crop}:\n"
            "वर्तमान पूर्वानुमान के अनुसार गलत मानसून शुरुआत (False Onset) का जोखिम कम है। "
            "{source_institution} द्वारा पंजीकृत कृषि दिशा-निर्देशों के अनुसार, "
            "बुवाई से पहले पर्याप्त वर्षा (75-100 मिमी) और मिट्टी में उचित नमी सुनिश्चित करें।"
        ),
        "mr": (
            "मेघवाणी अपडेट — {crop}:\n"
            "सध्याच्या अंदाजानुसार पावसाच्या सुरुवातीबाबतचा धोका (False Onset) कमी आहे. "
            "{source_institution} च्या अधिकृत कृषी मार्गदर्शक सूचनांनुसार, "
            "पेरणीपूर्वी पुरेशा पावसाची (७५-१०० मिमी) व योग्य वाफसा स्थितीची खात्री करा."
        )
    },
    MessageType.WAIT: {
        "en": (
            "Meghvani update for {crop}:\n"
            "Current forecast indicates elevated false-onset risk. "
            "Based on registered agricultural guidance from {source_institution}, "
            "delay sowing until adequate rainfall (75-100 mm) and sustained soil moisture are established."
        ),
        "hi": (
            "मेघवाणी अपडेट — {crop}:\n"
            "वर्तमान पूर्वानुमान के अनुसार गलत मानसून शुरुआत का जोखिम अधिक है। "
            "{source_institution} द्वारा पंजीकृत कृषि दिशा-निर्देशों के अनुसार, "
            "बुवाई रोकें और पर्याप्त वर्षा (75-100 मिमी) व मिट्टी में नमी आने तक प्रतीक्षा करें।"
        ),
        "mr": (
            "मेघवाणी अपडेट — {crop}:\n"
            "सध्याच्या अंदाजानुसार पावसाच्या सुरुवातीबाबतचा धोका अधिक आहे. "
            "{source_institution} च्या अधिकृत कृषी मार्गदर्शक सूचनांनुसार, "
            "पेरणी घाईने करू नका आणि पुरेसा पाऊस (७५-१०० मिमी) व जमिनीत ओलावा येईपर्यंत प्रतीक्षा करा."
        )
    },
    MessageType.SOW_PART_NOW: {
        "en": (
            "Meghvani has evaluated a partial-sowing posture for {crop}, "
            "but an approved crop-specific agronomic rule is not currently available for this situation."
        ),
        "hi": (
            "मेघवाणी ने {crop} के लिए आंशिक बुवाई की स्थिति पहचानी है, "
            "लेकिन इस स्थिति के लिए वर्तमान में कोई सत्यापित कृषि नियम उपलब्ध नहीं है।"
        ),
        "mr": (
            "मेघवाणीने {crop} साठी अंशतः पेरणीची स्थिती नोंदवली आहे, "
            "परंतु या स्थितीसाठी सध्या कोणताही प्रमाणित कृषी नियम उपलब्ध नाही."
        )
    },
    MessageType.NO_VALIDATED_RULE: {
        "en": "An approved crop-specific advisory is not currently available for this forecast situation.",
        "hi": "इस पूर्वानुमान स्थिति के लिए कोई सत्यापित फसल-विशिष्ट सलाह वर्तमान में उपलब्ध नहीं है।",
        "mr": "या हवामान अंदाजासाठी कोणतीही प्रमाणित पीकनिहाय कृषी सल्लापत्रिका सध्या उपलब्ध नाही."
    },
    MessageType.FORECAST_UNAVAILABLE: {
        "en": (
            "Meghvani forecast is currently unavailable for this location. "
            "Please use local agricultural guidance until an updated forecast is available."
        ),
        "hi": (
            "इस स्थान के लिए मेघवाणी पूर्वानुमान वर्तमान में उपलब्ध नहीं है। "
            "जब तक नया पूर्वानुमान उपलब्ध न हो, स्थानीय कृषि सलाह का पालन करें।"
        ),
        "mr": (
            "या परिसरासाठी मेघवाणी हवामान अंदाज सध्या उपलब्ध नाही. "
            "नवीन अंदाज उपलब्ध होईपर्यंत स्थानिक कृषी मार्गदर्शनाचा अवलंब करा."
        )
    }
}


# ---------------------------------------------------------------------------
# CHANNEL FORMATTING IMPLEMENTATION
# ---------------------------------------------------------------------------

def format_for_sms(body_text: str, warning_text: str) -> str:
    """
    Format message for SMS delivery:
    Concise, plain text, single string, with non-operational disclaimer footer.
    """
    clean_body = body_text.strip()
    return f"{clean_body}\n[{warning_text}]"


def format_for_whatsapp(body_text: str, warning_text: str, crop_name: str, is_validated: bool) -> str:
    """
    Format message for WhatsApp delivery:
    Readable, structured, clear section separation, with WhatsApp styling.
    """
    clean_body = body_text.strip()
    if is_validated:
        header = f"🌾 *Meghvani Advisory | {crop_name}*"
    else:
        header = f"ℹ️ *Meghvani Advisory Update | {crop_name}*"

    return f"{header}\n\n{clean_body}\n\n⚠️ _{warning_text}_"


def format_for_voice(body_text: str, warning_text: str, crop_name: str, language: str) -> str:
    """
    Format message for Voice / IVR text-to-speech:
    - Natural spoken sentences.
    - Expands numeric abbreviations (e.g. '75-100 mm' -> '75 to 100 millimeters').
    - Expands acronyms for clean speech synthesis (e.g. 'ICAR-CRIDA' -> 'ICAR CRIDA').
    - Removes formatting symbols, brackets, emojis, and slashes.
    - Includes spoken intro and spoken disclaimer.
    """
    text = body_text

    # 1. Normalize linebreaks to pauses
    text = text.replace("\n", ". ")

    # 2. Expand abbreviations by language
    if language == "en":
        text = text.replace("75-100 mm", "75 to 100 millimeters")
        text = text.replace("75–100 mm", "75 to 100 millimeters")
        text = text.replace("ICAR-CRIDA", "ICAR CRIDA")
        text = text.replace("ICAR-CICR", "ICAR CICR")
        text = text.replace("Dr. PDKV", "Doctor PDKV")
        text = text.replace("SOW NOW", "sow now")
        text = text.replace("WAIT", "wait")
        spoken_intro = f"This is an automated Meghvani weather and crop advisory for {crop_name}."
        spoken_outro = "Please note: this is a prototype advisory and does not replace local agricultural expert advice."
    elif language == "hi":
        text = text.replace("75-100 मिमी", "75 से 100 मिलीमीटर")
        text = text.replace("75-100 mm", "75 से 100 मिलीमीटर")
        text = text.replace("ICAR-CRIDA", "आई सी ए आर क्रीडा")
        text = text.replace("ICAR-CICR", "आई सी ए आर सी आई सी आर")
        text = text.replace("Dr. PDKV", "डॉक्टर पंजाबराव देशमुख कृषि विद्यापीठ")
        spoken_intro = f"यह {crop_name} के लिए मेघवाणी कृषि सलाह संदेश है।"
        spoken_outro = "ध्यान दें: यह एक प्रायोगिक सलाह है और स्थानीय कृषि विशेषज्ञ के मार्गदर्शन का विकल्प नहीं है।"
    else:  # Marathi
        text = text.replace("७५-१०० मिमी", "७५ ते १०० मिलीमीटर")
        text = text.replace("75-100 मिमी", "७५ ते १०० मिलीमीटर")
        text = text.replace("75-100 mm", "७५ ते १०० मिलीमीटर")
        text = text.replace("ICAR-CRIDA", "आय सी ए आर क्रीडा")
        text = text.replace("ICAR-CICR", "आय सी ए आर सी आय सी आर")
        text = text.replace("Dr. PDKV", "डॉक्टर पंजाबराव देशमुख कृषी विद्यापीठ")
        spoken_intro = f"हा {crop_name} पिकासाठी मेघवाणी कृषी सल्ला संदेश आहे."
        spoken_outro = "कृपया लक्षात घ्या: हा एक प्रायोगिक सल्ला असून स्थानिक कृषी तज्ज्ञांच्या मार्गदर्शनाचा पर्याय नाही."

    # 3. Clean symbols not suitable for TTS
    text = re.sub(r"[\*\_\[\]\(\)\{\}\#\~]", "", text)
    text = text.replace("—", ", ")
    text = text.replace("-", " ")
    text = text.replace("/", " किंवा " if language == "mr" else (" या " if language == "hi" else " or "))
    text = re.sub(r"\s+", " ", text).strip()

    return f"{spoken_intro} {text} {spoken_outro}".strip()


# ---------------------------------------------------------------------------
# ADVISORY MESSAGE GENERATOR SERVICE
# ---------------------------------------------------------------------------

class AdvisoryMessageGenerator:
    """
    Pure message generation and translation service.
    Accepts evaluated advisory results and creates channel-formatted farmer messages.
    """

    @staticmethod
    def normalize_language(language: Optional[str]) -> str:
        """
        Validates language against MessageLanguage enum or full name.
        Falls back safely to 'en' for any unsupported language.
        """
        if not language:
            return MessageLanguage.EN.value
        norm = language.strip().lower()
        lang_map = {
            "en": MessageLanguage.EN.value,
            "english": MessageLanguage.EN.value,
            "hi": MessageLanguage.HI.value,
            "hindi": MessageLanguage.HI.value,
            "mr": MessageLanguage.MR.value,
            "marathi": MessageLanguage.MR.value
        }
        if norm in lang_map:
            return lang_map[norm]
        logger.warning(f"Unsupported language requested '{language}'. Falling back safely to 'en'.")
        return MessageLanguage.EN.value

    @staticmethod
    def normalize_channel(channel: Optional[str]) -> str:
        """
        Validates channel against MessageChannel enum.
        Falls back safely to 'sms' for any unsupported channel.
        """
        if not channel:
            return MessageChannel.SMS.value
        norm = channel.strip().lower()
        if norm in [MessageChannel.SMS.value, MessageChannel.WHATSAPP.value, MessageChannel.VOICE.value]:
            return norm
        logger.warning(f"Unsupported channel requested '{channel}'. Falling back safely to 'sms'.")
        return MessageChannel.SMS.value

    @classmethod
    def get_crop_name(cls, crop_id: str, language: str) -> str:
        """
        Returns localized crop name for supported crops.
        """
        norm_crop = crop_id.strip().lower()
        crop_dict = CROP_LOCALIZED_NAMES.get(norm_crop)
        if crop_dict:
            return crop_dict.get(language, crop_dict.get("en", norm_crop.capitalize()))
        return norm_crop.capitalize()

    @classmethod
    def generate_message(
        cls,
        advisory_result: Optional[AdvisoryResult] = None,
        block_id: Optional[str] = None,
        crop_id: str = "soybean",
        decision: Optional[str] = None,
        language: str = "en",
        channel: str = "sms",
        forecast_available: bool = True
    ) -> FarmerAdvisoryMessage:
        """
        Main message synthesis method enforcing the validation gate.
        """
        lang = cls.normalize_language(language)
        chan = cls.normalize_channel(channel)
        norm_crop = crop_id.strip().lower()
        crop_name = cls.get_crop_name(norm_crop, lang)
        warning_text = PROTOTYPE_WARNING_TEXT[lang]

        # Case 1: Forecast unavailable
        if not forecast_available:
            body = MESSAGE_TEMPLATES[MessageType.FORECAST_UNAVAILABLE][lang]
            msg = cls._format_channel(body, warning_text, crop_name, chan, lang, False)
            return FarmerAdvisoryMessage(
                block_id=block_id,
                crop_id=norm_crop,
                crop_name=crop_name,
                decision=decision,
                language=lang,
                channel=chan,
                advisory_status="FORECAST_UNAVAILABLE",
                message=msg,
                source_institution=None,
                source_title=None,
                source_supported_conditions=[],
                source_vs_model_boundary=None,
                is_operational=False,
                prototype_warning=warning_text
            )

        # Case 2: SOW_PART_NOW (Always NO_VALIDATED_RULE in Phase 5C)
        effective_decision = decision or (advisory_result.decision if advisory_result else None)
        if effective_decision == "SOW_PART_NOW":
            template = MESSAGE_TEMPLATES[MessageType.SOW_PART_NOW][lang]
            body = template.format(crop=crop_name)
            msg = cls._format_channel(body, warning_text, crop_name, chan, lang, False)
            return FarmerAdvisoryMessage(
                block_id=block_id or (advisory_result.block_id if advisory_result else None),
                crop_id=norm_crop,
                crop_name=crop_name,
                decision=effective_decision,
                language=lang,
                channel=chan,
                advisory_status=AdvisoryStatus.NO_VALIDATED_RULE.value,
                message=msg,
                source_institution=None,
                source_title=None,
                source_supported_conditions=[],
                source_vs_model_boundary=None,
                is_operational=False,
                prototype_warning=warning_text
            )

        # Case 3: Check advisory rule validation gate
        is_validated = (
            advisory_result is not None
            and advisory_result.advisory_status == AdvisoryStatus.RULE_MATCHED
            and advisory_result.validation_status == ValidationStatus.VALIDATED
        )

        if not is_validated:
            # NO VALIDATED RULE -> Safe generic fallback
            body = MESSAGE_TEMPLATES[MessageType.NO_VALIDATED_RULE][lang]
            msg = cls._format_channel(body, warning_text, crop_name, chan, lang, False)
            return FarmerAdvisoryMessage(
                block_id=block_id or (advisory_result.block_id if advisory_result else None),
                crop_id=norm_crop,
                crop_name=crop_name,
                decision=effective_decision,
                language=lang,
                channel=chan,
                advisory_status=AdvisoryStatus.NO_VALIDATED_RULE.value,
                message=msg,
                source_institution=None,
                source_title=None,
                source_supported_conditions=[],
                source_vs_model_boundary=None,
                is_operational=False,
                prototype_warning=warning_text
            )

        # Case 4: Validated Rule Matched (SOW_NOW or WAIT)
        src_inst = (
            advisory_result.source.source_institution
            if advisory_result and advisory_result.source and advisory_result.source.source_institution
            else "registered agricultural institutions"
        )
        src_title = advisory_result.source.source_title if advisory_result and advisory_result.source else None

        if effective_decision == "SOW_NOW":
            template = MESSAGE_TEMPLATES[MessageType.SOW_NOW][lang]
        elif effective_decision == "WAIT":
            template = MESSAGE_TEMPLATES[MessageType.WAIT][lang]
        else:
            # Any unhandled decision posture
            template = MESSAGE_TEMPLATES[MessageType.NO_VALIDATED_RULE][lang]

        body = template.format(crop=crop_name, source_institution=src_inst)
        msg = cls._format_channel(body, warning_text, crop_name, chan, lang, True)

        return FarmerAdvisoryMessage(
            block_id=block_id or advisory_result.block_id,
            crop_id=norm_crop,
            crop_name=crop_name,
            decision=effective_decision,
            language=lang,
            channel=chan,
            advisory_status="VALIDATED_RULE",
            message=msg,
            source_institution=src_inst,
            source_title=src_title,
            source_supported_conditions=advisory_result.source_supported_conditions if hasattr(advisory_result, "source_supported_conditions") else [],
            source_vs_model_boundary=advisory_result.source_vs_model_boundary,
            is_operational=False,
            prototype_warning=warning_text
        )

    @classmethod
    def _format_channel(
        cls,
        body: str,
        warning: str,
        crop_name: str,
        channel: str,
        language: str,
        is_validated: bool
    ) -> str:
        """
        Directs body to the requested channel formatter.
        """
        if channel == MessageChannel.WHATSAPP.value:
            return format_for_whatsapp(body, warning, crop_name, is_validated)
        elif channel == MessageChannel.VOICE.value:
            return format_for_voice(body, warning, crop_name, language)
        else:
            return format_for_sms(body, warning)
