from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DoctorProfileBase(BaseModel):
    license_number: Optional[str] = None
    specialization: Optional[str] = None
    bio: Optional[str] = None
    years_of_experience: Optional[int] = None


class DoctorProfileCreate(DoctorProfileBase):
    user_id: int


class DoctorProfileUpdate(BaseModel):
    license_number: Optional[str] = None
    specialization: Optional[str] = None
    bio: Optional[str] = None
    years_of_experience: Optional[int] = None


class DoctorProfileResponse(DoctorProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True