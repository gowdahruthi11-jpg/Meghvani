import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directories
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
CONFIG_DIR = PROJECT_ROOT / "config"

# Locate and load active .env file
if (BACKEND_DIR / ".env").exists():
    ACTIVE_ENV_FILE = BACKEND_DIR / ".env"
elif (PROJECT_ROOT / ".env").exists():
    ACTIVE_ENV_FILE = PROJECT_ROOT / ".env"
else:
    ACTIVE_ENV_FILE = BACKEND_DIR / ".env"

load_dotenv(dotenv_path=ACTIVE_ENV_FILE, override=False)


class Settings(BaseSettings):
    app_name: str = "Meghvani"
    version: str = "1.0.0-phase1"
    environment: str = "development"
    debug: bool = True
    database_url: str = f"sqlite:///{BACKEND_DIR / 'meghvani.db'}"
    api_prefix: str = "/api"
    secret_key: str = "meghvani-prototype-secret-salt-2026"
    officer_api_key: str = "meghvani-officer-dev-key-2026"
    require_officer_auth: bool = False
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://meghvani.vercel.app",
        "https://*.vercel.app",
    ]

    # SMS Provider & Twilio configuration
    sms_provider: str = "MOCK"
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    sms_webhook_validation: bool = True
    twilio_trial_mode: bool = False
    twilio_trial_template_name: str = "sms_2fa"

    # Sarvam AI Voice configuration (Bulbul v3 Text-to-Speech)
    sarvam_api_key: Optional[str] = None
    sarvam_tts_model: str = "bulbul:v3"
    sarvam_tts_speaker: str = "shubh"
    sarvam_tts_pace: float = 1.0
    sarvam_tts_sample_rate: int = 24000
    sarvam_output_audio_codec: str = "wav"

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_DIR / ".env"), str(PROJECT_ROOT / ".env")),
        env_file_encoding="utf-8",
        extra="ignore"
    )


def load_yaml(file_name: str) -> Dict[str, Any]:
    file_path = CONFIG_DIR / file_name
    if not file_path.exists():
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


settings = Settings()

# Loaded configurations from YAML
app_config = load_yaml("app.yaml")
event_definitions_config = load_yaml("event_definitions.yaml")
event_thresholds_config = event_definitions_config or load_yaml("event_thresholds.yaml")
blocks_config = load_yaml("blocks.yaml")
crops_config = load_yaml("crops.yaml")
communication_config = load_yaml("communication.yaml")
advisory_rules_config = load_yaml("advisory_rules.yaml")
decision_costs_config = load_yaml("decision_costs.yaml")
