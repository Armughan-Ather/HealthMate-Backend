from sqlalchemy import (
    Column, Integer, String, Float, 
    DateTime, ForeignKey, Enum, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timedelta
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

    @validates('patient_profile_id')
    def validate_patient_profile_id(self, key, value):
        if value is None or value <= 0:
            raise ValueError("patient_profile_id must be a valid positive integer")
        return value

    @validates('unit')
    def validate_unit(self, key, value):
        if value is None:
            raise ValueError("Weight unit is required")
        if not isinstance(value, WeightUnitEnum):
            raise ValueError("Invalid weight unit")
        return value

    @validates('weight', 'unit')
    def validate_weight_and_unit(self, key, value):
        """
        Combined validator that handles both 'weight' and 'unit' changes.
        This allows enforcing realistic weight ranges depending on the unit.
        """
        # use the current or new values
        weight = value if key == 'weight' else self.weight
        unit = value if key == 'unit' else self.unit

        # If either is missing during object construction, defer validation
        if weight is None or unit is None:
            return value

        # Realistic weight ranges
        if unit == WeightUnitEnum.KG:
            if weight < 2 or weight > 500:
                raise ValueError("Weight must be between 2 kg and 500 kg")
        elif unit == WeightUnitEnum.LB:
            if weight < 5 or weight > 1100:
                raise ValueError("Weight must be between 5 lb and 1100 lb")
        else:
            raise ValueError("Unknown weight unit")

        return value

    @validates('checked_at')
    def validate_checked_at(self, key, value):
        if value is None:
            raise ValueError("checked_at is required")
        if value < datetime(2000, 1, 1):
            raise ValueError("checked_at must be after January 1, 2000")
        if value > datetime.utcnow() + timedelta(days=1):
            raise ValueError("checked_at cannot be more than 1 day in the future")
        return value

    @validates('logged_by')
    def validate_logged_by(self, key, value):
        if value is None or value <= 0:
            raise ValueError("logged_by must be a valid positive integer")
        return value