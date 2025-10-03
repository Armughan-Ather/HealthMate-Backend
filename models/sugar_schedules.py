from sqlalchemy import (
    Column, Integer, Boolean, Date, Time, 
    DateTime, ForeignKey, Enum, CheckConstraint, Index, ARRAY
)
from sqlalchemy.orm import relationship, validates
from datetime import date
from sqlalchemy.sql import func
from database import Base
from constants.enums import FrequencyEnum, DayOfWeekEnum, SugarTypeEnum

class SugarSchedule(Base):
    __tablename__ = 'sugar_schedules'
    
    id = Column(Integer, primary_key=True)
    patient_profile_id = Column(Integer, ForeignKey('patient_profiles.user_id', ondelete='CASCADE'), nullable=False, index=True)
    scheduled_time = Column(Time, nullable=False)
    sugar_type = Column(Enum(SugarTypeEnum), nullable=False)
    duration_days = Column(Integer, nullable=True)
    start_date = Column(Date, nullable=False)
    
    frequency = Column(Enum(FrequencyEnum), nullable=False, default=FrequencyEnum.DAILY)
    custom_days = Column(ARRAY(Enum(DayOfWeekEnum, name="day_of_week_enum")), nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    patient = relationship("PatientProfile", back_populates="sugar_schedules")
    creator = relationship("User", back_populates="created_sugar_schedules")
    logs = relationship("ScheduledSugarLog", back_populates="schedule", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint('duration_days IS NULL OR duration_days > 0', name='check_sugar_positive_duration'),
        CheckConstraint('duration_days IS NULL OR duration_days <= 3650', name='check_sugar_max_duration'),
        CheckConstraint('start_date >= DATE("2000-01-01")', name='check_sugar_reasonable_start_date'),
        CheckConstraint(
            "(frequency = 'DAILY' AND custom_days IS NULL) OR "
            "(frequency = 'WEEKLY' AND custom_days IS NOT NULL) OR "
            "(frequency = 'MONTHLY' AND custom_days IS NULL)",
            name='check_sugar_frequency_consistency'
        ),
        Index('idx_sugar_schedule_patient_active', 'patient_profile_id', 'is_active'),
    )

    @validates('duration_days')
    def validate_duration_days(self, key, value):
        if value is not None:
            if value <= 0:
                raise ValueError("duration_days must be positive")
            if value > 3650:
                raise ValueError("duration_days must not exceed 10 years (3650 days)")
        return value

    @validates('start_date')
    def validate_start_date(self, key, value):
        if value < date(2000, 1, 1):
            raise ValueError("start_date must not be earlier than 2000-01-01")
        return value

    @validates('frequency', 'custom_days')
    def validate_frequency_custom_days(self, key, value):
        """
        Validate the consistency between frequency and custom_days.
        Mirrors the DB constraint but catches issues earlier at the ORM layer.
        """
        # temporarily assign to current object for cross-field validation
        setattr(self, key, value)

        freq = getattr(self, 'frequency', None)
        days = getattr(self, 'custom_days', None)

        if freq is not None:
            if freq == FrequencyEnum.DAILY and days is not None:
                raise ValueError("custom_days must be NULL when frequency is DAILY")
            elif freq == FrequencyEnum.WEEKLY and (days is None or len(days) == 0):
                raise ValueError("custom_days must be provided when frequency is WEEKLY")
            elif freq == FrequencyEnum.MONTHLY and days is not None:
                raise ValueError("custom_days must be NULL when frequency is MONTHLY")

        return value