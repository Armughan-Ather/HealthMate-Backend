from sqlalchemy import (
    Column, Integer, String, Text,
    DateTime, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class DoctorProfile(Base):
    __tablename__ = 'doctor_profiles'
    
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    license_number = Column(String(100), unique=True, nullable=True, index=True)
    specialization = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)
    years_of_experience = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    
    __table_args__ = (
        CheckConstraint("license_number IS NULL OR LENGTH(TRIM(license_number)) >= 5", name='check_license_min_length'),
        CheckConstraint("years_of_experience IS NULL OR (years_of_experience >= 0 AND years_of_experience <= 70)", 
                       name='check_experience_range'),
        CheckConstraint("bio IS NULL OR LENGTH(bio) <= 5000", name='check_bio_max_length'),
    )