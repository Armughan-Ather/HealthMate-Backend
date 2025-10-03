from sqlalchemy import (
    Column, Integer, String, Text, Date,
    DateTime, ForeignKey, Enum, CheckConstraint, UniqueConstraint, JSON, Index, ARRAY
)
from sqlalchemy.orm import relationship, validates
from datetime import date
from sqlalchemy.sql import func
from database import Base
from constants.enums import InsightPeriodEnum

class Insight(Base):
    __tablename__ = 'insights'
    
    id = Column(Integer, primary_key=True)
    patient_profile_id = Column(Integer, ForeignKey('patient_profiles.user_id', ondelete='CASCADE'), nullable=False, index=True)
    period = Column(Enum(InsightPeriodEnum), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)
    json_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    patient = relationship("PatientProfile", back_populates="insights")
    
    __table_args__ = (
        CheckConstraint('end_date >= start_date', name='check_insight_date_order'),
        CheckConstraint('start_date >= DATE("2000-01-01")', name='check_insight_reasonable_start_date'),
        CheckConstraint("LENGTH(TRIM(title)) >= 5", name='check_insight_title_min_length'),
        CheckConstraint("LENGTH(title) <= 200", name='check_insight_title_max_length'),
        CheckConstraint("LENGTH(TRIM(summary)) >= 10", name='check_insight_summary_min_length'),
        CheckConstraint("LENGTH(summary) <= 5000", name='check_insight_summary_max_length'),
        UniqueConstraint('patient_profile_id', 'period', 'start_date', name='uq_patient_period_date'),
        Index('idx_insight_patient_period', 'patient_profile_id', 'period', 'start_date'),
    )

    @validates('period')
    def validate_period(self, key, value):
        """Ensure period is a valid enum value."""
        if value not in InsightPeriodEnum:
            raise ValueError(f"Invalid insight period: {value}")
        return value

    @validates('start_date')
    def validate_start_date(self, key, value):
        """Check that start_date is reasonable (not before 2000-01-01)."""
        if value < date(2000, 1, 1):
            raise ValueError("Start date must be on or after 2000-01-01.")
        return value

    @validates('end_date')
    def validate_end_date(self, key, value):
        """Ensure end_date is not before start_date."""
        if self.start_date and value < self.start_date:
            raise ValueError("End date cannot be earlier than start date.")
        return value

    @validates('title')
    def validate_title(self, key, value):
        """Trim title and enforce length constraints."""
        if value is None:
            raise ValueError("Title cannot be null.")
        trimmed = value.strip()
        if len(trimmed) < 5:
            raise ValueError("Title must be at least 5 characters long.")
        if len(trimmed) > 200:
            raise ValueError("Title cannot exceed 200 characters.")
        return trimmed

    @validates('summary')
    def validate_summary(self, key, value):
        """Trim summary and enforce length constraints."""
        if value is None:
            raise ValueError("Summary cannot be null.")
        trimmed = value.strip()
        if len(trimmed) < 10:
            raise ValueError("Summary must be at least 10 characters long.")
        if len(trimmed) > 5000:
            raise ValueError("Summary cannot exceed 5000 characters.")
        return trimmed

    @validates('json_data')
    def validate_json_data(self, key, value):
        """
        Optional: Validate json_data structure.
        You can enforce a schema or required keys here if needed.
        For now, we ensure it's either None or a dict.
        """
        if value is not None and not isinstance(value, dict):
            raise ValueError("json_data must be a valid JSON object (dict).")
        return value