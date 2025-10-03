from sqlalchemy import (
    Column, Integer, String, Text, Boolean, 
    DateTime, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timezone
from sqlalchemy.sql import func
from database import Base


class PatientNote(Base):
    __tablename__ = 'patient_notes'
    
    id = Column(Integer, primary_key=True)
    patient_profile_id = Column(Integer, ForeignKey('patient_profiles.user_id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    is_discussed = Column(Boolean, default=False, nullable=False)
    
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    patient = relationship("PatientProfile", back_populates="patient_notes")
    creator = relationship("User", back_populates="created_patient_notes")
    
    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(title)) >= 3", name='check_note_title_min_length'),
        CheckConstraint("LENGTH(title) <= 200", name='check_note_title_max_length'),
        CheckConstraint("LENGTH(TRIM(content)) >= 5", name='check_note_content_min_length'),
        CheckConstraint("LENGTH(content) <= 10000", name='check_note_content_max_length'),
        CheckConstraint("(is_discussed = FALSE AND discussed_at IS NULL) OR (is_discussed = TRUE)", 
                       name='check_note_discussed_consistency'),
        CheckConstraint("discussed_at IS NULL OR discussed_at >= created_at", name='check_note_discussed_after_creation'),
        Index('idx_patient_note_patient_discussed', 'patient_profile_id', 'is_discussed'),
    )

    @validates('title')
    def validate_title(self, key, value):
        if not value or not value.strip():
            raise ValueError("Title cannot be empty")
        trimmed = value.strip()
        if len(trimmed) < 3:
            raise ValueError("Title must be at least 3 characters long")
        if len(trimmed) > 200:
            raise ValueError("Title cannot exceed 200 characters")
        return trimmed

    @validates('content')
    def validate_content(self, key, value):
        if not value or not value.strip():
            raise ValueError("Content cannot be empty")
        trimmed = value.strip()
        if len(trimmed) < 5:
            raise ValueError("Content must be at least 5 characters long")
        if len(trimmed) > 10000:
            raise ValueError("Content cannot exceed 10,000 characters")
        return trimmed