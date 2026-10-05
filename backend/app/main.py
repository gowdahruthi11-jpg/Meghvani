from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.database import engine
from app.database.base import Base
# Import all models so metadata is complete
import app.models # noqa: F401
from app.database.seed import seed_database

# Import routers
from app.api.health import router as health_router
from app.api.blocks import router as blocks_router
from app.api.villages import router as villages_router
from app.api.crops import router as crops_router
from app.api.farmers import router as farmers_router
from app.api.registration import router as registration_router
from app.api.observations import router as observations_router
from app.api.alerts import router as alerts_router
from app.api.weather import router as weather_router
from app.api.historical import router as historical_router
from app.api.prediction import router as prediction_router
from app.api.forecast import router as forecast_router
from app.api.advisory import router as advisory_router
from app.api.demo import router as demo_router
from app.api.validation import (
    router as validation_router,
    calibration_router,
    rolling_origin_router
)
from app.api.communication import router as communication_router

from app.database.migrations import run_migrations

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist and seed demo data
    Base.metadata.create_all(bind=engine)
    run_migrations(engine)
    seed_database()
    yield
    # Shutdown logic if needed

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Hyperlocal Monsoon Onset and Break Prediction System (Block / Village Scale) - Phase 1, Phase 2, Phase 3A & Phase 3B Probabilistic Baseline",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under /api prefix
app.include_router(health_router, prefix="/api")
app.include_router(blocks_router, prefix="/api")
app.include_router(villages_router, prefix="/api")
app.include_router(crops_router, prefix="/api")
app.include_router(farmers_router, prefix="/api")
app.include_router(registration_router, prefix="/api")
app.include_router(observations_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
app.include_router(weather_router, prefix="/api")
app.include_router(historical_router, prefix="/api")
app.include_router(prediction_router, prefix="/api")
app.include_router(forecast_router, prefix="/api")
app.include_router(advisory_router, prefix="/api")
app.include_router(demo_router, prefix="/api")
app.include_router(validation_router, prefix="/api")
app.include_router(calibration_router, prefix="/api")
app.include_router(rolling_origin_router, prefix="/api")
app.include_router(communication_router, prefix="/api")

@app.get("/")
def root():
    return {
        "project": "Meghvani",
        "purpose": "Hyperlocal Monsoon Onset and Break Prediction System",
        "phase": "PHASE 1: PRODUCTION-READY FOUNDATION",
        "documentation": "/docs",
        "health": "/api/health",
        "disclaimer": "All weather data and communications in Phase 1 are DEMO/MOCKED."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
