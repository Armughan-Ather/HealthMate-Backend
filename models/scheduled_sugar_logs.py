from sqlalchemy import (
    Column, Integer, String, Float, 
    DateTime, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class ScheduledSugarLog(Base):
    __tablename__ = 'scheduled_sugar_logs'
    
    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, ForeignKey('sugar_schedules.id', ondelete='CASCADE'), nullable=False, index=True)
    value = Column(Float, nullable=False)
    notes = Column(String(500), nullable=True)
    
    checked_at = Column(DateTime(timezone=True), nullable=False)
    logged_by = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    schedule = relationship("SugarSchedule", back_populates="logs")
    logger = relationship("User", back_populates="logged_scheduled_sugar")
    
    __table_args__ = (
        CheckConstraint('value >= 20 AND value <= 1000', name='check_scheduled_sugar_value_range'),
        CheckConstraint("checked_at >= TIMESTAMP('2000-01-01')", name='check_scheduled_sugar_checked_at_reasonable'),
        CheckConstraint("checked_at <= CURRENT_TIMESTAMP + INTERVAL '1 day'", name='check_scheduled_sugar_checked_at_not_future'),
        Index('idx_scheduled_sugar_log_checked_at', 'checked_at'),
        Index('idx_scheduled_sugar_log_schedule', 'schedule_id', 'checked_at'),
    )

    from sqlalchemy import (
    Column, Integer, String, Float, 
    DateTime, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from database import Base


class ScheduledSugarLog(Base):
    __tablename__ = 'scheduled_sugar_logs'
    
    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, ForeignKey('sugar_schedules.id', ondelete='CASCADE'), nullable=False, index=True)
    value = Column(Float, nullable=False)
    notes = Column(String(500), nullable=True)
    
    checked_at = Column(DateTime(timezone=True), nullable=False)
    logged_by = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    schedule = relationship("SugarSchedule", back_populates="logs")
    logger = relationship("User", back_populates="logged_scheduled_sugar")
    
    __table_args__ = (
        CheckConstraint('value >= 20 AND value <= 1000', name='check_scheduled_sugar_value_range'),
        CheckConstraint("checked_at >= TIMESTAMP('2000-01-01')", name='check_scheduled_sugar_checked_at_reasonable'),
        CheckConstraint("checked_at <= CURRENT_TIMESTAMP + INTERVAL '1 day'", name='check_scheduled_sugar_checked_at_not_future'),
        Index('idx_scheduled_sugar_log_checked_at', 'checked_at'),
        Index('idx_scheduled_sugar_log_schedule', 'schedule_id', 'checked_at'),
    )

    # ------------------ Validators ------------------
    @validates('value')
    def validate_value(self, key, v):
        if v is None:
            raise ValueError("Sugar value cannot be null")
        if not (20 <= v <= 1000):
            raise ValueError("Sugar value must be between 20 and 1000 mg/dL")
        return v

    @validates('checked_at')
    def validate_checked_at(self, key, v):
        if v is None:
            raise ValueError("checked_at cannot be null")
        min_date = datetime(2000, 1, 1)
        if v < min_date:
            raise ValueError("checked_at must be on or after 2000-01-01")
        if v > datetime.utcnow() + timedelta(days=1):
            raise ValueError("checked_at cannot be more than 1 day in the future")
        return v

    @validates('notes')
    def validate_notes(self, key, v):
        if v is not None and len(v) > 500:
            raise ValueError("notes cannot exceed 500 characters")
        return v