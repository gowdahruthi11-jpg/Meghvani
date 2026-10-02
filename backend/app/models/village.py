from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class Village(Base):
    __tablename__ = "villages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False, index=True)
    pin_code = Column(String(10), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    boundary_reference = Column(String(255), nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    block = relationship("Block", back_populates="villages")
    farmers = relationship("Farmer", back_populates="village")
