from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PatientNoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    is_discussed: bool = False
    discussed_with_doctor: Optional[int] = None
    discussed_at: Optional[datetime] = None

class PatientNoteCreate(PatientNoteBase):
    user_id: int

class PatientNoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    is_discussed: Optional[bool] = None
    discussed_with_doctor: Optional[int] = None
    discussed_at: Optional[datetime] = None

class PatientNoteResponse(PatientNoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True