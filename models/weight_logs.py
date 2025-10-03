from sqlalchemy import (
    Column, Integer, String, Float, 
    DateTime, ForeignKey, Enum, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from constants.enums import WeightUnitEnum


class WeightLog(Base):
    __tablename__ = 'weight_logs'
    
    id = Column(Integer, primary_key=True)
    patient_profile_id = Column(Integer, ForeignKey('patient_profiles.user_id', ondelete='CASCADE'), nullable=False, index=True)
    weight = Column(Float, nullable=False)
    unit = Column(Enum(WeightUnitEnum), default=WeightUnitEnum.KG, nullable=False)
    notes = Column(String(500), nullable=True)
    
    checked_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    logged_by = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    patient = relationship("PatientProfile", back_populates="weight_logs")
    logger = relationship("User", back_populates="logged_weights")
    
    __table_args__ = (
        CheckConstraint('weight > 0 AND weight < 1000', name='check_weight_positive'),
        CheckConstraint("checked_at >= TIMESTAMP('2000-01-01')", name='check_weight_checked_at_reasonable'),
        CheckConstraint("checked_at <= CURRENT_TIMESTAMP + INTERVAL '1 day'", name='check_weight_checked_at_not_future'),
        Index('idx_weight_log_patient_checked', 'patient_profile_id', 'checked_at'),
    )