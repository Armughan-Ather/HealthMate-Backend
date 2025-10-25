from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DoctorProfileBase(BaseModel):
    license_number: str
    specialization: Optional[str] = None
    bio: Optional[str] = None
    years_of_experience: Optional[int] = 0


class DoctorProfileCreate(DoctorProfileBase):
    pass


class DoctorProfileUpdate(BaseModel):
    specialization: Optional[str] = None
    bio: Optional[str] = None
    years_of_experience: Optional[int] = None


class DoctorProfileResponse(DoctorProfileBase):
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True