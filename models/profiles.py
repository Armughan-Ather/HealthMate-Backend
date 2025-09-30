import enum
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from database import Base


class GenderEnum(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    emergency_contact = Column(String(20), nullable=True)

    bp_systolic_min = Column(Integer, nullable=True)
    bp_systolic_max = Column(Integer, nullable=True)
    bp_diastolic_min = Column(Integer, nullable=True)
    bp_diastolic_max = Column(Integer, nullable=True)

    sugar_fasting_min = Column(Float, nullable=True)
    sugar_fasting_max = Column(Float, nullable=True)
    sugar_random_min = Column(Float, nullable=True)
    sugar_random_max = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="patient_profile")


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    license_number = Column(String(100), unique=True, nullable=True)
    specialization = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    years_of_experience = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="doctor_profile")


