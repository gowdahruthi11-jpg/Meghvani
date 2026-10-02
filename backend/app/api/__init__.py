from app.api.health import router as health_router
from app.api.blocks import router as blocks_router
from app.api.villages import router as villages_router
from app.api.crops import router as crops_router
from app.api.farmers import router as farmers_router
from app.api.registration import router as registration_router
from app.api.observations import router as observations_router
from app.api.alerts import router as alerts_router
from app.api.weather import router as weather_router

__all__ = [
    "health_router",
    "blocks_router",
    "villages_router",
    "crops_router",
    "farmers_router",
    "registration_router",
    "observations_router",
    "alerts_router",
    "weather_router",
]
