from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base

class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    boundary_reference = Column(String(255), nullable=True) # GeoJSON or shapefile reference
    active = Column(Boolean, default=True, nullable=False)

    villages = relationship("Village", back_populates="block")
    farmers = relationship("Farmer", back_populates="block")
    weather_observations = relationship("WeatherObservation", back_populates="block")
    farmer_observations = relationship("FarmerObservation", back_populates="block")
    alert_logs = relationship("AlertLog", back_populates="block")
