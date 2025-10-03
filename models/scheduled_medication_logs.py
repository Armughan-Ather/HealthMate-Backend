from sqlalchemy import (
    Column, Integer, String, 
    DateTime, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from sqlalchemy.sql import func
from database import Base

class ScheduledMedicationLog(Base):
    __tablename__ = 'scheduled_medication_logs'
    
    id = Column(Integer, primary_key=True)
    medication_schedule_id = Column(Integer, ForeignKey('medication_schedules.id', ondelete='CASCADE'), nullable=False, index=True)
    notes = Column(String(500), nullable=True)
    
    taken_at = Column(DateTime(timezone=True), nullable=False)
    logged_by = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    schedule = relationship("MedicationSchedule", back_populates="logs")
    logger = relationship("User", back_populates="logged_scheduled_medications")
    
    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(dosage_taken)) >= 1", name='check_dosage_taken_not_empty'),
        CheckConstraint("taken_at >= TIMESTAMP('2000-01-01')", name='check_taken_at_reasonable'),
        CheckConstraint("taken_at <= CURRENT_TIMESTAMP + INTERVAL '1 day'", name='check_taken_at_not_future'),
        Index('idx_scheduled_med_log_taken_at', 'taken_at'),
        Index('idx_scheduled_med_log_schedule', 'medication_schedule_id', 'taken_at'),
    )

    @validates('taken_at')
    def validate_taken_at_range(cls, v):
        min_date = datetime(2000, 1, 1)
        if v < min_date:
            raise ValueError('taken_at must be on or after 2000-01-01')
        now = datetime.utcnow()
        if (v - now).total_seconds() > 86400:  # more than 1 day in the future
            raise ValueError('taken_at cannot be more than 1 day in the future')
        return v