from sqlalchemy import (
    Column, Integer, String, Boolean, Time, 
    DateTime, ForeignKey, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, validates
from datetime import time
from sqlalchemy.sql import func
from database import Base

class MedicationSchedule(Base):
    __tablename__ = 'medication_schedules'
    
    id = Column(Integer, primary_key=True)
    medication_id = Column(Integer, ForeignKey('medications.id', ondelete='CASCADE'), nullable=False, index=True)
    scheduled_time = Column(Time, nullable=False)
    dosage_instruction = Column(String(200), nullable=True)
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

    @validates('medication_id')
    def validate_medication_id(self, key, value):
        """Ensure medication_id is positive."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Invalid medication_id.")
        return value

    @validates('scheduled_time')
    def validate_scheduled_time(self, key, value):
        """Ensure scheduled_time is a valid time object."""
        if not isinstance(value, time):
            raise ValueError("scheduled_time must be a valid time object.")
        return value

    @validates('dosage_instruction')
    def validate_dosage_instruction(self, key, value):
        """Trim whitespace and enforce length rules for dosage_instruction."""
        if value is None:
            raise ValueError("Dosage instruction cannot be null.")
        trimmed = value.strip()
        if len(trimmed) < 2:
            raise ValueError("Dosage instruction must be at least 2 characters long.")
        if len(trimmed) > 200:
            raise ValueError("Dosage instruction cannot exceed 200 characters.")
        return trimmed

    @validates('is_active')
    def validate_is_active(self, key, value):
        """Ensure is_active is boolean."""
        if not isinstance(value, bool):
            raise ValueError("is_active must be a boolean.")
        return value