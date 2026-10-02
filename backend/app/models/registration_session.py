from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database.base import Base

class RegistrationSession(Base):
    """
    Session record for SMS/conversational registration state machine.
    Handles multi-turn conversational workflow without losing context.
    """
    __tablename__ = "registration_sessions"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    current_step = Column(String(50), nullable=False, default="START")
    language = Column(String(50), nullable=True)
    pin_code = Column(String(10), nullable=True)
    selected_village_id = Column(Integer, nullable=True)
    selected_block_id = Column(Integer, nullable=True)
    selected_crop_id = Column(Integer, nullable=True)
    consent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime, nullable=True)
