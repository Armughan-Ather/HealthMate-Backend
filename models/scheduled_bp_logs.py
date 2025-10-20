from sqlalchemy import (
    Column, Integer, String, 
    DateTime, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from sqlalchemy.sql import func
from database import Base

class ScheduledBPLog(Base):
    __tablename__ = 'scheduled_bp_logs'
    
    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, ForeignKey('bp_schedules.id', ondelete='CASCADE'), nullable=False, index=True)
    systolic = Column(Integer, nullable=False)
    diastolic = Column(Integer, nullable=False)
    pulse = Column(Integer, nullable=True)
    notes = Column(String(500), nullable=True)

    logged_by = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    checked_at = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    schedule = relationship("BPSchedule", back_populates="logs")
    logger = relationship("User", back_populates="logged_scheduled_bp")
    
    __table_args__ = (
        CheckConstraint('systolic >= 50 AND systolic <= 300', name='check_scheduled_bp_systolic_range'),
        CheckConstraint('diastolic >= 30 AND diastolic <= 200', name='check_scheduled_bp_diastolic_range'),
        CheckConstraint('pulse IS NULL OR (pulse >= 30 AND pulse <= 250)', name='check_scheduled_bp_pulse_range'),
        CheckConstraint('systolic > diastolic', name='check_scheduled_bp_systolic_greater'),
        CheckConstraint("checked_at >= TIMESTAMP '2000-01-01'", name='check_scheduled_bp_checked_at_reasonable'),
        CheckConstraint("checked_at <= CURRENT_TIMESTAMP + INTERVAL '1 day'", name='check_scheduled_bp_checked_at_not_future'),
        Index('idx_scheduled_bp_log_checked_at', 'checked_at'),
        Index('idx_scheduled_bp_log_schedule', 'schedule_id', 'checked_at'),
    )

    @validates('systolic')
    def validate_systolic_greater_than_diastolic(cls, v, values):
        diastolic = values.get('diastolic')
        if diastolic is not None and v <= diastolic:
            raise ValueError('systolic must be greater than diastolic')
        return v

    @validates('checked_at')
    def validate_checked_at_reasonable(cls, v):
        min_date = datetime(2000, 1, 1)
        max_date = datetime.utcnow().replace(microsecond=0)
        if v < min_date:
            raise ValueError('checked_at must be on or after 2000-01-01')
        # Allow checked_at up to 1 day in the future (like the SQL constraint)
        if v > max_date.replace(microsecond=0) and (v - max_date).total_seconds() > 86400:
            raise ValueError('checked_at cannot be more than 1 day in the future')
        return v