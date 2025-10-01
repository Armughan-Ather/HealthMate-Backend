from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date
from typing import Optional
from enum import Enum

class Specialization(str, Enum):
    GENERAL = "general"
    CARDIOLOGY = "cardiology"
    NEUROLOGY = "neurology"
    PEDIATRICS = "pediatrics"
    ORTHOPEDICS = "orthopedics"
    OTHER = "other"

class DoctorProfileBase(BaseModel):
    specialization: Specialization
    license_number: str
    experience_years: int = Field(..., ge=0)
    hospital_affiliation: Optional[str] = None
    consultation_fee: Optional[float] = Field(None, ge=0)
    available_hours: Optional[str] = None
    education: Optional[str] = None

class DoctorProfileCreate(DoctorProfileBase):
    user_id: int

class DoctorProfileUpdate(BaseModel):
    specialization: Optional[Specialization] = None
    license_number: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    hospital_affiliation: Optional[str] = None
    consultation_fee: Optional[float] = Field(None, ge=0)
    available_hours: Optional[str] = None
    education: Optional[str] = None

class DoctorProfileResponse(DoctorProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PatientProfileBase(BaseModel):
    height: Optional[float] = Field(None, gt=0, lt=300)
    birth_date: date
    gender: str
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None
    insurance_info: Optional[str] = None

class PatientProfileCreate(PatientProfileBase):
    user_id: int

class PatientProfileUpdate(BaseModel):
    height: Optional[float] = Field(None, gt=0, lt=300)
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None
    insurance_info: Optional[str] = None

class PatientProfileResponse(PatientProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True