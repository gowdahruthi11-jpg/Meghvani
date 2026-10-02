from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.database import get_db
from app.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Returns system status, active database connectivity, and environment flags.
    """
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "app": settings.app_name,
        "version": settings.version,
        "environment": settings.environment,
        "database": db_status,
        "ml_forecast_engine": "NOT_CONNECTED (Phase 1 Foundation Prototype)",
        "communication_providers": "MOCK_MODE",
        "weather_data": "DEMO_DATA"
    }
