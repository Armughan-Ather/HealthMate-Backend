from sqlalchemy import (
    Column, Integer, String, Boolean,
    DateTime, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Medicine(Base):
    __tablename__ = 'medicines'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    strength = Column(String(50), nullable=False)
    form = Column(String(50), nullable=False)  # tablet, syrup, injection, etc.
    generic_name = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    medications = relationship("Medication", back_populates="medicine")
    adhoc_logs = relationship("AdhocMedicationLog", back_populates="medicine")
    
    __table_args__ = (
        UniqueConstraint('name', 'strength', 'form', name='uq_medicine_combination'),
        CheckConstraint("LENGTH(TRIM(name)) >= 2", name='check_medicine_name_length'),
        CheckConstraint("LENGTH(TRIM(strength)) >= 1", name='check_strength_not_empty'),
        CheckConstraint("LENGTH(TRIM(form)) >= 2", name='check_form_not_empty'),
        Index('idx_medicine_name', 'name'),
        Index('idx_medicine_active', 'is_active'),
    )