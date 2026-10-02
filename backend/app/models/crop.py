from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base

class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    scientific_name = Column(String(150), nullable=True)
    season = Column(String(50), nullable=False, default="Kharif")
    water_requirement = Column(String(50), nullable=False) # LOW, MEDIUM, HIGH
    duration_category = Column(String(100), nullable=False) # SHORT, MEDIUM, LONG
    active = Column(Boolean, default=True, nullable=False)

    farmers = relationship("Farmer", back_populates="crop")
