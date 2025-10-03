from sqlalchemy import (
    Column, Integer, String, 
    DateTime, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, declarative_base, validates
from sqlalchemy.sql import func
from database import Base

class ScheduledMedicationLog(Base):
    __tablename__ = 'scheduled_medication_logs'
    
    id = Column(Integer, primary_key=True)
    medication_schedule_id = Column(Integer, ForeignKey('medication_schedules.id', ondelete='CASCADE'), nullable=False, index=True)
    dosage_taken = Column(String(100), nullable=False)
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
