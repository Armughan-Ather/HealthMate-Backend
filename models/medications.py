from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date,
    DateTime, ForeignKey, Enum, CheckConstraint, Index, ARRAY
)
from sqlalchemy.orm import relationship, validates
from datetime import date
from sqlalchemy.sql import func
from database import Base
from constants.enums import FrequencyEnum, DayOfWeekEnum

class Medication(Base):
    __tablename__ = 'medications'
    
    id = Column(Integer, primary_key=True)
    patient_profile_id = Column(Integer, ForeignKey('patient_profiles.user_id', ondelete='CASCADE'), nullable=False, index=True)
    medicine_id = Column(Integer, ForeignKey('medicines.id'), nullable=False, index=True)
    prescribed_by = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    purpose = Column(String(500), nullable=True)
    duration_days = Column(Integer, nullable=True)
    start_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    special_instructions = Column(Text, nullable=True)
    
    frequency = Column(Enum(FrequencyEnum), nullable=False, default=FrequencyEnum.DAILY)
    custom_days = Column(ARRAY(Enum(DayOfWeekEnum, name="day_of_week_enum")), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    patient = relationship("PatientProfile", back_populates="medications")
    prescriber = relationship("User", back_populates="prescribed_medications")
    medicine = relationship("Medicine", back_populates="medications")
    schedules = relationship("MedicationSchedule", back_populates="medication", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint('duration_days IS NULL OR duration_days > 0', name='check_medication_positive_duration'),
        CheckConstraint('duration_days IS NULL OR duration_days <= 3650', name='check_medication_max_duration'),  # 10 years max
        CheckConstraint('start_date >= DATE("2000-01-01")', name='check_medication_reasonable_start_date'),
        CheckConstraint(
            "(frequency = 'DAILY' AND custom_days IS NULL) OR "
            "(frequency = 'WEEKLY' AND custom_days IS NOT NULL) OR "
            "(frequency = 'MONTHLY' AND custom_days IS NULL)",
            name='check_medication_frequency_consistency'
        ),
        CheckConstraint("special_instructions IS NULL OR LENGTH(special_instructions) <= 2000", 
                       name='check_instructions_length'),
        Index('idx_medication_patient_active', 'patient_profile_id', 'is_active'),
        Index('idx_medication_start_date', 'start_date'),
    )

    @validates('patient_profile_id', 'medicine_id', 'prescribed_by')
    def validate_foreign_keys(self, key, value):
        """Ensure foreign key IDs are positive integers."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"{key} must be a positive integer.")
        return value

    @validates('purpose')
    def validate_purpose(self, key, value):
        """Trim and enforce length for purpose."""
        if value is None:
            return value
        trimmed = value.strip()
        if len(trimmed) == 0:
            return None
        if len(trimmed) > 500:
            raise ValueError("Purpose cannot exceed 500 characters.")
        return trimmed

    @validates('duration_days')
    def validate_duration_days(self, key, value):
        """Ensure duration_days is positive and reasonable if provided."""
        if value is None:
            return value
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Duration days must be a positive integer.")
        if value > 3650:
            raise ValueError("Duration days cannot exceed 3650 (10 years).")
        return value

    @validates('start_date')
    def validate_start_date(self, key, value):
        """Ensure start_date is not before 2000-01-01."""
        if not isinstance(value, date):
            raise ValueError("start_date must be a valid date object.")
        if value < date(2000, 1, 1):
            raise ValueError("Start date must be on or after 2000-01-01.")
        return value

    @validates('special_instructions')
    def validate_special_instructions(self, key, value):
        """Trim whitespace and enforce length for special_instructions."""
        if value is None:
            return value
        trimmed = value.strip()
        if len(trimmed) == 0:
            return None
        if len(trimmed) > 2000:
            raise ValueError("Special instructions cannot exceed 2000 characters.")
        return trimmed

    @validates('frequency')
    def validate_frequency(self, key, value):
        """Ensure frequency is a valid FrequencyEnum value."""
        if not isinstance(value, FrequencyEnum):
            raise ValueError("Invalid frequency value.")
        return value

    @validates('custom_days')
    def validate_custom_days(self, key, value):
        """
        Ensure custom_days align with frequency logic:
        - DAILY → custom_days must be None
        - WEEKLY → custom_days must be non-empty list of DayOfWeekEnum
        - MONTHLY → custom_days must be None
        """
        freq = self.frequency
        if freq == FrequencyEnum.DAILY:
            if value is not None:
                raise ValueError("custom_days must be null for DAILY frequency.")
        elif freq == FrequencyEnum.WEEKLY:
            if not value or not isinstance(value, list) or any(not isinstance(d, DayOfWeekEnum) for d in value):
                raise ValueError("For WEEKLY frequency, custom_days must be a non-empty list of valid days.")
        elif freq == FrequencyEnum.MONTHLY:
            if value is not None:
                raise ValueError("custom_days must be null for MONTHLY frequency.")
        return value

    @validates('is_active')
    def validate_is_active(self, key, value):
        """Ensure is_active is boolean."""
        if not isinstance(value, bool):
            raise ValueError("is_active must be a boolean.")
        return value