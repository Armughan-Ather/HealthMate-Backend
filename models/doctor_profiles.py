import enum
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from database import Base

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