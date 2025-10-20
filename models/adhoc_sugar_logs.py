from sqlalchemy import (
    Column, Integer, String, Float,
    DateTime, ForeignKey, Enum, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timezone
from sqlalchemy.sql import func
from database import Base
from constants.enums import SugarTypeEnum


class AdhocSugarLog(Base):
    __tablename__ = 'adhoc_sugar_logs'
    
    id = Column(Integer, primary_key=True)
    patient_profile_id = Column(Integer, ForeignKey('patient_profiles.user_id', ondelete='CASCADE'), nullable=False, index=True)
    value = Column(Float, nullable=False)
    type = Column(Enum(SugarTypeEnum), nullable=False)
    notes = Column(String(500), nullable=True)
    
    checked_at = Column(DateTime(timezone=True), nullable=False)
    logged_by = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    patient = relationship("PatientProfile", back_populates="adhoc_sugar_logs")
    logger = relationship("User", back_populates="logged_adhoc_sugar")
    
    __table_args__ = (
        CheckConstraint('value >= 20 AND value <= 1000', name='check_adhoc_sugar_value_range'),
        CheckConstraint("checked_at >= TIMESTAMP '2000-01-01'", name='check_adhoc_sugar_checked_at_reasonable'),
        CheckConstraint("checked_at <= CURRENT_TIMESTAMP + INTERVAL '1 day'", name='check_adhoc_sugar_checked_at_not_future'),
        Index('idx_adhoc_sugar_log_patient_checked', 'patient_profile_id', 'checked_at'),
    )

    @validates('value')
    def validate_value(self, key, value):
        if value is None:
            raise ValueError("Sugar value is required")
        if value < 20 or value > 1000:
            raise ValueError("Sugar value must be between 20 and 1000 mg/dL")
        return value

    @validates('type')
    def validate_type(self, key, value):
        if not isinstance(value, SugarTypeEnum):
            raise ValueError("Invalid sugar type")
        return value

    @validates('checked_at')
    def validate_checked_at(self, key, value):
        if not value:
            raise ValueError("checked_at is required")
        if value < datetime(2000, 1, 1, tzinfo=timezone.utc):
            raise ValueError("checked_at must be after year 2000")
        if value > datetime.now(timezone.utc):
            raise ValueError("checked_at cannot be in the future")
        return value

    @validates('notes')
    def validate_notes(self, key, value):
        if value and len(value) > 500:
            raise ValueError("Notes cannot exceed 500 characters")
        return value