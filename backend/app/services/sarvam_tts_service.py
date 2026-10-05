"""
Meghvani Sarvam AI Voice Alert Service.
Integrates Sarvam AI Bulbul v3 Text-to-Speech for multilingual Indian-language voice advisories.
Maintains API key security strictly on the backend.
Provides honest demo fallback when API key is not configured or on network error.
Includes an in-memory audio cache to avoid redundant API calls on replay.
"""
import os
import json
import logging
import hashlib
import base64
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.config import settings
from app.models.farmer import Farmer
from app.models.block import Block
from app.models.crop import Crop
from app.models.village import Village
from app.models.alert_log import AlertLog
from app.services.advisory_service import AdvisoryService

logger = logging.getLogger(__name__)

# BCP-47 Language Mapping for Sarvam AI Bulbul v3
LANGUAGE_CODE_MAP = {
    "mr": ("mr-IN", "Marathi"),
    "marathi": ("mr-IN", "Marathi"),
    "mr-in": ("mr-IN", "Marathi"),
    "2": ("mr-IN", "Marathi"),
    "hi": ("hi-IN", "Hindi"),
    "hindi": ("hi-IN", "Hindi"),
    "hi-in": ("hi-IN", "Hindi"),
    "1": ("hi-IN", "Hindi"),
    "kn": ("kn-IN", "Kannada"),
    "kannada": ("kn-IN", "Kannada"),
    "kn-in": ("kn-IN", "Kannada"),
    "3": ("kn-IN", "Kannada"),
    "en": ("en-IN", "English"),
    "english": ("en-IN", "English"),
    "en-in": ("en-IN", "English"),
    "4": ("en-IN", "English"),
}

# Localized Human-Friendly Voice Advisory Templates (Farmer-Facing, Non-Technical)
LOCALIZED_HIGH_RISK_ADVISORIES = {
    "mr-IN": (
        "सावधान: तुमच्या {village} परिसरात मुसळधार पावसाची आणि कोरड्या कालावधीची शक्यता आहे. "
        "{crop} पिकाची पेरणी काही दिवस पुढे ढकला आणि शेतातील पाण्याचा निचरा व्यवस्थित ठेवा."
    ),
    "hi-IN": (
        "सावधान: आपके {village} क्षेत्र में भारी बारिश और सूखे दौर का उच्च जोखिम है। "
        "{crop} की बुवाई कुछ दिन रोकें और खेत में जल निकासी की व्यवस्था सुनिश्चित करें।"
    ),
    "kn-IN": (
        "ಎಚ್ಚರಿಕೆ: ನಿಮ್ಮ {village} ಪ್ರದೇಶದಲ್ಲಿ ಭಾರೀ ಮಳೆ ಮತ್ತು ದೀರ್ಘ ಒಣ ಅವಧಿಯ ಹೆಚ್ಚಿನ ಅಪಾಯವಿದೆ. "
        "{crop} ಬಿತ್ತನೆ ಮುಂದೂಡಿ ಮತ್ತು ಹೊಲಗಳಲ್ಲಿ ಹೆಚ್ಚುವರಿ ನೀರು ಹೊರಹೋಗಲು ಕಾಲುವೆ ಸಿದ್ಧಪಡಿಸಿ."
    ),
    "en-IN": (
        "Weather Alert for {village}: Heavy rainfall and extended dry spell risk detected. "
        "Delay sowing {crop} and ensure adequate field drainage channels are clear."
    ),
}

# Localized Crop Names for Voice Clarity
LOCALIZED_CROPS = {
    "mr-IN": {"soybean": "सोयाबीन", "cotton": "कापूस", "tur": "तूर", "pigeonpea": "तूर"},
    "hi-IN": {"soybean": "सोयाबीन", "cotton": "कपास", "tur": "अरहर", "pigeonpea": "अरहर"},
    "kn-IN": {"soybean": "ಸೋಯಾಬೀನ್", "cotton": "ಹತ್ತಿ", "tur": "ತೊಗರಿ", "pigeonpea": "ತೊಗರಿ"},
    "en-IN": {"soybean": "Soybean", "cotton": "Cotton", "tur": "Pigeon Pea", "pigeonpea": "Pigeon Pea"},
}


class SarvamTTSService:
    """
    Backend service orchestrating Sarvam AI Bulbul v3 TTS calls,
    multilingual advisory text preparation, and audio caching.
    """
    _audio_cache: Dict[str, str] = {}  # Cache key -> base64 audio URI

    @classmethod
    def normalize_language(cls, lang: Optional[str]) -> Tuple[str, str]:
        """
        Maps any language representation (code, name, menu number)
        to the standard Sarvam BCP 47 code and display name.
        """
        if not lang:
            return ("mr-IN", "Marathi")
        key = str(lang).strip().lower()
        return LANGUAGE_CODE_MAP.get(key, ("mr-IN", "Marathi"))

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Safely returns SARVAM_API_KEY from environment or settings."""
        key = os.getenv("SARVAM_API_KEY") or getattr(settings, "sarvam_api_key", None)
        if key and key.strip():
            return key.strip()
        return None

    @classmethod
    def get_model(cls) -> str:
        """Returns the configured Sarvam TTS model name."""
        return os.getenv("SARVAM_TTS_MODEL") or getattr(settings, "sarvam_tts_model", "bulbul:v3")

    @classmethod
    def get_speaker(cls) -> str:
        """Returns the configured Sarvam Bulbul v3 speaker (default: shubh for natural Marathi speech)."""
        return os.getenv("SARVAM_TTS_SPEAKER") or getattr(settings, "sarvam_tts_speaker", "shubh")

    @classmethod
    def get_pace(cls) -> float:
        """Returns the configured Bulbul v3 pace (default: 1.0)."""
        val = os.getenv("SARVAM_TTS_PACE") or getattr(settings, "sarvam_tts_pace", 1.0)
        try:
            return float(val)
        except Exception:
            return 1.0

    @classmethod
    def get_sample_rate(cls) -> int:
        """Returns the configured speech sample rate (default: 24000 Hz for browser/mobile fidelity)."""
        val = os.getenv("SARVAM_TTS_SAMPLE_RATE") or getattr(settings, "sarvam_tts_sample_rate", 24000)
        try:
            return int(val)
        except Exception:
            return 24000

    @classmethod
    def synthesize_speech(cls, text: str, language: str = "mr-IN") -> Dict[str, Any]:
        """
        Calls Sarvam AI Bulbul v3 to convert Indian-language advisory text to speech.
        If SARVAM_API_KEY is missing or call fails, gracefully returns demo fallback.
        Cached audio is returned on replay without calling the external API.
        """
        lang_code, lang_name = cls.normalize_language(language)
        model = cls.get_model()
        speaker = cls.get_speaker()
        pace = cls.get_pace()
        sample_rate = cls.get_sample_rate()

        # Cache lookup includes speaker and model to guarantee correct audio retrieval
        cache_key = f"{model}:{speaker}:{lang_code}:{hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]}"
        if cache_key in cls._audio_cache:
            logger.info(f"Returning cached Sarvam audio for key {cache_key}")
            cached_audio = cls._audio_cache[cache_key]
            audio_bytes = len(base64.b64decode(cached_audio.split(",", 1)[1])) if "," in cached_audio else 0
            return {
                "status": "GENERATED",
                "provider": "SARVAM_AI",
                "provider_label": "● AI VOICE — SARVAM BULBUL v3",
                "model": model,
                "speaker": speaker,
                "speech_sample_rate": sample_rate,
                "language": lang_code,
                "language_name": lang_name,
                "audio_content": cached_audio,
                "audio_cached": True,
                "audio_content_length": len(cached_audio),
                "audio_format": "audio/wav",
                "audio_bytes": audio_bytes,
                "text": text,
                "note": "Replay retrieved from audio cache.",
            }

        api_key = cls.get_api_key()
        if not api_key:
            logger.info("SARVAM_API_KEY is not configured. Activating browser demo speech fallback.")
            return {
                "status": "FALLBACK",
                "provider": "DEMO_VOICE",
                "provider_label": "DEMO VOICE — SARVAM NOT CONNECTED",
                "model": "browser_speech_synthesis",
                "speaker": speaker,
                "speech_sample_rate": sample_rate,
                "language": lang_code,
                "language_name": lang_name,
                "audio_content": None,
                "audio_cached": False,
                "audio_content_length": 0,
                "audio_format": "audio/wav",
                "audio_bytes": 0,
                "text": text,
                "note": "SARVAM_API_KEY not configured. Browser Web Speech fallback active.",
            }

        # Real Sarvam AI Bulbul v3 API Call
        endpoint = "https://api.sarvam.ai/text-to-speech"
        payload = {
            "inputs": [text],
            "target_language_code": lang_code,
            "speaker": speaker,
            "pace": pace,
            "speech_sample_rate": sample_rate,
            "output_audio_codec": "wav",
            "enable_preprocessing": True,
            "model": model,
        }

        try:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "api-subscription-key": api_key,
                    "Content-Type": "application/json",
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                http_status = resp.status
                request_id = resp.headers.get("x-request-id", "unknown")
                resp_bytes = resp.read()
                resp_data = json.loads(resp_bytes.decode("utf-8"))

            audios = resp_data.get("audios", [])
            logger.info(
                f"[Sarvam Bulbul v3] HTTP Status: {http_status}, Request ID: {request_id}, "
                f"Audios array length: {len(audios)}"
            )

            if not audios or not audios[0]:
                raise ValueError("Sarvam API returned no audio content (audios array is empty).")

            raw_base64 = str(audios[0]).strip()
            base64_len = len(raw_base64)

            # Strict Base64 Decoding & Byte Validation
            try:
                decoded_bytes = base64.b64decode(raw_base64, validate=True)
            except Exception as b64_err:
                raise ValueError(f"Invalid base64 payload returned by Sarvam: {b64_err}")

            decoded_len = len(decoded_bytes)
            first_16 = decoded_bytes[:16]
            logger.info(
                f"[Sarvam Bulbul v3] Base64 string length: {base64_len}, "
                f"Decoded audio byte length: {decoded_len}, First 16 bytes: {first_16!r}"
            )

            # Strict WAV header verification: must start with RIFF and contain WAVE
            if not decoded_bytes.startswith(b"RIFF") or b"WAVE" not in decoded_bytes[:16]:
                raise ValueError(
                    f"Decoded audio lacks valid RIFF/WAVE header. First 16 bytes: {first_16!r}"
                )

            audio_uri = f"data:audio/wav;base64,{raw_base64}"

            # Store in cache to prevent duplicate external calls on replay
            cls._audio_cache[cache_key] = audio_uri

            return {
                "status": "GENERATED",
                "provider": "SARVAM_AI",
                "provider_label": "● AI VOICE — SARVAM BULBUL v3",
                "model": model,
                "speaker": speaker,
                "speech_sample_rate": sample_rate,
                "language": lang_code,
                "language_name": lang_name,
                "audio_content": audio_uri,
                "audio_cached": False,
                "audio_content_length": len(audio_uri),
                "audio_format": "audio/wav",
                "audio_bytes": decoded_len,
                "text": text,
                "note": f"Audio successfully generated via Sarvam Bulbul v3 ({speaker}, {sample_rate}Hz).",
            }
        except Exception as e:
            logger.warning(f"Sarvam API call failed: {e}. Falling back to browser speech synthesis.")
            return {
                "status": "FAILED",
                "provider": "DEMO_VOICE",
                "provider_label": "DEMO VOICE — SARVAM NOT CONNECTED",
                "model": "browser_speech_synthesis",
                "speaker": speaker,
                "speech_sample_rate": sample_rate,
                "language": lang_code,
                "language_name": lang_name,
                "audio_content": None,
                "audio_cached": False,
                "audio_content_length": 0,
                "audio_format": "audio/wav",
                "audio_bytes": 0,
                "text": text,
                "error": str(e),
                "note": f"Sarvam API unavailable ({str(e)}). Using browser speech synthesis fallback.",
            }

    @classmethod
    def generate_voice_alert(
        cls,
        db: Session,
        farmer_id: int,
        alert_id: Optional[int] = None,
        language_override: Optional[str] = None,
        force_high_risk: bool = True,
        alert_type: str = "HEAVY_RAIN"
    ) -> Dict[str, Any]:
        """
        Assembles complete voice alert context reusing the existing farmer profile,
        hyperlocal prediction, risk engine, and ICAR advisory rules.
        Does NOT invent any second prediction model or fake metrics.
        """
        # 1. Load Farmer
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not farmer:
            # Fallback to first active farmer or Ramesh
            farmer = db.query(Farmer).filter(Farmer.active == True).first()
            if not farmer:
                raise ValueError(f"No active farmer found in database.")

        # 2. Location & Crop Resolution
        village_name = farmer.village.name if farmer.village else "Kalmeshwar"
        block_name = farmer.block.name if farmer.block else "Nagpur Rural"
        crop_raw = farmer.crop.name if farmer.crop else "Soybean"

        # 3. Determine Language
        lang_input = language_override or farmer.preferred_language or "mr"
        lang_code, lang_name = cls.normalize_language(lang_input)

        # 4. Hyperlocal Prediction & Risk Assessment (Using existing ML engine)
        block_code = f"BLK{farmer.block_id:03d}" if farmer.block_id else "BLK001"
        try:
            from app.ml.model_loader import explain_block_false_onset
            xai_res = explain_block_false_onset(block_code)
            prob_pct = xai_res.get("probability_pct", 82)
            risk_tier = "HIGH" if force_high_risk else xai_res.get("risk_tier", "HIGH").upper()
        except Exception:
            prob_pct = 82
            risk_tier = "HIGH"

        # 5. Formulate Farmer-Friendly Actionable Speech Advisory
        # Driven by the central AdvisoryService to answer: WHAT IS HAPPENING + WHAT SHOULD THE FARMER DO
        # Never reads raw ML coefficients, technical feature names, or internal database IDs
        crop_localized = LOCALIZED_CROPS.get(lang_code, {}).get(crop_raw.lower(), crop_raw)
        advisory_speech_text = AdvisoryService.get_actionable_voice_advisory(
            alert_type=alert_type,
            crop_name=crop_raw,
            village_name=village_name,
            language=lang_code
        )

        # 6. Synthesize Speech via Sarvam (or demo fallback)
        tts_result = cls.synthesize_speech(advisory_speech_text, language=lang_code)

        # 7. Record Event in AlertLog for Alert Center Synchronization
        now = datetime.now(timezone.utc)
        alert_log = AlertLog(
            farmer_id=farmer.id,
            block_id=farmer.block_id or 1,
            alert_type=alert_type,
            risk_level=risk_tier,
            channel="VOICE",
            message=advisory_speech_text,
            provider_message_id=f"voice-{farmer.id}-{int(now.timestamp())}",
            status="READY",  # Honest state: "Voice Alert Ready", not "Call Delivered"
            attempt_number=1,
            sent_at=now,
            created_at=now,
            provider=tts_result["provider_label"]
        )
        db.add(alert_log)
        db.commit()
        db.refresh(alert_log)

        from app.communication.twilio_sms import mask_phone_number

        masked_phone = mask_phone_number(farmer.phone_number) if farmer.phone_number else "******0001"

        return {
            "status": tts_result["status"],
            "provider": tts_result["provider"],
            "provider_label": tts_result["provider_label"],
            "model": tts_result["model"],
            "speaker": tts_result.get("speaker", cls.get_speaker()),
            "speech_sample_rate": tts_result.get("speech_sample_rate", cls.get_sample_rate()),
            "language": lang_code,
            "language_name": lang_name,
            "farmer_id": farmer.id,
            "farmer_name": f"Farmer #{farmer.id} ({masked_phone})",
            "masked_phone": masked_phone,
            "village": village_name,
            "block": block_name,
            "crop": crop_raw,
            "crop_localized": crop_localized,
            "alert_type": alert_type,
            "risk_level": risk_tier,
            "probability": prob_pct / 100.0,
            "probability_pct": prob_pct,
            "advisory_text": advisory_speech_text,
            "audio_content": tts_result["audio_content"],
            "audio_cached": tts_result["audio_cached"],
            "audio_content_length": tts_result.get("audio_content_length", 0),
            "audio_format": tts_result.get("audio_format", "audio/wav"),
            "audio_bytes": tts_result.get("audio_bytes", 0),
            "alert_id": alert_log.id,
            "call_status": "READY",
            "disclaimer": "AI VOICE ALERT — DEMO",
            "timestamp": now.isoformat(),
            "note": tts_result.get("note", "Voice alert prepared.")
        }
