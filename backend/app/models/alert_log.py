from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class AlertLog(Base):
    """
    Log of all outbound communication, alerts, and dispatches.
    Channels: SMS, VOICE, WHATSAPP
    Statuses: PENDING, SIMULATED, SENT, DELIVERED, FAILED, NO_ANSWER
    """
    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False, index=True)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False) # ONSET, FALSE_ONSET, BREAK, HEAVY_RAIN, ROUTINE_ADVISORY
    risk_level = Column(String(50), nullable=False) # NORMAL, IMPORTANT, HIGH_RISK
    channel = Column(String(50), nullable=False) # SMS, VOICE, WHATSAPP
    message = Column(Text, nullable=False)
    provider_message_id = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="PENDING")
    attempt_number = Column(Integer, nullable=False, default=1)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    farmer = relationship("Farmer", back_populates="alert_logs")
    block = relationship("Block", back_populates="alert_logs")
