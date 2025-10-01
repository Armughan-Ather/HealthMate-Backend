from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional

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