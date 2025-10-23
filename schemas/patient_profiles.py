from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PatientProfileBase(BaseModel):
    emergency_contact: Optional[str] = None
    bp_systolic_min: Optional[int] = None
    bp_systolic_max: Optional[int] = None
    bp_diastolic_min: Optional[int] = None
    bp_diastolic_max: Optional[int] = None
    sugar_fasting_min: Optional[float] = None
    sugar_fasting_max: Optional[float] = None
    sugar_random_min: Optional[float] = None
    sugar_random_max: Optional[float] = None


class PatientProfileCreate(PatientProfileBase):
    pass


class PatientProfileUpdate(BaseModel):
    emergency_contact: Optional[str] = None
    bp_systolic_min: Optional[int] = None
    bp_systolic_max: Optional[int] = None
    bp_diastolic_min: Optional[int] = None
    bp_diastolic_max: Optional[int] = None
    sugar_fasting_min: Optional[float] = None
    sugar_fasting_max: Optional[float] = None
    sugar_random_min: Optional[float] = None
    sugar_random_max: Optional[float] = None


class PatientProfileResponse(PatientProfileBase):
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True