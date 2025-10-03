from sqlalchemy import (
    Column, Integer, String, 
    DateTime, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
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
        CheckConstraint("checked_at >= TIMESTAMP('2000-01-01')", name='check_scheduled_bp_checked_at_reasonable'),
        CheckConstraint("checked_at <= CURRENT_TIMESTAMP + INTERVAL '1 day'", name='check_scheduled_bp_checked_at_not_future'),
        Index('idx_scheduled_bp_log_checked_at', 'checked_at'),
        Index('idx_scheduled_bp_log_schedule', 'schedule_id', 'checked_at'),
    )