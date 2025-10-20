from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, Time, 
    DateTime, ForeignKey, Enum, CheckConstraint, Index, ARRAY
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from database import Base
from constants.enums import FrequencyEnum, DayOfWeekEnum


class Reminder(Base):
    __tablename__ = 'reminders'
    
    id = Column(Integer, primary_key=True)
    patient_profile_id = Column(Integer, ForeignKey('patient_profiles.user_id', ondelete='CASCADE'), nullable=False, index=True)
    tags = Column(String(100), nullable=False)
    topic = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    scheduled_time = Column(Time, nullable=False)
    start_date = Column(Date, nullable=False)
    duration_days = Column(Integer, nullable=True)
    
    frequency = Column(Enum(FrequencyEnum), nullable=False, default=FrequencyEnum.DAILY)
    custom_days = Column(ARRAY(Enum(DayOfWeekEnum, name="day_of_week_enum")), nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    patient = relationship("PatientProfile", back_populates="reminders")
    creator = relationship("User", back_populates="created_reminders")
    
    __table_args__ = (
        CheckConstraint("duration_days IS NULL OR duration_days > 0", name='check_reminder_positive_duration'),
        CheckConstraint("duration_days IS NULL OR duration_days <= 3650", name='check_reminder_max_duration'),
        CheckConstraint("LENGTH(TRIM(topic)) >= 3", name='check_topic_min_length'),
        CheckConstraint("LENGTH(topic) <= 200", name='check_topic_max_length'),
        CheckConstraint("LENGTH(TRIM(tags)) >= 2", name='check_tags_min_length'),
        CheckConstraint("start_date >= DATE '2000-01-01'", name='check_reminder_reasonable_start_date'),
        CheckConstraint(
            "(frequency = 'DAILY' AND custom_days IS NULL) OR "
            "(frequency = 'WEEKLY' AND custom_days IS NOT NULL) OR "
            "(frequency = 'MONTHLY' AND custom_days IS NULL)",
            name='check_reminder_frequency_consistency'
        ),
        CheckConstraint("description IS NULL OR LENGTH(description) <= 2000", name='check_reminder_description_length'),
        Index('idx_reminder_patient_active', 'patient_profile_id', 'is_active'),
        Index('idx_reminder_start_date', 'start_date'),
    )

    @validates('custom_days')
    def validate_frequency_and_custom_days(cls, v, values):
        freq = values.get('frequency')
        if freq == FrequencyEnum.DAILY:
            if v is not None:
                raise ValueError("custom_days must be NULL when frequency is DAILY")
        elif freq == FrequencyEnum.WEEKLY:
            if not v or len(v) == 0:
                raise ValueError("custom_days must be provided when frequency is WEEKLY")
        elif freq == FrequencyEnum.MONTHLY:
            if v is not None:
                raise ValueError("custom_days must be NULL when frequency is MONTHLY")
        return v