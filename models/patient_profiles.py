from sqlalchemy import (
    Column, Integer, String, Float, 
    DateTime, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class PatientProfile(Base):
    __tablename__ = 'patient_profiles'
    
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    emergency_contact = Column(String(20), nullable=True)
    
    bp_systolic_min = Column(Integer, nullable=True)
    bp_systolic_max = Column(Integer, nullable=True)
    bp_diastolic_min = Column(Integer, nullable=True)
    bp_diastolic_max = Column(Integer, nullable=True)
    sugar_fasting_min = Column(Float, nullable=True)
    sugar_fasting_max = Column(Float, nullable=True)
    sugar_random_min = Column(Float, nullable=True)
    sugar_random_max = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="patient_profile")
    connections_as_patient = relationship("Connection", foreign_keys="[Connection.patient_id]", back_populates="patient", cascade="all, delete-orphan")
    
    medications = relationship("Medication", back_populates="patient", cascade="all, delete-orphan")
    bp_schedules = relationship("BPSchedule", back_populates="patient", cascade="all, delete-orphan")
    sugar_schedules = relationship("SugarSchedule", back_populates="patient", cascade="all, delete-orphan")
    adhoc_medication_logs = relationship("AdhocMedicationLog", back_populates="patient", cascade="all, delete-orphan")
    adhoc_bp_logs = relationship("AdhocBPLog", back_populates="patient", cascade="all, delete-orphan")
    adhoc_sugar_logs = relationship("AdhocSugarLog", back_populates="patient", cascade="all, delete-orphan")
    weight_logs = relationship("WeightLog", back_populates="patient", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="patient", cascade="all, delete-orphan")
    patient_notes = relationship("PatientNote", back_populates="patient", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="patient", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("emergency_contact IS NULL OR LENGTH(emergency_contact) >= 10", name='check_emergency_contact_length'),
        # BP ranges validation
        CheckConstraint("bp_systolic_min IS NULL OR (bp_systolic_min >= 70 AND bp_systolic_min <= 200)", 
                       name='check_bp_systolic_min_range'),
        CheckConstraint("bp_systolic_max IS NULL OR (bp_systolic_max >= 70 AND bp_systolic_max <= 250)", 
                       name='check_bp_systolic_max_range'),
        CheckConstraint("bp_diastolic_min IS NULL OR (bp_diastolic_min >= 40 AND bp_diastolic_min <= 130)", 
                       name='check_bp_diastolic_min_range'),
        CheckConstraint("bp_diastolic_max IS NULL OR (bp_diastolic_max >= 40 AND bp_diastolic_max <= 150)", 
                       name='check_bp_diastolic_max_range'),
        CheckConstraint("bp_systolic_min IS NULL OR bp_systolic_max IS NULL OR bp_systolic_min < bp_systolic_max", 
                       name='check_bp_systolic_min_max_order'),
        CheckConstraint("bp_diastolic_min IS NULL OR bp_diastolic_max IS NULL OR bp_diastolic_min < bp_diastolic_max", 
                       name='check_bp_diastolic_min_max_order'),
        # Sugar ranges validation
        CheckConstraint("sugar_fasting_min IS NULL OR (sugar_fasting_min >= 50 AND sugar_fasting_min <= 200)", 
                       name='check_sugar_fasting_min_range'),
        CheckConstraint("sugar_fasting_max IS NULL OR (sugar_fasting_max >= 50 AND sugar_fasting_max <= 300)", 
                       name='check_sugar_fasting_max_range'),
        CheckConstraint("sugar_random_min IS NULL OR (sugar_random_min >= 50 AND sugar_random_min <= 200)", 
                       name='check_sugar_random_min_range'),
        CheckConstraint("sugar_random_max IS NULL OR (sugar_random_max >= 50 AND sugar_random_max <= 400)", 
                       name='check_sugar_random_max_range'),
        CheckConstraint("sugar_fasting_min IS NULL OR sugar_fasting_max IS NULL OR sugar_fasting_min < sugar_fasting_max", 
                       name='check_sugar_fasting_min_max_order'),
        CheckConstraint("sugar_random_min IS NULL OR sugar_random_max IS NULL OR sugar_random_min < sugar_random_max", 
                       name='check_sugar_random_min_max_order'),
    )
