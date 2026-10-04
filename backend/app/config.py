import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directories
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
CONFIG_DIR = PROJECT_ROOT / "config"


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
    ]

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
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
