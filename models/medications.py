from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date,
    DateTime, ForeignKey, Enum, CheckConstraint, Index, ARRAY
)
from sqlalchemy.orm import relationship
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