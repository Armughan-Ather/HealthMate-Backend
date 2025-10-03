from sqlalchemy import (
    Column, Integer, String, Float, 
    DateTime, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship, validates
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

    @validates('bp_systolic_min', 'bp_systolic_max')
    def validate_bp_systolic(self, key, value):
        if value is not None:
            if not (70 <= value <= 250):
                raise ValueError(f"{key} must be between 70 and 250 mmHg")
        # Also check min < max when either changes
        if key == 'bp_systolic_min' and self.bp_systolic_max is not None:
            if value is not None and value >= self.bp_systolic_max:
                raise ValueError("bp_systolic_min must be less than bp_systolic_max")
        elif key == 'bp_systolic_max' and self.bp_systolic_min is not None:
            if value is not None and value <= self.bp_systolic_min:
                raise ValueError("bp_systolic_max must be greater than bp_systolic_min")
        return value

    @validates('bp_diastolic_min', 'bp_diastolic_max')
    def validate_bp_diastolic(self, key, value):
        if value is not None:
            if not (40 <= value <= 150):
                raise ValueError(f"{key} must be between 40 and 150 mmHg")
        if key == 'bp_diastolic_min' and self.bp_diastolic_max is not None:
            if value is not None and value >= self.bp_diastolic_max:
                raise ValueError("bp_diastolic_min must be less than bp_diastolic_max")
        elif key == 'bp_diastolic_max' and self.bp_diastolic_min is not None:
            if value is not None and value <= self.bp_diastolic_min:
                raise ValueError("bp_diastolic_max must be greater than bp_diastolic_min")
        return value

    @validates('sugar_fasting_min', 'sugar_fasting_max')
    def validate_sugar_fasting(self, key, value):
        if value is not None:
            if not (50 <= value <= 300):
                raise ValueError(f"{key} must be between 50 and 300 mg/dL")
        if key == 'sugar_fasting_min' and self.sugar_fasting_max is not None:
            if value is not None and value >= self.sugar_fasting_max:
                raise ValueError("sugar_fasting_min must be less than sugar_fasting_max")
        elif key == 'sugar_fasting_max' and self.sugar_fasting_min is not None:
            if value is not None and value <= self.sugar_fasting_min:
                raise ValueError("sugar_fasting_max must be greater than sugar_fasting_min")
        return value

    @validates('sugar_random_min', 'sugar_random_max')
    def validate_sugar_random(self, key, value):
        if value is not None:
            if not (50 <= value <= 400):
                raise ValueError(f"{key} must be between 50 and 400 mg/dL")
        if key == 'sugar_random_min' and self.sugar_random_max is not None:
            if value is not None and value >= self.sugar_random_max:
                raise ValueError("sugar_random_min must be less than sugar_random_max")
        elif key == 'sugar_random_max' and self.sugar_random_min is not None:
            if value is not None and value <= self.sugar_random_min:
                raise ValueError("sugar_random_max must be greater than sugar_random_min")
        return value

    @validates('emergency_contact')
    def validate_emergency_contact(self, key, value):
        if value is not None and len(value.strip()) < 10:
            raise ValueError("Emergency contact must be at least 10 digits")
        return value