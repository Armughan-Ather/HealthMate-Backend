from sqlalchemy import (
    Column, Integer, String, Boolean, Time, 
    DateTime, ForeignKey, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class MedicationSchedule(Base):
    __tablename__ = 'medication_schedules'
    
    id = Column(Integer, primary_key=True)
    medication_id = Column(Integer, ForeignKey('medications.id', ondelete='CASCADE'), nullable=False, index=True)
    scheduled_time = Column(Time, nullable=False)
    dosage_instruction = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    medication = relationship("Medication", back_populates="schedules")
    logs = relationship("ScheduledMedicationLog", back_populates="schedule", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('medication_id', 'scheduled_time', name='uq_medication_schedule_time'),
        CheckConstraint("LENGTH(TRIM(dosage_instruction)) >= 2", name='check_dosage_instruction_not_empty'),
        CheckConstraint("LENGTH(dosage_instruction) <= 200", name='check_dosage_instruction_length'),
        Index('idx_schedule_medication_active', 'medication_id', 'is_active'),
    )