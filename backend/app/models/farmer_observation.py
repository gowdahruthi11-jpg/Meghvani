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
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=True, index=True)
    observation_date = Column(Date, nullable=False, index=True)
    observation_time = Column(String(20), nullable=True) # e.g. "18:30"
    observation_type = Column(String(50), nullable=False) # RAIN, DRY, HEAVY_RAIN
    value = Column(Float, nullable=True) # Optional numeric estimate if provided
    crop_id = Column(String(50), nullable=True)
    notes = Column(String(500), nullable=True)
    source = Column(String(50), nullable=False, default="FARMER") # Always FARMER for Phase 6B
    validation_status = Column(String(50), nullable=True, default="PENDING_REVIEW") # AGREEMENT, DISAGREEMENT, REFERENCE_DATA_UNAVAILABLE, REFERENCE_THRESHOLD_UNAVAILABLE, PENDING_REVIEW
    reference_rainfall_mm = Column(Float, nullable=True)
    comparison_notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    farmer = relationship("Farmer", back_populates="observations")
    block = relationship("Block", back_populates="farmer_observations")
    village = relationship("Village")
