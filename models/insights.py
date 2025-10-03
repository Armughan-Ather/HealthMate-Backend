from sqlalchemy import (
    Column, Integer, String, Text, Date,
    DateTime, ForeignKey, Enum, CheckConstraint, UniqueConstraint, JSON, Index, ARRAY
)
from sqlalchemy.orm import relationship
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