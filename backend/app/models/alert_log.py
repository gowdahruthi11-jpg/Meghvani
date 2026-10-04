from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base

class AlertLog(Base):
    """
    Log of all outbound communication, alerts, and dispatches.
    Channels: SMS, VOICE, WHATSAPP
    Phase 6A: Extended for communication simulation, alert routing, fallback tracking, and privacy audit.
    """
    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False, index=True)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False) # ONSET, FALSE_ONSET, BREAK, HEAVY_RAIN, SOW_NOW, WAIT, etc.
    risk_level = Column(String(50), nullable=False) # NORMAL, IMPORTANT, HIGH_RISK, INFO, HIGH
    channel = Column(String(50), nullable=False) # SMS, VOICE, WHATSAPP
    message = Column(Text, nullable=False)
    provider_message_id = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="PENDING")
    attempt_number = Column(Integer, nullable=False, default=1)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Phase 6A Extended Simulation Fields
    crop_id = Column(String(50), nullable=True)
    decision = Column(String(50), nullable=True) # SOW_NOW, WAIT, SOW_PART_NOW
    severity = Column(String(50), nullable=True) # INFO, IMPORTANT, HIGH
    message_type = Column(String(50), nullable=True)
    language = Column(String(20), nullable=True, default="en")
    provider = Column(String(50), nullable=True) # mock_sms, mock_whatsapp, mock_voice
    fallback_used = Column(Boolean, default=False, nullable=False)
    fallback_channel = Column(String(50), nullable=True)
    reason = Column(Text, nullable=True)
    external_dispatch = Column(Boolean, default=False, nullable=False)

    # Phase 8B Model and Advisory Provenance Fields
    model_version = Column(String(50), nullable=True)
    rule_id = Column(String(100), nullable=True)
    rule_version = Column(String(50), nullable=True)
    threshold_config_hash = Column(String(64), nullable=True)

    farmer = relationship("Farmer", back_populates="alert_logs")
    block = relationship("Block", back_populates="alert_logs")
