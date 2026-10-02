from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, Float, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class WeatherObservation(Base):
    """
    Block-scale daily weather observation entity.
    All rows in Phase 1 carry source='DEMO_DATA' or similar clear attribution.
    """
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False, index=True)
    observation_date = Column(Date, nullable=False, index=True)
    rainfall_mm = Column(Float, nullable=False, default=0.0)
    temperature_c = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True) # Percentage
    wind_speed = Column(Float, nullable=True) # km/h
    soil_moisture = Column(Float, nullable=True) # Percentage / volumetric fraction
    source = Column(String(100), nullable=False, default="DEMO_DATA") # DEMO_DATA, IMD_API, SATELLITE_ERA5
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    block = relationship("Block", back_populates="weather_observations")
