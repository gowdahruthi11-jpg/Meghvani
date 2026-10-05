import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base import Base


class InboundMessage(Base):
    """
    Persistent audit log for inbound SMS messages received via webhooks (Twilio or Mock).
    Maintains link to farmer if identified, state transitions, and outbound reply.
    """
    __tablename__ = "inbound_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    provider = Column(String(32), nullable=False, default="TWILIO")  # TWILIO, MOCK
    provider_message_id = Column(String(128), nullable=True, unique=True, index=True)  # MessageSid for idempotency
    from_phone = Column(String(32), nullable=False, index=True)
    to_phone = Column(String(32), nullable=True)
    message_body = Column(Text, nullable=False)
    normalized_body = Column(String(255), nullable=True)
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processing_status = Column(String(32), nullable=False, default="RECEIVED")  # RECEIVED, PROCESSED, DUPLICATE_SUPPRESSED, FAILED
    registration_step_before = Column(String(32), nullable=True)
    registration_step_after = Column(String(32), nullable=True)
    farmer_id = Column(String(36), ForeignKey("farmers.id", ondelete="SET NULL"), nullable=True, index=True)
    reply_message = Column(Text, nullable=True)
    reply_status = Column(String(32), nullable=True)  # SENT, FAILED, SKIPPED
    error_message = Column(Text, nullable=True)

    farmer = relationship("Farmer", backref="inbound_messages", lazy="joined")

    def to_dict(self, mask_phone: bool = True) -> dict:
        def _mask(phone: str | None) -> str:
            if not phone:
                return "Unknown"
            clean = "".join(filter(str.isdigit, phone))
            if len(clean) >= 4:
                return f"******{clean[-4:]}"
            return "******"

        return {
            "id": self.id,
            "provider": self.provider,
            "provider_message_id": self.provider_message_id,
            "from_phone": _mask(self.from_phone) if mask_phone else self.from_phone,
            "to_phone": _mask(self.to_phone) if (mask_phone and self.to_phone) else self.to_phone,
            "message_body": self.message_body,
            "normalized_body": self.normalized_body,
            "received_at": self.received_at.isoformat() if self.received_at else None,
            "processing_status": self.processing_status,
            "registration_step_before": self.registration_step_before,
            "registration_step_after": self.registration_step_after,
            "farmer_id": self.farmer_id,
            "reply_message": self.reply_message,
            "reply_status": self.reply_status,
            "error_message": self.error_message,
        }
