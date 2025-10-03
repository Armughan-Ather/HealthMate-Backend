from sqlalchemy import (
    Column, Integer, Boolean, Date, Time, 
    DateTime, ForeignKey, Enum, CheckConstraint, Index, ARRAY
)
from sqlalchemy.orm import relationship
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