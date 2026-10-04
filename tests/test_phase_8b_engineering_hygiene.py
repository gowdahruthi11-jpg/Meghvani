"""
Meghvani Phase 8B: Engineering Hygiene & Governance Tests.
Verifies:
1. Dockerfile & docker-compose configurations (Python 3.12 pinned).
2. GitHub Actions CI pipeline configuration.
3. Alembic migration chain and AlertLog provenance schema.
4. Officer administrative authentication (X-API-Key).
"""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect

from app.main import app
from app.config import settings, PROJECT_ROOT
from app.database.database import engine
from app.models.alert_log import AlertLog

client = TestClient(app)


def test_python_312_pinned():
    """Verify Python 3.12 is pinned in Dockerfile and .python-version."""
    backend_dockerfile = PROJECT_ROOT / "backend" / "Dockerfile"
    root_dockerfile = PROJECT_ROOT / "Dockerfile"
    python_version_file = PROJECT_ROOT / ".python-version"

    assert backend_dockerfile.exists()
    assert "3.12" in backend_dockerfile.read_text(encoding="utf-8")

    assert root_dockerfile.exists()
    assert "3.12" in root_dockerfile.read_text(encoding="utf-8")

    assert python_version_file.exists()
    assert "3.12" in python_version_file.read_text(encoding="utf-8")


def test_docker_compose_and_ci_workflow():
    """Verify docker-compose.yml and .github/workflows/ci.yml exist and specify required services/steps."""
    dc_file = PROJECT_ROOT / "docker-compose.yml"
    assert dc_file.exists()
    dc_text = dc_file.read_text(encoding="utf-8")
    assert "backend:" in dc_text
    assert "frontend:" in dc_text

    ci_file = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    assert ci_file.exists()
    ci_text = ci_file.read_text(encoding="utf-8")
    assert "pytest" in ci_text
    assert "npm run build" in ci_text
    assert "3.12" in ci_text


def test_alert_log_provenance_schema():
    """Verify AlertLog model and DB schema contain model_version, rule_id, rule_version, threshold_config_hash."""
    insp = inspect(engine)
    columns = {c["name"] for c in insp.get_columns("alert_logs")}

    assert "model_version" in columns
    assert "rule_id" in columns
    assert "rule_version" in columns
    assert "threshold_config_hash" in columns

    # Verify attributes on SQLAlchemy ORM model class
    assert hasattr(AlertLog, "model_version")
    assert hasattr(AlertLog, "rule_id")
    assert hasattr(AlertLog, "rule_version")
    assert hasattr(AlertLog, "threshold_config_hash")


def test_officer_api_key_authentication():
    """
    Test X-API-Key security on officer endpoints (/api/alerts/dispatch, /api/demo/run).
    """
    valid_key = settings.officer_api_key

    # 1. Dispatch with invalid key must return 401
    bad_res = client.post(
        "/api/alerts/dispatch",
        json={"farmer_id": 1, "crop_id": "cotton"},
        headers={"X-API-Key": "invalid-officer-token"}
    )
    assert bad_res.status_code == 401

    # 2. Dispatch with valid key must succeed with simulated provider output (Invariant 4)
    good_res = client.post(
        "/api/alerts/dispatch",
        json={"farmer_id": 1, "crop_id": "cotton"},
        headers={"X-API-Key": valid_key}
    )
    assert good_res.status_code == 200
    data = good_res.json()
    assert data["external_dispatch"] is False
    assert data["is_operational"] is False
    assert "status" in data

    # 3. Demo run with invalid key must return 401
    demo_bad = client.post(
        "/api/demo/run",
        json={"probability": 0.20},
        headers={"X-API-Key": "wrong-key"}
    )
    assert demo_bad.status_code == 401

    # 4. Strict mode test: require_officer_auth = True rejects missing key
    original_require = settings.require_officer_auth
    try:
        settings.require_officer_auth = True
        missing_res = client.post(
            "/api/alerts/dispatch",
            json={"farmer_id": 1, "crop_id": "cotton"}
        )
        assert missing_res.status_code == 401

        valid_strict_res = client.post(
            "/api/alerts/dispatch",
            json={"farmer_id": 1, "crop_id": "cotton"},
            headers={"X-API-Key": valid_key}
        )
        assert valid_strict_res.status_code == 200
    finally:
        settings.require_officer_auth = original_require
