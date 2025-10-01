import enum
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from database import Base


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    date_of_birth = Column(Date, nullable=True)
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