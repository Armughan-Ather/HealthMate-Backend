from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PatientNoteBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=5)
    is_discussed: bool = False
    discussed_at: Optional[datetime] = None


class PatientNoteCreate(PatientNoteBase):
    patient_profile_id: int
    created_by: int


class PatientNoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content: Optional[str] = Field(None, min_length=5)
    is_discussed: Optional[bool] = None
    discussed_at: Optional[datetime] = None


class PatientNoteResponse(PatientNoteBase):
    id: int
    patient_profile_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True