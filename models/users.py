from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, 
    DateTime, Enum, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from constants.enums import GenderEnum


class User(Base):
    __tablename__ = 'users'
    
    # Identity
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    password = Column(String(255), nullable=True)
    
    # Social Login
    microsoft_firebase_uid = Column(String(255), unique=True, nullable=True, index=True)
    google_firebase_uid = Column(String(255), unique=True, nullable=True, index=True)
    
    # Demographics (Universal)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    
    # Account Management
    reset_token = Column(String(255), nullable=True, index=True)
    reset_token_expiry = Column(DateTime(timezone=True), nullable=True)
    email_verification_token = Column(String(255), nullable=True, index=True)
    email_verification_token_expiry = Column(DateTime(timezone=True), nullable=True)
    email_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships - Universal
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    patient_profile = relationship("PatientProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # Relationships - As Actor
    prescribed_medications = relationship("Medication", foreign_keys="[Medication.prescribed_by]", back_populates="prescriber")
    logged_scheduled_medications = relationship("ScheduledMedicationLog", foreign_keys="[ScheduledMedicationLog.logged_by]", back_populates="logger")
    logged_adhoc_medications = relationship("AdhocMedicationLog", foreign_keys="[AdhocMedicationLog.logged_by]", back_populates="logger")
    
    created_bp_schedules = relationship("BPSchedule", foreign_keys="[BPSchedule.created_by]", back_populates="creator")
    logged_scheduled_bp = relationship("ScheduledBPLog", foreign_keys="[ScheduledBPLog.logged_by]", back_populates="logger")
    logged_adhoc_bp = relationship("AdhocBPLog", foreign_keys="[AdhocBPLog.logged_by]", back_populates="logger")
    
    created_sugar_schedules = relationship("SugarSchedule", foreign_keys="[SugarSchedule.created_by]", back_populates="creator")
    logged_scheduled_sugar = relationship("ScheduledSugarLog", foreign_keys="[ScheduledSugarLog.logged_by]", back_populates="logger")
    logged_adhoc_sugar = relationship("AdhocSugarLog", foreign_keys="[AdhocSugarLog.logged_by]", back_populates="logger")
    
    logged_weights = relationship("WeightLog", foreign_keys="[WeightLog.logged_by]", back_populates="logger")
    created_reminders = relationship("Reminder", foreign_keys="[Reminder.created_by]", back_populates="creator")
    created_patient_notes = relationship("PatientNote", foreign_keys="[PatientNote.created_by]", back_populates="creator")
    
    # Connection System
    connections_as_connected_user = relationship("Connection", foreign_keys="[Connection.connected_user_id]", back_populates="connected_user", cascade="all, delete-orphan")
    
    # Chat system
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("email LIKE '%@%' AND email LIKE '%_._%'", name='check_email_format'),
        CheckConstraint("LENGTH(TRIM(name)) >= 2", name='check_name_min_length'),
        CheckConstraint("LENGTH(name) <= 100", name='check_name_max_length'),
        CheckConstraint("password IS NOT NULL OR microsoft_firebase_uid IS NOT NULL OR google_firebase_uid IS NOT NULL", 
                       name='check_auth_method_exists'),
        CheckConstraint("phone IS NULL OR LENGTH(phone) >= 10", name='check_phone_min_length'),
        CheckConstraint("date_of_birth IS NULL OR date_of_birth < CURRENT_DATE", name='check_dob_past'),
        CheckConstraint("date_of_birth IS NULL OR date_of_birth >= DATE('1900-01-01')", name='check_dob_reasonable'),
        CheckConstraint("reset_token_expiry IS NULL OR reset_token IS NOT NULL", name='check_reset_token_consistency'),
        CheckConstraint("email_verification_token_expiry IS NULL OR email_verification_token IS NOT NULL", 
                       name='check_verification_token_consistency'),
        Index('idx_user_email_verified', 'email_verified', 'is_active'),
        Index('idx_user_created_at', 'created_at'),
    )