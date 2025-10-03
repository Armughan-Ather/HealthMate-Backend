from sqlalchemy import (
    Column, Integer, Boolean, Date, Time, 
    DateTime, ForeignKey, Enum, CheckConstraint, Index, ARRAY
)
from sqlalchemy.orm import relationship, validates
from datetime import date, time
from sqlalchemy.sql import func
from database import Base
from constants.enums import FrequencyEnum, DayOfWeekEnum


class BPSchedule(Base):
    __tablename__ = 'bp_schedules'
    
    id = Column(Integer, primary_key=True)
    patient_profile_id = Column(Integer, ForeignKey('patient_profiles.user_id', ondelete='CASCADE'), nullable=False, index=True)
    scheduled_time = Column(Time, nullable=False)
    duration_days = Column(Integer, nullable=True)
    start_date = Column(Date, nullable=False)
    
    frequency = Column(Enum(FrequencyEnum), nullable=False, default=FrequencyEnum.DAILY)
    custom_days = Column(ARRAY(Enum(DayOfWeekEnum, name="day_of_week_enum")), nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    patient = relationship("PatientProfile", back_populates="bp_schedules")
    creator = relationship("User", back_populates="created_bp_schedules")
    logs = relationship("ScheduledBPLog", back_populates="schedule", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint('duration_days IS NULL OR duration_days > 0', name='check_bp_positive_duration'),
        CheckConstraint('duration_days IS NULL OR duration_days <= 3650', name='check_bp_max_duration'),
        CheckConstraint('start_date >= DATE("2000-01-01")', name='check_bp_reasonable_start_date'),
        CheckConstraint(
            "(frequency = 'DAILY' AND custom_days IS NULL) OR "
            "(frequency = 'WEEKLY' AND custom_days IS NOT NULL) OR "
            "(frequency = 'MONTHLY' AND custom_days IS NULL)",
            name='check_bp_frequency_consistency'
        ),
        Index('idx_bp_schedule_patient_active', 'patient_profile_id', 'is_active'),
    )

    @validates('scheduled_time')
    def validate_scheduled_time(self, key, value):
        if not isinstance(value, time):
            raise ValueError("scheduled_time must be a valid time")
        return value

    @validates('duration_days')
    def validate_duration_days(self, key, value):
        if value is not None:
            if value <= 0:
                raise ValueError("duration_days must be positive if provided")
            if value > 3650:
                raise ValueError("duration_days cannot exceed 3650 days (10 years)")
        return value

    @validates('start_date')
    def validate_start_date(self, key, value):
        if not value:
            raise ValueError("start_date is required")
        if value < date(2000, 1, 1):
            raise ValueError("start_date must be on or after 2000-01-01")
        return value

    @validates('frequency', 'custom_days')
    def validate_frequency_custom_days(self, key, value):
        # We need both values, so we validate after assignment
        freq = self.frequency if key != 'frequency' else value
        custom = self.custom_days if key != 'custom_days' else value

        if freq == FrequencyEnum.DAILY:
            if custom is not None:
                raise ValueError("custom_days must be null for DAILY frequency")
        elif freq == FrequencyEnum.WEEKLY:
            if not custom or len(custom) == 0:
                raise ValueError("custom_days must be provided for WEEKLY frequency")
        elif freq == FrequencyEnum.MONTHLY:
            if custom is not None:
                raise ValueError("custom_days must be null for MONTHLY frequency")

        return value