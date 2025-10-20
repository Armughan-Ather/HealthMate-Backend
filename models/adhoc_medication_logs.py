from sqlalchemy import (
    Column, Integer, String,
    DateTime, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timezone
from sqlalchemy.sql import func
from database import Base


class AdhocMedicationLog(Base):
    __tablename__ = 'adhoc_medication_logs'
    
    id = Column(Integer, primary_key=True)
    patient_profile_id = Column(Integer, ForeignKey('patient_profiles.user_id', ondelete='CASCADE'), nullable=False, index=True)
    medicine_id = Column(Integer, ForeignKey('medicines.id'), nullable=False, index=True)
    dosage_taken = Column(String(100), nullable=True)
    notes = Column(String(500), nullable=True)
    
    taken_at = Column(DateTime(timezone=True), nullable=False)
    logged_by = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    patient = relationship("PatientProfile", back_populates="adhoc_medication_logs")
    medicine = relationship("Medicine", back_populates="adhoc_logs")
    logger = relationship("User", back_populates="logged_adhoc_medications")
    
    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(dosage_taken)) >= 1", name='check_adhoc_dosage_taken_not_empty'),
        CheckConstraint("taken_at >= TIMESTAMP '2000-01-01'", name='check_adhoc_taken_at_reasonable'),
        CheckConstraint("taken_at <= CURRENT_TIMESTAMP + INTERVAL '1 day'", name='check_adhoc_taken_at_not_future'),
        Index('idx_adhoc_med_log_patient_taken', 'patient_profile_id', 'taken_at'),
    )

    @validates('dosage_taken')
    def validate_dosage_taken(self, key, value):
        if not value or not value.strip():
            raise ValueError("Dosage taken cannot be empty")
        if len(value.strip()) > 100:
            raise ValueError("Dosage taken must be ≤ 100 characters")
        return value.strip()

    @validates('taken_at')
    def validate_taken_at(self, key, value):
        if not value:
            raise ValueError("taken_at is required")
        if value < datetime(2000, 1, 1, tzinfo=timezone.utc):
            raise ValueError("taken_at must be after year 2000")
        now = datetime.now(timezone.utc)
        if value > now:
            raise ValueError("taken_at cannot be in the future")
        return value

    @validates('notes')
    def validate_notes(self, key, value):
        if value and len(value) > 500:
            raise ValueError("Notes cannot exceed 500 characters")
        return value