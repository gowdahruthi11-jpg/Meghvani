from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class Farmer(Base):
    """
    Farmer profile entity.
    PRIVACY & ETHICAL GUIDELINES:
    - Never collect Aadhaar or unnecessary PII.
    - Phone number is sensitive data (treated with care, masked in officer dashboards).
    - Explicit consent is mandatory prior to activation.
    """
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    preferred_language = Column(String(50), nullable=False, default="Hindi")
    pin_code = Column(String(10), nullable=False, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False, index=True)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False, index=True)
    communication_preference = Column(String(20), nullable=False, default="SMS") # SMS, VOICE, WHATSAPP
    consent = Column(Boolean, nullable=False, default=False)
    consent_timestamp = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    village = relationship("Village", back_populates="farmers")
    block = relationship("Block", back_populates="farmers")
    crop = relationship("Crop", back_populates="farmers")
    observations = relationship("FarmerObservation", back_populates="farmer")
    alert_logs = relationship("AlertLog", back_populates="farmer")
