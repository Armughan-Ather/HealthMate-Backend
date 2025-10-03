from sqlalchemy import (
    Column, Integer, String, Text,
    DateTime, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship, validates
import re
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

    @validates('license_number')
    def validate_license_number(self, key, value):
        """Ensure license number is either None or properly formatted."""
        if value is None:
            return value
        trimmed = value.strip()
        if len(trimmed) < 5:
            raise ValueError("License number must be at least 5 characters long.")
        if len(trimmed) > 100:
            raise ValueError("License number exceeds maximum length.")
        # Optional: enforce alphanumeric format
        if not re.match(r'^[A-Za-z0-9\-]+$', trimmed):
            raise ValueError("License number can only contain letters, numbers, and dashes.")
        return trimmed

    @validates('specialization')
    def validate_specialization(self, key, value):
        """Clean and limit specialization text."""
        if value is None:
            return value
        trimmed = value.strip()
        if len(trimmed) == 0:
            return None
        if len(trimmed) > 200:
            raise ValueError("Specialization cannot exceed 200 characters.")
        return trimmed

    @validates('bio')
    def validate_bio(self, key, value):
        """Trim and enforce max length of bio."""
        if value is None:
            return value
        trimmed = value.strip()
        if len(trimmed) == 0:
            return None
        if len(trimmed) > 5000:
            raise ValueError("Bio cannot exceed 5000 characters.")
        return trimmed

    @validates('years_of_experience')
    def validate_years_of_experience(self, key, value):
        """Ensure years_of_experience is in a reasonable range."""
        if value is None:
            return value
        if not isinstance(value, int):
            raise ValueError("Years of experience must be an integer.")
        if value < 0 or value > 70:
            raise ValueError("Years of experience must be between 0 and 70.")
        return value