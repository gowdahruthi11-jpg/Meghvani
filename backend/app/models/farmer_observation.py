from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class FarmerObservation(Base):
    """
    Ground-truth crowd observations submitted by farmers.
    Types: RAIN, DRY, HEAVY_RAIN.
    CRITICAL POLICY: Never trigger automated ML retraining immediately from individual submissions.
    Stored for validation, bias monitoring, and future calibration research.
    """
    __tablename__ = "farmer_observations"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False, index=True)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False, index=True)
    observation_date = Column(Date, nullable=False, index=True)
    observation_type = Column(String(50), nullable=False) # RAIN, DRY, HEAVY_RAIN
    value = Column(Float, nullable=True) # Optional numeric estimate if provided
    source = Column(String(50), nullable=False, default="FARMER") # FARMER, VOICE_FEEDBACK, SMS_FEEDBACK
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    farmer = relationship("Farmer", back_populates="observations")
    block = relationship("Block", back_populates="farmer_observations")
