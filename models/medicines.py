import enum
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Time, ForeignKey, 
    Enum, Text, Float, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from database import Base

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    strength = Column(String(50), nullable=False)
    form = Column(String(50), nullable=False)
    generic_name = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    medication_list = relationship("Medication", back_populates="medicine")

    __table_args__ = (
        UniqueConstraint('name', 'strength', 'form', name='unique_medicine_strength_form'),
        CheckConstraint("LENGTH(name) > 0", name="check_medicine_name_not_empty"),
        CheckConstraint("LENGTH(strength) > 0", name="check_strength_not_empty"),
    )