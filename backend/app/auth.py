"""
Meghvani Officer Authentication Dependency (Phase 8B).
Provides X-API-Key verification for sensitive administrative / officer actions.
"""
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.config import settings

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_officer_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """
    Verifies X-API-Key header for officer administrative endpoints.

    Behavior:
    - If require_officer_auth is True (production / strict mode):
      Missing header -> 401 Unauthorized
      Wrong key -> 401 Unauthorized
      Matching key -> allowed
    - If require_officer_auth is False (dev / default mode):
      Missing header -> allowed (permissive for local development and backwards-compatible tests)
      Provided but incorrect key -> 401 Unauthorized
      Provided and correct key -> allowed
    """
    expected = settings.officer_api_key

    if not settings.require_officer_auth:
        if api_key is None:
            return "permissive_dev_officer"
        if api_key == expected:
            return api_key
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Officer API Key"
        )

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing required X-API-Key header for officer administrative endpoint"
        )
    if api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Officer API Key"
        )
    return api_key
