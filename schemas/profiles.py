from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional

class ProfileBase(BaseModel):
    height: Optional[float] = Field(None, gt=0, lt=300)
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    conditions: Optional[str] = None

class ProfileCreate(ProfileBase):
    user_id: int

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: int 
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True