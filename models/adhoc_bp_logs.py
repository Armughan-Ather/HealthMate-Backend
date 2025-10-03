from sqlalchemy import (
    Column, Integer, String,
    DateTime, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timezone
from sqlalchemy.sql import func
from database import Base


class AdhocBPLog(Base):
    __tablename__ = 'adhoc_bp_logs'
    
    id = Column(Integer, primary_key=True)
    patient_profile_id = Column(Integer, ForeignKey('patient_profiles.user_id', ondelete='CASCADE'), nullable=False, index=True)
    systolic = Column(Integer, nullable=False)
    diastolic = Column(Integer, nullable=False)
    pulse = Column(Integer, nullable=True)
    notes = Column(String(500), nullable=True)
    
    logged_by = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    checked_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    patient = relationship("PatientProfile", back_populates="adhoc_bp_logs")
    logger = relationship("User", back_populates="logged_adhoc_bp")
    
    __table_args__ = (
        CheckConstraint('systolic >= 50 AND systolic <= 300', name='check_adhoc_bp_systolic_range'),
        CheckConstraint('diastolic >= 30 AND diastolic <= 200', name='check_adhoc_bp_diastolic_range'),
        CheckConstraint('pulse IS NULL OR (pulse >= 30 AND pulse <= 250)', name='check_adhoc_bp_pulse_range'),
        CheckConstraint('systolic > diastolic', name='check_adhoc_bp_systolic_greater'),
        CheckConstraint("checked_at >= TIMESTAMP('2000-01-01')", name='check_adhoc_bp_checked_at_reasonable'),
        CheckConstraint("checked_at <= CURRENT_TIMESTAMP + INTERVAL '1 day'", name='check_adhoc_bp_checked_at_not_future'),
        Index('idx_adhoc_bp_log_patient_checked', 'patient_profile_id', 'checked_at'),
    )

    @validates('systolic')
    def validate_systolic(self, key, value):
        if value < 50 or value > 300:
            raise ValueError("Systolic must be between 50 and 300 mmHg")
        return value

    @validates('diastolic')
    def validate_diastolic(self, key, value):
        if value < 30 or value > 200:
            raise ValueError("Diastolic must be between 30 and 200 mmHg")
        return value

    @validates('pulse')
    def validate_pulse(self, key, value):
        if value is not None:
            if value < 30 or value > 250:
                raise ValueError("Pulse must be between 30 and 250 bpm")
        return value

    @validates('checked_at')
    def validate_checked_at(self, key, value):
        if value is None:
            raise ValueError("checked_at is required")
        now = datetime.now(timezone.utc)
        if value < datetime(2000, 1, 1, tzinfo=timezone.utc):
            raise ValueError("checked_at must be after year 2000")
        if value > now.replace(microsecond=0) + (now - now):  # basically 'now'
            raise ValueError("checked_at cannot be in the future")
        return value

    @validates('systolic', 'diastolic')
    def validate_bp_relation(self, key, value):
        """
        Additional check to ensure systolic > diastolic before committing.
        This works when both values are present on the instance.
        """
        # We use getattr to fetch the *other* value dynamically
        if key == 'systolic':
            diastolic_val = getattr(self, 'diastolic', None)
            if diastolic_val is not None and value <= diastolic_val:
                raise ValueError("Systolic must be greater than diastolic")
        elif key == 'diastolic':
            systolic_val = getattr(self, 'systolic', None)
            if systolic_val is not None and systolic_val <= value:
                raise ValueError("Systolic must be greater than diastolic")
        return value